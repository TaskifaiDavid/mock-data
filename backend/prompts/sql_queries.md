# 📊 20 Essential SQL Queries for CFOs & Company Owners

These queries are built for a sell-out reporting system, helping CFOs and business owners analyze performance by product, reseller, region, and time period. Based on the schema of the `sellout_entries2` table.

---

### 1. Total Sales Per Product
```sql
SELECT functional_name AS product, SUM(sales_eur) AS total_sales
FROM sellout_entries2
GROUP BY product
ORDER BY total_sales DESC;
```

### 2. Monthly Sales Trend by Product
```sql
SELECT year, month, functional_name AS product, SUM(sales_eur) AS total_sales
FROM sellout_entries2
GROUP BY year, month, product
ORDER BY year, month, product;
```

### 3. Sales by Quarter
```sql
SELECT 
  year,
  CASE 
    WHEN month IN (1,2,3) THEN 'Q1'
    WHEN month IN (4,5,6) THEN 'Q2'
    WHEN month IN (7,8,9) THEN 'Q3'
    WHEN month IN (10,11,12) THEN 'Q4'
  END AS quarter,
  SUM(sales_eur) AS total_sales
FROM sellout_entries2
GROUP BY year, quarter
ORDER BY year, quarter;
```

### 4. Top 5 Products by Sales in Last 12 Months
```sql
SELECT functional_name AS product, SUM(sales_eur) AS total_sales
FROM sellout_entries2
WHERE DATE_TRUNC('month', created_at) >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '12 months')
GROUP BY product
ORDER BY total_sales DESC
LIMIT 5;
```

### 5. Year-over-Year Growth by Product
```sql
SELECT 
  functional_name AS product,
  year,
  SUM(sales_eur) AS yearly_sales
FROM sellout_entries2
GROUP BY product, year
ORDER BY product, year;
```

### 6. Average Sales Price per Unit
```sql
SELECT functional_name AS product, 
       SUM(sales_eur) / NULLIF(SUM(quantity), 0) AS avg_price_per_unit
FROM sellout_entries2
GROUP BY product
ORDER BY avg_price_per_unit DESC;
```

### 7. Sales Breakdown by Reseller
```sql
SELECT reseller, SUM(sales_eur) AS total_sales
FROM sellout_entries2
GROUP BY reseller
ORDER BY total_sales DESC;
```

### 8. Monthly Revenue Trend (All Products)
```sql
SELECT year, month, SUM(sales_eur) AS total_sales
FROM sellout_entries2
GROUP BY year, month
ORDER BY year, month;
```

### 9. Product Sales Heatmap
```sql
SELECT functional_name AS product, month, SUM(sales_eur) AS total_sales
FROM sellout_entries2
GROUP BY product, month
ORDER BY product, month;
```

### 10. Products with Declining Sales (3-Month Comparison)
```sql
WITH recent_sales AS (
  SELECT functional_name, 
         DATE_TRUNC('month', created_at) AS period, 
         SUM(sales_eur) AS total_sales
  FROM sellout_entries2
  WHERE created_at >= CURRENT_DATE - INTERVAL '6 months'
  GROUP BY functional_name, period
),
ranked AS (
  SELECT functional_name,
         period,
         total_sales,
         ROW_NUMBER() OVER (PARTITION BY functional_name ORDER BY period DESC) AS rn
  FROM recent_sales
)
SELECT curr.functional_name,
       curr.total_sales AS latest_sales,
       prev.total_sales AS previous_sales
FROM ranked curr
JOIN ranked prev ON curr.functional_name = prev.functional_name AND curr.rn = 1 AND prev.rn = 2
WHERE curr.total_sales < prev.total_sales;
```

---

### 11. Most Sold Products by Quantity
```sql
SELECT functional_name AS product, SUM(quantity) AS total_units_sold
FROM sellout_entries2
GROUP BY product
ORDER BY total_units_sold DESC;
```

### 12. Monthly Average Sales per Product
```sql
SELECT functional_name AS product, 
       AVG(monthly_sales) AS avg_monthly_sales
FROM (
  SELECT year, month, functional_name, SUM(sales_eur) AS monthly_sales
  FROM sellout_entries2
  GROUP BY year, month, functional_name
) AS sub
GROUP BY product;
```

### 13. Returns or Negative Sales Detection
```sql
SELECT *
FROM sellout_entries2
WHERE quantity < 0 OR sales_eur < 0;
```

### 14. High Performing Resellers by Product
```sql
SELECT reseller, functional_name AS product, SUM(sales_eur) AS total_sales
FROM sellout_entries2
GROUP BY reseller, product
ORDER BY product, total_sales DESC;
```

### 15. Most Volatile Products (Price StdDev)
```sql
SELECT functional_name AS product,
       STDDEV(sales_eur / NULLIF(quantity, 0)) AS price_stddev
FROM sellout_entries2
WHERE quantity > 0
GROUP BY product
ORDER BY price_stddev DESC;
```

### 16. Share of Total Revenue by Product
```sql
SELECT functional_name AS product,
       ROUND(SUM(sales_eur) * 100.0 / SUM(SUM(sales_eur)) OVER (), 2) AS percent_of_total
FROM sellout_entries2
GROUP BY product
ORDER BY percent_of_total DESC;
```

### 17. Best Month Ever (Company-Wide)
```sql
SELECT year, month, SUM(sales_eur) AS total_sales
FROM sellout_entries2
GROUP BY year, month
ORDER BY total_sales DESC
LIMIT 1;
```

### 18. Product Launch Performance (First Month Sales)
```sql
SELECT functional_name AS product, MIN(year) AS launch_year, MIN(month) AS launch_month,
       SUM(sales_eur) AS first_month_sales
FROM sellout_entries2
GROUP BY product
ORDER BY first_month_sales DESC;
```

### 19. Products Not Sold in Last 6 Months
```sql
SELECT DISTINCT functional_name AS product
FROM sellout_entries2
WHERE functional_name NOT IN (
  SELECT DISTINCT functional_name
  FROM sellout_entries2
  WHERE created_at >= CURRENT_DATE - INTERVAL '6 months'
);
```

### 20. Quarterly Growth by Product
```sql
WITH product_quarters AS (
  SELECT functional_name,
         year,
         CASE 
           WHEN month IN (1,2,3) THEN 'Q1'
           WHEN month IN (4,5,6) THEN 'Q2'
           WHEN month IN (7,8,9) THEN 'Q3'
           WHEN month IN (10,11,12) THEN 'Q4'
         END AS quarter,
         SUM(sales_eur) AS total_sales
  FROM sellout_entries2
  GROUP BY functional_name, year, quarter
),
ranked AS (
  SELECT *,
         ROW_NUMBER() OVER (PARTITION BY functional_name ORDER BY year, quarter) AS rn
  FROM product_quarters
)
SELECT curr.functional_name, curr.year, curr.quarter, curr.total_sales,
       prev.total_sales AS previous_sales,
       (curr.total_sales - prev.total_sales) AS growth
FROM ranked curr
JOIN ranked prev ON curr.functional_name = prev.functional_name AND curr.rn = prev.rn + 1
ORDER BY curr.functional_name, curr.year, curr.quarter;
```

---

Let me know if you'd like this saved as a downloadable `.md` file or embedded in a dashboard.
