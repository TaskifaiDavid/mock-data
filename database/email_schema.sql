-- Email logs table for tracking email activities
CREATE TABLE IF NOT EXISTS public.email_logs (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id uuid REFERENCES public.users(id) ON DELETE CASCADE,
  recipient_email text NOT NULL,
  email_type text NOT NULL CHECK (email_type IN ('report', 'notification', 'auto_response')),
  status text NOT NULL CHECK (status IN ('sent', 'failed', 'pending')),
  sent_at timestamptz DEFAULT now(),
  metadata jsonb,
  error_message text,
  created_at timestamptz DEFAULT now()
);

-- Chat sessions table for AI chat feature
CREATE TABLE IF NOT EXISTS public.chat_sessions (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id uuid REFERENCES public.users(id) ON DELETE CASCADE,
  session_name text,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Chat messages table for storing conversation history
CREATE TABLE IF NOT EXISTS public.chat_messages (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  session_id uuid REFERENCES public.chat_sessions(id) ON DELETE CASCADE,
  user_id uuid REFERENCES public.users(id) ON DELETE CASCADE,
  message_type text NOT NULL CHECK (message_type IN ('user', 'assistant', 'system')),
  content text NOT NULL,
  sql_query text,
  query_result jsonb,
  created_at timestamptz DEFAULT now()
);

-- Dashboard configurations table
CREATE TABLE IF NOT EXISTS public.dashboard_configs (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id uuid REFERENCES public.users(id) ON DELETE CASCADE,
  dashboard_name text NOT NULL,
  dashboard_type text NOT NULL CHECK (dashboard_type IN ('tableau', 'powerbi', 'grafana', 'looker', 'metabase', 'custom')),
  dashboard_url text NOT NULL,
  authentication_method text CHECK (authentication_method IN ('token', 'sso', 'basic', 'none')),
  authentication_config jsonb,
  permissions jsonb,
  is_active boolean DEFAULT true,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_email_logs_user_id ON public.email_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_email_logs_sent_at ON public.email_logs(sent_at);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON public.chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON public.chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_user_id ON public.chat_messages(user_id);
CREATE INDEX IF NOT EXISTS idx_dashboard_configs_user_id ON public.dashboard_configs(user_id);

-- RLS policies for email logs
ALTER TABLE public.email_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own email logs" ON public.email_logs
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own email logs" ON public.email_logs
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Service role can manage email logs" ON public.email_logs
  FOR ALL USING (auth.role() = 'service_role');

-- RLS policies for chat sessions
ALTER TABLE public.chat_sessions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own chat sessions" ON public.chat_sessions
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own chat sessions" ON public.chat_sessions
  FOR ALL USING (auth.uid() = user_id);

-- RLS policies for chat messages
ALTER TABLE public.chat_messages ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own chat messages" ON public.chat_messages
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own chat messages" ON public.chat_messages
  FOR ALL USING (auth.uid() = user_id);

-- RLS policies for dashboard configs
ALTER TABLE public.dashboard_configs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own dashboard configs" ON public.dashboard_configs
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own dashboard configs" ON public.dashboard_configs
  FOR ALL USING (auth.uid() = user_id);