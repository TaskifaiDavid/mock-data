from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class UploadStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class UploadResponse(BaseModel):
    id: str
    filename: str
    status: UploadStatus
    uploaded_at: datetime
    rows_processed: Optional[int] = None
    rows_cleaned: Optional[int] = None
    error_message: Optional[str] = None

class ProcessingStatus(BaseModel):
    upload_id: str
    status: UploadStatus
    progress: Optional[int] = None
    message: Optional[str] = None
    rows_processed: Optional[int] = None
    rows_cleaned: Optional[int] = None
    processing_time_ms: Optional[int] = None

class SelloutEntry(BaseModel):
    product_ean: Optional[str] = None
    month: Optional[int] = None
    year: Optional[int] = None
    quantity: Optional[int] = None
    sales_lc: Optional[str] = None
    sales_eur: Optional[float] = None
    currency: Optional[str] = None
    reseller: Optional[str] = None
    functional_name: Optional[str] = None
    upload_id: Optional[str] = None

class Product(BaseModel):
    ean: str
    name: Optional[str] = None
    brand: str = "BIBBI"