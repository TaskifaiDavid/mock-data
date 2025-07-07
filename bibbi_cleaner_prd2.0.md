# Product Requirements Document: Bibbi Cleaner Enhancements

## Project Overview
**Product:** Bibbi Cleaner  
**Version:** 2.0  
**Date:** July 2025  
**Author:** Product Team  

## Executive Summary
This PRD outlines three major enhancements to the Bibbi Cleaner application:
1. Automated email reporting system with attachment support
2. AI-powered database chat interface using OpenAI GPT-4
3. External dashboard integration for analytics

## 1. Email Reporting System

### 1.1 Feature Overview
Implement an HTTP-based email system that sends cleaning reports with attachments to `report@bibbi-parfum.com` and receives automated email responses.

### 1.2 User Stories
- **As a data manager**, I want to automatically send cleaning reports via email so that stakeholders receive timely updates
- **As a recipient**, I want to receive confirmation emails with cleaning statistics so I can track progress
- **As an admin**, I want to view email send/receive logs so I can troubleshoot issues

### 1.3 Technical Requirements

#### Backend Requirements
```
- HTTP endpoint: POST /api/reports/email
- Email service integration (recommend: SendGrid, AWS SES, or Nodemailer)
- File attachment handling (PDF, CSV, Excel formats)
- Email template system for automated responses
- Queue system for email processing (recommend: Bull/Redis or AWS SQS)
- Email delivery status tracking
- Rate limiting and retry logic
```

#### API Specification
```javascript
POST /api/reports/email
{
  "reportType": "cleaning_summary",
  "recipientEmail": "report@bibbi-parfum.com",
  "attachments": [
    {
      "filename": "cleaning_report_2025_07.pdf",
      "data": "base64_encoded_data",
      "contentType": "application/pdf"
    }
  ],
  "metadata": {
    "cleanedRows": 24,
    "totalValue": 1250.50,
    "currency": "EUR"
  }
}
```

#### Response Format
```javascript
{
  "success": true,
  "messageId": "email_123456",
  "status": "sent",
  "timestamp": "2025-07-07T10:30:00Z",
  "autoResponse": "success, 24 rows cleaned to the value of 1250.50 euro."
}
```

### 1.4 Implementation Dependencies
- Email service provider setup
- Email templates creation
- File storage for attachments (temporary)
- Background job processing system

## 2. AI-Powered Database Chat Interface

### 2.1 Feature Overview
Connect the `sellout_entries2` database with an interactive chat interface powered by OpenAI GPT-4 for natural language database queries.

### 2.2 User Stories
- **As a business analyst**, I want to query the database using natural language so I can get insights without writing SQL
- **As a non-technical user**, I want to ask questions about sales data so I can make informed decisions
- **As a data scientist**, I want to explore data patterns through conversational interface so I can identify trends quickly

### 2.3 Technical Requirements

#### Core Components
```
- OpenAI GPT-4 API integration
- SQL query generation from natural language
- Database schema analysis and context
- Query result formatting and visualization
- Chat history and session management
- Security and access control
```

#### Database Integration
```sql
-- Required database introspection
SELECT 
  table_name,
  column_name,
  data_type,
  is_nullable
FROM information_schema.columns 
WHERE table_name = 'sellout_entries2';
```

#### API Endpoints
```javascript
POST /api/chat/query
{
  "message": "Show me total sales for last month",
  "sessionId": "chat_session_123",
  "userId": "user_456"
}

GET /api/chat/history/:sessionId
POST /api/chat/clear/:sessionId
```

#### Security Considerations
```
- SQL injection prevention
- Query whitelist/blacklist
- Read-only database access
- User permission validation
- Rate limiting per user
- Audit logging
```

### 2.4 Implementation Architecture
```
Frontend Chat UI → API Gateway → Chat Service → OpenAI API
                                     ↓
                              Query Generator → Database (Read-Only)
                                     ↓
                              Result Formatter → Response
```

### 2.5 OpenAI Configuration
```javascript
{
  "model": "gpt-4",
  "temperature": 0.1,
  "max_tokens": 1000,
  "system_prompt": "You are a SQL expert. Convert natural language to SQL queries for the sellout_entries2 database. Schema: [database_schema]"
}
```

## 3. External Dashboard Integration

### 3.1 Feature Overview
Add embedded dashboard capability under the analytics tab to integrate external business intelligence tools.

### 3.2 User Stories
- **As a business manager**, I want to view external dashboards within the app so I can have a unified interface
- **As an analyst**, I want to embed Tableau/PowerBI/Grafana dashboards so I can share insights with the team
- **As an admin**, I want to configure dashboard sources so I can control what data is displayed

### 3.3 Technical Requirements

#### Frontend Components
```jsx
// React component example
<DashboardEmbed 
  source="tableau"
  dashboardId="dashboard_123"
  width="100%"
  height="600px"
  authentication="sso"
/>
```

#### Supported Platforms
```
- Tableau Server/Online
- Microsoft Power BI
- Grafana
- Looker
- Custom iframe solutions
- Metabase
```

#### Configuration Schema
```javascript
{
  "dashboards": [
    {
      "id": "sales_dashboard",
      "name": "Sales Analytics",
      "type": "tableau",
      "url": "https://tableau.company.com/embed/dashboard",
      "authentication": {
        "method": "token",
        "credentials": "encrypted_token"
      },
      "permissions": ["sales_team", "managers"]
    }
  ]
}
```

### 3.4 Implementation Considerations
```
- Responsive iframe handling
- Cross-origin security (CORS)
- Authentication token management
- Dashboard loading states
- Error handling for external services
- Caching strategies
```

## Implementation Timeline

### Phase 1: Email System (2-3 weeks)
- Week 1: Email service setup and basic sending
- Week 2: Attachment handling and templates
- Week 3: Response parsing and error handling

### Phase 2: AI Chat Interface (3-4 weeks)
- Week 1: OpenAI integration and basic queries
- Week 2: Database schema analysis and SQL generation
- Week 3: Frontend chat interface
- Week 4: Security and optimization

### Phase 3: Dashboard Integration (1-2 weeks)
- Week 1: Iframe embedding and authentication
- Week 2: Configuration management and testing

## Technical Stack Recommendations

### Backend (assuming Node.js/Express)
```javascript
// Dependencies
{
  "openai": "^4.0.0",
  "nodemailer": "^6.9.0",
  "bull": "^4.10.0",
  "redis": "^4.6.0",
  "multer": "^1.4.5",
  "helmet": "^7.0.0",
  "express-rate-limit": "^6.7.0"
}
```

### Frontend (assuming React)
```javascript
// Dependencies
{
  "react-chat-widget": "^3.1.0",
  "react-markdown": "^8.0.0",
  "recharts": "^2.6.0",
  "axios": "^1.4.0"
}
```

### Environment Variables
```bash
OPENAI_API_KEY=sk-xxx
EMAIL_SERVICE_API_KEY=xxx
DATABASE_URL=xxx
REDIS_URL=xxx
CORS_ORIGIN=https://yourapp.com
```

## Security Requirements

### Data Protection
- Encrypt OpenAI API keys
- Sanitize all database queries
- Implement user authentication for chat
- Log all database access attempts
- Secure email attachment handling

### Access Control
- Role-based permissions for features
- Rate limiting on API endpoints
- Audit trail for all actions
- Secure token management for external dashboards

## Success Metrics

### Email System
- Email delivery rate > 99%
- Response processing time < 30 seconds
- Zero failed attachment deliveries

### AI Chat
- Query response time < 5 seconds
- Query accuracy rate > 95%
- User adoption > 70% within 30 days

### Dashboard Integration
- Dashboard load time < 3 seconds
- Zero authentication failures
- 100% uptime for embedded dashboards

## Risk Assessment

### High Risk
- OpenAI API rate limits and costs
- Database security vulnerabilities
- External dashboard service reliability

### Medium Risk
- Email service deliverability issues
- Cross-origin security challenges
- Performance impact on database

### Mitigation Strategies
- Implement comprehensive monitoring
- Set up fallback systems
- Regular security audits
- Performance optimization testing

## Acceptance Criteria

### Email System
- ✅ Send emails with attachments to specified recipients
- ✅ Receive and parse automated email responses
- ✅ Display success/failure status with detailed messages
- ✅ Handle multiple attachment formats (PDF, CSV, Excel)

### AI Chat
- ✅ Process natural language queries about sellout_entries2
- ✅ Generate accurate SQL from user questions
- ✅ Display results in user-friendly format
- ✅ Maintain conversation context and history

### Dashboard Integration
- ✅ Embed external dashboards in analytics tab
- ✅ Support multiple dashboard providers
- ✅ Secure authentication handling
- ✅ Responsive design across devices