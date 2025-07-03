# Reseller Profile Template

Use this template to provide structured information about new resellers for system integration.

## Reseller Information

**Reseller Name:** [Enter reseller name]
**Internal Code:** [Enter short code used in system, e.g., "boxnox", "liberty"]
**Currency:** [Enter currency code, e.g., "GBP", "EUR", "USD"]

## Detection Rules

### Filename Patterns
- **Primary Pattern:** [e.g., "contains 'boxnox' in filename"]
- **Secondary Pattern:** [e.g., "contains 'sell out by ean' in sheet names"]
- **Example Filenames:** 
  - [Example 1]
  - [Example 2]

### Sheet/Content Patterns
- **Sheet Names:** [List expected sheet names if Excel]
- **Content Identifiers:** [Unique text patterns that identify this reseller's data]
- **File Format:** [Excel/CSV/Other]

## Data Extraction Rules

### File Structure
- **Header Row:** [Row number where headers start, 0-indexed]
- **Data Starts:** [Row number where data begins]
- **Skip Rows:** [Any rows to skip at beginning]
- **Pivot Format:** [Yes/No - is data in pivot table format with months as columns?]

### Column Mappings
Map each database field to the source column:

| Database Field | Source Column | Position/Name | Notes |
|---------------|---------------|---------------|-------|
| reseller | [Fixed Value] | - | Always "[reseller_name]" |
| product_ean | [Lookup Strategy] | - | How to get EAN (lookup by SKU/name/etc) |
| month | [Column/Filename] | [Position/Pattern] | How to extract month |
| year | [Column/Filename] | [Position/Pattern] | How to extract year |
| quantity | [Column Name/Position] | [e.g., "QTY" or "Column U"] | Sales quantity |
| sales_lc | [Column Name/Position] | [e.g., "AMOUNT" or "Column V"] | Sales value local currency |
| currency | [Fixed/Column] | [Value/Position] | Currency code |
| functional_name | [Column Name/Position] | [e.g., "SKU" or "Column F"] | Product identifier |

### Special Processing Rules
- **Date Extraction:** [How to get month/year from filename or data]
- **Data Filtering:** [Any rows to skip - totals, headers, etc.]
- **Duplicate Handling:** [How to handle duplicate entries]
- **Value Conversions:** [Any special formatting for numbers/dates]
- **Product Matching:** [How to match products to get EAN]

## Business Rules

### Date Rules
- **Report Period:** [What period does the data represent?]
- **Date Calculation:** [Any date arithmetic needed? e.g., Liberty's -1 week rule]
- **Filename Date Format:** [Pattern for dates in filenames]

### Data Quality Rules
- **Required Fields:** [Which fields must have values]
- **Zero Values:** [How to handle zero quantities/sales]
- **Negative Values:** [How to handle negative values]
- **Missing Data:** [How to handle missing product names/codes]

### Processing Notes
- **File Size:** [Typical file sizes and row counts]
- **Frequency:** [How often files are received]
- **Special Considerations:** [Any unique aspects of this reseller's data]

## Sample Data

### Example Filename
```
[Provide actual filename example]
```

### Example Data Structure
```
[Provide sample rows showing column layout]
Row 1: [Header row if applicable]
Row 2: [First data row]
Row 3: [Second data row]
...
```

### Expected Output
After processing, data should map to:
```json
{
  "reseller": "[reseller_name]",
  "product_ean": "[13-digit EAN]",
  "month": "[1-12]",
  "year": "[YYYY]",
  "quantity": "[number]",
  "sales_lc": "[decimal]",
  "currency": "[currency_code]",
  "functional_name": "[product_identifier]"
}
```

## Implementation Checklist

- [ ] Detection patterns added to `VendorDetector.detect_vendor()`
- [ ] Vendor config added to `VendorDetector.get_vendor_config()`
- [ ] Cleaning method `_clean_[reseller]_data()` created
- [ ] Column mappings implemented
- [ ] Special processing rules coded
- [ ] Date extraction logic implemented
- [ ] Product lookup strategy implemented
- [ ] Testing completed with sample files