# DigitalOcean App Platform Deployment Guide

## Complete Guide for Full-Stack Data Processing Platform

This guide covers deploying your FastAPI + React + PostgreSQL application to DigitalOcean's App Platform.

## 📋 Prerequisites

- DigitalOcean account
- GitHub repository with your code
- Domain name (optional, can use App Platform provided domain)
- Supabase account (for PostgreSQL database)

## 🏗️ Architecture Overview

Your application consists of:
- **Frontend**: React app built with Vite
- **Backend**: FastAPI application with Python
- **Database**: PostgreSQL (via Supabase)
- **File Storage**: DigitalOcean Spaces or local uploads directory

## 🚀 Deployment Steps

### Step 1: Prepare Your Repository

1. **Organize your project structure**:
```
your-project/
├── frontend/          # React application
│   ├── package.json
│   ├── vite.config.js
│   └── src/
├── backend/           # FastAPI application
│   ├── requirements.txt
│   ├── main.py
│   └── app/
├── .env.example       # Environment variables template
└── README.md
```

2. **Create build configuration files**:

**Frontend Dockerfile** (`frontend/Dockerfile`):
```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Serve with nginx
FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**Frontend nginx.conf**:
```nginx
server {
    listen 80;
    location / {
        root /usr/share/nginx/html;
        index index.html index.htm;
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Backend Dockerfile** (`backend/Dockerfile`):
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p uploads

EXPOSE 8000

# Use uvicorn with proper configuration for production
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Step 2: Set Up Database

1. **Create Supabase Project**:
   - Go to [supabase.com](https://supabase.com)
   - Create new project
   - Note your project URL and anon key

2. **Configure Database Tables**:
   - Use Supabase SQL editor to run your schema migrations
   - Enable Row Level Security (RLS) for all tables
   - Set up authentication policies

### Step 3: Deploy to DigitalOcean App Platform

#### Option A: Using DigitalOcean Control Panel

1. **Create New App**:
   - Go to [DigitalOcean Control Panel](https://cloud.digitalocean.com/)
   - Click "Create" → "Apps"
   - Connect your GitHub repository

2. **Configure Services**:

**Frontend Service**:
```yaml
name: frontend
source_dir: /frontend
github:
  repo: your-username/your-repo
  branch: main
dockerfile_path: frontend/Dockerfile
http_port: 80
instance_count: 1
instance_size_slug: basic-xxs
routes:
- path: /
```

**Backend Service**:
```yaml
name: backend
source_dir: /backend
github:
  repo: your-username/your-repo
  branch: main
dockerfile_path: backend/Dockerfile
http_port: 8000
instance_count: 1
instance_size_slug: basic-xs
routes:
- path: /api
```

#### Option B: Using App Spec YAML

Create `.do/app.yaml`:
```yaml
name: data-processing-platform
services:
- name: frontend
  source_dir: /frontend
  github:
    repo: your-username/your-repo
    branch: main
    deploy_on_push: true
  dockerfile_path: frontend/Dockerfile
  http_port: 80
  instance_count: 1
  instance_size_slug: basic-xxs
  routes:
  - path: /

- name: backend
  source_dir: /backend
  github:
    repo: your-username/your-repo
    branch: main
    deploy_on_push: true
  dockerfile_path: backend/Dockerfile
  http_port: 8000
  instance_count: 1
  instance_size_slug: basic-xs
  routes:
  - path: /api
  envs:
  - key: SUPABASE_URL
    value: ${SUPABASE_URL}
  - key: SUPABASE_ANON_KEY
    value: ${SUPABASE_ANON_KEY}
  - key: SUPABASE_SERVICE_KEY
    value: ${SUPABASE_SERVICE_KEY}
    type: SECRET
  - key: JWT_SECRET_KEY
    value: ${JWT_SECRET_KEY}
    type: SECRET
  - key: DATABASE_URL
    value: ${DATABASE_URL}
    type: SECRET
  - key: OPENAI_API_KEY
    value: ${OPENAI_API_KEY}
    type: SECRET

static_sites:
- name: assets
  source_dir: /frontend/dist
  github:
    repo: your-username/your-repo
    branch: main
  routes:
  - path: /assets
```

### Step 4: Configure Environment Variables

**Required Environment Variables**:

| Variable | Description | Example |
|----------|-------------|---------|
| `SUPABASE_URL` | Your Supabase project URL | `https://xxx.supabase.co` |
| `SUPABASE_ANON_KEY` | Supabase anonymous key | `eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...` |
| `SUPABASE_SERVICE_KEY` | Supabase service role key (SECRET) | `eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...` |
| `JWT_SECRET_KEY` | JWT signing secret (SECRET) | Generate with `openssl rand -hex 32` |
| `DATABASE_URL` | PostgreSQL connection string (SECRET) | `postgresql://user:pass@host:port/db` |
| `OPENAI_API_KEY` | OpenAI API key (SECRET) | `sk-...` |

**Setting Environment Variables**:
1. In DigitalOcean control panel, go to your app
2. Click "Settings" tab
3. Scroll to "Environment Variables"
4. Add each variable, marking sensitive ones as "Encrypted"

### Step 5: Domain Configuration

#### Using Custom Domain:
1. **Add Domain to App**:
   - Go to app Settings → Domains
   - Add your domain (e.g., `yourdomain.com`)
   - DigitalOcean will provide DNS records

2. **Update DNS**:
   - Add CNAME record: `www` → `your-app.ondigitalocean.app`
   - Add ALIAS/ANAME record: `@` → `your-app.ondigitalocean.app`

3. **SSL Certificate**:
   - DigitalOcean automatically provisions Let's Encrypt SSL
   - Certificate auto-renews

### Step 6: Production Optimizations

#### Backend Optimizations:

1. **Add Health Check Endpoint**:
```python
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}
```

2. **Configure Logging**:
```python
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
```

3. **Add CORS Configuration**:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com", "https://your-app.ondigitalocean.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### Frontend Optimizations:

1. **Optimize Vite Build**:
```javascript
// vite.config.js
export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          charts: ['chart.js', 'react-chartjs-2']
        }
      }
    }
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

### Step 7: Multi-Environment Setup

Create separate apps for different environments:

**Development Environment**:
- App name: `your-app-dev`
- Branch: `develop`
- Smaller instance sizes
- Development database

**Staging Environment**:
- App name: `your-app-staging`
- Branch: `staging`
- Production-like configuration
- Staging database

**Production Environment**:
- App name: `your-app-prod`
- Branch: `main`
- Optimized instance sizes
- Production database with backups

### Step 8: Monitoring and Scaling

#### Enable Monitoring:
1. **App Platform Insights**:
   - CPU and memory usage
   - Request metrics
   - Error rates

2. **Application Logs**:
   - Access via DigitalOcean console
   - Structured logging in JSON format

3. **Database Monitoring**:
   - Supabase built-in monitoring
   - Query performance insights

#### Scaling Configuration:

**Horizontal Scaling**:
```yaml
services:
- name: backend
  instance_count: 2  # Multiple instances
  autoscaling:
    min_instance_count: 1
    max_instance_count: 5
    metrics:
    - type: cpu
      threshold: 70
```

**Vertical Scaling**:
- Start with `basic-xs` for backend
- Upgrade to `basic-s` or `professional-xs` based on load
- Frontend can usually stay on `basic-xxs`

## 💰 Cost Estimation

**Starter Configuration**:
- Frontend (basic-xxs): $5/month
- Backend (basic-xs): $10/month
- **Total: ~$15/month**

**Production Configuration**:
- Frontend (basic-xxs): $5/month
- Backend (professional-xs): $25/month
- Database (Supabase Pro): $25/month
- **Total: ~$55/month**

## 🚨 Security Best Practices

1. **Environment Variables**:
   - Never commit secrets to git
   - Use DigitalOcean's encrypted environment variables
   - Rotate secrets regularly

2. **Database Security**:
   - Enable Row Level Security (RLS)
   - Use service role key only for admin operations
   - Regular security updates

3. **API Security**:
   - Implement rate limiting
   - Use HTTPS only
   - Validate all inputs
   - Implement proper error handling

4. **CORS Configuration**:
   - Restrict origins to your domains only
   - Don't use wildcard (*) in production

## 🔧 Troubleshooting

**Common Issues**:

1. **Build Failures**:
   - Check Dockerfile syntax
   - Verify all dependencies in requirements.txt/package.json
   - Review build logs in App Platform

2. **Environment Variable Issues**:
   - Verify all required variables are set
   - Check for typos in variable names
   - Ensure secrets are marked as encrypted

3. **Database Connection Issues**:
   - Verify DATABASE_URL format
   - Check Supabase connection limits
   - Review RLS policies

4. **CORS Errors**:
   - Update allowed origins
   - Check request methods and headers
   - Verify preflight requests

## 📞 Support Resources

- [DigitalOcean App Platform Documentation](https://docs.digitalocean.com/products/app-platform/)
- [Supabase Documentation](https://supabase.com/docs)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [React Production Deployment](https://create-react-app.dev/docs/deployment/)

## 🎯 Next Steps

After deployment:
1. Set up monitoring and alerting
2. Implement automated testing in CI/CD
3. Configure automated backups
4. Set up staging environment
5. Implement blue-green deployments
6. Add performance monitoring
7. Set up log aggregation

---

**🔗 Useful Commands**:

```bash
# Test local Docker builds
docker build -t frontend ./frontend
docker build -t backend ./backend

# Check app status
doctl apps list
doctl apps get <app-id>

# View app logs
doctl apps logs <app-id> --follow
```

This guide provides a production-ready deployment strategy for your full-stack data processing platform on DigitalOcean App Platform.