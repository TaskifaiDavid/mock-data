from fastapi import APIRouter, Depends, HTTPException, Header
from app.models.upload import ProcessingStatus
from app.models.auth import UserInDB
from app.api.auth import get_current_user
from app.services.db_service import DatabaseService
from typing import List, Dict, Any, Optional

router = APIRouter(prefix="/status", tags=["status"])

@router.get("/uploads")
async def get_user_uploads(
    current_user: UserInDB = Depends(get_current_user),
    authorization: Optional[str] = Header(None)
) -> List[Dict[str, Any]]:
    """Get all uploads for the current user"""
    import logging
    logger = logging.getLogger(__name__)
    
    # Debug logging
    logger.info(f"🔍 STATUS DEBUG - Current user: {current_user}")
    logger.info(f"🔍 STATUS DEBUG - User ID: {current_user.id}")
    logger.info(f"🔍 STATUS DEBUG - User email: {current_user.email}")
    
    # Extract token for database operations
    user_token = None
    if authorization and authorization.startswith("Bearer "):
        user_token = authorization.split(" ")[1]
        logger.info(f"🔍 STATUS DEBUG - Token extracted, length: {len(user_token)}")
    
    # Create DatabaseService with user token for RLS
    db_service = DatabaseService(user_token=user_token)
    uploads = await db_service.get_user_uploads(current_user.id)
    
    logger.info(f"🔍 STATUS DEBUG - Query returned {len(uploads)} uploads")
    if uploads:
        logger.info(f"🔍 STATUS DEBUG - Sample upload: {uploads[0]}")
    
    return uploads

@router.get("/{upload_id}", response_model=ProcessingStatus)
async def get_status(
    upload_id: str,
    current_user: UserInDB = Depends(get_current_user),
    authorization: Optional[str] = Header(None)
):
    # Extract token for database operations
    user_token = None
    if authorization and authorization.startswith("Bearer "):
        user_token = authorization.split(" ")[1]
    
    # Create DatabaseService with user token for RLS
    db_service = DatabaseService(user_token=user_token)
    status = await db_service.get_upload_status(upload_id, current_user.id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    return status