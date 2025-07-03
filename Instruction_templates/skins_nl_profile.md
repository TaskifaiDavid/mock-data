# Skins NL Reseller Profile


## Reseller Information

**Reseller Name:** Skins NL
**Internal Code:** skins_nl
**Currency:** EUR

## Detection Rules

### Filename Patterns
- **Primary Pattern:** Contains "BIBBIPARFU" in filename (case insensitive)
- **Secondary Pattern:** Contains "SalesPerSKU" in sheet names
- **Example Filenames:** 
  - BIBBIPARFU_ReportPeriod02-2025.xlsx
  - BIBBIPARFU_ReportPeriod05-2025.xlsx

### Sheet/Content Patterns
- **Sheet Names:** "SalesPerSKU", "Sales Data"
- **Content Identifiers:** Column headers include "EANCode", "SalesQuantity", "SalesAmount"
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
| reseller | Fixed Value | - | Always "Skins NL" |
| product_ean | Direct Column | "EANCode" | EAN provided directly |
| month | Found in filename | - | Month number (1-12) |
| year | Found in filename  | - | Year (YYYY) |
| quantity | Direct Column | "SalesQuantity" | Sales quantity |
| sales_lc | Direct Column | "SalesAmount" | Sales value in EUR |
| currency | Fixed Value | - | Always "EUR" |
| functional_name | Does not exist | - | Product SKU/identifier |

### Special Processing Rules
- **Date Extraction:** Month and year found in filename.
- **Data Filtering:** No special filtering needed
- **Duplicate Handling:** No duplicates expected
- **Value Conversions:** Numbers may need string-to-numeric conversion
- **Product Matching:** EAN provided directly, no lookup needed

## Business Rules

### Date Rules
- **Report Period:** Monthly sales data
- **Date Calculation:** None needed, month/year in filename
- **Filename Date Format:** 02-2025

### Data Quality Rules
- **Required Fields:** EAN, QTY, AMOUNT, MONTH, YEAR
- **Zero Values:** Include zero quantities if amount > 0
- **Negative Values:** Include (returns/refunds)
- **Missing Data:** Skip rows with missing SalesQuantity / Quantity

### Processing Notes
- **File Size:** Typically 1-50 rows
- **Frequency:** Monthly
- **Special Considerations:** Clean, structured data with minimal processing needed

## Sample Data

### Example Filename
```
BIBBIPARFU_ReportPeriod02-2025.xlsx
```

### Example Data Structure
```
Row 1: Brand | Article | EANCode | Sales amount | SalesAmountSPLY | SalesAmountVariance  | SalesQuantity | SalesQuantitySPLY | SalesQuantityVariance
Row 2: BIBBIPARFU | 131362 - Tester Radio Child EDP 100ml | 7350154320497 |  | € 142 |  |  | 2 | 
Row 3: BIBBIPARFU | 1131381 - Tester Santal Beauty EDP 100ml | 7350154320459 | € 116 | € 142 | −18,1% | 2 | 2 | 0,0%
```

### Expected Output
After processing, data should map to:
```json
{
  "reseller": "Skins NL",
  "product_ean": "7350154320459",
  "month": 2,
  "year": 2025,
  "quantity": 2,
  "sales_lc": "116",
  "currency": "EUR",
  "functional_name": ""
}
```

## Implementation Status ✅

Skins NL implementation is now complete in the system:

- [x] Detection patterns added to `VendorDetector.detect_vendor()` (filename: "bibbiparfu", sheet: "salespersku")
- [x] Vendor config added to `VendorDetector.get_vendor_config()` (EUR currency, header_row=0)
- [x] Cleaning method `_clean_skins_nl_data()` created with full column mapping
- [x] Column mappings implemented (EANCode→ean, SalesQuantity→quantity, SalesAmount→sales_lc)
- [x] Special processing rules coded (EUR currency cleaning, empty SalesQuantity filtering)
- [x] Date extraction logic implemented (ReportPeriodMM-YYYY pattern from filename)
- [x] Product lookup strategy implemented (EAN provided directly, functional_name set to empty)
- [x] Testing completed with sample data - all transformations working correctly