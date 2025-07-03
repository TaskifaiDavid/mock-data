# BOXNOX Reseller Profile (Example)

This is an example of how to fill out the reseller template using BOXNOX data.

## Reseller Information

**Reseller Name:** BOXNOX
**Internal Code:** boxnox
**Currency:** EUR

## Detection Rules

### Filename Patterns
- **Primary Pattern:** Contains "boxnox" in filename (case insensitive)
- **Secondary Pattern:** Contains "sell out by ean" in sheet names
- **Example Filenames:** 
  - boxnox_sales_report_2025.xlsx
  - BOXNOX_sellout_data.xlsx

### Sheet/Content Patterns
- **Sheet Names:** "Sell Out By EAN", "Sales Data"
- **Content Identifiers:** Column headers include "EAN", "QTY", "AMOUNT"
- **File Format:** Excel

## Data Extraction Rules

### File Structure
- **Header Row:** 0 (first row contains headers)
- **Data Starts:** 1 (second row)
- **Skip Rows:** None
- **Pivot Format:** No (flat table format)

### Column Mappings

| Database Field | Source Column | Position/Name | Notes |
|---------------|---------------|---------------|-------|
| reseller | Fixed Value | - | Always "BOXNOX" |
| product_ean | Direct Column | "EAN" | EAN provided directly |
| month | Direct Column | "MONTH" | Month number (1-12) |
| year | Direct Column | "YEAR" | Year (YYYY) |
| quantity | Direct Column | "QTY" | Sales quantity |
| sales_lc | Direct Column | "AMOUNT" | Sales value in EUR |
| currency | Fixed Value | - | Always "EUR" |
| functional_name | Direct Column | "SKU" | Product SKU/identifier |

### Special Processing Rules
- **Date Extraction:** Month and year provided in separate columns
- **Data Filtering:** No special filtering needed
- **Duplicate Handling:** No duplicates expected
- **Value Conversions:** Numbers may need string-to-numeric conversion
- **Product Matching:** EAN provided directly, no lookup needed

## Business Rules

### Date Rules
- **Report Period:** Monthly sales data
- **Date Calculation:** None needed, month/year in data
- **Filename Date Format:** Not used for date extraction

### Data Quality Rules
- **Required Fields:** EAN, QTY, AMOUNT, MONTH, YEAR
- **Zero Values:** Include zero quantities if amount > 0
- **Negative Values:** Include (returns/refunds)
- **Missing Data:** Skip rows with missing EAN

### Processing Notes
- **File Size:** Typically 1000-5000 rows
- **Frequency:** Monthly
- **Special Considerations:** Clean, structured data with minimal processing needed

## Sample Data

### Example Filename
```
boxnox_sellout_march_2025.xlsx
```

### Example Data Structure
```
Row 1: YEAR | MONTH | CHANNEL | POS | EAN | QTY | AMOUNT | SKU
Row 2: 2025 | 3 | Retail | Store1 | 1234567890123 | 10 | 150.00 | SKU001
Row 3: 2025 | 3 | Online | Web | 1234567890124 | 5 | 75.50 | SKU002
```

### Expected Output
After processing, data should map to:
```json
{
  "reseller": "BOXNOX",
  "product_ean": "1234567890123",
  "month": 3,
  "year": 2025,
  "quantity": 10,
  "sales_lc": "150.00",
  "currency": "EUR",
  "functional_name": "SKU001"
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