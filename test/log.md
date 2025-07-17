INFO:     Will watch for changes in these directories: ['/home/david/cursor_project/backend']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [232565] using WatchFiles
INFO:     Started server process [232582]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     127.0.0.1:53778 - "OPTIONS /api/auth/login HTTP/1.1" 200 OK
2025-07-17 22:36:29,642 - httpx - INFO - HTTP Request: POST https://edckqdrbgtnnjfnshjfq.supabase.co/auth/v1/token?grant_type=password "HTTP/2 200 OK"
INFO:     127.0.0.1:53780 - "POST /api/auth/login HTTP/1.1" 200 OK
INFO:     127.0.0.1:53780 - "OPTIONS /api/auth/debug-token HTTP/1.1" 200 OK
2025-07-17 22:36:29,727 - app.services.auth_service - INFO - Attempting token verification for token starting with: eyJhbGciOiJIUzI1NiIs...
2025-07-17 22:36:29,979 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/auth/v1/user "HTTP/2 200 OK"
2025-07-17 22:36:29,980 - app.services.auth_service - INFO - Token verification successful for user: user@email.com
INFO:     127.0.0.1:53778 - "GET /api/auth/debug-token HTTP/1.1" 200 OK
INFO:     127.0.0.1:53778 - "GET /health HTTP/1.1" 200 OK
INFO:     127.0.0.1:53778 - "GET /health HTTP/1.1" 200 OK
INFO:     127.0.0.1:35122 - "OPTIONS /api/chat/query HTTP/1.1" 200 OK
2025-07-17 22:36:39,490 - app.services.auth_service - INFO - Attempting token verification for token starting with: eyJhbGciOiJIUzI1NiIs...
2025-07-17 22:36:39,648 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/auth/v1/user "HTTP/2 200 OK"
2025-07-17 22:36:39,649 - app.services.auth_service - INFO - Token verification successful for user: user@email.com
2025-07-17 22:36:39,649 - app.api.chat - INFO - Processing chat query for user user@email.com: "Show me my top 5 resellers...
🎯 MESSAGE INTENT: data_query
🎯 ORIGINAL MESSAGE: '"Show me my top 5 resellers'
🤖 DATA QUESTION CLASSIFICATION: show_table
🔄 CHAT2DB SELF-CORRECTION: Starting query execution with fallbacks
🎯 CHAT2DB MULTI-PATTERN SQL GENERATION
============================================================
Enhanced message: '"Show me my top 5 resellers' -> '"my top 5 resellers'
🎯 SQL INTENT DETECTION: Enhanced='"my top 5 resellers', Params={'limit': 5}
👥 RESELLER ANALYSIS: reseller=True, analysis=True
👥 MATCHED: Reseller analysis intent
✅ Pattern 1 (Intent): Confidence 1.00
🔄 Refreshing enhanced database schema cache...
📊 CHAT2DB SCHEMA ENHANCEMENT: Gathering table statistics...
2025-07-17 22:36:40,236 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/sellout_entries2?select=%2A&limit=1 "HTTP/2 200 OK"
2025-07-17 22:36:40,498 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/sellout_entries2?select=%2A "HTTP/2 206 Partial Content"
2025-07-17 22:36:40,560 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/sellout_entries2?select=%2A&limit=3 "HTTP/2 200 OK"
2025-07-17 22:36:40,622 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/uploads?select=%2A&limit=1 "HTTP/2 200 OK"
2025-07-17 22:36:40,692 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/uploads?select=%2A "HTTP/2 200 OK"
2025-07-17 22:36:40,743 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/uploads?select=%2A&limit=3 "HTTP/2 200 OK"
2025-07-17 22:36:40,794 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/products?select=%2A&limit=1 "HTTP/2 200 OK"
2025-07-17 22:36:40,848 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/products?select=%2A "HTTP/2 200 OK"
2025-07-17 22:36:40,906 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/products?select=%2A&limit=3 "HTTP/2 200 OK"
2025-07-17 22:36:40,963 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/chat_sessions?select=%2A&limit=1 "HTTP/2 200 OK"
2025-07-17 22:36:41,079 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/chat_sessions?select=%2A "HTTP/2 200 OK"
2025-07-17 22:36:41,126 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/chat_sessions?select=%2A&limit=3 "HTTP/2 200 OK"
2025-07-17 22:36:41,199 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/chat_messages?select=%2A&limit=1 "HTTP/2 200 OK"
No data found in table chat_messages
2025-07-17 22:36:41,269 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/email_logs?select=%2A&limit=1 "HTTP/2 200 OK"
No data found in table email_logs
📊 EXECUTING SELLOUT QUERY: 
                SELECT 
                    COUNT(*) as total_records,
                    COUNT(DISTINCT functional_name) as unique_products,
                    COUNT(DISTINCT reseller) as unique_resellers,
                    COUNT(DISTINCT CONCAT(year, '-', month)) as unique_time_periods,
                    MIN(sales_eur) as min_sales,
                    MAX(sales_eur) as max_sales,
                    AVG(sales_eur) as avg_sales,
                    SUM(sales_eur) as total_sales,
                    MIN(quantity) as min_quantity,
                    MAX(quantity) as max_quantity,
                    AVG(quantity) as avg_quantity,
                    SUM(quantity) as total_quantity,
                    MIN(year) as earliest_year,
                    MAX(year) as latest_year
                FROM sellout_entries2 se 
                JOIN uploads u ON se.upload_id = u.id;
                
📊 PARAMS: None
⚠️ WARNING: No user_id provided for sellout query
📊 EXECUTING SELLOUT QUERY: 
                SELECT functional_name, 
                       SUM(sales_eur) as total_sales,
                       SUM(quantity) as total_quantity
                FROM sellout_entries2 se 
                JOIN uploads u ON se.upload_id = u.id
                WHERE functional_name IS NOT NULL
                GROUP BY functional_name 
                ORDER BY total_sales DESC 
                LIMIT 5;
                
📊 PARAMS: None
⚠️ WARNING: No user_id provided for sellout query
📊 Found 0 top products for context
📊 EXECUTING SELLOUT QUERY: 
                SELECT reseller, 
                       SUM(sales_eur) as total_sales,
                       COUNT(DISTINCT functional_name) as product_count
                FROM sellout_entries2 se 
                JOIN uploads u ON se.upload_id = u.id
                WHERE reseller IS NOT NULL
                GROUP BY reseller 
                ORDER BY total_sales DESC 
                LIMIT 5;
                
📊 PARAMS: None
⚠️ WARNING: No user_id provided for sellout query
📊 Found 0 top resellers for context
✅ Enhanced schema complete with statistics and business context
✅ Enhanced schema cache refreshed. Found 4 tables
✅ Pattern 2 (Context): Confidence 1.00
✅ Pattern 3 (Template): Confidence 1.00
🏆 SELECTED: intent_based (confidence: 1.00)
📊 Generated 3 patterns total
🔄 ATTEMPT 1: Trying intent_based (confidence: 1.00)
📊 EXECUTING: 
        SELECT reseller, 
               SUM(sales_eur) AS total_sales,
               SUM(quantity...
📊 EXECUTING SELLOUT QUERY: 
        SELECT reseller, 
               SUM(sales_eur) AS total_sales,
               SUM(quantity) AS total_units,
               COUNT(*) AS transactions,
               COUNT(DISTINCT functional_name) AS unique_products
        FROM sellout_entries2 se 
        JOIN uploads u ON se.upload_id = u.id 
        WHERE u.user_id = %s
        GROUP BY reseller 
        ORDER BY total_sales DESC
        LIMIT 5;
        
📊 PARAMS: ('26d3c1b7-d944-42a0-9336-e68b1b32ebbf',)
👤 Executing query for user: 26d3c1b7-d944-42a0-9336-e68b1b32ebbf
🔍 ANALYZING QUERY: 
        SELECT RESELLER, 
               SUM(SALES_EUR) AS TOTAL_SALES,
               SUM(QUANTITY...
🛍️ DETECTED: Product analysis query
🛍️ Processing product analysis query
2025-07-17 22:36:41,371 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/sellout_entries2?select=functional_name%2C%20sales_eur%2C%20quantity%2C%20uploads%21inner%28user_id%29&uploads.user_id=eq.26d3c1b7-d944-42a0-9336-e68b1b32ebbf "HTTP/2 200 OK"
🛍️ Grouped by product: 24 products found
✅ SUCCESS: Query returned 20 results
🎯 CHAT SERVICE: Got 20 results from database
🔍 CHAT SERVICE: First result keys: ['functional_name', 'product', 'total_sales_eur', 'total_sales', 'total_quantity', 'record_count']
🔍 CHAT SERVICE: First result sample: {'functional_name': 'BBGOT100', 'product': 'BBGOT100', 'total_sales_eur': 136194.42}
🤖 CHAT SERVICE: Question type: show_table
🤖 CHAT SERVICE: Generating response for 20 results
📝 RESPONSE GEN: Question: '"Show me my top 5 resellers'
📝 RESPONSE GEN: Results count: 20
📝 RESPONSE GEN: Question type: show_table
📝 RESPONSE GEN: Sample result structure: ['functional_name', 'product', 'total_sales_eur', 'total_sales', 'total_quantity', 'record_count']
📝 RESPONSE GEN: Using contextual_summary logic
🤖 CHAT SERVICE: Generated response: I found 20 records. Covering 20 different product(s). Here are the results:...
2025-07-17 22:36:41,452 - httpx - INFO - HTTP Request: POST https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/chat_sessions "HTTP/2 201 Created"
ERROR in _insert_chat_message: not enough values to unpack (expected 7, got 5)
ERROR in _execute_insert: not enough values to unpack (expected 7, got 5)
ERROR in execute: not enough values to unpack (expected 7, got 5)
Query: 
                INSERT INTO chat_messages 
                (session_id, user_id, message_type, content, sql_query, query_result, created_at)
                VALUES (%s, %s, %s, %s, NULL, NULL, %s)
                
Params: ('1954cc07-b7bf-4386-9afb-8fb7465e1233', '26d3c1b7-d944-42a0-9336-e68b1b32ebbf', 'user', '"Show me my top 5 resellers', datetime.datetime(2025, 7, 17, 22, 36, 41, 454061))
2025-07-17 22:36:41,454 - app.services.chat_service - ERROR - Error logging chat activity: Failed to execute query: not enough values to unpack (expected 7, got 5)
INFO:     127.0.0.1:35128 - "POST /api/chat/query HTTP/1.1" 200 OK
2025-07-17 22:37:41,008 - app.services.auth_service - INFO - Attempting token verification for token starting with: eyJhbGciOiJIUzI1NiIs...
2025-07-17 22:37:41,149 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/auth/v1/user "HTTP/2 200 OK"
2025-07-17 22:37:41,150 - app.services.auth_service - INFO - Token verification successful for user: user@email.com
2025-07-17 22:37:41,150 - app.api.chat - INFO - Processing chat query for user user@email.com: what did I sell for 2024?...
🎯 MESSAGE INTENT: data_query
🎯 ORIGINAL MESSAGE: 'what did I sell for 2024?'
🤖 DATA QUESTION CLASSIFICATION: show_table
🔄 CHAT2DB SELF-CORRECTION: Starting query execution with fallbacks
🎯 CHAT2DB MULTI-PATTERN SQL GENERATION
============================================================
Enhanced message: 'what did I sell for 2024?' -> 'what did i sell year 2024?'
🎯 SQL INTENT DETECTION: Enhanced='what did i sell year 2024?', Params={'year': 2024}
📈 MATCHED: Yearly analysis intent
✅ Pattern 1 (Intent): Confidence 0.90
🔄 Refreshing enhanced database schema cache...
📊 CHAT2DB SCHEMA ENHANCEMENT: Gathering table statistics...
2025-07-17 22:37:41,388 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/sellout_entries2?select=%2A&limit=1 "HTTP/2 200 OK"
2025-07-17 22:37:41,592 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/sellout_entries2?select=%2A "HTTP/2 206 Partial Content"
2025-07-17 22:37:41,655 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/sellout_entries2?select=%2A&limit=3 "HTTP/2 200 OK"
2025-07-17 22:37:41,747 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/uploads?select=%2A&limit=1 "HTTP/2 200 OK"
2025-07-17 22:37:41,822 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/uploads?select=%2A "HTTP/2 200 OK"
2025-07-17 22:37:41,891 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/uploads?select=%2A&limit=3 "HTTP/2 200 OK"
2025-07-17 22:37:41,956 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/products?select=%2A&limit=1 "HTTP/2 200 OK"
2025-07-17 22:37:42,025 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/products?select=%2A "HTTP/2 200 OK"
2025-07-17 22:37:42,104 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/products?select=%2A&limit=3 "HTTP/2 200 OK"
2025-07-17 22:37:42,195 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/chat_sessions?select=%2A&limit=1 "HTTP/2 200 OK"
2025-07-17 22:37:42,263 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/chat_sessions?select=%2A "HTTP/2 200 OK"
2025-07-17 22:37:42,354 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/chat_sessions?select=%2A&limit=3 "HTTP/2 200 OK"
2025-07-17 22:37:42,456 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/chat_messages?select=%2A&limit=1 "HTTP/2 200 OK"
No data found in table chat_messages
2025-07-17 22:37:42,533 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/email_logs?select=%2A&limit=1 "HTTP/2 200 OK"
No data found in table email_logs
📊 EXECUTING SELLOUT QUERY: 
                SELECT 
                    COUNT(*) as total_records,
                    COUNT(DISTINCT functional_name) as unique_products,
                    COUNT(DISTINCT reseller) as unique_resellers,
                    COUNT(DISTINCT CONCAT(year, '-', month)) as unique_time_periods,
                    MIN(sales_eur) as min_sales,
                    MAX(sales_eur) as max_sales,
                    AVG(sales_eur) as avg_sales,
                    SUM(sales_eur) as total_sales,
                    MIN(quantity) as min_quantity,
                    MAX(quantity) as max_quantity,
                    AVG(quantity) as avg_quantity,
                    SUM(quantity) as total_quantity,
                    MIN(year) as earliest_year,
                    MAX(year) as latest_year
                FROM sellout_entries2 se 
                JOIN uploads u ON se.upload_id = u.id;
                
📊 PARAMS: None
⚠️ WARNING: No user_id provided for sellout query
📊 EXECUTING SELLOUT QUERY: 
                SELECT functional_name, 
                       SUM(sales_eur) as total_sales,
                       SUM(quantity) as total_quantity
                FROM sellout_entries2 se 
                JOIN uploads u ON se.upload_id = u.id
                WHERE functional_name IS NOT NULL
                GROUP BY functional_name 
                ORDER BY total_sales DESC 
                LIMIT 5;
                
📊 PARAMS: None
⚠️ WARNING: No user_id provided for sellout query
📊 Found 0 top products for context
📊 EXECUTING SELLOUT QUERY: 
                SELECT reseller, 
                       SUM(sales_eur) as total_sales,
                       COUNT(DISTINCT functional_name) as product_count
                FROM sellout_entries2 se 
                JOIN uploads u ON se.upload_id = u.id
                WHERE reseller IS NOT NULL
                GROUP BY reseller 
                ORDER BY total_sales DESC 
                LIMIT 5;
                
📊 PARAMS: None
⚠️ WARNING: No user_id provided for sellout query
📊 Found 0 top resellers for context
✅ Enhanced schema complete with statistics and business context
✅ Enhanced schema cache refreshed. Found 4 tables
✅ Pattern 2 (Context): Confidence 1.00
✅ Pattern 3 (Template): Confidence 0.40
🏆 SELECTED: context_aware (confidence: 1.00)
📊 Generated 3 patterns total
🔄 ATTEMPT 1: Trying context_aware (confidence: 1.00)
📊 EXECUTING: 
                SELECT year, month,
                       SUM(sales_eur) as monthly_sales,
       ...
📊 EXECUTING SELLOUT QUERY: 
                SELECT year, month,
                       SUM(sales_eur) as monthly_sales,
                       SUM(quantity) as monthly_units,
                       COUNT(DISTINCT functional_name) as products_sold,
                       COUNT(DISTINCT reseller) as active_resellers
                FROM sellout_entries2 se 
                JOIN uploads u ON se.upload_id = u.id 
                WHERE u.user_id = %s
                GROUP BY year, month 
                ORDER BY year DESC, month DESC
                LIMIT 24;
                
📊 PARAMS: ('26d3c1b7-d944-42a0-9336-e68b1b32ebbf',)
👤 Executing query for user: 26d3c1b7-d944-42a0-9336-e68b1b32ebbf
🔍 ANALYZING QUERY: 
                SELECT YEAR, MONTH,
                       SUM(SALES_EUR) AS MONTHLY_SALES,
       ...
📅 DETECTED: Time-based query
📅 Processing time-based query for meaningful breakdown
2025-07-17 22:37:42,655 - httpx - INFO - HTTP Request: GET https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/sellout_entries2?select=year%2C%20month%2C%20sales_eur%2C%20uploads%21inner%28user_id%29&uploads.user_id=eq.26d3c1b7-d944-42a0-9336-e68b1b32ebbf "HTTP/2 200 OK"
📅 Grouped by time: 14 periods found
✅ SUCCESS: Query returned 14 results
🎯 CHAT SERVICE: Got 14 results from database
🔍 CHAT SERVICE: First result keys: ['year', 'month', 'total_sales_eur', 'record_count']
🔍 CHAT SERVICE: First result sample: {'year': 2025, 'month': 6, 'total_sales_eur': 45451.619999999995}
🤖 CHAT SERVICE: Question type: show_table
🤖 CHAT SERVICE: Generating response for 14 results
📝 RESPONSE GEN: Question: 'what did I sell for 2024?'
📝 RESPONSE GEN: Results count: 14
📝 RESPONSE GEN: Question type: show_table
📝 RESPONSE GEN: Sample result structure: ['year', 'month', 'total_sales_eur', 'record_count']
📝 RESPONSE GEN: Using contextual_summary logic
🤖 CHAT SERVICE: Generated response: I found 14 records. Here are the results:...
2025-07-17 22:37:42,740 - httpx - INFO - HTTP Request: POST https://edckqdrbgtnnjfnshjfq.supabase.co/rest/v1/chat_sessions "HTTP/2 201 Created"
ERROR in _insert_chat_message: not enough values to unpack (expected 7, got 5)
ERROR in _execute_insert: not enough values to unpack (expected 7, got 5)
ERROR in execute: not enough values to unpack (expected 7, got 5)
Query: 
                INSERT INTO chat_messages 
                (session_id, user_id, message_type, content, sql_query, query_result, created_at)
                VALUES (%s, %s, %s, %s, NULL, NULL, %s)
                
Params: ('9583962a-57d3-4ec1-9635-536a8cd0ac3f', '26d3c1b7-d944-42a0-9336-e68b1b32ebbf', 'user', 'what did I sell for 2024?', datetime.datetime(2025, 7, 17, 22, 37, 42, 741762))
2025-07-17 22:37:42,741 - app.services.chat_service - ERROR - Error logging chat activity: Failed to execute query: not enough values to unpack (expected 7, got 5)
INFO:     127.0.0.1:38170 - "POST /api/chat/query HTTP/1.1" 200 OK