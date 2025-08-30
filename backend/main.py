from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api import auth, upload, status, email, dashboard, webhook, chat, migration
from app.utils.config import get_settings
from app.utils.exceptions import AppException
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Apply centralized logging configuration
from app.utils.logging_config import configure_application_logging, get_logger

configure_application_logging()
logger = get_logger(__name__)

app = FastAPI(
    title="Data Cleaning Pipeline API",
    description="API for uploading and cleaning Excel files",
    version="1.0.0"
)

settings = get_settings()

# CORS middleware - Environment-based configuration
def get_cors_origins():
    """Get CORS origins based on environment"""
    cors_origins = os.getenv("CORS_ORIGINS", "").split(",")
    if not cors_origins or cors_origins == [""]:
        # Development defaults
        return [
            "http://localhost:5173", 
            "http://localhost:5174",
            "http://localhost:5175",
            "http://localhost:5176",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:5174",
            "http://127.0.0.1:5175",
            "http://127.0.0.1:5176"
        ]
    return [origin.strip() for origin in cors_origins if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Standardized error response handler."""
    
    # Log the exception with context
    logger.error(
        f"AppException handled: {exc.message}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": exc.status_code,
            "details": exc.details,
            "user_agent": request.headers.get("user-agent"),
            "exception_type": exc.__class__.__name__
        }
    )
    
    # Return standardized error response
    response_content = {
        "error": exc.message,
        "status_code": exc.status_code
    }
    
    # Include details in development/debug mode
    if settings.environment == "development" and exc.details:
        response_content["details"] = exc.details
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response_content
    )

# Handle unexpected exceptions
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions with proper logging."""
    
    logger.error(
        f"Unexpected exception: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "exception_type": exc.__class__.__name__,
            "user_agent": request.headers.get("user-agent")
        },
        exc_info=True
    )
    
    # Don't leak internal details in production
    if settings.environment == "development":
        message = f"Internal server error: {str(exc)}"
    else:
        message = "Internal server error"
    
    return JSONResponse(
        status_code=500,
        content={"error": message, "status_code": 500}
    )

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(upload.router, prefix="/api")
app.include_router(status.router, prefix="/api")
app.include_router(email.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api/dashboards")
app.include_router(webhook.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(migration.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Data Cleaning Pipeline API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )