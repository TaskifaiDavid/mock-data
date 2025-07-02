import pandas as pd
import numpy as np
from typing import Tuple, List, Dict, Any
import re
from datetime import datetime, timedelta

class DataCleaner:
    def __init__(self, db_service=None):
        self.current_filename = None
        self.db_service = db_service
    
    async def clean_data(self, df: pd.DataFrame, vendor: str, filename: str = None) -> Tuple[pd.DataFrame, List[Dict[str, Any]]]:
        """Clean data based on vendor-specific rules"""
        
        self.current_filename = filename
        df_clean = df.copy()
        transformations = []
        
        # Remove empty rows
        df_clean = df_clean.dropna(how='all')
        
        # Apply vendor-specific cleaning
        if vendor == "galilu":
            df_clean, trans = await self._clean_galilu_data(df_clean)
        elif vendor == "boxnox":
            df_clean, trans = await self._clean_boxnox_data(df_clean)
        elif vendor == "skins_sa":
            df_clean, trans = await self._clean_skins_sa_data(df_clean)
        elif vendor == "cdlc":
            df_clean, trans = await self._clean_cdlc_data(df_clean)
        elif vendor == "continuity":
            df_clean, trans = await self._clean_continuity_data(df_clean)
        elif vendor == "liberty":
            df_clean, trans = await self._clean_liberty_data(df_clean)
        elif vendor == "ukraine":
            df_clean, trans = await self._clean_ukraine_data(df_clean)
        else:
            df_clean, trans = await self._clean_generic_data(df_clean)
        
        transformations.extend(trans)
        
        # Common cleaning for all vendors
        df_clean, common_trans = await self._apply_common_cleaning(df_clean)
        transformations.extend(common_trans)
        
        return df_clean, transformations
    
    async def _clean_galilu_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict]]:
        transformations = []
        
        # Skip rows with TOTAL
        mask = ~df.iloc[:, 0].str.contains('TOTAL', case=False, na=False)
        df = df[mask]
        
        # Unpivot monthly data
        if len(df.columns) > 12:
            # First column is store, rest are months
            id_vars = [df.columns[0]]
            value_vars = [col for col in df.columns[1:] if any(month in str(col).lower() for month in ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'])]
            
            if value_vars:
                df = pd.melt(df, id_vars=id_vars, value_vars=value_vars, var_name='month', value_name='quantity')
        
        return df, transformations
    
    async def _clean_boxnox_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict]]:
        transformations = []
        
        # Column mapping for Boxnox
        column_mapping = {
            'YEAR': 'report_year',
            'MONTH': 'report_month',
            'CHANNEL': 'channel',
            'POS': 'store',
            'EAN': 'ean',
            'QTY': 'quantity',
            'AMOUNT': 'gross_value',
            'SKU': 'sku'
        }
        
        # Rename columns
        df.rename(columns=column_mapping, inplace=True)
        
        return df, transformations
    
    async def _clean_skins_sa_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict]]:
        transformations = []
        
        # Column mapping for Skins SA
        column_mapping = {
            'OrderDate': 'order_date',
            'Branch': 'store',
            'StockCode': 'ean',
            'OrderQty': 'quantity',
            'NetSalesValue': 'net_value',
            'ExVatNetsales': 'net_value',
            'MONTH': 'report_month',
            'YEAR': 'report_year'
        }
        
        df.rename(columns=column_mapping, inplace=True)
        
        return df, transformations
    
    async def _clean_cdlc_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict]]:
        transformations = []
        
        # Skip first 2 rows if header is at row 3
        if len(df) > 3:
            df = df.iloc[2:].reset_index(drop=True)
            df.columns = df.iloc[0]
            df = df[1:]
        
        return df, transformations
    
    async def _clean_continuity_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict]]:
        transformations = []
        
        # Skip first 2 rows if header is at row 3 (per PRD section 9.3)
        if len(df) > 3:
            df = df.iloc[2:].reset_index(drop=True)
            # Check if first row contains headers
            if df.iloc[0].str.contains('Item|Reference|Sales', case=False, na=False).any():
                df.columns = df.iloc[0]
                df = df[1:].reset_index(drop=True)
        
        # Column mapping for Continuity per PRD section 9
        column_mapping = {
            'Item': 'product_name',
            'Supplier Reference': 'sku',
            'Sales Qty Un': 'quantity',
            'Sales Inc VAT £': 'gross_value'
        }
        
        df.rename(columns=column_mapping, inplace=True)
        
        # Extract year and month from data or set defaults
        # For Continuity, we need to extract from filename or use current date
        current_year = 2025  # Default from test data
        current_month = 6    # Default from test data filename
        
        df['report_year'] = current_year
        df['report_month'] = current_month
        
        transformations.append({
            "row_index": 0,
            "column_name": "report_year",
            "original_value": None,
            "cleaned_value": current_year,
            "transformation_type": "default_date_assignment"
        })
        
        transformations.append({
            "row_index": 0,
            "column_name": "report_month",
            "original_value": None,
            "cleaned_value": current_month,
            "transformation_type": "default_date_assignment"
        })
        
        return df, transformations
    
    async def _clean_liberty_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict]]:
        transformations = []
        
        # Extract year and month from filename with -1 week logic
        year, month = self._extract_liberty_date_from_filename()
        
        # Read data by Excel column positions (per Liberty instructions)  
        # Column U (index 20) = quantity, Column V (index 21) = sales_lc, Column F (index 5) = product_name
        # Based on CSV analysis: "All Sales Channels" columns are at positions 20 and 21
        liberty_data = []
        
        # Debug: Print DataFrame info
        print(f"Debug: DataFrame shape: {df.shape}")
        print(f"Debug: Column count: {len(df.columns)}")
        if len(df) > 0:
            print(f"Debug: Sample row 0 length: {len(df.iloc[0])}")
            print(f"Debug: First few values in row 0: {df.iloc[0][:10].tolist()}")
        
        # Find rows with data (skip empty rows and total/summary rows)
        for idx, row in df.iterrows():
            # Check if we have data in the key columns (U, V, F are 0-based columns 20, 21, 5)
            if len(row) > 21:  # Make sure we have enough columns
                quantity = row.iloc[20] if len(row) > 20 else None  # Column U (0-based index 20)
                sales_lc = row.iloc[21] if len(row) > 21 else None   # Column V (0-based index 21)  
                raw_functional_name = row.iloc[5] if len(row) > 5 else None  # Column F - Complete product string (0-based index 5)
                
                # Use the complete string from Column F (like "000834429 | 98-NO COLOUR Total")
                functional_name = None
                if pd.notna(raw_functional_name) and str(raw_functional_name).strip():
                    functional_name = str(raw_functional_name).strip()
                    print(f"DEBUG: Extracted functional_name '{functional_name}' from Column F")
                else:
                    print(f"DEBUG: Empty/null functional_name from Column F: '{raw_functional_name}'")
                
                # Debug: Print first few rows to verify column mapping
                if idx < 10 and pd.notna(quantity):
                    print(f"Debug Row {idx}: quantity={quantity}, sales_lc={sales_lc}, functional_name={functional_name}")
                
                # Enhanced debug for rows with valid sales data
                if pd.notna(quantity) and pd.notna(sales_lc) and idx < 20:
                    print(f"SALES ROW {idx}: Column F (index 5) = '{functional_name}' | Full row values:")
                    print(f"  - Column 0-10: {[row.iloc[i] if i < len(row) else 'N/A' for i in range(11)]}")
                    print(f"  - Quantity (index 20): {quantity}")
                    print(f"  - Sales_lc (index 21): {sales_lc}")
                    print(f"  - Functional_name (index 5): {functional_name}")
                    print("---")
                
                # Skip total/summary rows - check if any column contains "total" or similar
                is_total_row = False
                for col_val in row:
                    if pd.notna(col_val) and isinstance(col_val, str):
                        col_val_lower = str(col_val).lower()
                        if any(word in col_val_lower for word in ['total', 'sum', 'grand total', 'subtotal']) or col_val_lower.endswith(' total'):
                            is_total_row = True
                            break
                
                # Log every row that has quantity and sales data to debug missing functional_name
                if pd.notna(quantity) and pd.notna(sales_lc):
                    print(f"ROW {idx} - Quantity: {quantity}, Sales: {sales_lc}, Column F: '{raw_functional_name}', Parsed: '{functional_name}', Is_Total: {is_total_row}")
                
                # Only include rows with valid quantity and sales data, excluding total rows
                # Include products with zero sales for completeness
                if not is_total_row and pd.notna(quantity) and pd.notna(sales_lc):
                    # If functional_name is nan, check the next row for the product string
                    final_functional_name = functional_name
                    
                    if pd.isna(functional_name):
                        print(f"DEBUG: Row {idx} has NULL functional_name, trying fallbacks...")
                        
                        # Try next row
                        if idx + 1 < len(df):
                            next_row = df.iloc[idx + 1]
                            next_functional_name = next_row.iloc[5] if len(next_row) > 5 else None  # Column F
                            next_quantity = next_row.iloc[20] if len(next_row) > 20 else None
                            next_sales_lc = next_row.iloc[21] if len(next_row) > 21 else None
                            
                            print(f"DEBUG: Next row {idx+1} - F: '{next_functional_name}', Qty: {next_quantity}, Sales: {next_sales_lc}")
                            
                            # If next row has same sales data and a valid functional_name, use it
                            if (pd.notna(next_functional_name) and 
                                next_quantity == quantity and 
                                next_sales_lc == sales_lc):
                                final_functional_name = str(next_functional_name).strip()
                                print(f"DEBUG: ✓ Found functional_name in next row {idx+1}: '{final_functional_name}'")
                        
                        # Try previous row if next row didn't work
                        if pd.isna(final_functional_name) and idx > 0:
                            prev_row = df.iloc[idx - 1]
                            prev_functional_name = prev_row.iloc[5] if len(prev_row) > 5 else None  # Column F
                            print(f"DEBUG: Previous row {idx-1} - F: '{prev_functional_name}'")
                            
                            if pd.notna(prev_functional_name):
                                final_functional_name = str(prev_functional_name).strip()
                                print(f"DEBUG: ✓ Using previous row functional_name: '{final_functional_name}'")
                        
                        # Fallback to Column E if still no functional_name
                        if pd.isna(final_functional_name):
                            item_id = row.iloc[4] if len(row) > 4 else None  # Column E
                            print(f"DEBUG: Column E fallback: '{item_id}'")
                            if pd.notna(item_id):
                                final_functional_name = str(item_id).strip()
                                print(f"DEBUG: ✓ Using Column E as fallback: '{final_functional_name}'")
                        
                        if pd.isna(final_functional_name):
                            print(f"DEBUG: ✗ No functional_name found for row {idx} after all fallbacks")
                    
                    liberty_data.append({
                        'quantity': quantity,
                        'sales_lc': sales_lc,
                        'functional_name': final_functional_name,
                        'original_row': idx
                    })
        
        # Handle duplicate rows - only remove true consecutive pair duplicates
        # Sort by original row index to maintain order
        liberty_data.sort(key=lambda x: x['original_row'])
        
        # Remove only consecutive duplicates (within 2 rows of each other)
        final_data = []
        i = 0
        
        while i < len(liberty_data):
            current_entry = liberty_data[i]
            
            # Check if next entry (within 2 rows) is identical
            found_consecutive_duplicate = False
            if i + 1 < len(liberty_data):
                next_entry = liberty_data[i + 1]
                # Check if entries are consecutive or very close and identical
                if (next_entry['original_row'] - current_entry['original_row'] <= 2 and
                    current_entry['quantity'] == next_entry['quantity'] and
                    current_entry['sales_lc'] == next_entry['sales_lc'] and
                    current_entry.get('product_name', '') == next_entry.get('product_name', '')):
                    # Skip the first duplicate, keep the second (bottom of pair)
                    found_consecutive_duplicate = True
                    i += 1  # Skip current, will process next in next iteration
            
            if not found_consecutive_duplicate:
                final_data.append(current_entry)
            
            i += 1
        
        # Debug: Print processing summary
        print(f"Debug: Found {len(liberty_data)} raw entries, {len(final_data)} after deduplication")
        
        # Lookup product EANs using functional_name from Column E
        print(f"DEBUG: Looking up product EANs for {len(final_data)} entries using functional_name from Column E")
        
        if not self.db_service:
            print("ERROR: Database service not available for product lookup")
            for entry in final_data:
                entry['product_ean'] = None
        else:
            print("DEBUG: Database service is available, proceeding with lookups")
            successful_lookups = 0
            failed_lookups = 0
            
            for i, entry in enumerate(final_data):
                functional_name = entry.get('functional_name')
                print(f"DEBUG: Processing entry {i+1}/{len(final_data)}: functional_name='{functional_name}'")
                
                if functional_name and str(functional_name).strip():
                    try:
                        clean_functional_name = str(functional_name).strip()
                        print(f"DEBUG: Looking up product for functional_name: '{clean_functional_name}'")
                        
                        product = await self.db_service.get_product_by_name(clean_functional_name)
                        
                        if product and product.get('ean'):
                            entry['product_ean'] = product['ean']
                            successful_lookups += 1
                            print(f"DEBUG: ✓ Found EAN '{product['ean']}' for functional_name '{clean_functional_name}'")
                        else:
                            entry['product_ean'] = None
                            failed_lookups += 1
                            print(f"DEBUG: ✗ No EAN found for functional_name '{clean_functional_name}' (product: {product})")
                            
                    except Exception as e:
                        import traceback
                        entry['product_ean'] = None
                        failed_lookups += 1
                        print(f"ERROR: Failed to lookup EAN for '{functional_name}': {str(e)}")
                        print(f"ERROR: Full traceback: {traceback.format_exc()}")
                else:
                    entry['product_ean'] = None
                    failed_lookups += 1
                    print(f"DEBUG: ✗ Skipping entry with empty functional_name")
            
            print(f"DEBUG: Product lookup summary - Success: {successful_lookups}, Failed: {failed_lookups}, Total: {len(final_data)}")
            
            # Now do liberty_name to functional_name mapping
            print(f"DEBUG: Starting liberty_name to functional_name mapping for {len(final_data)} entries")
            liberty_mapping_success = 0
            liberty_mapping_failed = 0
            
            for i, entry in enumerate(final_data):
                extracted_functional_name = entry.get('functional_name')
                print(f"DEBUG: Processing entry {i+1}/{len(final_data)} for liberty mapping")
                
                if extracted_functional_name and str(extracted_functional_name).strip():
                    try:
                        # Look up the extracted functional_name in products.liberty_name
                        mapped_functional_name = await self.db_service.get_functional_name_by_liberty_name(str(extracted_functional_name).strip())
                        
                        if mapped_functional_name:
                            # Replace the extracted functional_name with the mapped one (in UPPERCASE)
                            uppercase_functional_name = mapped_functional_name.upper()
                            entry['original_functional_name'] = extracted_functional_name  # Keep original for reference
                            entry['functional_name'] = uppercase_functional_name
                            liberty_mapping_success += 1
                            print(f"DEBUG: ✓ Mapped '{extracted_functional_name}' → '{mapped_functional_name}' → '{uppercase_functional_name}' (UPPERCASE)")
                        else:
                            # No mapping found, keep the original
                            liberty_mapping_failed += 1
                            print(f"DEBUG: ✗ No mapping found for '{extracted_functional_name}', keeping original")
                            
                    except Exception as e:
                        liberty_mapping_failed += 1
                        print(f"ERROR: Failed to map liberty_name '{extracted_functional_name}': {str(e)}")
                else:
                    liberty_mapping_failed += 1
                    print(f"DEBUG: ✗ Skipping entry with empty functional_name for liberty mapping")
            
            print(f"DEBUG: Liberty mapping summary - Success: {liberty_mapping_success}, Failed: {liberty_mapping_failed}, Total: {len(final_data)}")
            
            # Now do functional_name to EAN lookup (final step)
            print(f"DEBUG: Starting functional_name to EAN lookup for {len(final_data)} entries")
            ean_lookup_success = 0
            ean_lookup_failed = 0
            
            for i, entry in enumerate(final_data):
                final_functional_name = entry.get('functional_name')
                print(f"DEBUG: Processing entry {i+1}/{len(final_data)} for EAN lookup")
                
                if final_functional_name and str(final_functional_name).strip():
                    try:
                        # Look up EAN using the final functional_name
                        ean = await self.db_service.get_ean_by_functional_name(str(final_functional_name).strip())
                        
                        if ean:
                            # Set the EAN for this entry
                            entry['product_ean'] = ean
                            ean_lookup_success += 1
                            print(f"DEBUG: ✓ Found EAN '{ean}' for functional_name '{final_functional_name}'")
                        else:
                            # No EAN found, leave product_ean as None
                            ean_lookup_failed += 1
                            print(f"DEBUG: ✗ No EAN found for functional_name '{final_functional_name}'")
                            
                    except Exception as e:
                        ean_lookup_failed += 1
                        print(f"ERROR: Failed to lookup EAN for functional_name '{final_functional_name}': {str(e)}")
                else:
                    ean_lookup_failed += 1
                    print(f"DEBUG: ✗ Skipping entry with empty functional_name for EAN lookup")
            
            print(f"DEBUG: EAN lookup summary - Success: {ean_lookup_success}, Failed: {ean_lookup_failed}, Total: {len(final_data)}")
            
            # Show unique functional_name values after mapping
            functional_names = [entry.get('functional_name') for entry in final_data if entry.get('functional_name')]
            unique_functional_names = list(set(functional_names))
            print(f"DEBUG: Unique functional_name values after complete mapping: {unique_functional_names[:10]}")  # Show first 10
            
            # Show unique EAN values found
            eans = [entry.get('product_ean') for entry in final_data if entry.get('product_ean')]
            unique_eans = list(set(eans))
            print(f"DEBUG: Unique EAN values found: {unique_eans[:10]}")  # Show first 10

        # Create new DataFrame with Liberty data
        if final_data:
            # Debug: Show functional_name values before DataFrame creation
            print("DEBUG: functional_name values before DataFrame creation:")
            for i, entry in enumerate(final_data[:5]):  # Show first 5
                fn = entry.get('functional_name')
                print(f"  Entry {i}: functional_name = '{fn}'")
            
            df_liberty = pd.DataFrame(final_data)
            
            # Debug: Show functional_name values after DataFrame creation
            if 'functional_name' in df_liberty.columns:
                print("DEBUG: functional_name values after DataFrame creation:")
                print(f"  Sample values: {df_liberty['functional_name'].head().tolist()}")
            
            # Add Liberty-specific fields
            df_liberty['report_year'] = year
            df_liberty['report_month'] = month
            df_liberty['reseller'] = 'Liberty'
            df_liberty['currency'] = 'GBP'
            
            # Log transformations
            transformations.append({
                "row_index": 0,
                "column_name": "report_year",
                "original_value": None,
                "cleaned_value": year,
                "transformation_type": "filename_date_extraction"
            })
            
            transformations.append({
                "row_index": 0,
                "column_name": "report_month", 
                "original_value": None,
                "cleaned_value": month,
                "transformation_type": "filename_date_extraction"
            })
            
            return df_liberty, transformations
        else:
            # Return empty DataFrame if no valid data found
            return pd.DataFrame(), transformations
    
    def _extract_liberty_date_from_filename(self) -> Tuple[int, int]:
        """Extract year and month from Liberty filename with -1 week logic"""
        if not self.current_filename:
            return 2025, 5  # Default values
        
        # Example filename: "Continuity Supplier Size Report 01_06_2025.xlsx"
        # Extract date pattern DD_MM_YYYY
        date_pattern = r'(\d{2})_(\d{2})_(\d{4})'
        match = re.search(date_pattern, self.current_filename)
        
        if match:
            day = int(match.group(1))
            month = int(match.group(2))
            year = int(match.group(3))
            
            # Create date and subtract 1 week
            file_date = datetime(year, month, day)
            report_date = file_date - timedelta(weeks=1)
            
            return report_date.year, report_date.month
        
        return 2025, 5  # Default if parsing fails
    
    async def _clean_ukraine_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict]]:
        transformations = []
        
        # Similar to Galilu - unpivot format
        df, trans = await self._clean_galilu_data(df)
        transformations.extend(trans)
        
        return df, transformations
    
    async def _clean_generic_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict]]:
        transformations = []
        return df, transformations
    
    async def _apply_common_cleaning(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict]]:
        transformations = []
        
        # Clean EAN codes
        if 'ean' in df.columns:
            for idx, value in df['ean'].items():
                if pd.notna(value):
                    # Remove spaces and ensure 13 digits
                    clean_value = str(value).strip().replace(' ', '')
                    if clean_value.isdigit():
                        clean_value = clean_value.zfill(13)
                        if clean_value != str(value):
                            transformations.append({
                                "row_index": idx,
                                "column_name": "ean",
                                "original_value": value,
                                "cleaned_value": clean_value,
                                "transformation_type": "ean_normalization"
                            })
                            df.at[idx, 'ean'] = clean_value
        
        # Clean SKU codes
        if 'sku' in df.columns:
            df['sku'] = df['sku'].str.strip().str.upper()
        
        # Clean product names
        if 'product_name' in df.columns:
            df['product_name'] = df['product_name'].str.strip().str.title()
        
        # Remove rows with zero or null quantities
        if 'quantity' in df.columns:
            # Convert to numeric first to handle string values safely
            df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
            # Remove rows with zero, negative, or non-numeric quantities
            df = df[df['quantity'] > 0]
        
        return df, transformations