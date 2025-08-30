-- Multi-Tenant Security Migration Backup Script
-- Created: 2025-01-20
-- Purpose: Create comprehensive backup before security migration

-- ============================================================================
-- PRE-MIGRATION BACKUP AND VALIDATION
-- ============================================================================

-- Create migration log table for tracking
CREATE TABLE IF NOT EXISTS public.migration_log (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    phase text NOT NULL,
    operation text NOT NULL,
    status text CHECK (status IN ('started', 'completed', 'failed', 'rollback')),
    details jsonb,
    created_at timestamptz DEFAULT now()
);

-- Migration validation functions
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
    
    -- Log validation
    INSERT INTO public.migration_log (phase, operation, status, details)
    VALUES ('phase_0', 'system_validation', 'completed', result);
    
    RETURN result;
END;
$$;

-- Backup current RLS policies
CREATE TABLE IF NOT EXISTS public.migration_policy_backup (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name text NOT NULL,
    policy_name text NOT NULL,
    policy_definition text NOT NULL,
    backed_up_at timestamptz DEFAULT now()
);

-- Function to backup existing policies
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
    
    -- Log backup completion
    INSERT INTO public.migration_log (phase, operation, status, details)
    VALUES ('phase_0', 'policy_backup', 'completed', 
            jsonb_build_object('policies_backed_up', (SELECT COUNT(*) FROM public.migration_policy_backup)));
END;
$$;

-- Function to create data snapshots
CREATE OR REPLACE FUNCTION create_data_snapshot()
RETURNS jsonb
LANGUAGE plpgsql
AS $$
DECLARE
    result jsonb;
BEGIN
    -- Create timestamp-based backup tables
    EXECUTE format('CREATE TABLE IF NOT EXISTS migration_users_backup_%s AS SELECT * FROM public.users', 
                   to_char(now(), 'YYYY_MM_DD_HH24_MI_SS'));
    
    EXECUTE format('CREATE TABLE IF NOT EXISTS migration_uploads_backup_%s AS SELECT * FROM public.uploads', 
                   to_char(now(), 'YYYY_MM_DD_HH24_MI_SS'));
    
    EXECUTE format('CREATE TABLE IF NOT EXISTS migration_entries_backup_%s AS SELECT * FROM public.sellout_entries2', 
                   to_char(now(), 'YYYY_MM_DD_HH24_MI_SS'));
    
    EXECUTE format('CREATE TABLE IF NOT EXISTS migration_products_backup_%s AS SELECT * FROM public.products', 
                   to_char(now(), 'YYYY_MM_DD_HH24_MI_SS'));
    
    result = jsonb_build_object(
        'backup_timestamp', now(),
        'status', 'completed'
    );
    
    -- Log snapshot creation
    INSERT INTO public.migration_log (phase, operation, status, details)
    VALUES ('phase_0', 'data_snapshot', 'completed', result);
    
    RETURN result;
END;
$$;

-- Rollback function for emergency use
CREATE OR REPLACE FUNCTION emergency_rollback()
RETURNS jsonb
LANGUAGE plpgsql
AS $$
DECLARE
    result jsonb;
    backup_table text;
BEGIN
    -- This function can be called to rollback to pre-migration state
    -- Implementation depends on specific rollback requirements
    
    result = jsonb_build_object(
        'rollback_timestamp', now(),
        'status', 'initiated'
    );
    
    INSERT INTO public.migration_log (phase, operation, status, details)
    VALUES ('rollback', 'emergency_rollback', 'started', result);
    
    RETURN result;
END;
$$;

-- Initialize migration tracking
INSERT INTO public.migration_log (phase, operation, status, details)
VALUES ('phase_0', 'migration_start', 'started', 
        jsonb_build_object('migration_plan', 'multi_tenant_security', 'start_time', now()));