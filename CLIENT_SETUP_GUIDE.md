# TaskifAI Data Processing Platform - Client Setup Guide

## System Overview

TaskifAI is an AI-powered platform that automates reseller data management for consumer brands. The system transforms messy Excel spreadsheets into clean, actionable insights through automatic data processing, real-time dashboards, and AI-powered analytics.

### Core Components
- **Backend**: FastAPI-based Python API with data processing pipeline
- **Frontend**: React-based dashboard with data visualization
- **Database**: Supabase (PostgreSQL) with row-level security
- **AI**: OpenAI GPT-4 integration for natural language queries
- **Processing**: Automated Excel file cleaning and normalization

## Prerequisites

### Required Software
- **Python 3.12+** (for backend)
- **Node.js 18+** (for frontend)
- **Git** (for version control)

### Required Services
- **Supabase Account** (database hosting)
- **OpenAI API Key** (AI functionality)
- **Redis** (optional, for background tasks)

## Initial Setup Process

### 1. Environment Setup

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Frontend Setup
```bash
cd frontend
npm install
```

### 2. Database Configuration

#### Create Supabase Project
1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Create a new project
3. Copy your project URL and keys
4. Run the database schema:
   ```sql
   -- Execute the contents of database/schema.sql in your Supabase SQL editor
   ```

### 3. Environment Configuration

#### Backend Environment
1. Copy `backend/.env.dev.template` to `backend/.env.dev`
2. Fill in your configuration:

```env
# Supabase Configuration
SUPABASE_URL=https://YOUR_PROJECT_ID.supabase.co
SUPABASE_ANON_KEY=YOUR_ANON_KEY
SUPABASE_SERVICE_KEY=YOUR_SERVICE_KEY

# Database Connection
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.YOUR_PROJECT_ID.supabase.co:5432/postgres

# JWT Security
JWT_SECRET_KEY=YOUR_GENERATED_SECRET_KEY

# OpenAI Integration
OPENAI_API_KEY=sk-your-openai-key-here
OPENAI_MODEL=gpt-4o

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=development
```

#### Frontend Environment
Create `frontend/.env`:
```env
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=https://YOUR_PROJECT_ID.supabase.co
VITE_SUPABASE_ANON_KEY=YOUR_ANON_KEY
```

### 4. Running the System

#### Start Backend
```bash
cd backend
source venv/bin/activate
python main.py
# Or use: ./run.sh
```

#### Start Frontend
```bash
cd frontend
npm run dev
```

## System Architecture

### Data Processing Pipeline
1. **Upload**: Excel files uploaded through web interface
2. **Detection**: AI determines vendor/reseller type from filename/content
3. **Cleaning**: Vendor-specific data normalization and cleaning
4. **Storage**: Processed data stored in PostgreSQL with audit trails
5. **Analytics**: Real-time dashboards and AI-powered queries

### Supported Vendor Formats
The system currently supports:
- **TaskifAI**: Demo report formats with EAN codes and sales data
- **Galilu**: Specific column mappings and data structures
- **Generic**: Fallback processing for unknown formats

### Security Features
- **Row-Level Security**: Users only see their own data
- **JWT Authentication**: Secure API access
- **SQL Injection Protection**: Parameterized queries and validation
- **CORS Configuration**: Restricted to allowed origins

## Key Features for Clients

### 1. File Upload & Processing
- Drag-and-drop Excel file upload
- Automatic vendor detection
- Real-time processing status
- Error handling and retry mechanisms

### 2. Data Visualization
- Interactive charts and graphs
- Sales performance analytics
- Product performance tracking
- Monthly/yearly comparisons

### 3. AI-Powered Chat
- Natural language queries about data
- Automatic SQL generation
- Intelligent data insights
- Export capabilities

### 4. Email Reporting
- Automated report generation
- Scheduled email delivery
- Custom report formats (PDF/Excel)

## Verification & Testing

### 1. System Health Check
```bash
# Check backend health
curl http://localhost:8000/health

# Expected response: {"status": "healthy"}
```

### 2. Authentication Test
1. Access frontend at `http://localhost:5173`
2. Register a new account
3. Upload a sample Excel file
4. Verify data appears in dashboard

### 3. Sample Data
Use the provided sample files:
- `Demo_ReportPeriod02-2025.xlsx` (TaskifAI format)
- `mock_data_100_rows.xlsx` (Generic format)

### 4. Feature Testing Checklist
- [ ] User registration/login
- [ ] File upload functionality
- [ ] Data processing completion
- [ ] Dashboard visualization
- [ ] AI chat queries
- [ ] Email report generation

## Configuration Customization

### Adding New Vendor Formats
1. Create detection rules in `demo_instructions.md`
2. Add cleaning logic in `backend/app/pipeline/cleaners.py`
3. Configure column mappings in data extraction rules
4. Test with sample files

### Customizing UI
- Modify React components in `frontend/src/components/`
- Update styling in `frontend/src/styles/index.css`
- Configure charts in `DataVisualization.jsx`

### Database Customization
- Add new tables/columns in `database/schema.sql`
- Update API models in `backend/app/models/`
- Modify security policies as needed

## Troubleshooting

### Common Issues

#### Backend Won't Start
- Check environment variables are set correctly
- Verify database connection with `python debug_env.py`
- Ensure Python virtual environment is activated

#### Frontend Build Errors
- Clear node_modules: `rm -rf node_modules && npm install`
- Check Node.js version compatibility
- Verify environment variables

#### Database Connection Issues
- Test Supabase connection from SQL editor
- Check firewall/network restrictions
- Verify DATABASE_URL format

#### File Processing Errors
- Check file format (must be .xlsx)
- Verify vendor detection patterns
- Review processing logs in database

### Support Resources
- **Logs**: Check `backend/backend.log` for detailed error messages
- **Database**: Query `processing_logs` table for upload issues
- **Debug**: Use `test_*.py` scripts for component testing

## Production Deployment

### Environment Differences
- Use production Supabase project
- Generate new JWT secrets
- Configure production CORS origins
- Set up monitoring and logging

### Security Considerations
- Rotate API keys regularly
- Use HTTPS in production
- Configure proper CORS settings
- Enable database backups

### Performance Optimization
- Configure Redis for caching
- Optimize database queries
- Set up CDN for frontend assets
- Monitor resource usage

## Success Criteria

Your TaskifAI setup is successful when:

1. ✅ Both backend and frontend start without errors
2. ✅ User can register and authenticate
3. ✅ Excel files upload and process correctly
4. ✅ Data appears in dashboard visualizations
5. ✅ AI chat responds to data queries
6. ✅ Email reports can be generated and sent
7. ✅ All data is properly secured per user

## Next Steps

After successful setup:
1. Import your actual reseller data files
2. Configure vendor-specific detection rules
3. Customize dashboard layouts
4. Set up automated reporting schedules
5. Train team on system usage

---

*For technical support or questions, refer to the development team or check the project's issue tracker.*