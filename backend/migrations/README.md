# Phase 1: Multi-Tenant Security Migration

This directory contains the Phase 1 migration scripts for implementing multi-tenant security in the application. Phase 1 establishes the foundational schema changes required for client data isolation.

## 🎯 Migration Overview

Phase 1 transforms the single-tenant database into a multi-tenant architecture by:

1. **Adding client_id columns** to all data tables
2. **Creating organization management** tables and relationships
3. **Setting up indexes** for efficient client-scoped queries
4. **Providing utility functions** for client data management
5. **Ensuring backward compatibility** with existing application code

## 📁 Files in this Directory

### Core Migration Files
- **`phase_1_multitenant_schema.sql`** - Main migration script with all schema changes
- **`phase_1_rollback.sql`** - Complete rollback script (⚠️ DESTRUCTIVE)
- **`execute_phase_1.py`** - Safe execution script with monitoring and validation

### Documentation
- **`README.md`** - This file
- **`migration_plan.md`** - Detailed implementation plan and timeline

## 🚀 Quick Start

### Prerequisites
- PostgreSQL 12+ database
- Python 3.8+ with required dependencies
- Database backup (MANDATORY before running)
- Maintenance window scheduled (recommended)

### Basic Execution

```bash
# 1. First, run a dry-run to see what will happen
python execute_phase_1.py --dry-run

# 2. Execute the migration (with safety prompts)
python execute_phase_1.py

# 3. For automated deployment (skip prompts)
python execute_phase_1.py --force
```

### Emergency Rollback

```bash
# DANGER: This permanently deletes all multi-tenant data
python execute_phase_1.py --rollback --force
```

## 🔧 What Phase 1 Does

### 1. Creates New Tables

#### `organizations`
```sql
CREATE TABLE public.organizations (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name text NOT NULL UNIQUE,
    slug text NOT NULL UNIQUE,
    settings jsonb DEFAULT '{}',
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);
```

#### `user_organizations`
```sql
CREATE TABLE public.user_organizations (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL,
    organization_id uuid NOT NULL REFERENCES organizations(id),
    role text NOT NULL DEFAULT 'member',
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);
```

### 2. Adds client_id Columns

The following tables get a new `client_id uuid` column:
- `users` - Links users to their organization
- `uploads` - Isolates file uploads by client
- `sellout_entries2` - Isolates sales data by client
- `products` - Isolates product catalogs by client
- `processing_logs` - Isolates processing history by client
- `transform_logs` - Isolates transformation logs by client
- `email_logs` - Isolates email history by client

### 3. Creates Performance Indexes

Composite indexes for efficient multi-tenant queries:
```sql
-- Example indexes created
CREATE INDEX idx_uploads_client_created_at ON uploads(client_id, created_at DESC);
CREATE INDEX idx_sellout_entries2_client_year_month ON sellout_entries2(client_id, year, month);
CREATE INDEX idx_products_client_ean ON products(client_id, ean);
```

### 4. Provides Utility Functions

- `get_user_organization_id(uuid)` - Get user's organization
- `validate_client_access(uuid, uuid)` - Validate user can access client data
- `validate_client_data_integrity()` - Check migration data integrity

## 📊 Data Migration Strategy

### Existing Data Handling
1. **Default Organization**: A "Default Organization" is created for all existing data
2. **Backward Compatibility**: All existing records are assigned to this default organization
3. **Zero Downtime**: Migration can run while application is live (with proper precautions)

### Data Validation
The migration includes comprehensive validation:
- Ensures all records have `client_id` values
- Verifies referential integrity
- Provides detailed logging of all changes

## 🛡️ Safety Features

### Pre-Migration Checks
- Database connectivity validation
- Existing schema analysis
- Data volume assessment
- Active transaction detection

### During Migration
- Transactional execution (all-or-nothing)
- Comprehensive logging
- Progress monitoring
- Rollback on any failure

### Post-Migration
- Data integrity validation
- Index usage verification
- Performance baseline establishment

## 📋 Migration Monitoring

### Migration Logs
All operations are logged to the `migration_log` table:

```sql
SELECT phase, operation, status, details, created_at 
FROM migration_log 
WHERE phase = 'phase_1' 
ORDER BY created_at DESC;
```

### Validation Queries
After migration, run these to verify success:

```sql
-- Check client_id columns exist
SELECT table_name, column_name 
FROM information_schema.columns 
WHERE column_name = 'client_id' AND table_schema = 'public';

-- Verify default organization
SELECT * FROM organizations WHERE slug = 'default-org';

-- Check data integrity
SELECT validate_client_data_integrity();
```

## ⚠️ Important Warnings

### Before Migration
1. **BACKUP YOUR DATABASE** - This cannot be stressed enough
2. **Test on staging** - Run the complete migration on a staging environment first
3. **Schedule maintenance** - Plan for potential downtime if needed
4. **Update monitoring** - Ensure your monitoring can handle the new schema

### After Migration
1. **Update application code** - Future phases will require code changes
2. **Monitor performance** - New indexes may change query plans
3. **Plan next phases** - This is just the first step in multi-tenant implementation

## 🔄 Rollback Considerations

### When to Rollback
- Migration validation fails
- Unexpected performance issues
- Application compatibility problems
- Data integrity concerns

### Rollback Process
The rollback script will:
1. Drop all utility functions
2. Remove all new indexes
3. Drop `client_id` columns (⚠️ **DATA LOSS**)
4. Drop organization tables (⚠️ **DATA LOSS**)

### ⚠️ CRITICAL WARNING
**The rollback process PERMANENTLY DELETES DATA**
- All `client_id` values are lost
- All organization relationships are lost
- This operation is IRREVERSIBLE

## 🚦 Next Steps (Future Phases)

After Phase 1 completion:
1. **Phase 2**: Implement Row-Level Security (RLS) policies
2. **Phase 3**: Update application code for multi-tenant context
3. **Phase 4**: Implement organization management UI
4. **Phase 5**: Add client isolation enforcement
5. **Phase 6**: Performance optimization and monitoring
6. **Phase 7**: Final validation and go-live

## 🆘 Troubleshooting

### Common Issues

#### Migration Fails with Permission Errors
```bash
# Ensure you're using the service role user with sufficient privileges
export SUPABASE_SERVICE_ROLE_PASSWORD="your-service-role-password"
```

#### Client_id Columns Not Added
Check the migration log for specific table errors:
```sql
SELECT * FROM migration_log 
WHERE operation LIKE '%client_id%' AND status = 'failed';
```

#### Performance Issues After Migration
Monitor slow queries and index usage:
```sql
-- Check for missing indexes
SELECT schemaname, tablename, indexname 
FROM pg_indexes 
WHERE tablename IN ('uploads', 'sellout_entries2', 'products')
AND indexname LIKE '%client%';
```

### Getting Help
1. Check the migration logs first
2. Verify prerequisites are met
3. Test on a staging environment
4. Review the validation queries
5. Check application logs for compatibility issues

## 📞 Support

For migration support:
- Review the migration logs in `migration_log` table
- Check the application logs for errors
- Verify the database schema matches expectations
- Test a few critical application flows

Remember: **Better to be safe than sorry** - always test thoroughly before production deployment.