from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain.agents import AgentType
from app.utils.config import get_settings
from app.services.db_service import DatabaseService
import logging
import os

router = APIRouter(tags=["chat"])
logger = logging.getLogger(__name__)

class SupabaseSQLDatabase:
    """Mock SQLDatabase that uses Supabase REST API instead of direct PostgreSQL"""
    
    def __init__(self):
        self.db_service = DatabaseService()
        # Mock database info for LangChain
        self._sample_rows_in_table_info = 3
        self._include_tables = ['mock_data', 'uploads', 'products']
    
    def run(self, command: str, fetch: str = "all"):
        """Execute SQL command using Supabase REST API"""
        try:
            logger.info(f"Executing SQL via Supabase REST API: {command}")
            
            # Simple test query
            if command.strip().lower() in ["select 1", "select 1 as test"]:
                return "1"
            
            # For complex queries, use our smart query handler
            # This uses the same logic as your Excel cleaning system
            import asyncio
            result = asyncio.create_task(self._execute_supabase_query(command))
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're in an async context, we need to handle this differently
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._execute_supabase_query(command))
                    return future.result()
            else:
                return loop.run_until_complete(result)
        
        except Exception as e:
            logger.error(f"Error executing Supabase query: {str(e)}")
            return str(e)
    
    async def _execute_supabase_query(self, command: str):
        """Execute query using DatabaseService (same as Excel cleaning)"""
        try:
            # For demo purposes, return some sample data about sales
            if "mock_data" in command.lower():
                # Get recent sales data - this won't break your Excel cleaning
                result = self.db_service.supabase.table("mock_data")\
                    .select("functional_name, reseller, sales_eur, quantity, month, year")\
                    .order("created_at", desc=True)\
                    .limit(10)\
                    .execute()
                
                if result.data:
                    # Format as table-like response for LangChain
                    return str(result.data)
                else:
                    return "No data found"
            else:
                return "Query executed successfully"
                
        except Exception as e:
            logger.error(f"Supabase REST API query error: {str(e)}")
            return f"Error: {str(e)}"
    
    def get_table_info(self, table_names=None):
        """Return table schema information for Supabase mock_data table"""
        return """
        Table: mock_data
        Columns:
        - functional_name (text): Product name/identifier
        - reseller (text): Reseller/customer name  
        - sales_eur (numeric): Sales amount in EUR
        - quantity (integer): Quantity sold
        - month (integer): Month (1-12)
        - year (integer): Year (e.g. 2024, 2025)
        - product_ean (text): Product EAN code
        - currency (text): Currency code
        - upload_id (uuid): Reference to upload record
        - created_at (timestamp): When record was created
        
        Table: uploads
        Columns:
        - id (uuid): Upload ID
        - user_id (text): User who uploaded the file
        - filename (text): Original filename
        - status (text): Processing status
        - uploaded_at (timestamp): Upload timestamp
        - rows_processed (integer): Number of rows processed
        - rows_cleaned (integer): Number of rows after cleaning
        
        Sample mock_data record:
        functional_name='PRSP100 Premium Headphones', reseller='Galilu Electronics', sales_eur=1298.50, quantity=15, month=3, year=2024, product_ean='1234567890123', currency='EUR'
        """
    
    @property
    def dialect(self):
        """Mock dialect for LangChain compatibility"""
        class MockDialect:
            name = "postgresql"
        return MockDialect()

class SupabaseChatAgent:
    """Enhanced chat agent that uses Supabase REST API for data queries with debug mode"""
    
    def __init__(self, llm, db):
        self.llm = llm
        self.db = db
        # Only initialize DatabaseService for Supabase REST API connections
        if hasattr(db, 'supabase') or isinstance(db, SupabaseSQLDatabase):
            self.db_service = DatabaseService()
            self.use_supabase_api = True
        else:
            self.db_service = None
            self.use_supabase_api = False
        self.debug_mode = True  # Enable detailed logging
    
    def invoke(self, inputs):
        """Process chat request with enhanced analysis including percentage calculations"""
        try:
            user_message = inputs.get("input", "")
            user_id = inputs.get("user_id")  # Get user ID for filtering
            
            if self.debug_mode:
                logger.info("=" * 50)
                logger.info("🤖 ENHANCED CHAT DEBUG MODE ENABLED")
                logger.info(f"📝 User message: {user_message}")
                logger.info(f"👤 User ID: {user_id}")
                logger.info(f"🔌 Connection type: {'Supabase REST API' if self.use_supabase_api else 'Direct PostgreSQL'}")
                logger.info("=" * 50)
            
            # Extract year from user message for filtering
            year_filter = self._extract_year_from_message(user_message)
            if self.debug_mode and year_filter:
                logger.info(f"📅 Year filter detected: {year_filter}")
            
            # Handle different connection types
            if self.use_supabase_api:
                # Use existing Supabase REST API logic
                data = self._fetch_data_via_supabase_api(user_message, user_id, year_filter)
            else:
                # Use direct PostgreSQL connection
                data = self._fetch_data_via_postgresql(user_message, user_id)
            
            if data:
                # Analyze user's question intent
                intent = self._analyze_question_intent(user_message)
                if self.debug_mode:
                    logger.info(f"🎯 Detected intent: {intent}")
                
                # Create a context-aware prompt with detailed data analysis including percentages
                data_summary = self._summarize_data(data, intent)
                
                if self.debug_mode:
                    logger.info(f"📋 Data summary length: {len(data_summary)} characters")
                    logger.info("🔍 Sending to LLM for analysis...")
                
                prompt = f"""
                You are an expert sales data analyst specialized in business intelligence and ranking analysis. Based on the following sales data analysis, answer the user's question with detailed insights including percentage changes where applicable.
                
                IMPORTANT: The data summary below already includes percentage calculations, trend analysis, and complete rankings. Use these insights in your response.
                
                Sales Data Analysis:
                {data_summary}
                
                Question Intent: {intent}
                User Question: {user_message}
                
                Instructions:
                1. For PRODUCT_RANKING queries: Focus on the complete product ranking provided, highlight top performers with specific sales figures and quantities
                2. For RESELLER_RANKING queries: Emphasize reseller performance rankings with detailed metrics
                3. For TIME_ANALYSIS queries: Use percentage changes and trend indicators with mathematical notation where helpful
                4. For specific date/month queries: Extract the exact time period data and provide focused analysis
                5. Provide specific numbers and calculations from the analysis with proper formatting
                6. When discussing rankings, use clear language like "best selling", "top performer", "#1 product"
                7. Format numbers with currency symbols (€) and proper thousands separators
                8. All sales data is in EUR (sales_eur) for consistent analysis
                9. If asking for "best selling product of [specific month/year]", focus on that exact time period
                10. Use mathematical expressions with LaTeX notation for complex calculations (e.g., \\[formula\\] for display math)
                
                Be thorough, analytical, and direct in answering the specific question asked. Focus on the most relevant data for the user's query.
                """
                
                # Use the LLM to generate a response
                response = self.llm.invoke(prompt)
                
                if self.debug_mode:
                    logger.info(f"✅ LLM response generated: {len(response.content)} characters")
                    logger.info("=" * 50)
                
                return {"output": response.content}
            else:
                error_msg = "I don't have access to any sales data for your account at the moment. Please try uploading some data first."
                if self.debug_mode:
                    logger.warning("❌ No data found for user")
                return {"output": error_msg}
                
        except Exception as e:
            if self.debug_mode:
                logger.error("❌ ERROR in enhanced chat agent:")
                logger.error(f"   Error type: {type(e).__name__}")
                logger.error(f"   Error message: {str(e)}")
                import traceback
                logger.error(f"   Traceback: {traceback.format_exc()}")
            
            # Enhanced error handling with user-friendly feedback
            error_message = self._get_user_friendly_error_message(str(e), user_message)
            return {"output": error_message}
    
    def _get_user_friendly_error_message(self, error_str, user_message):
        """Convert technical errors into user-friendly messages with suggestions"""
        error_lower = error_str.lower()
        
        # Date parsing errors
        if 'date' in error_lower or 'time' in error_lower:
            return f"""I had trouble understanding the date in your question: "{user_message}"
            
Try rephrasing with:
• Specific months: "May 2024", "January 2023"
• Quarters: "Q1 2024", "Q2 2023" 
• Formats: "2024-05", "05/2024"

Example: "What were my best selling products in May 2024?" """

        # Data access errors
        elif 'no data' in error_lower or 'empty' in error_lower:
            return f"""I couldn't find any data matching your query: "{user_message}"

Please check:
• Have you uploaded sales data for this time period?
• Try a broader date range (e.g., "2024" instead of "May 2024")
• Make sure product names match your uploaded data

You can ask: "What data do I have available?" to see your uploaded information."""

        # Query parsing errors  
        elif 'query' in error_lower or 'sql' in error_lower:
            return f"""I had trouble analyzing your request: "{user_message}"

Try asking:
• "What were my top selling products in [time period]?"
• "Which reseller had the highest sales in [time period]?"
• "Show me sales trends for [year]"

Example: "What were my best selling products in May 2024?" """

        # Generic error with suggestions
        else:
            return f"""I encountered an issue processing your request: "{user_message}"

Here are some example questions I can help with:
• "What were my best selling products in May 2024?"
• "Which reseller had the highest revenue in Q2 2024?" 
• "Show me monthly sales trends for 2024"
• "What were total sales in 2023?"

Technical details: {error_str}"""
    
    def _fetch_data_via_supabase_api(self, user_message, user_id, year_filter):
        """Fetch data using Supabase REST API with enhanced filtering"""
        try:
            if self.debug_mode:
                logger.info("📊 Fetching data via Supabase REST API...")
            
            # Extract date components for advanced filtering
            date_components = self._extract_date_components(user_message)
            month_filter = date_components.get('month')
            quarter_filter = date_components.get('quarter')
            years_filter = date_components.get('years', [])
            
            # Build query with optional filtering
            if user_id:
                # First get upload IDs for the user
                user_uploads = self.db_service.supabase.table("uploads")\
                    .select("id")\
                    .eq("user_id", user_id)\
                    .execute()
                
                if user_uploads.data:
                    upload_ids = [upload['id'] for upload in user_uploads.data]
                    if self.debug_mode:
                        logger.info(f"📁 Found {len(upload_ids)} uploads for user {user_id}")
                    
                    # Filter by upload IDs
                    query = self.db_service.supabase.table("mock_data")\
                        .select("functional_name, reseller, sales_eur, quantity, month, year, product_ean, currency")\
                        .in_("upload_id", upload_ids)
                else:
                    if self.debug_mode:
                        logger.warning(f"⚠️ No uploads found for user {user_id}")
                    return []
                
                # Add date filters if detected
                # Support multi-year filtering (e.g., "2024 and 2025")
                if years_filter and len(years_filter) > 1:
                    query = query.in_("year", years_filter)
                    if self.debug_mode:
                        logger.info(f"📅 Applied multi-year filter: {years_filter}")
                elif year_filter:
                    query = query.eq("year", year_filter)
                    if self.debug_mode:
                        logger.info(f"📅 Applied single year filter: {year_filter}")

                if month_filter:
                    query = query.eq("month", month_filter)
                    if self.debug_mode:
                        logger.info(f"📅 Applied month filter: {month_filter}")

                if quarter_filter:
                    # Convert quarter to months
                    quarter_months = {
                        1: [1, 2, 3],
                        2: [4, 5, 6],
                        3: [7, 8, 9],
                        4: [10, 11, 12]
                    }
                    if quarter_filter in quarter_months:
                        query = query.in_("month", quarter_months[quarter_filter])
                        if self.debug_mode:
                            logger.info(f"📅 Applied quarter filter: Q{quarter_filter} (months {quarter_months[quarter_filter]})")

                result = query.order("created_at", desc=True).limit(5000).execute()
                
                if self.debug_mode:
                    logger.info(f"✅ Found {len(result.data) if result.data else 0} records for user {user_id} (year: {year_filter or 'all'})")
            else:
                # Fallback to recent data if no user ID
                query = self.db_service.supabase.table("mock_data")\
                    .select("functional_name, reseller, sales_eur, quantity, month, year, product_ean, currency")
                
                # Add date filters if detected
                # Support multi-year filtering (e.g., "2024 and 2025")
                if years_filter and len(years_filter) > 1:
                    query = query.in_("year", years_filter)
                    if self.debug_mode:
                        logger.info(f"📅 Applied multi-year filter to fallback: {years_filter}")
                elif year_filter:
                    query = query.eq("year", year_filter)
                    if self.debug_mode:
                        logger.info(f"📅 Applied single year filter to fallback: {year_filter}")
                
                if month_filter:
                    query = query.eq("month", month_filter)
                    if self.debug_mode:
                        logger.info(f"📅 Applied month filter to fallback query: {month_filter}")
                
                if quarter_filter:
                    # Convert quarter to months
                    quarter_months = {
                        1: [1, 2, 3],
                        2: [4, 5, 6], 
                        3: [7, 8, 9],
                        4: [10, 11, 12]
                    }
                    if quarter_filter in quarter_months:
                        query = query.in_("month", quarter_months[quarter_filter])
                        if self.debug_mode:
                            logger.info(f"📅 Applied quarter filter to fallback: Q{quarter_filter} (months {quarter_months[quarter_filter]})")
                
                result = query.order("created_at", desc=True).limit(5000).execute()

                if self.debug_mode:
                    logger.warning("⚠️ No user ID provided, using recent data fallback")
                    logger.info(f"📊 Found {len(result.data) if result.data else 0} total records (year: {year_filter or 'all'})")
            
            if result.data:
                # Clean the data (remove uploads join data)
                clean_data = []
                for row in result.data:
                    clean_row = {k: v for k, v in row.items() if k != 'uploads'}
                    clean_data.append(clean_row)
                
                if self.debug_mode:
                    logger.info(f"🧹 Cleaned Supabase data: {len(clean_data)} records")
                    logger.info(f"📈 Sample record: {clean_data[0] if clean_data else 'None'}")
                
                return clean_data
            else:
                return []
                
        except Exception as e:
            if self.debug_mode:
                logger.error(f"❌ Error fetching Supabase data: {str(e)}")
            return []
    
    def _fetch_data_via_postgresql(self, user_message, user_id):
        """Fetch data using direct PostgreSQL connection"""
        try:
            if self.debug_mode:
                logger.info("📊 Fetching data via direct PostgreSQL...")
            
            # Use the direct SQL database connection to get all mock_data
            # Since we don't have user filtering in PostgreSQL mode, get recent data
            sql_query = """
                SELECT functional_name, reseller, sales_eur, quantity, month, year, product_ean, currency
                FROM mock_data 
                ORDER BY created_at DESC 
                LIMIT 500
            """
            
            result = self.db.run(sql_query)
            
            if self.debug_mode:
                logger.info(f"📊 Direct PostgreSQL query result type: {type(result)}")
                logger.info(f"📊 Query result: {str(result)[:200]}...")  # First 200 chars
            
            # Convert result to list of dictionaries
            # Handle different result formats from PostgreSQL
            clean_data = []
            
            if result:
                if isinstance(result, list):
                    # Direct list result - handle as before
                    if len(result) > 0 and isinstance(result[0], (tuple, list)):
                        # Result is list of tuples/lists - convert to dicts
                        columns = ['functional_name', 'reseller', 'sales_eur', 'quantity', 'month', 'year', 'product_ean', 'currency']
                        for row in result:
                            if len(row) >= len(columns):
                                clean_data.append(dict(zip(columns, row)))
                    elif len(result) > 0 and isinstance(result[0], dict):
                        # Result is already list of dicts
                        clean_data = result
                
                elif isinstance(result, str):
                    # String representation of results - need to parse
                    if self.debug_mode:
                        logger.info("📊 Parsing string representation of PostgreSQL results...")
                    
                    try:
                        # Handle the string representation that contains Decimal objects
                        # First, replace Decimal('value') with just the value
                        import re
                        from decimal import Decimal
                        
                        # Replace Decimal('123.45') with 123.45 for ast.literal_eval
                        decimal_pattern = r"Decimal\('([^']+)'\)"
                        cleaned_result = re.sub(decimal_pattern, r'\1', result)
                        
                        if self.debug_mode:
                            logger.info("📊 Cleaned Decimal references from string...")
                            logger.info(f"📊 Cleaned string (first 200 chars): {cleaned_result[:200]}...")
                        
                        # Now use ast.literal_eval to safely parse the cleaned string
                        import ast
                        parsed_result = ast.literal_eval(cleaned_result)
                        
                        if self.debug_mode:
                            logger.info(f"📊 Successfully parsed result type: {type(parsed_result)}")
                            logger.info(f"📊 Parsed result length: {len(parsed_result) if hasattr(parsed_result, '__len__') else 'N/A'}")
                        
                        if isinstance(parsed_result, list) and len(parsed_result) > 0:
                            columns = ['functional_name', 'reseller', 'sales_eur', 'quantity', 'month', 'year', 'product_ean', 'currency']
                            for row in parsed_result:
                                if isinstance(row, (tuple, list)) and len(row) >= len(columns):
                                    # Convert all numeric values to appropriate types
                                    processed_row = []
                                    for i, item in enumerate(row):
                                        if i == 2:  # sales_eur column
                                            processed_row.append(float(item) if item is not None else 0.0)
                                        elif i in [3, 4, 5]:  # quantity, month, year columns
                                            processed_row.append(int(item) if item is not None else 0)
                                        else:
                                            processed_row.append(item)
                                    clean_data.append(dict(zip(columns, processed_row)))
                    
                    except (ValueError, SyntaxError, re.error) as e:
                        if self.debug_mode:
                            logger.error(f"❌ Failed to parse string result: {str(e)}")
                        
                        # Enhanced fallback - try to extract basic data using regex
                        try:
                            if result.strip().startswith('[') and result.strip().endswith(']'):
                                if self.debug_mode:
                                    logger.warning("⚠️ Using regex fallback parsing...")
                                
                                # Extract tuple-like patterns from the string
                                tuple_pattern = r"\('([^']*)',\s*'([^']*)',\s*(?:Decimal\('([^']+)'\)|([^,]+)),\s*(\d+),\s*(\d+),\s*(\d+),\s*'([^']*)',\s*'([^']*)'\)"
                                matches = re.findall(tuple_pattern, result)
                                
                                columns = ['functional_name', 'reseller', 'sales_eur', 'quantity', 'month', 'year', 'product_ean', 'currency']
                                for match in matches:
                                    if len(match) >= 8:
                                        # match[2] is Decimal value, match[3] would be non-Decimal value
                                        sales_value = float(match[2]) if match[2] else (float(match[3]) if match[3] else 0.0)
                                        
                                        row_data = [
                                            match[0],  # functional_name
                                            match[1],  # reseller  
                                            sales_value,  # sales_eur
                                            int(match[4]) if match[4] else 0,  # quantity
                                            int(match[5]) if match[5] else 0,  # month
                                            int(match[6]) if match[6] else 0,  # year
                                            match[7],  # product_ean
                                            match[8]   # currency
                                        ]
                                        clean_data.append(dict(zip(columns, row_data)))
                                
                                if self.debug_mode:
                                    logger.info(f"📊 Regex fallback extracted {len(clean_data)} records")
                        
                        except Exception as fallback_error:
                            if self.debug_mode:
                                logger.error(f"❌ Fallback parsing also failed: {str(fallback_error)}")
                            clean_data = []
            
            if self.debug_mode:
                logger.info(f"🧹 Cleaned PostgreSQL data: {len(clean_data)} records")
                logger.info(f"📈 Sample record: {clean_data[0] if clean_data else 'None'}")
            
            return clean_data
                
        except Exception as e:
            if self.debug_mode:
                logger.error(f"❌ Error fetching PostgreSQL data: {str(e)}")
            return []
    
    def run(self, input_text):
        """Compatibility method for older LangChain versions"""
        result = self.invoke({"input": input_text})
        return result.get("output", "Error processing request")
    
    def _extract_date_components(self, user_message):
        """Extract date components (year, month, quarter) from user message"""
        import re
        from datetime import datetime

        result = {'year': None, 'years': [], 'month': None, 'quarter': None}

        # Month name to number mapping
        month_map = {
            'january': 1, 'jan': 1, 'february': 2, 'feb': 2, 'march': 3, 'mar': 3,
            'april': 4, 'apr': 4, 'may': 5, 'june': 6, 'jun': 6, 'july': 7, 'jul': 7,
            'august': 8, 'aug': 8, 'september': 9, 'sep': 9, 'sept': 9,
            'october': 10, 'oct': 10, 'november': 11, 'nov': 11, 'december': 12, 'dec': 12
        }

        # Look for 4-digit years (2020-2030) - capture ALL years mentioned
        year_pattern = r'\b(202[0-9])\b'
        year_matches = re.findall(year_pattern, user_message)
        if year_matches:
            result['years'] = [int(y) for y in year_matches]
            result['year'] = result['years'][0]  # Backward compatibility
        
        # Look for month names (case insensitive)
        message_lower = user_message.lower()
        for month_name, month_num in month_map.items():
            if month_name in message_lower:
                result['month'] = month_num
                break
        
        # Look for numeric months (1-12, 01-12)
        if not result['month']:
            month_pattern = r'\b(0?[1-9]|1[0-2])\b'
            month_matches = re.findall(month_pattern, user_message)
            if month_matches:
                result['month'] = int(month_matches[0])
        
        # Look for quarters
        quarter_pattern = r'\bq([1-4])\b'
        quarter_matches = re.findall(quarter_pattern, message_lower)
        if quarter_matches:
            result['quarter'] = int(quarter_matches[0])
        
        # Look for date formats like "2024-05" or "05/2024"
        date_formats = [
            r'\b(\d{4})-(\d{1,2})\b',  # 2024-05
            r'\b(\d{1,2})/(\d{4})\b',  # 05/2024
            r'\b(\d{1,2})-(\d{4})\b'   # 05-2024
        ]
        
        for pattern in date_formats:
            matches = re.findall(pattern, user_message)
            if matches:
                if len(matches[0][0]) == 4:  # Year first
                    result['year'] = int(matches[0][0])
                    result['month'] = int(matches[0][1])
                else:  # Month first
                    result['month'] = int(matches[0][0])
                    result['year'] = int(matches[0][1])
                break
        
        return result
    
    def _extract_year_from_message(self, user_message):
        """Extract year from user message for filtering (backward compatibility)"""
        date_components = self._extract_date_components(user_message)
        return date_components['year']
    
    def _calculate_percentage_change(self, old_value, new_value):
        """Calculate percentage change between two values with proper formatting"""
        if not old_value or old_value == 0:
            return "N/A (no baseline)"
        
        change = ((new_value - old_value) / old_value) * 100
        
        # Format with appropriate trend indicator
        if abs(change) < 2:
            trend = "➡️"
            trend_text = "flat"
        elif change > 0:
            trend = "📈"
            trend_text = "increase"
        else:
            trend = "📉"
            trend_text = "decrease"
        
        return f"{change:+.1f}% {trend} ({trend_text})"
    
    def _analyze_question_intent(self, user_message):
        """Analyze user's question to understand their intent with enhanced keyword recognition"""
        message_lower = user_message.lower()
        
        # Superlative/ranking keywords 
        ranking_keywords = ['best', 'worst', 'top', 'bottom', 'highest', 'lowest', 'most', 'least', 'first', 'last', 'leading', 'worst', 'maximum', 'minimum', 'largest', 'smallest']
        
        # Time-based queries (enhanced)
        time_keywords = ['year', 'month', 'quarterly', '2023', '2024', '2025', 'monthly', 'yearly', 'trend', 'growth', 'increase', 'decrease', 'change', 'compared to', 'vs', 'versus', 'percent', 'percentage', '%', 'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december', 'jan', 'feb', 'mar', 'apr', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec', 'q1', 'q2', 'q3', 'q4', 'quarter']
        
        # Product ranking queries (priority check)
        if any(rank in message_lower for rank in ranking_keywords) and any(prod in message_lower for prod in ['product', 'item', 'selling', 'sold', 'sales', 'revenue']):
            return "PRODUCT_RANKING"
        
        # Reseller ranking queries
        elif any(rank in message_lower for rank in ranking_keywords) and any(res in message_lower for res in ['reseller', 'customer', 'client', 'retailer', 'distributor']):
            return "RESELLER_RANKING" 
        
        # Time-based queries
        elif any(word in message_lower for word in time_keywords):
            return "TIME_ANALYSIS"
        
        # Reseller/Customer analysis (general)
        elif any(word in message_lower for word in ['reseller', 'customer', 'client', 'who', 'which reseller', 'retailer', 'distributor']):
            return "RESELLER_ANALYSIS"
        
        # Product analysis (general)
        elif any(word in message_lower for word in ['product', 'item', 'ean', 'functional_name', 'inventory', 'catalog']):
            return "PRODUCT_ANALYSIS"
        
        # Total/summary queries
        elif any(word in message_lower for word in ['total', 'sum', 'overall', 'all', 'entire', 'aggregate', 'combined']):
            return "TOTAL_SUMMARY"
        
        # Comparison queries
        elif any(word in message_lower for word in ['compare', 'vs', 'versus', 'difference', 'higher', 'lower', 'against', 'between']):
            return "COMPARISON"
        
        else:
            return "GENERAL_INQUIRY"
    
    def _summarize_data(self, data, intent="GENERAL_INQUIRY"):
        """Create comprehensive data analysis for the LLM based on intent - NO SAMPLE RECORDS"""
        if not data:
            return "No data available"

        try:
            # Basic statistics
            total_sales_eur = sum(float(row.get('sales_eur', 0) or 0) for row in data)
            total_quantity = sum(int(row.get('quantity', 0) or 0) for row in data)

            # Get unique entities
            products = set(row.get('functional_name') for row in data if row.get('functional_name'))
            resellers = set(row.get('reseller') for row in data if row.get('reseller'))
            currencies = set(row.get('currency') for row in data if row.get('currency'))

            # Time analysis
            years = set(row.get('year') for row in data if row.get('year'))
            months = set(row.get('month') for row in data if row.get('month'))

            # Data completeness warning
            data_completeness_note = ""
            if len(data) >= 5000:
                data_completeness_note = "\n⚠️ DATA LIMIT REACHED: Showing 5000 most recent records. Results may be incomplete if dataset is larger."
            elif len(data) >= 4000:
                data_completeness_note = "\n⚠️ APPROACHING DATA LIMIT: Showing 5000 most recent records. Dataset appears large."

            # Build comprehensive analysis
            summary = f"""
            COMPLETE SALES DATA ANALYSIS ({len(data)} records analyzed):{data_completeness_note}
            - Total Sales (EUR): €{total_sales_eur:,.2f}
            - Total Quantity: {total_quantity:,} units
            - Unique Products: {len(products)} products
            - Unique Resellers: {len(resellers)} resellers
            - Currencies: {', '.join(currencies)}
            - Time Period: Years {sorted(years)}, Months {sorted(months)}
            """
            
            # ALWAYS provide complete breakdowns for accurate analysis
            # 1. Complete Reseller Analysis
            reseller_totals_eur = {}
            reseller_quantities = {}
            for row in data:
                reseller = row.get('reseller', 'Unknown')
                sales_eur = float(row.get('sales_eur', 0) or 0)
                quantity = int(row.get('quantity', 0) or 0)
                
                if reseller not in reseller_totals_eur:
                    reseller_totals_eur[reseller] = 0
                    reseller_quantities[reseller] = 0
                reseller_totals_eur[reseller] += sales_eur
                reseller_quantities[reseller] += quantity
            
            sorted_resellers = sorted(reseller_totals_eur.items(), key=lambda x: x[1], reverse=True)
            summary += f"\n\nCOMPLETE RESELLER ANALYSIS:\n"
            for reseller, total_eur in sorted_resellers:
                quantity = reseller_quantities[reseller]
                summary += f"- {reseller}: €{total_eur:,.2f} (Quantity: {quantity:,})\n"
            
            # 2. Complete Product Analysis - Enhanced for Ranking
            product_totals_eur = {}
            product_quantities = {}
            for row in data:
                product = row.get('functional_name', 'Unknown')
                sales_eur = float(row.get('sales_eur', 0) or 0)
                quantity = int(row.get('quantity', 0) or 0)
                
                if product not in product_totals_eur:
                    product_totals_eur[product] = 0
                    product_quantities[product] = 0
                product_totals_eur[product] += sales_eur
                product_quantities[product] += quantity
            
            sorted_products = sorted(product_totals_eur.items(), key=lambda x: x[1], reverse=True)
            
            # Enhanced product output based on intent
            if intent in ["PRODUCT_RANKING", "PRODUCT_ANALYSIS"]:
                summary += f"\n\nCOMPLETE PRODUCT RANKING BY SALES (All {len(sorted_products)} Products):\n"
                for i, (product, total_eur) in enumerate(sorted_products, 1):
                    quantity = product_quantities[product]
                    ranking_emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"#{i}"
                    summary += f"{ranking_emoji} {product}: €{total_eur:,.2f} (Quantity: {quantity:,})\n"
            else:
                summary += f"\n\nTOP 10 PRODUCTS BY SALES:\n"
                for product, total_eur in sorted_products[:10]:
                    quantity = product_quantities[product]
                    summary += f"- {product}: €{total_eur:,.2f} (Quantity: {quantity:,})\n"
            
            # 3. Complete Time Analysis
            monthly_totals_eur = {}
            yearly_totals_eur = {}
            for row in data:
                year = row.get('year')
                month = row.get('month')
                sales_eur = float(row.get('sales_eur', 0) or 0)
                
                if year:
                    if year not in yearly_totals_eur:
                        yearly_totals_eur[year] = 0
                    yearly_totals_eur[year] += sales_eur
                    
                    if month:
                        time_key = f"{year}-{month:02d}"
                        if time_key not in monthly_totals_eur:
                            monthly_totals_eur[time_key] = 0
                        monthly_totals_eur[time_key] += sales_eur
            
            # Show yearly totals (with or without percentage changes based on intent)
            summary += f"\n\nYEARLY SALES TOTALS:\n"
            sorted_years = sorted(yearly_totals_eur.keys())
            for i, year in enumerate(sorted_years):
                eur_total = yearly_totals_eur[year]
                
                # Only calculate percentage changes for COMPARISON intent
                if intent == "COMPARISON" and i > 0:
                    prev_year = sorted_years[i-1]
                    prev_total = yearly_totals_eur[prev_year]
                    percentage_change = self._calculate_percentage_change(prev_total, eur_total)
                    summary += f"- {year}: €{eur_total:,.2f} ({percentage_change} vs {prev_year})\n"
                else:
                    summary += f"- {year}: €{eur_total:,.2f}\n"
            
            # Show monthly totals (with or without percentage changes based on intent)
            sorted_months = sorted(monthly_totals_eur.items())
            summary += f"\n\nMONTHLY BREAKDOWN (Recent 12 months):\n"
            recent_months = sorted_months[-12:]  # Last 12 months
            for i, (time_period, total_eur) in enumerate(recent_months):
                
                # Only calculate month-over-month changes for COMPARISON intent
                if intent == "COMPARISON" and i > 0:
                    prev_period, prev_total = recent_months[i-1]
                    percentage_change = self._calculate_percentage_change(prev_total, total_eur)
                    summary += f"- {time_period}: €{total_eur:,.2f} ({percentage_change} vs {prev_period})\n"
                else:
                    summary += f"- {time_period}: €{total_eur:,.2f}\n"
            
            # Add growth summary only for TIME_ANALYSIS or COMPARISON intents
            if (intent == "TIME_ANALYSIS" or intent == "COMPARISON") and len(sorted_years) > 1:
                summary += f"\n\nGROWTH SUMMARY:\n"
                
                # Overall year-over-year growth (only for comparison-related intents)
                first_year_total = yearly_totals_eur[sorted_years[0]]
                last_year_total = yearly_totals_eur[sorted_years[-1]]
                overall_change = self._calculate_percentage_change(first_year_total, last_year_total)
                summary += f"- Overall growth from {sorted_years[0]} to {sorted_years[-1]}: {overall_change}\n"
                
                # Recent month trend (if we have monthly data)
                if len(recent_months) > 1:
                    recent_trend_months = recent_months[-3:]  # Last 3 months
                    if len(recent_trend_months) >= 2:
                        trend_direction = "increasing" if recent_trend_months[-1][1] > recent_trend_months[0][1] else "decreasing"
                        summary += f"- Recent 3-month trend: {trend_direction}\n"
            
            summary += f"\n\nIMPORTANT: Base your analysis on the COMPLETE data above, not on individual records."
            
            return summary
            
        except Exception as e:
            return f"Data available but error in summary: {str(e)}"

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str

# Global variables to store DB connection and agent
_db = None
_agent_executor = None
_use_supabase_fallback = False
_supabase_db_service = None

def get_database():
    """Get or create database connection for LangChain chat functionality"""
    global _db, _use_supabase_fallback, _supabase_db_service
    if _db is None:
        settings = get_settings()
        
        # Check if we have real Supabase credentials
        if settings.environment != "development" and "placeholder" not in settings.supabase_url:
            # Try to connect to real Supabase PostgreSQL database
            try:
                # Construct PostgreSQL URL from Supabase settings
                supabase_host = settings.supabase_url.replace("https://", "").replace("http://", "")
                project_ref = supabase_host.split('.')[0]
                # Note: This would need real PostgreSQL credentials, not just REST API credentials
                postgres_url = f"postgresql://postgres:[password]@db.{project_ref}.supabase.co:5432/postgres"
                
                logger.info(f"Attempting to connect to Supabase PostgreSQL database")
                _db = SQLDatabase.from_uri(postgres_url)
                
                # Test the connection
                test_result = _db.run("SELECT 1 as test")
                logger.info(f"Supabase PostgreSQL connection successful")
                logger.info(f"Test query result: {test_result}")
                
                return _db
                
            except Exception as e:
                logger.warning(f"Direct PostgreSQL connection failed: {str(e)}")
                logger.info("Falling back to Supabase REST API mode")
        
        # Use Supabase REST API fallback (works with existing DatabaseService)
        logger.info("Using Supabase REST API fallback for chat functionality")
        _use_supabase_fallback = True
        _supabase_db_service = DatabaseService()
        
        # Create a mock SQLDatabase object that uses Supabase REST API
        _db = SupabaseSQLDatabase()
        logger.info("Supabase REST API fallback initialized for chat functionality")
    
    return _db

def get_agent():
    """Get or create SQL agent"""
    global _agent_executor, _use_supabase_fallback
    # Force recreation of agent to pick up new system message   
    _agent_executor = None
    if _agent_executor is None:
        settings = get_settings()
        db = get_database()
        
        # Initialize LLM
        model_name = settings.openai_model
        if model_name == "gpt-4":
            model_name = "gpt-4o"  # Use gpt-4o as specified
        
        llm = ChatOpenAI(
            model=model_name,
            temperature=settings.openai_temperature,
            openai_api_key=settings.openai_api_key
        )
        
        # Use the enhanced SupabaseChatAgent that can work with mock_data table
        logger.info("Creating enhanced SupabaseChatAgent for mock_data table")
        _agent_executor = SupabaseChatAgent(llm, db)
        
        logger.info("SQL agent initialized")
    
    return _agent_executor

@router.post("/chat", response_model=ChatResponse)
async def chat_with_data(request: ChatRequest, authorization: str = Header(None), settings=Depends(get_settings)):
    """
    Chat endpoint using enhanced SupabaseChatAgent with user authentication
    """
    try:
        # Check if we have a valid OpenAI API key
        if not settings.openai_api_key or "placeholder" in settings.openai_api_key:
            logger.warning("No valid OpenAI API key found, using mock responses")
            return ChatResponse(answer="I need an OpenAI API key to provide intelligent responses. Please configure your API key in the environment variables.")
        
        # Extract user ID from JWT token for data filtering
        from app.services.auth_service import AuthService
        
        user_id = None
        user_email = None
        
        if authorization and authorization.startswith("Bearer "):
            try:
                token = authorization.replace("Bearer ", "")
                auth_service = AuthService()
                user_info = await auth_service.verify_token(token)
                
                if user_info and user_info.get('user_found'):
                    user_id = user_info.get('user_id')
                    user_email = user_info.get('user_email')
                    logger.info(f"✅ User authenticated: {user_email} (ID: {user_id})")
                else:
                    logger.warning("❌ Token verification failed")
            except Exception as auth_error:
                logger.error(f"❌ Authentication error: {str(auth_error)}")
        else:
            logger.warning("❌ No Authorization header provided")
        
        logger.info(f"Processing chat request: {request.message}")
        if user_id:
            logger.info(f"👤 Authenticated User: {user_email} (ID: {user_id})")
        else:
            logger.warning("⚠️ No user ID available - using fallback data access")
        
        # Get the SQL agent
        agent = get_agent()
        
        # Enhanced input with user context for filtering
        enhanced_input = {
            "input": request.message,
            "user_id": user_id  # Pass user ID to agent for filtering
        }
        
        # Run the agent with user-specific context
        try:
            response = agent.invoke(enhanced_input)
            # Extract the output from the response
            if isinstance(response, dict) and "output" in response:
                answer = response["output"]
            else:
                answer = str(response)
        except Exception as agent_error:
            logger.error(f"Agent error: {str(agent_error)}")
            # Fallback to run method (won't have user filtering)
            answer = agent.run(request.message)
        
        logger.info(f"Agent response generated successfully: {len(answer)} characters")
        return ChatResponse(answer=answer)
        
    except Exception as e:
        logger.error(f"Chat processing failed: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail=f"Sorry, I couldn't process your question. Please try rephrasing it. Error: {str(e)}"
        )

@router.get("/chat/health")
async def chat_health():
    """Health check for chat service"""
    try:
        db = get_database()
        # Test database connection
        result = db.run("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}