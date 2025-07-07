# Sellout_Entries2 Table Analysis

## Plan
1. ✅ Search for schema files that define sellout_entries2 table structure
2. ✅ Look for SQL migration files or database setup scripts
3. ✅ Find examples of queries against sellout_entries2 table
4. ✅ Determine if sellout_entries2 table exists and has data
5. ✅ Document findings and table structure

## Findings

### 1. Table Structure

The `sellout_entries2` table has the following structure:

```sql
CREATE TABLE IF NOT EXISTS public.sellout_entries2 (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  product_ean text NULL,
  month integer NULL,
  year integer NULL,
  quantity integer NULL,
  sales_lc text NULL,
  sales_eur numeric NULL,
  currency text NULL,
  created_at timestamp without time zone NULL DEFAULT now(),
  reseller text NULL,
  functional_name text NULL,
  upload_id uuid NULL,
  CONSTRAINT sellout_entries2_pkey PRIMARY KEY (id),
  CONSTRAINT sellout_entries2_product_ean_fkey FOREIGN KEY (product_ean) REFERENCES products (ean),
  CONSTRAINT sellout_entries2_upload_id_fkey FOREIGN KEY (upload_id) REFERENCES uploads (id) ON DELETE SET NULL,
  CONSTRAINT sellout_entries_month_check CHECK (((month >= 1) AND (month <= 12))),
  CONSTRAINT sellout_entries_year_check CHECK ((year >= 2000))
);
```

### 2. Schema Files Found

- **Primary Schema**: `/home/david/cursor_project/database/schema.sql`
  - Contains commented-out CREATE TABLE statement for `sellout_entries2` 
  - Includes indexes and RLS policies
  - Has an ALTER TABLE statement to add `upload_id` column

- **Additional Schema**: `/home/david/cursor_project/database/email_schema.sql`
  - Contains tables for v2.0 features (email_logs, chat_sessions, chat_messages, dashboard_configs)

- **Migration Files**:
  - `/home/david/cursor_project/database/add_functional_name_to_products.sql`
  - `/home/david/cursor_project/apply_rls_fix.sql`
  - `/home/david/cursor_project/fix_galilu_trigger.sql`

### 3. Table Existence Status

**The table appears to exist but may have permission/access issues:**

1. **Evidence it exists:**
   - Schema definition found in `/home/david/cursor_project/Instruction_templates/reseller_instructions/Info_galilu.md`
   - Indexes are created for the table
   - RLS policies are applied
   - Trigger functions reference the table

2. **Current access limitations:**
   - Database service code contains workarounds for permission issues
   - Mock data is returned instead of real queries in `_query_sellout_entries`
   - Comments indicate "sellout_entries2 not accessible" scenarios

### 4. Query Examples Found

The following query patterns are used throughout the codebase:

**Chat Service Queries:**
```sql
SELECT SUM(sales_eur) as total_sales FROM sellout_entries2 LIMIT 1000;
SELECT DISTINCT functional_name FROM sellout_entries2 LIMIT 1000;
SELECT * FROM sellout_entries2 ORDER BY created_at DESC LIMIT 100;
```

**Report Service Queries:**
```sql
SELECT 
    se.product_ean,
    se.month,
    se.year,
    se.quantity,
    se.sales_lc,
    se.sales_eur,
    se.currency,
    se.reseller,
    se.functional_name,
    se.created_at,
    u.filename,
    u.uploaded_at
FROM sellout_entries2 se
JOIN uploads u ON se.upload_id = u.id
WHERE u.user_id = %s
ORDER BY se.created_at DESC
```

**Data Insertion:**
```sql
-- Insert operations handled through Supabase client
-- With batching (100 rows per batch)
-- Includes data validation and transformation
```

### 5. Data Pipeline Integration

The table is integrated into a comprehensive data pipeline:

1. **Upload Process**: Files are uploaded and processed through cleaning service
2. **Data Cleaning**: Vendor-specific rules applied via normalizers
3. **Data Storage**: Cleaned data inserted into `sellout_entries2`
4. **Data Access**: Used by chat service, report service, and dashboard integrations

### 6. Security & Access Control

- **RLS (Row Level Security)** enabled
- **User-based filtering** through `upload_id` relationship
- **Service role permissions** for background processing
- **Read-only access** for chat queries

### 7. Current Implementation Status

**Working Components:**
- Table schema is defined
- Data insertion pipeline exists
- Query examples are implemented
- Security policies are in place

**Potential Issues:**
- Permission errors during data insertion
- Mock data being returned instead of real queries
- Table accessibility concerns mentioned in debug code

## Recommendations

1. **Verify table existence** by running a simple SELECT query
2. **Check permissions** for the service account
3. **Test data insertion** with a small batch
4. **Replace mock data** with actual database queries once permissions are resolved
5. **Implement proper error handling** for database connectivity issues

## Next Steps

To implement proper SQL query execution instead of mock data:

1. Resolve any permission issues with the `sellout_entries2` table
2. Update the `_query_sellout_entries` method in `DatabaseService` to execute real queries
3. Test the chat service with actual data
4. Verify RLS policies are working correctly
5. Ensure all foreign key relationships are properly maintained