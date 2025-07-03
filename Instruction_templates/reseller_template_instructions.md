# How to Use the Reseller Template

## Quick Start Guide

1. **Copy the template** (`reseller_template.md`) for your new reseller
2. **Fill out each section** with reseller-specific information
3. **Provide sample files** or data structure examples
4. **Submit the completed template** for implementation

## Key Information Needed

### Most Important Fields
- **Filename patterns** - How to detect this reseller's files
- **Column mappings** - Where to find each required field
- **Date extraction** - How to get month/year
- **Special rules** - Any unique processing requirements

### Sample Data Requirements
- **Example filename** - Actual filename format
- **Column headers** - First row of data showing structure
- **3-5 sample rows** - Real data examples (anonymized if needed)

## Common Patterns

### Simple Resellers (like BOXNOX)
- Clean column headers
- Direct field mapping
- No special processing needed
- Month/year in separate columns

### Complex Resellers (like Liberty)
- Fixed column positions (A, B, C... or 1, 2, 3...)
- Date extraction from filename
- Special business rules (like "bottom of pairs")
- Product lookup required

## Template Sections Explained

### Detection Rules
**Why needed:** System must automatically identify reseller from filename/content
**What to provide:** 
- Filename patterns (contains "skins", ends with "_report.xlsx")
- Sheet names for Excel files
- Unique text that appears in the data

### Column Mappings
**Why needed:** System must know where to find each database field
**What to provide:**
- Column names (if headers exist): "Product Code", "Sales Qty"
- Column positions (if no headers): "Column A", "Column 5"
- Fixed values: "Always EUR", "Always this_reseller_name"

### Special Processing Rules
**Why needed:** Each reseller has unique data quirks
**Common examples:**
- Skip total rows
- Extract date from filename
- Handle duplicate entries
- Convert pivot table format
- Product name cleanup

## Example Workflows

### Workflow 1: Simple CSV Reseller
```
1. Files named: retailer_sales_YYYY-MM.csv
2. Headers: Date, Product, SKU, Quantity, Value
3. Currency: Always USD
4. Processing: Direct mapping, no special rules
```

### Workflow 2: Complex Excel Reseller  
```
1. Files named: Monthly_Report_DD-MM-YYYY.xlsx
2. Data in Column A=Product, Column F=Qty, Column G=Sales
3. Skip first 3 rows, extract date from filename
4. Handle merged cells and totals
```

## Getting Help

If you're unsure about any section:
1. **Look at existing examples** (boxnox_example.md, Liberty_instructions.md)
2. **Provide best guess** - I can clarify unclear parts
3. **Include sample file** - I can analyze the structure
4. **Ask specific questions** - "How do I handle this column layout?"

## Next Steps After Template

Once you submit a completed template, I will:
1. **Review the information** and ask clarifying questions
2. **Implement the detection logic** in `VendorDetector`
3. **Create the cleaning method** in `DataCleaner`
4. **Add vendor configuration** 
5. **Test with sample data** if provided
6. **Confirm implementation** is working correctly

## Quality Checklist

Before submitting, ensure you have:
- [ ] Reseller name and internal code
- [ ] At least one filename pattern
- [ ] Column mapping for all required fields
- [ ] Currency information
- [ ] Date extraction method
- [ ] Sample data structure
- [ ] Any special processing rules noted