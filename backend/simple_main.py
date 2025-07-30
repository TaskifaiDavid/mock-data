from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

# Simple logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Data Cleaning Pipeline API - Test Mode",
    description="API for uploading and cleaning Excel files",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple test endpoints
@app.get("/")
async def root():
    return {"message": "Data Cleaning Pipeline API - Test Mode", "version": "1.0.0", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "mode": "test"}

@app.get("/api/status")
async def get_status():
    return {"uploads": [], "message": "Test mode - no real data"}

@app.post("/api/auth/login")
async def test_login():
    return {"access_token": "test_token", "token_type": "bearer", "user": {"id": "test", "email": "test@example.com"}}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting test server...")
    uvicorn.run(
        "simple_main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )