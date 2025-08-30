# Client Requirements Template

**Instructions**: Please fill out this template completely to help us build your secure data processing platform. All information will be used to create a client-specific deployment with complete data isolation.

---

## Client Information

### Basic Details
- **Client Name**: `[Your Organization Name]`
- **Project Name**: `[Internal Project Name]`
- **Primary Contact**: `[Name, Email, Phone]`
- **Technical Contact**: `[Name, Email, Phone]`
- **Deployment Target Date**: `[YYYY-MM-DD]`
- **Budget Range**: `[Optional: $X - $Y]`

### Business Context
**What is your primary business?**
`[e.g., Consumer goods manufacturer, Retail brand, Distributor, etc.]`

**What problem are you trying to solve?**
`[Describe current pain points with data management]`

**How do you currently handle this data?**
`[Manual Excel processing, other tools, etc.]`

---

## Data Requirements

### Data Sources
**What types of files will you be uploading?**
- [ ] Excel files (.xlsx)
- [ ] CSV files
- [ ] Other: `[Specify formats]`

**Where does your data come from?**
- [ ] Resellers/Partners
- [ ] Internal sales systems
- [ ] Third-party platforms
- [ ] Other: `[Specify sources]`

**How often do you receive data?**
- [ ] Daily
- [ ] Weekly
- [ ] Monthly
- [ ] Quarterly
- [ ] As needed
- [ ] Other: `[Specify frequency]`

### Data Structure
**What information is in your files?** (Check all that apply)
- [ ] Product identifiers (SKU, EAN, UPC)
- [ ] Sales quantities
- [ ] Sales amounts/revenue
- [ ] Dates (order date, delivery date, etc.)
- [ ] Customer/reseller information
- [ ] Geographic data (country, region)
- [ ] Other: `[Specify additional fields]`

**Sample Data**
Please provide 2-3 sample Excel files or describe the typical structure:
```
[Upload sample files or describe structure like:]
Column A: Product SKU
Column B: Sales Amount
Column C: Quantity
Column D: Month/Year
...
```

### Data Vendors/Partners
**Who are your main data providers?** (This helps us create detection rules)
1. `[Vendor Name]` - `[File format description]`
2. `[Vendor Name]` - `[File format description]`
3. `[Vendor Name]` - `[File format description]`

**Do different vendors use different file formats?**
- [ ] Yes, each vendor has unique format
- [ ] Some standardization exists
- [ ] Mostly standardized
- [ ] Don't know

---

## Database & Infrastructure

### Database Preferences
**Do you have a preferred database hosting solution?**
- [ ] AWS RDS
- [ ] Google Cloud SQL
- [ ] Azure Database
- [ ] Self-hosted PostgreSQL
- [ ] Other: `[Specify]`
- [ ] Need recommendations

**What's your current database experience level?**
- [ ] Expert (we manage our own databases)
- [ ] Intermediate (some database knowledge)
- [ ] Basic (minimal database experience)
- [ ] None (need full management)

### Infrastructure Requirements
**Where do you want this system deployed?**
- [ ] Our own cloud account (AWS/Google/Azure)
- [ ] On-premises servers
- [ ] Hybrid cloud
- [ ] Need recommendations

**Do you have specific security/compliance requirements?**
- [ ] GDPR compliance
- [ ] HIPAA compliance
- [ ] SOC 2 compliance
- [ ] Industry-specific regulations
- [ ] Internal security policies
- [ ] Other: `[Specify requirements]`

**Expected system usage:**
- Number of users: `[X users]`
- Files per month: `[X files]`
- Average file size: `[X MB]`
- Peak usage times: `[Description]`

---

## Functional Requirements

### Core Features (Check desired features)
- [ ] File upload and processing
- [ ] Data cleaning and normalization
- [ ] Interactive dashboards
- [ ] Data visualization/charts
- [ ] AI-powered chat queries
- [ ] Automated email reports
- [ ] Data export capabilities
- [ ] User management
- [ ] Audit trails

### Dashboard & Analytics
**What kind of insights do you need?** (Check all that apply)
- [ ] Sales performance by product
- [ ] Performance by reseller/partner
- [ ] Monthly/quarterly trends
- [ ] Geographic analysis
- [ ] Top performing products
- [ ] Comparative analysis
- [ ] Custom KPIs: `[Specify]`

**How do you want to view data?**
- [ ] Charts and graphs
- [ ] Data tables
- [ ] Summary reports
- [ ] Real-time dashboards
- [ ] Downloadable reports

### AI Chat Features
**What questions do you want to ask your data?**
Examples:
- `[e.g., "What were my top 5 products last quarter?"]`
- `[e.g., "Which reseller had the highest growth?"]`
- `[e.g., "Show me sales trends for Product X"]`

### Reporting Requirements
**What reports do you need?**
- [ ] Daily sales summaries
- [ ] Monthly performance reports
- [ ] Quarterly business reviews
- [ ] Custom reports: `[Specify]`

**Who should receive reports?**
- [ ] Management team
- [ ] Sales team
- [ ] Operations team
- [ ] External partners
- [ ] Other: `[Specify roles]`

**Preferred report formats:**
- [ ] PDF
- [ ] Excel
- [ ] Email summaries
- [ ] Dashboard links

---

## User & Access Management

### User Roles
**Who will use this system?**
1. **Administrators**: `[X users]` - Full system access
2. **Managers**: `[X users]` - View all data, generate reports
3. **Analysts**: `[X users]` - Data analysis and visualization
4. **Viewers**: `[X users]` - Read-only access
5. **Other**: `[Specify custom roles]`

### Authentication Requirements
**How should users log in?**
- [ ] Email/password
- [ ] Single Sign-On (SSO)
- [ ] Multi-factor authentication (MFA)
- [ ] Integration with existing system: `[Specify system]`

---

## Integration Requirements

### Existing Systems
**What systems do you currently use?**
- CRM: `[System name]`
- ERP: `[System name]`
- Analytics: `[System name]`
- Email: `[System name]`
- Other: `[List other systems]`

**Do you need to integrate with any of these?**
- [ ] Yes, specify: `[Which systems and what data]`
- [ ] Maybe in the future
- [ ] No integration needed

### API Requirements
**Do you need API access for:**
- [ ] Automated file uploads
- [ ] Data extraction
- [ ] Real-time data feeds
- [ ] Integration with other tools
- [ ] Not needed

---

## Design & User Experience

### Design Preferences
**Do you have brand guidelines?**
- [ ] Yes, we'll provide brand assets
- [ ] Some preferences: `[Specify colors, fonts, etc.]`
- [ ] Use modern, professional design
- [ ] Keep it simple

**Reference systems you like:**
`[Any dashboards or analytics tools you find well-designed]`

### User Experience Priorities
**What's most important for your users?** (Rank 1-5)
- [ ] Ease of use
- [ ] Speed/performance
- [ ] Detailed analytics
- [ ] Mobile access
- [ ] Customization

---

## Security & Compliance

### Security Requirements
**Security priorities:** (Check all that apply)
- [ ] Data encryption at rest
- [ ] Data encryption in transit
- [ ] User access controls
- [ ] Audit logging
- [ ] IP restrictions
- [ ] VPN access only
- [ ] Regular security updates

**Data retention requirements:**
- Keep data for: `[X months/years]`
- Automatic deletion: `[Yes/No]`
- Backup requirements: `[Specify]`

### Compliance Needs
**Regulatory requirements:**
- [ ] GDPR (EU data protection)
- [ ] CCPA (California privacy)
- [ ] HIPAA (Healthcare)
- [ ] SOX (Financial)
- [ ] Industry specific: `[Specify]`
- [ ] None required

---

## Technical Preferences

### Development Approach
**Do you have technical team to support this?**
- [ ] Yes, we have developers
- [ ] Limited technical resources
- [ ] Need full development support
- [ ] Need ongoing maintenance

**Preferred technologies:** (If you have preferences)
- Backend: `[Python/Node.js/etc.]`
- Frontend: `[React/Vue/etc.]`
- Database: `[PostgreSQL/MySQL/etc.]`
- Cloud: `[AWS/Google/Azure]`
- Other: `[Specify preferences]`

### Maintenance & Support
**What level of support do you need?**
- [ ] Initial setup only
- [ ] Ongoing maintenance
- [ ] 24/7 support
- [ ] Business hours support
- [ ] Training for internal team

---

## Timeline & Budget

### Project Timeline
**When do you need this completed?**
- Ideal launch date: `[YYYY-MM-DD]`
- Hard deadline: `[YYYY-MM-DD]`
- Flexible timeline: `[Yes/No]`

**Project phases:** (If you prefer phased approach)
- Phase 1: `[Core features, timeline]`
- Phase 2: `[Additional features, timeline]`
- Phase 3: `[Future enhancements, timeline]`

### Budget Considerations
**Budget range:** (Optional but helpful)
- [ ] Under $25K
- [ ] $25K - $50K
- [ ] $50K - $100K
- [ ] $100K+
- [ ] Need estimate

**Ongoing costs acceptable?**
- Monthly hosting: `[Budget range]`
- Maintenance: `[Budget range]`
- Support: `[Budget range]`

---

## Additional Requirements

### Special Considerations
**Anything else we should know?**
`[Any unique requirements, constraints, or special needs]`

**Potential challenges you foresee:**
`[Data quality issues, user adoption, technical constraints, etc.]`

**Success criteria - How will you measure success?**
- [ ] Time savings: `[X hours/week saved]`
- [ ] Data accuracy: `[Improvement goals]`
- [ ] User adoption: `[X% of team using]`
- [ ] Business impact: `[Revenue, efficiency, etc.]`
- [ ] Other: `[Specify metrics]`

---

## Sample Files & Documentation

### Required Attachments
Please provide:
- [ ] 2-3 sample Excel files (with sensitive data removed/anonymized)
- [ ] Current process documentation
- [ ] Brand guidelines (if available)
- [ ] Technical architecture diagrams (if available)
- [ ] Compliance requirements documentation

### Questions for Us
**What questions do you have about this project?**
`[Any concerns, clarifications needed, or additional questions]`

---

## Signature & Approval

**Completed by:**
- Name: `[Name]`
- Title: `[Title]`
- Date: `[YYYY-MM-DD]`
- Signature: `[Digital signature or approval]`

**Project Sponsor Approval:**
- Name: `[Name]`
- Title: `[Title]`
- Date: `[YYYY-MM-DD]`
- Signature: `[Digital signature or approval]`

---

*This template helps ensure we build exactly what you need while maintaining the highest security standards. The more detail you provide, the better we can tailor the solution to your specific requirements.*