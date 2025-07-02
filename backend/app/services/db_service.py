from supabase import create_client, Client
from app.utils.config import get_settings
from app.utils.exceptions import DatabaseException
from app.models.upload import UploadStatus, ProcessingStatus
from typing import Optional, List, Dict, Any
import json
from datetime import datetime

class DatabaseService:
    def __init__(self):
        settings = get_settings()
        self.supabase: Client = create_client(
            settings.supabase_url,
            settings.supabase_service_key
        )
    
    async def create_upload_record(self, upload_id: str, user_id: str, filename: str, file_size: int):
        try:
            data = {
                "id": upload_id,
                "user_id": user_id,
                "filename": filename,
                "file_size": file_size,
                "status": UploadStatus.PENDING.value
            }
            
            self.supabase.table("uploads").insert(data).execute()
        except Exception as e:
            raise DatabaseException(f"Failed to create upload record: {str(e)}")
    
    async def update_upload_status(
        self,
        upload_id: str,
        status: UploadStatus,
        error_message: Optional[str] = None,
        rows_processed: Optional[int] = None,
        rows_cleaned: Optional[int] = None,
        processing_time_ms: Optional[int] = None
    ):
        try:
            update_data = {"status": status.value}
            
            if error_message:
                update_data["error_message"] = error_message
            if rows_processed is not None:
                update_data["rows_processed"] = rows_processed
            if rows_cleaned is not None:
                update_data["rows_cleaned"] = rows_cleaned
            if processing_time_ms is not None:
                update_data["processing_time_ms"] = processing_time_ms
            
            self.supabase.table("uploads").update(update_data).eq("id", upload_id).execute()
        except Exception as e:
            raise DatabaseException(f"Failed to update upload status: {str(e)}")
    
    async def get_upload_status(self, upload_id: str, user_id: str) -> Optional[ProcessingStatus]:
        try:
            result = self.supabase.table("uploads").select("*").eq("id", upload_id).eq("user_id", user_id).single().execute()
            
            if result.data:
                return ProcessingStatus(
                    upload_id=result.data["id"],
                    status=UploadStatus(result.data["status"]),
                    message=result.data.get("error_message"),
                    rows_processed=result.data.get("rows_processed"),
                    rows_cleaned=result.data.get("rows_cleaned"),
                    processing_time_ms=result.data.get("processing_time_ms")
                )
            return None
        except Exception:
            return None
    
    async def insert_sellout_entries(self, upload_id: str, entries: List[Dict[str, Any]]):
        try:
            print(f"DB Service: Starting insert_sellout_entries for upload {upload_id} with {len(entries)} entries")
            
            # First, ensure all products exist
            print("DB Service: Ensuring products exist...")
            await self._ensure_products_exist(entries)
            print("DB Service: Products ensured successfully")
            
            # Prepare sellout entries
            data = []
            for i, entry in enumerate(entries):
                sellout_entry = {
                    "upload_id": upload_id,
                    "product_ean": entry.get("product_ean"),
                    "month": entry.get("month"),
                    "year": entry.get("year"),
                    "quantity": entry.get("quantity"),
                    "sales_lc": entry.get("sales_lc"),
                    "sales_eur": entry.get("sales_eur"),
                    "currency": entry.get("currency"),
                    "reseller": entry.get("reseller"),
                    "functional_name": entry.get("functional_name")
                }
                # Only add non-null values
                sellout_entry = {k: v for k, v in sellout_entry.items() if v is not None}
                data.append(sellout_entry)
                
                if i < 3:  # Log first 3 entries
                    print(f"DB Service: Entry {i}: {sellout_entry}")
            
            print(f"DB Service: Prepared {len(data)} entries for insertion")
            
            # Insert in batches to avoid size limits
            batch_size = 100
            total_inserted = 0
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                print(f"DB Service: Inserting batch {i//batch_size + 1} with {len(batch)} entries")
                
                result = self.supabase.table("sellout_entries2").insert(batch).execute()
                print(f"DB Service: Batch insert result: {result}")
                total_inserted += len(batch)
                
            print(f"DB Service: Successfully inserted {total_inserted} total entries")
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"DB Service: Error inserting sellout entries: {str(e)}")
            print(f"DB Service: Full traceback: {error_details}")
            raise DatabaseException(f"Failed to insert sellout entries: {str(e)}")
    
    async def _ensure_products_exist(self, entries: List[Dict[str, Any]]):
        """Ensure all products exist in the products table"""
        try:
            # Get unique EANs from entries
            eans = set()
            for entry in entries:
                if entry.get("product_ean"):
                    eans.add(entry["product_ean"])
            
            if not eans:
                return
            
            # Check which products already exist
            existing_result = self.supabase.table("products").select("ean").in_("ean", list(eans)).execute()
            existing_eans = {row["ean"] for row in existing_result.data} if existing_result.data else set()
            
            # Create missing products
            missing_eans = eans - existing_eans
            if missing_eans:
                products_to_create = []
                for ean in missing_eans:
                    # Find the functional name for this EAN
                    functional_name = None
                    for entry in entries:
                        if entry.get("product_ean") == ean and entry.get("functional_name"):
                            functional_name = entry["functional_name"]
                            break
                    
                    products_to_create.append({
                        "ean": ean,
                        "name": functional_name,
                        "brand": "BIBBI"
                    })
                
                # Insert missing products
                self.supabase.table("products").insert(products_to_create).execute()
        except Exception as e:
            # Log but don't fail the entire process
            print(f"Warning: Failed to ensure products exist: {str(e)}")
    
    async def log_transformation(
        self,
        upload_id: str,
        row_index: int,
        column_name: str,
        original_value: Any,
        cleaned_value: Any,
        transformation_type: str
    ):
        try:
            data = {
                "upload_id": upload_id,
                "row_index": row_index,
                "column_name": column_name,
                "original_value": str(original_value) if original_value is not None else None,
                "cleaned_value": str(cleaned_value) if cleaned_value is not None else None,
                "transformation_type": transformation_type
            }
            
            self.supabase.table("transform_logs").insert(data).execute()
        except Exception:
            # Log transformation failures are non-critical
            pass