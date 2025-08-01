import os
from pathlib import Path
from fastapi import UploadFile
from app.services.db_service import DatabaseService
from app.utils.exceptions import FileProcessingException
from typing import Optional

class FileService:
    def __init__(self, user_token: str = None):
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(exist_ok=True)
        self.db_service = DatabaseService(user_token=user_token)
    
    async def save_upload(self, upload_id: str, file: UploadFile, user_id: str) -> str:
        try:
            # Save file to disk
            file_path = self.upload_dir / f"{upload_id}_{file.filename}"
            
            contents = await file.read()
            with open(file_path, "wb") as f:
                f.write(contents)
            
            # Create database record
            await self.db_service.create_upload_record(
                upload_id=upload_id,
                user_id=user_id,
                filename=file.filename,
                file_size=len(contents)
            )
            
            return str(file_path)
        except Exception as e:
            raise FileProcessingException(f"Failed to save file: {str(e)}")
    
    async def get_file_path(self, upload_id: str, filename: str) -> Optional[Path]:
        file_path = self.upload_dir / f"{upload_id}_{filename}"
        return file_path if file_path.exists() else None
    
    async def delete_file(self, upload_id: str, filename: str) -> bool:
        file_path = self.upload_dir / f"{upload_id}_{filename}"
        if file_path.exists():
            os.remove(file_path)
            return True
        return False