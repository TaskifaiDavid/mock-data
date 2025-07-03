# BOXNOX Reseller Profile (Example)

This is an example of how to fill out the reseller template using BOXNOX data.

## Reseller Information

**Reseller Name:** BOXNOX
**Internal Code:** boxnox
**Currency:** EUR

## Detection Rules

### Filename Patterns
- **Primary Pattern:** Contains "boxnox" in filename (case insensitive)
- **Secondary Pattern:** Contains "SELL OUT BY EAN" in sheet names
- **Example Filenames:** 
  - BOXNOX - BIBBI Monthly Sales Report APR2025
  - BOXNOX - BIBBI Monthly Sales Report JAN2025

### Sheet/Content Patterns
- **Sheet Names:** "SELL OUT BY EAN", "Sales Data"
- **Content Identifiers:** Column headers include "EAN", "QTY", "AMOUNT"
- **File Format:** Excel

## Data Extraction Rules

### File Structure
- **Header Row:** 0 (first row contains headers)
- **Data Starts:** 1 (second row)
- **Skip Rows:** Skip rows that is not for current month.
- **Pivot Format:** No (flat table format)

### Column Mappings

| Database Field | Source Column | Position/Name | Notes |
|---------------|---------------|---------------|-------|
| reseller | Fixed Value | - | Always "Boxnox" |
| product_ean | Direct Column | "EAN" | EAN provided directly |
| month | Direct Column | "MONTH" | Month number (1-12) |
| year | Direct Column | "YEAR" | Year (YYYY) |
| quantity | Direct Column | "QTY" | Sales quantity |
| sales_lc | Direct Column | "AMOUNT" | Sales value in EUR |
| currency | Fixed Value | - | Always "EUR" |
| functional_name | Direct Column | "SKU" | Product SKU/identifier |

### Special Processing Rules
- **Date Extraction:** Month and year provided in separate columns
- **Data Filtering:** If the report is for APR2025 - it should only look for MONTH:4 YEAR:2025
- **Duplicate Handling:** No duplicates expected
- **Value Conversions:** Numbers may need string-to-numeric conversion
- **Product Matching:** EAN provided directly, no lookup needed

## Business Rules

### Date Rules
- **Report Period:** Monthly sales data
- **Date Calculation:** None needed, month/year in filename
- **Filename Date Format:** APR2025 = APRIL 2025 = MONTH:4 YEAR:2025

### Data Quality Rules
- **Required Fields:** EAN, QTY, AMOUNT, MONTH, YEAR, SKU
- **Zero Values:** Include zero quantities if amount > 0
- **Negative Values:** Include (returns/refunds)
- **Missing Data:** Skip rows with missing EAN

### Processing Notes
- **File Size:** Typically 150-400
- **Frequency:** Monthly
- **Special Considerations:** Clean, structured data with minimal processing needed

## Sample Data

### Example Filename
```
BOXNOX - BIBBI Monthly Sales Report APR2025
```

### Example Data Structure
```
Row 1: YEAR | MONTH | CHANNEL | POS | EAN | QTY | AMOUNT | DESCRIPTION | SKU
Row 2: 2024 | 1 | Retail | Abanuc Online | 7350154320008 | 1 | 202,48 | EDP SOAP CLUB | BBSC100
Row 3: 2024 | 1 | Retail | Abanuc Online | 7350154320022 | 1 | 202,48 | EDP GHOST OF TOM  | BBGOT100
```

### Expected Output
After processing, data should map to:
```json
{
  "reseller": "Boxnox",
  "product_ean": "7350154320008",
  "month": 1,
  "year": 2024,
  "quantity": 1,
  "sales_lc": "202,48",
  "currency": "EUR",
  "functional_name": "BBSC100"
}
```

## Implementation Status ✅

This example shows how BOXNOX is already implemented in the system:

- [x] Detection patterns added to `VendorDetector.detect_vendor()` (line 14)
- [x] Vendor config added to `VendorDetector.get_vendor_config()` (lines 48-53)
- [x] Cleaning method `_clean_boxnox_data()` created (lines 66-84)
- [x] Column mappings implemented (lines 70-80)
- [x] Special processing rules coded (minimal processing needed)
- [x] Date extraction logic implemented (direct from columns)
- [x] Product lookup strategy implemented (EAN provided directly)
- [x] Testing completed with sample files