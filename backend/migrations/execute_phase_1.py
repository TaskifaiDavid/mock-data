#!/usr/bin/env python3
"""
Phase 1 Multi-Tenant Migration Executor
========================================
This script safely executes the Phase 1 schema migration with comprehensive
safety checks, monitoring, and rollback capabilities.

Usage:
    python execute_phase_1.py [--dry-run] [--force] [--rollback]

Options:
    --dry-run   : Show what would be done without executing (default: false)
    --force     : Skip safety prompts (DANGEROUS - use only for automation)
    --rollback  : Execute rollback instead of migration (DANGEROUS)
"""

import os
import sys
import argparse
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import psycopg2
from psycopg2.extras import RealDictCursor

# Add the backend app to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.utils.config import get_settings
from app.services.migration_service import MigrationService, MigrationLogEntry, MigrationPhase, MigrationStatus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration_phase_1.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class Phase1MigrationExecutor:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.settings = get_settings()
        self.migration_service = MigrationService()
        self.connection = None
        
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
            # Get DATABASE_URL from environment
            import os
            database_url = os.getenv('DATABASE_URL')
            
            if not database_url:
                raise ValueError("DATABASE_URL environment variable is required for migration connection")
            
            # Use DATABASE_URL directly  
            self.connection = psycopg2.connect(
                database_url,
                cursor_factory=RealDictCursor
            )
            logger.info("Database connection established using DATABASE_URL")
                
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
            
    async def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
            
    async def check_prerequisites(self) -> Dict[str, Any]:
        """Check migration prerequisites"""
        logger.info("Checking migration prerequisites...")
        
        prerequisites = await self.migration_service.check_migration_prerequisites()
        
        # Additional Phase 1 specific checks
        cursor = self.connection.cursor()
        
        try:
            # Check for existing client_id columns
            cursor.execute("""
                SELECT table_name, column_name 
                FROM information_schema.columns 
                WHERE column_name = 'client_id' 
                AND table_schema = 'public'
                AND table_name IN ('users', 'uploads', 'sellout_entries2', 'products', 'processing_logs', 'transform_logs', 'email_logs')
            """)
            existing_client_id_columns = cursor.fetchall()
            
            # Check for existing organization tables
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('organizations', 'user_organizations')
            """)
            existing_org_tables = cursor.fetchall()
            
            # Check current data volumes
            table_sizes = {}
            for table in ['users', 'uploads', 'sellout_entries2', 'products', 'processing_logs', 'transform_logs']:
                try:
                    cursor.execute(f"SELECT COUNT(*) as count FROM public.{table}")
                    result = cursor.fetchone()
                    table_sizes[table] = result['count'] if result else 0
                except:
                    table_sizes[table] = 'table_not_found'
            
            prerequisites.update({
                'existing_client_id_columns': len(existing_client_id_columns),
                'existing_org_tables': len(existing_org_tables),
                'table_sizes': table_sizes,
                'migration_already_run': len(existing_client_id_columns) > 0 or len(existing_org_tables) > 0
            })
            
        except Exception as e:
            logger.error(f"Prerequisites check failed: {e}")
            prerequisites['prerequisites_error'] = str(e)
        finally:
            cursor.close()
            
        return prerequisites
        
    def display_migration_plan(self):
        """Display what the migration will do"""
        print("\n" + "="*80)
        print("PHASE 1 MULTI-TENANT MIGRATION PLAN")
        print("="*80)
        print("""
This migration will make the following changes to your database:

1. CREATE NEW TABLES:
   - organizations (id, name, slug, settings, timestamps)
   - user_organizations (user-to-org relationships with roles)
   - migration_log (migration tracking)
   - migration_policy_backup (rollback safety)

2. ADD CLIENT_ID COLUMNS to existing tables:
   - users.client_id
   - uploads.client_id  
   - sellout_entries2.client_id
   - products.client_id
   - processing_logs.client_id
   - transform_logs.client_id
   - email_logs.client_id (if exists)

3. SET DEFAULT VALUES:
   - All existing records will be assigned to a default organization
   - client_id will be set to the default organization ID

4. CREATE INDEXES:
   - Composite indexes for efficient client-scoped queries
   - ~15 indexes total across all tables

5. CREATE UTILITY FUNCTIONS:
   - get_user_organization_id()
   - validate_client_access()
   - get_current_client_id()
   - validate_client_data_integrity()
   - create_data_snapshot()

6. DATA VALIDATION:
   - Verify all records have client_id values
   - Ensure data integrity after migration

SAFETY FEATURES:
✓ Backward compatible (doesn't break existing queries)
✓ Uses safe defaults for existing data
✓ Comprehensive logging and monitoring
✓ Built-in validation and rollback procedures
✓ Zero-downtime deployment ready
        """)
        print("="*80)
        
    async def execute_migration(self) -> bool:
        """Execute the Phase 1 migration"""
        logger.info("Starting Phase 1 migration execution")
        
        try:
            # Log migration start
            await self.migration_service.log_migration_event(MigrationLogEntry(
                phase=MigrationPhase.PHASE_1,
                operation="migration_execution_start",
                status=MigrationStatus.STARTED,
                details={"dry_run": self.dry_run, "timestamp": datetime.now().isoformat()}
            ))
            
            # Read migration script
            script_path = os.path.join(os.path.dirname(__file__), 'phase_1_multitenant_schema.sql')
            with open(script_path, 'r') as f:
                migration_sql = f.read()
            
            if self.dry_run:
                logger.info("DRY RUN: Migration script would be executed")
                logger.info(f"Script length: {len(migration_sql)} characters")
                return True
            
            # Execute migration script
            cursor = self.connection.cursor()
            try:
                logger.info("Executing migration script...")
                cursor.execute(migration_sql)
                self.connection.commit()
                logger.info("Migration script executed successfully")
                
                # Verify migration results
                await self._verify_migration_results()
                
                return True
                
            except Exception as e:
                logger.error(f"Migration execution failed: {e}")
                self.connection.rollback()
                
                await self.migration_service.log_migration_event(MigrationLogEntry(
                    phase=MigrationPhase.PHASE_1,
                    operation="migration_execution_failed",
                    status=MigrationStatus.FAILED,
                    details={"error": str(e)}
                ))
                
                return False
            finally:
                cursor.close()
                
        except Exception as e:
            logger.error(f"Migration execution error: {e}")
            return False
            
    async def execute_rollback(self) -> bool:
        """Execute the Phase 1 rollback"""
        logger.warning("Starting Phase 1 migration ROLLBACK")
        
        try:
            # Log rollback start
            await self.migration_service.log_migration_event(MigrationLogEntry(
                phase=MigrationPhase.PHASE_1,
                operation="rollback_execution_start",
                status=MigrationStatus.ROLLBACK,
                details={"dry_run": self.dry_run, "timestamp": datetime.now().isoformat()}
            ))
            
            # Read rollback script
            script_path = os.path.join(os.path.dirname(__file__), 'phase_1_rollback.sql')
            with open(script_path, 'r') as f:
                rollback_sql = f.read()
            
            if self.dry_run:
                logger.info("DRY RUN: Rollback script would be executed")
                logger.warning("DRY RUN: This would PERMANENTLY DELETE all multi-tenant data")
                return True
            
            # Execute rollback script
            cursor = self.connection.cursor()
            try:
                logger.warning("Executing rollback script - THIS WILL DELETE DATA")
                cursor.execute(rollback_sql)
                self.connection.commit()
                logger.info("Rollback script executed successfully")
                
                return True
                
            except Exception as e:
                logger.error(f"Rollback execution failed: {e}")
                self.connection.rollback()
                return False
            finally:
                cursor.close()
                
        except Exception as e:
            logger.error(f"Rollback execution error: {e}")
            return False
            
    async def _verify_migration_results(self):
        """Verify migration completed successfully"""
        cursor = self.connection.cursor()
        try:
            # Check client_id columns were added
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM information_schema.columns 
                WHERE column_name = 'client_id' 
                AND table_schema = 'public'
                AND table_name IN ('users', 'uploads', 'sellout_entries2', 'products', 'processing_logs', 'transform_logs')
            """)
            client_id_columns = cursor.fetchone()['count']
            
            # Check organization tables were created
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('organizations', 'user_organizations')
            """)
            org_tables = cursor.fetchone()['count']
            
            # Check default organization exists
            cursor.execute("SELECT COUNT(*) as count FROM public.organizations WHERE slug = 'default-org'")
            default_org = cursor.fetchone()['count']
            
            verification_results = {
                'client_id_columns_added': client_id_columns,
                'organization_tables_created': org_tables,
                'default_organization_exists': default_org > 0,
                'migration_successful': client_id_columns >= 6 and org_tables == 2 and default_org > 0
            }
            
            await self.migration_service.log_migration_event(MigrationLogEntry(
                phase=MigrationPhase.PHASE_1,
                operation="migration_verification",
                status=MigrationStatus.COMPLETED if verification_results['migration_successful'] else MigrationStatus.FAILED,
                details=verification_results
            ))
            
            if not verification_results['migration_successful']:
                raise Exception(f"Migration verification failed: {verification_results}")
                
            logger.info("Migration verification successful")
            
        finally:
            cursor.close()

async def main():
    parser = argparse.ArgumentParser(description='Execute Phase 1 Multi-Tenant Migration')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without executing')
    parser.add_argument('--force', action='store_true', help='Skip safety prompts (use with caution)')
    parser.add_argument('--rollback', action='store_true', help='Execute rollback instead of migration (DANGEROUS)')
    
    args = parser.parse_args()
    
    if args.rollback and not args.force:
        print("\n" + "="*80)
        print("WARNING: ROLLBACK OPERATION")
        print("="*80)
        print("This will PERMANENTLY DELETE all Phase 1 multi-tenant changes including:")
        print("- All client_id columns and their data")
        print("- All organization and user-organization data")
        print("- All multi-tenant indexes and functions")
        print("\nThis operation is IRREVERSIBLE!")
        
        if not args.dry_run:
            confirm = input("\nType 'PERMANENTLY DELETE' to confirm rollback: ")
            if confirm != 'PERMANENTLY DELETE':
                print("Rollback cancelled")
                return
    
    async with Phase1MigrationExecutor(dry_run=args.dry_run) as executor:
        # Check prerequisites
        prerequisites = await executor.check_prerequisites()
        
        print(f"\nPrerequisites Check Results:")
        for key, value in prerequisites.items():
            status = "✓" if value else "✗"
            print(f"  {status} {key}: {value}")
        
        if not all(prerequisites.values()):
            logger.error("Prerequisites check failed")
            return
            
        # Check if migration already ran
        if prerequisites.get('migration_already_run') and not args.rollback:
            logger.warning("Migration appears to have already been run")
            if not args.force:
                confirm = input("Continue anyway? (y/N): ")
                if confirm.lower() != 'y':
                    print("Migration cancelled")
                    return
        
        # Display plan
        if not args.rollback:
            executor.display_migration_plan()
        
        # Final confirmation for non-dry-run executions
        if not args.dry_run and not args.force:
            operation = "rollback" if args.rollback else "migration"
            confirm = input(f"\nProceed with {operation}? (y/N): ")
            if confirm.lower() != 'y':
                print(f"{operation.capitalize()} cancelled")
                return
        
        # Execute operation
        if args.rollback:
            success = await executor.execute_rollback()
        else:
            success = await executor.execute_migration()
        
        if success:
            operation = "rollback" if args.rollback else "migration"
            mode = "(DRY RUN)" if args.dry_run else ""
            logger.info(f"Phase 1 {operation} completed successfully {mode}")
        else:
            logger.error("Operation failed")
            sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())