# Skins NL Reseller Profile


## Reseller Information

**Reseller Name:** Skins SA
**Internal Code:** skins_sa
**Currency:** ZAR

## Detection Rules

### Filename Patterns
- **Primary Pattern:** Contains "Skins SA" in filename (case insensitive)
- **Secondary Pattern:** Contains "BIBBI" in sheet names
- **Example Filenames:** 
  - Skins SA BIBBI CY 2025 February
  - Skins SA BIBBI CY 2025 April

### Sheet/Content Patterns
- **Sheet Names:** "BIBBI", "sales summary"
- **Content Identifiers:** Column headers include "Branch", "OrderDate", "StockCode", "OrderQty", "StockDescription", "NetSalesValue", " ExVatNetsales", "MONTH", "YEAR", "STATUS", "SUPPLIER", "CATEGORY", "BRAND", "ABC MAP"
- **File Format:** Excel

## Data Extraction Rules

### File Structure
- **Header Row:** 0 (first row contains headers)
- **Data Starts:** 1 (second row)
- **Skip Rows:** That has no "StockCode" value.
- **Pivot Format:** No (flat table format)

### Column Mappings

| Database Field | Source Column | Position/Name | Notes |
|---------------|---------------|---------------|-------|
| reseller | Fixed Value | - | Always "Skins SA" |
| product_ean | Direct Column | "StockCode" | EAN provided directly |
| month | Found in filename | "MONTH" | Month number (1-12) |
| year | Found in filename  | "YEAR" | Year (YYYY) |
| quantity | Direct Column | "OrderQty" | Sales quantity |
| sales_lc | Direct Column | " ExVatNetsales" | Sales value in EUR |
| currency | Fixed Value | - | Always "ZAR" |
| functional_name | Does not exist | - | Product SKU/identifier not available |

### Special Processing Rules
- **Date Extraction:** Month and year found in filename.
- **Data Filtering:** Only extract from rows with matching month/year from extracted from filename. Similar logic to Skins NL.
- **Duplicate Handling:** there will be alot of duplicates, extract them all as long as the month/year match from filename.
- **Value Conversions:** Numbers may need string-to-numeric conversion
- **Product Matching:** EAN provided directly, no lookup needed

## Business Rules

### Date Rules
- **Report Period:** Monthly sales data
- **Date Calculation:** None needed, month/year in filename
- **Filename Date Format:** 02-2025 | named: FEB 2025

### Data Quality Rules
- **Required Fields:** StockCode, OrderQty,  ExVatNetsales, MONTH, YEAR
- **Zero Values:** Include zero quantities if amount > 0
- **Negative Values:** Include (returns/refunds)
- **Missing Data:** Skip rows with missing SalesQuantity / Quantity

### Processing Notes
- **File Size:** Typically 150-500
- **Frequency:** Monthly
- **Special Considerations:** Clean, structured data with minimal processing needed

## Sample Data

### Example Filename
```
Skins SA BIBBI CY 2025 February.xlsx
```

### Example Data Structure
```
Row 1: Branch | OrderDate | StockCode | OrderQty | StockDescription | NetSalesValue  |  ExVatNetsales | MONTH | YEAR | STATUS | SUPPLIER | CATEGORY | BRAND | ABC MAP
Row 2: SKINS GATEWAY | 1/28/2024 | 7350154320060 | 1 | Bibbi Boy of June EDP 100ml | 5920  |    5 147,83  | 1 | 2024 | ACTIVE | SKINS NETHERLANDS | FRAGRANCE | BIBBI | D
Row 3: SKINS GATEWAY | 1/26/2024 | 7350154320060 | 1 | Bibbi Boy of June EDP 100ml | 5920  |    5 147,83  | 1 | 2024 | ACTIVE | SKINS NETHERLANDS | FRAGRANCE | BIBBI | D
```

### Expected Output
After processing, data should map to:
```json
{
  "reseller": "Skins SA",
  "product_ean": "7350154320060",
  "month": 1,
  "year": 2024,
  "quantity": 1,
  "sales_lc": "  5 147,83",
  "currency": "ZAR",
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