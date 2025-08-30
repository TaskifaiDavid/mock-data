# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Data Cleaning Platform - Multi-Tenant Excel Processing System

## 🚀 Development Commands

### Frontend (React + Vite)
```bash
cd frontend
npm run dev      # Start frontend dev server on port 5173
npm run build    # Build for production
npm run preview  # Preview production build
```

### Backend (FastAPI + Python)
```bash
cd backend
source venv/bin/activate  # Activate virtual environment
python main.py           # Start backend server on port 8000
# or
./run.sh                # Run backend with venv activation
```

### Full Stack Development
- Frontend: http://localhost:5173 (proxies /api to backend)
- Backend API: http://localhost:8000/api
- API Docs: http://localhost:8000/docs

## 🎯 Available Subagents

Use these specialized agents by saying "Use the [agent-name] subagent for..."

### 🔵 feature-builder
**Use for:** Complete end-to-end feature development spanning database to UI
- Building new user authentication systems
- Creating full CRUD workflows with data visualization
- Implementing multi-step wizards or complex forms
- Developing file upload and processing features
- Adding notification systems with multiple channels

### 🟣 frontend-specialist  
**Use for:** React components, UI optimization, and user experience
- Creating responsive layouts and interactive components
- Implementing animations and micro-interactions
- Building data tables with sorting/filtering/pagination
- Optimizing component performance and state management
- Ensuring accessibility compliance (WCAG 2.2 AA)

### 🟢 backend-engineer
**Use for:** FastAPI development, APIs, and server-side logic
- Designing RESTful API endpoints
- Implementing authentication and authorization
- Building business logic and validation layers
- Integrating third-party services and webhooks
- Creating background task processing

### 🟠 database-architect
**Use for:** Database design, optimization, and query performance
- Designing schemas with proper client isolation
- Creating database migrations with rollback procedures
- Optimizing slow queries and indexing strategies
- Implementing Row-Level Security policies
- Planning data relationships and constraints

### 🟡 data-pipeline
**Use for:** Data processing, ETL, and file parsing
- Building vendor detection and file format recognition
- Creating data cleaning and transformation workflows
- Implementing Excel/CSV processing pipelines
- Handling data validation and quality assurance
- Building audit trails and reconciliation reports

### 🔴 security-audit
**Use for:** Security reviews and vulnerability assessment
- Conducting comprehensive security code reviews
- Verifying authentication and authorization implementations
- Checking for injection vulnerabilities and data exposure
- Validating client data isolation enforcement
- Ensuring compliance with security best practices

### 🩷 design-review
**Use for:** UI/UX quality assurance and visual validation
- Conducting systematic design reviews with screenshots
- Testing responsive behavior across all devices
- Validating accessibility compliance with keyboard navigation
- Checking visual hierarchy and interaction design
- Ensuring consistent design system usage

### 🔶 testing-specialist
**Use for:** Test automation and quality assurance
- Writing comprehensive test suites (unit/integration/E2E)
- Creating test data fixtures and factories
- Implementing CI/CD test integration
- Building performance and security test coverage
- Establishing code coverage and quality metrics

### 🔷 performance-optimizer
**Use for:** Speed optimization and scalability improvements
- Identifying and fixing performance bottlenecks
- Optimizing database queries and API response times
- Implementing caching strategies and code splitting
- Reducing bundle sizes and improving load times
- Planning for horizontal scaling and load balancing

### 🤎 debugger
**Use for:** Bug investigation and root cause analysis
- Systematically diagnosing complex issues
- Reproducing problems and tracing execution flow
- Conducting root cause analysis with prevention strategies
- Creating regression tests for bug fixes
- Implementing comprehensive error handling

### 🟣 ai-integration
**Use for:** AI features with LangChain and OpenAI
- Building conversational chat interfaces
- Implementing natural language data queries
- Creating context management and conversation history
- Integrating prompt engineering and response optimization
- Building AI-powered analytics and insights

### ⚫ docs-writer
**Use for:** Documentation creation and maintenance
- Writing comprehensive API documentation
- Creating user guides and technical specifications
- Documenting system architecture and data models
- Building deployment guides and troubleshooting docs
- Maintaining README files and code comments

## 🔄 Workflow Patterns

### Think → Plan → Build → Test → Review
1. **Think**: Use `think` / `think hard` / `think harder` / `ultrathink` for complex analysis
2. **Plan**: Have subagents create detailed implementation plans
3. **Build**: Use appropriate specialist subagents for implementation
4. **Test**: Employ testing-specialist for comprehensive coverage
5. **Review**: Use security-audit and design-review for quality assurance

### Multi-Agent Collaboration
- **Feature Development**: feature-builder → frontend-specialist + backend-engineer + database-architect
- **Quality Assurance**: testing-specialist → security-audit → design-review → performance-optimizer
- **Issue Resolution**: debugger → (appropriate specialist) → testing-specialist
- **Documentation**: Any specialist → docs-writer for comprehensive documentation

## 🛡️ Security Requirements

**CRITICAL: Every table MUST include client_id for data isolation**
- All database queries MUST filter by client_id
- All API endpoints MUST verify client access
- Never expose cross-client data
- Implement Row-Level Security policies

## 📐 Code Standards

### TypeScript/React
- Use ES modules (import/export), not CommonJS
- Destructure imports: `import { Component } from 'library'`
- Use functional components with hooks
- Implement proper error boundaries
- Follow WCAG 2.2 AA accessibility standards

### Python/FastAPI
- Use Pydantic for comprehensive data validation
- Implement async operations where beneficial
- Use dependency injection for testability
- Create custom exception classes with proper HTTP status codes
- Include comprehensive logging with security event tracking

### Database (PostgreSQL)
- Always include client_id in table schemas
- Use composite indexes for common query patterns
- Implement soft deletes with is_deleted flags
- Include created_at and updated_at timestamps
- Create proper foreign key relationships

## 🧪 Testing Strategy

- **Unit Tests**: 80%+ coverage, test business logic in isolation
- **Integration Tests**: API endpoints and service interactions
- **E2E Tests**: Critical user journeys and cross-browser compatibility
- **Security Tests**: Authentication, authorization, and data isolation
- **Performance Tests**: Load testing and bottleneck identification

## 📁 File Organization

```
/src
  /components     # Reusable React components
  /pages         # Route components
  /services      # API and business logic
  /types         # TypeScript type definitions
  /utils         # Helper functions
/tests
  /unit          # Component and function tests
  /integration   # API and service tests
  /e2e           # End-to-end test scenarios
/docs            # Project documentation
```

## 🚨 Important Notes

- **Multi-tenant Architecture**: Every data operation must respect client boundaries
- **Performance Targets**: Page load < 2.5s, API response < 200ms, DB queries < 100ms
- **Error Handling**: Never expose internal details to clients
- **Git Workflow**: Use descriptive commit messages, create PRs for all changes
- **Environment**: Use environment variables for all configuration

## 🎯 Agent Selection Guide

**For new features**: Start with feature-builder
**For UI work**: Use frontend-specialist 
**For API development**: Use backend-engineer
**For database changes**: Use database-architect
**For data processing**: Use data-pipeline
**For security concerns**: Use security-audit
**For visual validation**: Use design-review
**For testing**: Use testing-specialist
**For performance issues**: Use performance-optimizer
**For debugging**: Use debugger
**For AI features**: Use ai-integration
**For documentation**: Use docs-writer

Remember: You can use multiple subagents in sequence for complex tasks. Always start with exploration and planning before implementation.

## 🏗️ System Architecture

### Backend Structure (FastAPI)
```
backend/
├── main.py              # FastAPI app entry point with CORS and routing
├── app/
│   ├── api/            # API route handlers
│   │   ├── auth.py     # Authentication endpoints
│   │   ├── upload.py   # File upload processing
│   │   ├── chat.py     # AI chat functionality with LangChain
│   │   └── dashboard.py # Analytics and reporting
│   ├── models/         # Pydantic data models
│   ├── services/       # Business logic layer
│   │   ├── auth_service.py     # JWT auth and user management
│   │   ├── db_service.py       # Supabase database operations
│   │   ├── cleaning_service.py # Excel processing pipeline
│   │   └── file_service.py     # File handling utilities
│   ├── pipeline/       # Data processing pipeline
│   │   ├── detector.py      # Vendor format detection
│   │   ├── cleaners.py      # Data cleaning transformations
│   │   └── normalizers.py   # Data normalization
│   └── utils/
│       ├── config.py   # Settings management with Pydantic
│       └── exceptions.py # Custom exception classes
└── requirements.txt    # Python dependencies
```

### Frontend Structure (React + Vite)
```
frontend/src/
├── App.jsx             # Main app with auth routing
├── components/
│   ├── Upload.jsx      # File upload with progress tracking
│   ├── ChatSection.jsx # AI chat interface
│   ├── DataVisualization.jsx # Charts with Chart.js
│   └── AnalyticsDashboard.jsx # Analytics dashboard
├── pages/
│   ├── Login.jsx       # Authentication page
│   └── Dashboard.jsx   # Main dashboard with sidebar navigation
├── services/
│   ├── api.js         # API client functions
│   └── supabase.js    # Supabase client configuration
└── styles/
    └── index.css      # Global styles with responsive design
```

### Database Schema (PostgreSQL/Supabase)
- **users**: User accounts linked to Supabase auth
- **uploads**: File upload metadata with processing status
- **products**: Product catalog with EAN codes
- **sellout_entries2**: Normalized sales data from processed files

## 🔧 Key Technologies

### Backend Stack
- **FastAPI**: High-performance Python web framework
- **Supabase**: PostgreSQL database with Row-Level Security
- **LangChain + OpenAI**: AI chat functionality for data queries
- **Pandas + OpenPyXL**: Excel file processing
- **JWT**: Token-based authentication
- **Celery**: Background task processing (configured)

### Frontend Stack
- **React 18**: UI framework with hooks
- **Vite**: Build tool and dev server
- **Chart.js**: Data visualization
- **KaTeX**: Math rendering support
- **Supabase JS**: Real-time database client

## 🛡️ Security & Multi-Tenancy

**CRITICAL**: This is a multi-tenant system where data isolation is paramount:
- Every database table includes `user_id` for tenant isolation
- All API endpoints must verify user ownership via JWT tokens
- Row-Level Security (RLS) policies enforce data boundaries
- Never expose cross-user data in queries or responses

## 🔄 Data Processing Pipeline

1. **Upload**: User uploads Excel file via drag-and-drop interface
2. **Detection**: System identifies vendor format and data structure
3. **Cleaning**: Applied transformations based on vendor type
4. **Normalization**: Data converted to standard schema
5. **Storage**: Processed data saved with audit trail
6. **Analytics**: Real-time charts and AI-powered queries available

## 🧪 Environment Setup

### Required Environment Variables (.env)
```bash
# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key

# Database for LangChain (required)
DATABASE_URL=postgresql://user:pass@host:port/database

# JWT Authentication
JWT_SECRET_KEY=your_secret_key

# OpenAI (for chat functionality)
OPENAI_API_KEY=your_openai_key

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_USERNAME=your_email
SMTP_PASSWORD=your_app_password
```

## 🚨 Critical Notes

- **Client Isolation**: Every database operation must filter by authenticated user
- **File Processing**: Supports .xlsx files up to 10MB by default
- **Error Handling**: Custom exceptions with proper HTTP status codes
- **Logging**: Comprehensive logging for security events and data processing
- **CORS**: Configured for multiple localhost ports (5173-5176)

## 🎯 Common Development Tasks

### Adding New API Endpoints
1. Create route in appropriate `app/api/` file
2. Add business logic in `app/services/`
3. Update Pydantic models if needed
4. Ensure proper authentication and user filtering

### Adding New Data Processing Rules
1. Update detection logic in `app/pipeline/detector.py`
2. Add cleaning rules in `app/pipeline/cleaners.py`
3. Update normalization in `app/pipeline/normalizers.py`
4. Test with sample Excel files

### Frontend Component Development  
1. Create component in `src/components/`
2. Import required services from `src/services/`
3. Use consistent styling patterns from `src/styles/`
4. Ensure responsive design and accessibility