from fastapi import APIRouter, UploadFile, File, Depends, BackgroundTasks
from app.models.upload import UploadResponse, UploadStatus
from app.api.auth import get_current_user
from app.services.file_service import FileService
from app.services.cleaning_service import CleaningService
from app.utils.exceptions import ValidationException, FileProcessingException
from app.utils.config import get_settings
import uuid
from datetime import datetime

router = APIRouter(prefix="/upload", tags=["upload"])

async def get_file_service() -> FileService:
    return FileService()

async def get_cleaning_service() -> CleaningService:
    return CleaningService()

@router.post("/", response_model=UploadResponse)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    file_service: FileService = Depends(get_file_service),
    cleaning_service: CleaningService = Depends(get_cleaning_service)
):
    settings = get_settings()
    
    # Validate file
    if not file.filename.endswith(tuple(settings.allowed_extensions)):
        raise ValidationException(f"Only {settings.allowed_extensions} files are allowed")
    
    # Check file size
    file_size = 0
    contents = await file.read()
    file_size = len(contents)
    
    if file_size > settings.max_upload_size:
        raise ValidationException(f"File size exceeds {settings.max_upload_size / 1024 / 1024}MB limit")
    
    # Reset file position
    await file.seek(0)
    
    # Create upload record
    upload_id = str(uuid.uuid4())
    upload_response = UploadResponse(
        id=upload_id,
        filename=file.filename,
        status=UploadStatus.PENDING,
        uploaded_at=datetime.utcnow()
    )
    
    # Save file and create database record
    await file_service.save_upload(upload_id, file, current_user["id"])
    
    # Process file in background
    background_tasks.add_task(
        cleaning_service.process_file,
        upload_id,
        file.filename,
        contents,
        current_user["id"]
    )
    
    return upload_response