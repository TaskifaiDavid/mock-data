025-08-01 14:27:53,307 - app.services.db_service - WARNING - Failed to log processing step: {}
DEBUG: Starting normalization for vendor 'skins_nl' with 31 rows
DEBUG: Input columns: ['Brand', 'Article', 'functional_name', 'sales_lc', 'SalesAmountSPLY', 'SalesAmountVariance', 'quantity', 'SalesQuantitySPLY', 'SalesQuantityVariance', 'report_year', 'report_month', 'reseller', 'currency', 'product_ean']
DEBUG: Sample input row: {'Brand': 'TaskifAI', 'Article': 'Article 2', 'functional_name': 'PRDT35', 'sales_lc': '116.0', 'SalesAmountSPLY': 142.0, 'SalesAmountVariance': -0.181, 'quantity': 2.0, 'SalesQuantitySPLY': 2.0, 'SalesQuantityVariance': 0.0, 'report_year': 2025, 'report_month': 4, 'reseller': 'TaskifAI', 'currency': 'EUR', 'product_ean': ''}
DEBUG: Preserved sales_lc for skins_nl: ['116.0', '58.0', '58.0', '174.0', '2028.0']
DEBUG: Added sales_eur conversion for skins_nl EUR data
DEBUG: Zero quantity - Including 0 rows with sales, Excluding 0 rows without sales
DEBUG: Negative quantity - Including 0 rows with sales, Excluding 0 rows without sales
DEBUG: Normalization complete for vendor 'skins_nl' - 31 rows
DEBUG: Final normalized columns: ['product_ean', 'year', 'month', 'quantity', 'sales_lc', 'functional_name', 'currency', 'sales_eur', 'reseller']
DEBUG: Sample normalized row: {'product_ean': '', 'year': 2025, 'month': 4, 'quantity': 2, 'sales_lc': '116.0', 'functional_name': 'PRDT35', 'currency': 'EUR', 'sales_eur': 116.0, 'reseller': 'TaskifAI'}
2025-08-01 14:27:53,313 - app.services.cleaning_service - INFO - Normalized 31 rows
2025-08-01 14:27:53,353 - httpx - INFO - HTTP Request: POST https://nrkodllueunpbiotjbql.supabase.co/rest/v1/processing_logs "HTTP/2 404 Not Found"
2025-08-01 14:27:53,353 - app.services.db_service - WARNING - Failed to log processing step: {}
2025-08-01 14:27:53,355 - app.services.cleaning_service - INFO - Normalized data sample: [{'product_ean': '', 'year': 2025, 'month': 4, 'quantity': 2, 'sales_lc': '116.0', 'functional_name': 'PRDT35', 'currency': 'EUR', 'sales_eur': 116.0, 'reseller': 'TaskifAI'}, {'product_ean': '', 'year': 2025, 'month': 4, 'quantity': 1, 'sales_lc': '58.0', 'functional_name': 'PRGL40', 'currency': 'EUR', 'sales_eur': 58.0, 'reseller': 'TaskifAI'}, {'product_ean': '', 'year': 2025, 'month': 4, 'quantity': 1, 'sales_lc': '58.0', 'functional_name': 'PRBT75', 'currency': 'EUR', 'sales_eur': 58.0, 'reseller': 'TaskifAI'}]
2025-08-01 14:27:53,355 - app.services.cleaning_service - INFO - Normalized columns: ['product_ean', 'year', 'month', 'quantity', 'sales_lc', 'functional_name', 'currency', 'sales_eur', 'reseller']
2025-08-01 14:27:53,355 - app.services.cleaning_service - INFO - Normalized data types: {'product_ean': dtype('O'), 'year': Int64Dtype(), 'month': Int64Dtype(), 'quantity': Int64Dtype(), 'sales_lc': dtype('O'), 'functional_name': dtype('O'), 'currency': dtype('O'), 'sales_eur': dtype('float64'), 'reseller': dtype('O')}
2025-08-01 14:27:53,355 - app.services.cleaning_service - INFO - All required fields present
2025-08-01 14:27:53,356 - app.services.cleaning_service - INFO - Converting 31 entries for database insertion
2025-08-01 14:27:53,356 - app.services.cleaning_service - INFO - Sample entry for insertion: {'product_ean': '', 'year': 2025, 'month': 4, 'quantity': 2, 'sales_lc': '116.0', 'functional_name': 'PRDT35', 'currency': 'EUR', 'sales_eur': 116.0, 'reseller': 'TaskifAI'}
2025-08-01 14:27:53,356 - app.services.cleaning_service - INFO - Attempting to insert 31 entries into mock_data
2025-08-01 14:27:53,397 - httpx - INFO - HTTP Request: POST https://nrkodllueunpbiotjbql.supabase.co/rest/v1/processing_logs "HTTP/2 404 Not Found"
2025-08-01 14:27:53,398 - app.services.db_service - WARNING - Failed to log processing step: {}
DB Service: Starting insert_mock_data for upload d8149398-d9d8-4c85-b80a-c1fbef5edd31 with 31 entries
DB Service: Sample mock_data entry: {'id': 'c436155a-3650-4ac1-ad3c-73a151c75132', 'product_ean': '', 'month': 4, 'year': 2025, 'quantity': 2, 'sales_lc': '116.0', 'sales_eur': 116.0, 'currency': 'EUR', 'reseller': 'TaskifAI', 'functional_name': 'PRDT35', 'sales_date': datetime.date(2025, 4, 1), 'upload_id': 'd8149398-d9d8-4c85-b80a-c1fbef5edd31'}
DB Service: Error inserting mock data: Object of type date is not JSON serializable
DB Service: Full traceback: {}
2025-08-01 14:27:53,402 - app.services.cleaning_service - ERROR - Error processing upload d8149398-d9d8-4c85-b80a-c1fbef5edd31: Failed to insert mock data: Object of type date is not JSON serializable
2025-08-01 14:27:53,402 - app.services.cleaning_service - ERROR - Full traceback: Traceback (most recent call last):
  File "/home/david/mockDataRepo/backend/app/services/db_service.py", line 371, in insert_mock_data
    result = self.service_supabase.table("mock_data").insert(mock_data_entries).execute()
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/david/mockDataRepo/backend/venv/lib/python3.12/site-packages/postgrest/_sync/request_builder.py", line 58, in execute
    r = self.session.request(
        ^^^^^^^^^^^^^^^^^^^^^
  File "/home/david/mockDataRepo/backend/venv/lib/python3.12/site-packages/httpx/_client.py", line 824, in request
    request = self.build_request(
              ^^^^^^^^^^^^^^^^^^^
  File "/home/david/mockDataRepo/backend/venv/lib/python3.12/site-packages/httpx/_client.py", line 358, in build_request
    return Request(
           ^^^^^^^^
  File "/home/david/mockDataRepo/backend/venv/lib/python3.12/site-packages/httpx/_models.py", line 342, in __init__
    headers, stream = encode_request(
                      ^^^^^^^^^^^^^^^
  File "/home/david/mockDataRepo/backend/venv/lib/python3.12/site-packages/httpx/_content.py", line 214, in encode_request
    return encode_json(json)
           ^^^^^^^^^^^^^^^^^
  File "/home/david/mockDataRepo/backend/venv/lib/python3.12/site-packages/httpx/_content.py", line 177, in encode_json
    body = json_dumps(json).encode("utf-8")
           ^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/json/__init__.py", line 231, in dumps
    return _default_encoder.encode(obj)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/json/encoder.py", line 200, in encode
    chunks = self.iterencode(o, _one_shot=True)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/json/encoder.py", line 258, in iterencode
    return _iterencode(o, 0)
           ^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/json/encoder.py", line 180, in default
    raise TypeError(f'Object of type {o.__class__.__name__} '
TypeError: Object of type date is not JSON serializable

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/david/mockDataRepo/backend/app/services/cleaning_service.py", line 213, in process_file
    await self.db_service.insert_mock_data(upload_id, sellout_entries)
  File "/home/david/mockDataRepo/backend/app/services/db_service.py", line 379, in insert_mock_data
    raise DatabaseException(f"Failed to insert mock data: {str(e)}")
app.utils.exceptions.DatabaseException: Failed to insert mock data: Object of type date is not JSON serializable

2025-08-01 14:27:53,457 - httpx - INFO - HTTP Request: PATCH https://nrkodllueunpbiotjbql.supabase.co/rest/v1/uploads?id=eq.d8149398-d9d8-4c85-b80a-c1fbef5edd31 "HTTP/2 200 OK"
2025-08-01 14:27:53,460 - app.services.cleaning_service - INFO - Starting background task for upload 7885962a-76cd-46bc-82d0-014a63da9f45, filename: Demo_ReportPeriod01-2025 .xlsx, user: fdd71f95-e8d4-417e-85aa-9b7b0c92436d
2025-08-01 14:27:53,505 - httpx - INFO - HTTP Request: POST https://nrkodllueunpbiotjbql.supabase.co/rest/v1/processing_logs "HTTP/2 404 Not Found"
2025-08-01 14:27:53,506 - app.services.db_service - WARNING - Failed to log processing step: {}
2025-08-01 14:27:53,550 - httpx - INFO - HTTP Request: PATCH https://nrkodllueunpbiotjbql.supabase.co/rest/v1/uploads?id=eq.7885962a-76cd-46bc-82d0-014a63da9f45 "HTTP/2 200 OK"
2025-08-01 14:27:53,551 - app.services.cleaning_service - INFO - Updated upload 7885962a-76cd-46bc-82d0-014a63da9f45 status to PROCESSING
2025-08-01 14:27:53,568 - app.services.cleaning_service - INFO - Excel file sheet names: ['Info', 'SalesPerSKU']
2025-08-01 14:27:53,605 - httpx - INFO - HTTP Request: POST https://nrkodllueunpbiotjbql.supabase.co/rest/v1/processing_logs "HTTP/2 404 Not Found"
2025-08-01 14:27:53,606 - app.services.db_service - WARNING - Failed to log processing step: {}
2025-08-01 14:27:53,606 - app.services.cleaning_service - INFO - Detected vendor from filename and sheet names: skins_nl
2025-08-01 14:27:53,606 - app.services.cleaning_service - INFO - Available sheets: ['Info', 'SalesPerSKU']
2025-08-01 14:27:53,645 - httpx - INFO - HTTP Request: POST https://nrkodllueunpbiotjbql.supabase.co/rest/v1/processing_logs "HTTP/2 404 Not Found"
2025-08-01 14:27:53,646 - app.services.db_service - WARNING - Failed to log processing step: {}
2025-08-01 14:27:53,646 - app.services.cleaning_service - INFO - Default sheet selection: 'Info' (first sheet)
2025-08-01 14:27:53,646 - app.services.cleaning_service - INFO - Processing Skins NL - looking for SalesPerSKU sheet
2025-08-01 14:27:53,646 - app.services.cleaning_service - INFO - SalesPerSKU matching sheets: ['SalesPerSKU']
2025-08-01 14:27:53,646 - app.services.cleaning_service - INFO - Found SalesPerSKU sheet for Skins NL: SalesPerSKU
2025-08-01 14:27:53,670 - app.services.cleaning_service - INFO - Loaded Excel sheet 'SalesPerSKU' with 40 rows, columns: ['Brand', 'Article', 'EANCode', 'SalesAmount', 'SalesAmountSPLY', 'SalesAmountVariance', 'SalesQuantity', 'SalesQuantitySPLY', 'SalesQuantityVariance']
2025-08-01 14:27:53,671 - app.services.cleaning_service - INFO - First 3 rows preview: [{'Brand': 'TaskifAI', 'Article': 'Article 1', 'EANCode': 'PRDT35', 'SalesAmount': nan, 'SalesAmountSPLY': 142.0, 'SalesAmountVariance': nan, 'SalesQuantity': nan, 'SalesQuantitySPLY': 2.0, 'SalesQuantityVariance': nan}, {'Brand': 'TaskifAI', 'Article': 'Article 2', 'EANCode': 'PRDT35', 'SalesAmount': 116.0, 'SalesAmountSPLY': 142.0, 'SalesAmountVariance': -0.181, 'SalesQuantity': 2.0, 'SalesQuantitySPLY': 2.0, 'SalesQuantityVariance': 0.0}, {'Brand': 'TaskifAI', 'Article': 'Article 3', 'EANCode': 'PRGL40', 'SalesAmount': nan, 'SalesAmountSPLY': 142.0, 'SalesAmountVariance': nan, 'SalesQuantity': nan, 'SalesQuantitySPLY': 2.0, 'SalesQuantityVariance': nan}]
2025-08-01 14:27:53,671 - app.services.cleaning_service - INFO - Data types: {'Brand': dtype('O'), 'Article': dtype('O'), 'EANCode': dtype('O'), 'SalesAmount': dtype('float64'), 'SalesAmountSPLY': dtype('float64'), 'SalesAmountVariance': dtype('float64'), 'SalesQuantity': dtype('float64'), 'SalesQuantitySPLY': dtype('float64'), 'SalesQuantityVariance': dtype('float64')}
2025-08-01 14:27:53,671 - app.services.cleaning_service - INFO - Column data distribution:
2025-08-01 14:27:53,672 - app.services.cleaning_service - INFO -   Brand: 40/40 non-empty values
2025-08-01 14:27:53,672 - app.services.cleaning_service - INFO -   Article: 40/40 non-empty values
2025-08-01 14:27:53,672 - app.services.cleaning_service - INFO -   EANCode: 40/40 non-empty values
2025-08-01 14:27:53,673 - app.services.cleaning_service - INFO -   SalesAmount: 31/40 non-empty values
2025-08-01 14:27:53,673 - app.services.cleaning_service - INFO -   SalesAmountSPLY: 25/40 non-empty values
2025-08-01 14:27:53,673 - app.services.cleaning_service - INFO -   SalesAmountVariance: 15/40 non-empty values
2025-08-01 14:27:53,673 - app.services.cleaning_service - INFO -   SalesQuantity: 31/40 non-empty values
2025-08-01 14:27:53,673 - app.services.cleaning_service - INFO -   SalesQuantitySPLY: 25/40 non-empty values
2025-08-01 14:27:53,674 - app.services.cleaning_service - INFO -   SalesQuantityVariance: 16/40 non-empty values
2025-08-01 14:27:53,675 - app.services.cleaning_service - INFO - Last 3 rows preview: [{'Brand': 'TaskifAI', 'Article': 'Article 38', 'EANCode': 'PRDT35', 'SalesAmount': 2558.0, 'SalesAmountSPLY': nan, 'SalesAmountVariance': nan, 'SalesQuantity': 69.0, 'SalesQuantitySPLY': nan, 'SalesQuantityVariance': nan}, {'Brand': 'TaskifAI', 'Article': 'Article 39', 'EANCode': 'PRRC30', 'SalesAmount': 1122.0, 'SalesAmountSPLY': nan, 'SalesAmountVariance': nan, 'SalesQuantity': 25.0, 'SalesQuantitySPLY': nan, 'SalesQuantityVariance': nan}, {'Brand': 'TaskifAI', 'Article': 'Article 40', 'EANCode': 'PRDT35', 'SalesAmount': 182.0, 'SalesAmountSPLY': nan, 'SalesAmountVariance': nan, 'SalesQuantity': 2.0, 'SalesQuantitySPLY': nan, 'SalesQuantityVariance': nan}]
2025-08-01 14:27:53,675 - app.services.cleaning_service - INFO - Using vendor: skins_nl
2025-08-01 14:27:53,675 - app.services.cleaning_service - INFO - Vendor detection details - filename: 'Demo_ReportPeriod01-2025 .xlsx', sheet_names: ['Info', 'SalesPerSKU']
2025-08-01 14:27:53,675 - app.services.cleaning_service - INFO - Starting data cleaning for vendor 'skins_nl' with 40 rows
2025-08-01 14:27:53,711 - httpx - INFO - HTTP Request: POST https://nrkodllueunpbiotjbql.supabase.co/rest/v1/processing_logs "HTTP/2 404 Not Found"
2025-08-01 14:27:53,711 - app.services.db_service - WARNING - Failed to log processing step: {}
DEBUG: Applying vendor-specific cleaning for vendor: 'skins_nl'
DEBUG: Using _clean_skins_nl_data()
DEBUG: Extracting date from Skins NL filename: 'Demo_ReportPeriod01-2025 .xlsx'
DEBUG: Parsed Skins NL date - Month: 1, Year: 2025
DEBUG: Final Skins NL date - Month: 1, Year: 2025
DEBUG: Available columns in Skins NL file: ['Brand', 'Article', 'EANCode', 'SalesAmount', 'SalesAmountSPLY', 'SalesAmountVariance', 'SalesQuantity', 'SalesQuantitySPLY', 'SalesQuantityVariance']
DEBUG: Found EAN column (mapping to functional_name): EANCode
DEBUG: Found quantity column: SalesQuantity
DEBUG: Found sales amount column: SalesAmount
DEBUG: Column mapping for Skins NL: {'EANCode': 'functional_name', 'SalesQuantity': 'quantity', 'SalesAmount': 'sales_lc'}
DEBUG: Columns after mapping: ['Brand', 'Article', 'functional_name', 'sales_lc', 'SalesAmountSPLY', 'SalesAmountVariance', 'quantity', 'SalesQuantitySPLY', 'SalesQuantityVariance']
/home/david/mockDataRepo/backend/app/pipeline/cleaners.py:587: FutureWarning: Setting an item of incompatible dtype is deprecated and will raise in a future error of pandas. Value '116.0' has dtype incompatible with float64, please explicitly cast to a compatible dtype first.
  df.at[idx, 'sales_lc'] = str(cleaned_value)
DEBUG: Filtering rows with missing/invalid quantity. Rows before: 40
DEBUG: Quantity analysis - Total: 40, NotNA: 31, Empty string: 0, Zero string: 0, Zero numeric: 0
DEBUG: Sample quantity values: [nan, 2.0, nan, 1.0, nan, 1.0, nan, 3.0, nan, 16.0]
DEBUG: Rows after filtering invalid quantity: 31
DEBUG: Common cleaning - quantity filtering. Rows before: 31
DEBUG: Common cleaning - converted quantity to numeric. Rows after: 31
2025-08-01 14:27:53,719 - app.services.cleaning_service - INFO - Cleaned 31 rows (original: 40)
2025-08-01 14:27:53,719 - app.services.cleaning_service - INFO - Transformations applied: 33
2025-08-01 14:27:53,758 - httpx - INFO - HTTP Request: POST https://nrkodllueunpbiotjbql.supabase.co/rest/v1/processing_logs "HTTP/2 404 Not Found"
2025-08-01 14:27:53,759 - app.services.db_service - WARNING - Failed to log processing step: {}
2025-08-01 14:27:53,759 - app.services.cleaning_service - INFO - Cleaned data columns: ['Brand', 'Article', 'functional_name', 'sales_lc', 'SalesAmountSPLY', 'SalesAmountVariance', 'quantity', 'SalesQuantitySPLY', 'SalesQuantityVariance', 'report_year', 'report_month', 'reseller', 'currency', 'product_ean']
2025-08-01 14:27:53,761 - app.services.cleaning_service - INFO - Cleaned data sample: [{'Brand': 'TaskifAI', 'Article': 'Article 2', 'functional_name': 'PRDT35', 'sales_lc': '116.0', 'SalesAmountSPLY': 142.0, 'SalesAmountVariance': -0.181, 'quantity': 2.0, 'SalesQuantitySPLY': 2.0, 'SalesQuantityVariance': 0.0, 'report_year': 2025, 'report_month': 1, 'reseller': 'TaskifAI', 'currency': 'EUR', 'product_ean': ''}, {'Brand': 'TaskifAI', 'Article': 'Article 4', 'functional_name': 'PRGL40', 'sales_lc': '58.0', 'SalesAmountSPLY': 142.0, 'SalesAmountVariance': -0.591, 'quantity': 1.0, 'SalesQuantitySPLY': 2.0, 'SalesQuantityVariance': -0.5, 'report_year': 2025, 'report_month': 1, 'reseller': 'TaskifAI', 'currency': 'EUR', 'product_ean': ''}, {'Brand': 'TaskifAI', 'Article': 'Article 6', 'functional_name': 'PRBT75', 'sales_lc': '58.0', 'SalesAmountSPLY': 142.0, 'SalesAmountVariance': -0.591, 'quantity': 1.0, 'SalesQuantitySPLY': 2.0, 'SalesQuantityVariance': -0.5, 'report_year': 2025, 'report_month': 1, 'reseller': 'TaskifAI', 'currency': 'EUR', 'product_ean': ''}]
2025-08-01 14:27:53,761 - app.services.cleaning_service - INFO - Cleaned data types: {'Brand': dtype('O'), 'Article': dtype('O'), 'functional_name': dtype('O'), 'sales_lc': dtype('O'), 'SalesAmountSPLY': dtype('float64'), 'SalesAmountVariance': dtype('float64'), 'quantity': dtype('float64'), 'SalesQuantitySPLY': dtype('float64'), 'SalesQuantityVariance': dtype('float64'), 'report_year': dtype('int64'), 'report_month': dtype('int64'), 'reseller': dtype('O'), 'currency': dtype('O'), 'product_ean': dtype('O')}
2025-08-01 14:27:53,761 - app.services.cleaning_service - INFO - Starting data normalization for vendor 'skins_nl' with 31 cleaned rows
2025-08-01 14:27:53,798 - httpx - INFO - HTTP Request: POST https://nrkodllueunpbiotjbql.supabase.co/rest/v1/processing_logs "HTTP/2 404 Not Found"
2025-08-01 14:27:53,799 - app.services.db_service - WARNING - Failed to log processing step: {}
DEBUG: Starting normalization for vendor 'skins_nl' with 31 rows
DEBUG: Input columns: ['Brand', 'Article', 'functional_name', 'sales_lc', 'SalesAmountSPLY', 'SalesAmountVariance', 'quantity', 'SalesQuantitySPLY', 'SalesQuantityVariance', 'report_year', 'report_month', 'reseller', 'currency', 'product_ean']
DEBUG: Sample input row: {'Brand': 'TaskifAI', 'Article': 'Article 2', 'functional_name': 'PRDT35', 'sales_lc': '116.0', 'SalesAmountSPLY': 142.0, 'SalesAmountVariance': -0.181, 'quantity': 2.0, 'SalesQuantitySPLY': 2.0, 'SalesQuantityVariance': 0.0, 'report_year': 2025, 'report_month': 1, 'reseller': 'TaskifAI', 'currency': 'EUR', 'product_ean': ''}
DEBUG: Preserved sales_lc for skins_nl: ['116.0', '58.0', '58.0', '174.0', '2028.0']
DEBUG: Added sales_eur conversion for skins_nl EUR data
DEBUG: Zero quantity - Including 0 rows with sales, Excluding 0 rows without sales
DEBUG: Negative quantity - Including 0 rows with sales, Excluding 0 rows without sales
DEBUG: Normalization complete for vendor 'skins_nl' - 31 rows
DEBUG: Final normalized columns: ['product_ean', 'year', 'month', 'quantity', 'sales_lc', 'functional_name', 'currency', 'sales_eur', 'reseller']
DEBUG: Sample normalized row: {'product_ean': '', 'year': 2025, 'month': 1, 'quantity': 2, 'sales_lc': '116.0', 'functional_name': 'PRDT35', 'currency': 'EUR', 'sales_eur': 116.0, 'reseller': 'TaskifAI'}
2025-08-01 14:27:53,813 - app.services.cleaning_service - INFO - Normalized 31 rows
2025-08-01 14:27:53,862 - httpx - INFO - HTTP Request: POST https://nrkodllueunpbiotjbql.supabase.co/rest/v1/processing_logs "HTTP/2 404 Not Found"
2025-08-01 14:27:53,863 - app.services.db_service - WARNING - Failed to log processing step: {}
2025-08-01 14:27:53,865 - app.services.cleaning_service - INFO - Normalized data sample: [{'product_ean': '', 'year': 2025, 'month': 1, 'quantity': 2, 'sales_lc': '116.0', 'functional_name': 'PRDT35', 'currency': 'EUR', 'sales_eur': 116.0, 'reseller': 'TaskifAI'}, {'product_ean': '', 'year': 2025, 'month': 1, 'quantity': 1, 'sales_lc': '58.0', 'functional_name': 'PRGL40', 'currency': 'EUR', 'sales_eur': 58.0, 'reseller': 'TaskifAI'}, {'product_ean': '', 'year': 2025, 'month': 1, 'quantity': 1, 'sales_lc': '58.0', 'functional_name': 'PRBT75', 'currency': 'EUR', 'sales_eur': 58.0, 'reseller': 'TaskifAI'}]
2025-08-01 14:27:53,865 - app.services.cleaning_service - INFO - Normalized columns: ['product_ean', 'year', 'month', 'quantity', 'sales_lc', 'functional_name', 'currency', 'sales_eur', 'reseller']
2025-08-01 14:27:53,865 - app.services.cleaning_service - INFO - Normalized data types: {'product_ean': dtype('O'), 'year': Int64Dtype(), 'month': Int64Dtype(), 'quantity': Int64Dtype(), 'sales_lc': dtype('O'), 'functional_name': dtype('O'), 'currency': dtype('O'), 'sales_eur': dtype('float64'), 'reseller': dtype('O')}
2025-08-01 14:27:53,866 - app.services.cleaning_service - INFO - All required fields present
2025-08-01 14:27:53,868 - app.services.cleaning_service - INFO - Converting 31 entries for database insertion
2025-08-01 14:27:53,868 - app.services.cleaning_service - INFO - Sample entry for insertion: {'product_ean': '', 'year': 2025, 'month': 1, 'quantity': 2, 'sales_lc': '116.0', 'functional_name': 'PRDT35', 'currency': 'EUR', 'sales_eur': 116.0, 'reseller': 'TaskifAI'}
2025-08-01 14:27:53,868 - app.services.cleaning_service - INFO - Attempting to insert 31 entries into mock_data
2025-08-01 14:27:53,913 - httpx - INFO - HTTP Request: POST https://nrkodllueunpbiotjbql.supabase.co/rest/v1/processing_logs "HTTP/2 404 Not Found"
2025-08-01 14:27:53,913 - app.services.db_service - WARNING - Failed to log processing step: {}
DB Service: Starting insert_mock_data for upload 7885962a-76cd-46bc-82d0-014a63da9f45 with 31 entries
DB Service: Sample mock_data entry: {'id': 'e984760d-c63b-4375-904b-a639a2a783d8', 'product_ean': '', 'month': 1, 'year': 2025, 'quantity': 2, 'sales_lc': '116.0', 'sales_eur': 116.0, 'currency': 'EUR', 'reseller': 'TaskifAI', 'functional_name': 'PRDT35', 'sales_date': datetime.date(2025, 1, 1), 'upload_id': '7885962a-76cd-46bc-82d0-014a63da9f45'}
DB Service: Error inserting mock data: Object of type date is not JSON serializable
DB Service: Full traceback: {}
2025-08-01 14:27:53,917 - app.services.cleaning_service - ERROR - Error processing upload 7885962a-76cd-46bc-82d0-014a63da9f45: Failed to insert mock data: Object of type date is not JSON serializable
2025-08-01 14:27:53,918 - app.services.cleaning_service - ERROR - Full traceback: Traceback (most recent call last):
  File "/home/david/mockDataRepo/backend/app/services/db_service.py", line 371, in insert_mock_data
    result = self.service_supabase.table("mock_data").insert(mock_data_entries).execute()
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/david/mockDataRepo/backend/venv/lib/python3.12/site-packages/postgrest/_sync/request_builder.py", line 58, in execute
    r = self.session.request(
        ^^^^^^^^^^^^^^^^^^^^^
  File "/home/david/mockDataRepo/backend/venv/lib/python3.12/site-packages/httpx/_client.py", line 824, in request
    request = self.build_request(
              ^^^^^^^^^^^^^^^^^^^
  File "/home/david/mockDataRepo/backend/venv/lib/python3.12/site-packages/httpx/_client.py", line 358, in build_request
    return Request(
           ^^^^^^^^
  File "/home/david/mockDataRepo/backend/venv/lib/python3.12/site-packages/httpx/_models.py", line 342, in __init__
    headers, stream = encode_request(
                      ^^^^^^^^^^^^^^^
  File "/home/david/mockDataRepo/backend/venv/lib/python3.12/site-packages/httpx/_content.py", line 214, in encode_request
    return encode_json(json)
           ^^^^^^^^^^^^^^^^^
  File "/home/david/mockDataRepo/backend/venv/lib/python3.12/site-packages/httpx/_content.py", line 177, in encode_json
    body = json_dumps(json).encode("utf-8")
           ^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/json/__init__.py", line 231, in dumps
    return _default_encoder.encode(obj)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/json/encoder.py", line 200, in encode
    chunks = self.iterencode(o, _one_shot=True)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/json/encoder.py", line 258, in iterencode
    return _iterencode(o, 0)
           ^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/json/encoder.py", line 180, in default
    raise TypeError(f'Object of type {o.__class__.__name__} '
TypeError: Object of type date is not JSON serializable

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/david/mockDataRepo/backend/app/services/cleaning_service.py", line 213, in process_file
    await self.db_service.insert_mock_data(upload_id, sellout_entries)
  File "/home/david/mockDataRepo/backend/app/services/db_service.py", line 379, in insert_mock_data
    raise DatabaseException(f"Failed to insert mock data: {str(e)}")
app.utils.exceptions.DatabaseException: Failed to insert mock data: Object of type date is not JSON serializable

2025-08-01 14:27:53,957 - httpx - INFO - HTTP Request: PATCH https://nrkodllueunpbiotjbql.supabase.co/rest/v1/uploads?id=eq.7885962a-76cd-46bc-82d0-014a63da9f45 "HTTP/2 200 OK"
2025-08-01 14:27:53,960 - app.services.cleaning_service - INFO - Starting background task for upload 2e70dca9-b2b6-48a5-9618-86a7b4b85a2e, filename: Demo_ReportPeriod02-2025.xlsx, user: fdd71f95-e8d4-417e-85aa-9b7b0c92436d
2025-08-01 14:27:53,996 - httpx - INFO - HTTP Request: POST https://nrkodllueunpbiotjbql.supabase.co/rest/v1/processing_logs "HTTP/2 404 Not Found"
2025-08-01 14:27:53,997 - app.services.db_service - WARNING - Failed to log processing step: {}
2025-08-01 14:27:54,037 - httpx - INFO - HTTP Request: PATCH https://nrkodllueunpbiotjbql.supabase.co/rest/v1/uploads?id=eq.2e70dca9-b2b6-48a5-9618-86a7b4b85a2e "HTTP/2 200 OK"
2025-08-01 14:27:54,038 - app.services.cleaning_service - INFO - Updated upload 2e70dca9-b2b6-48a5-9618-86a7b4b85a2e status to PROCESSING
2025-08-01 14:27:54,045 - app.services.cleaning_service - INFO - Excel file sheet names: ['Info', 'SalesPerSKU']
2025-08-01 14:27:54,110 - httpx - INFO - HTTP Request: POST https://nrkodllueunpbiotjbql.supabase.co/rest/v1/processing_logs "HTTP/2 404 Not Found"
2025-08-01 14:27:54,110 - app.services.db_service - WARNING - Failed to log processing step: {}
2025-08-01 14:27:54,110 - app.services.cleaning_service - INFO - Detected vendor from filename and sheet names: skins_nl
2025-08-01 14:27:54,110 - app.services.cleaning_service - INFO - Available sheets: ['Info', 'SalesPerSKU']
2025-08-01 14:27:54,158 - httpx - INFO - HTTP Request: POST https://nrkodllueunpbiotjbql.supabase.co/rest/v1/processing_logs "HTTP/2 404 Not Found"
2025-08-01 14:27:54,159 - app.services.db_service - WARNING - Failed to log processing step: {}
2025-08-01 14:27:54,159 - app.services.cleaning_service - INFO - Default sheet selection: 'Info' (first sheet)
2025-08-01 14:27:54,159 - app.services.cleaning_service - INFO - Processing Skins NL - looking for SalesPerSKU sheet
2025-08-01 14:27:54,159 - app.services.cleaning_service - INFO - SalesPerSKU matching sheets: ['SalesPerSKU']
2025-08-01 14:27:54,159 - app.services.cleaning_service - INFO - Found SalesPerSKU sheet for Skins NL: SalesPerSKU
2025-08-01 14:27:54,180 - app.services.cleaning_service - INFO - Loaded Excel sheet 'SalesPerSKU' with 40 rows, columns: ['Brand', 'Article', 'EANCode', 'SalesAmount', 'SalesAmountSPLY', 'SalesAmountVariance', 'SalesQuantity', 'SalesQuantitySPLY', 'SalesQuantityVariance']
2025-08-01 14:27:54,182 - app.services.cleaning_service - INFO - First 3 rows preview: [{'Brand': 'TaskifAI', 'Article': 'Article 1', 'EANCode': 'PRDT35', 'SalesAmount': nan, 'SalesAmountSPLY': 142.0, 'SalesAmountVariance': nan, 'SalesQuantity': nan, 'SalesQuantitySPLY': 2.0, 'SalesQuantityVariance': nan}, {'Brand': 'TaskifAI', 'Article': 'Article 2', 'EANCode': 'PRDT35', 'SalesAmount': 116.0, 'SalesAmountSPLY': 142.0, 'SalesAmountVariance': -0.181, 'SalesQuantity': 2.0, 'SalesQuantitySPLY': 2.0, 'SalesQuantityVariance': 0.0}, {'Brand': 'TaskifAI', 'Article': 'Article 3', 'EANCode': 'PRGL40', 'SalesAmount': nan, 'SalesAmountSPLY': 142.0, 'SalesAmountVariance': nan, 'SalesQuantity': nan, 'SalesQuantitySPLY': 2.0, 'SalesQuantityVariance': nan}]
2025-08-01 14:27:54,182 - app.services.cleaning_service - INFO - Data types: {'Brand': dtype('O'), 'Article': dtype('O'), 'EANCode': dtype('O'), 'SalesAmount': dtype('float64'), 'SalesAmountSPLY': dtype('float64'), 'SalesAmountVariance': dtype('float64'), 'SalesQuantity': dtype('float64'), 'SalesQuantitySPLY': dtype('float64'), 'SalesQuantityVariance': dtype('float64')}
2025-08-01 14:27:54,182 - app.services.cleaning_service - INFO - Column data distribution:
2025-08-01 14:27:54,183 - app.services.cleaning_service - INFO -   Brand: 40/40 non-empty values
2025-08-01 14:27:54,183 - app.services.cleaning_service - INFO -   Article: 40/40 non-empty values
2025-08-01 14:27:54,183 - app.services.cleaning_service - INFO -   EANCode: 40/40 non-empty values
2025-08-01 14:27:54,184 - app.services.cleaning_service - INFO -   SalesAmount: 31/40 non-empty values
2025-08-01 14:27:54,184 - app.services.cleaning_service - INFO -   SalesAmountSPLY: 25/40 non-empty values
2025-08-01 14:27:54,184 - app.services.cleaning_service - INFO -   SalesAmountVariance: 15/40 non-empty values
2025-08-01 14:27:54,185 - app.services.cleaning_service - INFO -   SalesQuantity: 31/40 non-empty values
2025-08-01 14:27:54,185 - app.services.cleaning_service - INFO -   SalesQuantitySPLY: 25/40 non-empty values
2025-08-01 14:27:54,185 - app.services.cleaning_service - INFO -   SalesQuantityVariance: 16/40 non-empty values
2025-08-01 14:27:54,187 - app.services.cleaning_service - INFO - Last 3 rows preview: [{'Brand': 'TaskifAI', 'Article': 'Article 38', 'EANCode': 'PRDT35', 'SalesAmount': 2558.0, 'SalesAmountSPLY': nan, 'SalesAmountVariance': nan, 'SalesQuantity': 69.0, 'SalesQuantitySPLY': nan, 'SalesQuantityVariance': nan}, {'Brand': 'TaskifAI', 'Article': 'Article 39', 'EANCode': 'PRRC30', 'SalesAmount': 1122.0, 'SalesAmountSPLY': nan, 'SalesAmountVariance': nan, 'SalesQuantity': 25.0, 'SalesQuantitySPLY': nan, 'SalesQuantityVariance': nan}, {'Brand': 'TaskifAI', 'Article': 'Article 40', 'EANCode': 'PRDT35', 'SalesAmount': 182.0, 'SalesAmountSPLY': nan, 'SalesAmountVariance': nan, 'SalesQuantity': 2.0, 'SalesQuantitySPLY': nan, 'SalesQuantityVariance': nan}]
2025-08-01 14:27:54,187 - app.services.cleaning_service - INFO - Using vendor: skins_nl
2025-08-01 14:27:54,187 - app.services.cleaning_service - INFO - Vendor detection details - filename: 'Demo_ReportPeriod02-2025.xlsx', sheet_names: ['Info', 'SalesPerSKU']
2025-08-01 14:27:54,187 - app.services.cleaning_service - INFO - Starting data cleaning for vendor 'skins_nl' with 40 rows
2025-08-01 14:27:54,224 - httpx - INFO - HTTP Request: POST https://nrkodllueunpbiotjbql.supabase.co/rest/v1/processing_logs "HTTP/2 404 Not Found"
2025-08-01 14:27:54,225 - app.services.db_service - WARNING - Failed to log processing step: {}
DEBUG: Applying vendor-specific cleaning for vendor: 'skins_nl'
DEBUG: Using _clean_skins_nl_data()
DEBUG: Extracting date from Skins NL filename: 'Demo_ReportPeriod02-2025.xlsx'
DEBUG: Parsed Skins NL date - Month: 2, Year: 2025
DEBUG: Final Skins NL date - Month: 2, Year: 2025
DEBUG: Available columns in Skins NL file: ['Brand', 'Article', 'EANCode', 'SalesAmount', 'SalesAmountSPLY', 'SalesAmountVariance', 'SalesQuantity', 'SalesQuantitySPLY', 'SalesQuantityVariance']
DEBUG: Found EAN column (mapping to functional_name): EANCode
DEBUG: Found quantity column: SalesQuantity
DEBUG: Found sales amount column: SalesAmount
DEBUG: Column mapping for Skins NL: {'EANCode': 'functional_name', 'SalesQuantity': 'quantity', 'SalesAmount': 'sales_lc'}
DEBUG: Columns after mapping: ['Brand', 'Article', 'functional_name', 'sales_lc', 'SalesAmountSPLY', 'SalesAmountVariance', 'quantity', 'SalesQuantitySPLY', 'SalesQuantityVariance']
/home/david/mockDataRepo/backend/app/pipeline/cleaners.py:587: FutureWarning: Setting an item of incompatible dtype is deprecated and will raise in a future error of pandas. Value '116.0' has dtype incompatible with float64, please explicitly cast to a compatible dtype first.
  df.at[idx, 'sales_lc'] = str(cleaned_value)
DEBUG: Filtering rows with missing/invalid quantity. Rows before: 40
DEBUG: Quantity analysis - Total: 40, NotNA: 31, Empty string: 0, Zero string: 0, Zero numeric: 0
DEBUG: Sample quantity values: [nan, 2.0, nan, 1.0, nan, 1.0, nan, 3.0, nan, 16.0]
DEBUG: Rows after filtering invalid quantity: 31
DEBUG: Common cleaning - quantity filtering. Rows before: 31
DEBUG: Common cleaning - converted quantity to numeric. Rows after: 31
2025-08-01 14:27:54,228 - app.services.cleaning_service - INFO - Cleaned 31 rows (original: 40)
2025-08-01 14:27:54,228 - app.services.cleaning_service - INFO - Transformations applied: 33
2025-08-01 14:27:54,265 - httpx - INFO - HTTP Request: POST https://nrkodllueunpbiotjbql.supabase.co/rest/v1/processing_logs "HTTP/2 404 Not Found"
2025-08-01 14:27:54,266 - app.services.db_service - WARNING - Failed to log processing step: {}
2025-08-01 14:27:54,266 - app.services.cleaning_service - INFO - Cleaned data columns: ['Brand', 'Article', 'functional_name', 'sales_lc', 'SalesAmountSPLY', 'SalesAmountVariance', 'quantity', 'SalesQuantitySPLY', 'SalesQuantityVariance', 'report_year', 'report_month', 'reseller', 'currency', 'product_ean']
2025-08-01 14:27:54,267 - app.services.cleaning_service - INFO - Cleaned data sample: [{'Brand': 'TaskifAI', 'Article': 'Article 2', 'functional_name': 'PRDT35', 'sales_lc': '116.0', 'SalesAmountSPLY': 142.0, 'SalesAmountVariance': -0.181, 'quantity': 2.0, 'SalesQuantitySPLY': 2.0, 'SalesQuantityVariance': 0.0, 'report_year': 2025, 'report_month': 2, 'reseller': 'TaskifAI', 'currency': 'EUR', 'product_ean': ''}, {'Brand': 'TaskifAI', 'Article': 'Article 4', 'functional_name': 'PRGL40', 'sales_lc': '58.0', 'SalesAmountSPLY': 142.0, 'SalesAmountVariance': -0.591, 'quantity': 1.0, 'SalesQuantitySPLY': 2.0, 'SalesQuantityVariance': -0.5, 'report_year': 2025, 'report_month': 2, 'reseller': 'TaskifAI', 'currency': 'EUR', 'product_ean': ''}, {'Brand': 'TaskifAI', 'Article': 'Article 6', 'functional_name': 'PRBT75', 'sales_lc': '58.0', 'SalesAmountSPLY': 142.0, 'SalesAmountVariance': -0.591, 'quantity': 1.0, 'SalesQuantitySPLY': 2.0, 'SalesQuantityVariance': -0.5, 'report_year': 2025, 'report_month': 2, 'reseller': 'TaskifAI', 'currency': 'EUR', 'product_ean': ''}]
2025-08-01 14:27:54,268 - app.services.cleaning_service - INFO - Cleaned data types: {'Brand': dtype('O'), 'Article': dtype('O'), 'functional_name': dtype('O'), 'sales_lc': dtype('O'), 'SalesAmountSPLY': dtype('float64'), 'SalesAmountVariance': dtype('float64'), 'quantity': dtype('float64'), 'SalesQuantitySPLY': dtype('float64'), 'SalesQuantityVariance': dtype('float64'), 'report_year': dtype('int64'), 'report_month': dtype('int64'), 'reseller': dtype('O'), 'currency': dtype('O'), 'product_ean': dtype('O')}
2025-08-01 14:27:54,268 - app.services.cleaning_service - INFO - Starting data normalization for vendor 'skins_nl' with 31 cleaned rows
2025-08-01 14:27:54,318 - httpx - INFO - HTTP Request: POST https://nrkodllueunpbiotjbql.supabase.co/rest/v1/processing_logs "HTTP/2 404 Not Found"
2025-08-01 14:27:54,319 - app.services.db_service - WARNING - Failed to log processing step: {}
DEBUG: Starting normalization for vendor 'skins_nl' with 31 rows
DEBUG: Input columns: ['Brand', 'Article', 'functional_name', 'sales_lc', 'SalesAmountSPLY', 'SalesAmountVariance', 'quantity', 'SalesQuantitySPLY', 'SalesQuantityVariance', 'report_year', 'report_month', 'reseller', 'currency', 'product_ean']
DEBUG: Sample input row: {'Brand': 'TaskifAI', 'Article': 'Article 2', 'functional_name': 'PRDT35', 'sales_lc': '116.0', 'SalesAmountSPLY': 142.0, 'SalesAmountVariance': -0.181, 'quantity': 2.0, 'SalesQuantitySPLY': 2.0, 'SalesQuantityVariance': 0.0, 'report_year': 2025, 'report_month': 2, 'reseller': 'TaskifAI', 'currency': 'EUR', 'product_ean': ''}
DEBUG: Preserved sales_lc for skins_nl: ['116.0', '58.0', '58.0', '174.0', '2028.0']
DEBUG: Added sales_eur conversion for skins_nl EUR data
DEBUG: Zero quantity - Including 0 rows with sales, Excluding 0 rows without sales
DEBUG: Negative quantity - Including 0 rows with sales, Excluding 0 rows without sales
DEBUG: Normalization complete for vendor 'skins_nl' - 31 rows
DEBUG: Final normalized columns: ['product_ean', 'year', 'month', 'quantity', 'sales_lc', 'functional_name', 'currency', 'sales_eur', 'reseller']
DEBUG: Sample normalized row: {'product_ean': '', 'year': 2025, 'month': 2, 'quantity': 2, 'sales_lc': '116.0', 'functional_name': 'PRDT35', 'currency': 'EUR', 'sales_eur': 116.0, 'reseller': 'TaskifAI'}
2025-08-01 14:27:54,333 - app.services.cleaning_service - INFO - Normalized 31 rows
2025-08-01 14:27:54,373 - httpx - INFO - HTTP Request: POST https://nrkodllueunpbiotjbql.supabase.co/rest/v1/processing_logs "HTTP/2 404 Not Found"
2025-08-01 14:27:54,373 - app.services.db_service - WARNING - Failed to log processing step: {}
2025-08-01 14:27:54,375 - app.services.cleaning_service - INFO - Normalized data sample: [{'product_ean': '', 'year': 2025, 'month': 2, 'quantity': 2, 'sales_lc': '116.0', 'functional_name': 'PRDT35', 'currency': 'EUR', 'sales_eur': 116.0, 'reseller': 'TaskifAI'}, {'product_ean': '', 'year': 2025, 'month': 2, 'quantity': 1, 'sales_lc': '58.0', 'functional_name': 'PRGL40', 'currency': 'EUR', 'sales_eur': 58.0, 'reseller': 'TaskifAI'}, {'product_ean': '', 'year': 2025, 'month': 2, 'quantity': 1, 'sales_lc': '58.0', 'functional_name': 'PRBT75', 'currency': 'EUR', 'sales_eur': 58.0, 'reseller': 'TaskifAI'}]
2025-08-01 14:27:54,375 - app.services.cleaning_service - INFO - Normalized columns: ['product_ean', 'year', 'month', 'quantity', 'sales_lc', 'functional_name', 'currency', 'sales_eur', 'reseller']
2025-08-01 14:27:54,375 - app.services.cleaning_service - INFO - Normalized data types: {'product_ean': dtype('O'), 'year': Int64Dtype(), 'month': Int64Dtype(), 'quantity': Int64Dtype(), 'sales_lc': dtype('O'), 'functional_name': dtype('O'), 'currency': dtype('O'), 'sales_eur': dtype('float64'), 'reseller': dtype('O')}
2025-08-01 14:27:54,376 - app.services.cleaning_service - INFO - All required fields present
2025-08-01 14:27:54,378 - app.services.cleaning_service - INFO - Converting 31 entries for database insertion
2025-08-01 14:27:54,378 - app.services.cleaning_service - INFO - Sample entry for insertion: {'product_ean': '', 'year': 2025, 'month': 2, 'quantity': 2, 'sales_lc': '116.0', 'functional_name': 'PRDT35', 'currency': 'EUR', 'sales_eur': 116.0, 'reseller': 'TaskifAI'}
2025-08-01 14:27:54,378 - app.services.cleaning_service - INFO - Attempting to insert 31 entries into mock_data
2025-08-01 14:27:54,426 - httpx - INFO - HTTP Request: POST https://nrkodllueunpbiotjbql.supabase.co/rest/v1/processing_logs "HTTP/2 404 Not Found"
2025-08-01 14:27:54,427 - app.services.db_service - WARNING - Failed to log processing step: {}
DB Service: Starting insert_mock_data for upload 2e70dca9-b2b6-48a5-9618-86a7b4b85a2e with 31 entries
DB Service: Sample mock_data entry: {'id': 'd687eff2-1aed-4c6d-92d3-6883080f530c', 'product_ean': '', 'month': 2, 'year': 2025, 'quantity': 2, 'sales_lc': '116.0', 'sales_eur': 116.0, 'currency': 'EUR', 'reseller': 'TaskifAI', 'functional_name': 'PRDT35', 'sales_date': datetime.date(2025, 2, 1), 'upload_id': '2e70dca9-b2b6-48a5-9618-86a7b4b85a2e'}
DB Service: Error inserting mock data: Object of type date is not JSON serializable
DB Service: Full traceback: {}
2025-08-01 14:27:54,429 - app.services.cleaning_service - ERROR - Error processing upload 2e70dca9-b2b6-48a5-9618-86a7b4b85a2e: Failed to insert mock data: Object of type date is not JSON serializable
2025-08-01 14:27:54,429 - app.services.cleaning_service - ERROR - Full traceback: Traceback (most recent call last):
  File "/home/david/mockDataRepo/backend/app/services/db_service.py", line 371, in insert_mock_data
    result = self.service_supabase.table("mock_data").insert(mock_data_entries).execute()
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/david/mockDataRepo/backend/venv/lib/python3.12/site-packages/postgrest/_sync/request_builder.py", line 58, in execute
    r = self.session.request(
        ^^^^^^^^^^^^^^^^^^^^^
  File "/home/david/mockDataRepo/backend/venv/lib/python3.12/site-packages/httpx/_client.py", line 824, in request
    request = self.build_request(
              ^^^^^^^^^^^^^^^^^^^
  File "/home/david/mockDataRepo/backend/venv/lib/python3.12/site-packages/httpx/_client.py", line 358, in build_request
    return Request(
           ^^^^^^^^
  File "/home/david/mockDataRepo/backend/venv/lib/python3.12/site-packages/httpx/_models.py", line 342, in __init__
    headers, stream = encode_request(
                      ^^^^^^^^^^^^^^^
  File "/home/david/mockDataRepo/backend/venv/lib/python3.12/site-packages/httpx/_content.py", line 214, in encode_request
    return encode_json(json)
           ^^^^^^^^^^^^^^^^^
  File "/home/david/mockDataRepo/backend/venv/lib/python3.12/site-packages/httpx/_content.py", line 177, in encode_json
    body = json_dumps(json).encode("utf-8")
           ^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/json/__init__.py", line 231, in dumps
    return _default_encoder.encode(obj)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/json/encoder.py", line 200, in encode
    chunks = self.iterencode(o, _one_shot=True)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/json/encoder.py", line 258, in iterencode
    return _iterencode(o, 0)
           ^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/json/encoder.py", line 180, in default
    raise TypeError(f'Object of type {o.__class__.__name__} '
TypeError: Object of type date is not JSON serializable

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/david/mockDataRepo/backend/app/services/cleaning_service.py", line 213, in process_file
    await self.db_service.insert_mock_data(upload_id, sellout_entries)
  File "/home/david/mockDataRepo/backend/app/services/db_service.py", line 379, in insert_mock_data
    raise DatabaseException(f"Failed to insert mock data: {str(e)}")
app.utils.exceptions.DatabaseException: Failed to insert mock data: Object of type date is not JSON serializable

2025-08-01 14:27:54,467 - httpx - INFO - HTTP Request: PATCH https://nrkodllueunpbiotjbql.supabase.co/rest/v1/uploads?id=eq.2e70dca9-b2b6-48a5-9618-86a7b4b85a2e "HTTP/2 200 OK"
2025-08-01 14:27:54,471 - app.services.cleaning_service - INFO - Starting background task for upload e87a76c0-3596-4bd6-a9a8-439e0d852ce7, filename: Demo_ReportPeriod03-2025.xlsx, user: fdd71f95-e8d4-417e-85aa-9b7b0c92436d
2025-08-01 14:27:54,507 - httpx - INFO - HTTP Request: POST https://nrkodllueunpbiotjbql.supabase.co/rest/v1/processing_logs "HTTP/2 404 Not Found"
2025-08-01 14:27:54,508 - app.services.db_service - WARNING - Failed to log processing step: {}
2025-08-01 14:27:54,574 - httpx - INFO - HTTP Request: PATCH https://nrkodllueunpbiotjbql.supabase.co/rest/v1/uploads?id=eq.e87a76c0-3596-4bd6-a9a8-439e0d852ce7 "HTTP/2 200 OK"
2025-08-01 14:27:54,575 - app.services.cleaning_service - INFO - Updated upload e87a76c0-3596-4bd6-a9a8-439e0d852ce7 status to PROCESSING
2025-08-01 14:27:54,592 - app.services.cleaning_service - INFO - Excel file sheet names: ['Info', 'SalesPerSKU']
2025-08-01 14:27:54,636 - httpx - INFO - HTTP Request: POST https://nrkodllueunpbiotjbql.supabase.co/rest/v1/processing_logs "HTTP/2 404 Not Found"
2025-08-01 14:27:54,636 - app.services.db_service - WARNING - Failed to log processing step: {}
2025-08-01 14:27:54,637 - app.services.cleaning_service - INFO - Detected vendor from filename and sheet names: skins_nl
2025-08-01 14:27:54,637 - app.services.cleaning_service - INFO - Available sheets: ['Info', 'SalesPerSKU']
2025-08-01 14:27:54,677 - httpx - INFO - HTTP Request: POST https://nrkodllueunpbiotjbql.supabase.co/rest/v1/processing_logs "HTTP/2 404 Not Found"
2025-08-01 14:27:54,678 - app.services.db_service - WARNING - Failed to log processing step: {}
2025-08-01 14:27:54,678 - app.services.cleaning_service - INFO - Default sheet selection: 'Info' (first sheet)
2025-08-01 14:27:54,678 - app.services.cleaning_service - INFO - Processing Skins NL - looking for SalesPerSKU sheet
2025-08-01 14:27:54,678 - app.services.cleaning_service - INFO - SalesPerSKU matching sheets: ['SalesPerSKU']
2025-08-01 14:27:54,678 - app.services.cleaning_service - INFO - Found SalesPerSKU sheet for Skins NL: SalesPerSKU
2025-08-01 14:27:54,701 - app.services.cleaning_service - INFO - Loaded Excel sheet 'SalesPerSKU' with 40 rows, columns: ['Brand', 'Article', 'EANCode', 'SalesAmount', 'SalesAmountSPLY', 'SalesAmountVariance', 'SalesQuantity', 'SalesQuantitySPLY', 'SalesQuantityVariance']
2025-08-01 14:27:54,702 - app.services.cleaning_service - INFO - First 3 rows preview: [{'Brand': 'TaskifAI', 'Article': 'Article 1', 'EANCode': 'PRDT35', 'SalesAmount': nan, 'SalesAmountSPLY': 142.0, 'SalesAmountVariance': nan, 'SalesQuantity': nan, 'SalesQuantitySPLY': 2.0, 'SalesQuantityVariance': nan}, {'Brand': 'TaskifAI', 'Article': 'Article 2', 'EANCode': 'PRDT35', 'SalesAmount': 116.0, 'SalesAmountSPLY': 142.0, 'SalesAmountVariance': -0.181, 'SalesQuantity': 2.0, 'SalesQuantitySPLY': 2.0, 'SalesQuantityVariance': 0.0}, {'Brand': 'TaskifAI', 'Article': 'Article 3', 'EANCode': 'PRGL40', 'SalesAmount': nan, 'SalesAmountSPLY': 142.0, 'SalesAmountVariance': nan, 'SalesQuantity': nan, 'SalesQuantitySPLY': 2.0, 'SalesQuantityVariance': nan}]
2025-08-01 14:27:54,703 - app.services.cleaning_service - INFO - Data types: {'Brand': dtype('O'), 'Article': dtype('O'), 'EANCode': dtype('O'), 'SalesAmount': dtype('float64'), 'SalesAmountSPLY': dtype('float64'), 'SalesAmountVariance': dtype('float64'), 'SalesQuantity': dtype('float64'), 'SalesQuantitySPLY': dtype('float64'), 'SalesQuantityVariance': dtype('float64')}
2025-08-01 14:27:54,703 - app.services.cleaning_service - INFO - Column data distribution:
2025-08-01 14:27:54,703 - app.services.cleaning_service - INFO -   Brand: 40/40 non-empty values
2025-08-01 14:27:54,704 - app.services.cleaning_service - INFO -   Article: 40/40 non-empty values
2025-08-01 14:27:54,704 - app.services.cleaning_service - INFO -   EANCode: 40/40 non-empty values
2025-08-01 14:27:54,704 - app.services.cleaning_service - INFO -   SalesAmount: 31/40 non-empty values
2025-08-01 14:27:54,705 - app.services.cleaning_service - INFO -   SalesAmountSPLY: 25/40 non-empty values
2025-08-01 14:27:54,705 - app.services.cleaning_service - INFO -   SalesAmountVariance: 15/40 non-empty values
2025-08-01 14:27:54,705 - app.services.cleaning_service - INFO -   SalesQuantity: 31/40 non-empty values
2025-08-01 14:27:54,706 - app.services.cleaning_service - INFO -   SalesQuantitySPLY: 25/40 non-empty values
2025-08-01 14:27:54,706 - app.services.cleaning_service - INFO -   SalesQuantityVariance: 16/40 non-empty values
2025-08-01 14:27:54,707 - app.services.cleaning_service - INFO - Last 3 rows preview: [{'Brand': 'TaskifAI', 'Article': 'Article 38', 'EANCode': 'PRDT35', 'SalesAmount': 2558.0, 'SalesAmountSPLY': nan, 'SalesAmountVariance': nan, 'SalesQuantity': 69.0, 'SalesQuantitySPLY': nan, 'SalesQuantityVariance': nan}, {'Brand': 'TaskifAI', 'Article': 'Article 39', 'EANCode': 'PRRC30', 'SalesAmount': 1122.0, 'SalesAmountSPLY': nan, 'SalesAmountVariance': nan, 'SalesQuantity': 25.0, 'SalesQuantitySPLY': nan, 'SalesQuantityVariance': nan}, {'Brand': 'TaskifAI', 'Article': 'Article 40', 'EANCode': 'PRDT35', 'SalesAmount': 182.0, 'SalesAmountSPLY': nan, 'SalesAmountVariance': nan, 'SalesQuantity': 2.0, 'SalesQuantitySPLY': nan, 'SalesQuantityVariance': nan}]
2025-08-01 14:27:54,707 - app.services.cleaning_service - INFO - Using vendor: skins_nl
2025-08-01 14:27:54,707 - app.services.cleaning_service - INFO - Vendor detection details - filename: 'Demo_ReportPeriod03-2025.xlsx', sheet_names: ['Info', 'SalesPerSKU']
2025-08-01 14:27:54,707 - app.services.cleaning_service - INFO - Starting data cleaning for vendor 'skins_nl' with 40 rows
2025-08-01 14:27:54,747 - httpx - INFO - HTTP Request: POST https://nrkodllueunpbiotjbql.supabase.co/rest/v1/processing_logs "HTTP/2 404 Not Found"
2025-08-01 14:27:54,748 - app.services.db_service - WARNING - Failed to log processing step: {}
DEBUG: Applying vendor-specific cleaning for vendor: 'skins_nl'
DEBUG: Using _clean_skins_nl_data()
DEBUG: Extracting date from Skins NL filename: 'Demo_ReportPeriod03-2025.xlsx'
DEBUG: Parsed Skins NL date - Month: 3, Year: 2025
DEBUG: Final Skins NL date - Month: 3, Year: 2025
DEBUG: Available columns in Skins NL file: ['Brand', 'Article', 'EANCode', 'SalesAmount', 'SalesAmountSPLY', 'SalesAmountVariance', 'SalesQuantity', 'SalesQuantitySPLY', 'SalesQuantityVariance']
DEBUG: Found EAN column (mapping to functional_name): EANCode
DEBUG: Found quantity column: SalesQuantity
DEBUG: Found sales amount column: SalesAmount
DEBUG: Column mapping for Skins NL: {'EANCode': 'functional_name', 'SalesQuantity': 'quantity', 'SalesAmount': 'sales_lc'}
DEBUG: Columns after mapping: ['Brand', 'Article', 'functional_name', 'sales_lc', 'SalesAmountSPLY', 'SalesAmountVariance', 'quantity', 'SalesQuantitySPLY', 'SalesQuantityVariance']
/home/david/mockDataRepo/backend/app/pipeline/cleaners.py:587: FutureWarning: Setting an item of incompatible dtype is deprecated and will raise in a future error of pandas. Value '116.0' has dtype incompatible with float64, please explicitly cast to a compatible dtype first.
  df.at[idx, 'sales_lc'] = str(cleaned_value)
DEBUG: Filtering rows with missing/invalid quantity. Rows before: 40
DEBUG: Quantity analysis - Total: 40, NotNA: 31, Empty string: 0, Zero string: 0, Zero numeric: 0
DEBUG: Sample quantity values: [nan, 2.0, nan, 1.0, nan, 1.0, nan, 3.0, nan, 16.0]
DEBUG: Rows after filtering invalid quantity: 31
DEBUG: Common cleaning - quantity filtering. Rows before: 31
DEBUG: Common cleaning - converted quantity to numeric. Rows after: 31
2025-08-01 14:27:54,751 - app.services.cleaning_service - INFO - Cleaned 31 rows (original: 40)
2025-08-01 14:27:54,751 - app.services.cleaning_service - INFO - Transformations applied: 33
2025-08-01 14:27:54,800 - httpx - INFO - HTTP Request: POST https://nrkodllueunpbiotjbql.supabase.co/rest/v1/processing_logs "HTTP/2 404 Not Found"
2025-08-01 14:27:54,801 - app.services.db_service - WARNING - Failed to log processing step: {}
2025-08-01 14:27:54,801 - app.services.cleaning_service - INFO - Cleaned data columns: ['Brand', 'Article', 'functional_name', 'sales_lc', 'SalesAmountSPLY', 'SalesAmountVariance', 'quantity', 'SalesQuantitySPLY', 'SalesQuantityVariance', 'report_year', 'report_month', 'reseller', 'currency', 'product_ean']
2025-08-01 14:27:54,803 - app.services.cleaning_service - INFO - Cleaned data sample: [{'Brand': 'TaskifAI', 'Article': 'Article 2', 'functional_name': 'PRDT35', 'sales_lc': '116.0', 'SalesAmountSPLY': 142.0, 'SalesAmountVariance': -0.181, 'quantity': 2.0, 'SalesQuantitySPLY': 2.0, 'SalesQuantityVariance': 0.0, 'report_year': 2025, 'report_month': 3, 'reseller': 'TaskifAI', 'currency': 'EUR', 'product_ean': ''}, {'Brand': 'TaskifAI', 'Article': 'Article 4', 'functional_name': 'PRGL40', 'sales_lc': '58.0', 'SalesAmountSPLY': 142.0, 'SalesAmountVariance': -0.591, 'quantity': 1.0, 'SalesQuantitySPLY': 2.0, 'SalesQuantityVariance': -0.5, 'report_year': 2025, 'report_month': 3, 'reseller': 'TaskifAI', 'currency': 'EUR', 'product_ean': ''}, {'Brand': 'TaskifAI', 'Article': 'Article 6', 'functional_name': 'PRBT75', 'sales_lc': '58.0', 'SalesAmountSPLY': 142.0, 'SalesAmountVariance': -0.591, 'quantity': 1.0, 'SalesQuantitySPLY': 2.0, 'SalesQuantityVariance': -0.5, 'report_year': 2025, 'report_month': 3, 'reseller': 'TaskifAI', 'currency': 'EUR', 'product_ean': ''}]
2025-08-01 14:27:54,803 - app.services.cleaning_service - INFO - Cleaned data types: {'Brand': dtype('O'), 'Article': dtype('O'), 'functional_name': dtype('O'), 'sales_lc': dtype('O'), 'SalesAmountSPLY': dtype('float64'), 'SalesAmountVariance': dtype('float64'), 'quantity': dtype('float64'), 'SalesQuantitySPLY': dtype('float64'), 'SalesQuantityVariance': dtype('float64'), 'report_year': dtype('int64'), 'report_month': dtype('int64'), 'reseller': dtype('O'), 'currency': dtype('O'), 'product_ean': dtype('O')}
2025-08-01 14:27:54,803 - app.services.cleaning_service - INFO - Starting data normalization for vendor 'skins_nl' with 31 cleaned rows
2025-08-01 14:27:54,844 - httpx - INFO - HTTP Request: POST https://nrkodllueunpbiotjbql.supabase.co/rest/v1/processing_logs "HTTP/2 404 Not Found"
2025-08-01 14:27:54,845 - app.services.db_service - WARNING - Failed to log processing step: {}
DEBUG: Starting normalization for vendor 'skins_nl' with 31 rows
DEBUG: Input columns: ['Brand', 'Article', 'functional_name', 'sales_lc', 'SalesAmountSPLY', 'SalesAmountVariance', 'quantity', 'SalesQuantitySPLY', 'SalesQuantityVariance', 'report_year', 'report_month', 'reseller', 'currency', 'product_ean']
DEBUG: Sample input row: {'Brand': 'TaskifAI', 'Article': 'Article 2', 'functional_name': 'PRDT35', 'sales_lc': '116.0', 'SalesAmountSPLY': 142.0, 'SalesAmountVariance': -0.181, 'quantity': 2.0, 'SalesQuantitySPLY': 2.0, 'SalesQuantityVariance': 0.0, 'report_year': 2025, 'report_month': 3, 'reseller': 'TaskifAI', 'currency': 'EUR', 'product_ean': ''}
DEBUG: Preserved sales_lc for skins_nl: ['116.0', '58.0', '58.0', '174.0', '2028.0']
DEBUG: Added sales_eur conversion for skins_nl EUR data
DEBUG: Zero quantity - Including 0 rows with sales, Excluding 0 rows without sales
DEBUG: Negative quantity - Including 0 rows with sales, Excluding 0 rows without sales
DEBUG: Normalization complete for vendor 'skins_nl' - 31 rows
DEBUG: Final normalized columns: ['product_ean', 'year', 'month', 'quantity', 'sales_lc', 'functional_name', 'currency', 'sales_eur', 'reseller']
DEBUG: Sample normalized row: {'product_ean': '', 'year': 2025, 'month': 3, 'quantity': 2, 'sales_lc': '116.0', 'functional_name': 'PRDT35', 'currency': 'EUR', 'sales_eur': 116.0, 'reseller': 'TaskifAI'}
2025-08-01 14:27:54,862 - app.services.cleaning_service - INFO - Normalized 31 rows
2025-08-01 14:27:54,906 - httpx - INFO - HTTP Request: POST https://nrkodllueunpbiotjbql.supabase.co/rest/v1/processing_logs "HTTP/2 404 Not Found"
2025-08-01 14:27:54,907 - app.services.db_service - WARNING - Failed to log processing step: {}
2025-08-01 14:27:54,910 - app.services.cleaning_service - INFO - Normalized data sample: [{'product_ean': '', 'year': 2025, 'month': 3, 'quantity': 2, 'sales_lc': '116.0', 'functional_name': 'PRDT35', 'currency': 'EUR', 'sales_eur': 116.0, 'reseller': 'TaskifAI'}, {'product_ean': '', 'year': 2025, 'month': 3, 'quantity': 1, 'sales_lc': '58.0', 'functional_name': 'PRGL40', 'currency': 'EUR', 'sales_eur': 58.0, 'reseller': 'TaskifAI'}, {'product_ean': '', 'year': 2025, 'month': 3, 'quantity': 1, 'sales_lc': '58.0', 'functional_name': 'PRBT75', 'currency': 'EUR', 'sales_eur': 58.0, 'reseller': 'TaskifAI'}]
2025-08-01 14:27:54,910 - app.services.cleaning_service - INFO - Normalized columns: ['product_ean', 'year', 'month', 'quantity', 'sales_lc', 'functional_name', 'currency', 'sales_eur', 'reseller']
2025-08-01 14:27:54,910 - app.services.cleaning_service - INFO - Normalized data types: {'product_ean': dtype('O'), 'year': Int64Dtype(), 'month': Int64Dtype(), 'quantity': Int64Dtype(), 'sales_lc': dtype('O'), 'functional_name': dtype('O'), 'currency': dtype('O'), 'sales_eur': dtype('float64'), 'reseller': dtype('O')}
2025-08-01 14:27:54,911 - app.services.cleaning_service - INFO - All required fields present
2025-08-01 14:27:54,913 - app.services.cleaning_service - INFO - Converting 31 entries for database insertion
2025-08-01 14:27:54,913 - app.services.cleaning_service - INFO - Sample entry for insertion: {'product_ean': '', 'year': 2025, 'month': 3, 'quantity': 2, 'sales_lc': '116.0', 'functional_name': 'PRDT35', 'currency': 'EUR', 'sales_eur': 116.0, 'reseller': 'TaskifAI'}
2025-08-01 14:27:54,913 - app.services.cleaning_service - INFO - Attempting to insert 31 entries into mock_data
2025-08-01 14:27:54,967 - httpx - INFO - HTTP Request: POST https://nrkodllueunpbiotjbql.supabase.co/rest/v1/processing_logs "HTTP/2 404 Not Found"
2025-08-01 14:27:54,968 - app.services.db_service - WARNING - Failed to log processing step: {}
DB Service: Starting insert_mock_data for upload e87a76c0-3596-4bd6-a9a8-439e0d852ce7 with 31 entries
DB Service: Sample mock_data entry: {'id': '69dc9f55-9278-4d67-90ab-35e0b5901412', 'product_ean': '', 'month': 3, 'year': 2025, 'quantity': 2, 'sales_lc': '116.0', 'sales_eur': 116.0, 'currency': 'EUR', 'reseller': 'TaskifAI', 'functional_name': 'PRDT35', 'sales_date': datetime.date(2025, 3, 1), 'upload_id': 'e87a76c0-3596-4bd6-a9a8-439e0d852ce7'}
DB Service: Error inserting mock data: Object of type date is not JSON serializable
DB Service: Full traceback: {}
2025-08-01 14:27:54,971 - app.services.cleaning_service - ERROR - Error processing upload e87a76c0-3596-4bd6-a9a8-439e0d852ce7: Failed to insert mock data: Object of type date is not JSON serializable
2025-08-01 14:27:54,971 - app.services.cleaning_service - ERROR - Full traceback: Traceback (most recent call last):
  File "/home/david/mockDataRepo/backend/app/services/db_service.py", line 371, in insert_mock_data
    result = self.service_supabase.table("mock_data").insert(mock_data_entries).execute()
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/david/mockDataRepo/backend/venv/lib/python3.12/site-packages/postgrest/_sync/request_builder.py", line 58, in execute
    r = self.session.request(
        ^^^^^^^^^^^^^^^^^^^^^
  File "/home/david/mockDataRepo/backend/venv/lib/python3.12/site-packages/httpx/_client.py", line 824, in request
    request = self.build_request(
              ^^^^^^^^^^^^^^^^^^^
  File "/home/david/mockDataRepo/backend/venv/lib/python3.12/site-packages/httpx/_client.py", line 358, in build_request
    return Request(
           ^^^^^^^^
  File "/home/david/mockDataRepo/backend/venv/lib/python3.12/site-packages/httpx/_models.py", line 342, in __init__
    headers, stream = encode_request(
                      ^^^^^^^^^^^^^^^
  File "/home/david/mockDataRepo/backend/venv/lib/python3.12/site-packages/httpx/_content.py", line 214, in encode_request
    return encode_json(json)
           ^^^^^^^^^^^^^^^^^
  File "/home/david/mockDataRepo/backend/venv/lib/python3.12/site-packages/httpx/_content.py", line 177, in encode_json
    body = json_dumps(json).encode("utf-8")
           ^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/json/__init__.py", line 231, in dumps
    return _default_encoder.encode(obj)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/json/encoder.py", line 200, in encode
    chunks = self.iterencode(o, _one_shot=True)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/json/encoder.py", line 258, in iterencode
    return _iterencode(o, 0)
           ^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/json/encoder.py", line 180, in default
    raise TypeError(f'Object of type {o.__class__.__name__} '
TypeError: Object of type date is not JSON serializable

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/david/mockDataRepo/backend/app/services/cleaning_service.py", line 213, in process_file
    await self.db_service.insert_mock_data(upload_id, sellout_entries)
  File "/home/david/mockDataRepo/backend/app/services/db_service.py", line 379, in insert_mock_data
    raise DatabaseException(f"Failed to insert mock data: {str(e)}")
app.utils.exceptions.DatabaseException: Failed to insert mock data: Object of type date is not JSON serializable

2025-08-01 14:27:55,021 - httpx - INFO - HTTP Request: PATCH https://nrkodllueunpbiotjbql.supabase.co/rest/v1/uploads?id=eq.e87a76c0-3596-4bd6-a9a8-439e0d852ce7 "HTTP/2 200 OK"
2025-08-01 14:27:56,693 - app.api.auth - INFO - get_current_user called
2025-08-01 14:27:56,693 - app.api.auth - INFO - Authorization header: Present
2025-08-01 14:27:56,694 - app.api.auth - INFO - Extracted token length: 722
2025-08-01 14:27:56,694 - app.services.auth_service - INFO - Attempting token verification for token ending with: ...xz-A
2025-08-01 14:27:56,803 - httpx - INFO - HTTP Request: GET https://nrkodllueunpbiotjbql.supabase.co/auth/v1/user "HTTP/2 200 OK"
2025-08-01 14:27:56,804 - app.services.auth_service - INFO - Token verification successful for user: user@email.com
2025-08-01 14:27:56,804 - app.api.auth - INFO - Successfully authenticated user: user@email.com
2025-08-01 14:27:56,805 - app.api.status - INFO - 🔍 STATUS DEBUG - Current user: {'id': 'fdd71f95-e8d4-417e-85aa-9b7b0c92436d', 'app_metadata': {'provider': 'email', 'providers': ['email']}, 'user_metadata': {'email_verified': True}, 'aud': 'authenticated', 'confirmation_sent_at': None, 'recovery_sent_at': None, 'email_change_sent_at': None, 'new_email': None, 'new_phone': None, 'invited_at': None, 'action_link': None, 'email': 'user@email.com', 'phone': '', 'created_at': datetime.datetime(2025, 7, 22, 20, 40, 20, 818984, tzinfo=TzInfo(UTC)), 'confirmed_at': datetime.datetime(2025, 7, 30, 10, 26, 20, 179047, tzinfo=TzInfo(UTC)), 'email_confirmed_at': datetime.datetime(2025, 7, 30, 10, 26, 20, 179047, tzinfo=TzInfo(UTC)), 'phone_confirmed_at': None, 'last_sign_in_at': datetime.datetime(2025, 8, 1, 12, 23, 1, 651542, tzinfo=TzInfo(UTC)), 'role': 'authenticated', 'updated_at': datetime.datetime(2025, 8, 1, 12, 23, 1, 659794, tzinfo=TzInfo(UTC)), 'identities': [{'id': 'fdd71f95-e8d4-417e-85aa-9b7b0c92436d', 'identity_id': '1152cd60-4a0e-46c9-8fda-8810acb0a814', 'user_id': 'fdd71f95-e8d4-417e-85aa-9b7b0c92436d', 'identity_data': {'email': 'user@email.com', 'email_verified': False, 'phone_verified': False, 'sub': 'fdd71f95-e8d4-417e-85aa-9b7b0c92436d'}, 'provider': 'email', 'created_at': datetime.datetime(2025, 7, 22, 20, 40, 20, 836907, tzinfo=TzInfo(UTC)), 'last_sign_in_at': datetime.datetime(2025, 7, 22, 20, 40, 20, 836838, tzinfo=TzInfo(UTC)), 'updated_at': datetime.datetime(2025, 7, 22, 20, 40, 20, 836907, tzinfo=TzInfo(UTC))}], 'is_anonymous': False, 'factors': None}
2025-08-01 14:27:56,805 - app.api.status - INFO - 🔍 STATUS DEBUG - User ID: fdd71f95-e8d4-417e-85aa-9b7b0c92436d
2025-08-01 14:27:56,805 - app.api.status - INFO - 🔍 STATUS DEBUG - User email: user@email.com
2025-08-01 14:27:56,805 - app.api.status - INFO - 🔍 STATUS DEBUG - Token extracted, length: 722
2025-08-01 14:27:56,991 - httpx - INFO - HTTP Request: GET https://nrkodllueunpbiotjbql.supabase.co/rest/v1/uploads?select=%2A&user_id=eq.fdd71f95-e8d4-417e-85aa-9b7b0c92436d&order=uploaded_at.desc "HTTP/2 200 OK"
2025-08-01 14:27:56,992 - app.services.db_service - INFO - 📊 DB Service: Query for user fdd71f95... returned 22 uploads
2025-08-01 14:27:56,992 - app.api.status - INFO - 🔍 STATUS DEBUG - Query returned 22 uploads
2025-08-01 14:27:56,992 - app.api.status - INFO - 🔍 STATUS DEBUG - Sample upload: {'id': 'e87a76c0-3596-4bd6-a9a8-439e0d852ce7', 'user_id': 'fdd71f95-e8d4-417e-85aa-9b7b0c92436d', 'filename': 'Demo_ReportPeriod03-2025.xlsx', 'file_size': 17728, 'uploaded_at': '2025-08-01T12:27:52.286312+00:00', 'status': 'failed', 'error_message': 'Failed to insert mock data: Object of type date is not JSON serializable', 'rows_processed': None, 'rows_cleaned': None, 'processing_time_ms': None}
INFO:     127.0.0.1:33314 - "GET /api/status/uploads HTTP/1.1" 200 OK
2025-08-01 14:27:57,063 - app.api.auth - INFO - get_current_user called
2025-08-01 14:27:57,063 - app.api.auth - INFO - Authorization header: Present
2025-08-01 14:27:57,063 - app.api.auth - INFO - Extracted token length: 722
2025-08-01 14:27:57,063 - app.services.auth_service - INFO - Attempting token verification for token ending with: ...xz-A
2025-08-01 14:27:57,169 - httpx - INFO - HTTP Request: GET https://nrkodllueunpbiotjbql.supabase.co/auth/v1/user "HTTP/2 200 OK"
2025-08-01 14:27:57,169 - app.services.auth_service - INFO - Token verification successful for user: user@email.com
2025-08-01 14:27:57,169 - app.api.auth - INFO - Successfully authenticated user: user@email.com
2025-08-01 14:27:57,170 - app.api.status - INFO - 🔍 STATUS DEBUG - Current user: {'id': 'fdd71f95-e8d4-417e-85aa-9b7b0c92436d', 'app_metadata': {'provider': 'email', 'providers': ['email']}, 'user_metadata': {'email_verified': True}, 'aud': 'authenticated', 'confirmation_sent_at': None, 'recovery_sent_at': None, 'email_change_sent_at': None, 'new_email': None, 'new_phone': None, 'invited_at': None, 'action_link': None, 'email': 'user@email.com', 'phone': '', 'created_at': datetime.datetime(2025, 7, 22, 20, 40, 20, 818984, tzinfo=TzInfo(UTC)), 'confirmed_at': datetime.datetime(2025, 7, 30, 10, 26, 20, 179047, tzinfo=TzInfo(UTC)), 'email_confirmed_at': datetime.datetime(2025, 7, 30, 10, 26, 20, 179047, tzinfo=TzInfo(UTC)), 'phone_confirmed_at': None, 'last_sign_in_at': datetime.datetime(2025, 8, 1, 12, 23, 1, 651542, tzinfo=TzInfo(UTC)), 'role': 'authenticated', 'updated_at': datetime.datetime(2025, 8, 1, 12, 23, 1, 659794, tzinfo=TzInfo(UTC)), 'identities': [{'id': 'fdd71f95-e8d4-417e-85aa-9b7b0c92436d', 'identity_id': '1152cd60-4a0e-46c9-8fda-8810acb0a814', 'user_id': 'fdd71f95-e8d4-417e-85aa-9b7b0c92436d', 'identity_data': {'email': 'user@email.com', 'email_verified': False, 'phone_verified': False, 'sub': 'fdd71f95-e8d4-417e-85aa-9b7b0c92436d'}, 'provider': 'email', 'created_at': datetime.datetime(2025, 7, 22, 20, 40, 20, 836907, tzinfo=TzInfo(UTC)), 'last_sign_in_at': datetime.datetime(2025, 7, 22, 20, 40, 20, 836838, tzinfo=TzInfo(UTC)), 'updated_at': datetime.datetime(2025, 7, 22, 20, 40, 20, 836907, tzinfo=TzInfo(UTC))}], 'is_anonymous': False, 'factors': None}
2025-08-01 14:27:57,170 - app.api.status - INFO - 🔍 STATUS DEBUG - User ID: fdd71f95-e8d4-417e-85aa-9b7b0c92436d
2025-08-01 14:27:57,170 - app.api.status - INFO - 🔍 STATUS DEBUG - User email: user@email.com
2025-08-01 14:27:57,170 - app.api.status - INFO - 🔍 STATUS DEBUG - Token extracted, length: 722
2025-08-01 14:27:57,338 - httpx - INFO - HTTP Request: GET https://nrkodllueunpbiotjbql.supabase.co/rest/v1/uploads?select=%2A&user_id=eq.fdd71f95-e8d4-417e-85aa-9b7b0c92436d&order=uploaded_at.desc "HTTP/2 200 OK"
2025-08-01 14:27:57,341 - app.services.db_service - INFO - 📊 DB Service: Query for user fdd71f95... returned 22 uploads
2025-08-01 14:27:57,341 - app.api.status - INFO - 🔍 STATUS DEBUG - Query returned 22 uploads
2025-08-01 14:27:57,341 - app.api.status - INFO - 🔍 STATUS DEBUG - Sample upload: {'id': 'e87a76c0-3596-4bd6-a9a8-439e0d852ce7', 'user_id': 'fdd71f95-e8d4-417e-85aa-9b7b0c92436d', 'filename': 'Demo_ReportPeriod03-2025.xlsx', 'file_size': 17728, 'uploaded_at': '2025-08-01T12:27:52.286312+00:00', 'status': 'failed', 'error_message': 'Failed to insert mock data: Object of type date is not JSON serializable', 'rows_processed': None, 'rows_cleaned': None, 'processing_time_ms': None}
INFO:     127.0.0.1:33324 - "GET /api/status/uploads HTTP/1.1" 200 OK
2025-08-01 14:28:26,697 - app.api.auth - INFO - get_current_user called
2025-08-01 14:28:26,697 - app.api.auth - INFO - Authorization header: Present
2025-08-01 14:28:26,697 - app.api.auth - INFO - Extracted token length: 722
2025-08-01 14:28:26,697 - app.services.auth_service - INFO - Attempting token verification for token ending with: ...xz-A
2025-08-01 14:28:26,804 - httpx - INFO - HTTP Request: GET https://nrkodllueunpbiotjbql.supabase.co/auth/v1/user "HTTP/2 200 OK"
2025-08-01 14:28:26,805 - app.services.auth_service - INFO - Token verification successful for user: user@email.com
2025-08-01 14:28:26,805 - app.api.auth - INFO - Successfully authenticated user: user@email.com
2025-08-01 14:28:26,806 - app.api.status - INFO - 🔍 STATUS DEBUG - Current user: {'id': 'fdd71f95-e8d4-417e-85aa-9b7b0c92436d', 'app_metadata': {'provider': 'email', 'providers': ['email']}, 'user_metadata': {'email_verified': True}, 'aud': 'authenticated', 'confirmation_sent_at': None, 'recovery_sent_at': None, 'email_change_sent_at': None, 'new_email': None, 'new_phone': None, 'invited_at': None, 'action_link': None, 'email': 'user@email.com', 'phone': '', 'created_at': datetime.datetime(2025, 7, 22, 20, 40, 20, 818984, tzinfo=TzInfo(UTC)), 'confirmed_at': datetime.datetime(2025, 7, 30, 10, 26, 20, 179047, tzinfo=TzInfo(UTC)), 'email_confirmed_at': datetime.datetime(2025, 7, 30, 10, 26, 20, 179047, tzinfo=TzInfo(UTC)), 'phone_confirmed_at': None, 'last_sign_in_at': datetime.datetime(2025, 8, 1, 12, 23, 1, 651542, tzinfo=TzInfo(UTC)), 'role': 'authenticated', 'updated_at': datetime.datetime(2025, 8, 1, 12, 23, 1, 659794, tzinfo=TzInfo(UTC)), 'identities': [{'id': 'fdd71f95-e8d4-417e-85aa-9b7b0c92436d', 'identity_id': '1152cd60-4a0e-46c9-8fda-8810acb0a814', 'user_id': 'fdd71f95-e8d4-417e-85aa-9b7b0c92436d', 'identity_data': {'email': 'user@email.com', 'email_verified': False, 'phone_verified': False, 'sub': 'fdd71f95-e8d4-417e-85aa-9b7b0c92436d'}, 'provider': 'email', 'created_at': datetime.datetime(2025, 7, 22, 20, 40, 20, 836907, tzinfo=TzInfo(UTC)), 'last_sign_in_at': datetime.datetime(2025, 7, 22, 20, 40, 20, 836838, tzinfo=TzInfo(UTC)), 'updated_at': datetime.datetime(2025, 7, 22, 20, 40, 20, 836907, tzinfo=TzInfo(UTC))}], 'is_anonymous': False, 'factors': None}
2025-08-01 14:28:26,806 - app.api.status - INFO - 🔍 STATUS DEBUG - User ID: fdd71f95-e8d4-417e-85aa-9b7b0c92436d
2025-08-01 14:28:26,806 - app.api.status - INFO - 🔍 STATUS DEBUG - User email: user@email.com
2025-08-01 14:28:26,806 - app.api.status - INFO - 🔍 STATUS DEBUG - Token extracted, length: 722
2025-08-01 14:28:26,995 - httpx - INFO - HTTP Request: GET https://nrkodllueunpbiotjbql.supabase.co/rest/v1/uploads?select=%2A&user_id=eq.fdd71f95-e8d4-417e-85aa-9b7b0c92436d&order=uploaded_at.desc "HTTP/2 200 OK"
2025-08-01 14:28:26,996 - app.services.db_service - INFO - 📊 DB Service: Query for user fdd71f95... returned 22 uploads
2025-08-01 14:28:26,996 - app.api.status - INFO - 🔍 STATUS DEBUG - Query returned 22 uploads
2025-08-01 14:28:26,996 - app.api.status - INFO - 🔍 STATUS DEBUG - Sample upload: {'id': 'e87a76c0-3596-4bd6-a9a8-439e0d852ce7', 'user_id': 'fdd71f95-e8d4-417e-85aa-9b7b0c92436d', 'filename': 'Demo_ReportPeriod03-2025.xlsx', 'file_size': 17728, 'uploaded_at': '2025-08-01T12:27:52.286312+00:00', 'status': 'failed', 'error_message': 'Failed to insert mock data: Object of type date is not JSON serializable', 'rows_processed': None, 'rows_cleaned': None, 'processing_time_ms': None}
INFO:     127.0.0.1:51216 - "GET /api/status/uploads HTTP/1.1" 200 OK
2025-08-01 14:28:56,697 - app.api.auth - INFO - get_current_user called
2025-08-01 14:28:56,697 - app.api.auth - INFO - Authorization header: Present
2025-08-01 14:28:56,697 - app.api.auth - INFO - Extracted token length: 722
2025-08-01 14:28:56,697 - app.services.auth_service - INFO - Attempting token verification for token ending with: ...xz-A
2025-08-01 14:28:56,969 - httpx - INFO - HTTP Request: GET https://nrkodllueunpbiotjbql.supabase.co/auth/v1/user "HTTP/2 200 OK"
2025-08-01 14:28:56,969 - app.services.auth_service - INFO - Token verification successful for user: user@email.com
2025-08-01 14:28:56,970 - app.api.auth - INFO - Successfully authenticated user: user@email.com
2025-08-01 14:28:56,970 - app.api.status - INFO - 🔍 STATUS DEBUG - Current user: {'id': 'fdd71f95-e8d4-417e-85aa-9b7b0c92436d', 'app_metadata': {'provider': 'email', 'providers': ['email']}, 'user_metadata': {'email_verified': True}, 'aud': 'authenticated', 'confirmation_sent_at': None, 'recovery_sent_at': None, 'email_change_sent_at': None, 'new_email': None, 'new_phone': None, 'invited_at': None, 'action_link': None, 'email': 'user@email.com', 'phone': '', 'created_at': datetime.datetime(2025, 7, 22, 20, 40, 20, 818984, tzinfo=TzInfo(UTC)), 'confirmed_at': datetime.datetime(2025, 7, 30, 10, 26, 20, 179047, tzinfo=TzInfo(UTC)), 'email_confirmed_at': datetime.datetime(2025, 7, 30, 10, 26, 20, 179047, tzinfo=TzInfo(UTC)), 'phone_confirmed_at': None, 'last_sign_in_at': datetime.datetime(2025, 8, 1, 12, 23, 1, 651542, tzinfo=TzInfo(UTC)), 'role': 'authenticated', 'updated_at': datetime.datetime(2025, 8, 1, 12, 23, 1, 659794, tzinfo=TzInfo(UTC)), 'identities': [{'id': 'fdd71f95-e8d4-417e-85aa-9b7b0c92436d', 'identity_id': '1152cd60-4a0e-46c9-8fda-8810acb0a814', 'user_id': 'fdd71f95-e8d4-417e-85aa-9b7b0c92436d', 'identity_data': {'email': 'user@email.com', 'email_verified': False, 'phone_verified': False, 'sub': 'fdd71f95-e8d4-417e-85aa-9b7b0c92436d'}, 'provider': 'email', 'created_at': datetime.datetime(2025, 7, 22, 20, 40, 20, 836907, tzinfo=TzInfo(UTC)), 'last_sign_in_at': datetime.datetime(2025, 7, 22, 20, 40, 20, 836838, tzinfo=TzInfo(UTC)), 'updated_at': datetime.datetime(2025, 7, 22, 20, 40, 20, 836907, tzinfo=TzInfo(UTC))}], 'is_anonymous': False, 'factors': None}
2025-08-01 14:28:56,970 - app.api.status - INFO - 🔍 STATUS DEBUG - User ID: fdd71f95-e8d4-417e-85aa-9b7b0c92436d
2025-08-01 14:28:56,970 - app.api.status - INFO - 🔍 STATUS DEBUG - User email: user@email.com
2025-08-01 14:28:56,970 - app.api.status - INFO - 🔍 STATUS DEBUG - Token extracted, length: 722
2025-08-01 14:28:57,195 - httpx - INFO - HTTP Request: GET https://nrkodllueunpbiotjbql.supabase.co/rest/v1/uploads?select=%2A&user_id=eq.fdd71f95-e8d4-417e-85aa-9b7b0c92436d&order=uploaded_at.desc "HTTP/2 200 OK"
2025-08-01 14:28:57,196 - app.services.db_service - INFO - 📊 DB Service: Query for user fdd71f95... returned 22 uploads
2025-08-01 14:28:57,196 - app.api.status - INFO - 🔍 STATUS DEBUG - Query returned 22 uploads
2025-08-01 14:28:57,196 - app.api.status - INFO - 🔍 STATUS DEBUG - Sample upload: {'id': 'e87a76c0-3596-4bd6-a9a8-439e0d852ce7', 'user_id': 'fdd71f95-e8d4-417e-85aa-9b7b0c92436d', 'filename': 'Demo_ReportPeriod03-2025.xlsx', 'file_size': 17728, 'uploaded_at': '2025-08-01T12:27:52.286312+00:00', 'status': 'failed', 'error_message': 'Failed to insert mock data: Object of type date is not JSON serializable', 'rows_processed': None, 'rows_cleaned': None, 'processing_time_ms': None}
INFO:     127.0.0.1:59426 - "GET /api/status/uploads HTTP/1.1" 200 OK
