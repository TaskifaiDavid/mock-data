# Reseller Profile Template

Use this template to provide structured information about new resellers for system integration.

## Reseller Information

**Reseller Name:** Aromateque  
**Internal Code:** aromateque  
**Currency:** EUR

## Detection Rules

### Filename Patterns
- **Primary Pattern:** contains 'bibbi sales' in filename (case insensitive)
- **Secondary Pattern:** have a sheet named 'TDSheet'
- **Example Filenames:** 
  - bibbi sales march'25 
  - bibbi sales march'25 (4)

### Sheet/Content Patterns
- **Sheet Names:** "TDSheet"
- **Content Identifiers:** Rows containing "BIBBI PARFUM"
- **File Format:** Excel (.xlsx)

## Data Extraction Rules

### File Structure
- **Header Row:** 11 (0-indexed, first row [0] contains headers)
- **Data Starts:** 12 (0-indexed)
- **Skip Rows:** 0-11
- **Pivot Format:** No - standard tabular format

### Column Mappings
Map each database field to the source column:

| Database Field | Source Column | Position/Name | Notes |
|---------------|---------------|---------------|-------|
| reseller | Fixed Value | - | Always "Aromateque" |
| product_ean | Lookup Required | - | Must lookup EAN by SKU/name |
| month | From Filename | Extract from filename | Parse month from filename |
| year | From Filename | Extract from filename | Parse year from filename |
| quantity | Column Name | - | Exists under date column - starts row 11 (index 0) |
| sales_lc | Column Name | - | Does not exist|
| currency | Fixed Value | - | Always "EUR" |
| functional_name | Column Name | - | Stores under column B - starts row 12 (index 0) |

### Special Processing Rules
- **Date Extraction:** 
  - Extract month/year from filename patterns
  - Support formats: "march'25"
- **Data Filtering:** 
  - First, check report date - if month for example is March, only look for 01.03.2025 and take the quantity below. then fetch functional_name.
- **Duplicate Handling:** Remove exact duplicates
- **Value Conversions:** 
  - Handle empty cells as 0 for quantities
  - Clean currency symbols from sales values
- **Product Matching:** 

## Business Rules

### Date Rules
- **Report Period:** Monthly sales data
- **Date Calculation:** Extract from filename, no arithmetic needed
- **Filename Date Format:** 
  - Month/Year patterns: "YYYY_MM", "Month YYYY", "MonthYY"

### Data Quality Rules
- **Required Fields:** 
- **Zero Values:** Include products with zero quantities if they have sales
- **Negative Values:** Include negative values (returns/refunds)
- **Missing Data:** 
  - Skip rows without product identifiers
  - Set missing quantities to 0

### Processing Notes
- **File Size:** Medium files, typically 1-50 rows
- **Frequency:** Monthly
- **Special Considerations:** 
  - Only extract rows that has quantity for that month.

## Sample Data

### Example Filename
```
bibbi sales march'25.xslx
```

### Example Data Structure
```
Row 0:  | |01.01.2025 | 01.02.2025 | 01.03.2025 | 01.04.2025 | Total | Total in euro
Row 1: BIBBI PARFUM Boy of June EAU DE PARFUM 100 ML | BBBOJ100 | 2,000 | 4,000 | 2,000 | | 8,000 | €1 960,00
```

### Expected Output
After processing, data should map to:
```json
{
  "reseller": "Aromateque",
  "product_ean": "",
  "month": "3",
  "year": "2025",
  "quantity": "2",
  "sales_lc": "",
  "currency": "EUR",
  "functional_name": "BBBOJ100"
}
```

## Implementation Checklist

- [ ] Detection patterns added to `VendorDetector.detect_vendor()`
- [ ] Vendor config added to `VendorDetector.get_vendor_config()`
- [ ] Cleaning method `_clean_aromateque_data()` created
- [ ] Column mappings implemented
- [ ] Special processing rules coded
- [ ] Date extraction logic implemented
- [ ] Product lookup strategy implemented
- [ ] Testing completed with sample files