from fastapi import APIRouter, Request, Header
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
import json
import os
from datetime import datetime

router = APIRouter(prefix="/webhook", tags=["webhook"])
logger = logging.getLogger(__name__)

class WebhookResponse(BaseModel):
    success: bool
    message: str
    timestamp: str
    received_data: Optional[Dict[str, Any]] = None

@router.post("/", response_model=WebhookResponse)
@router.post("", response_model=WebhookResponse)
async def receive_webhook(request: Request, x_webhook_key: Optional[str] = Header(None)):
    """
    Simple webhook endpoint for Make.com integration.
    Accepts any JSON data with optional authentication via X-Webhook-Key header.
    Available at both /api/webhook/ and /api/webhook (with and without trailing slash).
    """
    try:
        # Optional security: Check webhook key if configured
        webhook_key = os.getenv("WEBHOOK_KEY")
        if webhook_key and x_webhook_key != webhook_key:
            logger.warning(f"Invalid webhook key from {request.client.host if request.client else 'unknown'}")
            return WebhookResponse(
                success=False,
                message="Invalid webhook key",
                timestamp=datetime.now().isoformat()
            )
        # Get the raw request body
        body = await request.body()
        
        # Parse JSON if available
        webhook_data = {}
        if body:
            try:
                webhook_data = json.loads(body.decode('utf-8'))
            except json.JSONDecodeError:
                webhook_data = {"raw_body": body.decode('utf-8', errors='ignore')}
        
        # Log the webhook call
        logger.info(f"Webhook received from {request.client.host if request.client else 'unknown'}")
        logger.info(f"Webhook data: {webhook_data}")
        
        # Return success response
        response = WebhookResponse(
            success=True,
            message="Webhook received successfully",
            timestamp=datetime.now().isoformat(),
            received_data=webhook_data
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return WebhookResponse(
            success=False,
            message=f"Error processing webhook: {str(e)}",
            timestamp=datetime.now().isoformat()
        )

@router.post("/test", response_model=WebhookResponse)
async def test_webhook(data: Dict[str, Any]):
    """
    Test endpoint for webhook with JSON validation.
    Useful for testing from tools like Postman.
    """
    try:
        logger.info(f"Test webhook called with data: {data}")
        
        return WebhookResponse(
            success=True,
            message="Test webhook received successfully",
            timestamp=datetime.now().isoformat(),
            received_data=data
        )
        
    except Exception as e:
        logger.error(f"Error in test webhook: {str(e)}")
        return WebhookResponse(
            success=False,
            message=f"Error in test webhook: {str(e)}",
            timestamp=datetime.now().isoformat()
        )

@router.get("/health")
async def webhook_health():
    """Health check endpoint for webhook service"""
    return {
        "status": "healthy",
        "service": "webhook",
        "timestamp": datetime.now().isoformat()
    }