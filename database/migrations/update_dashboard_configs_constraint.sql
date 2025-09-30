-- Migration: Update dashboard_configs CHECK constraint to match frontend values
-- Date: 2025-09-30
-- Purpose: Fix dashboard type validation mismatch causing save failures

-- Drop the old constraint
ALTER TABLE public.dashboard_configs
DROP CONSTRAINT IF EXISTS dashboard_configs_dashboard_type_check;

-- Add the new constraint with frontend-compatible values
ALTER TABLE public.dashboard_configs
ADD CONSTRAINT dashboard_configs_dashboard_type_check
CHECK (dashboard_type IN ('looker', 'google_analytics', 'tableau', 'power_bi', 'custom'));

-- Verify the constraint was updated
SELECT conname, pg_get_constraintdef(oid)
FROM pg_constraint
WHERE conrelid = 'public.dashboard_configs'::regclass
AND conname = 'dashboard_configs_dashboard_type_check';
