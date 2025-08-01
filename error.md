2025-08-01 09:45:21,352 - app.services.auth_service - INFO - Attempting token verification for token ending with: ...6u4Y
2025-08-01 09:45:21,868 - httpx - INFO - HTTP Request: GET https://nrkodllueunpbiotjbql.supabase.co/auth/v1/user "HTTP/2 403 Forbidden"
2025-08-01 09:45:21,869 - app.services.auth_service - ERROR - Token verification error: invalid JWT: unable to parse or verify signature, token has invalid claims: token is expired
2025-08-01 09:45:21,870 - app.services.auth_service - ERROR - Token type: <class 'str'>
2025-08-01 09:45:21,870 - app.services.auth_service - ERROR - Token length: 722
INFO:     127.0.0.1:50724 - "GET /api/auth/debug-token HTTP/1.1" 200 OK
2025-08-01 09:45:21,918 - app.services.auth_service - INFO - Attempting token verification for token ending with: ...6u4Y
2025-08-01 09:45:22,073 - httpx - INFO - HTTP Request: GET https://nrkodllueunpbiotjbql.supabase.co/auth/v1/user "HTTP/2 403 Forbidden"
2025-08-01 09:45:22,073 - app.services.auth_service - ERROR - Token verification error: invalid JWT: unable to parse or verify signature, token has invalid claims: token is expired
2025-08-01 09:45:22,073 - app.services.auth_service - ERROR - Token type: <class 'str'>
2025-08-01 09:45:22,073 - app.services.auth_service - ERROR - Token length: 722
INFO:     127.0.0.1:50724 - "GET /api/auth/debug-token HTTP/1.1" 200 OK
INFO:     127.0.0.1:47234 - "OPTIONS /api/auth/login HTTP/1.1" 200 OK
2025-08-01 09:45:31,974 - httpx - INFO - HTTP Request: POST https://nrkodllueunpbiotjbql.supabase.co/auth/v1/token?grant_type=password "HTTP/2 200 OK"
INFO:     127.0.0.1:47240 - "POST /api/auth/login HTTP/1.1" 200 OK
2025-08-01 09:45:32,048 - app.services.auth_service - INFO - Attempting token verification for token ending with: ...KEJw
2025-08-01 09:45:32,175 - httpx - INFO - HTTP Request: GET https://nrkodllueunpbiotjbql.supabase.co/auth/v1/user "HTTP/2 200 OK"
2025-08-01 09:45:32,176 - app.services.auth_service - INFO - Token verification successful for user: user@email.com
INFO:     127.0.0.1:47240 - "GET /api/auth/debug-token HTTP/1.1" 200 OK
INFO:     127.0.0.1:47240 - "OPTIONS /api/upload/ HTTP/1.1" 200 OK
2025-08-01 09:45:36,721 - app.api.auth - INFO - get_current_user called
2025-08-01 09:45:36,722 - app.api.auth - INFO - Authorization header: Present
2025-08-01 09:45:36,722 - app.api.auth - INFO - Extracted token length: 722
2025-08-01 09:45:36,722 - app.services.auth_service - INFO - Attempting token verification for token ending with: ...KEJw
2025-08-01 09:45:36,852 - httpx - INFO - HTTP Request: GET https://nrkodllueunpbiotjbql.supabase.co/auth/v1/user "HTTP/2 200 OK"
2025-08-01 09:45:36,853 - app.services.auth_service - INFO - Token verification successful for user: user@email.com
2025-08-01 09:45:36,853 - app.api.auth - INFO - Successfully authenticated user: user@email.com
2025-08-01 09:45:37,006 - app.api.upload - INFO - Current user object: {'id': 'fdd71f95-e8d4-417e-85aa-9b7b0c92436d', 'app_metadata': {'provider': 'email', 'providers': ['email']}, 'user_metadata': {'email_verified': True}, 'aud': 'authenticated', 'confirmation_sent_at': None, 'recovery_sent_at': None, 'email_change_sent_at': None, 'new_email': None, 'new_phone': None, 'invited_at': None, 'action_link': None, 'email': 'user@email.com', 'phone': '', 'created_at': datetime.datetime(2025, 7, 22, 20, 40, 20, 818984, tzinfo=TzInfo(UTC)), 'confirmed_at': datetime.datetime(2025, 7, 30, 10, 26, 20, 179047, tzinfo=TzInfo(UTC)), 'email_confirmed_at': datetime.datetime(2025, 7, 30, 10, 26, 20, 179047, tzinfo=TzInfo(UTC)), 'phone_confirmed_at': None, 'last_sign_in_at': datetime.datetime(2025, 8, 1, 7, 45, 31, 188451, tzinfo=TzInfo(UTC)), 'role': 'authenticated', 'updated_at': datetime.datetime(2025, 8, 1, 7, 45, 31, 244344, tzinfo=TzInfo(UTC)), 'identities': [{'id': 'fdd71f95-e8d4-417e-85aa-9b7b0c92436d', 'identity_id': '1152cd60-4a0e-46c9-8fda-8810acb0a814', 'user_id': 'fdd71f95-e8d4-417e-85aa-9b7b0c92436d', 'identity_data': {'email': 'user@email.com', 'email_verified': False, 'phone_verified': False, 'sub': 'fdd71f95-e8d4-417e-85aa-9b7b0c92436d'}, 'provider': 'email', 'created_at': datetime.datetime(2025, 7, 22, 20, 40, 20, 836907, tzinfo=TzInfo(UTC)), 'last_sign_in_at': datetime.datetime(2025, 7, 22, 20, 40, 20, 836838, tzinfo=TzInfo(UTC)), 'updated_at': datetime.datetime(2025, 7, 22, 20, 40, 20, 836907, tzinfo=TzInfo(UTC))}], 'is_anonymous': False, 'factors': None}
2025-08-01 09:45:37,006 - app.api.upload - INFO - User ID being used: fdd71f95-e8d4-417e-85aa-9b7b0c92436d
2025-08-01 09:45:37,006 - app.services.db_service - INFO - Attempting to create upload record with service role (bypassing RLS)
2025-08-01 09:45:37,077 - watchfiles.main - INFO - 1 change detected
2025-08-01 09:45:37,520 - httpx - INFO - HTTP Request: POST https://nrkodllueunpbiotjbql.supabase.co/rest/v1/uploads "HTTP/2 409 Conflict"
2025-08-01 09:45:37,521 - app.services.db_service - ERROR - Database error creating upload record: {'code': '23503', 'details': 'Key (user_id)=(fdd71f95-e8d4-417e-85aa-9b7b0c92436d) is not present in table "users".', 'hint': None, 'message': 'insert or update on table "uploads" violates foreign key constraint "uploads_user_id_fkey"'}
2025-08-01 09:45:37,521 - app.services.db_service - ERROR - Upload data: {'id': 'c96d7056-af7f-43ba-a655-2145a334b267', 'user_id': 'fdd71f95-e8d4-417e-85aa-9b7b0c92436d', 'filename': 'Demo_ReportPeriod02-2025.xlsx', 'file_size': 17728, 'status': 'pending'}
2025-08-01 09:45:37,521 - app.services.db_service - ERROR - Supabase error details: Key (user_id)=(fdd71f95-e8d4-417e-85aa-9b7b0c92436d) is not present in table "users".
2025-08-01 09:45:37,521 - app.services.db_service - ERROR - Supabase error message: insert or update on table "uploads" violates foreign key constraint "uploads_user_id_fkey"
INFO:     127.0.0.1:47240 - "POST /api/upload/ HTTP/1.1" 400 Bad Request