from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, EmailStr
from typing import List, Dict, Any, Optional
import base64
import logging
from datetime import datetime
from app.services.email_service import EmailService
from app.services.report_service import ReportService
from app.services.auth_service import get_current_user
from app.models.auth import UserInDB
from app.utils.exceptions import AppException

logger = logging.getLogger(__name__)

router = APIRouter()

class EmailAttachment(BaseModel):
    filename: str
    data: str  # base64 encoded
    contentType: str

class EmailRequest(BaseModel):
    reportType: str
    recipientEmail: EmailStr
    attachments: Optional[List[EmailAttachment]] = None
    metadata: Optional[Dict[str, Any]] = None

class EmailResponse(BaseModel):
    success: bool
    messageId: str
    status: str
    timestamp: str
    autoResponse: str

class EmailLogRequest(BaseModel):
    recipientEmail: EmailStr
    subject: str
    message: str

class ReportGenerationRequest(BaseModel):
    uploadId: Optional[str] = None
    format: str = "pdf"
    autoSend: bool = False
    recipientEmail: Optional[EmailStr] = None

@router.post("/reports/email", response_model=EmailResponse)
async def send_report_email(
    request: EmailRequest,
    background_tasks: BackgroundTasks,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Send email with report attachments
    """
    try:
        logger.info(f"Sending report email to {request.recipientEmail} for user {current_user.email}")
        
        # Initialize email service
        email_service = EmailService()
        
        # Process attachments if provided
        processed_attachments = []
        if request.attachments:
            for attachment in request.attachments:
                try:
                    # Decode base64 data
                    decoded_data = base64.b64decode(attachment.data)
                    processed_attachments.append({
                        "filename": attachment.filename,
                        "data": decoded_data,
                        "content_type": attachment.contentType
                    })
                except Exception as e:
                    logger.error(f"Failed to process attachment {attachment.filename}: {e}")
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid attachment data for {attachment.filename}"
                    )
        
        # Send email
        result = email_service.send_report_email(
            recipient_email=request.recipientEmail,
            report_type=request.reportType,
            attachments=processed_attachments,
            metadata=request.metadata
        )
        
        # Log the email sending activity
        await log_email_activity(
            user_id=current_user.id,
            recipient_email=request.recipientEmail,
            email_type="report",
            status="sent",
            metadata=request.metadata
        )
        
        return EmailResponse(**result)
        
    except AppException as e:
        logger.error(f"Email service error: {e}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error sending email: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/email/notification")
async def send_notification_email(
    request: EmailLogRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Send notification email
    """
    try:
        logger.info(f"Sending notification email to {request.recipientEmail} for user {current_user.email}")
        
        # Initialize email service
        email_service = EmailService()
        
        # Send email
        result = email_service.send_notification_email(
            recipient_email=request.recipientEmail,
            subject=request.subject,
            message=request.message
        )
        
        # Log the email sending activity
        await log_email_activity(
            user_id=current_user.id,
            recipient_email=request.recipientEmail,
            email_type="notification",
            status="sent"
        )
        
        return result
        
    except AppException as e:
        logger.error(f"Email service error: {e}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error sending notification: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/email/logs")
async def get_email_logs(
    current_user: UserInDB = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0
):
    """
    Get email logs for the current user
    """
    try:
        from app.services.db_service import DatabaseService
        
        db_service = DatabaseService()
        
        # Query email logs
        query = """
        SELECT 
            id,
            recipient_email,
            email_type,
            status,
            sent_at,
            metadata,
            error_message
        FROM email_logs 
        WHERE user_id = %s 
        ORDER BY sent_at DESC 
        LIMIT %s OFFSET %s
        """
        
        logs = await db_service.fetch_all(query, (current_user.id, limit, offset))
        
        return {
            "logs": logs,
            "total": len(logs),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error fetching email logs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def log_email_activity(
    user_id: str,
    recipient_email: str,
    email_type: str,
    status: str,
    metadata: Optional[Dict[str, Any]] = None,
    error_message: Optional[str] = None
):
    """
    Log email activity to database
    """
    try:
        from app.services.db_service import DatabaseService
        
        db_service = DatabaseService()
        
        # Insert email log
        query = """
        INSERT INTO email_logs 
        (user_id, recipient_email, email_type, status, sent_at, metadata, error_message)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        await db_service.execute(
            query,
            (
                user_id,
                recipient_email,
                email_type,
                status,
                datetime.now(),
                metadata,
                error_message
            )
        )
        
    except Exception as e:
        logger.error(f"Failed to log email activity: {e}")
        # Don't raise exception here to avoid breaking the main email functionality

@router.post("/reports/generate")
async def generate_report(
    request: ReportGenerationRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Generate cleaning report and optionally send via email
    """
    try:
        logger.info(f"Generating report for user {current_user.email}")
        
        # Initialize report service
        report_service = ReportService()
        
        # Generate report
        report_data = await report_service.generate_cleaning_report(
            user_id=current_user.id,
            upload_id=request.uploadId,
            format=request.format
        )
        
        # If auto-send is enabled, send the report via email
        if request.autoSend and request.recipientEmail:
            email_service = EmailService()
            
            # Prepare attachment
            attachment = {
                "filename": report_data["filename"],
                "data": report_data["data"],
                "content_type": report_data["content_type"]
            }
            
            # Send email
            email_result = email_service.send_report_email(
                recipient_email=request.recipientEmail,
                report_type="cleaning_summary",
                attachments=[attachment],
                metadata=report_data["metadata"]
            )
            
            # Log email activity
            await log_email_activity(
                user_id=current_user.id,
                recipient_email=request.recipientEmail,
                email_type="report",
                status="sent",
                metadata=report_data["metadata"]
            )
            
            return {
                "report": report_data,
                "email": email_result
            }
        
        return {
            "report": report_data,
            "email": None
        }
        
    except AppException as e:
        logger.error(f"Report generation error: {e}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error generating report: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")