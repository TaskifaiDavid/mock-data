# Reseller Profile Template

Use this template to provide structured information about new resellers for system integration.

## Reseller Information

**Reseller Name:** Galilu
**Internal Code:** Galilu
**Currency:** PLY

## Detection Rules

### Filename Patterns
- **Primary Pattern:** [e.g., "contains 'Galilu' in filename"]
- **Secondary Pattern:** [e.g., "contains 'product ranking_' in sheet names"]
- **Example Filenames:** 
  - BIbbi_sellout_Galilu_2025

### Sheet/Content Patterns
- **Sheet Names:** YoY, monthly sellout, product_ranking_2025, product_ranking_2023-24, Split_by_store_2025. You going to fetch data from product_ranking_2025
- **Content Identifiers:** 
- **File Format:** Excel - *.xlsx

## Data Extraction Rules

### File Structure
- **Header Row:** 0
- **Data Starts:** 1
- **Skip Rows:**
- **Pivot Format:** No

### Column Mappings
Map each database field to the source column:

| Database Field | Source Column | Position/Name | Notes |
|---------------|---------------|---------------|-------|
| reseller | [Fixed value] | - | Always "[Galilu]" |
| product_ean | Not available |  | |
| month | Column header left of column "Total" | - | Always new due to variable column. Find the total column and take the column header next to that |
| year | Column A | Cell A1 | How to extract year |
| quantity | Check same column as month and go down the list | [For example, if May were the report month, you should go to column F since its left of total and  the 5th month (6th column since total is before) | Sales quantity |
| sales_lc | not available | [e.g., "AMOUNT" or "Column V"] | Sales value local currency |
| currency | not available | [Value/Position] | Currency code |
| functional_name | not available | [e.g., "SKU" or "Column F"] | Product identifier |

### Special Processing Rules
- **Date Extraction:** Find the month row besides total and go down to column. (qt)
- **Data Filtering:** Skip to column that are not next to "Total"
- **Duplicate Handling:** 
- **Value Conversions:** [Any special formatting for numbers/dates]
- **Product Matching:** Column A got description. And that converstion should be done with a switch pattern.

## Business Rules

### Date Rules
- **Report Period:** month
- **Date Calculation:** 
- **Filename Date Format:** No date in filename, just year.

### Data Quality Rules
- **Required Fields:** Column A
- **Zero Values:** Dont add
- **Negative Values:** take negative values
- **Missing Data:** pass

### Processing Notes
- **File Size:** 1-50 rows
- **Frequency:** monthly
- **Special Considerations:** 

## Sample Data

### Example Filename
```
BIbbi_sellout_Galilu_2025.xlsx
```

### Example Data Structure
```
[Provide sample rows showing column layout]
Row 1: 2025 | Jan | Feb | Mar | Apr | May | Total
Row 2: Bibbi Parfum Discovery Set 5 x 2 ml | 11 | 7 | 12 | 2 | 11 | 43
Row 3: BIRTH COUNTRY świeca zapachowa 310 g | 1 | - | 1 | 2 | - | 4
...
```

### Expected Output
After processing, data should map to:
```json
{
  "reseller": "Galilu,
  "product_ean": "",
  "month": "5",
  "year": "2025",
  "quantity": "11",
  "sales_lc": "",
  "currency": "",
  "functional_name": "Bibbi Parfum Discovery Set 5 x 2 ml"
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

