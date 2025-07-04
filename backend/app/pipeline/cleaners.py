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
        elif vendor == "skins_nl":
            df_clean, trans = await self._clean_skins_nl_data(df_clean)
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
        
        # Extract target month and year from filename
        target_year, target_month = self._extract_boxnox_date_from_filename()
        
        print(f"DEBUG: BOXNOX filtering for Year: {target_year}, Month: {target_month}")
        print(f"DEBUG: Original DataFrame shape: {df.shape}")
        print(f"DEBUG: DataFrame columns: {list(df.columns)}")
        print(f"DEBUG: DataFrame dtypes: {df.dtypes.to_dict()}")
        if len(df) > 0:
            print(f"DEBUG: First 3 rows: {df.head(3).to_dict('records')}")
        
        # Check if required columns exist
        required_columns = ['YEAR', 'MONTH']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"ERROR: Missing required columns: {missing_columns}")
            print(f"ERROR: Available columns: {list(df.columns)}")
            # Return original dataframe without filtering if required columns are missing
            transformations.append({
                "row_index": 0,
                "column_name": "filter_skip",
                "original_value": f"Missing columns: {missing_columns}",
                "cleaned_value": f"Skipped filtering due to missing columns: {missing_columns}",
                "transformation_type": "no_filtering_missing_columns"
            })
            df_filtered = df.copy()
        else:
            # Filter data to only include rows matching the target month and year
            initial_rows = len(df)
            df_filtered = df[
                (df['YEAR'] == target_year) & 
                (df['MONTH'] == target_month)
            ].copy()
            
            final_rows = len(df_filtered)
            print(f"DEBUG: After filtering - kept {final_rows} rows out of {initial_rows}")
            
            transformations.append({
                "row_index": 0,
                "column_name": "date_filter",
                "original_value": f"All rows: {initial_rows}",
                "cleaned_value": f"Filtered to Year {target_year}, Month {target_month}: {final_rows} rows",
                "transformation_type": "month_year_filtering"
            })
        
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
        df_filtered.rename(columns=column_mapping, inplace=True)
        
        return df_filtered, transformations
    
    async def _clean_skins_sa_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict]]:
        transformations = []
        
        # Extract year and month from filename
        year, month = self._extract_skins_sa_date_from_filename()
        
        # Debug: Log available columns
        print(f"DEBUG: Available columns in Skins SA file: {list(df.columns)}")
        
        # Column mapping for Skins SA
        column_mapping = {
            'OrderDate': 'order_date',
            'Branch': 'store',
            'StockCode': 'ean',
            'OrderQty': 'quantity',
            ' ExVatNetsales': 'sales_lc',  # Note: space in column name
            'ExVatNetsales': 'sales_lc',
            'MONTH': 'file_month',
            'YEAR': 'file_year'
        }
        
        print(f"DEBUG: Column mapping for Skins SA: {column_mapping}")
        
        # Rename columns
        df.rename(columns=column_mapping, inplace=True)
        print(f"DEBUG: Columns after mapping: {list(df.columns)}")
        
        # Clean EAN data types - convert floats to strings and normalize
        if 'ean' in df.columns:
            print(f"DEBUG: Cleaning EAN data types. Sample before: {df['ean'].head().tolist()}")
            
            for idx, value in df['ean'].items():
                if pd.notna(value):
                    original_value = value
                    
                    # Convert to string and remove decimal points from floats
                    clean_value = str(value).strip()
                    if clean_value.endswith('.0'):
                        clean_value = clean_value[:-2]  # Remove .0
                    
                    # Ensure EAN is digits only and normalize to 13 digits
                    if clean_value.isdigit():
                        clean_value = clean_value.zfill(13)
                        
                        if clean_value != str(original_value):
                            df.at[idx, 'ean'] = clean_value
                            transformations.append({
                                "row_index": idx,
                                "column_name": "ean",
                                "original_value": original_value,
                                "cleaned_value": clean_value,
                                "transformation_type": "ean_normalization"
                            })
                    else:
                        print(f"DEBUG: Invalid EAN format at row {idx}: '{clean_value}' (original: '{original_value}')")
            
            print(f"DEBUG: Sample EANs after cleaning: {df['ean'].head().tolist()}")
        
        # Filter rows - skip rows without StockCode/ean
        if 'ean' in df.columns:
            print(f"DEBUG: Filtering rows with missing StockCode/ean. Rows before: {len(df)}")
            
            # Remove rows where ean is null, empty, or whitespace
            initial_count = len(df)
            df = df[df['ean'].notna() & (df['ean'] != '') & (df['ean'].astype(str).str.strip() != '')]
            filtered_count = len(df)
            
            print(f"DEBUG: Rows after filtering missing StockCode: {filtered_count}")
            
            transformations.append({
                "row_index": 0,
                "column_name": "ean_filter",
                "original_value": f"All rows: {initial_count}",
                "cleaned_value": f"Filtered rows with valid StockCode: {filtered_count}",
                "transformation_type": "stockcode_filtering"
            })
        
        # Filter by month/year matching filename date
        if 'file_month' in df.columns and 'file_year' in df.columns:
            print(f"DEBUG: Filtering by month/year from filename. Target: {month}/{year}")
            
            initial_count = len(df)
            df_filtered = df[
                (pd.to_numeric(df['file_month'], errors='coerce') == month) & 
                (pd.to_numeric(df['file_year'], errors='coerce') == year)
            ].copy()
            
            final_count = len(df_filtered)
            print(f"DEBUG: After date filtering - kept {final_count} rows out of {initial_count}")
            
            transformations.append({
                "row_index": 0,
                "column_name": "date_filter",
                "original_value": f"All rows: {initial_count}",
                "cleaned_value": f"Filtered to Year {year}, Month {month}: {final_count} rows",
                "transformation_type": "month_year_filtering"
            })
            
            df = df_filtered
        else:
            print("DEBUG: No MONTH/YEAR columns found in data, skipping date filtering")
        
        # Clean ZAR currency values - remove spaces and convert to numeric
        if 'sales_lc' in df.columns:
            for idx, value in df['sales_lc'].items():
                if pd.notna(value) and value != '':
                    # Remove spaces and convert to numeric
                    clean_value = str(value).replace(' ', '').replace(',', '').strip()
                    if clean_value:
                        try:
                            numeric_value = float(clean_value)
                            df.at[idx, 'sales_lc'] = str(numeric_value)
                            transformations.append({
                                "row_index": idx,
                                "column_name": "sales_lc",
                                "original_value": value,
                                "cleaned_value": str(numeric_value),
                                "transformation_type": "currency_cleaning"
                            })
                        except ValueError:
                            # If conversion fails, keep original value
                            pass
        
        # Add year and month columns from filename
        df['report_year'] = year
        df['report_month'] = month
        
        # Add reseller and currency
        df['reseller'] = 'Skins SA'
        df['currency'] = 'ZAR'
        
        # Add empty functional_name (not available in Skins SA data)
        df['functional_name'] = ''
        
        # Log transformations for date fields
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
        
        return df, transformations
    
    async def _clean_skins_nl_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict]]:
        transformations = []
        
        # Extract year and month from filename
        year, month = self._extract_skins_nl_date_from_filename()
        
        # Debug: Log available columns
        print(f"DEBUG: Available columns in Skins NL file: {list(df.columns)}")
        
        # Column mapping for Skins NL with fallback options
        column_mapping = {}
        
        # Check for EAN column variations
        ean_columns = ['EANCode', 'EAN', 'ean', 'EAN Code', 'EAN_Code']
        for col in ean_columns:
            if col in df.columns:
                column_mapping[col] = 'ean'
                print(f"DEBUG: Found EAN column: {col}")
                break
        
        # Check for quantity column variations
        quantity_columns = ['SalesQuantity', 'Sales Quantity', 'Quantity', 'quantity', 'Qty', 'Sales_Quantity']
        for col in quantity_columns:
            if col in df.columns:
                column_mapping[col] = 'quantity'
                print(f"DEBUG: Found quantity column: {col}")
                break
        
        # Check for sales amount column variations
        sales_columns = ['SalesAmount', 'Sales Amount', 'Amount', 'Sales_Amount', 'sales_amount']
        for col in sales_columns:
            if col in df.columns:
                column_mapping[col] = 'sales_lc'
                print(f"DEBUG: Found sales amount column: {col}")
                break
        
        print(f"DEBUG: Column mapping for Skins NL: {column_mapping}")
        
        # Rename columns that were found
        if column_mapping:
            df.rename(columns=column_mapping, inplace=True)
            print(f"DEBUG: Columns after mapping: {list(df.columns)}")
        else:
            print("ERROR: No matching columns found for Skins NL data")
            return df, transformations
        
        # Clean EUR currency values - remove € symbol and convert to numeric
        if 'sales_lc' in df.columns:
            for idx, value in df['sales_lc'].items():
                if pd.notna(value) and value != '':
                    # Remove € symbol and convert to numeric
                    clean_value = str(value).replace('€', '').replace(',', '').strip()
                    if clean_value:
                        try:
                            numeric_value = float(clean_value)
                            df.at[idx, 'sales_lc'] = str(numeric_value)
                            transformations.append({
                                "row_index": idx,
                                "column_name": "sales_lc",
                                "original_value": value,
                                "cleaned_value": str(numeric_value),
                                "transformation_type": "currency_cleaning"
                            })
                        except ValueError:
                            # If conversion fails, keep original value
                            pass
        
        # Add year and month columns
        df['report_year'] = year
        df['report_month'] = month
        
        # Add reseller and currency
        df['reseller'] = 'Skins NL'
        df['currency'] = 'EUR'
        
        # Add empty functional_name (not available in Skins NL data)
        df['functional_name'] = ''
        
        # Filter rows more carefully - only remove if quantity is truly missing/invalid
        if 'quantity' in df.columns:
            print(f"DEBUG: Filtering rows with missing/invalid quantity. Rows before: {len(df)}")
            
            # Count different types of quantity values
            total_rows = len(df)
            quantity_notna = df['quantity'].notna().sum()
            quantity_empty_string = (df['quantity'] == '').sum()
            quantity_zero = (df['quantity'] == '0').sum()
            quantity_zero_numeric = (pd.to_numeric(df['quantity'], errors='coerce') == 0).sum()
            
            print(f"DEBUG: Quantity analysis - Total: {total_rows}, NotNA: {quantity_notna}, Empty string: {quantity_empty_string}, Zero string: {quantity_zero}, Zero numeric: {quantity_zero_numeric}")
            
            # Show some sample quantity values to understand the data
            print(f"DEBUG: Sample quantity values: {df['quantity'].head(10).tolist()}")
            
            # More lenient filtering - only remove if quantity is null, empty string, or cannot be converted to positive number
            def is_valid_quantity(val):
                if pd.isna(val):
                    return False
                if val == '' or val == ' ':
                    return False
                try:
                    num_val = float(str(val).strip())
                    return num_val > 0  # Allow positive quantities only
                except (ValueError, TypeError):
                    return False
            
            valid_mask = df['quantity'].apply(is_valid_quantity)
            df = df[valid_mask]
            
            print(f"DEBUG: Rows after filtering invalid quantity: {len(df)}")
            
            # Log some examples of what was filtered out if significant data loss
            if len(df) < total_rows * 0.5:  # If we lost more than 50% of rows
                print("WARNING: Significant data loss during quantity filtering!")
                invalid_quantities = df[~valid_mask]['quantity'].value_counts()
                print(f"DEBUG: Most common invalid quantity values: {invalid_quantities.head()}")
        else:
            print("WARNING: No quantity column found after mapping, skipping quantity filtering")
        
        # Log transformations for date fields
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
                # Include products with zero/negative quantities if they have sales_lc values (returns, refunds, adjustments)
                if not is_total_row and pd.notna(quantity) and pd.notna(sales_lc):
                    # Convert to numeric for comparison, handling string values like "0.00", "-10.50"
                    try:
                        # Handle quantity conversion
                        if pd.notna(quantity):
                            if isinstance(quantity, str):
                                quantity_clean = quantity.strip().replace(',', '')
                                numeric_quantity = float(quantity_clean) if quantity_clean else 0
                            else:
                                numeric_quantity = float(quantity)
                        else:
                            numeric_quantity = 0
                            
                        # Handle sales_lc conversion  
                        if pd.notna(sales_lc):
                            if isinstance(sales_lc, str):
                                sales_lc_clean = sales_lc.strip().replace(',', '').replace('$', '').replace('£', '')
                                numeric_sales_lc = float(sales_lc_clean) if sales_lc_clean else 0
                            else:
                                numeric_sales_lc = float(sales_lc)
                        else:
                            numeric_sales_lc = 0
                            
                    except (ValueError, TypeError) as e:
                        print(f"DEBUG: Error converting values to numeric - quantity: '{quantity}', sales_lc: '{sales_lc}', error: {e}")
                        numeric_quantity = 0
                        numeric_sales_lc = 0
                    
                    # Include if quantity is non-zero OR if quantity is zero/negative but has non-zero sales value
                    include_row = numeric_quantity != 0 or (numeric_quantity == 0 and numeric_sales_lc != 0)
                    
                    # Debug logging for zero quantity row decisions
                    if numeric_quantity == 0:
                        if numeric_sales_lc != 0:
                            print(f"DEBUG: Including zero quantity row {idx} - qty: {quantity} ({numeric_quantity}), sales: {sales_lc} ({numeric_sales_lc}) - HAS SALES VALUE")
                        else:
                            print(f"DEBUG: Excluding zero quantity row {idx} - qty: {quantity} ({numeric_quantity}), sales: {sales_lc} ({numeric_sales_lc}) - NO SALES VALUE")
                    elif numeric_quantity < 0:
                        if numeric_sales_lc != 0:
                            print(f"DEBUG: Including negative quantity row {idx} - qty: {quantity} ({numeric_quantity}), sales: {sales_lc} ({numeric_sales_lc}) - HAS SALES VALUE")
                        else:
                            print(f"DEBUG: Excluding negative quantity row {idx} - qty: {quantity} ({numeric_quantity}), sales: {sales_lc} ({numeric_sales_lc}) - NO SALES VALUE")
                    
                    if include_row:
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
        """Extract year and month from Liberty filename DD-MM-YYYY format"""
        if not self.current_filename:
            return 2025, 5  # Default values
        
        print(f"DEBUG: Extracting date from filename: '{self.current_filename}'")
        
        # Support both formats: DD-MM-YYYY and DD_MM_YYYY
        # Example filenames: 
        # "Continuity Supplier Size Report 11-04-2025.xlsx" 
        # "Continuity Supplier Size Report 01_06_2025.xlsx"
        date_pattern = r'(\d{2})[-_](\d{2})[-_](\d{4})'
        match = re.search(date_pattern, self.current_filename)
        
        if match:
            day = int(match.group(1))
            month = int(match.group(2))
            year = int(match.group(3))
            
            print(f"DEBUG: Parsed date - Day: {day}, Month: {month}, Year: {year}")
            
            # Validate month is 1-12
            if month < 1 or month > 12:
                print(f"ERROR: Invalid month {month}, using defaults")
                return 2025, 5
            
            # Return month and year directly (no date arithmetic needed)
            print(f"DEBUG: Final date - Month: {month}, Year: {year}")
            return year, month
        
        print("DEBUG: No date pattern found, using defaults")
        return 2025, 5  # Default if parsing fails
    
    def _extract_skins_nl_date_from_filename(self) -> Tuple[int, int]:
        """Extract year and month from Skins NL filename ReportPeriodMM-YYYY format"""
        if not self.current_filename:
            return 2025, 1  # Default values
        
        print(f"DEBUG: Extracting date from Skins NL filename: '{self.current_filename}'")
        
        # Pattern: ReportPeriod02-2025
        # Example: BIBBIPARFU_ReportPeriod02-2025.xlsx
        date_pattern = r'ReportPeriod(\d{2})-(\d{4})'
        match = re.search(date_pattern, self.current_filename)
        
        if match:
            month = int(match.group(1))
            year = int(match.group(2))
            
            print(f"DEBUG: Parsed Skins NL date - Month: {month}, Year: {year}")
            
            # Validate month is 1-12
            if month < 1 or month > 12:
                print(f"ERROR: Invalid month {month}, using defaults")
                return 2025, 1
            
            print(f"DEBUG: Final Skins NL date - Month: {month}, Year: {year}")
            return year, month
        
        print("DEBUG: No ReportPeriod date pattern found, using defaults")
        return 2025, 1  # Default if parsing fails
    
    def _extract_skins_sa_date_from_filename(self) -> Tuple[int, int]:
        """Extract year and month from Skins SA filename format (e.g., 'Skins SA BIBBI CY 2025 February')"""
        if not self.current_filename:
            return 2025, 1  # Default values
        
        print(f"DEBUG: Extracting date from Skins SA filename: '{self.current_filename}'")
        
        # Pattern: Skins SA BIBBI CY 2025 February
        # Example: "Skins SA BIBBI CY 2025 February.xlsx"
        
        # First try to extract year (4 digits)
        year_pattern = r'(\d{4})'
        year_match = re.search(year_pattern, self.current_filename)
        
        if year_match:
            year = int(year_match.group(1))
            print(f"DEBUG: Found year: {year}")
        else:
            year = 2025  # Default
            print(f"DEBUG: No year found, using default: {year}")
        
        # Then try to extract month name
        month_names = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12,
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
            'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
            'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        
        month = 1  # Default
        filename_lower = self.current_filename.lower()
        
        for month_name, month_num in month_names.items():
            if month_name in filename_lower:
                month = month_num
                print(f"DEBUG: Found month '{month_name}' -> {month}")
                break
        
        if month == 1:
            print(f"DEBUG: No month found in filename, using default: {month}")
        
        print(f"DEBUG: Final Skins SA date - Month: {month}, Year: {year}")
        return year, month
    
    def _parse_month_name(self, month_name: str) -> int:
        """Convert month name to number (e.g., 'APR' -> 4)"""
        month_mapping = {
            'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
            'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12
        }
        return month_mapping.get(month_name.upper(), 1)
    
    def _extract_boxnox_date_from_filename(self) -> Tuple[int, int]:
        """Extract year and month from BOXNOX filename APR2025 format"""
        if not self.current_filename:
            return 2025, 4  # Default values
        
        print(f"DEBUG: Extracting date from BOXNOX filename: '{self.current_filename}'")
        
        # Pattern for month names followed by year
        # Example: "BOXNOX - BIBBI Monthly Sales Report APR2025"
        date_pattern = r'([A-Z]{3})(\d{4})'
        match = re.search(date_pattern, self.current_filename.upper())
        
        if match:
            month_str = match.group(1)
            year = int(match.group(2))
            month = self._parse_month_name(month_str)
            
            print(f"DEBUG: Parsed BOXNOX date - Month: {month_str} ({month}), Year: {year}")
            return year, month
        
        print("DEBUG: No BOXNOX date pattern found, using defaults")
        return 2025, 4  # Default if parsing fails
    
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
        
        # Remove rows with zero or null quantities (but preserve for some vendors)
        if 'quantity' in df.columns:
            print(f"DEBUG: Common cleaning - quantity filtering. Rows before: {len(df)}")
            # Convert to numeric first to handle string values safely
            df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
            
            # For most vendors, remove zero/negative quantities
            # But this filtering is now handled in vendor-specific cleaning and normalization
            # So we'll just convert to numeric here and let other stages handle filtering
            print(f"DEBUG: Common cleaning - converted quantity to numeric. Rows after: {len(df)}")
            
            # Only remove truly invalid (NaN) quantities that couldn't be converted
            initial_count = len(df)
            df = df[df['quantity'].notna()]
            filtered_count = len(df)
            
            if filtered_count < initial_count:
                print(f"DEBUG: Common cleaning - removed {initial_count - filtered_count} rows with non-numeric quantities")
        
        return df, transformations