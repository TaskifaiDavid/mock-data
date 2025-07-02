-- Add functional_name column to products table for Liberty Item ID storage
ALTER TABLE public.products 
ADD COLUMN IF NOT EXISTS functional_name text;

-- Create index for better lookup performance
CREATE INDEX IF NOT EXISTS idx_products_functional_name ON public.products(functional_name);