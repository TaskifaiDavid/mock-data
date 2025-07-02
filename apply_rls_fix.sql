-- Fix RLS policies to allow service role to manage data for background processing

-- Service role can manage uploads (for background processing)
CREATE POLICY IF NOT EXISTS "Service role can manage uploads" ON public.uploads
  FOR ALL USING (auth.role() = 'service_role');

-- Service role can insert sellout entries (for background processing)
CREATE POLICY IF NOT EXISTS "Service role can insert sellout entries" ON public.sellout_entries2
  FOR INSERT WITH CHECK (auth.role() = 'service_role');

-- Service role can manage transform logs (for background processing)
CREATE POLICY IF NOT EXISTS "Service role can manage transform logs" ON public.transform_logs
  FOR ALL USING (auth.role() = 'service_role');