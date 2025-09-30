# Database Migrations

## How to Apply Migrations to Supabase

### Option 1: Supabase Dashboard (Recommended)
1. Go to your Supabase project dashboard
2. Navigate to **SQL Editor**
3. Click **New Query**
4. Copy and paste the contents of the migration file
5. Click **Run** to execute

### Option 2: Supabase CLI
```bash
# Install Supabase CLI if not already installed
npm install -g supabase

# Login to Supabase
supabase login

# Run the migration
supabase db execute -f database/migrations/update_dashboard_configs_constraint.sql
```

### Option 3: Direct PostgreSQL Connection
```bash
psql "postgresql://postgres:[YOUR-PASSWORD]@[YOUR-PROJECT-REF].supabase.co:5432/postgres" -f database/migrations/update_dashboard_configs_constraint.sql
```

## Current Migrations

### 2025-09-30: Update Dashboard Configs Constraint
**File**: `update_dashboard_configs_constraint.sql`
**Purpose**: Fix dashboard type validation to accept frontend values
**Status**: ⏳ Pending

This migration updates the CHECK constraint on the `dashboard_configs.dashboard_type` column to accept:
- `looker` (Google Looker Studio)
- `google_analytics` (Google Analytics)
- `tableau` (Tableau)
- `power_bi` (Power BI)
- `custom` (Custom dashboards)

**Before running**: Ensure no dashboards exist with old types (`powerbi`, `grafana`, `metabase`)
**After running**: Test dashboard creation/update from the UI

## Verification Steps

After applying the migration:

1. **Verify constraint was updated**:
```sql
SELECT conname, pg_get_constraintdef(oid)
FROM pg_constraint
WHERE conrelid = 'public.dashboard_configs'::regclass
AND conname = 'dashboard_configs_dashboard_type_check';
```

2. **Test insert with new values**:
```sql
INSERT INTO public.dashboard_configs (
  user_id, dashboard_name, dashboard_type, dashboard_url
) VALUES (
  auth.uid(),
  'Test Dashboard',
  'google_analytics',
  'https://analytics.google.com/test'
);
```

3. **Verify from UI**:
   - Open Analytics Dashboard
   - Click "Add New Dashboard"
   - Fill in form with Google Analytics type
   - Save and verify it persists after page refresh

## Rollback

If you need to rollback this migration:

```sql
ALTER TABLE public.dashboard_configs
DROP CONSTRAINT IF EXISTS dashboard_configs_dashboard_type_check;

ALTER TABLE public.dashboard_configs
ADD CONSTRAINT dashboard_configs_dashboard_type_check
CHECK (dashboard_type IN ('tableau', 'powerbi', 'grafana', 'looker', 'metabase', 'custom'));
```
