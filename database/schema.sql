-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS public.users (
  id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email text UNIQUE NOT NULL,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Products table (if it doesn't exist)
CREATE TABLE IF NOT EXISTS public.products (
  ean text PRIMARY KEY,
  name text,
  brand text DEFAULT 'BIBBI',
  created_at timestamptz DEFAULT now()
);

-- Raw upload metadata
CREATE TABLE IF NOT EXISTS public.uploads (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id uuid REFERENCES public.users(id) ON DELETE CASCADE,
  filename text NOT NULL,
  file_size bigint,
  uploaded_at timestamptz DEFAULT now(),
  status text CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
  error_message text,
  rows_processed integer,
  rows_cleaned integer,
  processing_time_ms integer
);

-- Existing sellout_entries2 table (reference - should already exist)
-- CREATE TABLE IF NOT EXISTS public.sellout_entries2 (
--   id uuid NOT NULL DEFAULT gen_random_uuid(),
--   product_ean text NULL,
--   month integer NULL,
--   year integer NULL,
--   quantity integer NULL,
--   sales_lc text NULL,
--   sales_eur numeric NULL,
--   currency text NULL,
--   created_at timestamp without time zone NULL DEFAULT now(),
--   reseller text NULL,
--   functional_name text NULL,
--   CONSTRAINT sellout_entries2_pkey PRIMARY KEY (id),
--   CONSTRAINT sellout_entries2_product_ean_fkey FOREIGN KEY (product_ean) REFERENCES products (ean),
--   CONSTRAINT sellout_entries_month_check CHECK (((month >= 1) AND (month <= 12))),
--   CONSTRAINT sellout_entries_year_check CHECK ((year >= 2000))
-- );

-- Transformation logs
CREATE TABLE IF NOT EXISTS public.transform_logs (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  upload_id uuid REFERENCES public.uploads(id) ON DELETE CASCADE,
  row_index integer,
  column_name text,
  original_value text,
  cleaned_value text,
  transformation_type text,
  logged_at timestamptz DEFAULT now()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_uploads_user_id ON public.uploads(user_id);
CREATE INDEX IF NOT EXISTS idx_uploads_status ON public.uploads(status);
CREATE INDEX IF NOT EXISTS idx_sellout_entries2_upload_id ON public.sellout_entries2(upload_id) WHERE upload_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_sellout_entries2_product_ean ON public.sellout_entries2(product_ean);
CREATE INDEX IF NOT EXISTS idx_sellout_entries2_reseller ON public.sellout_entries2(reseller);
CREATE INDEX IF NOT EXISTS idx_transform_logs_upload_id ON public.transform_logs(upload_id);

-- Add upload_id column to sellout_entries2 if it doesn't exist
ALTER TABLE public.sellout_entries2 
ADD COLUMN IF NOT EXISTS upload_id uuid REFERENCES public.uploads(id) ON DELETE SET NULL;

-- RLS (Row Level Security) policies
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.uploads ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sellout_entries2 ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.transform_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.products ENABLE ROW LEVEL SECURITY;

-- Users can only see their own data
CREATE POLICY "Users can view own profile" ON public.users
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Service role can create users" ON public.users
  FOR INSERT WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "Users can view own uploads" ON public.uploads
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own uploads" ON public.uploads
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Service role can manage uploads (for background processing)
CREATE POLICY "Service role can manage uploads" ON public.uploads
  FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Users can view own sellout entries" ON public.sellout_entries2
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM public.uploads
      WHERE uploads.id = sellout_entries2.upload_id
      AND uploads.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can insert own sellout entries" ON public.sellout_entries2
  FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.uploads
      WHERE uploads.id = sellout_entries2.upload_id
      AND uploads.user_id = auth.uid()
    )
  );

-- Service role can insert sellout entries (for background processing)
CREATE POLICY "Service role can insert sellout entries" ON public.sellout_entries2
  FOR INSERT WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "Users can view own transform logs" ON public.transform_logs
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM public.uploads
      WHERE uploads.id = transform_logs.upload_id
      AND uploads.user_id = auth.uid()
    )
  );

-- Service role can manage transform logs (for background processing)
CREATE POLICY "Service role can manage transform logs" ON public.transform_logs
  FOR ALL USING (auth.role() = 'service_role');

-- Everyone can view products (read-only)
CREATE POLICY "Anyone can view products" ON public.products
  FOR SELECT USING (true);

-- Service role can manage products
CREATE POLICY "Service role can manage products" ON public.products
  FOR ALL USING (auth.role() = 'service_role');