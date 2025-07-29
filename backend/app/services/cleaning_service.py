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
            excel_file = pd.ExcelFile(io.BytesIO(file_contents), engine='openpyxl')
            logger.info(f"Excel file sheet names: {excel_file.sheet_names}")
            
            # First, detect vendor from filename and sheet names to determine correct sheet
            vendor = self.vendor_detector.detect_vendor(filename, excel_file)
            logger.info(f"Detected vendor from filename and sheet names: {vendor}")
            logger.info(f"Available sheets: {excel_file.sheet_names}")
            
            # Select appropriate sheet based on vendor
            sheet_name = excel_file.sheet_names[0]  # Default to first sheet
            logger.info(f"Default sheet selection: '{sheet_name}' (first sheet)")
            
            # For Skins NL, try to find SalesPerSKU sheet if available
            if vendor == "skins_nl":
                logger.info("Processing Skins NL - looking for SalesPerSKU sheet")
                matching_sheets = [name for name in excel_file.sheet_names if "salespersku" in name.lower()]
                logger.info(f"SalesPerSKU matching sheets: {matching_sheets}")
                if matching_sheets:
                    sheet_name = matching_sheets[0]
                    logger.info(f"Found SalesPerSKU sheet for Skins NL: {sheet_name}")
                else:
                    logger.info(f"No SalesPerSKU sheet found, using default: {sheet_name}")
            
            # For BOXNOX, try to find "SELL OUT BY EAN" sheet if available
            elif vendor == "boxnox":
                logger.info("Processing BOXNOX - looking for 'SELL OUT BY EAN' sheet")
                matching_sheets = [name for name in excel_file.sheet_names if "sell out by ean" in name.lower()]
                logger.info(f"SELL OUT BY EAN matching sheets: {matching_sheets}")
                if matching_sheets:
                    sheet_name = matching_sheets[0]
                    logger.info(f"Found 'SELL OUT BY EAN' sheet for BOXNOX: {sheet_name}")
                else:
                    logger.info(f"No 'SELL OUT BY EAN' sheet found, using default: {sheet_name}")
            
            # For Aromateque, use TDSheet
            elif vendor == "aromateque":
                logger.info("Processing Aromateque - looking for TDSheet")
                matching_sheets = [name for name in excel_file.sheet_names if "tdsheet" in name.lower()]
                logger.info(f"TDSheet matching sheets: {matching_sheets}")
                if matching_sheets:
                    sheet_name = matching_sheets[0]
                    logger.info(f"Found 'TDSheet' sheet for Aromateque: {sheet_name}")
                else:
                    logger.info(f"No TDSheet found, using default: {sheet_name}")
            
            # For Galilu, try to find "product_ranking_2025" sheet if available
            elif vendor == "galilu":
                logger.info("Processing Galilu - looking for 'product_ranking_2025' sheet")
                logger.info(f"Checking each sheet for Galilu pattern:")
                for i, name in enumerate(excel_file.sheet_names):
                    logger.info(f"  Sheet {i}: '{name}' - contains 'product_ranking_2025'? {'product_ranking_2025' in name.lower()}")
                
                matching_sheets = [name for name in excel_file.sheet_names if "product_ranking_2025" in name.lower()]
                logger.info(f"Galilu product_ranking_2025 matching sheets: {matching_sheets}")
                
                if matching_sheets:
                    sheet_name = matching_sheets[0]
                    logger.info(f"✅ Found 'product_ranking_2025' sheet for Galilu: '{sheet_name}'")
                else:
                    logger.warning(f"⚠️ No 'product_ranking_2025' sheet found for Galilu, using default: '{sheet_name}'")
                    # Try alternative patterns
                    alt_patterns = ["product_ranking", "ranking_2025", "product ranking"]
                    for pattern in alt_patterns:
                        alt_matching = [name for name in excel_file.sheet_names if pattern in name.lower()]
                        if alt_matching:
                            sheet_name = alt_matching[0]
                            logger.info(f"🔄 Found alternative Galilu sheet with pattern '{pattern}': '{sheet_name}'")
                            break
                    else:
                        logger.warning(f"🚨 No alternative Galilu sheet patterns found, proceeding with default: '{sheet_name}'")
            
            # For Aromateque, read as text to prevent date auto-conversion
            if vendor == "aromateque":
                df = pd.read_excel(excel_file, sheet_name=sheet_name, dtype=str, header=None)
                logger.info(f"Read Aromateque file as text to preserve Ukrainian headers")
            else:
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
            
            # Vendor already detected above
            logger.info(f"Using vendor: {vendor}")
            logger.info(f"Vendor detection details - filename: '{filename}', sheet_names: {excel_file.sheet_names}")
            
            # Clean data
            logger.info(f"Starting data cleaning for vendor '{vendor}' with {len(df)} rows")
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
            logger.info(f"Starting data normalization for vendor '{vendor}' with {len(cleaned_df)} cleaned rows")
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
                logger.info(f"Attempting to insert {len(sellout_entries)} entries into mock_data")
                await self.db_service.insert_mock_data(upload_id, sellout_entries)
                logger.info(f"Successfully inserted {len(sellout_entries)} entries into mock_data")
                
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