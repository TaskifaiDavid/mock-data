INFO:     127.0.0.1:43744 - "OPTIONS /api/upload/ HTTP/1.1" 200 OK
2025-07-07 00:07:58,480 - app.api.auth - INFO - get_current_user called
2025-07-07 00:07:58,480 - app.api.auth - INFO - Authorization header: Bearer eyJhbGciOiJIUzI1NiIsImtpZCI6InJMelFCZWp1WXZ...
2025-07-07 00:07:58,480 - app.api.auth - INFO - Extracted token length: 722
2025-07-07 00:07:58,480 - app.services.auth_service - INFO - Attempting token verification for token starting with: eyJhbGciOiJIUzI1NiIs...
2025-07-07 00:07:58,719 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/auth/v1/user "HTTP/2 200 OK"
2025-07-07 00:07:58,720 - app.services.auth_service - INFO - Token verification successful for user: user@email.com
2025-07-07 00:07:58,720 - app.api.auth - INFO - Successfully authenticated user: user@email.com
2025-07-07 00:07:58,910 - watchfiles.main - INFO - 1 change detected
2025-07-07 00:07:58,959 - httpx - INFO - HTTP Request: POST https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/uploads "HTTP/2 201 Created"
INFO:     127.0.0.1:43744 - "POST /api/upload/ HTTP/1.1" 200 OK
2025-07-07 00:07:58,962 - app.services.cleaning_service - INFO - Starting background task for upload f11e7bea-807d-4d59-9760-8bd36a0b6485, filename: BIbbi_sellout_Galilu_2025.xlsx, user: 26d3c1b7-d944-42a0-9336-e68b1b32ebbf
2025-07-07 00:07:59,071 - httpx - INFO - HTTP Request: PATCH https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/uploads?id=eq.f11e7bea-807d-4d59-9760-8bd36a0b6485 "HTTP/2 200 OK"
2025-07-07 00:07:59,073 - app.services.cleaning_service - INFO - Updated upload f11e7bea-807d-4d59-9760-8bd36a0b6485 status to PROCESSING
2025-07-07 00:07:59,169 - app.services.cleaning_service - INFO - Excel file sheet names: ['YoY', 'monthly sellout', 'product ranking_2025', 'product ranking_2023-24', 'Split_by_store_2025']
2025-07-07 00:07:59,169 - app.services.cleaning_service - INFO - Detected vendor from filename and sheet names: galilu
2025-07-07 00:07:59,169 - app.services.cleaning_service - INFO - Available sheets: ['YoY', 'monthly sellout', 'product ranking_2025', 'product ranking_2023-24', 'Split_by_store_2025']
2025-07-07 00:07:59,169 - app.services.cleaning_service - INFO - Default sheet selection: 'YoY' (first sheet)
2025-07-07 00:07:59,169 - app.services.cleaning_service - INFO - Processing Galilu - looking for 'product_ranking_2025' sheet
2025-07-07 00:07:59,169 - app.services.cleaning_service - INFO - Checking each sheet for Galilu pattern:
2025-07-07 00:07:59,169 - app.services.cleaning_service - INFO -   Sheet 0: 'YoY' - contains 'product_ranking_2025'? False
2025-07-07 00:07:59,169 - app.services.cleaning_service - INFO -   Sheet 1: 'monthly sellout' - contains 'product_ranking_2025'? False
2025-07-07 00:07:59,169 - app.services.cleaning_service - INFO -   Sheet 2: 'product ranking_2025' - contains 'product_ranking_2025'? False
2025-07-07 00:07:59,169 - app.services.cleaning_service - INFO -   Sheet 3: 'product ranking_2023-24' - contains 'product_ranking_2025'? False
2025-07-07 00:07:59,169 - app.services.cleaning_service - INFO -   Sheet 4: 'Split_by_store_2025' - contains 'product_ranking_2025'? False
2025-07-07 00:07:59,169 - app.services.cleaning_service - INFO - Galilu product_ranking_2025 matching sheets: []
2025-07-07 00:07:59,169 - app.services.cleaning_service - WARNING - ⚠️ No 'product_ranking_2025' sheet found for Galilu, using default: 'YoY'
2025-07-07 00:07:59,169 - app.services.cleaning_service - INFO - 🔄 Found alternative Galilu sheet with pattern 'ranking_2025': 'product ranking_2025'
/home/david/.local/lib/python3.10/site-packages/openpyxl/worksheet/_reader.py:329: UserWarning: Unknown extension is not supported and will be removed
  warn(msg)
/home/david/.local/lib/python3.10/site-packages/openpyxl/worksheet/_reader.py:329: UserWarning: Conditional Formatting extension is not supported and will be removed
  warn(msg)
2025-07-07 00:07:59,172 - app.services.cleaning_service - INFO - Loaded Excel sheet 'product ranking_2025' with 26 rows, columns: [2025, 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Total']
2025-07-07 00:07:59,173 - app.services.cleaning_service - INFO - First 3 rows preview: [{2025: 'Bibbi Parfum Discovery Set 5 x 2 ml ', 'Jan': 11.0, 'Feb': 7.0, 'Mar': 12.0, 'Apr': 2.0, 'May': 11.0, 'Total': 43}, {2025: 'BIRTH COUNTRY świeca zapachowa 310 g', 'Jan': 1.0, 'Feb': nan, 'Mar': 1.0, 'Apr': 2.0, 'May': nan, 'Total': 4}, {2025: 'Boy of June EDP 100ML', 'Jan': 3.0, 'Feb': 2.0, 'Mar': 2.0, 'Apr': 2.0, 'May': 1.0, 'Total': 10}]
2025-07-07 00:07:59,174 - app.services.cleaning_service - INFO - Data types: {2025: dtype('O'), 'Jan': dtype('float64'), 'Feb': dtype('float64'), 'Mar': dtype('float64'), 'Apr': dtype('float64'), 'May': dtype('float64'), 'Total': dtype('int64')}
2025-07-07 00:07:59,174 - app.services.cleaning_service - INFO - Column data distribution:
2025-07-07 00:07:59,174 - app.services.cleaning_service - INFO -   2025: 26/26 non-empty values
2025-07-07 00:07:59,174 - app.services.cleaning_service - INFO -   Jan: 20/26 non-empty values
2025-07-07 00:07:59,174 - app.services.cleaning_service - INFO -   Feb: 20/26 non-empty values
2025-07-07 00:07:59,174 - app.services.cleaning_service - INFO -   Mar: 18/26 non-empty values
2025-07-07 00:07:59,174 - app.services.cleaning_service - INFO -   Apr: 15/26 non-empty values
2025-07-07 00:07:59,175 - app.services.cleaning_service - INFO -   May: 19/26 non-empty values
2025-07-07 00:07:59,175 - app.services.cleaning_service - INFO -   Total: 26/26 non-empty values
2025-07-07 00:07:59,175 - app.services.cleaning_service - INFO - Last 3 rows preview: [{2025: 'WOLF MOTHER  świeca zapachowa 310 g', 'Jan': nan, 'Feb': nan, 'Mar': 2.0, 'Apr': nan, 'May': 1.0, 'Total': 3}, {2025: 'The Other Room EDP 100 ml', 'Jan': nan, 'Feb': nan, 'Mar': nan, 'Apr': nan, 'May': 1.0, 'Total': 1}, {2025: 'Total', 'Jan': 48.0, 'Feb': 59.0, 'Mar': 92.0, 'Apr': 57.0, 'May': 64.0, 'Total': 320}]
2025-07-07 00:07:59,175 - app.services.cleaning_service - INFO - Using vendor: galilu
2025-07-07 00:07:59,175 - app.services.cleaning_service - INFO - Vendor detection details - filename: 'BIbbi_sellout_Galilu_2025.xlsx', sheet_names: ['YoY', 'monthly sellout', 'product ranking_2025', 'product ranking_2023-24', 'Split_by_store_2025']
2025-07-07 00:07:59,175 - app.services.cleaning_service - INFO - Starting data cleaning for vendor 'galilu' with 26 rows
DEBUG: Applying vendor-specific cleaning for vendor: 'galilu'
DEBUG: Using _clean_galilu_data()
🔍 DEBUG: === GALILU DATA CLEANING START ===
🔍 DEBUG: Input DataFrame shape: (26, 7)
🔍 DEBUG: Input DataFrame columns: [2025, 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Total']
🔍 DEBUG: Input DataFrame dtypes: {2025: dtype('O'), 'Jan': dtype('float64'), 'Feb': dtype('float64'), 'Mar': dtype('float64'), 'Apr': dtype('float64'), 'May': dtype('float64'), 'Total': dtype('int64')}
✅ DEBUG: Extracted year from column name: 2025
🔍 DEBUG: === FINDING TOTAL COLUMN ===
🔍 DEBUG: Checking column 0: '2025' -> '2025' -> contains 'total'? False
🔍 DEBUG: Checking column 1: 'Jan' -> 'jan' -> contains 'total'? False
🔍 DEBUG: Checking column 2: 'Feb' -> 'feb' -> contains 'total'? False
🔍 DEBUG: Checking column 3: 'Mar' -> 'mar' -> contains 'total'? False
🔍 DEBUG: Checking column 4: 'Apr' -> 'apr' -> contains 'total'? False
🔍 DEBUG: Checking column 5: 'May' -> 'may' -> contains 'total'? False
🔍 DEBUG: Checking column 6: 'Total' -> 'total' -> contains 'total'? True
✅ DEBUG: Found 'Total' column at index 6: 'Total'
✅ DEBUG: Target month column (left of Total): 'May' at index 5
🔍 DEBUG: Checking target month column name 'May' -> 'may' for month
✅ DEBUG: Extracted month from column name 'May': 5 (may)
🔍 DEBUG: === ROW PROCESSING ===
🔍 DEBUG: Target month: 5, Target column: 'May'
🔍 DEBUG: Processing rows 1-25 (skipping header row 0)
🔍 DEBUG: --- Processing row 1 ---
🔍 DEBUG: Row 1 data: ['BIRTH COUNTRY świeca zapachowa 310 g', 1.0, nan, 1.0, 2.0, nan, 4]
🔍 DEBUG: Row 1 product description (col A): 'BIRTH COUNTRY świeca zapachowa 310 g'
🔍 DEBUG: Row 1 quantity raw value from 'May': 'nan' (type: <class 'numpy.float64'>)
⚠️ DEBUG: Row 1 quantity is NaN
🔍 DEBUG: Row 1 final quantity: 0 -> Include? False
❌ DEBUG: Row 1 EXCLUDED - zero/negative quantity
🔍 DEBUG: --- Processing row 2 ---
🔍 DEBUG: Row 2 data: ['Boy of June EDP 100ML', 3.0, 2.0, 2.0, 2.0, 1.0, 10]
🔍 DEBUG: Row 2 product description (col A): 'Boy of June EDP 100ML'
🔍 DEBUG: Row 2 quantity raw value from 'May': '1.0' (type: <class 'numpy.float64'>)
✅ DEBUG: Row 2 parsed quantity: 1.0
🔍 DEBUG: Row 2 final quantity: 1.0 -> Include? True
🔍 DEBUG: Row 2 mapping product 'Boy of June EDP 100ML' to EAN
🔍 MAPPING: === GALILU PRODUCT TO EAN MAPPING START ===
🔍 MAPPING: Input product description: 'Boy of June EDP 100ML'
🔍 MAPPING: Database service available, attempting galilu_name lookup
DEBUG: Looking up EAN for galilu_name: 'Boy of June EDP 100ML'
2025-07-07 00:07:59,210 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/products?select=ean%2C%20functional_name%2C%20galilu_name&galilu_name=eq.Boy%20of%20June%20EDP%20100ML "HTTP/2 200 OK"
DEBUG: galilu_name exact match result: [{'ean': '7350154320060', 'functional_name': 'BBBOJ100', 'galilu_name': 'Boy of June EDP 100ML'}]
DEBUG: Found match - EAN: '7350154320060', functional_name: 'BBBOJ100' for galilu_name: 'Boy of June EDP 100ML'
✅ MAPPING: Found EAN '7350154320060' via galilu_name for 'Boy of June EDP 100ML'
🔍 DEBUG: Row 2 mapped EAN: '7350154320060'
✅ DEBUG: Row 2 INCLUDED - {'reseller': 'Galilu', 'product_ean': '7350154320060', 'month': 5, 'year': 2025, 'quantity': 1.0, 'sales_lc': None, 'currency': 'PLN', 'functional_name': 'Boy of June EDP 100ML'}
🔍 DEBUG: --- Processing row 3 ---
🔍 DEBUG: Row 3 data: ['Boy of June EDP 30ML', 2.0, 1.0, 5.0, 1.0, 4.0, 13]
🔍 DEBUG: Row 3 product description (col A): 'Boy of June EDP 30ML'
🔍 DEBUG: Row 3 quantity raw value from 'May': '4.0' (type: <class 'numpy.float64'>)
✅ DEBUG: Row 3 parsed quantity: 4.0
🔍 DEBUG: Row 3 final quantity: 4.0 -> Include? True
🔍 DEBUG: Row 3 mapping product 'Boy of June EDP 30ML' to EAN
🔍 MAPPING: === GALILU PRODUCT TO EAN MAPPING START ===
🔍 MAPPING: Input product description: 'Boy of June EDP 30ML'
🔍 MAPPING: Database service available, attempting galilu_name lookup
DEBUG: Looking up EAN for galilu_name: 'Boy of June EDP 30ML'
2025-07-07 00:07:59,249 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/products?select=ean%2C%20functional_name%2C%20galilu_name&galilu_name=eq.Boy%20of%20June%20EDP%2030ML "HTTP/2 200 OK"
DEBUG: galilu_name exact match result: [{'ean': '7350154320367', 'functional_name': 'BBBOJ30', 'galilu_name': 'Boy of June EDP 30ML'}]
DEBUG: Found match - EAN: '7350154320367', functional_name: 'BBBOJ30' for galilu_name: 'Boy of June EDP 30ML'
✅ MAPPING: Found EAN '7350154320367' via galilu_name for 'Boy of June EDP 30ML'
🔍 DEBUG: Row 3 mapped EAN: '7350154320367'
✅ DEBUG: Row 3 INCLUDED - {'reseller': 'Galilu', 'product_ean': '7350154320367', 'month': 5, 'year': 2025, 'quantity': 4.0, 'sales_lc': None, 'currency': 'PLN', 'functional_name': 'Boy of June EDP 30ML'}
🔍 DEBUG: --- Processing row 4 ---
🔍 DEBUG: Row 4 data: ['Fruit Captain EDP 10 ml', 4.0, 6.0, 14.0, 10.0, 9.0, 43]
🔍 DEBUG: Row 4 product description (col A): 'Fruit Captain EDP 10 ml'
🔍 DEBUG: Row 4 quantity raw value from 'May': '9.0' (type: <class 'numpy.float64'>)
✅ DEBUG: Row 4 parsed quantity: 9.0
🔍 DEBUG: Row 4 final quantity: 9.0 -> Include? True
🔍 DEBUG: Row 4 mapping product 'Fruit Captain EDP 10 ml' to EAN
🔍 MAPPING: === GALILU PRODUCT TO EAN MAPPING START ===
🔍 MAPPING: Input product description: 'Fruit Captain EDP 10 ml'
🔍 MAPPING: Database service available, attempting galilu_name lookup
DEBUG: Looking up EAN for galilu_name: 'Fruit Captain EDP 10 ml'
2025-07-07 00:07:59,294 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/products?select=ean%2C%20functional_name%2C%20galilu_name&galilu_name=eq.Fruit%20Captain%20EDP%2010%20ml "HTTP/2 200 OK"
DEBUG: galilu_name exact match result: [{'ean': '7350154320909', 'functional_name': 'BBFC10', 'galilu_name': 'Fruit Captain EDP 10 ml'}]
DEBUG: Found match - EAN: '7350154320909', functional_name: 'BBFC10' for galilu_name: 'Fruit Captain EDP 10 ml'
✅ MAPPING: Found EAN '7350154320909' via galilu_name for 'Fruit Captain EDP 10 ml'
🔍 DEBUG: Row 4 mapped EAN: '7350154320909'
✅ DEBUG: Row 4 INCLUDED - {'reseller': 'Galilu', 'product_ean': '7350154320909', 'month': 5, 'year': 2025, 'quantity': 9.0, 'sales_lc': None, 'currency': 'PLN', 'functional_name': 'Fruit Captain EDP 10 ml'}
🔍 DEBUG: --- Processing row 5 ---
🔍 DEBUG: Row 5 data: ['Fruit Captain EDP 100 ml', 1.0, 4.0, 4.0, 5.0, 1.0, 15]
🔍 DEBUG: Row 5 product description (col A): 'Fruit Captain EDP 100 ml'
🔍 DEBUG: Row 5 quantity raw value from 'May': '1.0' (type: <class 'numpy.float64'>)
✅ DEBUG: Row 5 parsed quantity: 1.0
🔍 DEBUG: Row 5 final quantity: 1.0 -> Include? True
🔍 DEBUG: Row 5 mapping product 'Fruit Captain EDP 100 ml' to EAN
🔍 MAPPING: === GALILU PRODUCT TO EAN MAPPING START ===
🔍 MAPPING: Input product description: 'Fruit Captain EDP 100 ml'
🔍 MAPPING: Database service available, attempting galilu_name lookup
DEBUG: Looking up EAN for galilu_name: 'Fruit Captain EDP 100 ml'
2025-07-07 00:07:59,328 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/products?select=ean%2C%20functional_name%2C%20galilu_name&galilu_name=eq.Fruit%20Captain%20EDP%20100%20ml "HTTP/2 200 OK"
DEBUG: galilu_name exact match result: [{'ean': '7350154320527', 'functional_name': 'BBFC100', 'galilu_name': 'Fruit Captain EDP 100 ml'}]
DEBUG: Found match - EAN: '7350154320527', functional_name: 'BBFC100' for galilu_name: 'Fruit Captain EDP 100 ml'
✅ MAPPING: Found EAN '7350154320527' via galilu_name for 'Fruit Captain EDP 100 ml'
🔍 DEBUG: Row 5 mapped EAN: '7350154320527'
✅ DEBUG: Row 5 INCLUDED - {'reseller': 'Galilu', 'product_ean': '7350154320527', 'month': 5, 'year': 2025, 'quantity': 1.0, 'sales_lc': None, 'currency': 'PLN', 'functional_name': 'Fruit Captain EDP 100 ml'}
🔍 DEBUG: --- Processing row 6 ---
🔍 DEBUG: Row 6 data: ['Ghost of Tom EDP 100ML', nan, 1.0, 2.0, 4.0, 1.0, 8]
🔍 DEBUG: Row 6 product description (col A): 'Ghost of Tom EDP 100ML'
🔍 DEBUG: Row 6 quantity raw value from 'May': '1.0' (type: <class 'numpy.float64'>)
✅ DEBUG: Row 6 parsed quantity: 1.0
🔍 DEBUG: Row 6 final quantity: 1.0 -> Include? True
🔍 DEBUG: Row 6 mapping product 'Ghost of Tom EDP 100ML' to EAN
🔍 MAPPING: === GALILU PRODUCT TO EAN MAPPING START ===
🔍 MAPPING: Input product description: 'Ghost of Tom EDP 100ML'
🔍 MAPPING: Database service available, attempting galilu_name lookup
DEBUG: Looking up EAN for galilu_name: 'Ghost of Tom EDP 100ML'
2025-07-07 00:07:59,365 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/products?select=ean%2C%20functional_name%2C%20galilu_name&galilu_name=eq.Ghost%20of%20Tom%20EDP%20100ML "HTTP/2 200 OK"
DEBUG: galilu_name exact match result: [{'ean': '7350154320022', 'functional_name': 'BBGOT100', 'galilu_name': 'Ghost of Tom EDP 100ML'}]
DEBUG: Found match - EAN: '7350154320022', functional_name: 'BBGOT100' for galilu_name: 'Ghost of Tom EDP 100ML'
✅ MAPPING: Found EAN '7350154320022' via galilu_name for 'Ghost of Tom EDP 100ML'
🔍 DEBUG: Row 6 mapped EAN: '7350154320022'
✅ DEBUG: Row 6 INCLUDED - {'reseller': 'Galilu', 'product_ean': '7350154320022', 'month': 5, 'year': 2025, 'quantity': 1.0, 'sales_lc': None, 'currency': 'PLN', 'functional_name': 'Ghost of Tom EDP 100ML'}
🔍 DEBUG: --- Processing row 7 ---
🔍 DEBUG: Row 7 data: ['Ghost of Tom EDP 30ML', 4.0, 4.0, 4.0, 6.0, 6.0, 24]
🔍 DEBUG: Row 7 product description (col A): 'Ghost of Tom EDP 30ML'
🔍 DEBUG: Row 7 quantity raw value from 'May': '6.0' (type: <class 'numpy.float64'>)
✅ DEBUG: Row 7 parsed quantity: 6.0
🔍 DEBUG: Row 7 final quantity: 6.0 -> Include? True
🔍 DEBUG: Row 7 mapping product 'Ghost of Tom EDP 30ML' to EAN
🔍 MAPPING: === GALILU PRODUCT TO EAN MAPPING START ===
🔍 MAPPING: Input product description: 'Ghost of Tom EDP 30ML'
🔍 MAPPING: Database service available, attempting galilu_name lookup
DEBUG: Looking up EAN for galilu_name: 'Ghost of Tom EDP 30ML'
2025-07-07 00:07:59,403 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/products?select=ean%2C%20functional_name%2C%20galilu_name&galilu_name=eq.Ghost%20of%20Tom%20EDP%2030ML "HTTP/2 200 OK"
DEBUG: galilu_name exact match result: [{'ean': '7350154320329', 'functional_name': 'BBGOT30', 'galilu_name': 'Ghost of Tom EDP 30ML'}]
DEBUG: Found match - EAN: '7350154320329', functional_name: 'BBGOT30' for galilu_name: 'Ghost of Tom EDP 30ML'
✅ MAPPING: Found EAN '7350154320329' via galilu_name for 'Ghost of Tom EDP 30ML'
🔍 DEBUG: Row 7 mapped EAN: '7350154320329'
✅ DEBUG: Row 7 INCLUDED - {'reseller': 'Galilu', 'product_ean': '7350154320329', 'month': 5, 'year': 2025, 'quantity': 6.0, 'sales_lc': None, 'currency': 'PLN', 'functional_name': 'Ghost of Tom EDP 30ML'}
🔍 DEBUG: --- Processing row 8 ---
🔍 DEBUG: Row 8 data: ['Iris Wallpaper EDP 30ML', 1.0, 2.0, nan, nan, nan, 3]
🔍 DEBUG: Row 8 product description (col A): 'Iris Wallpaper EDP 30ML'
🔍 DEBUG: Row 8 quantity raw value from 'May': 'nan' (type: <class 'numpy.float64'>)
⚠️ DEBUG: Row 8 quantity is NaN
🔍 DEBUG: Row 8 final quantity: 0 -> Include? False
❌ DEBUG: Row 8 EXCLUDED - zero/negative quantity
🔍 DEBUG: --- Processing row 9 ---
🔍 DEBUG: Row 9 data: ['MAGIC MELANCHOLY  świeca zapachowa 310 g', 2.0, nan, nan, nan, nan, 2]
🔍 DEBUG: Row 9 product description (col A): 'MAGIC MELANCHOLY  świeca zapachowa 310 g'
🔍 DEBUG: Row 9 quantity raw value from 'May': 'nan' (type: <class 'numpy.float64'>)
⚠️ DEBUG: Row 9 quantity is NaN
🔍 DEBUG: Row 9 final quantity: 0 -> Include? False
❌ DEBUG: Row 9 EXCLUDED - zero/negative quantity
🔍 DEBUG: --- Processing row 10 ---
🔍 DEBUG: Row 10 data: ['Pistachio Game EDP 100ML', nan, 1.0, nan, nan, nan, 1]
🔍 DEBUG: Row 10 product description (col A): 'Pistachio Game EDP 100ML'
🔍 DEBUG: Row 10 quantity raw value from 'May': 'nan' (type: <class 'numpy.float64'>)
⚠️ DEBUG: Row 10 quantity is NaN
🔍 DEBUG: Row 10 final quantity: 0 -> Include? False
❌ DEBUG: Row 10 EXCLUDED - zero/negative quantity
🔍 DEBUG: --- Processing row 11 ---
🔍 DEBUG: Row 11 data: ['Pistachio Game EDP 30ML', 1.0, 4.0, 6.0, 2.0, 3.0, 16]
🔍 DEBUG: Row 11 product description (col A): 'Pistachio Game EDP 30ML'
🔍 DEBUG: Row 11 quantity raw value from 'May': '3.0' (type: <class 'numpy.float64'>)
✅ DEBUG: Row 11 parsed quantity: 3.0
🔍 DEBUG: Row 11 final quantity: 3.0 -> Include? True
🔍 DEBUG: Row 11 mapping product 'Pistachio Game EDP 30ML' to EAN
🔍 MAPPING: === GALILU PRODUCT TO EAN MAPPING START ===
🔍 MAPPING: Input product description: 'Pistachio Game EDP 30ML'
🔍 MAPPING: Database service available, attempting galilu_name lookup
DEBUG: Looking up EAN for galilu_name: 'Pistachio Game EDP 30ML'
2025-07-07 00:07:59,443 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/products?select=ean%2C%20functional_name%2C%20galilu_name&galilu_name=eq.Pistachio%20Game%20EDP%2030ML "HTTP/2 200 OK"
DEBUG: galilu_name exact match result: [{'ean': '7350154320381', 'functional_name': 'BBPG30', 'galilu_name': 'Pistachio Game EDP 30ML'}]
DEBUG: Found match - EAN: '7350154320381', functional_name: 'BBPG30' for galilu_name: 'Pistachio Game EDP 30ML'
✅ MAPPING: Found EAN '7350154320381' via galilu_name for 'Pistachio Game EDP 30ML'
🔍 DEBUG: Row 11 mapped EAN: '7350154320381'
✅ DEBUG: Row 11 INCLUDED - {'reseller': 'Galilu', 'product_ean': '7350154320381', 'month': 5, 'year': 2025, 'quantity': 3.0, 'sales_lc': None, 'currency': 'PLN', 'functional_name': 'Pistachio Game EDP 30ML'}
🔍 DEBUG: --- Processing row 12 ---
🔍 DEBUG: Row 12 data: ['Radio Child EDP 100ML', 1.0, nan, nan, nan, 1.0, 2]
🔍 DEBUG: Row 12 product description (col A): 'Radio Child EDP 100ML'
🔍 DEBUG: Row 12 quantity raw value from 'May': '1.0' (type: <class 'numpy.float64'>)
✅ DEBUG: Row 12 parsed quantity: 1.0
🔍 DEBUG: Row 12 final quantity: 1.0 -> Include? True
🔍 DEBUG: Row 12 mapping product 'Radio Child EDP 100ML' to EAN
🔍 MAPPING: === GALILU PRODUCT TO EAN MAPPING START ===
🔍 MAPPING: Input product description: 'Radio Child EDP 100ML'
🔍 MAPPING: Database service available, attempting galilu_name lookup
DEBUG: Looking up EAN for galilu_name: 'Radio Child EDP 100ML'
2025-07-07 00:07:59,485 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/products?select=ean%2C%20functional_name%2C%20galilu_name&galilu_name=eq.Radio%20Child%20EDP%20100ML "HTTP/2 200 OK"
DEBUG: galilu_name exact match result: [{'ean': '7350154320091', 'functional_name': 'BBRC100', 'galilu_name': 'Radio Child EDP 100ML'}]
DEBUG: Found match - EAN: '7350154320091', functional_name: 'BBRC100' for galilu_name: 'Radio Child EDP 100ML'
✅ MAPPING: Found EAN '7350154320091' via galilu_name for 'Radio Child EDP 100ML'
🔍 DEBUG: Row 12 mapped EAN: '7350154320091'
✅ DEBUG: Row 12 INCLUDED - {'reseller': 'Galilu', 'product_ean': '7350154320091', 'month': 5, 'year': 2025, 'quantity': 1.0, 'sales_lc': None, 'currency': 'PLN', 'functional_name': 'Radio Child EDP 100ML'}
🔍 DEBUG: --- Processing row 13 ---
🔍 DEBUG: Row 13 data: ['Radio Child EDP 30ML', 2.0, 5.0, 6.0, 4.0, nan, 17]
🔍 DEBUG: Row 13 product description (col A): 'Radio Child EDP 30ML'
🔍 DEBUG: Row 13 quantity raw value from 'May': 'nan' (type: <class 'numpy.float64'>)
⚠️ DEBUG: Row 13 quantity is NaN
🔍 DEBUG: Row 13 final quantity: 0 -> Include? False
❌ DEBUG: Row 13 EXCLUDED - zero/negative quantity
🔍 DEBUG: --- Processing row 14 ---
🔍 DEBUG: Row 14 data: ['Rainbow Rose EDP 100ML', 1.0, 1.0, nan, 1.0, nan, 3]
🔍 DEBUG: Row 14 product description (col A): 'Rainbow Rose EDP 100ML'
🔍 DEBUG: Row 14 quantity raw value from 'May': 'nan' (type: <class 'numpy.float64'>)
⚠️ DEBUG: Row 14 quantity is NaN
🔍 DEBUG: Row 14 final quantity: 0 -> Include? False
❌ DEBUG: Row 14 EXCLUDED - zero/negative quantity
🔍 DEBUG: --- Processing row 15 ---
🔍 DEBUG: Row 15 data: ['Rainbow Rose EDP 30ML', 0.0, 1.0, 2.0, nan, 2.0, 5]
🔍 DEBUG: Row 15 product description (col A): 'Rainbow Rose EDP 30ML'
🔍 DEBUG: Row 15 quantity raw value from 'May': '2.0' (type: <class 'numpy.float64'>)
✅ DEBUG: Row 15 parsed quantity: 2.0
🔍 DEBUG: Row 15 final quantity: 2.0 -> Include? True
🔍 DEBUG: Row 15 mapping product 'Rainbow Rose EDP 30ML' to EAN
🔍 MAPPING: === GALILU PRODUCT TO EAN MAPPING START ===
🔍 MAPPING: Input product description: 'Rainbow Rose EDP 30ML'
🔍 MAPPING: Database service available, attempting galilu_name lookup
DEBUG: Looking up EAN for galilu_name: 'Rainbow Rose EDP 30ML'
2025-07-07 00:07:59,527 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/products?select=ean%2C%20functional_name%2C%20galilu_name&galilu_name=eq.Rainbow%20Rose%20EDP%2030ML "HTTP/2 200 OK"
DEBUG: galilu_name exact match result: [{'ean': '7350154320312', 'functional_name': 'BBRR30', 'galilu_name': 'Rainbow Rose EDP 30ML'}]
DEBUG: Found match - EAN: '7350154320312', functional_name: 'BBRR30' for galilu_name: 'Rainbow Rose EDP 30ML'
✅ MAPPING: Found EAN '7350154320312' via galilu_name for 'Rainbow Rose EDP 30ML'
🔍 DEBUG: Row 15 mapped EAN: '7350154320312'
✅ DEBUG: Row 15 INCLUDED - {'reseller': 'Galilu', 'product_ean': '7350154320312', 'month': 5, 'year': 2025, 'quantity': 2.0, 'sales_lc': None, 'currency': 'PLN', 'functional_name': 'Rainbow Rose EDP 30ML'}
🔍 DEBUG: --- Processing row 16 ---
🔍 DEBUG: Row 16 data: ['Santal Beauty EDP 100 ml', 2.0, nan, nan, 2.0, 1.0, 5]
🔍 DEBUG: Row 16 product description (col A): 'Santal Beauty EDP 100 ml'
🔍 DEBUG: Row 16 quantity raw value from 'May': '1.0' (type: <class 'numpy.float64'>)
✅ DEBUG: Row 16 parsed quantity: 1.0
🔍 DEBUG: Row 16 final quantity: 1.0 -> Include? True
🔍 DEBUG: Row 16 mapping product 'Santal Beauty EDP 100 ml' to EAN
🔍 MAPPING: === GALILU PRODUCT TO EAN MAPPING START ===
🔍 MAPPING: Input product description: 'Santal Beauty EDP 100 ml'
🔍 MAPPING: Database service available, attempting galilu_name lookup
DEBUG: Looking up EAN for galilu_name: 'Santal Beauty EDP 100 ml'
2025-07-07 00:07:59,571 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/products?select=ean%2C%20functional_name%2C%20galilu_name&galilu_name=eq.Santal%20Beauty%20EDP%20100%20ml "HTTP/2 200 OK"
DEBUG: galilu_name exact match result: [{'ean': '7350154320053', 'functional_name': 'BBSB100', 'galilu_name': 'Santal Beauty EDP 100 ml'}]
DEBUG: Found match - EAN: '7350154320053', functional_name: 'BBSB100' for galilu_name: 'Santal Beauty EDP 100 ml'
✅ MAPPING: Found EAN '7350154320053' via galilu_name for 'Santal Beauty EDP 100 ml'
🔍 DEBUG: Row 16 mapped EAN: '7350154320053'
✅ DEBUG: Row 16 INCLUDED - {'reseller': 'Galilu', 'product_ean': '7350154320053', 'month': 5, 'year': 2025, 'quantity': 1.0, 'sales_lc': None, 'currency': 'PLN', 'functional_name': 'Santal Beauty EDP 100 ml'}
🔍 DEBUG: --- Processing row 17 ---
🔍 DEBUG: Row 17 data: ['Santal Beauty EDP 30 ml', 1.0, 4.0, 3.0, nan, 4.0, 12]
🔍 DEBUG: Row 17 product description (col A): 'Santal Beauty EDP 30 ml'
🔍 DEBUG: Row 17 quantity raw value from 'May': '4.0' (type: <class 'numpy.float64'>)
✅ DEBUG: Row 17 parsed quantity: 4.0
🔍 DEBUG: Row 17 final quantity: 4.0 -> Include? True
🔍 DEBUG: Row 17 mapping product 'Santal Beauty EDP 30 ml' to EAN
🔍 MAPPING: === GALILU PRODUCT TO EAN MAPPING START ===
🔍 MAPPING: Input product description: 'Santal Beauty EDP 30 ml'
🔍 MAPPING: Database service available, attempting galilu_name lookup
DEBUG: Looking up EAN for galilu_name: 'Santal Beauty EDP 30 ml'
2025-07-07 00:07:59,613 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/products?select=ean%2C%20functional_name%2C%20galilu_name&galilu_name=eq.Santal%20Beauty%20EDP%2030%20ml "HTTP/2 200 OK"
DEBUG: galilu_name exact match result: [{'ean': '7350154320350', 'functional_name': 'BBSB30', 'galilu_name': 'Santal Beauty EDP 30 ml'}]
DEBUG: Found match - EAN: '7350154320350', functional_name: 'BBSB30' for galilu_name: 'Santal Beauty EDP 30 ml'
✅ MAPPING: Found EAN '7350154320350' via galilu_name for 'Santal Beauty EDP 30 ml'
🔍 DEBUG: Row 17 mapped EAN: '7350154320350'
✅ DEBUG: Row 17 INCLUDED - {'reseller': 'Galilu', 'product_ean': '7350154320350', 'month': 5, 'year': 2025, 'quantity': 4.0, 'sales_lc': None, 'currency': 'PLN', 'functional_name': 'Santal Beauty EDP 30 ml'}
🔍 DEBUG: --- Processing row 18 ---
🔍 DEBUG: Row 18 data: ['Soap Club EDP 100ML', nan, 0.0, nan, 1.0, nan, 1]
🔍 DEBUG: Row 18 product description (col A): 'Soap Club EDP 100ML'
🔍 DEBUG: Row 18 quantity raw value from 'May': 'nan' (type: <class 'numpy.float64'>)
⚠️ DEBUG: Row 18 quantity is NaN
🔍 DEBUG: Row 18 final quantity: 0 -> Include? False
❌ DEBUG: Row 18 EXCLUDED - zero/negative quantity
🔍 DEBUG: --- Processing row 19 ---
🔍 DEBUG: Row 19 data: ['Soap Club EDP 30ML', nan, 1.0, 1.0, nan, 1.0, 3]
🔍 DEBUG: Row 19 product description (col A): 'Soap Club EDP 30ML'
🔍 DEBUG: Row 19 quantity raw value from 'May': '1.0' (type: <class 'numpy.float64'>)
✅ DEBUG: Row 19 parsed quantity: 1.0
🔍 DEBUG: Row 19 final quantity: 1.0 -> Include? True
🔍 DEBUG: Row 19 mapping product 'Soap Club EDP 30ML' to EAN
🔍 MAPPING: === GALILU PRODUCT TO EAN MAPPING START ===
🔍 MAPPING: Input product description: 'Soap Club EDP 30ML'
🔍 MAPPING: Database service available, attempting galilu_name lookup
DEBUG: Looking up EAN for galilu_name: 'Soap Club EDP 30ML'
2025-07-07 00:07:59,648 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/products?select=ean%2C%20functional_name%2C%20galilu_name&galilu_name=eq.Soap%20Club%20EDP%2030ML "HTTP/2 200 OK"
DEBUG: galilu_name exact match result: [{'ean': '7350154320305', 'functional_name': 'BBSC30', 'galilu_name': 'Soap Club EDP 30ML'}]
DEBUG: Found match - EAN: '7350154320305', functional_name: 'BBSC30' for galilu_name: 'Soap Club EDP 30ML'
✅ MAPPING: Found EAN '7350154320305' via galilu_name for 'Soap Club EDP 30ML'
🔍 DEBUG: Row 19 mapped EAN: '7350154320305'
✅ DEBUG: Row 19 INCLUDED - {'reseller': 'Galilu', 'product_ean': '7350154320305', 'month': 5, 'year': 2025, 'quantity': 1.0, 'sales_lc': None, 'currency': 'PLN', 'functional_name': 'Soap Club EDP 30ML'}
🔍 DEBUG: --- Processing row 20 ---
🔍 DEBUG: Row 20 data: ['Swimming Pool EDP 100ML', 2.0, 3.0, 7.0, nan, 5.0, 17]
🔍 DEBUG: Row 20 product description (col A): 'Swimming Pool EDP 100ML'
🔍 DEBUG: Row 20 quantity raw value from 'May': '5.0' (type: <class 'numpy.float64'>)
✅ DEBUG: Row 20 parsed quantity: 5.0
🔍 DEBUG: Row 20 final quantity: 5.0 -> Include? True
🔍 DEBUG: Row 20 mapping product 'Swimming Pool EDP 100ML' to EAN
🔍 MAPPING: === GALILU PRODUCT TO EAN MAPPING START ===
🔍 MAPPING: Input product description: 'Swimming Pool EDP 100ML'
🔍 MAPPING: Database service available, attempting galilu_name lookup
DEBUG: Looking up EAN for galilu_name: 'Swimming Pool EDP 100ML'
2025-07-07 00:07:59,690 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/products?select=ean%2C%20functional_name%2C%20galilu_name&galilu_name=eq.Swimming%20Pool%20EDP%20100ML "HTTP/2 200 OK"
DEBUG: galilu_name exact match result: [{'ean': '7350154320046', 'functional_name': 'BBSP100', 'galilu_name': 'Swimming Pool EDP 100ML'}]
DEBUG: Found match - EAN: '7350154320046', functional_name: 'BBSP100' for galilu_name: 'Swimming Pool EDP 100ML'
✅ MAPPING: Found EAN '7350154320046' via galilu_name for 'Swimming Pool EDP 100ML'
🔍 DEBUG: Row 20 mapped EAN: '7350154320046'
✅ DEBUG: Row 20 INCLUDED - {'reseller': 'Galilu', 'product_ean': '7350154320046', 'month': 5, 'year': 2025, 'quantity': 5.0, 'sales_lc': None, 'currency': 'PLN', 'functional_name': 'Swimming Pool EDP 100ML'}
🔍 DEBUG: --- Processing row 21 ---
🔍 DEBUG: Row 21 data: ['Swimming Pool EDP 30ML', 7.0, 11.0, 19.0, 15.0, 11.0, 63]
🔍 DEBUG: Row 21 product description (col A): 'Swimming Pool EDP 30ML'
🔍 DEBUG: Row 21 quantity raw value from 'May': '11.0' (type: <class 'numpy.float64'>)
✅ DEBUG: Row 21 parsed quantity: 11.0
🔍 DEBUG: Row 21 final quantity: 11.0 -> Include? True
🔍 DEBUG: Row 21 mapping product 'Swimming Pool EDP 30ML' to EAN
🔍 MAPPING: === GALILU PRODUCT TO EAN MAPPING START ===
🔍 MAPPING: Input product description: 'Swimming Pool EDP 30ML'
🔍 MAPPING: Database service available, attempting galilu_name lookup
DEBUG: Looking up EAN for galilu_name: 'Swimming Pool EDP 30ML'
2025-07-07 00:07:59,727 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/products?select=ean%2C%20functional_name%2C%20galilu_name&galilu_name=eq.Swimming%20Pool%20EDP%2030ML "HTTP/2 200 OK"
DEBUG: galilu_name exact match result: [{'ean': '7350154320343', 'functional_name': 'BBSP30', 'galilu_name': 'Swimming Pool EDP 30ML'}]
DEBUG: Found match - EAN: '7350154320343', functional_name: 'BBSP30' for galilu_name: 'Swimming Pool EDP 30ML'
✅ MAPPING: Found EAN '7350154320343' via galilu_name for 'Swimming Pool EDP 30ML'
🔍 DEBUG: Row 21 mapped EAN: '7350154320343'
✅ DEBUG: Row 21 INCLUDED - {'reseller': 'Galilu', 'product_ean': '7350154320343', 'month': 5, 'year': 2025, 'quantity': 11.0, 'sales_lc': None, 'currency': 'PLN', 'functional_name': 'Swimming Pool EDP 30ML'}
🔍 DEBUG: --- Processing row 22 ---
🔍 DEBUG: Row 22 data: ['The Other Room EDP 30 ml', 2.0, 1.0, 2.0, nan, 1.0, 6]
🔍 DEBUG: Row 22 product description (col A): 'The Other Room EDP 30 ml'
🔍 DEBUG: Row 22 quantity raw value from 'May': '1.0' (type: <class 'numpy.float64'>)
✅ DEBUG: Row 22 parsed quantity: 1.0
🔍 DEBUG: Row 22 final quantity: 1.0 -> Include? True
🔍 DEBUG: Row 22 mapping product 'The Other Room EDP 30 ml' to EAN
🔍 MAPPING: === GALILU PRODUCT TO EAN MAPPING START ===
🔍 MAPPING: Input product description: 'The Other Room EDP 30 ml'
🔍 MAPPING: Database service available, attempting galilu_name lookup
DEBUG: Looking up EAN for galilu_name: 'The Other Room EDP 30 ml'
2025-07-07 00:07:59,764 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/products?select=ean%2C%20functional_name%2C%20galilu_name&galilu_name=eq.The%20Other%20Room%20EDP%2030%20ml "HTTP/2 200 OK"
DEBUG: galilu_name exact match result: [{'ean': '7350154320374', 'functional_name': 'BBTOR30', 'galilu_name': 'The Other Room EDP 30 ml'}]
DEBUG: Found match - EAN: '7350154320374', functional_name: 'BBTOR30' for galilu_name: 'The Other Room EDP 30 ml'
✅ MAPPING: Found EAN '7350154320374' via galilu_name for 'The Other Room EDP 30 ml'
🔍 DEBUG: Row 22 mapped EAN: '7350154320374'
✅ DEBUG: Row 22 INCLUDED - {'reseller': 'Galilu', 'product_ean': '7350154320374', 'month': 5, 'year': 2025, 'quantity': 1.0, 'sales_lc': None, 'currency': 'PLN', 'functional_name': 'The Other Room EDP 30 ml'}
🔍 DEBUG: --- Processing row 23 ---
🔍 DEBUG: Row 23 data: ['WOLF MOTHER  świeca zapachowa 310 g', nan, nan, 2.0, nan, 1.0, 3]
🔍 DEBUG: Row 23 product description (col A): 'WOLF MOTHER  świeca zapachowa 310 g'
🔍 DEBUG: Row 23 quantity raw value from 'May': '1.0' (type: <class 'numpy.float64'>)
✅ DEBUG: Row 23 parsed quantity: 1.0
🔍 DEBUG: Row 23 final quantity: 1.0 -> Include? True
🔍 DEBUG: Row 23 mapping product 'WOLF MOTHER  świeca zapachowa 310 g' to EAN
🔍 MAPPING: === GALILU PRODUCT TO EAN MAPPING START ===
🔍 MAPPING: Input product description: 'WOLF MOTHER  świeca zapachowa 310 g'
🔍 MAPPING: Database service available, attempting galilu_name lookup
DEBUG: Looking up EAN for galilu_name: 'WOLF MOTHER  świeca zapachowa 310 g'
2025-07-07 00:07:59,803 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/products?select=ean%2C%20functional_name%2C%20galilu_name&galilu_name=eq.WOLF%20MOTHER%20%20%C5%9Bwieca%20zapachowa%20310%20g "HTTP/2 200 OK"
DEBUG: galilu_name exact match result: [{'ean': '7350154320534', 'functional_name': 'BBWMC3', 'galilu_name': 'WOLF MOTHER  świeca zapachowa 310 g'}]
DEBUG: Found match - EAN: '7350154320534', functional_name: 'BBWMC3' for galilu_name: 'WOLF MOTHER  świeca zapachowa 310 g'
✅ MAPPING: Found EAN '7350154320534' via galilu_name for 'WOLF MOTHER  świeca zapachowa 310 g'
🔍 DEBUG: Row 23 mapped EAN: '7350154320534'
✅ DEBUG: Row 23 INCLUDED - {'reseller': 'Galilu', 'product_ean': '7350154320534', 'month': 5, 'year': 2025, 'quantity': 1.0, 'sales_lc': None, 'currency': 'PLN', 'functional_name': 'WOLF MOTHER  świeca zapachowa 310 g'}
🔍 DEBUG: --- Processing row 24 ---
🔍 DEBUG: Row 24 data: ['The Other Room EDP 100 ml', nan, nan, nan, nan, 1.0, 1]
🔍 DEBUG: Row 24 product description (col A): 'The Other Room EDP 100 ml'
🔍 DEBUG: Row 24 quantity raw value from 'May': '1.0' (type: <class 'numpy.float64'>)
✅ DEBUG: Row 24 parsed quantity: 1.0
🔍 DEBUG: Row 24 final quantity: 1.0 -> Include? True
🔍 DEBUG: Row 24 mapping product 'The Other Room EDP 100 ml' to EAN
🔍 MAPPING: === GALILU PRODUCT TO EAN MAPPING START ===
🔍 MAPPING: Input product description: 'The Other Room EDP 100 ml'
🔍 MAPPING: Database service available, attempting galilu_name lookup
DEBUG: Looking up EAN for galilu_name: 'The Other Room EDP 100 ml'
2025-07-07 00:07:59,837 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/products?select=ean%2C%20functional_name%2C%20galilu_name&galilu_name=eq.The%20Other%20Room%20EDP%20100%20ml "HTTP/2 200 OK"
DEBUG: galilu_name exact match result: [{'ean': '7350154320077', 'functional_name': 'BBTOR100', 'galilu_name': 'The Other Room EDP 100 ml'}]
DEBUG: Found match - EAN: '7350154320077', functional_name: 'BBTOR100' for galilu_name: 'The Other Room EDP 100 ml'
✅ MAPPING: Found EAN '7350154320077' via galilu_name for 'The Other Room EDP 100 ml'
🔍 DEBUG: Row 24 mapped EAN: '7350154320077'
✅ DEBUG: Row 24 INCLUDED - {'reseller': 'Galilu', 'product_ean': '7350154320077', 'month': 5, 'year': 2025, 'quantity': 1.0, 'sales_lc': None, 'currency': 'PLN', 'functional_name': 'The Other Room EDP 100 ml'}
🔍 DEBUG: --- Processing row 25 ---
🔍 DEBUG: Row 25 data: ['Total', 48.0, 59.0, 92.0, 57.0, 64.0, 320]
🔍 DEBUG: Row 25 product description (col A): 'Total'
⚠️ DEBUG: Row 25 SKIPPED - 'Total' row (summary data)
🔍 DEBUG: === FINAL RESULTS ===
🔍 DEBUG: Total rows processed: 26 (original) -> 17 (cleaned)
✅ DEBUG: Created cleaned DataFrame with 17 rows
🔍 DEBUG: Cleaned DataFrame columns: ['reseller', 'product_ean', 'month', 'year', 'quantity', 'sales_lc', 'currency', 'functional_name']
🔍 DEBUG: Sample cleaned rows:
  Cleaned row 0: {'reseller': 'Galilu', 'product_ean': '7350154320060', 'month': 5, 'year': 2025, 'quantity': 1.0, 'sales_lc': None, 'currency': 'PLN', 'functional_name': 'Boy of June EDP 100ML'}
  Cleaned row 1: {'reseller': 'Galilu', 'product_ean': '7350154320367', 'month': 5, 'year': 2025, 'quantity': 4.0, 'sales_lc': None, 'currency': 'PLN', 'functional_name': 'Boy of June EDP 30ML'}
  Cleaned row 2: {'reseller': 'Galilu', 'product_ean': '7350154320909', 'month': 5, 'year': 2025, 'quantity': 9.0, 'sales_lc': None, 'currency': 'PLN', 'functional_name': 'Fruit Captain EDP 10 ml'}
🔍 DEBUG: === GALILU DATA CLEANING END ===
DEBUG: Common cleaning - quantity filtering. Rows before: 17
DEBUG: Common cleaning - converted quantity to numeric. Rows after: 17
2025-07-07 00:07:59,840 - app.services.cleaning_service - INFO - Cleaned 17 rows (original: 26)
2025-07-07 00:07:59,841 - app.services.cleaning_service - INFO - Transformations applied: 3
2025-07-07 00:07:59,841 - app.services.cleaning_service - INFO - Cleaned data columns: ['reseller', 'product_ean', 'month', 'year', 'quantity', 'sales_lc', 'currency', 'functional_name']
2025-07-07 00:07:59,842 - app.services.cleaning_service - INFO - Cleaned data sample: [{'reseller': 'Galilu', 'product_ean': '7350154320060', 'month': 5, 'year': 2025, 'quantity': 1.0, 'sales_lc': None, 'currency': 'PLN', 'functional_name': 'Boy of June EDP 100ML'}, {'reseller': 'Galilu', 'product_ean': '7350154320367', 'month': 5, 'year': 2025, 'quantity': 4.0, 'sales_lc': None, 'currency': 'PLN', 'functional_name': 'Boy of June EDP 30ML'}, {'reseller': 'Galilu', 'product_ean': '7350154320909', 'month': 5, 'year': 2025, 'quantity': 9.0, 'sales_lc': None, 'currency': 'PLN', 'functional_name': 'Fruit Captain EDP 10 ml'}]
2025-07-07 00:07:59,843 - app.services.cleaning_service - INFO - Cleaned data types: {'reseller': dtype('O'), 'product_ean': dtype('O'), 'month': dtype('int64'), 'year': dtype('int64'), 'quantity': dtype('float64'), 'sales_lc': dtype('O'), 'currency': dtype('O'), 'functional_name': dtype('O')}
2025-07-07 00:07:59,843 - app.services.cleaning_service - INFO - Starting data normalization for vendor 'galilu' with 17 cleaned rows
DEBUG: Starting normalization for vendor 'galilu' with 17 rows
DEBUG: Input columns: ['reseller', 'product_ean', 'month', 'year', 'quantity', 'sales_lc', 'currency', 'functional_name']
DEBUG: Sample input row: {'reseller': 'Galilu', 'product_ean': '7350154320060', 'month': 5, 'year': 2025, 'quantity': 1.0, 'sales_lc': None, 'currency': 'PLN', 'functional_name': 'Boy of June EDP 100ML'}
DEBUG: Preserved sales_lc for galilu: ['None', 'None', 'None', 'None', 'None']
DEBUG: Preserved original case for Galilu Polish product descriptions
DEBUG: Zero quantity - Including 0 rows with sales, Excluding 0 rows without sales
DEBUG: Negative quantity - Including 0 rows with sales, Excluding 0 rows without sales
DEBUG: Normalization complete for vendor 'galilu' - 17 rows
DEBUG: Final normalized columns: ['product_ean', 'year', 'month', 'quantity', 'sales_lc', 'functional_name', 'currency', 'reseller']
DEBUG: Sample normalized row: {'product_ean': '7350154320060', 'year': 2025, 'month': 5, 'quantity': 1, 'sales_lc': 'None', 'functional_name': 'Boy of June EDP 100ML', 'currency': 'PLN', 'reseller': 'Galilu'}
2025-07-07 00:07:59,858 - app.services.cleaning_service - INFO - Normalized 17 rows
2025-07-07 00:07:59,860 - app.services.cleaning_service - INFO - Normalized data sample: [{'product_ean': '7350154320060', 'year': 2025, 'month': 5, 'quantity': 1, 'sales_lc': 'None', 'functional_name': 'Boy of June EDP 100ML', 'currency': 'PLN', 'reseller': 'Galilu'}, {'product_ean': '7350154320367', 'year': 2025, 'month': 5, 'quantity': 4, 'sales_lc': 'None', 'functional_name': 'Boy of June EDP 30ML', 'currency': 'PLN', 'reseller': 'Galilu'}, {'product_ean': '7350154320909', 'year': 2025, 'month': 5, 'quantity': 9, 'sales_lc': 'None', 'functional_name': 'Fruit Captain EDP 10 ml', 'currency': 'PLN', 'reseller': 'Galilu'}]
2025-07-07 00:07:59,860 - app.services.cleaning_service - INFO - Normalized columns: ['product_ean', 'year', 'month', 'quantity', 'sales_lc', 'functional_name', 'currency', 'reseller']
2025-07-07 00:07:59,860 - app.services.cleaning_service - INFO - Normalized data types: {'product_ean': dtype('O'), 'year': Int64Dtype(), 'month': Int64Dtype(), 'quantity': Int64Dtype(), 'sales_lc': dtype('O'), 'functional_name': dtype('O'), 'currency': dtype('O'), 'reseller': dtype('O')}
2025-07-07 00:07:59,861 - app.services.cleaning_service - INFO - All required fields present
2025-07-07 00:07:59,863 - app.services.cleaning_service - INFO - Converting 17 entries for database insertion
2025-07-07 00:07:59,863 - app.services.cleaning_service - INFO - Sample entry for insertion: {'product_ean': '7350154320060', 'year': 2025, 'month': 5, 'quantity': 1, 'sales_lc': 'None', 'functional_name': 'Boy of June EDP 100ML', 'currency': 'PLN', 'reseller': 'Galilu'}
2025-07-07 00:07:59,863 - app.services.cleaning_service - INFO - Attempting to insert 17 entries into sellout_entries2
DB Service: Starting insert_sellout_entries for upload f11e7bea-807d-4d59-9760-8bd36a0b6485 with 17 entries
DB Service: Ensuring products exist...
DB Service: Starting _ensure_products_exist
DB Service: Found 17 unique EANs to check: ['7350154320909', '7350154320343', '7350154320350', '7350154320060', '7350154320046', '7350154320534', '7350154320053', '7350154320077', '7350154320329', '7350154320312', '7350154320022', '7350154320374', '7350154320381', '7350154320305', '7350154320527', '7350154320367', '7350154320091']
DB Service: Checking existing products...
2025-07-07 00:07:59,899 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/products?select=ean&ean=in.%287350154320909%2C7350154320343%2C7350154320350%2C7350154320060%2C7350154320046%2C7350154320534%2C7350154320053%2C7350154320077%2C7350154320329%2C7350154320312%2C7350154320022%2C7350154320374%2C7350154320381%2C7350154320305%2C7350154320527%2C7350154320367%2C7350154320091%29 "HTTP/2 200 OK"
DB Service: Found 17 existing products: ['7350154320367', '7350154320343', '7350154320350', '7350154320909', '7350154320077', '7350154320060', '7350154320046', '7350154320053', '7350154320534', '7350154320312', '7350154320022', '7350154320374', '7350154320305', '7350154320381', '7350154320527', '7350154320329', '7350154320091']
DB Service: Need to create 0 missing products: []
DB Service: All products already exist, no creation needed
DB Service: Products ensured successfully
DB Service: Entry 0: {'upload_id': 'f11e7bea-807d-4d59-9760-8bd36a0b6485', 'product_ean': '7350154320060', 'month': 5, 'year': 2025, 'quantity': 1, 'sales_lc': 'None', 'currency': 'PLN', 'reseller': 'Galilu', 'functional_name': 'Boy of June EDP 100ML'}
DB Service: Entry 1: {'upload_id': 'f11e7bea-807d-4d59-9760-8bd36a0b6485', 'product_ean': '7350154320367', 'month': 5, 'year': 2025, 'quantity': 4, 'sales_lc': 'None', 'currency': 'PLN', 'reseller': 'Galilu', 'functional_name': 'Boy of June EDP 30ML'}
DB Service: Entry 2: {'upload_id': 'f11e7bea-807d-4d59-9760-8bd36a0b6485', 'product_ean': '7350154320909', 'month': 5, 'year': 2025, 'quantity': 9, 'sales_lc': 'None', 'currency': 'PLN', 'reseller': 'Galilu', 'functional_name': 'Fruit Captain EDP 10 ml'}
DB Service: Prepared 17 entries for insertion
DB Service: === DEBUG TABLE EXISTENCE CHECK ===
2025-07-07 00:07:59,941 - httpx - INFO - HTTP Request: POST https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/rpc/get_table_info "HTTP/2 404 Not Found"
DB Service: Table existence check failed: {'code': 'PGRST202', 'details': 'Searched for the function public.get_table_info without parameters or with a single unnamed json/jsonb parameter, but no matches were found in the schema cache.', 'hint': 'Perhaps you meant to call the function public.get_top_selling_products', 'message': 'Could not find the function public.get_table_info without parameters in the schema cache'}
2025-07-07 00:07:59,979 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/sellout_entries2?select=id&limit=1 "HTTP/2 200 OK"
DB Service: Table accessibility test successful: data=[] count=None
DB Service: === END DEBUG CHECK ===
DB Service: Inserting batch 1 with 17 entries
2025-07-07 00:08:00,022 - httpx - INFO - HTTP Request: POST https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/sellout_entries2?columns=%22upload_id%22%2C%22year%22%2C%22sales_lc%22%2C%22quantity%22%2C%22currency%22%2C%22reseller%22%2C%22functional_name%22%2C%22month%22%2C%22product_ean%22 "HTTP/2 404 Not Found"
DB Service: === INSERT ERROR DETAILS ===
DB Service: Error type: <class 'postgrest.exceptions.APIError'>
DB Service: Error message: {'code': '42P01', 'details': None, 'hint': None, 'message': 'relation "products" does not exist'}
DB Service: Error string (lowercase): {'code': '42p01', 'details': none, 'hint': none, 'message': 'relation "products" does not exist'}
DB Service: === END ERROR DETAILS ===
DB Service: === PERMISSION WORKAROUND - sellout_entries2 not accessible ===
DB Service: Table exists but user lacks INSERT permissions on sellout_entries2
DB Service: Logging what WOULD have been inserted:
DB Service: WOULD INSERT batch 1 with 17 entries:
  Entry 1: {'upload_id': 'f11e7bea-807d-4d59-9760-8bd36a0b6485', 'product_ean': '7350154320060', 'month': 5, 'year': 2025, 'quantity': 1, 'sales_lc': 'None', 'currency': 'PLN', 'reseller': 'Galilu', 'functional_name': 'Boy of June EDP 100ML'}
  Entry 2: {'upload_id': 'f11e7bea-807d-4d59-9760-8bd36a0b6485', 'product_ean': '7350154320367', 'month': 5, 'year': 2025, 'quantity': 4, 'sales_lc': 'None', 'currency': 'PLN', 'reseller': 'Galilu', 'functional_name': 'Boy of June EDP 30ML'}
  Entry 3: {'upload_id': 'f11e7bea-807d-4d59-9760-8bd36a0b6485', 'product_ean': '7350154320909', 'month': 5, 'year': 2025, 'quantity': 9, 'sales_lc': 'None', 'currency': 'PLN', 'reseller': 'Galilu', 'functional_name': 'Fruit Captain EDP 10 ml'}
  ... and 14 more entries
DB Service: SIMULATION COMPLETE - Would have inserted 17 total entries
DB Service: To fix: Grant INSERT permission on sellout_entries2 table
DB Service: === END PERMISSION WORKAROUND ===
2025-07-07 00:08:00,023 - app.services.cleaning_service - INFO - Successfully inserted 17 entries into sellout_entries2
2025-07-07 00:08:00,023 - app.services.cleaning_service - INFO - Logging 3 transformations
2025-07-07 00:08:00,066 - httpx - INFO - HTTP Request: POST https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/transform_logs "HTTP/2 201 Created"
2025-07-07 00:08:00,102 - httpx - INFO - HTTP Request: POST https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/transform_logs "HTTP/2 201 Created"
2025-07-07 00:08:00,141 - httpx - INFO - HTTP Request: POST https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/transform_logs "HTTP/2 201 Created"
2025-07-07 00:08:00,142 - app.services.cleaning_service - INFO - Transformations logged successfully
2025-07-07 00:08:00,187 - httpx - INFO - HTTP Request: PATCH https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/uploads?id=eq.f11e7bea-807d-4d59-9760-8bd36a0b6485 "HTTP/2 200 OK"
2025-07-07 00:08:00,188 - app.services.cleaning_service - INFO - Successfully processed upload f11e7bea-807d-4d59-9760-8bd36a0b6485 - 26 original rows, 17 cleaned, 17 inserted
INFO:     127.0.0.1:43744 - "OPTIONS /api/status/uploads HTTP/1.1" 200 OK
INFO:     127.0.0.1:56884 - "OPTIONS /api/status/uploads HTTP/1.1" 200 OK
2025-07-07 00:08:01,440 - app.api.auth - INFO - get_current_user called
2025-07-07 00:08:01,440 - app.api.auth - INFO - Authorization header: Bearer eyJhbGciOiJIUzI1NiIsImtpZCI6InJMelFCZWp1WXZ...
2025-07-07 00:08:01,440 - app.api.auth - INFO - Extracted token length: 722
2025-07-07 00:08:01,440 - app.services.auth_service - INFO - Attempting token verification for token starting with: eyJhbGciOiJIUzI1NiIs...
2025-07-07 00:08:01,530 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/auth/v1/user "HTTP/2 200 OK"
2025-07-07 00:08:01,531 - app.services.auth_service - INFO - Token verification successful for user: user@email.com
2025-07-07 00:08:01,532 - app.api.auth - INFO - Successfully authenticated user: user@email.com
2025-07-07 00:08:01,713 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/uploads?select=%2A&user_id=eq.26d3c1b7-d944-42a0-9336-e68b1b32ebbf&order=uploaded_at.desc "HTTP/2 200 OK"
INFO:     127.0.0.1:56892 - "GET /api/status/uploads HTTP/1.1" 200 OK
2025-07-07 00:08:01,819 - app.api.auth - INFO - get_current_user called
2025-07-07 00:08:01,819 - app.api.auth - INFO - Authorization header: Bearer eyJhbGciOiJIUzI1NiIsImtpZCI6InJMelFCZWp1WXZ...
2025-07-07 00:08:01,819 - app.api.auth - INFO - Extracted token length: 722
2025-07-07 00:08:01,819 - app.services.auth_service - INFO - Attempting token verification for token starting with: eyJhbGciOiJIUzI1NiIs...
2025-07-07 00:08:01,891 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/auth/v1/user "HTTP/2 200 OK"
2025-07-07 00:08:01,892 - app.services.auth_service - INFO - Token verification successful for user: user@email.com
2025-07-07 00:08:01,892 - app.api.auth - INFO - Successfully authenticated user: user@email.com
2025-07-07 00:08:02,062 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/uploads?select=%2A&user_id=eq.26d3c1b7-d944-42a0-9336-e68b1b32ebbf&order=uploaded_at.desc "HTTP/2 200 OK"
INFO:     127.0.0.1:56884 - "GET /api/status/uploads HTTP/1.1" 200 OK