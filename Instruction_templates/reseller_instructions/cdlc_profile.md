# Reseller Profile Template

Use this template to provide structured information about new resellers for system integration.

## Reseller Information

**Reseller Name:** Creme de la Creme  
**Internal Code:** CDLC
**Currency:** EUR

## Detection Rules

### Filename Patterns
- **Primary Pattern:** contains 'BIBBI' in filename (case insensitive)
- **Secondary Pattern:** contains 'Sell_Out' or 'Sell Out' in filename
- **Example Filenames:** 
  - BIBBI_Sell_Out_2025 04.xlsx
  - BIBBI_Sell_Out_2025 05.xlsx

### Sheet/Content Patterns
- **Sheet Names:** Format "YYYY MM" (e.g., "2025 04")
- **Content Identifiers:** Products starting with "BIBBI." in product descriptions
- **File Format:** Excel (.xlsx)

## Data Extraction Rules

### File Structure
- **Header Row:** 3 (0-indexed, where column headers "Qty"/"Sum Eur" are located)
- **Data Starts:** 4 (0-indexed)
- **Skip Rows:** 0-3 (header rows)
- **Pivot Format:** Yes - data is in pivot table format with stores as column groups

### Column Mappings
Map each database field to the source column:

| Database Field | Source Column | Position/Name | Notes |
|---------------|---------------|---------------|-------|
| reseller | Fixed Value | - | Always "BIBBI" |
| product_ean | Column B | Position 1 | 13-digit EAN codes (e.g., 7350154320046) |
| month | Cell B2 or Sheet Name | Extract from "2025 April" or sheet name | Parse month from period indicator |
| year | Cell B2 or Sheet Name | Extract from "2025 April" or sheet name | Parse year from period indicator |
| quantity | Columns D,F,H,J,L | Store-specific Qty columns | Sum across all store locations |
| sales_lc | Columns E,G,I,K,M | Store-specific Sum Eur columns | Sum across all store locations |
| currency | Fixed Value | - | Always "EUR" |
| functional_name | Column C | Position 2 | Product description (e.g., "BIBBI. Swimming Pool EDP 100 ml") |

### Special Processing Rules
- **Date Extraction:** Extract from cell B2 which contains format "YYYY Month" (e.g., "2025 April") or from sheet name "YYYY MM"
- **Data Filtering:** Skip rows where Column B is empty or doesn't contain a valid 13-digit EAN
- **Duplicate Handling:** Aggregate quantities and sales across all store locations for same EAN
- **Value Conversions:** Handle empty cells as 0 for quantities and amounts
- **Product Matching:** EAN is directly provided in Column B, no lookup needed

## Business Rules

### Date Rules
- **Report Period:** Monthly sales data
- **Date Calculation:** Direct extraction from header (B2) or sheet name
- **Filename Date Format:** "YYYY MM" format in filename (e.g., "2025 04" for April 2025)

### Data Quality Rules
- **Required Fields:** EAN (Column B), at least one non-zero quantity or sales value
- **Zero Values:** Include all products even with zero sales in specific stores
- **Negative Values:** Flag for review but include in processing
- **Missing Data:** Skip rows without valid EAN codes

### Processing Notes
- **File Size:** Small files, typically <100 rows
- **Frequency:** Monthly
- **Special Considerations:** 
  - Data is in pivot format with multiple store locations
  - Need to aggregate across all stores (excluding Total column)
  - Store columns: E-shop (D-E), Vilnius Panorama (F-G), Vilnius Akropolis (H-I), Kaunas Akropolis (J-K), LV Riga Spice CdlC (L-M)
  - Ignore Total columns (N-O) as we'll calculate our own

## Sample Data

### Example Filename
```
BIBBI_Sell_Out_2025 04.xlsx
```

### Example Data Structure
```
Row 2: [2025 April] [E-shop header] [Lithuania header] [Latvia header] [Total header]
Row 3: [Store names: Vilnius Panorama, Vilnius Akropolis, Kaunas Akropolis, LV Riga Spice CdlC]
Row 4: [Qty] [Sum Eur] [Qty] [Sum Eur] [Qty] [Sum Eur] [Qty] [Sum Eur] [Qty] [Sum Eur]
Row 5: [7350154320046] [BIBBI. Swimming Pool EDP 100 ml] [] [] [3] [661.50] [2] [490.00] [] [] [1] [245.00]
```

### Expected Output
After processing, data should map to:
```json
{
  "reseller": "BIBBI",
  "product_ean": "7350154320046",
  "month": "4",
  "year": "2025",
  "quantity": "6",
  "sales_lc": "1396.51",
  "currency": "EUR",
  "functional_name": ""
}
```