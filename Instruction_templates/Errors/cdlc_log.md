INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [255941] using WatchFiles
INFO:     Started server process [255956]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
2025-07-04 13:02:35,070 - app.api.auth - INFO - get_current_user called
2025-07-04 13:02:35,071 - app.api.auth - INFO - Authorization header: Bearer eyJhbGciOiJIUzI1NiIsImtpZCI6InJMelFCZWp1WXZ...
2025-07-04 13:02:35,071 - app.api.auth - INFO - Extracted token length: 722
2025-07-04 13:02:35,071 - app.services.auth_service - INFO - Attempting token verification for token starting with: eyJhbGciOiJIUzI1NiIs...
2025-07-04 13:02:35,399 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/auth/v1/user "HTTP/2 200 OK"
2025-07-04 13:02:35,400 - app.services.auth_service - INFO - Token verification successful for user: user@email.com
2025-07-04 13:02:35,400 - app.api.auth - INFO - Successfully authenticated user: user@email.com
2025-07-04 13:02:35,684 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/uploads?select=%2A&user_id=eq.26d3c1b7-d944-42a0-9336-e68b1b32ebbf&order=uploaded_at.desc "HTTP/2 200 OK"
INFO:     127.0.0.1:42026 - "GET /api/status/uploads HTTP/1.1" 200 OK
INFO:     127.0.0.1:42026 - "OPTIONS /api/auth/debug-token HTTP/1.1" 200 OK
INFO:     127.0.0.1:42038 - "OPTIONS /api/auth/debug-token HTTP/1.1" 200 OK
2025-07-04 13:02:36,860 - app.services.auth_service - INFO - Attempting token verification for token starting with: eyJhbGciOiJIUzI1NiIs...
2025-07-04 13:02:37,049 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/auth/v1/user "HTTP/2 200 OK"
2025-07-04 13:02:37,052 - app.services.auth_service - INFO - Token verification successful for user: user@email.com
INFO:     127.0.0.1:42042 - "GET /api/auth/debug-token HTTP/1.1" 200 OK
2025-07-04 13:02:37,208 - app.services.auth_service - INFO - Attempting token verification for token starting with: eyJhbGciOiJIUzI1NiIs...
2025-07-04 13:02:37,413 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/auth/v1/user "HTTP/2 200 OK"
2025-07-04 13:02:37,414 - app.services.auth_service - INFO - Token verification successful for user: user@email.com
INFO:     127.0.0.1:42042 - "GET /api/auth/debug-token HTTP/1.1" 200 OK
INFO:     127.0.0.1:56544 - "OPTIONS /api/upload/ HTTP/1.1" 200 OK
2025-07-04 13:02:54,923 - app.api.auth - INFO - get_current_user called
2025-07-04 13:02:54,923 - app.api.auth - INFO - Authorization header: Bearer eyJhbGciOiJIUzI1NiIsImtpZCI6InJMelFCZWp1WXZ...
2025-07-04 13:02:54,923 - app.api.auth - INFO - Extracted token length: 722
2025-07-04 13:02:54,923 - app.services.auth_service - INFO - Attempting token verification for token starting with: eyJhbGciOiJIUzI1NiIs...
2025-07-04 13:02:55,332 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/auth/v1/user "HTTP/2 200 OK"
2025-07-04 13:02:55,333 - app.services.auth_service - INFO - Token verification successful for user: user@email.com
2025-07-04 13:02:55,333 - app.api.auth - INFO - Successfully authenticated user: user@email.com
2025-07-04 13:02:55,532 - watchfiles.main - INFO - 1 change detected
2025-07-04 13:02:55,766 - httpx - INFO - HTTP Request: POST https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/uploads "HTTP/2 201 Created"
INFO:     127.0.0.1:56544 - "POST /api/upload/ HTTP/1.1" 200 OK
2025-07-04 13:02:55,773 - app.services.cleaning_service - INFO - Starting background task for upload b6e90a95-3a25-41c4-9cae-f9e7e9deb7b4, filename: BIBBI_Sell_Out_2025 04.xlsx, user: 26d3c1b7-d944-42a0-9336-e68b1b32ebbf
2025-07-04 13:02:56,013 - httpx - INFO - HTTP Request: PATCH https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/uploads?id=eq.b6e90a95-3a25-41c4-9cae-f9e7e9deb7b4 "HTTP/2 200 OK"
2025-07-04 13:02:56,016 - app.services.cleaning_service - INFO - Updated upload b6e90a95-3a25-41c4-9cae-f9e7e9deb7b4 status to PROCESSING
2025-07-04 13:02:56,178 - app.services.cleaning_service - INFO - Excel file sheet names: ['2025 04']
2025-07-04 13:02:56,179 - app.services.cleaning_service - INFO - Detected vendor from filename: cdlc
2025-07-04 13:02:56,183 - app.services.cleaning_service - INFO - Loaded Excel sheet '2025 04' with 11 rows, columns: ['Unnamed: 0', 'Unnamed: 1', 'Unnamed: 2', 'Unnamed: 3', 'Unnamed: 4', 'Unnamed: 5', 'Unnamed: 6', 'Unnamed: 7', 'Unnamed: 8', 'Unnamed: 9', 'Unnamed: 10', 'Unnamed: 11', 'Unnamed: 12', 'Unnamed: 13', 'Unnamed: 14']
2025-07-04 13:02:56,185 - app.services.cleaning_service - INFO - First 3 rows preview: [{'Unnamed: 0': nan, 'Unnamed: 1': '2025 April', 'Unnamed: 2': nan, 'Unnamed: 3': 'E-shop', 'Unnamed: 4': nan, 'Unnamed: 5': 'Lithuania', 'Unnamed: 6': nan, 'Unnamed: 7': nan, 'Unnamed: 8': nan, 'Unnamed: 9': nan, 'Unnamed: 10': nan, 'Unnamed: 11': 'Latvia', 'Unnamed: 12': nan, 'Unnamed: 13': 'Total', 'Unnamed: 14': nan}, {'Unnamed: 0': nan, 'Unnamed: 1': nan, 'Unnamed: 2': nan, 'Unnamed: 3': nan, 'Unnamed: 4': nan, 'Unnamed: 5': 'Vilnius Panorama', 'Unnamed: 6': 'Vilnius Panorama', 'Unnamed: 7': 'Vilnius Akropolis', 'Unnamed: 8': 'Vilnius Akropolis', 'Unnamed: 9': 'Kaunas Akropolis', 'Unnamed: 10': 'Kaunas Akropolis', 'Unnamed: 11': 'LV Riga Spice CdlC', 'Unnamed: 12': 'LV Riga Spice CdlC', 'Unnamed: 13': nan, 'Unnamed: 14': nan}, {'Unnamed: 0': nan, 'Unnamed: 1': nan, 'Unnamed: 2': nan, 'Unnamed: 3': 'Qty', 'Unnamed: 4': 'Sum Eur', 'Unnamed: 5': 'Qty', 'Unnamed: 6': 'Sum Eur', 'Unnamed: 7': 'Qty', 'Unnamed: 8': 'Sum Eur', 'Unnamed: 9': 'Qty', 'Unnamed: 10': 'Sum Eur', 'Unnamed: 11': 'Qty', 'Unnamed: 12': 'Sum Eur', 'Unnamed: 13': 'Qty', 'Unnamed: 14': 'Sum Eur'}]
2025-07-04 13:02:56,186 - app.services.cleaning_service - INFO - Data types: {'Unnamed: 0': dtype('float64'), 'Unnamed: 1': dtype('O'), 'Unnamed: 2': dtype('O'), 'Unnamed: 3': dtype('O'), 'Unnamed: 4': dtype('O'), 'Unnamed: 5': dtype('O'), 'Unnamed: 6': dtype('O'), 'Unnamed: 7': dtype('O'), 'Unnamed: 8': dtype('O'), 'Unnamed: 9': dtype('O'), 'Unnamed: 10': dtype('O'), 'Unnamed: 11': dtype('O'), 'Unnamed: 12': dtype('O'), 'Unnamed: 13': dtype('O'), 'Unnamed: 14': dtype('O')}
2025-07-04 13:02:56,186 - app.services.cleaning_service - INFO - Column data distribution:
2025-07-04 13:02:56,186 - app.services.cleaning_service - INFO -   Unnamed: 0: 0/11 non-empty values
2025-07-04 13:02:56,186 - app.services.cleaning_service - INFO -   Unnamed: 1: 9/11 non-empty values
2025-07-04 13:02:56,187 - app.services.cleaning_service - INFO -   Unnamed: 2: 7/11 non-empty values
2025-07-04 13:02:56,187 - app.services.cleaning_service - INFO -   Unnamed: 3: 6/11 non-empty values
2025-07-04 13:02:56,187 - app.services.cleaning_service - INFO -   Unnamed: 4: 5/11 non-empty values
2025-07-04 13:02:56,187 - app.services.cleaning_service - INFO -   Unnamed: 5: 6/11 non-empty values
2025-07-04 13:02:56,187 - app.services.cleaning_service - INFO -   Unnamed: 6: 5/11 non-empty values
2025-07-04 13:02:56,188 - app.services.cleaning_service - INFO -   Unnamed: 7: 5/11 non-empty values
2025-07-04 13:02:56,188 - app.services.cleaning_service - INFO -   Unnamed: 8: 5/11 non-empty values
2025-07-04 13:02:56,188 - app.services.cleaning_service - INFO -   Unnamed: 9: 4/11 non-empty values
2025-07-04 13:02:56,188 - app.services.cleaning_service - INFO -   Unnamed: 10: 4/11 non-empty values
2025-07-04 13:02:56,188 - app.services.cleaning_service - INFO -   Unnamed: 11: 5/11 non-empty values
2025-07-04 13:02:56,189 - app.services.cleaning_service - INFO -   Unnamed: 12: 4/11 non-empty values
2025-07-04 13:02:56,189 - app.services.cleaning_service - INFO -   Unnamed: 13: 10/11 non-empty values
2025-07-04 13:02:56,189 - app.services.cleaning_service - INFO -   Unnamed: 14: 9/11 non-empty values
2025-07-04 13:02:56,190 - app.services.cleaning_service - INFO - Last 3 rows preview: [{'Unnamed: 0': nan, 'Unnamed: 1': '7350154320367', 'Unnamed: 2': 'BIBBI. Boy of June EDP 30 ml', 'Unnamed: 3': 1, 'Unnamed: 4': 119.9957, 'Unnamed: 5': nan, 'Unnamed: 6': nan, 'Unnamed: 7': nan, 'Unnamed: 8': nan, 'Unnamed: 9': nan, 'Unnamed: 10': nan, 'Unnamed: 11': nan, 'Unnamed: 12': nan, 'Unnamed: 13': 1, 'Unnamed: 14': 119.9957}, {'Unnamed: 0': nan, 'Unnamed: 1': '7350154320503', 'Unnamed: 2': 'BIBBI. Fragrance Discovery Set 5 x 2 ml', 'Unnamed: 3': 2, 'Unnamed: 4': 70.0106, 'Unnamed: 5': nan, 'Unnamed: 6': nan, 'Unnamed: 7': nan, 'Unnamed: 8': nan, 'Unnamed: 9': nan, 'Unnamed: 10': nan, 'Unnamed: 11': nan, 'Unnamed: 12': nan, 'Unnamed: 13': 2, 'Unnamed: 14': 70.0106}, {'Unnamed: 0': nan, 'Unnamed: 1': 'Total', 'Unnamed: 2': nan, 'Unnamed: 3': 5, 'Unnamed: 4': 429.9977, 'Unnamed: 5': 4, 'Unnamed: 6': 906.5078000000001, 'Unnamed: 7': 4, 'Unnamed: 8': 980.0031999999999, 'Unnamed: 9': 1, 'Unnamed: 10': 245.00079999999997, 'Unnamed: 11': 1, 'Unnamed: 12': 245.00079999999997, 'Unnamed: 13': 15, 'Unnamed: 14': 2806.5102999999995}]
2025-07-04 13:02:56,191 - app.services.cleaning_service - INFO - Using vendor: cdlc
DEBUG: Extracting date from CDLC filename: 'BIBBI_Sell_Out_2025 04.xlsx'
DEBUG: Found date in filename - Year: 2025, Month: 4
DEBUG: CDLC processing for Year: 2025, Month: 4
DEBUG: Original DataFrame shape: (11, 15)
DEBUG: DataFrame columns: ['Unnamed: 0', 'Unnamed: 1', 'Unnamed: 2', 'Unnamed: 3', 'Unnamed: 4', 'Unnamed: 5', 'Unnamed: 6', 'Unnamed: 7', 'Unnamed: 8', 'Unnamed: 9', 'Unnamed: 10', 'Unnamed: 11', 'Unnamed: 12', 'Unnamed: 13', 'Unnamed: 14']
DEBUG: === HEADER PROCESSING STEP ===
DEBUG: Original DataFrame shape before header processing: (11, 15)
DEBUG: Skipping first 3 rows (0-2), keeping rows 3+ as header and data
DEBUG: Row 3 (header): [nan, '7350154320046', 'BIBBI. Swimming Pool EDP 100 ml', nan, nan, 3, 661.5070000000001, 2, 490.00159999999994, nan, nan, 1, 245.00079999999997, 6, 1396.5094]
DEBUG: Rows 4+ (data): 7 rows
DEBUG: Row 3: [nan, '7350154320046', 'BIBBI. Swimming Pool EDP 100 ml', nan, nan, 3, 661.5070000000001, 2, 490.00159999999994, nan, nan, 1, 245.00079999999997, 6, 1396.5094]
DEBUG: Row 4: [nan, '7350154320527', 'BIBBI. Fruit Captain EDP 100 ml', nan, nan, nan, nan, 2, 490.00159999999994, nan, nan, nan, nan, 2, 490.00159999999994]
DEBUG: Row 5: [nan, '7350154320053', 'BIBBI. Santal Beauty EDP 100 ml', nan, nan, 1, 245.00079999999997, nan, nan, nan, nan, nan, nan, 1, 245.00079999999997]
DEBUG: Row 6: [nan, '7350154320060', 'BIBBI. Boy of June EDP 100 ml', nan, nan, nan, nan, nan, nan, 1, 245.00079999999997, nan, nan, 1, 245.00079999999997]
DEBUG: Row 7: [nan, '7350154320343', 'BIBBI. Swimming Pool EDP 30 ml', 2, 239.9914, nan, nan, nan, nan, nan, nan, nan, nan, 2, 239.9914]
DEBUG: Row 8: [nan, '7350154320367', 'BIBBI. Boy of June EDP 30 ml', 1, 119.9957, nan, nan, nan, nan, nan, nan, nan, nan, 1, 119.9957]
DEBUG: Row 9: [nan, '7350154320503', 'BIBBI. Fragrance Discovery Set 5 x 2 ml', 2, 70.0106, nan, nan, nan, nan, nan, nan, nan, nan, 2, 70.0106]
DEBUG: After iloc[3:] - shape: (8, 15)
DEBUG: Setting column names from row 0: [nan, '7350154320046', 'BIBBI. Swimming Pool EDP 100 ml', nan, nan, 3, 661.5070000000001, 2, 490.00159999999994, nan, nan, 1, 245.00079999999997, 6, 1396.5094]
DEBUG: Before dropping header row - shape: (8, 15)
DEBUG: After dropping header row - final shape: (7, 15)
DEBUG: After header processing - DataFrame shape: (7, 15)
DEBUG: Column names after header processing: [nan, '7350154320046', 'BIBBI. Swimming Pool EDP 100 ml', nan, nan, 3, 661.5070000000001, 2, 490.00159999999994, nan, nan, 1, 245.00079999999997, 6, 1396.5094]
DEBUG: Expected 7 data rows, actual rows available: 7
DEBUG: All rows after header processing:
  Row 0: [nan, '7350154320527', 'BIBBI. Fruit Captain EDP 100 ml', nan, nan, nan, nan, 2, 490.00159999999994, nan, nan, nan, nan, 2, 490.00159999999994]
  Row 1: [nan, '7350154320053', 'BIBBI. Santal Beauty EDP 100 ml', nan, nan, 1, 245.00079999999997, nan, nan, nan, nan, nan, nan, 1, 245.00079999999997]
  Row 2: [nan, '7350154320060', 'BIBBI. Boy of June EDP 100 ml', nan, nan, nan, nan, nan, nan, 1, 245.00079999999997, nan, nan, 1, 245.00079999999997]
  Row 3: [nan, '7350154320343', 'BIBBI. Swimming Pool EDP 30 ml', 2, 239.9914, nan, nan, nan, nan, nan, nan, nan, nan, 2, 239.9914]
  Row 4: [nan, '7350154320367', 'BIBBI. Boy of June EDP 30 ml', 1, 119.9957, nan, nan, nan, nan, nan, nan, nan, nan, 1, 119.9957]
  Row 5: [nan, '7350154320503', 'BIBBI. Fragrance Discovery Set 5 x 2 ml', 2, 70.0106, nan, nan, nan, nan, nan, nan, nan, nan, 2, 70.0106]
  Row 6: [nan, 'Total', nan, 5, 429.9977, 4, 906.5078000000001, 4, 980.0031999999999, 1, 245.00079999999997, 1, 245.00079999999997, 15, 2806.5102999999995]

DEBUG: === PROCESSING ROW 0 (iteration 1) ===
DEBUG: Raw row data: [nan, '7350154320527', 'BIBBI. Fruit Captain EDP 100 ml', nan, nan, nan, nan, 2, 490.00159999999994, nan, nan, nan, nan, 2, 490.00159999999994]
DEBUG: Column 1 (EAN position) value: '7350154320527' (type: <class 'str'>)
DEBUG: Extracted EAN: '7350154320527' (length: 13)
DEBUG: ✓ Valid EAN: '7350154320527'
DEBUG: Product name (column 2): 'BIBBI. Fruit Captain EDP 100 ml'
DEBUG: Column 13 (Total Qty) raw value: '2' (type: <class 'int'>)
DEBUG: ✓ Parsed quantity: 2.0
DEBUG: Column 14 (Total Sales) raw value: '490.00159999999994' (type: <class 'float'>)
DEBUG: ✓ Parsed sales: 490.00159999999994
DEBUG: Final values - Qty: 2.0, Sales: 490.00159999999994
DEBUG: ✓ INCLUDING row 0 - has non-zero quantity or sales
DEBUG: ✓ ADDED to processed_rows - EAN: 7350154320527, Qty: 2.0, Sales: 490.00159999999994

DEBUG: === PROCESSING ROW 1 (iteration 2) ===
DEBUG: Raw row data: [nan, '7350154320053', 'BIBBI. Santal Beauty EDP 100 ml', nan, nan, 1, 245.00079999999997, nan, nan, nan, nan, nan, nan, 1, 245.00079999999997]
DEBUG: Column 1 (EAN position) value: '7350154320053' (type: <class 'str'>)
DEBUG: Extracted EAN: '7350154320053' (length: 13)
DEBUG: ✓ Valid EAN: '7350154320053'
DEBUG: Product name (column 2): 'BIBBI. Santal Beauty EDP 100 ml'
DEBUG: Column 13 (Total Qty) raw value: '1' (type: <class 'int'>)
DEBUG: ✓ Parsed quantity: 1.0
DEBUG: Column 14 (Total Sales) raw value: '245.00079999999997' (type: <class 'float'>)
DEBUG: ✓ Parsed sales: 245.00079999999997
DEBUG: Final values - Qty: 1.0, Sales: 245.00079999999997
DEBUG: ✓ INCLUDING row 1 - has non-zero quantity or sales
DEBUG: ✓ ADDED to processed_rows - EAN: 7350154320053, Qty: 1.0, Sales: 245.00079999999997

DEBUG: === PROCESSING ROW 2 (iteration 3) ===
DEBUG: Raw row data: [nan, '7350154320060', 'BIBBI. Boy of June EDP 100 ml', nan, nan, nan, nan, nan, nan, 1, 245.00079999999997, nan, nan, 1, 245.00079999999997]
DEBUG: Column 1 (EAN position) value: '7350154320060' (type: <class 'str'>)
DEBUG: Extracted EAN: '7350154320060' (length: 13)
DEBUG: ✓ Valid EAN: '7350154320060'
DEBUG: Product name (column 2): 'BIBBI. Boy of June EDP 100 ml'
DEBUG: Column 13 (Total Qty) raw value: '1' (type: <class 'int'>)
DEBUG: ✓ Parsed quantity: 1.0
DEBUG: Column 14 (Total Sales) raw value: '245.00079999999997' (type: <class 'float'>)
DEBUG: ✓ Parsed sales: 245.00079999999997
DEBUG: Final values - Qty: 1.0, Sales: 245.00079999999997
DEBUG: ✓ INCLUDING row 2 - has non-zero quantity or sales
DEBUG: ✓ ADDED to processed_rows - EAN: 7350154320060, Qty: 1.0, Sales: 245.00079999999997

DEBUG: === PROCESSING ROW 3 (iteration 4) ===
DEBUG: Raw row data: [nan, '7350154320343', 'BIBBI. Swimming Pool EDP 30 ml', 2, 239.9914, nan, nan, nan, nan, nan, nan, nan, nan, 2, 239.9914]
DEBUG: Column 1 (EAN position) value: '7350154320343' (type: <class 'str'>)
DEBUG: Extracted EAN: '7350154320343' (length: 13)
DEBUG: ✓ Valid EAN: '7350154320343'
DEBUG: Product name (column 2): 'BIBBI. Swimming Pool EDP 30 ml'
DEBUG: Column 13 (Total Qty) raw value: '2' (type: <class 'int'>)
DEBUG: ✓ Parsed quantity: 2.0
DEBUG: Column 14 (Total Sales) raw value: '239.9914' (type: <class 'float'>)
DEBUG: ✓ Parsed sales: 239.9914
DEBUG: Final values - Qty: 2.0, Sales: 239.9914
DEBUG: ✓ INCLUDING row 3 - has non-zero quantity or sales
DEBUG: ✓ ADDED to processed_rows - EAN: 7350154320343, Qty: 2.0, Sales: 239.9914

DEBUG: === PROCESSING ROW 4 (iteration 5) ===
DEBUG: Raw row data: [nan, '7350154320367', 'BIBBI. Boy of June EDP 30 ml', 1, 119.9957, nan, nan, nan, nan, nan, nan, nan, nan, 1, 119.9957]
DEBUG: Column 1 (EAN position) value: '7350154320367' (type: <class 'str'>)
DEBUG: Extracted EAN: '7350154320367' (length: 13)
DEBUG: ✓ Valid EAN: '7350154320367'
DEBUG: Product name (column 2): 'BIBBI. Boy of June EDP 30 ml'
DEBUG: Column 13 (Total Qty) raw value: '1' (type: <class 'int'>)
DEBUG: ✓ Parsed quantity: 1.0
DEBUG: Column 14 (Total Sales) raw value: '119.9957' (type: <class 'float'>)
DEBUG: ✓ Parsed sales: 119.9957
DEBUG: Final values - Qty: 1.0, Sales: 119.9957
DEBUG: ✓ INCLUDING row 4 - has non-zero quantity or sales
DEBUG: ✓ ADDED to processed_rows - EAN: 7350154320367, Qty: 1.0, Sales: 119.9957

DEBUG: === PROCESSING ROW 5 (iteration 6) ===
DEBUG: Raw row data: [nan, '7350154320503', 'BIBBI. Fragrance Discovery Set 5 x 2 ml', 2, 70.0106, nan, nan, nan, nan, nan, nan, nan, nan, 2, 70.0106]
DEBUG: Column 1 (EAN position) value: '7350154320503' (type: <class 'str'>)
DEBUG: Extracted EAN: '7350154320503' (length: 13)
DEBUG: ✓ Valid EAN: '7350154320503'
DEBUG: Product name (column 2): 'BIBBI. Fragrance Discovery Set 5 x 2 ml'
DEBUG: Column 13 (Total Qty) raw value: '2' (type: <class 'int'>)
DEBUG: ✓ Parsed quantity: 2.0
DEBUG: Column 14 (Total Sales) raw value: '70.0106' (type: <class 'float'>)
DEBUG: ✓ Parsed sales: 70.0106
DEBUG: Final values - Qty: 2.0, Sales: 70.0106
DEBUG: ✓ INCLUDING row 5 - has non-zero quantity or sales
DEBUG: ✓ ADDED to processed_rows - EAN: 7350154320503, Qty: 2.0, Sales: 70.0106

DEBUG: === PROCESSING ROW 6 (iteration 7) ===
DEBUG: Raw row data: [nan, 'Total', nan, 5, 429.9977, 4, 906.5078000000001, 4, 980.0031999999999, 1, 245.00079999999997, 1, 245.00079999999997, 15, 2806.5102999999995]
DEBUG: Column 1 (EAN position) value: 'Total' (type: <class 'str'>)
DEBUG: Extracted EAN: 'Total' (length: 5)
DEBUG: SKIPPING row 6 - EAN not all digits: 'Total'
DEBUG: === PROCESSING SUMMARY ===
DEBUG: Total rows processed: 7
DEBUG: Rows successfully added: 6
DEBUG: Rows skipped: 1
DEBUG: Reasons for skipping:
  - Row 6: EAN not digits - 'Total'

DEBUG: Created cleaned DataFrame with 6 rows
DEBUG: Common cleaning - quantity filtering. Rows before: 6
DEBUG: Common cleaning - converted quantity to numeric. Rows after: 6
2025-07-04 13:02:56,196 - app.services.cleaning_service - INFO - Cleaned 6 rows (original: 11)
2025-07-04 13:02:56,196 - app.services.cleaning_service - INFO - Transformations applied: 3
2025-07-04 13:02:56,196 - app.services.cleaning_service - INFO - Cleaned data columns: ['product_ean', 'functional_name', 'quantity', 'sales_lc', 'report_year', 'report_month', 'reseller', 'currency']
2025-07-04 13:02:56,197 - app.services.cleaning_service - INFO - Cleaned data sample: [{'product_ean': '7350154320527', 'functional_name': '', 'quantity': 2.0, 'sales_lc': 490.00159999999994, 'report_year': 2025, 'report_month': 4, 'reseller': 'Creme de la Creme', 'currency': 'EUR'}, {'product_ean': '7350154320053', 'functional_name': '', 'quantity': 1.0, 'sales_lc': 245.00079999999997, 'report_year': 2025, 'report_month': 4, 'reseller': 'Creme de la Creme', 'currency': 'EUR'}, {'product_ean': '7350154320060', 'functional_name': '', 'quantity': 1.0, 'sales_lc': 245.00079999999997, 'report_year': 2025, 'report_month': 4, 'reseller': 'Creme de la Creme', 'currency': 'EUR'}]
2025-07-04 13:02:56,197 - app.services.cleaning_service - INFO - Cleaned data types: {'product_ean': dtype('O'), 'functional_name': dtype('O'), 'quantity': dtype('float64'), 'sales_lc': dtype('float64'), 'report_year': dtype('int64'), 'report_month': dtype('int64'), 'reseller': dtype('O'), 'currency': dtype('O')}
DEBUG: Starting normalization for vendor 'cdlc' with 6 rows
DEBUG: Input columns: ['product_ean', 'functional_name', 'quantity', 'sales_lc', 'report_year', 'report_month', 'reseller', 'currency']
DEBUG: Sample input row: {'product_ean': '7350154320527', 'functional_name': '', 'quantity': 2.0, 'sales_lc': 490.00159999999994, 'report_year': 2025, 'report_month': 4, 'reseller': 'Creme de la Creme', 'currency': 'EUR'}
DEBUG: Preserved sales_lc for cdlc: ['490.00159999999994', '245.00079999999997', '245.00079999999997', '239.9914', '119.9957']
DEBUG: Zero quantity - Including 0 rows with sales, Excluding 0 rows without sales
DEBUG: Negative quantity - Including 0 rows with sales, Excluding 0 rows without sales
DEBUG: Normalization complete for vendor 'cdlc' - 6 rows
DEBUG: Final normalized columns: ['product_ean', 'year', 'month', 'quantity', 'sales_lc', 'functional_name', 'currency', 'reseller']
DEBUG: Sample normalized row: {'product_ean': '7350154320527', 'year': 2025, 'month': 4, 'quantity': 2, 'sales_lc': '490.00159999999994', 'functional_name': '', 'currency': 'EUR', 'reseller': 'Creme de la Creme'}
2025-07-04 13:02:56,207 - app.services.cleaning_service - INFO - Normalized 6 rows
2025-07-04 13:02:56,208 - app.services.cleaning_service - INFO - Normalized data sample: [{'product_ean': '7350154320527', 'year': 2025, 'month': 4, 'quantity': 2, 'sales_lc': '490.00159999999994', 'functional_name': '', 'currency': 'EUR', 'reseller': 'Creme de la Creme'}, {'product_ean': '7350154320053', 'year': 2025, 'month': 4, 'quantity': 1, 'sales_lc': '245.00079999999997', 'functional_name': '', 'currency': 'EUR', 'reseller': 'Creme de la Creme'}, {'product_ean': '7350154320060', 'year': 2025, 'month': 4, 'quantity': 1, 'sales_lc': '245.00079999999997', 'functional_name': '', 'currency': 'EUR', 'reseller': 'Creme de la Creme'}]
2025-07-04 13:02:56,208 - app.services.cleaning_service - INFO - Normalized columns: ['product_ean', 'year', 'month', 'quantity', 'sales_lc', 'functional_name', 'currency', 'reseller']
2025-07-04 13:02:56,208 - app.services.cleaning_service - INFO - Normalized data types: {'product_ean': dtype('O'), 'year': Int64Dtype(), 'month': Int64Dtype(), 'quantity': Int64Dtype(), 'sales_lc': dtype('O'), 'functional_name': dtype('O'), 'currency': dtype('O'), 'reseller': dtype('O')}
2025-07-04 13:02:56,209 - app.services.cleaning_service - INFO - All required fields present
2025-07-04 13:02:56,210 - app.services.cleaning_service - INFO - Converting 6 entries for database insertion
2025-07-04 13:02:56,210 - app.services.cleaning_service - INFO - Sample entry for insertion: {'product_ean': '7350154320527', 'year': 2025, 'month': 4, 'quantity': 2, 'sales_lc': '490.00159999999994', 'functional_name': '', 'currency': 'EUR', 'reseller': 'Creme de la Creme'}
2025-07-04 13:02:56,210 - app.services.cleaning_service - INFO - Attempting to insert 6 entries into sellout_entries2
DB Service: Starting insert_sellout_entries for upload b6e90a95-3a25-41c4-9cae-f9e7e9deb7b4 with 6 entries
DB Service: Ensuring products exist...
2025-07-04 13:02:56,289 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/products?select=ean&ean=in.%287350154320503%2C7350154320367%2C7350154320343%2C7350154320053%2C7350154320527%2C7350154320060%29 "HTTP/2 200 OK"
DB Service: Products ensured successfully
DB Service: Entry 0: {'upload_id': 'b6e90a95-3a25-41c4-9cae-f9e7e9deb7b4', 'product_ean': '7350154320527', 'month': 4, 'year': 2025, 'quantity': 2, 'sales_lc': '490.00159999999994', 'currency': 'EUR', 'reseller': 'Creme de la Creme', 'functional_name': ''}
DB Service: Entry 1: {'upload_id': 'b6e90a95-3a25-41c4-9cae-f9e7e9deb7b4', 'product_ean': '7350154320053', 'month': 4, 'year': 2025, 'quantity': 1, 'sales_lc': '245.00079999999997', 'currency': 'EUR', 'reseller': 'Creme de la Creme', 'functional_name': ''}
DB Service: Entry 2: {'upload_id': 'b6e90a95-3a25-41c4-9cae-f9e7e9deb7b4', 'product_ean': '7350154320060', 'month': 4, 'year': 2025, 'quantity': 1, 'sales_lc': '245.00079999999997', 'currency': 'EUR', 'reseller': 'Creme de la Creme', 'functional_name': ''}
DB Service: Prepared 6 entries for insertion
DB Service: Inserting batch 1 with 6 entries
2025-07-04 13:02:56,442 - httpx - INFO - HTTP Request: POST https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/sellout_entries2?columns=%22month%22%2C%22upload_id%22%2C%22quantity%22%2C%22year%22%2C%22currency%22%2C%22sales_lc%22%2C%22reseller%22%2C%22functional_name%22%2C%22product_ean%22 "HTTP/2 201 Created"
DB Service: Batch insert result: data=[{'id': '4056a8a9-8ec3-40b2-84de-72438532753c', 'product_ean': '7350154320527', 'month': 4, 'year': 2025, 'quantity': 2, 'sales_lc': '490.00159999999994', 'sales_eur': None, 'currency': 'EUR', 'created_at': '2025-07-04T11:02:56.472904', 'reseller': 'Creme de la Creme', 'functional_name': '', 'upload_id': 'b6e90a95-3a25-41c4-9cae-f9e7e9deb7b4'}, {'id': '315fae85-cc56-49de-9946-b7140522f844', 'product_ean': '7350154320053', 'month': 4, 'year': 2025, 'quantity': 1, 'sales_lc': '245.00079999999997', 'sales_eur': None, 'currency': 'EUR', 'created_at': '2025-07-04T11:02:56.472904', 'reseller': 'Creme de la Creme', 'functional_name': '', 'upload_id': 'b6e90a95-3a25-41c4-9cae-f9e7e9deb7b4'}, {'id': '04aedbe8-b189-4566-b32f-6baf16ea4956', 'product_ean': '7350154320060', 'month': 4, 'year': 2025, 'quantity': 1, 'sales_lc': '245.00079999999997', 'sales_eur': None, 'currency': 'EUR', 'created_at': '2025-07-04T11:02:56.472904', 'reseller': 'Creme de la Creme', 'functional_name': '', 'upload_id': 'b6e90a95-3a25-41c4-9cae-f9e7e9deb7b4'}, {'id': '456b75b8-00d3-4b2d-aee8-6f9cf658021e', 'product_ean': '7350154320343', 'month': 4, 'year': 2025, 'quantity': 2, 'sales_lc': '239.9914', 'sales_eur': None, 'currency': 'EUR', 'created_at': '2025-07-04T11:02:56.472904', 'reseller': 'Creme de la Creme', 'functional_name': '', 'upload_id': 'b6e90a95-3a25-41c4-9cae-f9e7e9deb7b4'}, {'id': '8608bafd-8e30-4620-bea8-fe370788f953', 'product_ean': '7350154320367', 'month': 4, 'year': 2025, 'quantity': 1, 'sales_lc': '119.9957', 'sales_eur': None, 'currency': 'EUR', 'created_at': '2025-07-04T11:02:56.472904', 'reseller': 'Creme de la Creme', 'functional_name': '', 'upload_id': 'b6e90a95-3a25-41c4-9cae-f9e7e9deb7b4'}, {'id': '06b9323c-25e5-43d6-9e5c-46e3970ad759', 'product_ean': '7350154320503', 'month': 4, 'year': 2025, 'quantity': 2, 'sales_lc': '70.0106', 'sales_eur': None, 'currency': 'EUR', 'created_at': '2025-07-04T11:02:56.472904', 'reseller': 'Creme de la Creme', 'functional_name': '', 'upload_id': 'b6e90a95-3a25-41c4-9cae-f9e7e9deb7b4'}] count=None
DB Service: Successfully inserted 6 total entries
2025-07-04 13:02:56,446 - app.services.cleaning_service - INFO - Successfully inserted 6 entries into sellout_entries2
2025-07-04 13:02:56,447 - app.services.cleaning_service - INFO - Logging 3 transformations
2025-07-04 13:02:56,514 - httpx - INFO - HTTP Request: POST https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/transform_logs "HTTP/2 201 Created"
2025-07-04 13:02:56,585 - httpx - INFO - HTTP Request: POST https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/transform_logs "HTTP/2 201 Created"
2025-07-04 13:02:56,660 - httpx - INFO - HTTP Request: POST https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/transform_logs "HTTP/2 201 Created"
2025-07-04 13:02:56,663 - app.services.cleaning_service - INFO - Transformations logged successfully
2025-07-04 13:02:56,750 - httpx - INFO - HTTP Request: PATCH https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/uploads?id=eq.b6e90a95-3a25-41c4-9cae-f9e7e9deb7b4 "HTTP/2 200 OK"
2025-07-04 13:02:56,751 - app.services.cleaning_service - INFO - Successfully processed upload b6e90a95-3a25-41c4-9cae-f9e7e9deb7b4 - 11 original rows, 6 cleaned, 6 inserted
2025-07-04 13:02:59,295 - app.api.auth - INFO - get_current_user called
2025-07-04 13:02:59,295 - app.api.auth - INFO - Authorization header: Bearer eyJhbGciOiJIUzI1NiIsImtpZCI6InJMelFCZWp1WXZ...
2025-07-04 13:02:59,295 - app.api.auth - INFO - Extracted token length: 722
2025-07-04 13:02:59,295 - app.services.auth_service - INFO - Attempting token verification for token starting with: eyJhbGciOiJIUzI1NiIs...
2025-07-04 13:02:59,474 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/auth/v1/user "HTTP/2 200 OK"
2025-07-04 13:02:59,475 - app.services.auth_service - INFO - Token verification successful for user: user@email.com
2025-07-04 13:02:59,475 - app.api.auth - INFO - Successfully authenticated user: user@email.com
2025-07-04 13:02:59,758 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/uploads?select=%2A&user_id=eq.26d3c1b7-d944-42a0-9336-e68b1b32ebbf&order=uploaded_at.desc "HTTP/2 200 OK"
INFO:     127.0.0.1:56544 - "GET /api/status/uploads HTTP/1.1" 200 OK
2025-07-04 13:02:59,916 - app.api.auth - INFO - get_current_user called
2025-07-04 13:02:59,916 - app.api.auth - INFO - Authorization header: Bearer eyJhbGciOiJIUzI1NiIsImtpZCI6InJMelFCZWp1WXZ...
2025-07-04 13:02:59,916 - app.api.auth - INFO - Extracted token length: 722
2025-07-04 13:02:59,916 - app.services.auth_service - INFO - Attempting token verification for token starting with: eyJhbGciOiJIUzI1NiIs...
2025-07-04 13:03:00,063 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/auth/v1/user "HTTP/2 200 OK"
2025-07-04 13:03:00,064 - app.services.auth_service - INFO - Token verification successful for user: user@email.com
2025-07-04 13:03:00,064 - app.api.auth - INFO - Successfully authenticated user: user@email.com
2025-07-04 13:03:00,333 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/uploads?select=%2A&user_id=eq.26d3c1b7-d944-42a0-9336-e68b1b32ebbf&order=uploaded_at.desc "HTTP/2 200 OK"
INFO:     127.0.0.1:56546 - "GET /api/status/uploads HTTP/1.1" 200 OK
2025-07-04 13:03:30,248 - app.api.auth - INFO - get_current_user called
2025-07-04 13:03:30,248 - app.api.auth - INFO - Authorization header: Bearer eyJhbGciOiJIUzI1NiIsImtpZCI6InJMelFCZWp1WXZ...
2025-07-04 13:03:30,248 - app.api.auth - INFO - Extracted token length: 722
2025-07-04 13:03:30,248 - app.services.auth_service - INFO - Attempting token verification for token starting with: eyJhbGciOiJIUzI1NiIs...
2025-07-04 13:03:30,401 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/auth/v1/user "HTTP/2 200 OK"
2025-07-04 13:03:30,402 - app.services.auth_service - INFO - Token verification successful for user: user@email.com
2025-07-04 13:03:30,402 - app.api.auth - INFO - Successfully authenticated user: user@email.com
2025-07-04 13:03:30,726 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/uploads?select=%2A&user_id=eq.26d3c1b7-d944-42a0-9336-e68b1b32ebbf&order=uploaded_at.desc "HTTP/2 200 OK"
INFO:     127.0.0.1:52326 - "GET /api/status/uploads HTTP/1.1" 200 OK
2025-07-04 13:04:00,235 - app.api.auth - INFO - get_current_user called
2025-07-04 13:04:00,235 - app.api.auth - INFO - Authorization header: Bearer eyJhbGciOiJIUzI1NiIsImtpZCI6InJMelFCZWp1WXZ...
2025-07-04 13:04:00,235 - app.api.auth - INFO - Extracted token length: 722
2025-07-04 13:04:00,235 - app.services.auth_service - INFO - Attempting token verification for token starting with: eyJhbGciOiJIUzI1NiIs...
2025-07-04 13:04:00,400 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/auth/v1/user "HTTP/2 200 OK"
2025-07-04 13:04:00,400 - app.services.auth_service - INFO - Token verification successful for user: user@email.com
2025-07-04 13:04:00,400 - app.api.auth - INFO - Successfully authenticated user: user@email.com
2025-07-04 13:04:00,759 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/uploads?select=%2A&user_id=eq.26d3c1b7-d944-42a0-9336-e68b1b32ebbf&order=uploaded_at.desc "HTTP/2 200 OK"
INFO:     127.0.0.1:39472 - "GET /api/status/uploads HTTP/1.1" 200 OK
2025-07-04 13:04:30,234 - app.api.auth - INFO - get_current_user called
2025-07-04 13:04:30,234 - app.api.auth - INFO - Authorization header: Bearer eyJhbGciOiJIUzI1NiIsImtpZCI6InJMelFCZWp1WXZ...
2025-07-04 13:04:30,234 - app.api.auth - INFO - Extracted token length: 722
2025-07-04 13:04:30,234 - app.services.auth_service - INFO - Attempting token verification for token starting with: eyJhbGciOiJIUzI1NiIs...
2025-07-04 13:04:30,374 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/auth/v1/user "HTTP/2 200 OK"
2025-07-04 13:04:30,375 - app.services.auth_service - INFO - Token verification successful for user: user@email.com
2025-07-04 13:04:30,375 - app.api.auth - INFO - Successfully authenticated user: user@email.com
2025-07-04 13:04:30,634 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/uploads?select=%2A&user_id=eq.26d3c1b7-d944-42a0-9336-e68b1b32ebbf&order=uploaded_at.desc "HTTP/2 200 OK"
INFO:     127.0.0.1:49356 - "GET /api/status/uploads HTTP/1.1" 200 OK