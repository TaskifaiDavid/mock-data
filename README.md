# Bibbi Cleaner v2.0

A comprehensive data cleaning and analytics platform for Bibbi Parfum sales data management.

## Features

### Core Data Pipeline
- Secure user authentication via Supabase
- Excel file upload (.xlsx up to 10MB)
- Intelligent data cleaning pipeline with vendor-specific rules
- Automatic schema detection and normalization
- Data persistence in Supabase
- Processing status tracking and error reporting

### Email Reporting System (v2.0)
- Automated email reports with PDF/CSV/Excel attachments
- Email delivery tracking and status monitoring
- Customizable report generation with metadata
- Email logs and history viewer
- Integration with external email services (SMTP/SendGrid)

### AI-Powered Database Chat (v2.0)
- Natural language SQL query generation using OpenAI GPT-4
- Interactive chat interface for data exploration
- Secure read-only database access with user isolation
- Query history and session management
- Real-time data visualization and insights

### External Dashboard Integration (v2.0)
- Iframe embedding for external analytics platforms
- Support for Tableau, Power BI, Grafana, Looker, and Metabase
- Dashboard configuration management
- Authentication handling for external services
- Responsive dashboard viewing with error handling

## Project Structure

```
.
├── backend/          # Python FastAPI backend
├── frontend/         # React frontend with Vite
├── database/         # Database schemas and migrations
├── PRD.md           # Product Requirements Document
└── README.md        # This file
```

## Setup

1. **Clone and install dependencies:**
   ```bash
   # Backend
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt

   # Frontend
   cd ../frontend
   npm install
   ```

2. **Configure environment:**
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env with your configuration:
   # - Supabase credentials
   # - Email service settings (SMTP/SendGrid)
   # - OpenAI API key for chat functionality
   # - Redis URL for background processing
   ```

3. **Setup Database:**
   - Create a new Supabase project
   - Run the base schema: `database/schema.sql`
   - Run the v2.0 extensions: `database/email_schema.sql`
   - Copy project URL and keys to `.env`

4. **Run the application:**
   ```bash
   # Terminal 1 - Backend
   cd backend
   uvicorn main:app --reload

   # Terminal 2 - Frontend
   cd frontend
   npm run dev
   ```

## Supported Excel Formats

The pipeline handles vendor-specific formats:
- Galilu
- Boxnox
- Skins SA
- CDLC
- Continuity
- Ukraine TDSheet

See PRD.md for detailed field mappings and cleaning rules.

## New Features (v2.0)

### Using the Email Reporting System
1. Navigate to the "Email Reports" tab
2. Configure report format (PDF/CSV/Excel)
3. Set recipient email address
4. Generate reports manually or enable auto-send
5. View email delivery logs and status

### Using the AI Chat Interface
1. Go to the "AI Chat" tab
2. Ask questions in natural language about your data:
   - "Show me total sales for last month"
   - "Which reseller has the highest sales?"
   - "What are my top selling products?"
3. View generated SQL queries (optional)
4. Export query results

### Setting Up External Dashboards
1. Navigate to the "Analytics" tab
2. Click "Add Dashboard"
3. Configure dashboard settings:
   - Dashboard name and type
   - URL for embedding
   - Authentication method
4. View embedded dashboards within the application

## API Endpoints (v2.0)

### Email & Reporting
- `POST /api/reports/email` - Send email with attachments
- `POST /api/reports/generate` - Generate reports
- `GET /api/email/logs` - Get email delivery logs

### AI Chat
- `POST /api/chat/query` - Send natural language query
- `GET /api/chat/history/{session_id}` - Get chat history
- `POST /api/chat/clear/{session_id}` - Clear chat session

### Dashboard Management
- `GET /api/dashboards/configs` - Get dashboard configurations
- `POST /api/dashboards/configs` - Create dashboard config
- `PUT /api/dashboards/configs/{id}` - Update dashboard config
- `DELETE /api/dashboards/configs/{id}` - Delete dashboard config

## Environment Variables

Key environment variables for v2.0 features:

```bash
# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM_EMAIL=your_email@gmail.com

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.1

# Redis (for future queue implementation)
REDIS_URL=redis://localhost:6379
```

## Security Features

- Row Level Security (RLS) policies for multi-tenant data isolation
- Read-only database access for AI chat queries
- SQL injection prevention and query validation
- Secure email attachment handling
- Authentication token management for external dashboards