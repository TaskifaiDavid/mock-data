import logging
import pandas as pd
import asyncio
from functools import partial
from typing import Optional, List, Any
from concurrent.futures import ProcessPoolExecutor

logger = logging.getLogger(__name__)
from app.pipeline.detector import VendorDetector

class DataNormalizer:
    def __init__(self):
        self.vendor_detector = VendorDetector()
    
    async def normalize_data(self, df: pd.DataFrame, vendor: str) -> pd.DataFrame:
        """Normalize data to sellout_entries2 schema with async optimization"""
        
        logger.debug(f"DEBUG: Starting normalization for vendor '{vendor}' with {len(df)} rows")
        logger.debug(f"DEBUG: Input columns: {list(df.columns)}")
        if len(df) > 0:
            logger.debug(f"DEBUG: Sample input row: {df.iloc[0].to_dict()}")
        
        # For large DataFrames, use chunked processing to avoid blocking the event loop
        if len(df) > 10000:
            return await self._normalize_data_chunked(df, vendor)
        else:
            return await self._normalize_data_sync(df, vendor)
        
    async def _normalize_data_sync(self, df: pd.DataFrame, vendor: str) -> pd.DataFrame:
        """Synchronous normalization for smaller datasets"""
        # Offload to thread pool to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self._normalize_data_blocking, df, vendor
        )
    
    async def _normalize_data_chunked(self, df: pd.DataFrame, vendor: str) -> pd.DataFrame:
        """Async chunked processing for large datasets"""
        chunk_size = 5000  # Process in chunks of 5000 rows
        chunks = [df.iloc[i:i + chunk_size] for i in range(0, len(df), chunk_size)]
        
        logger.debug(f"DEBUG: Processing {len(chunks)} chunks of size {chunk_size}")
        
        # Process chunks concurrently
        tasks = []
        for i, chunk in enumerate(chunks):
            task = asyncio.create_task(self._normalize_chunk(chunk, vendor, i))
            tasks.append(task)
            
            # Limit concurrent chunks to avoid memory issues
            if len(tasks) >= 3:  # Process max 3 chunks concurrently
                results = await asyncio.gather(*tasks)
                tasks = []
                # Combine results (first iteration)
                if 'combined_df' not in locals():
                    combined_df = pd.concat(results, ignore_index=True)
                else:
                    combined_df = pd.concat([combined_df] + results, ignore_index=True)
        
        # Process remaining tasks
        if tasks:
            results = await asyncio.gather(*tasks)
            if 'combined_df' not in locals():
                combined_df = pd.concat(results, ignore_index=True)
            else:
                combined_df = pd.concat([combined_df] + results, ignore_index=True)
        
        logger.debug(f"DEBUG: Chunked processing complete - {len(combined_df)} total rows")
        return combined_df
    
    async def _normalize_chunk(self, chunk: pd.DataFrame, vendor: str, chunk_id: int) -> pd.DataFrame:
        """Process a single chunk asynchronously"""
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, self._normalize_data_blocking, chunk, vendor
        )
        logger.debug(f"DEBUG: Chunk {chunk_id} processed - {len(result)} rows")
        return result
    
    def _normalize_data_blocking(self, df: pd.DataFrame, vendor: str) -> pd.DataFrame:
        """Blocking normalization logic moved to separate method"""
        vendor_config = self.vendor_detector.get_vendor_config(vendor)
        
        # Create normalized dataframe with sellout_entries2 columns
        normalized_df = pd.DataFrame()
        
        # Map columns to sellout_entries2 schema
        column_mapping = {
            # EAN mappings
            'ean': 'product_ean',
            'eancode': 'product_ean',
            'stockcode': 'product_ean',
            'product_ean': 'product_ean',  # Direct mapping for Liberty
            
            # Date mappings
            'report_year': 'year',
            'year': 'year',
            'report_month': 'month',
            'month': 'month',
            
            # Quantity mappings
            'quantity': 'quantity',
            'qty': 'quantity',
            'orderqty': 'quantity',
            
            # Sales value mappings
            'gross_value': 'sales_eur',
            'amount': 'sales_eur',
            'net_value': 'sales_eur',
            'sales_inc_vat': 'sales_eur',
            'netsalesvalue': 'sales_eur',
            'exvatnetsales': 'sales_eur',
            'sales_lc': 'sales_lc',  # Direct mapping for local currency sales
            'sales_eur': 'sales_eur',  # Direct mapping for EUR sales
            
            # Product name mappings
            'product_name': 'functional_name',
            'description': 'functional_name',
            'stockdescription': 'functional_name',
            'item': 'functional_name',
            'article': 'functional_name',
            'functional_name': 'functional_name',  # Direct mapping for Liberty
            
            # Currency
            'currency': 'currency'
        }
        
        # Apply mappings
        for source_col, target_col in column_mapping.items():
            if source_col in df.columns:
                normalized_df[target_col] = df[source_col]
        
        # Special handling for SKU column based on vendor
        if 'sku' in df.columns:
            if vendor == 'boxnox':
                # For Boxnox, map SKU to functional_name
                normalized_df['functional_name'] = df['sku']
            else:
                # For other vendors, keep SKU as sku_temp for EAN fallback
                normalized_df['sku_temp'] = df['sku']
        
        # Special handling for sales_lc - preserve raw value from local currency
        if vendor in ['liberty', 'skins_nl', 'cdlc', 'galilu'] and 'sales_lc' in df.columns:
            # Keep the raw sales_lc value as text (don't convert to EUR)
            normalized_df['sales_lc'] = df['sales_lc'].astype(str)
            logger.debug(f"DEBUG: Preserved sales_lc for {vendor}: {normalized_df['sales_lc'].head().tolist()}")
            
            # For EUR currency vendors (like skins_nl), copy sales_lc to sales_eur
            if vendor == 'skins_nl' and 'currency' in df.columns and (df['currency'] == 'EUR').any():
                normalized_df['sales_eur'] = pd.to_numeric(normalized_df['sales_lc'], errors='coerce')
                logger.debug(f"DEBUG: Added sales_eur conversion for skins_nl EUR data")
        
        # Fallback logic: if product_ean is missing but we have SKU, try to use that
        if 'product_ean' not in normalized_df.columns or normalized_df['product_ean'].isna().all():
            if 'sku_temp' in normalized_df.columns:
                # Generate EAN from SKU - for now, use SKU as placeholder
                normalized_df['product_ean'] = normalized_df['sku_temp'].astype(str).str.zfill(13)
        
        # Add vendor as reseller (special cases for proper formatting)
        if vendor == 'liberty':
            normalized_df['reseller'] = 'Liberty'
        elif vendor == 'skins_nl':
            normalized_df['reseller'] = 'TaskifAI'  # Demo profile reseller name
        elif vendor == 'cdlc':
            normalized_df['reseller'] = 'Creme de la Creme'  # CDLC files are for Creme de la Creme reseller
        elif vendor == 'aromateque':
            normalized_df['reseller'] = 'Aromateque'  # Preserve proper capitalization
        elif vendor == 'galilu':
            normalized_df['reseller'] = 'Galilu'  # Proper capitalization for Galilu
        elif vendor == 'unknown':
            normalized_df['reseller'] = 'Demo'  # Demo reseller for unknown/mock data
        else:
            normalized_df['reseller'] = vendor.replace('_', ' ').title()
        
        # Add currency from vendor config if not present
        if 'currency' not in normalized_df.columns or normalized_df['currency'].isna().all():
            normalized_df['currency'] = vendor_config.get('currency', 'USD')
        
        # Convert data types efficiently using vectorized operations
        # Use memory-efficient conversion methods
        if 'year' in normalized_df.columns:
            normalized_df['year'] = pd.to_numeric(normalized_df['year'], errors='coerce', downcast='integer')
            normalized_df['year'] = normalized_df['year'].astype('Int64')  # Nullable integer
        
        if 'month' in normalized_df.columns:
            normalized_df['month'] = pd.to_numeric(normalized_df['month'], errors='coerce', downcast='integer')
            normalized_df['month'] = normalized_df['month'].astype('Int64')  # Nullable integer
        
        if 'quantity' in normalized_df.columns:
            normalized_df['quantity'] = pd.to_numeric(normalized_df['quantity'], errors='coerce', downcast='float')
        
        if 'sales_eur' in normalized_df.columns:
            normalized_df['sales_eur'] = pd.to_numeric(normalized_df['sales_eur'], errors='coerce', downcast='float')
        
        # Handle sales_lc (sales in local currency)
        # If we have both EUR and local currency, use local currency value as sales_lc
        # Skip this for vendors that already handled sales_lc above
        if vendor not in ['liberty', 'skins_nl', 'skins_sa', 'galilu'] and 'sales_eur' in normalized_df.columns and normalized_df['currency'].notna().any():
            # Convert sales_eur to string, but handle NaN values properly
            normalized_df['sales_lc'] = normalized_df['sales_eur'].apply(
                lambda x: None if pd.isna(x) else str(x)
            )
        
        # Clean product EAN - ensure 13 digits
        if 'product_ean' in normalized_df.columns:
            # For Liberty, remove product_ean column entirely if all values are None to avoid foreign key constraint
            if vendor == 'liberty' and normalized_df['product_ean'].isna().all():
                normalized_df = normalized_df.drop('product_ean', axis=1)
                logger.debug("DEBUG: Removed product_ean column for Liberty data (all None values)")
            else:
                normalized_df['product_ean'] = normalized_df['product_ean'].astype(str)
                normalized_df['product_ean'] = normalized_df['product_ean'].str.strip()
                # Zero-pad to 13 digits for valid EANs
                mask = normalized_df['product_ean'].str.isdigit()
                normalized_df.loc[mask, 'product_ean'] = normalized_df.loc[mask, 'product_ean'].str.zfill(13)
                
                # For Liberty, also remove rows where product_ean is 'None', 'nan', etc.
                if vendor == 'liberty':
                    invalid_eans = ['None', 'nan', 'NaN', 'null', '']
                    mask = ~normalized_df['product_ean'].isin(invalid_eans)
                    if not mask.all():
                        logger.debug(f"DEBUG: Removing {(~mask).sum()} Liberty rows with invalid product_ean values")
                        normalized_df = normalized_df[mask]
        
        # Clean functional_name
        if 'functional_name' in normalized_df.columns:
            if vendor == 'liberty':
                # For Liberty, only strip whitespace but preserve case (uppercase set in cleaner)
                normalized_df['functional_name'] = normalized_df['functional_name'].str.strip()
                logger.debug("DEBUG: Preserved functional_name case for Liberty data (no title case conversion)")
            elif vendor == 'boxnox':
                # For Boxnox, convert SKU to uppercase
                normalized_df['functional_name'] = normalized_df['functional_name'].str.strip().str.upper()
                logger.debug("DEBUG: Converted functional_name to uppercase for Boxnox SKU data")
            elif vendor == 'aromateque':
                # For Aromateque, preserve uppercase functional_name (set in cleaner)
                normalized_df['functional_name'] = normalized_df['functional_name'].str.strip().str.upper()
                logger.debug("DEBUG: Preserved uppercase functional_name for Aromateque data")
            elif vendor == 'galilu':
                # For Galilu, preserve original Polish product descriptions (no case conversion)
                normalized_df['functional_name'] = normalized_df['functional_name'].str.strip()
                logger.debug("DEBUG: Preserved original case for Galilu Polish product descriptions")
            else:
                # For other/unknown vendors, keep uppercase (demo data should stay uppercase)
                normalized_df['functional_name'] = normalized_df['functional_name'].str.strip().str.upper()
        
        # Remove rows with missing essential data
        # For Liberty, product_ean will be matched later in Supabase, so don't filter it out
        if vendor == 'liberty':
            essential_columns = ['quantity']
        else:
            essential_columns = ['product_ean', 'quantity']
            
        for col in essential_columns:
            if col in normalized_df.columns:
                normalized_df = normalized_df[normalized_df[col].notna()]
        
        # Remove rows with zero or negative quantity, except when they have sales_lc values (returns, refunds, adjustments)
        if 'quantity' in normalized_df.columns:
            # Convert quantity to numeric first to handle string values
            normalized_df['quantity'] = pd.to_numeric(normalized_df['quantity'], errors='coerce', downcast='float')
            
            # Include rows with positive quantity OR rows with zero/negative quantity that have sales_lc values
            if 'sales_lc' in normalized_df.columns:
                # Vectorized sales_lc cleaning for better performance
                sales_lc_numeric = self._vectorized_clean_sales_values(normalized_df['sales_lc'])
                
                valid_rows_mask = (normalized_df['quantity'] > 0) | (
                    (normalized_df['quantity'] <= 0) & 
                    (normalized_df['sales_lc'].notna()) & 
                    (sales_lc_numeric != 0)
                )
                
                # Debug logging for zero/negative quantity decisions
                zero_with_sales = ((normalized_df['quantity'] == 0) & (sales_lc_numeric != 0)).sum()
                zero_without_sales = ((normalized_df['quantity'] == 0) & (sales_lc_numeric == 0)).sum()
                negative_with_sales = ((normalized_df['quantity'] < 0) & (sales_lc_numeric != 0)).sum()
                negative_without_sales = ((normalized_df['quantity'] < 0) & (sales_lc_numeric == 0)).sum()
                
                logger.debug(f"DEBUG: Zero quantity - Including {zero_with_sales} rows with sales, Excluding {zero_without_sales} rows without sales")
                logger.debug(f"DEBUG: Negative quantity - Including {negative_with_sales} rows with sales, Excluding {negative_without_sales} rows without sales")
                
                normalized_df = normalized_df[valid_rows_mask]
            else:
                # Original logic for vendors without sales_lc
                normalized_df = normalized_df[normalized_df['quantity'] > 0]
            
            # Convert to nullable integer after filtering
            normalized_df['quantity'] = normalized_df['quantity'].astype('Int64')
        
        # Clean up temporary columns
        if 'sku_temp' in normalized_df.columns:
            normalized_df = normalized_df.drop('sku_temp', axis=1)
        
        logger.debug(f"DEBUG: Normalization complete for vendor '{vendor}' - {len(normalized_df)} rows")
        logger.debug(f"DEBUG: Final normalized columns: {list(normalized_df.columns)}")
        if len(normalized_df) > 0:
            logger.debug(f"DEBUG: Sample normalized row: {normalized_df.iloc[0].to_dict()}")
        else:
            logger.debug("WARNING: No rows in normalized data - all data was filtered out!")
        
        return normalized_df
    
    def _vectorized_clean_sales_values(self, sales_series: pd.Series) -> pd.Series:
        """Vectorized cleaning of sales_lc values for better performance"""
        # Handle null values
        result = sales_series.fillna(0)
        
        # Convert to string for cleaning
        result = result.astype(str)
        
        # Remove currency symbols and clean formatting - vectorized
        result = result.str.strip()
        result = result.str.replace(',', '.', regex=False)
        result = result.str.replace('[$£€]', '', regex=True)
        result = result.str.replace(' ', '', regex=False)
        
        # Convert to numeric, coercing errors to 0
        result = pd.to_numeric(result, errors='coerce').fillna(0)
        
        return result