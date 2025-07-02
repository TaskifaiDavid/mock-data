# Data Cleaning Pipeline Web App

A lightweight web application for authenticated users to upload Excel files and automatically clean, normalize, and persist data in Supabase.

## Features

- Secure user authentication via Supabase
- Excel file upload (.xlsx up to 10MB)
- Intelligent data cleaning pipeline with vendor-specific rules
- Automatic schema detection and normalization
- Data persistence in Supabase
- Processing status tracking and error reporting

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
   cp .env.example .env
   # Edit .env with your Supabase credentials
   ```

3. **Setup Supabase:**
   - Create a new Supabase project
   - Run the schema in `database/schema.sql`
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