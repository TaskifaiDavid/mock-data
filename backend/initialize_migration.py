#!/usr/bin/env python3
"""
Initialize Migration Infrastructure
Script to set up the migration infrastructure in the database.
"""

import asyncio
import logging
from app.services.db_service import DatabaseService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def initialize_migration_infrastructure():
    """Initialize migration tables and functions in the database."""
    db_service = DatabaseService()
    
    try:
        logger.info("Initializing migration infrastructure...")
        
        # Create migration log table
        migration_log_sql = """
        CREATE TABLE IF NOT EXISTS public.migration_log (
            id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
            phase text NOT NULL,
            operation text NOT NULL,
            status text CHECK (status IN ('started', 'completed', 'failed', 'rollback')),
            details jsonb,
            created_at timestamptz DEFAULT now()
        );
        """
        
        await db_service.execute(migration_log_sql, ())
        logger.info("✅ Created migration_log table")
        
        # Create migration policy backup table
        policy_backup_sql = """
        CREATE TABLE IF NOT EXISTS public.migration_policy_backup (
            id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
            table_name text NOT NULL,
            policy_name text NOT NULL,
            policy_definition text NOT NULL,
            backed_up_at timestamptz DEFAULT now()
        );
        """
        
        await db_service.execute(policy_backup_sql, ())
        logger.info("✅ Created migration_policy_backup table")
        
        # Create validation function
        validation_function_sql = """
        CREATE OR REPLACE FUNCTION validate_system_state()
        RETURNS jsonb
        LANGUAGE plpgsql
        AS $$
        DECLARE
            result jsonb := '{}'::jsonb;
            user_count int;
            upload_count int;
            entry_count int;
            product_count int;
        BEGIN
            -- Count current data
            SELECT COUNT(*) INTO user_count FROM public.users;
            SELECT COUNT(*) INTO upload_count FROM public.uploads;
            SELECT COUNT(*) INTO entry_count FROM public.sellout_entries2;
            SELECT COUNT(*) INTO product_count FROM public.products;
            
            result = jsonb_build_object(
                'users', user_count,
                'uploads', upload_count,
                'sellout_entries', entry_count,
                'products', product_count,
                'timestamp', now()
            );
            
            RETURN result;
        END;
        $$;
        """
        
        await db_service.execute(validation_function_sql, ())
        logger.info("✅ Created validate_system_state function")
        
        # Create backup function
        backup_function_sql = """
        CREATE OR REPLACE FUNCTION backup_rls_policies()
        RETURNS void
        LANGUAGE plpgsql
        AS $$
        DECLARE
            policy_record record;
        BEGIN
            -- Clear existing backups
            DELETE FROM public.migration_policy_backup;
            
            -- Backup all current RLS policies
            FOR policy_record IN
                SELECT schemaname, tablename, policyname, definition
                FROM pg_policies
                WHERE schemaname = 'public'
            LOOP
                INSERT INTO public.migration_policy_backup (table_name, policy_name, policy_definition)
                VALUES (
                    policy_record.tablename,
                    policy_record.policyname,
                    policy_record.definition
                );
            END LOOP;
        END;
        $$;
        """
        
        await db_service.execute(backup_function_sql, ())
        logger.info("✅ Created backup_rls_policies function")
        
        # Create data snapshot function
        snapshot_function_sql = """
        CREATE OR REPLACE FUNCTION create_data_snapshot()
        RETURNS jsonb
        LANGUAGE plpgsql
        AS $$
        DECLARE
            result jsonb;
            timestamp_suffix text;
        BEGIN
            timestamp_suffix := to_char(now(), 'YYYY_MM_DD_HH24_MI_SS');
            
            -- Create timestamp-based backup tables
            EXECUTE format('CREATE TABLE IF NOT EXISTS migration_users_backup_%s AS SELECT * FROM public.users', timestamp_suffix);
            EXECUTE format('CREATE TABLE IF NOT EXISTS migration_uploads_backup_%s AS SELECT * FROM public.uploads', timestamp_suffix);
            EXECUTE format('CREATE TABLE IF NOT EXISTS migration_entries_backup_%s AS SELECT * FROM public.sellout_entries2', timestamp_suffix);
            EXECUTE format('CREATE TABLE IF NOT EXISTS migration_products_backup_%s AS SELECT * FROM public.products', timestamp_suffix);
            
            result = jsonb_build_object(
                'backup_timestamp', now(),
                'timestamp_suffix', timestamp_suffix,
                'status', 'completed'
            );
            
            RETURN result;
        END;
        $$;
        """
        
        await db_service.execute(snapshot_function_sql, ())
        logger.info("✅ Created create_data_snapshot function")
        
        # Test the functions
        logger.info("Testing migration functions...")
        
        # Test validation
        validation_result = await db_service.fetch_one("SELECT validate_system_state() as state", ())
        logger.info(f"✅ System validation: {validation_result}")
        
        # Log initialization completion
        log_entry_sql = """
        INSERT INTO public.migration_log (phase, operation, status, details)
        VALUES (%s, %s, %s, %s)
        """
        
        await db_service.execute(log_entry_sql, (
            'phase_0',
            'infrastructure_initialization',
            'completed',
            '{"message": "Migration infrastructure successfully initialized"}'
        ))
        
        logger.info("🎉 Migration infrastructure initialized successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize migration infrastructure: {e}")
        
        # Log failure
        try:
            await db_service.execute(log_entry_sql, (
                'phase_0',
                'infrastructure_initialization',
                'failed',
                f'{{"error": "{str(e)}"}}'
            ))
        except:
            pass  # Don't fail if logging fails
        
        return False

if __name__ == "__main__":
    success = asyncio.run(initialize_migration_infrastructure())
    exit(0 if success else 1)