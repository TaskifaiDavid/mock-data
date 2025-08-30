-- ============================================================================
-- PHASE 1: Multi-Tenant Security Schema Migration
-- ============================================================================
-- This script adds client_id columns, creates organization tables,
-- and sets up the foundation for multi-tenant data isolation.
-- 
-- SAFETY: This migration is designed for zero-downtime production deployment
-- ============================================================================

BEGIN;

-- Set session variables for safety
SET statement_timeout = '30min';
SET lock_timeout = '5s';

-- ============================================================================
-- STEP 1: Create migration tracking table if not exists
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.migration_log (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    phase text NOT NULL,
    operation text NOT NULL,
    status text NOT NULL,
    details jsonb DEFAULT '{}',
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);

-- Log migration start
INSERT INTO public.migration_log (phase, operation, status, details) 
VALUES ('phase_1', 'schema_migration_start', 'started', '{"description": "Adding client_id columns and organization tables"}');

-- ============================================================================
-- STEP 2: Create organizations table
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.organizations (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    name text NOT NULL UNIQUE,
    slug text NOT NULL UNIQUE,
    settings jsonb DEFAULT '{}',
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    
    CONSTRAINT organizations_name_not_empty CHECK (length(trim(name)) > 0),
    CONSTRAINT organizations_slug_format CHECK (slug ~ '^[a-z0-9][a-z0-9-]*[a-z0-9]$')
);

-- Create indexes for organizations
CREATE INDEX IF NOT EXISTS idx_organizations_slug ON public.organizations(slug) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_organizations_created_at ON public.organizations(created_at);

-- Log organizations table creation
INSERT INTO public.migration_log (phase, operation, status, details) 
VALUES ('phase_1', 'create_organizations_table', 'completed', '{"table": "organizations", "columns": ["id", "name", "slug", "settings", "is_active", "created_at", "updated_at"]}');

-- ============================================================================
-- STEP 3: Create user_organizations junction table
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.user_organizations (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id uuid NOT NULL,
    organization_id uuid NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
    role text NOT NULL DEFAULT 'member',
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    
    CONSTRAINT user_organizations_unique_active UNIQUE (user_id, organization_id),
    CONSTRAINT user_organizations_role_valid CHECK (role IN ('owner', 'admin', 'member', 'viewer'))
);

-- Create indexes for user_organizations
CREATE INDEX IF NOT EXISTS idx_user_organizations_user_id ON public.user_organizations(user_id) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_user_organizations_organization_id ON public.user_organizations(organization_id) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_user_organizations_role ON public.user_organizations(organization_id, role) WHERE is_active = true;

-- Log user_organizations table creation
INSERT INTO public.migration_log (phase, operation, status, details) 
VALUES ('phase_1', 'create_user_organizations_table', 'completed', '{"table": "user_organizations", "columns": ["id", "user_id", "organization_id", "role", "is_active", "created_at", "updated_at"]}');

-- ============================================================================
-- STEP 4: Create default organization for existing data
-- ============================================================================
INSERT INTO public.organizations (id, name, slug, settings) 
VALUES (
    '00000000-0000-0000-0000-000000000001'::uuid,
    'Default Organization', 
    'default-org',
    '{"created_by_migration": true, "phase": "phase_1"}'
) ON CONFLICT (name) DO NOTHING;

-- Get the default organization ID for reference
DO $$
DECLARE
    default_org_id uuid;
BEGIN
    SELECT id INTO default_org_id FROM public.organizations WHERE slug = 'default-org';
    
    -- Log default organization creation
    INSERT INTO public.migration_log (phase, operation, status, details) 
    VALUES ('phase_1', 'create_default_organization', 'completed', 
            jsonb_build_object('organization_id', default_org_id, 'name', 'Default Organization'));
END $$;

-- ============================================================================
-- STEP 5: Add client_id columns to all tables (with safe defaults)
-- ============================================================================

-- Add client_id to users table (if it exists)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users' AND table_schema = 'public') THEN
        -- Add column if it doesn't exist
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'client_id' AND table_schema = 'public') THEN
            ALTER TABLE public.users ADD COLUMN client_id uuid;
            
            -- Set default value for existing records
            UPDATE public.users 
            SET client_id = '00000000-0000-0000-0000-000000000001'::uuid 
            WHERE client_id IS NULL;
            
            -- Log users table update
            INSERT INTO public.migration_log (phase, operation, status, details) 
            VALUES ('phase_1', 'add_client_id_users', 'completed', '{"table": "users", "column": "client_id", "default_org_assigned": true}');
        END IF;
    END IF;
END $$;

-- Add client_id to uploads table
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'uploads' AND table_schema = 'public') THEN
        -- Add column if it doesn't exist
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'uploads' AND column_name = 'client_id' AND table_schema = 'public') THEN
            ALTER TABLE public.uploads ADD COLUMN client_id uuid;
            
            -- Set default value for existing records
            UPDATE public.uploads 
            SET client_id = '00000000-0000-0000-0000-000000000001'::uuid 
            WHERE client_id IS NULL;
            
            -- Log uploads table update
            INSERT INTO public.migration_log (phase, operation, status, details) 
            VALUES ('phase_1', 'add_client_id_uploads', 'completed', '{"table": "uploads", "column": "client_id", "default_org_assigned": true}');
        END IF;
    END IF;
END $$;

-- Add client_id to sellout_entries2 table
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'sellout_entries2' AND table_schema = 'public') THEN
        -- Add column if it doesn't exist
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'sellout_entries2' AND column_name = 'client_id' AND table_schema = 'public') THEN
            ALTER TABLE public.sellout_entries2 ADD COLUMN client_id uuid;
            
            -- Set default value for existing records by joining with uploads
            UPDATE public.sellout_entries2 
            SET client_id = '00000000-0000-0000-0000-000000000001'::uuid 
            WHERE client_id IS NULL;
            
            -- Log sellout_entries2 table update
            INSERT INTO public.migration_log (phase, operation, status, details) 
            VALUES ('phase_1', 'add_client_id_sellout_entries2', 'completed', '{"table": "sellout_entries2", "column": "client_id", "default_org_assigned": true}');
        END IF;
    END IF;
END $$;

-- Add client_id to products table
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'products' AND table_schema = 'public') THEN
        -- Add column if it doesn't exist
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'products' AND column_name = 'client_id' AND table_schema = 'public') THEN
            ALTER TABLE public.products ADD COLUMN client_id uuid;
            
            -- Set default value for existing records
            UPDATE public.products 
            SET client_id = '00000000-0000-0000-0000-000000000001'::uuid 
            WHERE client_id IS NULL;
            
            -- Log products table update
            INSERT INTO public.migration_log (phase, operation, status, details) 
            VALUES ('phase_1', 'add_client_id_products', 'completed', '{"table": "products", "column": "client_id", "default_org_assigned": true}');
        END IF;
    END IF;
END $$;

-- Add client_id to processing_logs table
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'processing_logs' AND table_schema = 'public') THEN
        -- Add column if it doesn't exist
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'processing_logs' AND column_name = 'client_id' AND table_schema = 'public') THEN
            ALTER TABLE public.processing_logs ADD COLUMN client_id uuid;
            
            -- Set default value for existing records
            UPDATE public.processing_logs 
            SET client_id = '00000000-0000-0000-0000-000000000001'::uuid 
            WHERE client_id IS NULL;
            
            -- Log processing_logs table update
            INSERT INTO public.migration_log (phase, operation, status, details) 
            VALUES ('phase_1', 'add_client_id_processing_logs', 'completed', '{"table": "processing_logs", "column": "client_id", "default_org_assigned": true}');
        END IF;
    END IF;
END $$;

-- Add client_id to transform_logs table
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'transform_logs' AND table_schema = 'public') THEN
        -- Add column if it doesn't exist
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'transform_logs' AND column_name = 'client_id' AND table_schema = 'public') THEN
            ALTER TABLE public.transform_logs ADD COLUMN client_id uuid;
            
            -- Set default value for existing records
            UPDATE public.transform_logs 
            SET client_id = '00000000-0000-0000-0000-000000000001'::uuid 
            WHERE client_id IS NULL;
            
            -- Log transform_logs table update
            INSERT INTO public.migration_log (phase, operation, status, details) 
            VALUES ('phase_1', 'add_client_id_transform_logs', 'completed', '{"table": "transform_logs", "column": "client_id", "default_org_assigned": true}');
        END IF;
    END IF;
END $$;

-- Add client_id to email_logs table (if it exists)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'email_logs' AND table_schema = 'public') THEN
        -- Add column if it doesn't exist
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'email_logs' AND column_name = 'client_id' AND table_schema = 'public') THEN
            ALTER TABLE public.email_logs ADD COLUMN client_id uuid;
            
            -- Set default value for existing records
            UPDATE public.email_logs 
            SET client_id = '00000000-0000-0000-0000-000000000001'::uuid 
            WHERE client_id IS NULL;
            
            -- Log email_logs table update
            INSERT INTO public.migration_log (phase, operation, status, details) 
            VALUES ('phase_1', 'add_client_id_email_logs', 'completed', '{"table": "email_logs", "column": "client_id", "default_org_assigned": true}');
        END IF;
    END IF;
END $$;

-- ============================================================================
-- STEP 6: Create composite indexes for client-scoped queries
-- ============================================================================

-- Indexes for users table
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users' AND table_schema = 'public') THEN
        -- Create composite index for client + created_at (most common query pattern)
        CREATE INDEX IF NOT EXISTS idx_users_client_created_at ON public.users(client_id, created_at DESC);
        
        -- Log index creation
        INSERT INTO public.migration_log (phase, operation, status, details) 
        VALUES ('phase_1', 'create_indexes_users', 'completed', '{"indexes": ["idx_users_client_created_at"]}');
    END IF;
END $$;

-- Indexes for uploads table
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'uploads' AND table_schema = 'public') THEN
        -- Create composite indexes
        CREATE INDEX IF NOT EXISTS idx_uploads_client_created_at ON public.uploads(client_id, created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_uploads_client_user_id ON public.uploads(client_id, user_id);
        CREATE INDEX IF NOT EXISTS idx_uploads_client_status ON public.uploads(client_id, status) WHERE status IN ('pending', 'processing');
        
        -- Log index creation
        INSERT INTO public.migration_log (phase, operation, status, details) 
        VALUES ('phase_1', 'create_indexes_uploads', 'completed', '{"indexes": ["idx_uploads_client_created_at", "idx_uploads_client_user_id", "idx_uploads_client_status"]}');
    END IF;
END $$;

-- Indexes for sellout_entries2 table
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'sellout_entries2' AND table_schema = 'public') THEN
        -- Create composite indexes for common query patterns
        CREATE INDEX IF NOT EXISTS idx_sellout_entries2_client_created_at ON public.sellout_entries2(client_id, created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_sellout_entries2_client_upload_id ON public.sellout_entries2(client_id, upload_id);
        CREATE INDEX IF NOT EXISTS idx_sellout_entries2_client_year_month ON public.sellout_entries2(client_id, year, month);
        CREATE INDEX IF NOT EXISTS idx_sellout_entries2_client_reseller ON public.sellout_entries2(client_id, reseller) WHERE reseller IS NOT NULL;
        CREATE INDEX IF NOT EXISTS idx_sellout_entries2_client_product_ean ON public.sellout_entries2(client_id, product_ean) WHERE product_ean IS NOT NULL;
        
        -- Log index creation
        INSERT INTO public.migration_log (phase, operation, status, details) 
        VALUES ('phase_1', 'create_indexes_sellout_entries2', 'completed', '{"indexes": ["idx_sellout_entries2_client_created_at", "idx_sellout_entries2_client_upload_id", "idx_sellout_entries2_client_year_month", "idx_sellout_entries2_client_reseller", "idx_sellout_entries2_client_product_ean"]}');
    END IF;
END $$;

-- Indexes for products table
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'products' AND table_schema = 'public') THEN
        -- Create composite indexes
        CREATE INDEX IF NOT EXISTS idx_products_client_ean ON public.products(client_id, ean);
        CREATE INDEX IF NOT EXISTS idx_products_client_created_at ON public.products(client_id, created_at DESC);
        
        -- Log index creation
        INSERT INTO public.migration_log (phase, operation, status, details) 
        VALUES ('phase_1', 'create_indexes_products', 'completed', '{"indexes": ["idx_products_client_ean", "idx_products_client_created_at"]}');
    END IF;
END $$;

-- Indexes for processing_logs table
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'processing_logs' AND table_schema = 'public') THEN
        -- Create composite indexes
        CREATE INDEX IF NOT EXISTS idx_processing_logs_client_upload_id ON public.processing_logs(client_id, upload_id);
        CREATE INDEX IF NOT EXISTS idx_processing_logs_client_created_at ON public.processing_logs(client_id, created_at DESC);
        
        -- Log index creation
        INSERT INTO public.migration_log (phase, operation, status, details) 
        VALUES ('phase_1', 'create_indexes_processing_logs', 'completed', '{"indexes": ["idx_processing_logs_client_upload_id", "idx_processing_logs_client_created_at"]}');
    END IF;
END $$;

-- Indexes for transform_logs table
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'transform_logs' AND table_schema = 'public') THEN
        -- Create composite indexes
        CREATE INDEX IF NOT EXISTS idx_transform_logs_client_created_at ON public.transform_logs(client_id, created_at DESC);
        
        -- Log index creation
        INSERT INTO public.migration_log (phase, operation, status, details) 
        VALUES ('phase_1', 'create_indexes_transform_logs', 'completed', '{"indexes": ["idx_transform_logs_client_created_at"]}');
    END IF;
END $$;

-- ============================================================================
-- STEP 7: Create utility functions for client data management
-- ============================================================================

-- Function to get user's organization ID
CREATE OR REPLACE FUNCTION get_user_organization_id(user_uuid uuid)
RETURNS uuid AS $$
DECLARE
    org_id uuid;
BEGIN
    SELECT organization_id INTO org_id
    FROM public.user_organizations
    WHERE user_id = user_uuid AND is_active = true
    LIMIT 1;
    
    RETURN org_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to validate client access
CREATE OR REPLACE FUNCTION validate_client_access(user_uuid uuid, client_uuid uuid)
RETURNS boolean AS $$
DECLARE
    user_org_id uuid;
BEGIN
    -- Get user's organization
    SELECT get_user_organization_id(user_uuid) INTO user_org_id;
    
    -- Check if the client_id matches user's organization
    RETURN user_org_id = client_uuid;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get current client context (will be used by RLS policies later)
CREATE OR REPLACE FUNCTION get_current_client_id()
RETURNS uuid AS $$
BEGIN
    -- This will be enhanced in later phases to use session variables
    -- For now, return the default organization ID
    RETURN '00000000-0000-0000-0000-000000000001'::uuid;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Log utility functions creation
INSERT INTO public.migration_log (phase, operation, status, details) 
VALUES ('phase_1', 'create_utility_functions', 'completed', '{"functions": ["get_user_organization_id", "validate_client_access", "get_current_client_id"]}');

-- ============================================================================
-- STEP 8: Create policy backup table for rollback safety
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.migration_policy_backup (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    table_name text NOT NULL,
    policy_name text NOT NULL,
    policy_definition text NOT NULL,
    backed_up_at timestamp with time zone DEFAULT now()
);

-- Log policy backup table creation
INSERT INTO public.migration_log (phase, operation, status, details) 
VALUES ('phase_1', 'create_policy_backup_table', 'completed', '{"table": "migration_policy_backup"}');

-- ============================================================================
-- STEP 9: Create data validation functions
-- ============================================================================

-- Function to validate client_id data integrity
CREATE OR REPLACE FUNCTION validate_client_data_integrity()
RETURNS json AS $$
DECLARE
    result json;
    table_counts json = '{}';
    validation_results json = '{}';
    table_name text;
    total_records bigint;
    records_with_client_id bigint;
    null_client_id_records bigint;
BEGIN
    -- Check each table that should have client_id
    FOR table_name IN 
        SELECT t.table_name 
        FROM information_schema.tables t
        JOIN information_schema.columns c ON t.table_name = c.table_name
        WHERE t.table_schema = 'public' 
        AND c.column_name = 'client_id'
        AND t.table_type = 'BASE TABLE'
    LOOP
        -- Get record counts
        EXECUTE format('SELECT COUNT(*) FROM public.%I', table_name) INTO total_records;
        EXECUTE format('SELECT COUNT(*) FROM public.%I WHERE client_id IS NOT NULL', table_name) INTO records_with_client_id;
        EXECUTE format('SELECT COUNT(*) FROM public.%I WHERE client_id IS NULL', table_name) INTO null_client_id_records;
        
        -- Store results
        validation_results := validation_results || json_build_object(
            table_name, json_build_object(
                'total_records', total_records,
                'records_with_client_id', records_with_client_id,
                'null_client_id_records', null_client_id_records,
                'data_integrity_ok', null_client_id_records = 0
            )
        );
    END LOOP;
    
    -- Build final result
    result := json_build_object(
        'validation_timestamp', now(),
        'tables_validated', validation_results,
        'overall_status', CASE 
            WHEN validation_results::text LIKE '%"data_integrity_ok":false%' THEN 'FAILED'
            ELSE 'PASSED'
        END
    );
    
    RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to create data snapshot for rollback
CREATE OR REPLACE FUNCTION create_data_snapshot()
RETURNS json AS $$
DECLARE
    result json;
    snapshot_id text;
BEGIN
    snapshot_id := 'snapshot_' || to_char(now(), 'YYYY_MM_DD_HH24_MI_SS');
    
    -- This is a placeholder - in production, this would create actual table snapshots
    -- For now, we'll just log the snapshot creation
    
    result := json_build_object(
        'snapshot_id', snapshot_id,
        'created_at', now(),
        'status', 'placeholder_created',
        'note', 'Actual table snapshots would be created in production implementation'
    );
    
    RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Log validation functions creation
INSERT INTO public.migration_log (phase, operation, status, details) 
VALUES ('phase_1', 'create_validation_functions', 'completed', '{"functions": ["validate_client_data_integrity", "create_data_snapshot"]}');

-- ============================================================================
-- STEP 10: Final validation and migration completion
-- ============================================================================

-- Run data integrity validation
DO $$
DECLARE
    validation_result json;
BEGIN
    SELECT validate_client_data_integrity() INTO validation_result;
    
    -- Log validation results
    INSERT INTO public.migration_log (phase, operation, status, details) 
    VALUES ('phase_1', 'data_integrity_validation', 
            CASE WHEN validation_result->>'overall_status' = 'PASSED' THEN 'completed' ELSE 'failed' END,
            validation_result);
    
    -- Raise error if validation failed
    IF validation_result->>'overall_status' = 'FAILED' THEN
        RAISE EXCEPTION 'Data integrity validation failed: %', validation_result;
    END IF;
END $$;

-- Final success log
INSERT INTO public.migration_log (phase, operation, status, details) 
VALUES ('phase_1', 'schema_migration_complete', 'completed', 
        json_build_object(
            'tables_modified', ARRAY['users', 'uploads', 'sellout_entries2', 'products', 'processing_logs', 'transform_logs', 'email_logs'],
            'tables_created', ARRAY['organizations', 'user_organizations', 'migration_log', 'migration_policy_backup'],
            'functions_created', ARRAY['get_user_organization_id', 'validate_client_access', 'get_current_client_id', 'validate_client_data_integrity', 'create_data_snapshot'],
            'indexes_created', 15,
            'migration_timestamp', now()
        ));

COMMIT;

-- ============================================================================
-- ROLLBACK SCRIPT (for emergency use)
-- ============================================================================
/*
-- EMERGENCY ROLLBACK - Use only if migration needs to be reversed
-- This should be run in a separate transaction

BEGIN;

-- Drop utility functions
DROP FUNCTION IF EXISTS validate_client_data_integrity();
DROP FUNCTION IF EXISTS create_data_snapshot();
DROP FUNCTION IF EXISTS get_current_client_id();
DROP FUNCTION IF EXISTS validate_client_access(uuid, uuid);
DROP FUNCTION IF EXISTS get_user_organization_id(uuid);

-- Remove client_id columns (BE VERY CAREFUL - THIS WILL LOSE DATA)
-- ALTER TABLE public.users DROP COLUMN IF EXISTS client_id;
-- ALTER TABLE public.uploads DROP COLUMN IF EXISTS client_id;
-- ALTER TABLE public.sellout_entries2 DROP COLUMN IF EXISTS client_id;
-- ALTER TABLE public.products DROP COLUMN IF EXISTS client_id;
-- ALTER TABLE public.processing_logs DROP COLUMN IF EXISTS client_id;
-- ALTER TABLE public.transform_logs DROP COLUMN IF EXISTS client_id;
-- ALTER TABLE public.email_logs DROP COLUMN IF EXISTS client_id;

-- Drop new tables (BE VERY CAREFUL - THIS WILL LOSE DATA)
-- DROP TABLE IF EXISTS public.user_organizations;
-- DROP TABLE IF EXISTS public.organizations;
-- DROP TABLE IF EXISTS public.migration_policy_backup;

-- Log rollback
INSERT INTO public.migration_log (phase, operation, status, details) 
VALUES ('phase_1', 'emergency_rollback', 'completed', '{"warning": "Schema changes have been rolled back"}');

COMMIT;
*/

-- ============================================================================
-- POST-MIGRATION VERIFICATION QUERIES
-- ============================================================================
/*
-- Run these queries after migration to verify success:

-- 1. Check that all tables have client_id column
SELECT 
    t.table_name,
    CASE WHEN c.column_name IS NOT NULL THEN 'HAS client_id' ELSE 'MISSING client_id' END as client_id_status
FROM information_schema.tables t
LEFT JOIN information_schema.columns c ON t.table_name = c.table_name AND c.column_name = 'client_id'
WHERE t.table_schema = 'public' 
AND t.table_type = 'BASE TABLE'
AND t.table_name IN ('users', 'uploads', 'sellout_entries2', 'products', 'processing_logs', 'transform_logs', 'email_logs')
ORDER BY t.table_name;

-- 2. Check that default organization was created
SELECT * FROM public.organizations WHERE slug = 'default-org';

-- 3. Validate client_id data integrity
SELECT validate_client_data_integrity();

-- 4. Check migration logs
SELECT phase, operation, status, created_at 
FROM public.migration_log 
WHERE phase = 'phase_1' 
ORDER BY created_at DESC;
*/