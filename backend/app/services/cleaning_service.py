import pandas as pd
import io
from typing import Dict, Any, List, Optional
from datetime import datetime
import time
from app.services.db_service import DatabaseService
from app.models.upload import UploadStatus
from app.pipeline.detector import VendorDetector
from app.pipeline.cleaners import DataCleaner
from app.pipeline.normalizers import DataNormalizer
import logging

logger = logging.getLogger(__name__)

class CleaningService:
    def __init__(self):
        self.db_service = DatabaseService()
        self.vendor_detector = VendorDetector()
        self.data_cleaner = DataCleaner(db_service=self.db_service)
        self.data_normalizer = DataNormalizer()
    
    async def process_file(self, upload_id: str, filename: str, file_contents: bytes, user_id: str):
        start_time = time.time()
        
        try:
            logger.info(f"Starting background task for upload {upload_id}, filename: {filename}, user: {user_id}")
            
            # Update status to processing
            await self.db_service.update_upload_status(upload_id, UploadStatus.PROCESSING)
            logger.info(f"Updated upload {upload_id} status to PROCESSING")
            
            # Read Excel file with better debugging
            excel_file = pd.ExcelFile(io.BytesIO(file_contents))
            logger.info(f"Excel file sheet names: {excel_file.sheet_names}")
            
            # Read the first sheet (or try to find the right sheet)
            sheet_name = excel_file.sheet_names[0]  # Default to first sheet
            
            # For Skins NL, try to find SalesPerSKU sheet if available
            if any("salespersku" in name.lower() for name in excel_file.sheet_names):
                sheet_name = next(name for name in excel_file.sheet_names if "salespersku" in name.lower())
                logger.info(f"Found SalesPerSKU sheet: {sheet_name}")
            
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            logger.info(f"Loaded Excel sheet '{sheet_name}' with {len(df)} rows, columns: {list(df.columns)}")
            logger.info(f"First 3 rows preview: {df.head(3).to_dict('records')}")
            logger.info(f"Data types: {df.dtypes.to_dict()}")
            
            # Debug: Count non-empty rows for each column to understand data distribution
            if len(df) > 0:
                logger.info("Column data distribution:")
                for col in df.columns:
                    non_empty = df[col].notna().sum()
                    logger.info(f"  {col}: {non_empty}/{len(df)} non-empty values")
                    
                # Show last few rows to see if data extends to end of file
                logger.info(f"Last 3 rows preview: {df.tail(3).to_dict('records')}")
            
            # Detect vendor
            vendor = self.vendor_detector.detect_vendor(filename, df)
            logger.info(f"Detected vendor: {vendor}")
            
            # Clean data
            cleaned_df, transformations = await self.data_cleaner.clean_data(df, vendor, filename)
            logger.info(f"Cleaned {len(cleaned_df)} rows (original: {len(df)})")
            logger.info(f"Transformations applied: {len(transformations)}")
            logger.info(f"Cleaned data columns: {list(cleaned_df.columns)}")
            if len(cleaned_df) > 0:
                logger.info(f"Cleaned data sample: {cleaned_df.head(3).to_dict('records')}")
                logger.info(f"Cleaned data types: {cleaned_df.dtypes.to_dict()}")
            else:
                logger.warning("No rows left after cleaning!")
            
            # Normalize data
            normalized_df = await self.data_normalizer.normalize_data(cleaned_df, vendor)
            logger.info(f"Normalized {len(normalized_df)} rows")
            if len(normalized_df) > 0:
                logger.info(f"Normalized data sample: {normalized_df.head(3).to_dict('records')}")
                logger.info(f"Normalized columns: {list(normalized_df.columns)}")
                logger.info(f"Normalized data types: {normalized_df.dtypes.to_dict()}")
                
                # Check for required fields
                required_fields = ['product_ean', 'quantity', 'year', 'month']
                missing_fields = [field for field in required_fields if field not in normalized_df.columns or normalized_df[field].isna().all()]
                if missing_fields:
                    logger.warning(f"Missing required fields: {missing_fields}")
                else:
                    logger.info("All required fields present")
            else:
                logger.warning("No rows left after normalization!")
            
            # Convert to records for sellout_entries2 table
            sellout_entries = normalized_df.to_dict('records')
            logger.info(f"Converting {len(sellout_entries)} entries for database insertion")
            
            if len(sellout_entries) > 0:
                logger.info(f"Sample entry for insertion: {sellout_entries[0]}")
                
                # Save to database
                logger.info(f"Attempting to insert {len(sellout_entries)} entries into sellout_entries2")
                await self.db_service.insert_sellout_entries(upload_id, sellout_entries)
                logger.info(f"Successfully inserted {len(sellout_entries)} entries into sellout_entries2")
                
                # Log transformations
                logger.info(f"Logging {len(transformations)} transformations")
                for transform in transformations:
                    await self.db_service.log_transformation(
                        upload_id=upload_id,
                        **transform
                    )
                logger.info("Transformations logged successfully")
            else:
                logger.warning("No entries to insert - processing completed with 0 records")
            
            # Calculate processing time
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            # Update status to completed
            await self.db_service.update_upload_status(
                upload_id=upload_id,
                status=UploadStatus.COMPLETED,
                rows_processed=len(df),
                rows_cleaned=len(cleaned_df),
                processing_time_ms=processing_time_ms
            )
            
            logger.info(f"Successfully processed upload {upload_id} - {len(df)} original rows, {len(cleaned_df)} cleaned, {len(sellout_entries)} inserted")
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"Error processing upload {upload_id}: {str(e)}")
            logger.error(f"Full traceback: {error_details}")
            await self.db_service.update_upload_status(
                upload_id=upload_id,
                status=UploadStatus.FAILED,
                error_message=str(e)
            )