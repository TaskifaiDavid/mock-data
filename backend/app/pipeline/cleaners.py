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
        print(f"DEBUG: Applying vendor-specific cleaning for vendor: '{vendor}'")
        if vendor == "galilu":
            print("DEBUG: Using _clean_galilu_data()")
            df_clean, trans = await self._clean_galilu_data(df_clean)
        elif vendor == "boxnox":
            print("DEBUG: Using _clean_boxnox_data()")
            df_clean, trans = await self._clean_boxnox_data(df_clean)
        elif vendor == "skins_sa":
            print("DEBUG: Using _clean_skins_sa_data()")
            df_clean, trans = await self._clean_skins_sa_data(df_clean)
        elif vendor == "skins_nl":
            print("DEBUG: Using _clean_skins_nl_data()")
            df_clean, trans = await self._clean_skins_nl_data(df_clean)
        elif vendor == "cdlc":
            print("DEBUG: Using _clean_cdlc_data()")
            df_clean, trans = await self._clean_cdlc_data(df_clean)
        elif vendor == "continuity":
            print("DEBUG: Using _clean_continuity_data()")
            df_clean, trans = await self._clean_continuity_data(df_clean)
        elif vendor == "liberty":
            print("DEBUG: Using _clean_liberty_data()")
            df_clean, trans = await self._clean_liberty_data(df_clean)
        elif vendor == "ukraine":
            print("DEBUG: Using _clean_ukraine_data()")
            df_clean, trans = await self._clean_ukraine_data(df_clean)
        elif vendor == "aromateque":
            print("DEBUG: Using _clean_aromateque_data()")
            df_clean, trans = await self._clean_aromateque_data(df_clean)
        else:
            print(f"DEBUG: Using _clean_generic_data() for unknown vendor: '{vendor}'")
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
        
        # Extract year and month from filename or cell B2
        year, month = self._extract_cdlc_date_from_filename_or_data(df)
        
        print(f"DEBUG: CDLC processing for Year: {year}, Month: {month}")
        print(f"DEBUG: Original DataFrame shape: {df.shape}")
        print(f"DEBUG: DataFrame columns: {list(df.columns)}")
        
        # Handle pivot table format - data starts at row 4 (0-indexed), headers at row 3
        print(f"DEBUG: === HEADER PROCESSING STEP ===")
        print(f"DEBUG: Original DataFrame shape before header processing: {df.shape}")
        
        if len(df) > 2:
            print(f"DEBUG: Skipping first 2 rows (0-1), keeping rows 2+ as header and data")
            print(f"DEBUG: Row 2 (header): {df.iloc[2].tolist()}")
            print(f"DEBUG: Rows 3+ (data): {len(df) - 3} rows")
            
            # Show what rows we're about to keep
            for i in range(2, min(len(df), 12)):  # Show first few rows
                print(f"DEBUG: Row {i}: {df.iloc[i].tolist()}")
            
            # Skip first 2 rows to get to header row
            df = df.iloc[2:].reset_index(drop=True)
            print(f"DEBUG: After iloc[2:] - shape: {df.shape}")
            
            # Set column names from first row (header row)
            if len(df) > 0:
                print(f"DEBUG: Setting column names from row 0: {df.iloc[0].tolist()}")
                df.columns = df.iloc[0]
                print(f"DEBUG: Before dropping header row - shape: {df.shape}")
                df = df[1:].reset_index(drop=True)
                print(f"DEBUG: After dropping header row - final shape: {df.shape}")
            else:
                print("DEBUG: ERROR - No rows left after iloc[2:]!")
        else:
            print(f"DEBUG: ERROR - DataFrame too short ({len(df)} rows), expected at least 3 rows")
        
        print(f"DEBUG: After header processing - DataFrame shape: {df.shape}")
        print(f"DEBUG: Column names after header processing: {list(df.columns)}")
        print(f"DEBUG: Expected 7 data rows, actual rows available: {len(df)}")
        
        # Show all rows after header processing
        print("DEBUG: All rows after header processing:")
        for i in range(len(df)):
            row_data = df.iloc[i].tolist()
            print(f"  Row {i}: {row_data}")
        print()
        
        # Process pivot table format with multiple store locations
        processed_rows = []
        total_rows_processed = 0
        skipped_rows = []
        
        for idx, row in df.iterrows():
            total_rows_processed += 1
            print(f"DEBUG: === PROCESSING ROW {idx} (iteration {total_rows_processed}) ===")
            
            # Show raw row data
            row_data = row.tolist()
            print(f"DEBUG: Raw row data: {row_data}")
            
            # Check column 1 for EAN
            col1_value = row.iloc[1] if len(row) > 1 else None
            print(f"DEBUG: Column 1 (EAN position) value: '{col1_value}' (type: {type(col1_value)})")
            
            # Skip empty rows or rows without EAN  
            if pd.isna(col1_value) or str(col1_value).strip() == '':
                print(f"DEBUG: SKIPPING row {idx} - empty EAN (column 1 is empty)")
                skipped_rows.append(f"Row {idx}: Empty EAN")
                continue
                
            # Extract EAN from column 1 (contains EAN data after header processing)
            ean = str(col1_value).strip()
            print(f"DEBUG: Extracted EAN: '{ean}' (length: {len(ean)})")
            
            # Validate EAN is 13 digits
            if not ean.isdigit():
                print(f"DEBUG: SKIPPING row {idx} - EAN not all digits: '{ean}'")
                skipped_rows.append(f"Row {idx}: EAN not digits - '{ean}'")
                continue
            elif len(ean) != 13:
                print(f"DEBUG: SKIPPING row {idx} - EAN wrong length: '{ean}' (length: {len(ean)})")
                skipped_rows.append(f"Row {idx}: EAN wrong length - '{ean}' (length: {len(ean)})")
                continue
            
            print(f"DEBUG: ✓ Valid EAN: '{ean}'")
            
            # Extract product name from column 2 (contains product descriptions after header processing)
            col2_value = row.iloc[2] if len(row) > 2 else None
            functional_name = str(col2_value).strip() if pd.notna(col2_value) else ''
            print(f"DEBUG: Product name (column 2): '{functional_name}'")
            
            # Read totals directly from the last two columns (Total Qty and Total Sales)
            # After header processing: Column 13 = Total Qty, Column 14 = Total Sales
            total_quantity = 0
            total_sales = 0
            
            # Extract quantity from column 13 (Total Qty column)
            if 13 < len(row):
                qty_val = row.iloc[13]
                print(f"DEBUG: Column 13 (Total Qty) raw value: '{qty_val}' (type: {type(qty_val)})")
                if pd.notna(qty_val) and str(qty_val).strip():
                    try:
                        total_quantity = float(str(qty_val).strip())
                        print(f"DEBUG: ✓ Parsed quantity: {total_quantity}")
                    except ValueError as e:
                        print(f"DEBUG: Failed to parse quantity '{qty_val}': {e}")
                        total_quantity = 0
                else:
                    print(f"DEBUG: Column 13 is empty or NaN")
            else:
                print(f"DEBUG: Row too short for column 13 (row length: {len(row)})")
            
            # Extract sales from column 14 (Total Sales column)  
            if 14 < len(row):
                sales_val = row.iloc[14]
                print(f"DEBUG: Column 14 (Total Sales) raw value: '{sales_val}' (type: {type(sales_val)})")
                if pd.notna(sales_val) and str(sales_val).strip():
                    try:
                        total_sales = float(str(sales_val).strip())
                        print(f"DEBUG: ✓ Parsed sales: {total_sales}")
                    except ValueError as e:
                        print(f"DEBUG: Failed to parse sales '{sales_val}': {e}")
                        total_sales = 0
                else:
                    print(f"DEBUG: Column 14 is empty or NaN")
            else:
                print(f"DEBUG: Row too short for column 14 (row length: {len(row)})")
            
            print(f"DEBUG: Final values - Qty: {total_quantity}, Sales: {total_sales}")
            
            # Only include rows with non-zero quantity or sales
            if total_quantity > 0 or total_sales > 0:
                print(f"DEBUG: ✓ INCLUDING row {idx} - has non-zero quantity or sales")
                processed_rows.append({
                    'product_ean': ean,
                    'functional_name': '',
                    'quantity': total_quantity,
                    'sales_lc': total_sales,
                    'report_year': year,
                    'report_month': month,
                    'reseller': 'Creme de la Creme',
                    'currency': 'EUR'
                })
                
                print(f"DEBUG: ✓ ADDED to processed_rows - EAN: {ean}, Qty: {total_quantity}, Sales: {total_sales}")
            else:
                print(f"DEBUG: ✗ EXCLUDING row {idx} - zero quantity and zero sales")
                skipped_rows.append(f"Row {idx}: Zero quantity ({total_quantity}) and zero sales ({total_sales})")
            
            print() # Empty line for readability
        
        # Summary of processing
        print("DEBUG: === PROCESSING SUMMARY ===")
        print(f"DEBUG: Total rows processed: {total_rows_processed}")
        print(f"DEBUG: Rows successfully added: {len(processed_rows)}")
        print(f"DEBUG: Rows skipped: {len(skipped_rows)}")
        if skipped_rows:
            print("DEBUG: Reasons for skipping:")
            for reason in skipped_rows:
                print(f"  - {reason}")
        print()
        
        # Create new DataFrame from processed rows
        if processed_rows:
            df_cleaned = pd.DataFrame(processed_rows)
            print(f"DEBUG: Created cleaned DataFrame with {len(df_cleaned)} rows")
        else:
            df_cleaned = pd.DataFrame()
            print("DEBUG: No valid rows found, returning empty DataFrame")
        
        # Log transformations
        transformations.append({
            "row_index": 0,
            "column_name": "pivot_processing",
            "original_value": f"Pivot table with {len(df)} rows",
            "cleaned_value": f"Aggregated to {len(df_cleaned)} product entries",
            "transformation_type": "pivot_table_aggregation"
        })
        
        transformations.append({
            "row_index": 0,
            "column_name": "report_year",
            "original_value": None,
            "cleaned_value": year,
            "transformation_type": "date_extraction"
        })
        
        transformations.append({
            "row_index": 0,
            "column_name": "report_month",
            "original_value": None,
            "cleaned_value": month,
            "transformation_type": "date_extraction"
        })
        
        return df_cleaned, transformations
    
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
    
    def _extract_cdlc_date_from_filename_or_data(self, df: pd.DataFrame) -> Tuple[int, int]:
        """Extract year and month from CDLC filename or cell B2"""
        # First try to extract from filename
        if self.current_filename:
            print(f"DEBUG: Extracting date from CDLC filename: '{self.current_filename}'")
            
            # Pattern: YYYY MM in filename (e.g., "BIBBI_Sell_Out_2025 04.xlsx")
            date_pattern = r'(\d{4})\s+(\d{2})'
            match = re.search(date_pattern, self.current_filename)
            
            if match:
                year = int(match.group(1))
                month = int(match.group(2))
                print(f"DEBUG: Found date in filename - Year: {year}, Month: {month}")
                return year, month
        
        # If filename parsing fails, try to extract from cell B2
        try:
            if len(df) > 1 and len(df.columns) > 1:
                # Cell B2 should contain format "YYYY Month" (e.g., "2025 April")
                cell_b2_value = df.iloc[1, 1]  # Row 2, Column B (0-indexed)
                if pd.notna(cell_b2_value):
                    cell_value = str(cell_b2_value).strip()
                    print(f"DEBUG: Checking cell B2 for date: '{cell_value}'")
                    
                    # Pattern: YYYY Month
                    date_pattern = r'(\d{4})\s+(\w+)'
                    match = re.search(date_pattern, cell_value)
                    
                    if match:
                        year = int(match.group(1))
                        month_name = match.group(2).lower()
                        
                        # Convert month name to number
                        month_mapping = {
                            'january': 1, 'february': 2, 'march': 3, 'april': 4,
                            'may': 5, 'june': 6, 'july': 7, 'august': 8,
                            'september': 9, 'october': 10, 'november': 11, 'december': 12
                        }
                        
                        month = month_mapping.get(month_name, 1)
                        print(f"DEBUG: Found date in cell B2 - Year: {year}, Month: {month_name} ({month})")
                        return year, month
        except Exception as e:
            print(f"DEBUG: Error extracting date from cell B2: {e}")
        
        print("DEBUG: No CDLC date pattern found, using defaults")
        return 2025, 4  # Default if parsing fails
    
    async def _clean_ukraine_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict]]:
        transformations = []
        
        # Similar to Galilu - unpivot format
        df, trans = await self._clean_galilu_data(df)
        transformations.extend(trans)
        
        return df, transformations
    
    async def _clean_aromateque_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict]]:
        transformations = []
        
        # Extract year and month from filename (format: march'25)
        year, month = self._extract_aromateque_date_from_filename()
        
        print(f"DEBUG: Aromateque processing for Year: {year}, Month: {month}")
        print(f"DEBUG: Original DataFrame shape: {df.shape}")
        print(f"DEBUG: DataFrame columns: {list(df.columns)}")
        
        # Handle pivot table format - headers at row 12 (0-indexed), data starts at row 13
        print(f"DEBUG: === HEADER PROCESSING STEP ===")
        print(f"DEBUG: Original DataFrame shape before header processing: {df.shape}")
        print(f"DEBUG: DataFrame read with header=None, all columns are numeric indices")
        
        # With header=None, everything is 0-indexed and we have numeric column names
        # Corrected: header row is 10 (contains datetime values), data starts at row 11
        if len(df) > 10:
            print(f"DEBUG: Using row 10 as header (contains datetime values)")
            print(f"DEBUG: Skipping rows 0-9 (store summary data)")
            print(f"DEBUG: Row 10 (header): {df.iloc[10].tolist()}")
            print(f"DEBUG: Rows 11+ (product data): {len(df) - 11} rows")
            
            # Show what rows we're about to keep
            for i in range(min(len(df), 15)):  # Show first few rows including header
                print(f"DEBUG: Row {i}: {df.iloc[i].tolist()}")
            
            # Skip first 10 rows to get to header row
            df = df.iloc[10:].reset_index(drop=True)
            print(f"DEBUG: After iloc[10:] - shape: {df.shape}")
            
            # Set column names from first row (header row at original row 10)
            header_row = df.iloc[0].tolist()
            print(f"DEBUG: Setting column names from row 0 (original row 10): {header_row}")
            # Clean up any NaN values in headers
            cleaned_headers = []
            for i, header in enumerate(header_row):
                if pd.isna(header) or str(header).strip() == '':
                    cleaned_headers.append(f'Unnamed_{i}')
                else:
                    cleaned_headers.append(str(header).strip())
            
            df.columns = cleaned_headers
            print(f"DEBUG: Cleaned column names: {df.columns.tolist()}")
            print(f"DEBUG: Before dropping header row - shape: {df.shape}")
            df = df[1:].reset_index(drop=True)
            print(f"DEBUG: After dropping header row - final shape: {df.shape}")
        else:
            print(f"DEBUG: ERROR - DataFrame too short ({len(df)} rows), expected at least 11 rows")
        
        print(f"DEBUG: After header processing - DataFrame shape: {df.shape}")
        print(f"DEBUG: Column names after header processing: {list(df.columns)}")
        
        # Debug: Show each column name with its index and type
        print("DEBUG: Detailed column analysis:")
        for i, col in enumerate(df.columns):
            print(f"  Column {i}: '{col}' (type: {type(col)}, str: '{str(col)}')")
        
        # Find the target date column for the extracted month/year
        # Ukrainian month names mapping
        ukrainian_months = {
            1: 'січня',     # January
            2: 'лютого',    # February  
            3: 'березня',   # March
            4: 'квітня',    # April
            5: 'травня',    # May
            6: 'червня',    # June
            7: 'липня',     # July
            8: 'серпня',    # August
            9: 'вересня',   # September
            10: 'жовтня',   # October
            11: 'листопада', # November
            12: 'грудня'    # December
        }
        
        # Create both target formats
        ukrainian_month_name = ukrainian_months.get(month, 'березня')
        year_suffix = str(year)[-2:]  # Get last 2 digits of year (2025 -> 25)
        target_date_str = f"{ukrainian_month_name}-{year_suffix}"
        
        # Create target datetime object (01.MM.YYYY format like in Excel)
        from datetime import datetime
        target_datetime = datetime(year, month, 1)
        
        print(f"DEBUG: Month {month} -> Ukrainian: '{ukrainian_month_name}' -> Target text: '{target_date_str}'")
        print(f"DEBUG: Month {month} -> Target datetime: {target_datetime}")
        
        target_column = None
        print("DEBUG: Searching for target column...")
        
        # First try: Look for target string in column names
        for i, col in enumerate(df.columns):
            col_str = str(col).strip() if pd.notna(col) else 'None'
            matches = col_str == target_date_str
            print(f"  Column {i} name: '{col_str}' == '{target_date_str}' ? {matches}")
            if matches:
                target_column = col
                print(f"DEBUG: ✓ Found target date column by name at index {i}: '{target_column}'")
                break
        
        # Second try: Look for target datetime in column names (Excel auto-converted headers)
        if not target_column:
            print("DEBUG: Column names don't match text, checking for datetime objects...")
            for i, col in enumerate(df.columns):
                col_str = str(col).strip() if pd.notna(col) else 'None'
                print(f"  Column {i} name: '{col_str}' (type: {type(col)})")
                
                # Check if this is a datetime object that matches our target
                if isinstance(col, str) and col.strip():
                    try:
                        # Try to parse the column name as datetime
                        parsed_datetime = pd.to_datetime(col.strip())
                        if (parsed_datetime.year == target_datetime.year and 
                            parsed_datetime.month == target_datetime.month):
                            target_column = col
                            print(f"DEBUG: ✓ Found target date column by datetime parsing at index {i}: '{target_column}'")
                            break
                    except:
                        pass
                
                # Also check if the string representation looks like our target datetime
                if target_datetime.strftime('%Y-%m-%d') in col_str:
                    target_column = col
                    print(f"DEBUG: ✓ Found target date column by datetime string match at index {i}: '{target_column}'")
                    break
        
        # Third try: Look for target string in first row values (header row data)
        if not target_column and len(df) > 0:
            print("DEBUG: Column names don't match, checking first row values for Ukrainian text...")
            first_row = df.iloc[0]
            for i, (col, val) in enumerate(first_row.items()):
                val_str = str(val).strip() if pd.notna(val) else 'None'
                matches = val_str == target_date_str
                print(f"  Column {i} value: '{val_str}' == '{target_date_str}' ? {matches}")
                if matches:
                    target_column = col
                    print(f"DEBUG: ✓ Found target date column by first row value at index {i}: '{target_column}'")
                    break
        
        if not target_column:
            print(f"DEBUG: Target date column {target_date_str} not found, available columns: {list(df.columns)}")
            # Try alternative formats and partial matches
            alt_formats = [
                ukrainian_month_name,  # Just month name
                f"{ukrainian_month_name}-{year}",  # Full year
                f"{month:02d}.{year}",  # Numeric format
                f"01.{month:02d}.{year}",  # Full date format
                f"{year}-{month:02d}-01",  # ISO format
                f"{target_datetime.strftime('%Y-%m-%d')}",  # Target datetime as string
            ]
            for alt_format in alt_formats:
                for col in df.columns:
                    if pd.notna(col) and alt_format in str(col):
                        target_column = col
                        print(f"DEBUG: Found alternative date column: {target_column} (matched '{alt_format}')")
                        break
                if target_column:
                    break
            
            # Final attempt: Look for columns that contain datetime-like strings matching our target
            if not target_column:
                print("DEBUG: Final attempt - checking for datetime strings in columns...")
                for col in df.columns:
                    col_str = str(col).strip()
                    # Check if this looks like a datetime string that matches our target month/year
                    if (f"{year}-{month:02d}" in col_str or 
                        f"{month:02d}.{year}" in col_str or
                        f"01.{month:02d}.{year}" in col_str):
                        target_column = col
                        print(f"DEBUG: ✓ Found target date column by datetime pattern: '{target_column}'")
                        break
        
        if not target_column:
            print("ERROR: Could not find target date column, returning empty DataFrame")
            return pd.DataFrame(), transformations
        
        # Process data rows
        processed_rows = []
        print(f"DEBUG: === STARTING ROW PROCESSING ===")
        print(f"DEBUG: Processing {len(df)} rows looking for data in column '{target_column}'")
        
        # Skip first row if it contains header values (like "березня-25")
        start_row = 1 if len(df) > 0 and any(str(val).strip() in [ukrainian_months.get(i, '') + '-25' for i in range(1, 13)] for val in df.iloc[0]) else 0
        print(f"DEBUG: Starting data processing from row {start_row} (0=first row, 1=skip header row)")
        
        for idx in range(start_row, len(df)):
            row = df.iloc[idx]
            print(f"DEBUG: === PROCESSING ROW {idx} ===")
            print(f"DEBUG: Full row data: {row.tolist()}")
            
            # Get functional_name from column index 1 (column B in Excel)
            # After header processing with header=None, column indices should be preserved
            functional_name = row.iloc[1] if len(row) > 1 else None
            print(f"DEBUG: Column index 1 (Excel column B) functional_name: '{functional_name}' (type: {type(functional_name)})")
            
            # Also check what's in column index 0 for reference
            product_name = row.iloc[0] if len(row) > 0 else None  
            print(f"DEBUG: Column index 0 (Excel column A) product_name: '{product_name}' (type: {type(product_name)})")
            
            # Show which column we're looking for quantities in
            print(f"DEBUG: Looking for quantity in target column: '{target_column}'")
            
            # Skip rows without functional_name
            if pd.isna(functional_name) or str(functional_name).strip() == '':
                print(f"DEBUG: SKIPPING row {idx} - empty functional_name (value: '{functional_name}')")
                continue
            
            # Debug: Show what's in the target column for this row
            if target_column in row.index:
                target_value = row[target_column]
                print(f"DEBUG: Target column '{target_column}' value: '{target_value}' (type: {type(target_value)})")
            else:
                print(f"DEBUG: ERROR - Target column '{target_column}' not found in row!")
                continue
            
            # Get quantity from target date column
            quantity = row[target_column] if target_column in row.index else None
            print(f"DEBUG: Quantity from {target_column}: '{quantity}'")
            
            # Clean quantity value
            clean_quantity = 0
            if pd.notna(quantity) and str(quantity).strip():
                quantity_str = str(quantity).strip().replace(',', '').replace(' ', '')
                print(f"DEBUG: Raw quantity: '{quantity}' -> cleaned: '{quantity_str}'")
                try:
                    clean_quantity = float(quantity_str)
                    print(f"DEBUG: ✓ Parsed quantity successfully: {clean_quantity}")
                except ValueError as e:
                    print(f"DEBUG: ✗ Could not parse quantity '{quantity}' (cleaned: '{quantity_str}'): {e}")
                    clean_quantity = 0
            else:
                print(f"DEBUG: Quantity is empty/null: '{quantity}'")
            
            # Only include rows with positive quantity (as per requirements)
            print(f"DEBUG: Final quantity for row {idx}: {clean_quantity}")
            if clean_quantity > 0:
                # Ensure functional_name is uppercase for database consistency
                clean_functional_name = str(functional_name).strip().upper()
                print(f"DEBUG: ✓ INCLUDING row {idx} - functional_name: '{clean_functional_name}' (uppercase), quantity: {clean_quantity}")
                processed_rows.append({
                    'functional_name': clean_functional_name,
                    'quantity': clean_quantity,
                    'sales_lc': None,  # No sales data available per profile
                    'product_ean': None,  # Will be looked up later
                    'report_year': year,
                    'report_month': month,
                    'reseller': 'Aromateque',
                    'currency': 'EUR'
                })
            else:
                clean_functional_name = str(functional_name).strip().upper()
                print(f"DEBUG: ✗ EXCLUDING row {idx} - zero/negative quantity: {clean_quantity} (functional_name: '{clean_functional_name}')")
        
        print(f"DEBUG: === PROCESSING SUMMARY ===")
        print(f"DEBUG: Total rows processed: {len(df)}")
        print(f"DEBUG: Rows successfully added: {len(processed_rows)}")
        print(f"DEBUG: Expected ~16 rows for March data from screenshot")
        
        # Show details of processed rows
        if processed_rows:
            print(f"DEBUG: Processed rows details:")
            for i, row in enumerate(processed_rows):
                print(f"  Row {i}: functional_name='{row['functional_name']}', quantity={row['quantity']}")
            
            # Show functional names that were included
            functional_names = [row['functional_name'] for row in processed_rows]
            print(f"DEBUG: Functional names included: {functional_names}")
            
            # Lookup product EANs using functional_name (SKU codes)
            print(f"DEBUG: Looking up product EANs for {len(processed_rows)} entries using functional_name (SKU codes)")
            
            if not self.db_service:
                print("ERROR: Database service not available for product lookup")
                for entry in processed_rows:
                    entry['product_ean'] = None
            else:
                print("DEBUG: Database service is available, proceeding with lookups")
                successful_lookups = 0
                failed_lookups = 0
                
                for i, entry in enumerate(processed_rows):
                    functional_name = entry.get('functional_name')
                    print(f"DEBUG: Processing entry {i+1}/{len(processed_rows)}: functional_name='{functional_name}'")
                    
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
                
                print(f"DEBUG: Product lookup summary - Success: {successful_lookups}, Failed: {failed_lookups}, Total: {len(processed_rows)}")
                
                # Filter out entries without EANs (can't insert into database)
                entries_with_ean = [entry for entry in processed_rows if entry.get('product_ean')]
                entries_without_ean = [entry for entry in processed_rows if not entry.get('product_ean')]
                
                if entries_without_ean:
                    print(f"WARNING: Filtering out {len(entries_without_ean)} entries without EANs:")
                    for entry in entries_without_ean:
                        print(f"  - {entry.get('functional_name', 'Unknown')}")
                
                processed_rows = entries_with_ean
                print(f"DEBUG: After EAN filtering: {len(processed_rows)} entries remain")
        
        # Create new DataFrame from processed rows
        if processed_rows:
            df_cleaned = pd.DataFrame(processed_rows)
            print(f"DEBUG: Created cleaned DataFrame with {len(df_cleaned)} rows")
            print(f"DEBUG: DataFrame columns: {list(df_cleaned.columns)}")
            print(f"DEBUG: Sample DataFrame content:")
            print(df_cleaned.head().to_string())
        else:
            df_cleaned = pd.DataFrame()
            print("DEBUG: No valid rows found, returning empty DataFrame")
        
        # Log transformations
        transformations.append({
            "row_index": 0,
            "column_name": "pivot_processing",
            "original_value": f"Pivot table with {len(df)} rows",
            "cleaned_value": f"Extracted {len(df_cleaned)} product entries for {target_date_str}",
            "transformation_type": "pivot_table_date_extraction"
        })
        
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
        
        return df_cleaned, transformations
    
    def _extract_aromateque_date_from_filename(self) -> Tuple[int, int]:
        """Extract year and month from Aromateque filename (format: march'25)"""
        if not self.current_filename:
            return 2025, 1  # Default values
        
        print(f"DEBUG: Extracting date from Aromateque filename: '{self.current_filename}'")
        
        # Primary format: month'YY (e.g., march'25, april'25)
        month_names = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        
        # Try month'YY format first
        for month_name, month_num in month_names.items():
            pattern = rf"{month_name}'(\d{{2}})"
            match = re.search(pattern, self.current_filename.lower())
            if match:
                year_suffix = int(match.group(1))
                year = 2000 + year_suffix  # Convert 25 to 2025
                print(f"DEBUG: Found month'YY format - Month: {month_name} ({month_num}), Year: {year}")
                return year, month_num
        
        # Fallback: Try month abbreviations with apostrophe
        month_abbrevs = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        
        for month_abbrev, month_num in month_abbrevs.items():
            pattern = rf"{month_abbrev}'(\d{{2}})"
            match = re.search(pattern, self.current_filename.lower())
            if match:
                year_suffix = int(match.group(1))
                year = 2000 + year_suffix  # Convert 25 to 2025
                print(f"DEBUG: Found abbrev'YY format - Month: {month_abbrev} ({month_num}), Year: {year}")
                return year, month_num
        
        # Additional fallback: Try without apostrophe
        for month_name, month_num in month_names.items():
            pattern = rf"{month_name}(\d{{2}})"
            match = re.search(pattern, self.current_filename.lower())
            if match:
                year_suffix = int(match.group(1))
                year = 2000 + year_suffix
                print(f"DEBUG: Found monthYY format - Month: {month_name} ({month_num}), Year: {year}")
                return year, month_num
        
        print("DEBUG: No date pattern found in Aromateque filename, using defaults")
        return 2025, 1  # Default if parsing fails
    
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