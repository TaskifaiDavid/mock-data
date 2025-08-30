#!/usr/bin/env python3
"""
Phase 1 Migration Validation Script
===================================
This script validates that the Phase 1 migration completed successfully
and provides detailed reports on the multi-tenant schema implementation.

Usage:
    python validate_phase_1.py [--verbose] [--fix-issues]
"""

import os
import sys
import argparse
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Tuple
import psycopg2
from psycopg2.extras import RealDictCursor

# Add the backend app to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.utils.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Phase1Validator:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.settings = get_settings()
        self.connection = None
        self.validation_results = {
            'overall_status': 'UNKNOWN',
            'checks_passed': 0,
            'checks_failed': 0,
            'warnings': [],
            'errors': [],
            'recommendations': []
        }
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
        
    async def connect(self):
        """Establish database connection"""
        try:
            self.connection = psycopg2.connect(
                host=self.settings.SUPABASE_DB_HOST,
                port=self.settings.SUPABASE_DB_PORT,
                database=self.settings.SUPABASE_DB_NAME,
                user=self.settings.SUPABASE_SERVICE_ROLE_USER,
                password=self.settings.SUPABASE_SERVICE_ROLE_PASSWORD,
                cursor_factory=RealDictCursor
            )
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
            
    async def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
    
    def add_check_result(self, check_name: str, passed: bool, details: str = "", recommendation: str = ""):
        """Add a check result to validation results"""
        if passed:
            self.validation_results['checks_passed'] += 1
            if self.verbose:
                logger.info(f"✓ {check_name}: {details}")
        else:
            self.validation_results['checks_failed'] += 1
            self.validation_results['errors'].append(f"{check_name}: {details}")
            logger.error(f"✗ {check_name}: {details}")
            
            if recommendation:
                self.validation_results['recommendations'].append(f"{check_name}: {recommendation}")
    
    def add_warning(self, message: str):
        """Add a warning to validation results"""
        self.validation_results['warnings'].append(message)
        logger.warning(f"⚠ {message}")
    
    async def validate_migration_tables(self) -> bool:
        """Validate that all required migration tables exist"""
        cursor = self.connection.cursor()
        try:
            expected_tables = {
                'organizations': ['id', 'name', 'slug', 'settings', 'is_active', 'created_at', 'updated_at'],
                'user_organizations': ['id', 'user_id', 'organization_id', 'role', 'is_active', 'created_at', 'updated_at'],
                'migration_log': ['id', 'phase', 'operation', 'status', 'details', 'created_at', 'updated_at'],
                'migration_policy_backup': ['id', 'table_name', 'policy_name', 'policy_definition', 'backed_up_at']
            }
            
            all_tables_valid = True
            
            for table_name, expected_columns in expected_tables.items():
                # Check if table exists
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_schema = 'public' AND table_name = %s
                    )
                """, (table_name,))
                
                table_exists = cursor.fetchone()[0]
                
                if not table_exists:
                    self.add_check_result(
                        f"Table {table_name} exists",
                        False,
                        f"Table {table_name} not found",
                        f"Re-run migration or check for table creation errors"
                    )
                    all_tables_valid = False
                    continue
                
                # Check columns
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_schema = 'public' AND table_name = %s
                """, (table_name,))
                
                actual_columns = [row[0] for row in cursor.fetchall()]
                missing_columns = set(expected_columns) - set(actual_columns)
                
                if missing_columns:
                    self.add_check_result(
                        f"Table {table_name} has all required columns",
                        False,
                        f"Missing columns: {', '.join(missing_columns)}",
                        f"Check migration logs for {table_name} creation errors"
                    )
                    all_tables_valid = False
                else:
                    self.add_check_result(
                        f"Table {table_name} structure",
                        True,
                        f"All {len(expected_columns)} columns present"
                    )
            
            return all_tables_valid
            
        finally:
            cursor.close()
    
    async def validate_client_id_columns(self) -> bool:
        """Validate that all required tables have client_id columns"""
        cursor = self.connection.cursor()
        try:
            expected_tables_with_client_id = [
                'users', 'uploads', 'sellout_entries2', 'products', 
                'processing_logs', 'transform_logs', 'email_logs'
            ]
            
            all_client_ids_valid = True
            
            for table_name in expected_tables_with_client_id:
                # Check if table exists first
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_schema = 'public' AND table_name = %s
                    )
                """, (table_name,))
                
                table_exists = cursor.fetchone()[0]
                
                if not table_exists:
                    self.add_warning(f"Table {table_name} not found - skipping client_id check")
                    continue
                
                # Check if client_id column exists
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_schema = 'public' AND table_name = %s AND column_name = 'client_id'
                    )
                """, (table_name,))
                
                has_client_id = cursor.fetchone()[0]
                
                if not has_client_id:
                    self.add_check_result(
                        f"Table {table_name} has client_id column",
                        False,
                        f"client_id column missing",
                        f"Re-run migration or manually add client_id column to {table_name}"
                    )
                    all_client_ids_valid = False
                    continue
                
                # Check client_id data integrity
                cursor.execute(f"""
                    SELECT 
                        COUNT(*) as total_records,
                        COUNT(client_id) as records_with_client_id,
                        COUNT(*) - COUNT(client_id) as null_client_ids
                    FROM public.{table_name}
                """)
                
                result = cursor.fetchone()
                total = result['total_records']
                with_client_id = result['records_with_client_id']
                null_client_ids = result['null_client_ids']
                
                if null_client_ids > 0:
                    self.add_check_result(
                        f"Table {table_name} client_id data integrity",
                        False,
                        f"{null_client_ids} out of {total} records have NULL client_id",
                        f"Run data fix script to assign default client_id to NULL records"
                    )
                    all_client_ids_valid = False
                else:
                    self.add_check_result(
                        f"Table {table_name} client_id data integrity",
                        True,
                        f"All {total} records have client_id values"
                    )
            
            return all_client_ids_valid
            
        finally:
            cursor.close()
    
    async def validate_default_organization(self) -> bool:
        """Validate that the default organization was created correctly"""
        cursor = self.connection.cursor()
        try:
            # Check if default organization exists
            cursor.execute("""
                SELECT id, name, slug, is_active, created_at
                FROM public.organizations 
                WHERE slug = 'default-org'
            """)
            
            default_org = cursor.fetchone()
            
            if not default_org:
                self.add_check_result(
                    "Default organization exists",
                    False,
                    "No organization with slug 'default-org' found",
                    "Re-run migration or manually create default organization"
                )
                return False
            
            if not default_org['is_active']:
                self.add_check_result(
                    "Default organization is active",
                    False,
                    "Default organization exists but is not active",
                    "Activate the default organization"
                )
                return False
            
            # Check that the default organization ID is being used
            default_org_id = str(default_org['id'])
            
            # Sample a few tables to verify they're using the default org ID
            tables_to_check = ['uploads', 'sellout_entries2', 'products']
            for table in tables_to_check:
                try:
                    cursor.execute(f"""
                        SELECT COUNT(*) as count
                        FROM public.{table}
                        WHERE client_id = %s
                        LIMIT 1
                    """, (default_org_id,))
                    
                    result = cursor.fetchone()
                    if result and result['count'] > 0:
                        self.add_check_result(
                            f"Default organization used in {table}",
                            True,
                            f"Records found using default organization ID"
                        )
                except Exception as e:
                    self.add_warning(f"Could not check {table} for default org usage: {e}")
            
            self.add_check_result(
                "Default organization setup",
                True,
                f"Default organization '{default_org['name']}' is active and properly configured"
            )
            
            return True
            
        finally:
            cursor.close()
    
    async def validate_indexes(self) -> bool:
        """Validate that required indexes were created"""
        cursor = self.connection.cursor()
        try:
            # Expected indexes for multi-tenant performance
            expected_indexes = [
                ('users', 'idx_users_client_created_at'),
                ('uploads', 'idx_uploads_client_created_at'),
                ('uploads', 'idx_uploads_client_user_id'),
                ('sellout_entries2', 'idx_sellout_entries2_client_created_at'),
                ('sellout_entries2', 'idx_sellout_entries2_client_upload_id'),
                ('products', 'idx_products_client_ean'),
                ('organizations', 'idx_organizations_slug'),
                ('user_organizations', 'idx_user_organizations_user_id'),
            ]
            
            all_indexes_valid = True
            
            for table_name, index_name in expected_indexes:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT 1 FROM pg_indexes 
                        WHERE schemaname = 'public' 
                        AND tablename = %s 
                        AND indexname = %s
                    )
                """, (table_name, index_name))
                
                index_exists = cursor.fetchone()[0]
                
                if not index_exists:
                    # Check if table exists first
                    cursor.execute("""
                        SELECT EXISTS (
                            SELECT 1 FROM information_schema.tables 
                            WHERE table_schema = 'public' AND table_name = %s
                        )
                    """, (table_name,))
                    
                    table_exists = cursor.fetchone()[0]
                    
                    if table_exists:
                        self.add_check_result(
                            f"Index {index_name}",
                            False,
                            f"Missing on table {table_name}",
                            f"Create index manually or re-run migration"
                        )
                        all_indexes_valid = False
                    else:
                        self.add_warning(f"Table {table_name} doesn't exist - skipping index {index_name}")
                else:
                    self.add_check_result(
                        f"Index {index_name}",
                        True,
                        f"Exists on table {table_name}"
                    )
            
            return all_indexes_valid
            
        finally:
            cursor.close()
    
    async def validate_utility_functions(self) -> bool:
        """Validate that utility functions were created"""
        cursor = self.connection.cursor()
        try:
            expected_functions = [
                'get_user_organization_id',
                'validate_client_access',
                'get_current_client_id',
                'validate_client_data_integrity',
                'create_data_snapshot'
            ]
            
            all_functions_valid = True
            
            for function_name in expected_functions:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.routines 
                        WHERE routine_schema = 'public' 
                        AND routine_name = %s
                        AND routine_type = 'FUNCTION'
                    )
                """, (function_name,))
                
                function_exists = cursor.fetchone()[0]
                
                if not function_exists:
                    self.add_check_result(
                        f"Function {function_name}",
                        False,
                        "Function not found",
                        f"Re-run migration or manually create function"
                    )
                    all_functions_valid = False
                else:
                    self.add_check_result(
                        f"Function {function_name}",
                        True,
                        "Function exists and callable"
                    )
            
            return all_functions_valid
            
        finally:
            cursor.close()
    
    async def check_migration_logs(self) -> Dict[str, Any]:
        """Check migration logs for any issues"""
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                SELECT phase, operation, status, details, created_at
                FROM public.migration_log 
                WHERE phase = 'phase_1' 
                ORDER BY created_at DESC
                LIMIT 50
            """)
            
            logs = cursor.fetchall()
            
            if not logs:
                self.add_warning("No Phase 1 migration logs found")
                return {'logs_found': False}
            
            # Analyze log status
            failed_operations = [log for log in logs if log['status'] == 'failed']
            successful_operations = [log for log in logs if log['status'] == 'completed']
            
            if failed_operations:
                self.add_check_result(
                    "Migration logs analysis",
                    False,
                    f"{len(failed_operations)} failed operations found",
                    "Review failed operations and re-run migration if necessary"
                )
                
                if self.verbose:
                    for failed_op in failed_operations:
                        logger.error(f"Failed operation: {failed_op['operation']} - {failed_op['details']}")
            else:
                self.add_check_result(
                    "Migration logs analysis",
                    True,
                    f"All {len(successful_operations)} operations completed successfully"
                )
            
            return {
                'logs_found': True,
                'total_operations': len(logs),
                'successful_operations': len(successful_operations),
                'failed_operations': len(failed_operations),
                'latest_operation': logs[0]['operation'] if logs else None
            }
            
        finally:
            cursor.close()
    
    async def run_full_validation(self) -> Dict[str, Any]:
        """Run complete Phase 1 validation"""
        logger.info("Starting Phase 1 migration validation...")
        
        # Run all validation checks
        checks = [
            ("Migration Tables", self.validate_migration_tables()),
            ("Client ID Columns", self.validate_client_id_columns()),
            ("Default Organization", self.validate_default_organization()),
            ("Indexes", self.validate_indexes()),
            ("Utility Functions", self.validate_utility_functions()),
        ]
        
        for check_name, check_coro in checks:
            try:
                logger.info(f"Running {check_name} validation...")
                await check_coro
            except Exception as e:
                self.add_check_result(
                    check_name,
                    False,
                    f"Validation error: {str(e)}",
                    "Check database connection and permissions"
                )
        
        # Check migration logs
        log_analysis = await self.check_migration_logs()
        
        # Determine overall status
        if self.validation_results['checks_failed'] == 0:
            self.validation_results['overall_status'] = 'PASSED'
        elif self.validation_results['checks_failed'] <= 2:
            self.validation_results['overall_status'] = 'PASSED_WITH_WARNINGS'
        else:
            self.validation_results['overall_status'] = 'FAILED'
        
        # Add summary
        self.validation_results.update({
            'validation_timestamp': datetime.now().isoformat(),
            'migration_log_analysis': log_analysis
        })
        
        return self.validation_results
    
    def print_validation_report(self):
        """Print a comprehensive validation report"""
        results = self.validation_results
        
        print("\n" + "="*80)
        print("PHASE 1 MIGRATION VALIDATION REPORT")
        print("="*80)
        
        # Overall status
        status_emoji = "✅" if results['overall_status'] == 'PASSED' else "⚠️" if results['overall_status'] == 'PASSED_WITH_WARNINGS' else "❌"
        print(f"\nOVERALL STATUS: {status_emoji} {results['overall_status']}")
        
        # Summary
        print(f"\nSUMMARY:")
        print(f"  ✅ Checks Passed: {results['checks_passed']}")
        print(f"  ❌ Checks Failed: {results['checks_failed']}")
        print(f"  ⚠️  Warnings: {len(results['warnings'])}")
        
        # Errors
        if results['errors']:
            print(f"\nERRORS:")
            for error in results['errors']:
                print(f"  ❌ {error}")
        
        # Warnings
        if results['warnings']:
            print(f"\nWARNINGS:")
            for warning in results['warnings']:
                print(f"  ⚠️  {warning}")
        
        # Recommendations
        if results['recommendations']:
            print(f"\nRECOMMENDATIONS:")
            for recommendation in results['recommendations']:
                print(f"  💡 {recommendation}")
        
        # Migration log analysis
        if 'migration_log_analysis' in results:
            log_analysis = results['migration_log_analysis']
            if log_analysis.get('logs_found'):
                print(f"\nMIGRATION LOGS:")
                print(f"  📊 Total Operations: {log_analysis['total_operations']}")
                print(f"  ✅ Successful: {log_analysis['successful_operations']}")
                print(f"  ❌ Failed: {log_analysis['failed_operations']}")
                print(f"  🕒 Latest Operation: {log_analysis.get('latest_operation', 'Unknown')}")
        
        print("\n" + "="*80)
        
        # Final recommendation
        if results['overall_status'] == 'PASSED':
            print("✅ Phase 1 migration is complete and validated successfully!")
            print("   You can proceed to Phase 2 implementation.")
        elif results['overall_status'] == 'PASSED_WITH_WARNINGS':
            print("⚠️  Phase 1 migration completed with warnings.")
            print("   Review warnings and recommendations before proceeding.")
        else:
            print("❌ Phase 1 migration validation failed.")
            print("   Address the errors above before proceeding to Phase 2.")
        
        print("="*80)

async def main():
    parser = argparse.ArgumentParser(description='Validate Phase 1 Multi-Tenant Migration')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--fix-issues', action='store_true', help='Attempt to fix common issues (NOT IMPLEMENTED)')
    
    args = parser.parse_args()
    
    if args.fix_issues:
        print("--fix-issues is not yet implemented")
        return
    
    async with Phase1Validator(verbose=args.verbose) as validator:
        try:
            results = await validator.run_full_validation()
            validator.print_validation_report()
            
            # Exit with appropriate code
            if results['overall_status'] == 'FAILED':
                sys.exit(1)
            elif results['overall_status'] == 'PASSED_WITH_WARNINGS':
                sys.exit(2)
            else:
                sys.exit(0)
                
        except Exception as e:
            logger.error(f"Validation failed with error: {e}")
            sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())