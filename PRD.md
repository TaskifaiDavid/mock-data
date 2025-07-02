1.
a lightweight web application that allows authenticated users to log in, upload an Excel (.xlsx) file, and then automatically triggers a backend pipeline to detect, clean, and normalize data before persisting it in Supabase. The front end remains minimal—just a login screen and an upload interface—while all heavy lifting occurs server‑side.

2. Goals and Success Metrics
Goal 1: Enable secure user authentication and file upload.
Goal 2: Implement an intelligent backend pipeline that auto-detects data schemas, identifies dirty fields (e.g., inconsistent dates, malformed emails), and applies cleaning routines.
Goal 3: Persist cleaned, validated records in Supabase to support downstream analytics and reporting.

Success Metrics:
-Upload Success Rate: ≥ 95% of uploaded files are processed without manual intervention.
-Data Quality Improvement: ≥ 90% of identified anomalies automatically corrected.
-Processing Latency: Median end-to-end processing ≤ 5 seconds for files up to 100 rows.

User Satisfaction: Positive feedback score ≥ 4/5 in post-upload survey.

3. User Stories

As a user, I want to securely log in so only authorized individuals can process data.

As a user, I want to upload an Excel file so the system can automatically clean and normalize it.

As a product owner, I want the backend to intelligently detect data issues (e.g., date formats, missing values) and apply standardized cleaning rules.

As a developer, I want a clear, modular pipeline—file ingestion, schema detection, cleaning stages, and database persistence—so I can maintain and extend logic easily.

4. Functional Requirements

-User authentication (email/password or OAuth) with session management.


-Upload interface accepting .xlsx files up to 10 MB.


-Backend ingestion: parse Excel, infer header row and column types.


-Cleaning pipeline: trim whitespace, normalize case, standardize dates, validate formats.


-Anomaly detection: flag missing or out-of-range values, apply default rules or heuristics.


-Backend writes cleaned dataset and logs original-to-clean transformations in Supabase.


-Provide processing status and summary report (rows processed, errors fixed) to the user UI.


-Error handling: surface parsing or validation errors with actionable messages.

-Rate-limit uploads per user (e.g., 5 uploads per minute).


5. Non‑functional Requirements

Performance: Single-file (<100 rows) processing under 5 seconds.

Scalability: Handle up to 50 concurrent users uploading files.

Security: HTTPS, input sanitization, secure file storage, and GDPR compliance.

Maintainability: Modular code with unit tests for each cleaning rule.

Observability: Track ingestion counts, error rates, and processing times in a dashboard.

6. Technical Architecture

Frontend

React (Vite) or vanilla JS hosted on GoDaddy.

Screens: Login, File Upload, Processing Status.

Communicates via authenticated fetch() requests.

Auth & Sessions

Supabase Auth or Auth0 for user login and JWT-based sessions.



Ingestion: Receive file, parse XLSX with xlsx library.

Schema Detection: Infer types (date, number, string) per column.

Cleaning: Apply configured rules (e.g., date parsing, regex validations).

Anomaly Detection: Identify outliers/missing cells and apply heuristics.

Persistence: Bulk insert cleaned rows and transformation logs to Supabase.

Database

Supabase (PostgreSQL) with tables:

-- Raw upload metadata
CREATE TABLE uploads (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id uuid REFERENCES users(id),
  uploaded_at timestamptz DEFAULT now(),
  status text
);

-- Cleaned data storage (dynamic schema or JSONB)
CREATE TABLE cleaned_data (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  upload_id uuid REFERENCES uploads(id),
  row_data jsonb,
  cleaned_at timestamptz DEFAULT now()
);

-- Transformation logs
CREATE TABLE transform_logs (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  upload_id uuid,
  row_index int,
  column_name text,
  original_value text,
  cleaned_value text,
  logged_at timestamptz DEFAULT now()
);

Monitoring & Alerts

Sentry for error tracking.

Grafana dashboards via Prometheus metrics for throughput and latency.

7. Workflow and Data Flow

User logs in and navigates to the upload page.

User selects an .xlsx file and submits.

Frontend sends file via authenticated POST to /api/upload.

Backend:

Preferably python code with pandas for cleaning functionality

Saves file to temporary storage.

Parses and infers schema.

Runs cleaning rules and logs transformations.

Inserts cleaned records and logs into Supabase.

Backend emits a webhook/event for downstream processes (e.g., notifications).

Frontend polls /api/status/{uploadId} to show progress and final summary.

8. Security and Privacy

Enforce HTTPS and secure JWT verification.

Virus-scan or validate file type before parsing.

Limit file size and upload frequency.

Data retention and removal policies to satisfy GDPR.


## 9. Excel Data Extraction & Normalization — *what to pull from every upload*

| **Canonical field<br>(for `cleaned_data.row_data`)** | **Typical header variants** | **How to derive / normalise** | **Example source file(s)** |
| --- | --- | --- | --- |
| `reseller` | *(n/a — taken from file-name or sheet title)* | Regex on file‐name → “Galilu”, “Boxnox”, “Skins SA”, “CDLC”, “Continuity”… | `BIbbi_sellout_Galilu_2025.xlsx`, `BOXNOX – BIBBI Monthly Sales Report APR2025.xlsx` |
| `report_year` | `YEAR`, year in sheet label, or date column | If a per-row date exists → `YEAR(OrderDate)`; else integer year column or sheet title | Boxnox **SELL OUT BY EAN** sheet (`YEAR` col) |
| `report_month` | `MONTH`, month in sheet label, or date column | As above (`MONTH(OrderDate)` or integer month col) | Boxnox (`MONTH` col) |
| `order_date` *(optional)* | `OrderDate`, `Date`, Excel serial | Parse to ISO 8601 (UTC) | Skins SA **BIBBI** |
| `store` / `branch` / `pos` | `Store`, `Branch`, `POS`, pivot-row label | For wide pivot tables this is the first column. Ignore blank/“total” rows. | Galilu monthly sheet |
| `channel` *(optional)* | `CHANNEL` | Copy as-is | Boxnox |
| `ean` | `EAN`, `EANCode`, `Código de barras`, `StockCode` | Strip spaces, zero-pad to 13 digits | Boxnox, Skins SA |
| `sku` | `SKU`, `Referencia interna`, `Supplier Reference` | Upper-case; trim | Boxnox, Continuity |
| `product_name` | `Description`, `StockDescription`, `Article`, `Item` | Title Case; collapse spaces | Boxnox, Skins SA, BIBBIPARFU |
| `quantity` | `Qty`, `QTY`, `OrderQty`, `SalesQuantity`, `Sales Qty Un` | Float; drop rows with 0/NaN | Boxnox, Skins SA, Continuity |
| `gross_value` *(incl. VAT)* | `AMOUNT`, `SalesAmount`, `Sales Inc VAT £` | Numeric; currency determined below | Boxnox (`AMOUNT`) |
| `net_value` *(ex. VAT)* | `ExVatNetsales`, `NetSalesValue`, `SalesAmount` | Numeric | Skins SA (`ExVatNetsales`) |
| `currency` | explicit column or label row | • If column present use ISO-4217 code • Else defaults:<br>  – Galilu → PLN<br>  – Boxnox → EUR<br>  – Skins SA → ZAR<br>  – CDLC → EUR | Galilu row 3 “value in PLN” |
| `brand` / `category` *(optional)* | `BRAND`, `Brand`, `CATEGORY` | Copy if present (currently always “BIBBI”) | Skins SA |

---

### 9.1 Header detection & dynamic mapping

1. **Scan first 10 rows** of each sheet until a row contains ≥ 2 known header keywords (see table).  
2. If none found, treat sheet as **wide pivot**:  
   * first non-blank column → `store`  
   * subsequent columns whose labels match month names (`jan`–`dec`) or ISO dates become `report_month`  
3. “Unnamed” columns are discarded unless their second row contains a header keyword.

---

### 9.2 Row-level cleaning rules

* Skip rows where `store` **or** `product_name` ∈ {`TOTAL`, `Sub Total`, NaN}.  
* Coerce `ean` to 13-digit string (`zfill(13)`), trim `sku` and `product_name`.  
* Convert Excel numeric dates → ISO `YYYY-MM-DD`.  
* **Unpivot wide sheets** (`pd.melt`) so each month cell becomes its own row with either `quantity` **or** `gross_value`:  
  * If sheet label contains “value” → cell → `gross_value`, set `quantity` = NaN.  
  * Else cell → `quantity`, set `gross_value` = NaN.  

---

### 9.3 Vendor-specific quirks

| Vendor / file pattern | Sheet(s) | Notes |
| --- | --- | --- |
| **Galilu** (`*_Galilu_*`) | `monthly sellout` | Values in PLN; unpivot months; no per-EAN detail. |
| **Boxnox** (`BOXNOX*`) | `SELL OUT BY EAN` | Already tidy; keep `YEAR`, `MONTH`, `CHANNEL`, `POS`, `EAN`, `QTY`, `AMOUNT`, `SKU`. |
| **Skins SA** (`Skins SA*`) | `BIBBI` | One row per sale; extract `OrderDate`, `Branch`, `StockCode`→`ean`, `OrderQty`, `NetSalesValue`, `ExVatNetsales`, `MONTH`, `YEAR`. |
| **CDLC** (`CDLC*`) | *first sheet* | Header row at line 3 (“Qty” / “Sum Eur”); blank qty cells = 0. |
| **Continuity** (`Continuity*`) | `Sales By Size` | Use header row 3; map `Item`, `Supplier Reference`→`sku`, `Sales Qty Un`→`quantity`, `Sales Inc VAT £`→`gross_value`. |
| **Ukraine TDSheet** (`bibbi sales*`) | `TDSheet` | First data row label = `Store`; month columns are Excel dates; unpivot as quantity. |

---

### 9.4 Post-processing & persistence

1. Populate `upload_id`, `uploader_user_id`, `file_source`.  
2. Bulk-insert rows into **`cleaned_data`**; log raw↔clean pairs in **`transform_logs`**.  
3. Return a `processing_summary` to UI (rows processed, skipped, anomalies fixed).

