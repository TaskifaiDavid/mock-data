2025-07-05 22:19:48,654 - app.api.auth - INFO - get_current_user called
2025-07-05 22:19:48,654 - app.api.auth - INFO - Authorization header: Bearer eyJhbGciOiJIUzI1NiIsImtpZCI6InJMelFCZWp1WXZ...
2025-07-05 22:19:48,654 - app.api.auth - INFO - Extracted token length: 722
2025-07-05 22:19:48,654 - app.services.auth_service - INFO - Attempting token verification for token starting with: eyJhbGciOiJIUzI1NiIs...
2025-07-05 22:19:48,753 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/auth/v1/user "HTTP/2 200 OK"
2025-07-05 22:19:48,754 - app.services.auth_service - INFO - Token verification successful for user: user@email.com
2025-07-05 22:19:48,754 - app.api.auth - INFO - Successfully authenticated user: user@email.com
2025-07-05 22:19:48,922 - watchfiles.main - INFO - 1 change detected
2025-07-05 22:19:48,968 - httpx - INFO - HTTP Request: POST https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/uploads "HTTP/2 201 Created"
INFO:     127.0.0.1:34800 - "POST /api/upload/ HTTP/1.1" 200 OK
2025-07-05 22:19:48,970 - app.services.cleaning_service - INFO - Starting background task for upload b2f2b041-bfc8-4d65-a95b-1cdd4db9dc5a, filename: bibbi sales march'25 (4).xlsx, user: 26d3c1b7-d944-42a0-9336-e68b1b32ebbf
2025-07-05 22:19:49,101 - httpx - INFO - HTTP Request: PATCH https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/uploads?id=eq.b2f2b041-bfc8-4d65-a95b-1cdd4db9dc5a "HTTP/2 200 OK"
2025-07-05 22:19:49,102 - app.services.cleaning_service - INFO - Updated upload b2f2b041-bfc8-4d65-a95b-1cdd4db9dc5a status to PROCESSING
2025-07-05 22:19:49,156 - app.services.cleaning_service - INFO - Excel file sheet names: ['TDSheet']
2025-07-05 22:19:49,156 - app.services.cleaning_service - INFO - Detected vendor from filename and sheet names: aromateque
2025-07-05 22:19:49,156 - app.services.cleaning_service - INFO - Found 'TDSheet' sheet for Aromateque: TDSheet
2025-07-05 22:19:49,186 - app.services.cleaning_service - INFO - Read Aromateque file as text to preserve Ukrainian headers
2025-07-05 22:19:49,187 - app.services.cleaning_service - INFO - Loaded Excel sheet 'TDSheet' with 32 rows, columns: [0, 1, 2, 3, 4, 5, 6, 7]
2025-07-05 22:19:49,187 - app.services.cleaning_service - INFO - First 3 rows preview: [{0: nan, 1: 'Store', 2: '2025-01-01 00:00:00', 3: '2025-02-01 00:00:00', 4: '2025-03-01 00:00:00', 5: '2025-04-01 00:00:00', 6: 'total', 7: nan}, {0: nan, 1: 'Blockbuster Mall', 2: nan, 3: nan, 4: '16', 5: '4', 6: '20', 7: nan}, {0: nan, 1: 'Dnipro', 2: '3', 3: nan, 4: '9', 5: '3', 6: '15', 7: nan}]
2025-07-05 22:19:49,187 - app.services.cleaning_service - INFO - Data types: {0: dtype('O'), 1: dtype('O'), 2: dtype('O'), 3: dtype('O'), 4: dtype('O'), 5: dtype('O'), 6: dtype('O'), 7: dtype('O')}
2025-07-05 22:19:49,187 - app.services.cleaning_service - INFO - Column data distribution:
2025-07-05 22:19:49,187 - app.services.cleaning_service - INFO -   0: 19/32 non-empty values
2025-07-05 22:19:49,188 - app.services.cleaning_service - INFO -   1: 29/32 non-empty values
2025-07-05 22:19:49,188 - app.services.cleaning_service - INFO -   2: 17/32 non-empty values
2025-07-05 22:19:49,188 - app.services.cleaning_service - INFO -   3: 22/32 non-empty values
2025-07-05 22:19:49,188 - app.services.cleaning_service - INFO -   4: 28/32 non-empty values
2025-07-05 22:19:49,188 - app.services.cleaning_service - INFO -   5: 22/32 non-empty values
2025-07-05 22:19:49,188 - app.services.cleaning_service - INFO -   6: 31/32 non-empty values
2025-07-05 22:19:49,188 - app.services.cleaning_service - INFO -   7: 21/32 non-empty values
2025-07-05 22:19:49,189 - app.services.cleaning_service - INFO - Last 3 rows preview: [{0: 'BIBBI PARFUM Fruit Captain EAU DE PARFUM 10 ML                                                                                                        ', 1: 'BBFC10', 2: nan, 3: '1', 4: '48', 5: '7', 6: '56', 7: '2520'}, {0: 'BIBBI PARFUM Fruit Captain EAU DE PARFUM 100 ML                                                                                                       ', 1: 'BBFC100', 2: nan, 3: '1', 4: '24', 5: '4', 6: '29', 7: '7105'}, {0: nan, 1: nan, 2: '15', 3: '23', 4: '140', 5: '26', 6: '204', 7: '26950'}]
2025-07-05 22:19:49,189 - app.services.cleaning_service - INFO - Using vendor: aromateque
2025-07-05 22:19:49,189 - app.services.cleaning_service - INFO - Vendor detection details - filename: 'bibbi sales march'25 (4).xlsx', sheet_names: ['TDSheet']
2025-07-05 22:19:49,189 - app.services.cleaning_service - INFO - Starting data cleaning for vendor 'aromateque' with 32 rows
DEBUG: Applying vendor-specific cleaning for vendor: 'aromateque'
DEBUG: Using _clean_aromateque_data()
DEBUG: Extracting date from Aromateque filename: 'bibbi sales march'25 (4).xlsx'
DEBUG: Found month'YY format - Month: march (3), Year: 2025
DEBUG: Aromateque processing for Year: 2025, Month: 3
DEBUG: Original DataFrame shape: (31, 8)
DEBUG: DataFrame columns: [0, 1, 2, 3, 4, 5, 6, 7]
DEBUG: === HEADER PROCESSING STEP ===
DEBUG: Original DataFrame shape before header processing: (31, 8)
DEBUG: DataFrame read with header=None, all columns are numeric indices
DEBUG: Using row 11 as header (per profile specification)
DEBUG: Skipping rows 0-10 (store summary data)
DEBUG: Row 11 (header): ['BIBBI PARFUM Boy of June EAU DE PARFUM 100 ML                                                                                                         ', 'BBBOJ100', '2', '4', '2', nan, '8', '1960']
DEBUG: Rows 12+ (product data): 19 rows
DEBUG: Row 0: [nan, 'Store', '2025-01-01 00:00:00', '2025-02-01 00:00:00', '2025-03-01 00:00:00', '2025-04-01 00:00:00', 'total', nan]
DEBUG: Row 1: [nan, 'Blockbuster Mall', nan, nan, '16', '4', '20', nan]
DEBUG: Row 2: [nan, 'Dnipro', '3', nan, '9', '3', '15', nan]
DEBUG: Row 3: [nan, 'Online', '1', '4', '19', '3', '27', nan]
DEBUG: Row 4: [nan, 'Kyiv LU', '3', '2', '7', '2', '14', nan]
DEBUG: Row 5: [nan, 'Lavina Mall', nan, '1', '27', '1', '29', nan]
DEBUG: Row 6: [nan, 'Respublika', '3', '5', '19', '3', '30', nan]
DEBUG: Row 7: [nan, 'River Mall', '2', '4', '9', nan, '15', nan]
DEBUG: Row 8: [nan, 'TSUM', '3', '7', '34', '10', '54', nan]
DEBUG: Row 9: [nan, 'total', '15', '23', '140', '26', '204', nan]
DEBUG: Row 10: [nan, nan, '2025-01-01 00:00:00', '2025-02-01 00:00:00', '2025-03-01 00:00:00', '2025-04-01 00:00:00', 'total', 'Total in euro']
DEBUG: Row 11: ['BIBBI PARFUM Boy of June EAU DE PARFUM 100 ML                                                                                                         ', 'BBBOJ100', '2', '4', '2', nan, '8', '1960']
DEBUG: Row 12: ['BIBBI PARFUM Boy of June EAU DE PARFUM 30 ML                                                                                                          ', 'BBBOJ30', '1', nan, '5', nan, '6', '720']
DEBUG: Row 13: ['BIBBI PARFUM Wolf Mother Bougie Parfumee 310 Gr                                                                                                       ', 'BBWMC3', nan, '1', nan, nan, '1', '110']
DEBUG: Row 14: ['BIBBI PARFUM Ghost of Tom EAU DE PARFUM 100 ML                                                                                                        ', 'BBGOT100', '2', '3', '4', '1', '10', '2450']
DEBUG: After iloc[11:] - shape: (20, 8)
DEBUG: Setting column names from row 0 (original row 11): ['BIBBI PARFUM Boy of June EAU DE PARFUM 100 ML                                                                                                         ', 'BBBOJ100', '2', '4', '2', nan, '8', '1960']
DEBUG: Cleaned column names: ['BIBBI PARFUM Boy of June EAU DE PARFUM 100 ML', 'BBBOJ100', '2', '4', '2', 'Unnamed_5', '8', '1960']
DEBUG: Before dropping header row - shape: (20, 8)
DEBUG: After dropping header row - final shape: (19, 8)
DEBUG: After header processing - DataFrame shape: (19, 8)
DEBUG: Column names after header processing: ['BIBBI PARFUM Boy of June EAU DE PARFUM 100 ML', 'BBBOJ100', '2', '4', '2', 'Unnamed_5', '8', '1960']
DEBUG: Detailed column analysis:
  Column 0: 'BIBBI PARFUM Boy of June EAU DE PARFUM 100 ML' (type: <class 'str'>, str: 'BIBBI PARFUM Boy of June EAU DE PARFUM 100 ML')
  Column 1: 'BBBOJ100' (type: <class 'str'>, str: 'BBBOJ100')
  Column 2: '2' (type: <class 'str'>, str: '2')
  Column 3: '4' (type: <class 'str'>, str: '4')
  Column 4: '2' (type: <class 'str'>, str: '2')
  Column 5: 'Unnamed_5' (type: <class 'str'>, str: 'Unnamed_5')
  Column 6: '8' (type: <class 'str'>, str: '8')
  Column 7: '1960' (type: <class 'str'>, str: '1960')
DEBUG: Month 3 -> Ukrainian: 'березня' -> Target text: 'березня-25'
DEBUG: Month 3 -> Target datetime: 2025-03-01 00:00:00
DEBUG: Searching for target column...
  Column 0 name: 'BIBBI PARFUM Boy of June EAU DE PARFUM 100 ML' == 'березня-25' ? False
  Column 1 name: 'BBBOJ100' == 'березня-25' ? False
  Column 2 name: '2' == 'березня-25' ? False
  Column 3 name: '4' == 'березня-25' ? False
  Column 4 name: '2' == 'березня-25' ? False
  Column 5 name: 'Unnamed_5' == 'березня-25' ? False
  Column 6 name: '8' == 'березня-25' ? False
  Column 7 name: '1960' == 'березня-25' ? False
DEBUG: Column names don't match text, checking for datetime objects...
  Column 0 name: 'BIBBI PARFUM Boy of June EAU DE PARFUM 100 ML' (type: <class 'str'>)
  Column 1 name: 'BBBOJ100' (type: <class 'str'>)
  Column 2 name: '2' (type: <class 'str'>)
  Column 3 name: '4' (type: <class 'str'>)
  Column 4 name: '2' (type: <class 'str'>)
  Column 5 name: 'Unnamed_5' (type: <class 'str'>)
  Column 6 name: '8' (type: <class 'str'>)
  Column 7 name: '1960' (type: <class 'str'>)
DEBUG: Column names don't match, checking first row values for Ukrainian text...
  Column 0 value: 'BIBBI PARFUM Boy of June EAU DE PARFUM 30 ML' == 'березня-25' ? False
  Column 1 value: 'BBBOJ30' == 'березня-25' ? False
  Column 2 value: '1' == 'березня-25' ? False
  Column 3 value: 'None' == 'березня-25' ? False
  Column 4 value: '5' == 'березня-25' ? False
  Column 5 value: 'None' == 'березня-25' ? False
  Column 6 value: '6' == 'березня-25' ? False
  Column 7 value: '720' == 'березня-25' ? False
DEBUG: Target date column березня-25 not found, available columns: ['BIBBI PARFUM Boy of June EAU DE PARFUM 100 ML', 'BBBOJ100', '2', '4', '2', 'Unnamed_5', '8', '1960']
DEBUG: Final attempt - checking for datetime strings in columns...
ERROR: Could not find target date column, returning empty DataFrame
2025-07-05 22:19:49,192 - app.services.cleaning_service - INFO - Cleaned 0 rows (original: 32)
2025-07-05 22:19:49,192 - app.services.cleaning_service - INFO - Transformations applied: 0
2025-07-05 22:19:49,192 - app.services.cleaning_service - INFO - Cleaned data columns: []
2025-07-05 22:19:49,192 - app.services.cleaning_service - WARNING - No rows left after cleaning!
2025-07-05 22:19:49,192 - app.services.cleaning_service - INFO - Starting data normalization for vendor 'aromateque' with 0 cleaned rows
DEBUG: Starting normalization for vendor 'aromateque' with 0 rows
DEBUG: Input columns: []
DEBUG: Normalization complete for vendor 'aromateque' - 0 rows
DEBUG: Final normalized columns: ['reseller', 'currency']
WARNING: No rows in normalized data - all data was filtered out!
2025-07-05 22:19:49,193 - app.services.cleaning_service - INFO - Normalized 0 rows
2025-07-05 22:19:49,193 - app.services.cleaning_service - WARNING - No rows left after normalization!
2025-07-05 22:19:49,193 - app.services.cleaning_service - INFO - Converting 0 entries for database insertion
2025-07-05 22:19:49,193 - app.services.cleaning_service - WARNING - No entries to insert - processing completed with 0 records
2025-07-05 22:19:49,229 - httpx - INFO - HTTP Request: PATCH https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/uploads?id=eq.b2f2b041-bfc8-4d65-a95b-1cdd4db9dc5a "HTTP/2 200 OK"
2025-07-05 22:19:49,231 - app.services.cleaning_service - INFO - Successfully processed upload b2f2b041-bfc8-4d65-a95b-1cdd4db9dc5a - 32 original rows, 0 cleaned, 0 inserted