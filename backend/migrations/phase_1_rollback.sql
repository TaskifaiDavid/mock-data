-- ============================================================================
-- PHASE 1 ROLLBACK: Multi-Tenant Security Schema Rollback
-- ============================================================================
-- CRITICAL WARNING: This script will PERMANENTLY DELETE data and schema changes
-- Only run this script if you are certain you need to rollback Phase 1 changes
-- Make sure you have proper backups before executing this script
-- ============================================================================

-- Verification step - display current migration status before rollback
SELECT 
    'CURRENT MIGRATION STATUS' as info,
    phase, 
    operation, 
    status, 
    created_at,
    details
FROM public.migration_log 
WHERE phase = 'phase_1' 
ORDER BY created_at DESC
LIMIT 10;

-- Pause for manual confirmation
\echo '============================================================================'
\echo 'WARNING: This rollback script will permanently delete:'
\echo '1. All client_id columns from existing tables'
\echo '2. All organization and user_organization data'
\echo '3. All utility functions created in Phase 1'
\echo '4. All indexes created for multi-tenant queries'
\echo ''
\echo 'Make sure you have proper backups and really want to proceed.'
\echo 'Press Ctrl+C to cancel or any key to continue...'
\pause

BEGIN;

-- Set session variables for safety
SET statement_timeout = '30min';
SET lock_timeout = '5s';

-- Log rollback start
INSERT INTO public.migration_log (phase, operation, status, details) 
VALUES ('phase_1', 'rollback_start', 'started', '{"warning": "Beginning Phase 1 rollback - data will be permanently deleted"}');

-- ============================================================================
-- STEP 1: Drop all utility functions
-- ============================================================================

-- Drop validation functions
DROP FUNCTION IF EXISTS validate_client_data_integrity() CASCADE;
DROP FUNCTION IF EXISTS create_data_snapshot() CASCADE;

-- Drop client management functions
DROP FUNCTION IF EXISTS get_current_client_id() CASCADE;
DROP FUNCTION IF EXISTS validate_client_access(uuid, uuid) CASCADE;
DROP FUNCTION IF EXISTS get_user_organization_id(uuid) CASCADE;

-- Log function removal
INSERT INTO public.migration_log (phase, operation, status, details) 
VALUES ('phase_1', 'rollback_drop_functions', 'completed', '{"functions_dropped": ["validate_client_data_integrity", "create_data_snapshot", "get_current_client_id", "validate_client_access", "get_user_organization_id"]}');

-- ============================================================================
-- STEP 2: Drop all client_id related indexes
-- ============================================================================

-- Drop indexes from users table
DROP INDEX IF EXISTS public.idx_users_client_created_at;

-- Drop indexes from uploads table
DROP INDEX IF EXISTS public.idx_uploads_client_created_at;
DROP INDEX IF EXISTS public.idx_uploads_client_user_id;
DROP INDEX IF EXISTS public.idx_uploads_client_status;

-- Drop indexes from sellout_entries2 table
DROP INDEX IF EXISTS public.idx_sellout_entries2_client_created_at;
DROP INDEX IF EXISTS public.idx_sellout_entries2_client_upload_id;
DROP INDEX IF EXISTS public.idx_sellout_entries2_client_year_month;
DROP INDEX IF EXISTS public.idx_sellout_entries2_client_reseller;
DROP INDEX IF EXISTS public.idx_sellout_entries2_client_product_ean;

-- Drop indexes from products table
DROP INDEX IF EXISTS public.idx_products_client_ean;
DROP INDEX IF EXISTS public.idx_products_client_created_at;

-- Drop indexes from processing_logs table
DROP INDEX IF EXISTS public.idx_processing_logs_client_upload_id;
DROP INDEX IF EXISTS public.idx_processing_logs_client_created_at;

-- Drop indexes from transform_logs table
DROP INDEX IF EXISTS public.idx_transform_logs_client_created_at;

-- Drop indexes from organizations table
DROP INDEX IF EXISTS public.idx_organizations_slug;
DROP INDEX IF EXISTS public.idx_organizations_created_at;

-- Drop indexes from user_organizations table
DROP INDEX IF EXISTS public.idx_user_organizations_user_id;
DROP INDEX IF EXISTS public.idx_user_organizations_organization_id;
DROP INDEX IF EXISTS public.idx_user_organizations_role;

-- Log index removal
INSERT INTO public.migration_log (phase, operation, status, details) 
VALUES ('phase_1', 'rollback_drop_indexes', 'completed', '{"indexes_dropped": 18, "note": "All client_id related indexes removed"}');

-- ============================================================================
-- STEP 3: Remove client_id columns from all tables
-- ============================================================================
-- WARNING: This step will PERMANENTLY DELETE the client_id data

-- Remove client_id from users table
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'client_id' AND table_schema = 'public') THEN
        ALTER TABLE public.users DROP COLUMN client_id;
        INSERT INTO public.migration_log (phase, operation, status, details) 
        VALUES ('phase_1', 'rollback_remove_client_id_users', 'completed', '{"table": "users", "column_dropped": "client_id"}');
    END IF;
END $$;

-- Remove client_id from uploads table
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'uploads' AND column_name = 'client_id' AND table_schema = 'public') THEN
        ALTER TABLE public.uploads DROP COLUMN client_id;
        INSERT INTO public.migration_log (phase, operation, status, details) 
        VALUES ('phase_1', 'rollback_remove_client_id_uploads', 'completed', '{"table": "uploads", "column_dropped": "client_id"}');
    END IF;
END $$;

-- Remove client_id from sellout_entries2 table
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'sellout_entries2' AND column_name = 'client_id' AND table_schema = 'public') THEN
        ALTER TABLE public.sellout_entries2 DROP COLUMN client_id;
        INSERT INTO public.migration_log (phase, operation, status, details) 
        VALUES ('phase_1', 'rollback_remove_client_id_sellout_entries2', 'completed', '{"table": "sellout_entries2", "column_dropped": "client_id"}');
    END IF;
END $$;

-- Remove client_id from products table
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'products' AND column_name = 'client_id' AND table_schema = 'public') THEN
        ALTER TABLE public.products DROP COLUMN client_id;
        INSERT INTO public.migration_log (phase, operation, status, details) 
        VALUES ('phase_1', 'rollback_remove_client_id_products', 'completed', '{"table": "products", "column_dropped": "client_id"}');
    END IF;
END $$;

-- Remove client_id from processing_logs table
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'processing_logs' AND column_name = 'client_id' AND table_schema = 'public') THEN
        ALTER TABLE public.processing_logs DROP COLUMN client_id;
        INSERT INTO public.migration_log (phase, operation, status, details) 
        VALUES ('phase_1', 'rollback_remove_client_id_processing_logs', 'completed', '{"table": "processing_logs", "column_dropped": "client_id"}');
    END IF;
END $$;

-- Remove client_id from transform_logs table
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'transform_logs' AND column_name = 'client_id' AND table_schema = 'public') THEN
        ALTER TABLE public.transform_logs DROP COLUMN client_id;
        INSERT INTO public.migration_log (phase, operation, status, details) 
        VALUES ('phase_1', 'rollback_remove_client_id_transform_logs', 'completed', '{"table": "transform_logs", "column_dropped": "client_id"}');
    END IF;
END $$;

-- Remove client_id from email_logs table
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'email_logs' AND column_name = 'client_id' AND table_schema = 'public') THEN
        ALTER TABLE public.email_logs DROP COLUMN client_id;
        INSERT INTO public.migration_log (phase, operation, status, details) 
        VALUES ('phase_1', 'rollback_remove_client_id_email_logs', 'completed', '{"table": "email_logs", "column_dropped": "client_id"}');
    END IF;
END $$;

-- ============================================================================
-- STEP 4: Drop multi-tenant tables
-- ============================================================================
-- WARNING: This step will PERMANENTLY DELETE all organization data

-- Count records before deletion for logging
DO $$
DECLARE
    user_org_count integer := 0;
    org_count integer := 0;
BEGIN
    -- Count user_organizations records
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'user_organizations' AND table_schema = 'public') THEN
        SELECT COUNT(*) INTO user_org_count FROM public.user_organizations;
    END IF;
    
    -- Count organizations records
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'organizations' AND table_schema = 'public') THEN
        SELECT COUNT(*) INTO org_count FROM public.organizations;
    END IF;
    
    -- Drop user_organizations table
    DROP TABLE IF EXISTS public.user_organizations CASCADE;
    
    -- Drop organizations table
    DROP TABLE IF EXISTS public.organizations CASCADE;
    
    -- Log table removal
    INSERT INTO public.migration_log (phase, operation, status, details) 
    VALUES ('phase_1', 'rollback_drop_tables', 'completed', 
            json_build_object(
                'tables_dropped', ARRAY['user_organizations', 'organizations'],
                'user_organizations_records_deleted', user_org_count,
                'organizations_records_deleted', org_count,
                'warning', 'All organization and user-organization relationship data permanently deleted'
            ));
END $$;

-- ============================================================================
-- STEP 5: Clean up migration infrastructure (optional)
-- ============================================================================
-- Drop policy backup table (uncomment if you want to remove completely)
-- DROP TABLE IF EXISTS public.migration_policy_backup CASCADE;

-- ============================================================================
-- STEP 6: Final rollback validation and logging
-- ============================================================================

-- Verify that client_id columns have been removed
DO $$
DECLARE
    remaining_client_id_columns integer := 0;
    table_list text[];
BEGIN
    -- Check for any remaining client_id columns
    SELECT COUNT(*), array_agg(table_name)
    INTO remaining_client_id_columns, table_list
    FROM information_schema.columns 
    WHERE column_name = 'client_id' 
    AND table_schema = 'public'
    AND table_name IN ('users', 'uploads', 'sellout_entries2', 'products', 'processing_logs', 'transform_logs', 'email_logs');
    
    -- Log validation results
    INSERT INTO public.migration_log (phase, operation, status, details) 
    VALUES ('phase_1', 'rollback_validation', 
            CASE WHEN remaining_client_id_columns = 0 THEN 'completed' ELSE 'failed' END,
            json_build_object(
                'remaining_client_id_columns', remaining_client_id_columns,
                'tables_with_client_id', COALESCE(table_list, ARRAY[]::text[])
            ));
    
    -- Raise error if validation failed
    IF remaining_client_id_columns > 0 THEN
        RAISE EXCEPTION 'Rollback validation failed: % tables still have client_id columns: %', 
                       remaining_client_id_columns, array_to_string(table_list, ', ');
    END IF;
END $$;

-- Final rollback completion log
INSERT INTO public.migration_log (phase, operation, status, details) 
VALUES ('phase_1', 'rollback_complete', 'completed', 
        json_build_object(
            'rollback_timestamp', now(),
            'warning', 'Phase 1 multi-tenant schema changes have been completely rolled back',
            'data_loss', 'All client_id columns and organization data permanently deleted',
            'recommendation', 'Review application code to ensure it still works without client_id columns'
        ));

COMMIT;

-- ============================================================================
-- POST-ROLLBACK VERIFICATION QUERIES
-- ============================================================================
\echo '============================================================================'
\echo 'POST-ROLLBACK VERIFICATION'
\echo '============================================================================'

-- 1. Verify no client_id columns remain
\echo 'Checking for remaining client_id columns...'
SELECT 
    table_name,
    'STILL HAS client_id - ROLLBACK FAILED' as status
FROM information_schema.columns 
WHERE column_name = 'client_id' 
AND table_schema = 'public'
AND table_name IN ('users', 'uploads', 'sellout_entries2', 'products', 'processing_logs', 'transform_logs', 'email_logs');

-- 2. Verify organization tables are gone
\echo 'Checking for organization tables...'
SELECT 
    table_name,
    'TABLE STILL EXISTS - ROLLBACK FAILED' as status
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('organizations', 'user_organizations');

-- 3. Show rollback log entries
\echo 'Rollback operations log:'
SELECT 
    operation,
    status,
    created_at,
    details->>'warning' as warning
FROM public.migration_log 
WHERE phase = 'phase_1' AND operation LIKE 'rollback%'
ORDER BY created_at DESC;

\echo '============================================================================'
\echo 'ROLLBACK COMPLETE'
\echo 'Verify your application still functions correctly without multi-tenant support'
\echo '============================================================================'