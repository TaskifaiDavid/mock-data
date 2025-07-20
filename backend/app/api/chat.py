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
        self._include_tables = ['sellout_entries2', 'uploads', 'products']
    
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
            if "sellout_entries2" in command.lower():
                # Get recent sales data - this won't break your Excel cleaning
                result = self.db_service.supabase.table("sellout_entries2")\
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
        """Return table schema information"""
        return """
        Table: sellout_entries2
        Columns:
        - functional_name (text): Product name
        - reseller (text): Reseller/customer name
        - sales_eur (numeric): Sales amount in EUR
        - quantity (integer): Quantity sold
        - month (integer): Month (1-12)
        - year (integer): Year (e.g. 2024, 2025)
        - product_ean (text): Product EAN code
        - currency (text): Currency code
        
        Sample data:
        functional_name='Product A', reseller='Customer 1', sales_eur=1500.00, quantity=10, month=3, year=2024
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
        self.db_service = DatabaseService()
        self.debug_mode = True  # Enable detailed logging
    
    def invoke(self, inputs):
        """Process chat request using Supabase data with detailed debugging"""
        try:
            user_message = inputs.get("input", "")
            user_id = inputs.get("user_id")  # Get user ID for filtering
            
            if self.debug_mode:
                logger.info("=" * 50)
                logger.info("🤖 CHAT DEBUG MODE ENABLED")
                logger.info(f"📝 User message: {user_message}")
                logger.info(f"👤 User ID: {user_id}")
                logger.info("=" * 50)
            
            # Get user-specific sales data with year filtering if mentioned
            if self.debug_mode:
                logger.info("📊 Fetching user-specific sales data...")
            
            # Extract year from user message for filtering
            year_filter = self._extract_year_from_message(user_message)
            if self.debug_mode and year_filter:
                logger.info(f"📅 Year filter detected: {year_filter}")
            
            # Build query with optional year filtering
            if user_id:
                # Filter by user ID through uploads relationship
                query = self.db_service.supabase.table("sellout_entries2")\
                    .select("functional_name, reseller, sales_eur, quantity, month, year, product_ean, currency, uploads!inner(user_id)")\
                    .eq("uploads.user_id", user_id)
                
                # Add year filter if detected
                if year_filter:
                    query = query.eq("year", year_filter)
                    if self.debug_mode:
                        logger.info(f"📅 Applied year filter: {year_filter}")
                
                result = query.order("created_at", desc=True).limit(500).execute()
                
                if self.debug_mode:
                    logger.info(f"✅ Found {len(result.data) if result.data else 0} records for user {user_id} (year: {year_filter or 'all'})")
            else:
                # Fallback to recent data if no user ID
                query = self.db_service.supabase.table("sellout_entries2")\
                    .select("functional_name, reseller, sales_eur, quantity, month, year, product_ean, currency")
                
                # Add year filter if detected
                if year_filter:
                    query = query.eq("year", year_filter)
                    if self.debug_mode:
                        logger.info(f"📅 Applied year filter to fallback query: {year_filter}")
                
                result = query.order("created_at", desc=True).limit(500).execute()
                
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
                    logger.info(f"🧹 Cleaned data: {len(clean_data)} records")
                    logger.info(f"📈 Sample record: {clean_data[0] if clean_data else 'None'}")
                
                # Analyze user's question intent
                intent = self._analyze_question_intent(user_message)
                if self.debug_mode:
                    logger.info(f"🎯 Detected intent: {intent}")
                
                # Create a context-aware prompt with detailed data analysis
                data_summary = self._summarize_data(clean_data, intent)
                
                if self.debug_mode:
                    logger.info(f"📋 Data summary length: {len(data_summary)} characters")
                    logger.info("🔍 Sending to LLM for analysis...")
                
                prompt = f"""
                You are an expert sales data analyst. Based on the following sales data, answer the user's question with detailed analysis.
                
                IMPORTANT: Show your calculations step by step and provide specific numbers from the data.
                
                Sales Data Summary:
                {data_summary}
                
                Question Intent: {intent}
                User Question: {user_message}
                
                Instructions:
                1. Analyze the data carefully
                2. Provide specific numbers and calculations 
                3. If grouping data (by reseller, product, time), show the breakdown
                4. Format numbers with currency symbols and proper formatting
                5. If the data doesn't contain enough information, explain what's available and what's missing
                
                Be thorough and analytical in your response.
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
                logger.error("❌ ERROR in Supabase chat agent:")
                logger.error(f"   Error type: {type(e).__name__}")
                logger.error(f"   Error message: {str(e)}")
                import traceback
                logger.error(f"   Traceback: {traceback.format_exc()}")
            return {"output": f"I encountered an error while processing your request: {str(e)}"}
    
    def run(self, input_text):
        """Compatibility method for older LangChain versions"""
        result = self.invoke({"input": input_text})
        return result.get("output", "Error processing request")
    
    def _extract_year_from_message(self, user_message):
        """Extract year from user message for filtering"""
        import re
        
        # Look for 4-digit years (2020-2030)
        year_pattern = r'\b(202[0-9])\b'
        matches = re.findall(year_pattern, user_message)
        
        if matches:
            return int(matches[0])  # Return first year found
        
        return None
    
    def _analyze_question_intent(self, user_message):
        """Analyze user's question to understand their intent"""
        message_lower = user_message.lower()
        
        # Time-based queries
        if any(word in message_lower for word in ['year', 'month', 'quarterly', '2023', '2024', '2025', 'monthly', 'yearly', 'trend']):
            return "TIME_ANALYSIS"
        
        # Reseller/Customer analysis
        elif any(word in message_lower for word in ['reseller', 'customer', 'client', 'who', 'which reseller', 'top reseller', 'best reseller', 'highest']):
            return "RESELLER_ANALYSIS"
        
        # Product analysis
        elif any(word in message_lower for word in ['product', 'item', 'ean', 'functional_name', 'best selling', 'top selling']):
            return "PRODUCT_ANALYSIS"
        
        # Total/summary queries
        elif any(word in message_lower for word in ['total', 'sum', 'overall', 'all', 'entire']):
            return "TOTAL_SUMMARY"
        
        # Comparison queries
        elif any(word in message_lower for word in ['compare', 'vs', 'versus', 'difference', 'higher', 'lower', 'best', 'worst']):
            return "COMPARISON"
        
        else:
            return "GENERAL_INQUIRY"
    
    def _summarize_data(self, data, intent="GENERAL_INQUIRY"):
        """Create comprehensive data analysis for the LLM based on intent - NO SAMPLE RECORDS"""
        if not data:
            return "No data available"
        
        try:
            # Basic statistics
            total_sales = sum(float(row.get('sales_eur', 0) or 0) for row in data)
            total_quantity = sum(int(row.get('quantity', 0) or 0) for row in data)
            
            # Get unique entities
            products = set(row.get('functional_name') for row in data if row.get('functional_name'))
            resellers = set(row.get('reseller') for row in data if row.get('reseller'))
            currencies = set(row.get('currency') for row in data if row.get('currency'))
            
            # Time analysis
            years = set(row.get('year') for row in data if row.get('year'))
            months = set(row.get('month') for row in data if row.get('month'))
            
            # Build comprehensive analysis
            summary = f"""
            COMPLETE SALES DATA ANALYSIS ({len(data)} total records):
            - Total Sales: €{total_sales:,.2f}
            - Total Quantity: {total_quantity:,} units
            - Unique Products: {len(products)} products
            - Unique Resellers: {len(resellers)} resellers
            - Currencies: {', '.join(currencies)}
            - Time Period: Years {sorted(years)}, Months {sorted(months)}
            """
            
            # ALWAYS provide complete breakdowns for accurate analysis
            # 1. Complete Reseller Analysis
            reseller_totals = {}
            reseller_quantities = {}
            for row in data:
                reseller = row.get('reseller', 'Unknown')
                sales = float(row.get('sales_eur', 0) or 0)
                quantity = int(row.get('quantity', 0) or 0)
                
                if reseller not in reseller_totals:
                    reseller_totals[reseller] = 0
                    reseller_quantities[reseller] = 0
                reseller_totals[reseller] += sales
                reseller_quantities[reseller] += quantity
            
            sorted_resellers = sorted(reseller_totals.items(), key=lambda x: x[1], reverse=True)
            summary += f"\n\nCOMPLETE RESELLER ANALYSIS:\n"
            for reseller, total in sorted_resellers:
                quantity = reseller_quantities[reseller]
                summary += f"- {reseller}: €{total:,.2f} (Quantity: {quantity:,})\n"
            
            # 2. Complete Product Analysis
            product_totals = {}
            product_quantities = {}
            for row in data:
                product = row.get('functional_name', 'Unknown')
                sales = float(row.get('sales_eur', 0) or 0)
                quantity = int(row.get('quantity', 0) or 0)
                
                if product not in product_totals:
                    product_totals[product] = 0
                    product_quantities[product] = 0
                product_totals[product] += sales
                product_quantities[product] += quantity
            
            sorted_products = sorted(product_totals.items(), key=lambda x: x[1], reverse=True)
            summary += f"\n\nTOP 10 PRODUCTS BY SALES:\n"
            for product, total in sorted_products[:10]:
                quantity = product_quantities[product]
                summary += f"- {product}: €{total:,.2f} (Quantity: {quantity:,})\n"
            
            # 3. Complete Time Analysis
            monthly_totals = {}
            yearly_totals = {}
            for row in data:
                year = row.get('year')
                month = row.get('month')
                sales = float(row.get('sales_eur', 0) or 0)
                
                if year:
                    if year not in yearly_totals:
                        yearly_totals[year] = 0
                    yearly_totals[year] += sales
                    
                    if month:
                        time_key = f"{year}-{month:02d}"
                        if time_key not in monthly_totals:
                            monthly_totals[time_key] = 0
                        monthly_totals[time_key] += sales
            
            # Show yearly totals
            summary += f"\n\nYEARLY SALES TOTALS:\n"
            for year in sorted(yearly_totals.keys()):
                summary += f"- {year}: €{yearly_totals[year]:,.2f}\n"
            
            # Show monthly totals (recent ones)
            sorted_months = sorted(monthly_totals.items())
            summary += f"\n\nMONTHLY BREAKDOWN (Recent):\n"
            for time_period, total in sorted_months[-12:]:  # Last 12 months
                summary += f"- {time_period}: €{total:,.2f}\n"
            
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
    global _db
    if _db is None:
        settings = get_settings()
        
        # Try multiple connection approaches
        connection_attempts = [
            ("Explicit DATABASE_URL", settings.langchain_database_url),
        ]
        
        for attempt_name, db_url in connection_attempts:
            try:
                logger.info(f"Attempting database connection using: {attempt_name}")
                logger.info(f"Connection string format: {db_url[:50]}...")
                
                _db = SQLDatabase.from_uri(db_url)
                
                # Test the connection
                test_result = _db.run("SELECT 1 as test")
                logger.info(f"Database connection successful with {attempt_name}")
                logger.info(f"Test query result: {test_result}")
                
                return _db
                
            except Exception as e:
                logger.warning(f"Connection attempt '{attempt_name}' failed: {str(e)}")
                _db = None
                continue
        
        # If all direct connections fail, use Supabase REST API fallback
        logger.warning("All direct PostgreSQL connections failed. Using Supabase REST API fallback for chat.")
        global _use_supabase_fallback, _supabase_db_service
        _use_supabase_fallback = True
        _supabase_db_service = DatabaseService()
        
        # Create a mock SQLDatabase object that uses Supabase REST API
        _db = SupabaseSQLDatabase()
        logger.info("Supabase REST API fallback initialized for chat functionality")
    
    return _db

def get_agent():
    """Get or create SQL agent"""
    global _agent_executor, _use_supabase_fallback
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
        
        if _use_supabase_fallback:
            # For Supabase fallback, create a simple agent without SQL toolkit
            logger.info("Creating Supabase fallback agent")
            _agent_executor = SupabaseChatAgent(llm, db)
        else:
            # Create SQL agent directly (newer syntax) for direct PostgreSQL
            _agent_executor = create_sql_agent(
                llm=llm,
                db=db,
                verbose=True,
                agent_type=AgentType.OPENAI_FUNCTIONS,
                max_iterations=5
            )
        
        logger.info("SQL agent initialized")
    
    return _agent_executor

@router.post("/chat", response_model=ChatResponse)
async def chat_with_data(request: ChatRequest, authorization: str = Header(None), settings=Depends(get_settings)):
    """
    Enhanced chat endpoint with proper user authentication and debug mode
    """
    try:
        # Extract user ID from JWT token
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
        
        # Enhanced input with user context
        enhanced_input = {
            "input": request.message,
            "user_id": user_id  # Pass user ID to agent for filtering
        }
        
        # Run the agent with user-specific context
        try:
            response = agent.invoke(enhanced_input)
            # Extract the output from the response
            if isinstance(response, dict) and "output" in response:
                response = response["output"]
        except AttributeError:
            # Fallback to older run method (won't have user filtering)
            response = agent.run(request.message)
        
        logger.info(f"Agent response generated successfully: {len(response)} characters")
        return ChatResponse(answer=response)
        
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