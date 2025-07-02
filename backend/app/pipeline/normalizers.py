import pandas as pd
from typing import Optional
from app.pipeline.detector import VendorDetector

class DataNormalizer:
    def __init__(self):
        self.vendor_detector = VendorDetector()
    
    async def normalize_data(self, df: pd.DataFrame, vendor: str) -> pd.DataFrame:
        """Normalize data to sellout_entries2 schema"""
        
        vendor_config = self.vendor_detector.get_vendor_config(vendor)
        
        # Create normalized dataframe with sellout_entries2 columns
        normalized_df = pd.DataFrame()
        
        # Map columns to sellout_entries2 schema
        column_mapping = {
            # EAN mappings
            'ean': 'product_ean',
            'eancode': 'product_ean',
            'stockcode': 'product_ean',
            
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
            
            # Product name mappings
            'product_name': 'functional_name',
            'description': 'functional_name',
            'stockdescription': 'functional_name',
            'item': 'functional_name',
            'article': 'functional_name',
            
            # SKU mappings for creating product_ean when missing
            'sku': 'sku_temp',
            
            # Currency
            'currency': 'currency'
        }
        
        # Apply mappings
        for source_col, target_col in column_mapping.items():
            if source_col in df.columns:
                normalized_df[target_col] = df[source_col]
        
        # Fallback logic: if product_ean is missing but we have SKU, try to use that
        if 'product_ean' not in normalized_df.columns or normalized_df['product_ean'].isna().all():
            if 'sku_temp' in normalized_df.columns:
                # Generate EAN from SKU - for now, use SKU as placeholder
                normalized_df['product_ean'] = normalized_df['sku_temp'].astype(str).str.zfill(13)
        
        # Add vendor as reseller
        normalized_df['reseller'] = vendor.replace('_', ' ').title()
        
        # Add currency from vendor config if not present
        if 'currency' not in normalized_df.columns or normalized_df['currency'].isna().all():
            normalized_df['currency'] = vendor_config.get('currency', 'USD')
        
        # Convert data types
        if 'year' in normalized_df.columns:
            normalized_df['year'] = pd.to_numeric(normalized_df['year'], errors='coerce')
            normalized_df['year'] = normalized_df['year'].astype('Int64')  # Nullable integer
        
        if 'month' in normalized_df.columns:
            normalized_df['month'] = pd.to_numeric(normalized_df['month'], errors='coerce')
            normalized_df['month'] = normalized_df['month'].astype('Int64')  # Nullable integer
        
        if 'quantity' in normalized_df.columns:
            normalized_df['quantity'] = pd.to_numeric(normalized_df['quantity'], errors='coerce')
            normalized_df['quantity'] = normalized_df['quantity'].astype('Int64')  # Nullable integer
        
        if 'sales_eur' in normalized_df.columns:
            normalized_df['sales_eur'] = pd.to_numeric(normalized_df['sales_eur'], errors='coerce')
        
        # Handle sales_lc (sales in local currency)
        # If we have both EUR and local currency, use local currency value as sales_lc
        if 'sales_eur' in normalized_df.columns and normalized_df['currency'].notna().any():
            # For now, assume sales_lc is the same as sales_eur converted to string
            normalized_df['sales_lc'] = normalized_df['sales_eur'].astype(str)
        
        # Clean product EAN - ensure 13 digits
        if 'product_ean' in normalized_df.columns:
            normalized_df['product_ean'] = normalized_df['product_ean'].astype(str)
            normalized_df['product_ean'] = normalized_df['product_ean'].str.strip()
            # Zero-pad to 13 digits for valid EANs
            mask = normalized_df['product_ean'].str.isdigit()
            normalized_df.loc[mask, 'product_ean'] = normalized_df.loc[mask, 'product_ean'].str.zfill(13)
        
        # Clean functional_name
        if 'functional_name' in normalized_df.columns:
            normalized_df['functional_name'] = normalized_df['functional_name'].str.strip().str.title()
        
        # Remove rows with missing essential data
        essential_columns = ['product_ean', 'quantity']
        for col in essential_columns:
            if col in normalized_df.columns:
                normalized_df = normalized_df[normalized_df[col].notna()]
        
        # Remove rows with zero or negative quantity
        if 'quantity' in normalized_df.columns:
            normalized_df = normalized_df[normalized_df['quantity'] > 0]
        
        # Clean up temporary columns
        if 'sku_temp' in normalized_df.columns:
            normalized_df = normalized_df.drop('sku_temp', axis=1)
        
        return normalized_df