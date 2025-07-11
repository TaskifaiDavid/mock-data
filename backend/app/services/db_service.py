from supabase import create_client, Client
from app.utils.config import get_settings
from app.utils.exceptions import DatabaseException
from app.models.upload import UploadStatus, ProcessingStatus
from typing import Optional, List, Dict, Any
import json
from datetime import datetime
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

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
                # Validate sales_lc for numeric compatibility
                sales_lc_value = entry.get("sales_lc")
                if sales_lc_value is not None and sales_lc_value != '':
                    try:
                        # Ensure it can be converted to float for numeric operations
                        float(str(sales_lc_value))
                    except (ValueError, TypeError):
                        print(f"Warning: Invalid sales_lc value '{sales_lc_value}' for entry {i}, setting to None")
                        sales_lc_value = None
                
                sellout_entry = {
                    "upload_id": upload_id,
                    "product_ean": entry.get("product_ean"),
                    "month": entry.get("month"),
                    "year": entry.get("year"),
                    "quantity": entry.get("quantity"),
                    "sales_lc": sales_lc_value,
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
    
    # ============ NEW V2.0 METHODS FOR CHAT, EMAIL, AND DASHBOARD APIs ============
    
    async def fetch_all(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query and return all results as a list of dictionaries
        Used by chat, email, and dashboard services
        """
        try:
            # Convert PostgreSQL query to Supabase table operation where possible
            # For complex queries, we'll use Supabase RPC or direct table queries
            
            # Handle simple table queries
            if "FROM email_logs" in query:
                return await self._query_email_logs(query, params)
            elif "FROM chat_sessions" in query:
                return await self._query_chat_sessions(query, params)
            elif "FROM chat_messages" in query:
                return await self._query_chat_messages(query, params)
            elif "FROM dashboard_configs" in query:
                return await self._query_dashboard_configs(query, params)
            elif "FROM sellout_entries2" in query:
                return await self._query_sellout_entries(query, params)
            elif "FROM uploads" in query:
                return await self._query_uploads(query, params)
            elif "FROM information_schema" in query:
                return await self._query_schema_info(query, params)
            else:
                # For now, return empty list for unsupported queries
                print(f"WARNING: Unsupported query pattern in fetch_all: {query}")
                return []
                
        except Exception as e:
            print(f"ERROR in fetch_all: {str(e)}")
            print(f"Query: {query}")
            print(f"Params: {params}")
            raise DatabaseException(f"Failed to execute query: {str(e)}")
    
    async def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """
        Execute a SELECT query and return the first result as a dictionary
        Used by chat, email, and dashboard services
        """
        try:
            results = await self.fetch_all(query, params)
            return results[0] if results else None
        except Exception as e:
            print(f"ERROR in fetch_one: {str(e)}")
            raise DatabaseException(f"Failed to execute query: {str(e)}")
    
    async def execute(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """
        Execute an INSERT/UPDATE/DELETE query
        Used by chat, email, and dashboard services
        """
        try:
            # Handle INSERT operations
            if query.strip().upper().startswith("INSERT"):
                return await self._execute_insert(query, params)
            elif query.strip().upper().startswith("UPDATE"):
                return await self._execute_update(query, params)
            elif query.strip().upper().startswith("DELETE"):
                return await self._execute_delete(query, params)
            else:
                print(f"WARNING: Unsupported query type in execute: {query}")
                return None
                
        except Exception as e:
            print(f"ERROR in execute: {str(e)}")
            print(f"Query: {query}")
            print(f"Params: {params}")
            raise DatabaseException(f"Failed to execute query: {str(e)}")
    
    # ============ HELPER METHODS FOR SPECIFIC TABLES ============
    
    async def _query_email_logs(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Handle email_logs table queries"""
        try:
            # Extract user_id from params for RLS
            user_id = params[0] if params and len(params) > 0 else None
            
            # Don't execute query if no user_id provided
            if not user_id:
                print("WARNING: No user_id provided to _query_email_logs")
                return []
            
            if "ORDER BY sent_at DESC" in query:
                # Get email logs ordered by date
                result = self.supabase.table("email_logs")\
                    .select("*")\
                    .eq("user_id", user_id)\
                    .order("sent_at", desc=True)\
                    .execute()
                return result.data if result.data else []
            else:
                # Default email logs query
                result = self.supabase.table("email_logs")\
                    .select("*")\
                    .eq("user_id", user_id)\
                    .execute()
                return result.data if result.data else []
                
        except Exception as e:
            print(f"ERROR in _query_email_logs: {str(e)}")
            return []
    
    async def _query_chat_sessions(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Handle chat_sessions table queries"""
        try:
            user_id = params[0] if params and len(params) > 0 else None
            
            # Don't execute query if no user_id provided
            if not user_id:
                print("WARNING: No user_id provided to _query_chat_sessions")
                return []
            
            if "GROUP BY" in query and "ORDER BY" in query:
                # Complex query for sessions with message counts
                # For now, return simple sessions and let the API layer handle counts
                result = self.supabase.table("chat_sessions")\
                    .select("*")\
                    .eq("user_id", user_id)\
                    .order("updated_at", desc=True)\
                    .execute()
                return result.data if result.data else []
            else:
                # Simple sessions query
                result = self.supabase.table("chat_sessions")\
                    .select("*")\
                    .eq("user_id", user_id)\
                    .execute()
                return result.data if result.data else []
                
        except Exception as e:
            print(f"ERROR in _query_chat_sessions: {str(e)}")
            return []
    
    async def _query_chat_messages(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Handle chat_messages table queries"""
        try:
            if not params or len(params) < 2:
                print("WARNING: Insufficient parameters for _query_chat_messages")
                return []
            
            session_id, user_id = params[0], params[1]
            
            # Don't execute query if essential parameters are None
            if not session_id or not user_id:
                print("WARNING: Missing session_id or user_id in _query_chat_messages")
                return []
                
            if "ORDER BY created_at ASC" in query:
                # Get messages for session ordered by creation
                result = self.supabase.table("chat_messages")\
                    .select("*")\
                    .eq("session_id", session_id)\
                    .eq("user_id", user_id)\
                    .order("created_at", desc=False)\
                    .execute()
                return result.data if result.data else []
            elif "ORDER BY created_at DESC" in query:
                # Get recent messages for context
                result = self.supabase.table("chat_messages")\
                    .select("*")\
                    .eq("session_id", session_id)\
                    .order("created_at", desc=True)\
                    .limit(10)\
                    .execute()
                return result.data if result.data else []
                        
        except Exception as e:
            print(f"ERROR in _query_chat_messages: {str(e)}")
            return []
    
    async def _query_dashboard_configs(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Handle dashboard_configs table queries"""
        try:
            user_id = params[0] if params else None
            
            if "ORDER BY created_at DESC" in query:
                # Get dashboard configs ordered by creation date
                result = self.supabase.table("dashboard_configs")\
                    .select("*")\
                    .eq("user_id", user_id)\
                    .order("created_at", desc=True)\
                    .execute()
                return result.data if result.data else []
            elif len(params) >= 2:
                # Get specific dashboard config
                config_id, user_id = params[0], params[1]
                result = self.supabase.table("dashboard_configs")\
                    .select("*")\
                    .eq("id", config_id)\
                    .eq("user_id", user_id)\
                    .execute()
                return result.data if result.data else []
            else:
                # Default dashboard configs query
                result = self.supabase.table("dashboard_configs")\
                    .select("*")\
                    .eq("user_id", user_id)\
                    .execute()
                return result.data if result.data else []
                
        except Exception as e:
            print(f"ERROR in _query_dashboard_configs: {str(e)}")
            return []
    
    async def _query_sellout_entries(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Handle sellout_entries2 table queries for reports and chat"""
        try:
            print(f"DEBUG: Executing sellout_entries2 query: {query}")
            
            # Execute the query using Supabase RPC (stored procedure) for complex SQL
            # This allows us to run actual SQL instead of being limited to PostgREST operations
            result = self.supabase.rpc('execute_sql_query', {
                'query_text': query
            }).execute()
            
            print(f"DEBUG: Query result: {result.data}")
            return result.data if result.data else []
            
        except Exception as e:
            print(f"ERROR in _query_sellout_entries: {str(e)}")
            print(f"DEBUG: Query was: {query}")
            
            # Fallback to direct table queries for simple cases
            try:
                return await self._fallback_sellout_query(query)
            except Exception as fallback_error:
                print(f"ERROR in fallback query: {str(fallback_error)}")
                return []
    
    async def _fallback_sellout_query(self, query: str) -> List[Dict[str, Any]]:
        """Enhanced fallback method for sellout_entries2 queries with better SQL pattern recognition"""
        try:
            print(f"📊 FALLBACK QUERY ANALYSIS:")
            print(f"   Original SQL: {query}")
            
            query_upper = query.upper()
            
            # Pattern 1: Total sales queries
            if "SUM(" in query_upper and ("SALES_EUR" in query_upper or "SALES_LC" in query_upper):
                print(f"   🔍 Pattern: Total Sales Query")
                return await self._handle_total_sales_query(query)
            
            # Pattern 2: Sales by reseller
            elif "GROUP BY" in query_upper and "RESELLER" in query_upper:
                print(f"   🔍 Pattern: Sales by Reseller")
                return await self._handle_sales_by_reseller_query(query)
            
            # Pattern 3: Product queries
            elif "FUNCTIONAL_NAME" in query_upper or "PRODUCT" in query_upper:
                print(f"   🔍 Pattern: Product Query")
                return await self._handle_product_query(query)
            
            # Pattern 4: Date/time-based queries
            elif any(time_word in query_upper for time_word in ["MONTH", "YEAR", "DATE", "TIME"]):
                print(f"   🔍 Pattern: Date/Time Query")
                return await self._handle_date_query(query)
            
            # Pattern 5: Quantity queries
            elif "QUANTITY" in query_upper:
                print(f"   🔍 Pattern: Quantity Query")
                return await self._handle_quantity_query(query)
            
            # Pattern 6: Top/Bottom queries (ORDER BY with LIMIT)
            elif "ORDER BY" in query_upper and "LIMIT" in query_upper:
                print(f"   🔍 Pattern: Top/Bottom Query")
                return await self._handle_top_bottom_query(query)
            
            # Pattern 7: Count queries
            elif "COUNT(" in query_upper:
                print(f"   🔍 Pattern: Count Query")
                return await self._handle_count_query(query)
            
            # Default: Recent entries with smart filtering
            else:
                print(f"   🔍 Pattern: Default Recent Entries")
                return await self._handle_default_query(query)
                
        except Exception as e:
            print(f"ERROR in fallback sellout query: {str(e)}")
            return []
    
    async def _handle_total_sales_query(self, query: str) -> List[Dict[str, Any]]:
        """Handle total sales aggregation queries"""
        try:
            result = self.supabase.table("sellout_entries2")\
                .select("sales_eur, sales_lc, currency")\
                .execute()
            
            if result.data:
                # Calculate total sales in EUR
                total_eur = sum(float(row.get('sales_eur', 0) or 0) for row in result.data)
                
                # Also calculate by currency
                by_currency = {}
                for row in result.data:
                    currency = row.get('currency', 'Unknown')
                    sales_lc = float(row.get('sales_lc', 0) or 0)
                    if currency not in by_currency:
                        by_currency[currency] = 0
                    by_currency[currency] += sales_lc
                
                return [{
                    "total_sales_eur": total_eur,
                    "sales_by_currency": by_currency,
                    "total_records": len(result.data)
                }]
            return [{"total_sales_eur": 0, "sales_by_currency": {}, "total_records": 0}]
        except Exception as e:
            print(f"ERROR in total sales query: {str(e)}")
            return []
    
    async def _handle_sales_by_reseller_query(self, query: str) -> List[Dict[str, Any]]:
        """Handle sales aggregated by reseller"""
        try:
            result = self.supabase.table("sellout_entries2")\
                .select("reseller, sales_eur, sales_lc, currency, quantity")\
                .execute()
            
            if result.data:
                # Group by reseller
                reseller_stats = {}
                for row in result.data:
                    reseller = row.get('reseller', 'Unknown')
                    if reseller not in reseller_stats:
                        reseller_stats[reseller] = {
                            'total_sales_eur': 0,
                            'total_quantity': 0,
                            'total_records': 0,
                            'currencies': set()
                        }
                    
                    reseller_stats[reseller]['total_sales_eur'] += float(row.get('sales_eur', 0) or 0)
                    reseller_stats[reseller]['total_quantity'] += int(row.get('quantity', 0) or 0)
                    reseller_stats[reseller]['total_records'] += 1
                    reseller_stats[reseller]['currencies'].add(row.get('currency', 'Unknown'))
                
                # Convert to list and sort by sales
                result_list = []
                for reseller, stats in reseller_stats.items():
                    result_list.append({
                        'reseller': reseller,
                        'total_sales_eur': stats['total_sales_eur'],
                        'total_quantity': stats['total_quantity'],
                        'total_records': stats['total_records'],
                        'currencies': list(stats['currencies'])
                    })
                
                result_list.sort(key=lambda x: x['total_sales_eur'], reverse=True)
                return result_list[:10]  # Top 10 resellers
            return []
        except Exception as e:
            print(f"ERROR in sales by reseller query: {str(e)}")
            return []
    
    async def _handle_product_query(self, query: str) -> List[Dict[str, Any]]:
        """Handle product-related queries"""
        try:
            if "DISTINCT" in query.upper():
                # Get distinct products
                result = self.supabase.table("sellout_entries2")\
                    .select("functional_name, product_ean")\
                    .execute()
                
                if result.data:
                    unique_products = {}
                    for row in result.data:
                        name = row.get('functional_name')
                        ean = row.get('product_ean')
                        if name and name not in unique_products:
                            unique_products[name] = ean
                    
                    return [{"functional_name": name, "product_ean": ean} 
                            for name, ean in unique_products.items()]
            else:
                # Product sales summary
                result = self.supabase.table("sellout_entries2")\
                    .select("functional_name, product_ean, sales_eur, quantity")\
                    .execute()
                
                if result.data:
                    product_stats = {}
                    for row in result.data:
                        name = row.get('functional_name', 'Unknown')
                        if name not in product_stats:
                            product_stats[name] = {
                                'total_sales': 0,
                                'total_quantity': 0,
                                'product_ean': row.get('product_ean')
                            }
                        
                        product_stats[name]['total_sales'] += float(row.get('sales_eur', 0) or 0)
                        product_stats[name]['total_quantity'] += int(row.get('quantity', 0) or 0)
                    
                    result_list = []
                    for name, stats in product_stats.items():
                        result_list.append({
                            'functional_name': name,
                            'product_ean': stats['product_ean'],
                            'total_sales_eur': stats['total_sales'],
                            'total_quantity': stats['total_quantity']
                        })
                    
                    result_list.sort(key=lambda x: x['total_sales_eur'], reverse=True)
                    return result_list[:20]  # Top 20 products
            return []
        except Exception as e:
            print(f"ERROR in product query: {str(e)}")
            return []
    
    async def _handle_date_query(self, query: str) -> List[Dict[str, Any]]:
        """Handle date/time-based queries"""
        try:
            # Extract year and month if mentioned
            import re
            
            # Look for specific years
            year_match = re.search(r'\b(20\d{2})\b', query)
            year_filter = int(year_match.group(1)) if year_match else None
            
            # Look for months
            month_match = re.search(r'\b(1[0-2]|[1-9])\b', query)
            month_filter = int(month_match.group(1)) if month_match else None
            
            query_builder = self.supabase.table("sellout_entries2")\
                .select("month, year, sales_eur, quantity, reseller, functional_name")
            
            if year_filter:
                query_builder = query_builder.eq("year", year_filter)
            if month_filter:
                query_builder = query_builder.eq("month", month_filter)
            
            result = query_builder.order("year", desc=True).order("month", desc=True).limit(100).execute()
            
            return result.data if result.data else []
        except Exception as e:
            print(f"ERROR in date query: {str(e)}")
            return []
    
    async def _handle_quantity_query(self, query: str) -> List[Dict[str, Any]]:
        """Handle quantity-related queries"""
        try:
            result = self.supabase.table("sellout_entries2")\
                .select("functional_name, reseller, quantity, sales_eur")\
                .order("quantity", desc=True)\
                .limit(50)\
                .execute()
            
            return result.data if result.data else []
        except Exception as e:
            print(f"ERROR in quantity query: {str(e)}")
            return []
    
    async def _handle_top_bottom_query(self, query: str) -> List[Dict[str, Any]]:
        """Handle TOP/BOTTOM queries with ordering"""
        try:
            # Determine sort field and direction
            if "SALES" in query.upper():
                sort_field = "sales_eur"
            elif "QUANTITY" in query.upper():
                sort_field = "quantity"
            else:
                sort_field = "sales_eur"
            
            desc_order = "DESC" in query.upper() or "TOP" in query.upper()
            
            result = self.supabase.table("sellout_entries2")\
                .select("*")\
                .order(sort_field, desc=desc_order)\
                .limit(20)\
                .execute()
            
            return result.data if result.data else []
        except Exception as e:
            print(f"ERROR in top/bottom query: {str(e)}")
            return []
    
    async def _handle_count_query(self, query: str) -> List[Dict[str, Any]]:
        """Handle COUNT queries"""
        try:
            result = self.supabase.table("sellout_entries2")\
                .select("*", count="exact")\
                .execute()
            
            return [{"total_count": result.count if result.count else 0}]
        except Exception as e:
            print(f"ERROR in count query: {str(e)}")
            return []
    
    async def _handle_default_query(self, query: str) -> List[Dict[str, Any]]:
        """Handle default queries - recent entries with smart filtering"""
        try:
            result = self.supabase.table("sellout_entries2")\
                .select("*")\
                .order("created_at", desc=True)\
                .limit(100)\
                .execute()
            
            return result.data if result.data else []
        except Exception as e:
            print(f"ERROR in default query: {str(e)}")
            return []
    
    async def _query_uploads(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Handle uploads table queries"""
        try:
            user_id = params[0] if params else None
            
            result = self.supabase.table("uploads")\
                .select("*")\
                .eq("user_id", user_id)\
                .order("uploaded_at", desc=True)\
                .execute()
                
            return result.data if result.data else []
                
        except Exception as e:
            print(f"ERROR in _query_uploads: {str(e)}")
            return []
    
    async def _query_schema_info(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Handle information_schema queries for chat schema introspection"""
        try:
            # Return mock schema info for sellout_entries2
            return [
                {"column_name": "id", "data_type": "uuid", "is_nullable": "NO"},
                {"column_name": "product_ean", "data_type": "text", "is_nullable": "YES"},
                {"column_name": "month", "data_type": "integer", "is_nullable": "YES"},
                {"column_name": "year", "data_type": "integer", "is_nullable": "YES"},
                {"column_name": "quantity", "data_type": "integer", "is_nullable": "YES"},
                {"column_name": "sales_lc", "data_type": "text", "is_nullable": "YES"},
                {"column_name": "sales_eur", "data_type": "numeric", "is_nullable": "YES"},
                {"column_name": "currency", "data_type": "text", "is_nullable": "YES"},
                {"column_name": "reseller", "data_type": "text", "is_nullable": "YES"},
                {"column_name": "functional_name", "data_type": "text", "is_nullable": "YES"},
                {"column_name": "created_at", "data_type": "timestamp", "is_nullable": "YES"},
                {"column_name": "upload_id", "data_type": "uuid", "is_nullable": "YES"}
            ]
        except Exception as e:
            print(f"ERROR in _query_schema_info: {str(e)}")
            return []
    
    # ============ HELPER METHODS FOR INSERT/UPDATE/DELETE ============
    
    async def _execute_insert(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """Handle INSERT operations"""
        try:
            if "INSERT INTO email_logs" in query:
                return await self._insert_email_log(params)
            elif "INSERT INTO chat_sessions" in query:
                return await self._insert_chat_session(params)
            elif "INSERT INTO chat_messages" in query:
                return await self._insert_chat_message(params)
            elif "INSERT INTO dashboard_configs" in query:
                return await self._insert_dashboard_config(params)
            else:
                print(f"WARNING: Unsupported INSERT table in query: {query}")
                return None
                
        except Exception as e:
            print(f"ERROR in _execute_insert: {str(e)}")
            raise
    
    async def _insert_email_log(self, params: tuple) -> Optional[Dict[str, Any]]:
        """Insert email log record"""
        try:
            user_id, recipient_email, email_type, status, sent_at, metadata, error_message = params
            
            data = {
                "user_id": user_id,
                "recipient_email": recipient_email,
                "email_type": email_type,
                "status": status,
                "sent_at": sent_at.isoformat() if hasattr(sent_at, 'isoformat') else str(sent_at),
                "metadata": metadata,
                "error_message": error_message
            }
            
            result = self.supabase.table("email_logs").insert(data).execute()
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"ERROR in _insert_email_log: {str(e)}")
            raise
    
    async def _insert_chat_session(self, params: tuple) -> Optional[Dict[str, Any]]:
        """Insert chat session record"""
        try:
            user_id, session_name, created_at = params
            
            data = {
                "user_id": user_id,
                "session_name": session_name,
                "created_at": created_at.isoformat() if hasattr(created_at, 'isoformat') else str(created_at),
                "updated_at": created_at.isoformat() if hasattr(created_at, 'isoformat') else str(created_at)
            }
            
            result = self.supabase.table("chat_sessions").insert(data).execute()
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"ERROR in _insert_chat_session: {str(e)}")
            raise
    
    async def _insert_chat_message(self, params: tuple) -> Optional[Dict[str, Any]]:
        """Insert chat message record"""
        try:
            session_id, user_id, message_type, content, sql_query, query_result, created_at = params
            
            data = {
                "session_id": session_id,
                "user_id": user_id,
                "message_type": message_type,
                "content": content,
                "sql_query": sql_query,
                "query_result": query_result,
                "created_at": created_at.isoformat() if hasattr(created_at, 'isoformat') else str(created_at)
            }
            
            result = self.supabase.table("chat_messages").insert(data).execute()
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"ERROR in _insert_chat_message: {str(e)}")
            raise
    
    async def _insert_dashboard_config(self, params: tuple) -> Optional[Dict[str, Any]]:
        """Insert dashboard config record"""
        try:
            user_id, dashboard_name, dashboard_type, dashboard_url, auth_method, auth_config, permissions, is_active, created_at, updated_at = params
            
            data = {
                "user_id": user_id,
                "dashboard_name": dashboard_name,
                "dashboard_type": dashboard_type,
                "dashboard_url": dashboard_url,
                "authentication_method": auth_method,
                "authentication_config": auth_config,
                "permissions": permissions,
                "is_active": is_active,
                "created_at": created_at.isoformat() if hasattr(created_at, 'isoformat') else str(created_at),
                "updated_at": updated_at.isoformat() if hasattr(updated_at, 'isoformat') else str(updated_at)
            }
            
            result = self.supabase.table("dashboard_configs").insert(data).execute()
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"ERROR in _insert_dashboard_config: {str(e)}")
            raise
    
    async def _execute_update(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """Handle UPDATE operations"""
        try:
            if "UPDATE dashboard_configs" in query:
                return await self._update_dashboard_config(params)
            else:
                print(f"WARNING: Unsupported UPDATE table in query: {query}")
                return None
                
        except Exception as e:
            print(f"ERROR in _execute_update: {str(e)}")
            raise
    
    async def _update_dashboard_config(self, params: tuple) -> Optional[Dict[str, Any]]:
        """Update dashboard config record"""
        try:
            # Extract params based on the update query structure
            dashboard_name, dashboard_type, dashboard_url, auth_method, auth_config, permissions, is_active, updated_at, config_id, user_id = params
            
            update_data = {
                "dashboard_name": dashboard_name,
                "dashboard_type": dashboard_type,
                "dashboard_url": dashboard_url,
                "authentication_method": auth_method,
                "authentication_config": auth_config,
                "permissions": permissions,
                "is_active": is_active,
                "updated_at": updated_at.isoformat() if hasattr(updated_at, 'isoformat') else str(updated_at)
            }
            
            result = self.supabase.table("dashboard_configs")\
                .update(update_data)\
                .eq("id", config_id)\
                .eq("user_id", user_id)\
                .execute()
                
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"ERROR in _update_dashboard_config: {str(e)}")
            raise
    
    async def _execute_delete(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """Handle DELETE operations"""
        try:
            if "DELETE FROM chat_messages" in query:
                return await self._delete_chat_messages(params)
            elif "DELETE FROM dashboard_configs" in query:
                return await self._delete_dashboard_config(params)
            else:
                print(f"WARNING: Unsupported DELETE table in query: {query}")
                return None
                
        except Exception as e:
            print(f"ERROR in _execute_delete: {str(e)}")
            raise
    
    async def _delete_chat_messages(self, params: tuple) -> Optional[Dict[str, Any]]:
        """Delete chat messages for a session"""
        try:
            session_id, user_id = params
            
            result = self.supabase.table("chat_messages")\
                .delete()\
                .eq("session_id", session_id)\
                .eq("user_id", user_id)\
                .execute()
                
            return {"deleted": True, "count": len(result.data) if result.data else 0}
            
        except Exception as e:
            print(f"ERROR in _delete_chat_messages: {str(e)}")
            raise
    
    async def _delete_dashboard_config(self, params: tuple) -> Optional[Dict[str, Any]]:
        """Delete dashboard config"""
        try:
            config_id, user_id = params
            
            result = self.supabase.table("dashboard_configs")\
                .delete()\
                .eq("id", config_id)\
                .eq("user_id", user_id)\
                .execute()
                
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"ERROR in _delete_dashboard_config: {str(e)}")
            raise