import pandas as pd
import re
from typing import Optional

class VendorDetector:
    def detect_vendor(self, filename: str, df: pd.DataFrame) -> Optional[str]:
        """Detect vendor based on filename and sheet content"""
        
        filename_lower = filename.lower()
        
        # Check filename patterns
        if "galilu" in filename_lower:
            return "galilu"
        elif "boxnox" in filename_lower:
            return "boxnox"
        elif "skins sa" in filename_lower:
            return "skins_sa"
        elif "bibbiparfu" in filename_lower:
            return "skins_nl"
        elif "cdlc" in filename_lower:
            return "cdlc"
        elif "continuity" in filename_lower:
            return "liberty"
        elif "bibbi sales" in filename_lower:
            return "ukraine"
        
        # Check sheet names if available
        if hasattr(df, 'sheet_names'):
            sheet_names = [s.lower() for s in df.sheet_names]
            if any("sell out by ean" in s for s in sheet_names):
                return "boxnox"
            elif any("salespersku" in s for s in sheet_names):
                return "skins_nl"
            elif any("bibbi" in s for s in sheet_names):
                return "skins_sa"
            elif any("tdsheet" in s for s in sheet_names):
                return "ukraine"
        
        # Default vendor if pattern not found
        return "unknown"
    
    def get_vendor_config(self, vendor: str) -> dict:
        """Get vendor-specific configuration"""
        
        configs = {
            "galilu": {
                "currency": "PLN",
                "header_row": 0,
                "pivot_format": True,
                "date_columns": []
            },
            "boxnox": {
                "currency": "EUR",
                "header_row": 0,
                "pivot_format": False,
                "date_columns": []
            },
            "skins_sa": {
                "currency": "ZAR",
                "header_row": 0,
                "pivot_format": False,
                "date_columns": ["OrderDate"]
            },
            "cdlc": {
                "currency": "EUR",
                "header_row": 2,
                "pivot_format": False,
                "date_columns": []
            },
            "continuity": {
                "currency": "GBP",
                "header_row": 2,
                "pivot_format": False,
                "date_columns": []
            },
            "ukraine": {
                "currency": "UAH",
                "header_row": 0,
                "pivot_format": True,
                "date_columns": []
            },
            "liberty": {
                "currency": "GBP",
                "header_row": 0,
                "pivot_format": False,
                "date_columns": []
            },
            "skins_nl": {
                "currency": "EUR",
                "header_row": 0,
                "pivot_format": False,
                "date_columns": []
            }
        }
        
        return configs.get(vendor, {
            "currency": "USD",
            "header_row": 0,
            "pivot_format": False,
            "date_columns": []
        })