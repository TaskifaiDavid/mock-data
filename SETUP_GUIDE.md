# Bibbi Cleaner v2.0 Setup Guide

## ✅ Complete Setup Instructions

### Step 1: Database Schema Setup

1. **Go to your Supabase Dashboard**: https://supabase.com/dashboard
2. **Open SQL Editor** (left sidebar)
3. **Run the v2.0 schema** by copying and pasting this SQL:

```sql
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
```

### Step 2: Get Required API Keys

#### 🔑 OpenAI API Key (Required for AI Chat)
1. Go to: https://platform.openai.com/api-keys
2. Sign in to your OpenAI account
3. Click "Create new secret key"
4. Name it "Bibbi Cleaner" and copy the key
5. **Important**: You need to add payment method to OpenAI account for API access

#### 📧 Email Configuration (Required for Email Reports)

**Option A: Gmail (Recommended)**
1. Enable 2-Factor Authentication on your Gmail account
2. Go to: Google Account Settings > Security > App passwords
3. Generate an app password for "Mail"
4. Use this app password (not your regular Gmail password)

**Option B: Other SMTP Provider**
- Use your email provider's SMTP settings
- Common providers: SendGrid, Mailgun, Outlook, etc.

### Step 3: Update Environment Variables

Edit `/backend/.env` file and replace these values:

```bash
# Email Configuration - REPLACE WITH YOUR VALUES
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password_here  # Use Gmail app password, not regular password
SMTP_FROM_EMAIL=your_email@gmail.com

# OpenAI Configuration - REPLACE WITH YOUR VALUES
OPENAI_API_KEY=your_openai_api_key_here
```

### Step 4: Install Dependencies

```bash
# Backend dependencies
cd backend
pip install -r requirements.txt

# Frontend dependencies  
cd ../frontend
npm install
```

### Step 5: Start the Application

```bash
# Terminal 1 - Backend
cd backend
uvicorn main:app --reload

# Terminal 2 - Frontend (new terminal)
cd frontend
npm run dev
```

### Step 6: Test Features

1. **Upload Data**: Test the existing file upload functionality
2. **Email Reports**: Go to "Email Reports" tab and try generating a report
3. **AI Chat**: Go to "AI Chat" tab and ask: "Show me total sales"
4. **Analytics**: Go to "Analytics" tab and try adding a dashboard

## 🔧 Troubleshooting

### Email Issues
- **"Authentication failed"**: Make sure you're using Gmail app password, not regular password
- **"SMTP connection failed"**: Check firewall/antivirus blocking port 587

### AI Chat Issues
- **"OpenAI API error"**: Check your API key and account has payment method
- **"No results"**: Make sure you have uploaded some data first

### General Issues
- **"Database connection failed"**: Check your Supabase credentials in .env
- **"Table doesn't exist"**: Make sure you ran the SQL schema in Step 1

## 📝 Environment Variables Reference

```bash
# Required for basic functionality
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_service_key
JWT_SECRET_KEY=your_jwt_secret

# Required for v2.0 features
SMTP_USERNAME=your_email@gmail.com        # Your email address
SMTP_PASSWORD=your_app_password           # Gmail app password
SMTP_FROM_EMAIL=your_email@gmail.com      # Same as username
OPENAI_API_KEY=sk-your_openai_key         # From OpenAI platform

# Optional customization
SMTP_HOST=smtp.gmail.com                  # Default: Gmail
SMTP_PORT=587                            # Default: Gmail port
OPENAI_MODEL=gpt-4                       # Default: GPT-4
```

## 🎯 What Each Feature Does

### 📊 Email Reports
- Generate PDF/CSV/Excel reports of cleaned data
- Send reports automatically to `report@bibbi-parfum.com`
- Track email delivery status and history

### 🤖 AI Chat
- Ask questions about your data in natural language
- Automatically generates SQL queries
- Shows results in tables with export options

### 📈 Analytics Dashboards
- Embed external dashboards (Tableau, PowerBI, etc.)
- Configure multiple dashboards with authentication
- View all dashboards within the application

## ✅ Success Indicators

When everything is working:
- ✅ Backend starts without errors on http://localhost:8000
- ✅ Frontend starts without errors on http://localhost:5173
- ✅ You can log in and upload Excel files
- ✅ Email Reports tab loads without errors
- ✅ AI Chat tab loads and shows welcome message
- ✅ Analytics tab loads dashboard configuration form

**Need help?** Check the console logs in your browser for any error messages.