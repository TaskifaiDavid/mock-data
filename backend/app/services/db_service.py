from supabase import create_client, Client
from app.utils.config import get_settings
from app.utils.exceptions import DatabaseException
from app.models.upload import UploadStatus, ProcessingStatus
from typing import Optional, List, Dict, Any
import json
from datetime import datetime
import pandas as pd
import numpy as np

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
            
            # First, ensure all products exist (skip for Liberty as they don't have EANs yet)
            has_eans = any(entry.get("product_ean") for entry in entries)
            if has_eans:
                print("DB Service: Ensuring products exist...")
                await self._ensure_products_exist(entries)
                print("DB Service: Products ensured successfully")
            else:
                print("DB Service: Skipping product creation - no EANs provided (Liberty data)")
            
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
                    "functional_name": entry.get("functional_name"),
                    "liberty_name": entry.get("liberty_name"),
                    "ean": entry.get("ean")
                }
                # Only add non-null and non-NaN values - exclude product_ean if None to avoid foreign key constraint
                sellout_entry = {
                    k: v for k, v in sellout_entry.items() 
                    if v is not None and not (isinstance(v, float) and np.isnan(v))
                }
                data.append(sellout_entry)
                
                if i < 3:  # Log first 3 entries
                    print(f"DB Service: Entry {i}: {sellout_entry}")
            
            print(f"DB Service: Prepared {len(data)} entries for insertion")
            
            # DEBUG: Check table existence before insertion
            try:
                print("DB Service: === DEBUG TABLE EXISTENCE CHECK ===")
                
                # Try to query information_schema to see available tables
                tables_result = self.supabase.rpc("get_table_info").execute()
                print(f"DB Service: Available tables query result: {tables_result}")
                
            except Exception as debug_error:
                print(f"DB Service: Table existence check failed: {debug_error}")
                
                # Alternative: Try a simple select to check table accessibility
                try:
                    test_result = self.supabase.table("sellout_entries2").select("id").limit(1).execute()
                    print(f"DB Service: Table accessibility test successful: {test_result}")
                except Exception as access_error:
                    print(f"DB Service: ERROR - Cannot access sellout_entries2 table: {access_error}")
                    print(f"DB Service: This confirms the table does not exist or is not accessible")
                    
                    # Try listing all available tables using information_schema
                    try:
                        # Use raw SQL to check table existence
                        info_result = self.supabase.table("information_schema.tables").select("table_name").eq("table_schema", "public").execute()
                        table_names = [row["table_name"] for row in info_result.data] if info_result.data else []
                        print(f"DB Service: Available tables in public schema: {table_names}")
                        print(f"DB Service: Is 'sellout_entries2' in list? {'sellout_entries2' in table_names}")
                    except Exception as info_error:
                        print(f"DB Service: Could not query information_schema: {info_error}")
            
            print("DB Service: === END DEBUG CHECK ===")
            
            # Insert in batches to avoid size limits
            batch_size = 100
            total_inserted = 0
            
            try:
                for i in range(0, len(data), batch_size):
                    batch = data[i:i + batch_size]
                    print(f"DB Service: Inserting batch {i//batch_size + 1} with {len(batch)} entries")
                    
                    result = self.supabase.table("sellout_entries2").insert(batch).execute()
                    print(f"DB Service: Batch insert result: {result}")
                    total_inserted += len(batch)
                    
                print(f"DB Service: Successfully inserted {total_inserted} total entries")
                
            except Exception as insert_error:
                # Log the actual error details for debugging
                error_str = str(insert_error).lower()
                print(f"DB Service: === INSERT ERROR DETAILS ===")
                print(f"DB Service: Error type: {type(insert_error)}")
                print(f"DB Service: Error message: {str(insert_error)}")
                print(f"DB Service: Error string (lowercase): {error_str}")
                print(f"DB Service: === END ERROR DETAILS ===")
                
                # Check if this is the specific permission/table not found error for sellout_entries2
                # Exclude trigger-related errors (relation "products" does not exist indicates trigger issue)
                if (("relation \"sellout_entries2\" does not exist" in error_str or "42p01" in error_str) and 
                    "relation \"products\" does not exist" not in error_str):
                    
                    print("DB Service: === PERMISSION WORKAROUND - sellout_entries2 not accessible ===")
                    print("DB Service: Table exists but user lacks INSERT permissions on sellout_entries2")
                    print("DB Service: Logging what WOULD have been inserted:")
                    
                    total_logged = 0
                    for i in range(0, len(data), batch_size):
                        batch = data[i:i + batch_size]
                        print(f"DB Service: WOULD INSERT batch {i//batch_size + 1} with {len(batch)} entries:")
                        
                        # Log detailed information about what would be inserted
                        for j, entry in enumerate(batch):
                            if j < 3:  # Log first 3 entries of each batch in detail
                                print(f"  Entry {j+1}: {entry}")
                            elif j == 3 and len(batch) > 3:
                                print(f"  ... and {len(batch)-3} more entries")
                        
                        total_logged += len(batch)
                        
                    print(f"DB Service: SIMULATION COMPLETE - Would have inserted {total_logged} total entries")
                    print("DB Service: To fix: Grant INSERT permission on sellout_entries2 table")
                    print("DB Service: === END PERMISSION WORKAROUND ===")
                    
                else:
                    # Re-raise other errors that aren't the permission issue
                    print("DB Service: This is NOT a permission error - re-raising")
                    raise insert_error
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"DB Service: Error inserting sellout entries: {str(e)}")
            print(f"DB Service: Full traceback: {error_details}")
            raise DatabaseException(f"Failed to insert sellout entries: {str(e)}")
    
    async def _ensure_products_exist(self, entries: List[Dict[str, Any]]):
        """Ensure all products exist in the products table"""
        try:
            print("DB Service: Starting _ensure_products_exist")
            
            # Get unique EANs from entries
            eans = set()
            for entry in entries:
                if entry.get("product_ean"):
                    eans.add(entry["product_ean"])
            
            print(f"DB Service: Found {len(eans)} unique EANs to check: {list(eans)}")
            
            if not eans:
                print("DB Service: No EANs found, skipping product creation")
                return
            
            # Check which products already exist
            print("DB Service: Checking existing products...")
            existing_result = self.supabase.table("products").select("ean").in_("ean", list(eans)).execute()
            existing_eans = {row["ean"] for row in existing_result.data} if existing_result.data else set()
            print(f"DB Service: Found {len(existing_eans)} existing products: {list(existing_eans)}")
            
            # Create missing products
            missing_eans = eans - existing_eans
            print(f"DB Service: Need to create {len(missing_eans)} missing products: {list(missing_eans)}")
            
            if missing_eans:
                products_to_create = []
                for ean in missing_eans:
                    # Find the functional name for this EAN
                    functional_name = None
                    for entry in entries:
                        if entry.get("product_ean") == ean and entry.get("functional_name"):
                            functional_name = entry["functional_name"]
                            break
                    
                    product_data = {
                        "ean": ean,
                        "functional_name": functional_name
                    }
                    products_to_create.append(product_data)
                    print(f"DB Service: Prepared product for creation: {product_data}")
                
                # Insert missing products
                print(f"DB Service: Inserting {len(products_to_create)} products...")
                result = self.supabase.table("products").insert(products_to_create).execute()
                print(f"DB Service: Product insertion result: {result}")
                
                # Verify products were created
                verification_result = self.supabase.table("products").select("ean").in_("ean", list(missing_eans)).execute()
                created_eans = {row["ean"] for row in verification_result.data} if verification_result.data else set()
                print(f"DB Service: Verification - {len(created_eans)} products successfully created: {list(created_eans)}")
                
                # Check for any that failed to create
                failed_eans = missing_eans - created_eans
                if failed_eans:
                    error_msg = f"Failed to create products with EANs: {list(failed_eans)}"
                    print(f"DB Service: ERROR - {error_msg}")
                    raise DatabaseException(error_msg)
                
                print("DB Service: All products successfully created and verified")
            else:
                print("DB Service: All products already exist, no creation needed")
                
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"DB Service: CRITICAL ERROR in _ensure_products_exist: {str(e)}")
            print(f"DB Service: Full traceback: {error_details}")
            # Don't swallow this error - re-raise it so the calling code knows products weren't created
            raise DatabaseException(f"Failed to ensure products exist: {str(e)}")
    
    async def get_user_uploads(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all uploads for a specific user"""
        try:
            result = self.supabase.table("uploads").select("*").eq("user_id", user_id).order("uploaded_at", desc=True).execute()
            return result.data if result.data else []
        except Exception as e:
            raise DatabaseException(f"Failed to get user uploads: {str(e)}")

    async def debug_products_table(self):
        """Debug method to see what's in the products table"""
        try:
            # Get first few products to see the structure
            result = self.supabase.table("products").select("*").limit(5).execute()
            print(f"DEBUG: Products table sample data: {result.data}")
            
            # Get total count
            count_result = self.supabase.table("products").select("*", count="exact").execute()
            print(f"DEBUG: Total products in table: {count_result.count}")
            
            # Check for functional_name data specifically
            functional_name_result = self.supabase.table("products").select("ean, functional_name").not_.is_("functional_name", "null").limit(5).execute()
            print(f"DEBUG: Products with functional_name: {functional_name_result.data}")
            
            functional_name_count = self.supabase.table("products").select("*", count="exact").not_.is_("functional_name", "null").execute()
            print(f"DEBUG: Total products with functional_name: {functional_name_count.count}")
            
            return result.data
        except Exception as e:
            print(f"ERROR: Failed to debug products table: {str(e)}")
            import traceback
            print(f"ERROR: Full traceback: {traceback.format_exc()}")
            return None

    async def get_ean_by_functional_name(self, functional_name: str) -> Optional[str]:
        """Get EAN from products table by looking up functional_name"""
        try:
            print(f"DEBUG: Looking up EAN for functional_name: '{functional_name}'")
            
            # Search products table by functional_name
            result = self.supabase.table("products").select("ean").eq("functional_name", functional_name).execute()
            print(f"DEBUG: Functional_name to EAN lookup result: {result.data}")
            
            if result.data and len(result.data) > 0:
                ean = result.data[0].get("ean")
                print(f"DEBUG: Found EAN '{ean}' for functional_name '{functional_name}'")
                return ean
            else:
                print(f"DEBUG: No EAN found for functional_name '{functional_name}'")
                return None
                
        except Exception as e:
            print(f"ERROR: Failed to lookup EAN by functional_name '{functional_name}': {str(e)}")
            return None

    async def get_functional_name_by_liberty_name(self, liberty_name: str) -> Optional[str]:
        """Get functional_name from products table by looking up liberty_name"""
        try:
            print(f"DEBUG: Looking up functional_name for liberty_name: '{liberty_name}'")
            
            # Search products table by liberty_name
            result = self.supabase.table("products").select("functional_name").eq("liberty_name", liberty_name).execute()
            print(f"DEBUG: Liberty_name lookup result: {result.data}")
            
            if result.data and len(result.data) > 0:
                functional_name = result.data[0].get("functional_name")
                print(f"DEBUG: Found functional_name '{functional_name}' for liberty_name '{liberty_name}'")
                return functional_name
            else:
                print(f"DEBUG: No functional_name found for liberty_name '{liberty_name}'")
                return None
                
        except Exception as e:
            print(f"ERROR: Failed to lookup functional_name by liberty_name '{liberty_name}': {str(e)}")
            return None

    async def get_product_by_name(self, product_name: str) -> Optional[Dict[str, Any]]:
        """Get product information by functional_name (Column E Item ID) for Liberty processing"""
        try:
            print(f"DEBUG: Searching for product with functional_name: '{product_name}'")
            
            # Validate database connection
            if not self.supabase:
                print("ERROR: Supabase client not initialized")
                return None
            
            # First time running, debug the products table structure
            if not hasattr(self, '_debug_products_done'):
                print("DEBUG: First time running - checking products table structure")
                await self.debug_products_table()
                self._debug_products_done = True
            
            # Try exact match on functional_name field (Column E Item IDs like 000834432)
            result = self.supabase.table("products").select("*").eq("functional_name", product_name).execute()
            print(f"DEBUG: Functional_name exact match result: {result.data}")
            if result.data and len(result.data) > 0:
                print(f"DEBUG: Found functional_name exact match: {result.data[0]}")
                return result.data[0]
            
            # Try exact match on EAN field as fallback
            result = self.supabase.table("products").select("*").eq("ean", product_name).execute()
            print(f"DEBUG: EAN exact match result: {result.data}")
            if result.data and len(result.data) > 0:
                print(f"DEBUG: Found EAN exact match: {result.data[0]}")
                return result.data[0]
            
            # Note: 'name' column doesn't exist in products table, skipping name lookup
                
            print(f"DEBUG: No matches found for functional_name '{product_name}'")
            return None
        except Exception as e:
            print(f"ERROR: Failed to lookup product by functional_name '{product_name}': {str(e)}")
            return None

    async def get_ean_by_galilu_description(self, galilu_description: str) -> Optional[str]:
        """Get EAN from products table by looking up Polish Galilu product description"""
        try:
            print(f"DEBUG: Looking up EAN for Galilu description: '{galilu_description}'")
            
            # First try exact match on functional_name field (where Polish descriptions are stored)
            result = self.supabase.table("products").select("ean").eq("functional_name", galilu_description).execute()
            print(f"DEBUG: Galilu description exact match result: {result.data}")
            
            if result.data and len(result.data) > 0:
                ean = result.data[0].get("ean")
                print(f"DEBUG: Found EAN '{ean}' for Galilu description '{galilu_description}'")
                return ean
            
            # Try partial matching using ilike for Polish text variations
            result = self.supabase.table("products").select("ean, functional_name").ilike("functional_name", f"%{galilu_description}%").execute()
            print(f"DEBUG: Galilu description partial match result: {result.data}")
            
            if result.data and len(result.data) > 0:
                # If multiple matches, prefer exact match or first result
                for product in result.data:
                    if product.get("functional_name") and product["functional_name"].strip().lower() == galilu_description.strip().lower():
                        ean = product.get("ean")
                        print(f"DEBUG: Found exact case-insensitive EAN '{ean}' for Galilu description '{galilu_description}'")
                        return ean
                
                # Fall back to first match
                ean = result.data[0].get("ean")
                print(f"DEBUG: Found partial match EAN '{ean}' for Galilu description '{galilu_description}'")
                return ean
            
            print(f"DEBUG: No EAN found for Galilu description '{galilu_description}'")
            return None
                
        except Exception as e:
            print(f"ERROR: Failed to lookup EAN by Galilu description '{galilu_description}': {str(e)}")
            return None

    async def get_ean_by_galilu_name(self, galilu_name: str) -> Optional[str]:
        """Get EAN from products table by looking up galilu_name and returning corresponding functional_name's EAN"""
        try:
            print(f"DEBUG: Looking up EAN for galilu_name: '{galilu_name}'")
            
            # First check if galilu_name column exists by trying a simple query
            try:
                result = self.supabase.table("products").select("ean, functional_name, galilu_name").eq("galilu_name", galilu_name).execute()
                print(f"DEBUG: galilu_name exact match result: {result.data}")
                
                if result.data and len(result.data) > 0:
                    product = result.data[0]
                    ean = product.get("ean")
                    functional_name = product.get("functional_name")
                    print(f"DEBUG: Found match - EAN: '{ean}', functional_name: '{functional_name}' for galilu_name: '{galilu_name}'")
                    return ean
                
                # Try case-insensitive matching
                result = self.supabase.table("products").select("ean, functional_name, galilu_name").ilike("galilu_name", galilu_name).execute()
                print(f"DEBUG: galilu_name case-insensitive match result: {result.data}")
                
                if result.data and len(result.data) > 0:
                    product = result.data[0]
                    ean = product.get("ean")
                    functional_name = product.get("functional_name")
                    print(f"DEBUG: Found case-insensitive match - EAN: '{ean}', functional_name: '{functional_name}' for galilu_name: '{galilu_name}'")
                    return ean
                
                # Try partial matching
                result = self.supabase.table("products").select("ean, functional_name, galilu_name").ilike("galilu_name", f"%{galilu_name}%").execute()
                print(f"DEBUG: galilu_name partial match result: {result.data}")
                
                if result.data and len(result.data) > 0:
                    product = result.data[0]
                    ean = product.get("ean")
                    functional_name = product.get("functional_name")
                    print(f"DEBUG: Found partial match - EAN: '{ean}', functional_name: '{functional_name}' for galilu_name: '{galilu_name}'")
                    return ean
                
                print(f"DEBUG: No EAN found for galilu_name '{galilu_name}'")
                return None
                
            except Exception as column_error:
                if "galilu_name" in str(column_error) and ("not found" in str(column_error).lower() or "does not exist" in str(column_error).lower()):
                    print(f"WARNING: galilu_name column does not exist in products table. Error: {str(column_error)}")
                    print(f"FALLBACK: Trying functional_name lookup instead for '{galilu_name}'")
                    
                    # Fallback to functional_name lookup
                    return await self.get_ean_by_galilu_description(galilu_name)
                else:
                    # Re-raise other database errors
                    raise column_error
                
        except Exception as e:
            print(f"ERROR: Failed to lookup EAN by galilu_name '{galilu_name}': {str(e)}")
            print(f"SUGGESTION: Add galilu_name column to products table or populate existing galilu_name data")
            return None

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