from fastapi import APIRouter, Depends, HTTPException
from app.models.upload import ProcessingStatus
from app.api.auth import get_current_user
from app.services.db_service import DatabaseService
from typing import List, Dict, Any

router = APIRouter(prefix="/status", tags=["status"])

async def get_db_service() -> DatabaseService:
    return DatabaseService()

@router.get("/uploads")
async def get_user_uploads(
    current_user: dict = Depends(get_current_user),
    db_service: DatabaseService = Depends(get_db_service)
) -> List[Dict[str, Any]]:
    """Get all uploads for the current user"""
    uploads = await db_service.get_user_uploads(current_user["id"])
    return uploads

@router.get("/{upload_id}", response_model=ProcessingStatus)
async def get_status(
    upload_id: str,
    current_user: dict = Depends(get_current_user),
    db_service: DatabaseService = Depends(get_db_service)
):
    status = await db_service.get_upload_status(upload_id, current_user["id"])
    
    if not status:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    return status