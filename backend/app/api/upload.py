from fastapi import APIRouter, UploadFile, File, Depends, BackgroundTasks, Header
from app.models.upload import UploadResponse, UploadStatus
from app.api.auth import get_current_user
from app.services.file_service import FileService
from app.services.cleaning_service import CleaningService
from app.utils.exceptions import ValidationException, FileProcessingException, DatabaseException
from app.utils.config import get_settings
import uuid
from datetime import datetime
from typing import List, Optional

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
    authorization: Optional[str] = Header(None),
    file_service: FileService = Depends(get_file_service),
    cleaning_service: CleaningService = Depends(get_cleaning_service)
):
    settings = get_settings()
    
    # Extract token for database operations
    user_token = None
    if authorization and authorization.startswith("Bearer "):
        user_token = authorization.split(" ")[1]
    
    # Create services with user token
    file_service_with_token = FileService(user_token=user_token)
    
    # Debug: Log current_user contents
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Current user object: {current_user}")
    logger.info(f"User ID being used: {current_user['id']}")
    
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
    try:
        await file_service_with_token.save_upload(upload_id, file, current_user["id"])
    except DatabaseException as e:
        raise ValidationException(f"Upload failed: {str(e)}")
    except Exception as e:
        raise FileProcessingException(f"Failed to save file: {str(e)}")
    
    # Process file in background
    background_tasks.add_task(
        cleaning_service.process_file,
        upload_id,
        file.filename,
        contents,
        current_user["id"]
    )
    
    return upload_response

@router.post("/multiple", response_model=List[UploadResponse])
async def upload_multiple_files(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    current_user: dict = Depends(get_current_user),
    authorization: Optional[str] = Header(None),
    file_service: FileService = Depends(get_file_service),
    cleaning_service: CleaningService = Depends(get_cleaning_service)
):
    """Upload multiple files and process them in queue"""
    settings = get_settings()
    
    # Extract token for database operations
    user_token = None
    if authorization and authorization.startswith("Bearer "):
        user_token = authorization.split(" ")[1]
    
    # Create services with user token
    file_service_with_token = FileService(user_token=user_token)
    
    upload_responses = []
    valid_files = []
    
    # Validate all files first
    for file in files:
        try:
            # Validate file extension
            if not file.filename.endswith(tuple(settings.allowed_extensions)):
                raise ValidationException(f"File {file.filename}: Only {settings.allowed_extensions} files are allowed")
            
            # Check file size
            contents = await file.read()
            file_size = len(contents)
            
            if file_size > settings.max_upload_size:
                raise ValidationException(f"File {file.filename}: Size exceeds {settings.max_upload_size / 1024 / 1024}MB limit")
            
            # Reset file position
            await file.seek(0)
            
            # Store file info for processing
            valid_files.append({
                'file': file,
                'contents': contents,
                'size': file_size
            })
            
        except Exception as e:
            # Create failed upload record for invalid files
            upload_id = str(uuid.uuid4())
            upload_response = UploadResponse(
                id=upload_id,
                filename=file.filename,
                status=UploadStatus.FAILED,
                uploaded_at=datetime.utcnow()
            )
            upload_responses.append(upload_response)
            continue
    
    # Create upload records for all valid files
    for file_info in valid_files:
        file = file_info['file']
        contents = file_info['contents']
        
        upload_id = str(uuid.uuid4())
        upload_response = UploadResponse(
            id=upload_id,
            filename=file.filename,
            status=UploadStatus.PENDING,
            uploaded_at=datetime.utcnow()
        )
        upload_responses.append(upload_response)
        
        # Save file and create database record
        try:
            await file_service_with_token.save_upload(upload_id, file, current_user["id"])
        except DatabaseException as e:
            # Mark this upload as failed and continue with others
            upload_response.status = UploadStatus.FAILED
            continue
        except Exception as e:
            # Mark this upload as failed and continue with others
            upload_response.status = UploadStatus.FAILED
            continue
        
        # Add to processing queue (process files sequentially)
        background_tasks.add_task(
            cleaning_service.process_file,
            upload_id,
            file.filename,
            contents,
            current_user["id"]
        )
    
    return upload_responses