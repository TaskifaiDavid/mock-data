import openai
from typing import Dict, Any, List, Optional
import logging
import re
import json
import os
from datetime import datetime
from app.services.db_service import DatabaseService
from app.utils.config import get_settings
from app.utils.exceptions import AppException

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        self.settings = get_settings()
        self.db_service = DatabaseService()
        self.client = openai.OpenAI(api_key=self.settings.openai_api_key)
        
        # Cache for database schema to avoid repeated lookups
        self._schema_cache = None
        self._schema_cache_timestamp = None
        self._enhanced_prompt_cache = None
        
        # Load base system prompt - enhanced prompt will be loaded lazily
        self.base_system_prompt = self._load_system_prompt()
    
    async def _get_enhanced_system_prompt(self) -> str:
        """Get enhanced system prompt with current database schema (async)"""
        try:
            # Check if we have a cached enhanced prompt that's still valid
            if self._enhanced_prompt_cache and self._is_schema_cache_valid():
                return self._enhanced_prompt_cache
            
            print("🔄 Loading enhanced system prompt with database schema...")
            
            # Get current database schema for enhanced context
            schema_info = await self._get_database_schema_async()
            
            # Build enhanced prompt with schema information
            enhanced_prompt = self._build_schema_enhanced_prompt(self.base_system_prompt, schema_info)
            
            # Cache the enhanced prompt
            self._enhanced_prompt_cache = enhanced_prompt
            
            print("✅ Enhanced system prompt loaded successfully")
            return enhanced_prompt
            
        except Exception as e:
            logger.error(f"Error creating enhanced system prompt: {e}")
            print(f"⚠️ Falling back to base system prompt due to error: {e}")
            # Fall back to basic prompt
            return self.base_system_prompt
    
    def _load_system_prompt(self) -> str:
        """Load system prompt from the prompts/system_prompt.txt file"""
        try:
            # Get the directory where this file is located
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up to backend directory and then to prompts
            prompt_file = os.path.join(current_dir, '..', '..', 'prompts', 'system_prompt.txt')
            
            with open(prompt_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            logger.warning("System prompt file not found, using fallback prompt")
            # Fallback system prompt
            return """You are a SQL expert assistant for the Bibbi data cleaning system. 
            Convert natural language queries into SQL queries for the sellout_entries2 database.
            Always respond with ONLY valid SQL - no explanations. Only generate SELECT queries.
            Always include appropriate LIMIT clauses (max 1000 rows).
            For sellout_entries2 queries, always filter by user using: JOIN uploads u ON se.upload_id = u.id WHERE u.user_id = %s"""
        except Exception as e:
            logger.error(f"Error loading system prompt: {e}")
            raise AppException(f"Failed to load system prompt: {str(e)}", 500)
    
    async def _get_database_schema_async(self) -> Dict[str, Any]:
        """Get enhanced database schema with statistics and relationships (Chat2DB-inspired)"""
        try:
            from datetime import datetime, timedelta
            
            now = datetime.now()
            cache_duration = timedelta(minutes=5)
            
            # Check if we need to refresh the cache
            if (self._schema_cache is None or 
                self._schema_cache_timestamp is None or 
                now - self._schema_cache_timestamp > cache_duration):
                
                print("🔄 Refreshing enhanced database schema cache...")
                
                # Get enhanced schema with Chat2DB-style statistics
                self._schema_cache = await self._get_enhanced_schema_with_stats()
                self._schema_cache_timestamp = now
                
                print(f"✅ Enhanced schema cache refreshed. Found {len(self._schema_cache.get('tables', {}))} tables")
            
            return self._schema_cache or {"tables": {}, "relationships": [], "sample_data": {}}
            
        except Exception as e:
            logger.error(f"Error getting database schema: {e}")
            print(f"❌ Schema discovery failed: {e}")
            # Return a minimal fallback schema for sellout_entries2
            return self._get_fallback_schema()
    
    def _is_schema_cache_valid(self) -> bool:
        """Check if the current schema cache is still valid"""
        try:
            from datetime import datetime, timedelta
            
            if self._schema_cache_timestamp is None:
                return False
            
            now = datetime.now()
            cache_duration = timedelta(minutes=5)
            
            return now - self._schema_cache_timestamp <= cache_duration
            
        except Exception:
            return False
    
    def _get_fallback_schema(self) -> Dict[str, Any]:
        """Provide a hardcoded fallback schema if discovery fails"""
        return {
            "tables": {
                "sellout_entries2": {
                    "name": "sellout_entries2",
                    "columns": [
                        {"name": "id", "type": "uuid"},
                        {"name": "upload_id", "type": "uuid"},
                        {"name": "product_ean", "type": "text"},
                        {"name": "functional_name", "type": "text"},
                        {"name": "reseller", "type": "text"},
                        {"name": "quantity", "type": "integer"},
                        {"name": "sales_eur", "type": "numeric"},
                        {"name": "sales_lc", "type": "text"},
                        {"name": "currency", "type": "text"},
                        {"name": "month", "type": "integer"},
                        {"name": "year", "type": "integer"},
                        {"name": "created_at", "type": "timestamp"}
                    ],
                    "row_count": "unknown",
                    "description": "Sales transaction records with product, reseller, quantities, and revenue data"
                },
                "uploads": {
                    "name": "uploads",
                    "columns": [
                        {"name": "id", "type": "uuid"},
                        {"name": "user_id", "type": "uuid"},
                        {"name": "filename", "type": "text"},
                        {"name": "status", "type": "text"}
                    ],
                    "row_count": "unknown", 
                    "description": "File upload tracking with user ownership"
                }
            },
            "relationships": [
                {
                    "from_table": "sellout_entries2",
                    "to_table": "uploads",
                    "join_condition": "sellout_entries2.upload_id = uploads.id",
                    "description": "Sales entries belong to file uploads"
                }
            ],
            "sample_data": {}
        }
    
    def _build_schema_enhanced_prompt(self, base_prompt: str, schema_info: Dict[str, Any]) -> str:
        """Build an advanced AI prompt system with comprehensive database context"""
        try:
            # Start with the base system prompt
            enhanced_prompt = base_prompt + "\n\n"
            
            # Add comprehensive database schema information
            enhanced_prompt += "=== COMPREHENSIVE DATABASE SCHEMA ===\n\n"
            
            # Primary Table (sellout_entries2) - Most Important
            enhanced_prompt += """PRIMARY DATA TABLE: sellout_entries2
This is the main business data table containing all sales transactions.

CRITICAL COLUMNS:
- id (uuid): Unique record identifier
- upload_id (uuid): Links to uploads table for user filtering - ALWAYS REQUIRED
- product_ean (text): Product identifier, links to products table
- functional_name (text): Standardized product name for reporting
- reseller (text): Customer/partner who made the sale
- quantity (integer): Number of units sold
- sales_eur (numeric): Revenue in EUR - PRIMARY METRIC for sales analysis
- sales_lc (text): Sales in local currency (original)
- currency (text): Original currency code
- month (integer): Month of sale (1-12)
- year (integer): Year of sale
- created_at (timestamp): Record creation time

BUSINESS RULES:
- sales_eur is the MAIN revenue metric (always use for "sales" questions)
- User data isolation: ALWAYS JOIN with uploads table on upload_id and filter by user_id
- Time queries: Use month (1-12) and year columns
- Product analysis: Use functional_name for standardized product names
- Reseller analysis: reseller column contains customer/partner names

"""
            
            # Add table relationships with examples
            enhanced_prompt += """=== TABLE RELATIONSHIPS & JOINS ===

MANDATORY USER FILTERING (Security Requirement):
Every sellout_entries2 query MUST include:
JOIN uploads u ON se.upload_id = u.id WHERE u.user_id = %s

PRODUCT INFORMATION:
JOIN products p ON se.product_ean = p.ean
(Optional - only if product details beyond functional_name are needed)

"""
            
            # Add intelligent query patterns for different business scenarios
            enhanced_prompt += """=== INTELLIGENT QUERY PATTERNS ===

SALES ANALYSIS PATTERNS:

1. TOTAL SALES (simple aggregation):
Question patterns: "total sales", "how much did I sell", "revenue"
Template: SELECT SUM(sales_eur) as total_sales_eur FROM sellout_entries2 se JOIN uploads u ON se.upload_id = u.id WHERE u.user_id = %s;

2. TIME-BASED SALES (temporal filtering):
Question patterns: "sales in [month/year]", "September 2024", "Q3", "this year"
Template: SELECT SUM(sales_eur) as total_sales_eur FROM sellout_entries2 se JOIN uploads u ON se.upload_id = u.id WHERE u.user_id = %s AND [time_filters];

3. RESELLER PERFORMANCE (grouping & ranking):
Question patterns: "top resellers", "best customers", "sales by partner"
Template: SELECT reseller, SUM(sales_eur) as total_sales, COUNT(*) as transactions FROM sellout_entries2 se JOIN uploads u ON se.upload_id = u.id WHERE u.user_id = %s GROUP BY reseller ORDER BY total_sales DESC LIMIT 20;

4. PRODUCT ANALYSIS (product performance):
Question patterns: "top products", "best selling items", "product performance"
Template: SELECT functional_name, SUM(sales_eur) as total_sales, SUM(quantity) as units_sold FROM sellout_entries2 se JOIN uploads u ON se.upload_id = u.id WHERE u.user_id = %s GROUP BY functional_name ORDER BY total_sales DESC LIMIT 20;

5. TEMPORAL TRENDS (time series):
Question patterns: "monthly sales", "trends", "sales over time"
Template: SELECT year, month, SUM(sales_eur) as monthly_sales, COUNT(*) as transactions FROM sellout_entries2 se JOIN uploads u ON se.upload_id = u.id WHERE u.user_id = %s GROUP BY year, month ORDER BY year DESC, month DESC LIMIT 24;

6. COMPARATIVE ANALYSIS (comparisons):
Question patterns: "compare [X] to [Y]", "vs", "versus", "year over year"
Template: Use subqueries or CTEs to compare different time periods or entities

7. DETAILED BREAKDOWNS (multi-dimensional analysis):
Question patterns: "breakdown by", "analysis", "detailed view"
Template: SELECT reseller, functional_name, year, month, SUM(sales_eur) as sales, SUM(quantity) as qty FROM sellout_entries2 se JOIN uploads u ON se.upload_id = u.id WHERE u.user_id = %s GROUP BY reseller, functional_name, year, month;

"""
            
            # Add advanced query optimization and best practices
            enhanced_prompt += """=== QUERY OPTIMIZATION & BEST PRACTICES ===

PERFORMANCE GUIDELINES:
1. Always include LIMIT clause (max 1000 rows for data exploration, fewer for top/bottom queries)
2. Use proper indexes: queries on year, month, reseller, functional_name are optimized
3. Aggregate before joining when possible
4. Use meaningful column aliases (total_sales, monthly_revenue, etc.)

DATA QUALITY HANDLING:
1. Handle NULL values: COALESCE(sales_eur, 0) for safe aggregations
2. Filter out test data if needed: WHERE reseller NOT LIKE '%test%'
3. Date validation: year >= 2020 AND month BETWEEN 1 AND 12

ADVANCED SQL FEATURES:
1. Window functions for ranking: ROW_NUMBER() OVER (ORDER BY sales_eur DESC)
2. CTEs for complex analysis: WITH monthly_data AS (...)
3. CASE statements for categorization: CASE WHEN sales_eur > 1000 THEN 'High' ELSE 'Low' END

"""
            
            # Add intelligent response guidelines
            enhanced_prompt += """=== INTELLIGENT RESPONSE GENERATION ===

QUERY COMPLEXITY MATCHING:
- Simple questions ("total sales") → Simple aggregation queries
- Complex questions ("top 5 products by revenue in Q3 2024 vs Q3 2023") → Complex multi-part queries
- Comparison questions → Use subqueries or CTEs
- Trend questions → Include time series grouping

COLUMN SELECTION INTELLIGENCE:
- Sales questions: Always include sales_eur
- Product questions: Include functional_name, sales_eur, quantity
- Reseller questions: Include reseller, sales_eur, transaction counts
- Time analysis: Include year, month, and appropriate aggregations

FILTERING INTELLIGENCE:
- Temporal filters: Convert natural language dates to month/year filters
- Performance filters: Add appropriate ORDER BY and LIMIT clauses
- Comparison filters: Use date ranges, reseller lists, product categories

=== CRITICAL REQUIREMENTS ===

1. SECURITY: Every query MUST include user filtering via uploads table join
2. CURRENCY: Always use sales_eur for consistent financial analysis
3. PERFORMANCE: Include appropriate LIMIT clauses
4. READABILITY: Use clear column aliases and logical ordering
5. SQL ONLY: Return ONLY valid SQL - no explanations, markdown, or comments

=== OUTPUT FORMAT ===
Generate ONLY the SQL query. No explanations, no markdown formatting, no comments.
The query should be ready to execute immediately.

"""
            
            return enhanced_prompt
            
        except Exception as e:
            logger.error(f"Error building enhanced prompt: {e}")
            return base_prompt
    
    def _detect_message_intent(self, message: str) -> str:
        """Detect the intent of the user's message"""
        message_lower = message.lower().strip()
        
        # Greeting patterns
        greeting_patterns = [
            'hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening',
            'how are you', 'howdy', 'greetings', 'what\'s up', 'whats up'
        ]
        
        if any(pattern in message_lower for pattern in greeting_patterns):
            return 'greeting'
        
        # Help/capability questions
        help_patterns = [
            'what can you do', 'what do you do', 'help', 'how can you help',
            'what are your capabilities', 'what can i ask', 'how do you work',
            'what is this', 'what are you', 'how does this work'
        ]
        
        if any(pattern in message_lower for pattern in help_patterns):
            return 'help'
        
        # Data query patterns - anything related to sales, products, resellers, data
        data_patterns = [
            # Sales related
            'sales', 'revenue', 'income', 'earnings', 'total', 'sum',
            # Product related  
            'product', 'item', 'functional_name', 'ean', 'sku',
            # Reseller related
            'reseller', 'customer', 'client', 'partner', 'retailer',
            # Query words
            'show', 'display', 'list', 'what', 'how much', 'how many',
            'best', 'top', 'highest', 'lowest', 'most', 'least',
            # Time related
            'month', 'year', 'quarter', 'q1', 'q2', 'q3', 'q4',
            'this year', 'last year', 'this month', 'last month',
            # Analysis
            'analyze', 'breakdown', 'compare', 'trend', 'performance'
        ]
        
        if any(pattern in message_lower for pattern in data_patterns):
            return 'data_query'
        
        # General conversation - anything else
        return 'conversation'
    
    def _classify_question(self, message: str) -> str:
        """Classify the type of data question to determine response format"""
        message_lower = message.lower()
        
        # Best/top/ranking questions should show tables
        if any(phrase in message_lower for phrase in [
            'best selling', 'top selling', 'best product', 'top product',
            'highest sales', 'most sales', 'top reseller', 'best reseller',
            'which is my best', 'which is my top', 'what are my best',
            'what are my top'
        ]):
            return 'show_table'
        
        # List/table questions (should show data tables)
        if any(phrase in message_lower for phrase in [
            'show me all', 'list all', 'show all', 'give me a list',
            'show me the', 'display all', 'what are all', 'show products',
            'show resellers', 'show sales'
        ]):
            return 'show_table'
        
        # Analysis questions (should show tables)
        if any(phrase in message_lower for phrase in [
            'analyze', 'breakdown', 'compare', 'trend', 'over time',
            'by month', 'by year', 'by reseller', 'by product'
        ]):
            return 'show_table'
        
        # Time-based questions (should show tables)
        if any(phrase in message_lower for phrase in [
            'july 2024', 'september 2024', 'january 2025', 'q1', 'q2', 'q3', 'q4',
            'monthly trends', 'quarterly', 'this year', 'last year', 'in 2024', 'in 2025',
            'sales in', 'performance in', 'sales for', 'revenue in'
        ]):
            return 'show_table'
        
        # Simple total/count questions (direct answers)
        if any(phrase in message_lower for phrase in [
            'what is my total', 'what are my total', 'how much total',
            'what is the total', 'what are the total', 'how much is',
            'how much did', 'how much have', 'what did i sell total',
            'how many total', 'how many records', 'how many sales'
        ]):
            return 'direct_answer'
        
        # Count questions (direct answers)
        if any(phrase in message_lower for phrase in [
            'how many', 'count of', 'number of'
        ]):
            return 'direct_answer'
        
        # Default to show_table for multi-word questions
        if len(message.split()) > 4:
            return 'show_table'
        
        return 'direct_answer'
    
    async def _handle_greeting(self, message: str) -> Dict[str, Any]:
        """Handle greeting messages"""
        greeting_responses = [
            "Hello! I'm your sales data assistant. I can help you analyze your sales data or just have a conversation. What would you like to know?",
            "Hi there! I'm here to help you with your sales data analysis. You can ask me about sales, products, resellers, or anything else!",
            "Hey! Nice to meet you. I can help you explore your sales data or chat about whatever's on your mind. What can I help you with?",
            "Greetings! I'm your AI assistant for sales data analysis. Feel free to ask me about your business data or just chat!"
        ]
        
        import random
        response = random.choice(greeting_responses)
        
        return {
            "success": True,
            "message": response,
            "sql_query": None,
            "results": [],
            "results_count": 0,
            "timestamp": datetime.now().isoformat(),
            "intent": "greeting"
        }
    
    async def _handle_help(self, message: str) -> Dict[str, Any]:
        """Handle help/capability questions"""
        help_response = """I'm your AI sales data assistant! Here's what I can do:

🤖 **General Chat**: I can have normal conversations and answer questions

📊 **Sales Data Analysis**: I can help you explore your sales data by asking questions like:
• "What are my total sales this year?"
• "Show me my top 5 resellers"
• "Which products sold the most last month?"
• "How did Q4 perform compared to Q3?"

📈 **Insights & Trends**: I can analyze patterns in your data:
• Monthly/yearly sales trends
• Product performance comparisons
• Reseller analysis
• Time-based breakdowns

💬 **Natural Language**: Just ask in plain English - I'll understand and help you get the information you need!

What would you like to explore today?"""

        return {
            "success": True,
            "message": help_response,
            "sql_query": None,
            "results": [],
            "results_count": 0,
            "timestamp": datetime.now().isoformat(),
            "intent": "help"
        }
    
    async def _handle_conversation(self, message: str) -> Dict[str, Any]:
        """Handle general conversational messages using OpenAI"""
        try:
            # Use OpenAI for conversational responses
            conversation_prompt = """You are a helpful and friendly AI assistant that works with sales data. 
            You can have normal conversations while also being knowledgeable about business and data analysis.
            Be conversational, helpful, and engaging. If the user asks about data, gently suggest they ask specific 
            questions about their sales data. Keep responses concise and friendly."""
            
            response = self.client.chat.completions.create(
                model=self.settings.openai_model,
                messages=[
                    {"role": "system", "content": conversation_prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            conversational_response = response.choices[0].message.content.strip()
            
            return {
                "success": True,
                "message": conversational_response,
                "sql_query": None,
                "results": [],
                "results_count": 0,
                "timestamp": datetime.now().isoformat(),
                "intent": "conversation"
            }
            
        except Exception as e:
            logger.error(f"Error generating conversational response: {e}")
            # Fallback response
            return {
                "success": True,
                "message": "I'm here to help! Feel free to ask me about your sales data or anything else on your mind.",
                "sql_query": None,
                "results": [],
                "results_count": 0,
                "timestamp": datetime.now().isoformat(),
                "intent": "conversation"
            }
    
    async def process_query(
        self, 
        user_id: str, 
        message: str, 
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process natural language query and return appropriate response
        
        Args:
            user_id: User ID for data filtering
            message: Natural language query
            session_id: Optional session ID for context
            
        Returns:
            Dictionary with query, results, and metadata
        """
        try:
            # First, detect the intent of the message
            intent = self._detect_message_intent(message)
            print(f"🎯 MESSAGE INTENT: {intent}")
            print(f"🎯 ORIGINAL MESSAGE: '{message}'")
            
            # Route based on intent
            if intent == 'greeting':
                response = await self._handle_greeting(message)
            elif intent == 'help':
                response = await self._handle_help(message)
            elif intent == 'conversation':
                response = await self._handle_conversation(message)
            elif intent == 'data_query':
                response = await self._handle_data_query(message, user_id, session_id)
            else:
                # Default to conversation for unknown intents
                response = await self._handle_conversation(message)
            
            # Log the interaction
            await self._log_chat_activity(
                user_id=user_id,
                session_id=session_id,
                user_message=message,
                sql_query=response.get('sql_query'),
                results_count=response.get('results_count', 0),
                response_text=response.get('message', '')
            )
            
            return response
                
        except Exception as e:
            logger.error(f"Error processing chat query: {e}", exc_info=True)
            print(f"CHAT SERVICE ERROR: {str(e)}")
            
            error_msg = f"I encountered an error processing your request: {str(e)}. Please try rephrasing your question."
            return {
                "success": False,
                "message": error_msg,
                "sql_query": None,
                "results": [],
                "results_count": 0,
                "error": str(e),
                "error_type": type(e).__name__,
                "timestamp": datetime.now().isoformat(),
                "intent": "error"
            }
    
    async def _handle_data_query(
        self, 
        message: str, 
        user_id: str, 
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Handle data query requests - the original SQL generation logic"""
        try:
            # Classify the question type for data queries
            question_type = self._classify_question(message)
            print(f"🤖 DATA QUESTION CLASSIFICATION: {question_type}")
            
            # Chat2DB Enhancement: Self-correcting query execution with fallbacks
            execution_result = await self._execute_query_with_self_correction(message, user_id, session_id)
            
            if execution_result['success']:
                results = execution_result['results']
                filtered_query = execution_result['final_query']
                print(f"🎯 CHAT SERVICE: Got {len(results)} results from database")
                
                # Debug: Log first few results to see actual data structure
                if results:
                    print(f"🔍 CHAT SERVICE: First result keys: {list(results[0].keys())}")
                    print(f"🔍 CHAT SERVICE: First result sample: {dict(list(results[0].items())[:3])}")
                else:
                    print(f"⚠️  CHAT SERVICE: No results returned from database!")
                    print(f"🔍 CHAT SERVICE: Query executed was: {filtered_query}")
                    print(f"🔍 CHAT SERVICE: User ID used: {user_id}")
                
                # Format results for display
                formatted_results = self._format_results(results)
                
                # Generate natural language response based on question type
                print(f"🤖 CHAT SERVICE: Question type: {question_type}")
                print(f"🤖 CHAT SERVICE: Generating response for {len(results)} results")
                response_text = await self._generate_response(message, results, filtered_query, question_type)
                print(f"🤖 CHAT SERVICE: Generated response: {response_text[:100]}...")
                
                return {
                    "success": True,
                    "message": response_text,
                    "sql_query": filtered_query,
                    "results": formatted_results,
                    "results_count": len(results),
                    "timestamp": datetime.now().isoformat(),
                    "intent": "data_query",
                    "query_method": execution_result.get('method', 'unknown'),
                    "patterns_tried": execution_result.get('patterns_tried', 1)
                }
            else:
                # Return the error from the self-correction system
                return {
                    "success": False,
                    "message": execution_result['error_message'],
                    "sql_query": execution_result.get('failed_query'),
                    "results": [],
                    "results_count": 0,
                    "timestamp": datetime.now().isoformat(),
                    "intent": "data_query",
                    "patterns_tried": execution_result.get('patterns_tried', 1)
                }
                
        except Exception as e:
            logger.error(f"Error processing data query: {e}", exc_info=True)
            error_msg = f"I encountered an error processing your data request: {str(e)}. Please try rephrasing your question."
            return {
                "success": False,
                "message": error_msg,
                "sql_query": None,
                "results": [],
                "results_count": 0,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "intent": "data_query"
            }
    
    async def _generate_sql_query(
        self, 
        message: str, 
        user_id: str, 
        session_id: Optional[str] = None
    ) -> str:
        """Generate SQL query using Chat2DB-inspired multi-pattern system"""
        try:
            # Chat2DB Enhancement: Multi-pattern generation with confidence scoring
            sql_result = await self._generate_multi_pattern_sql(message, user_id, session_id)
            
            # Return the best SQL query
            return sql_result['sql_query']
            
        except Exception as e:
            logger.error(f"Error generating SQL query: {e}")
            raise AppException(f"Failed to generate query: {str(e)}", 500)

    async def _generate_multi_pattern_sql(
        self, 
        message: str, 
        user_id: str, 
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Chat2DB-inspired multi-pattern SQL generation with confidence scoring.
        Generates multiple SQL variations and selects the best one.
        """
        try:
            print("🎯 CHAT2DB MULTI-PATTERN SQL GENERATION")
            print("=" * 60)
            
            # Pre-process the message for better understanding
            enhanced_message = self._enhance_natural_language(message)
            
            # Generate multiple SQL patterns using different approaches
            sql_patterns = []
            
            # Pattern 1: Intent-based generation (existing system)
            try:
                pattern1_sql = self._generate_sql_from_intent(enhanced_message, message)
                pattern1_confidence = self._calculate_pattern_confidence(pattern1_sql, message, "intent_based")
                sql_patterns.append({
                    'sql': pattern1_sql,
                    'confidence': pattern1_confidence,
                    'method': 'intent_based',
                    'description': 'Intent detection with template matching'
                })
                print(f"✅ Pattern 1 (Intent): Confidence {pattern1_confidence:.2f}")
            except Exception as e:
                print(f"⚠️ Pattern 1 failed: {e}")
            
            # Pattern 2: Enhanced context-aware generation
            try:
                pattern2_sql = await self._generate_context_aware_sql(enhanced_message, message, user_id)
                pattern2_confidence = self._calculate_pattern_confidence(pattern2_sql, message, "context_aware")
                sql_patterns.append({
                    'sql': pattern2_sql,
                    'confidence': pattern2_confidence,
                    'method': 'context_aware',
                    'description': 'Schema-aware generation with user context'
                })
                print(f"✅ Pattern 2 (Context): Confidence {pattern2_confidence:.2f}")
            except Exception as e:
                print(f"⚠️ Pattern 2 failed: {e}")
            
            # Pattern 3: Template-based with variations (Chat2DB style)
            try:
                pattern3_sql = self._generate_template_variation_sql(enhanced_message, message)
                pattern3_confidence = self._calculate_pattern_confidence(pattern3_sql, message, "template_variation")
                sql_patterns.append({
                    'sql': pattern3_sql,
                    'confidence': pattern3_confidence,
                    'method': 'template_variation',
                    'description': 'Template with business-logic variations'
                })
                print(f"✅ Pattern 3 (Template): Confidence {pattern3_confidence:.2f}")
            except Exception as e:
                print(f"⚠️ Pattern 3 failed: {e}")
            
            # Select the best pattern based on confidence score
            if not sql_patterns:
                # Fallback to basic total sales if all patterns fail
                fallback_sql = self._get_total_sales_sql({})
                return {
                    'sql_query': self._clean_sql_query(fallback_sql),
                    'confidence': 0.3,
                    'method': 'fallback',
                    'patterns_generated': 0,
                    'description': 'Fallback total sales query'
                }
            
            # Sort by confidence and select the best
            best_pattern = max(sql_patterns, key=lambda x: x['confidence'])
            
            print(f"🏆 SELECTED: {best_pattern['method']} (confidence: {best_pattern['confidence']:.2f})")
            print(f"📊 Generated {len(sql_patterns)} patterns total")
            
            # Clean up the selected SQL
            cleaned_sql = self._clean_sql_query(best_pattern['sql'])
            
            return {
                'sql_query': cleaned_sql,
                'confidence': best_pattern['confidence'],
                'method': best_pattern['method'],
                'patterns_generated': len(sql_patterns),
                'description': best_pattern['description'],
                'all_patterns': sql_patterns  # For debugging
            }
            
        except Exception as e:
            logger.error(f"Error in multi-pattern SQL generation: {e}")
            # Fallback to original method
            enhanced_message = self._enhance_natural_language(message)
            fallback_sql = self._generate_sql_from_intent(enhanced_message, message)
            return {
                'sql_query': self._clean_sql_query(fallback_sql),
                'confidence': 0.5,
                'method': 'fallback_original',
                'patterns_generated': 1,
                'description': 'Fallback to original intent system'
            }
    
    def _generate_sql_from_intent(self, enhanced_message: str, original_message: str) -> str:
        """Generate SQL based on detected intent patterns from sql_queries.md"""
        enhanced_lower = enhanced_message.lower()
        original_lower = original_message.lower()
        
        # Extract parameters from the enhanced message
        params = self._extract_query_parameters(enhanced_message, original_message)
        
        print(f"🎯 SQL INTENT DETECTION: Enhanced='{enhanced_lower}', Params={params}")
        
        # PRODUCT ANALYSIS INTENTS - Flexible word-based detection
        if self._is_product_analysis_query(enhanced_lower, original_lower):
            print("🛍️ MATCHED: Product analysis intent")
            return self._get_product_analysis_sql(params)
        
        if self._is_product_performance_query(enhanced_lower, original_lower):
            print("📊 MATCHED: Product performance intent")
            return self._get_product_quantity_sql(params)
        
        if self._is_price_analysis_query(enhanced_lower, original_lower):
            print("💰 MATCHED: Price analysis intent")
            return self._get_average_price_sql(params)
        
        # TEMPORAL ANALYSIS INTENTS - Flexible detection
        if self._is_monthly_trends_query(enhanced_lower, original_lower):
            print("📅 MATCHED: Monthly trends intent")
            return self._get_monthly_trends_sql(params)
        
        if self._is_quarterly_analysis_query(enhanced_lower, original_lower):
            print("📊 MATCHED: Quarterly analysis intent")
            return self._get_quarterly_analysis_sql(params)
        
        if self._is_yearly_analysis_query(enhanced_lower, original_lower):
            print("📈 MATCHED: Yearly analysis intent")
            return self._get_yearly_analysis_sql(params)
        
        # RESELLER ANALYSIS INTENTS - Flexible detection
        if self._is_reseller_analysis_query(enhanced_lower, original_lower):
            print("👥 MATCHED: Reseller analysis intent")
            return self._get_reseller_analysis_sql(params)
        
        if self._is_reseller_performance_query(enhanced_lower, original_lower):
            print("📊 MATCHED: Reseller performance intent")
            return self._get_reseller_product_analysis_sql(params)
        
        # COMPARATIVE ANALYSIS INTENTS
        if self._is_comparison_query(enhanced_lower, original_lower):
            print("⚖️ MATCHED: Comparison intent")
            return self._get_comparative_analysis_sql(params)
        
        # SPECIFIC TIME PERIOD QUERIES
        if params.get('month') and params.get('year'):
            print("📅 MATCHED: Time-filtered query (month + year)")
            return self._get_time_filtered_sales_sql(params)
        
        if params.get('year') and not params.get('month'):
            print("📅 MATCHED: Yearly query")
            return self._get_yearly_sales_sql(params)
        
        # SMART FALLBACK - Try to detect any missed patterns
        print("🔍 CHECKING FALLBACK PATTERNS...")
        
        # Check for any product-related words
        if any(word in enhanced_lower for word in ['product', 'products', 'item', 'items', 'selling', 'sell']):
            print("🛍️ FALLBACK: Detected product-related query")
            return self._get_product_analysis_sql(params)
        
        # Check for any customer/reseller words  
        if any(word in enhanced_lower for word in ['customer', 'customers', 'reseller', 'resellers', 'client', 'clients']):
            print("👥 FALLBACK: Detected reseller-related query")
            return self._get_reseller_analysis_sql(params)
        
        # Check for any time-related words
        if any(word in enhanced_lower for word in ['month', 'year', '2024', '2025', 'time', 'trend', 'trends']):
            print("📅 FALLBACK: Detected time-related query")
            return self._get_monthly_trends_sql(params)
        
        # DEFAULT: TOTAL SALES (true fallback)
        print("💰 DEFAULT: Using total sales fallback")
        return self._get_total_sales_sql(params)
    
    def _enhance_natural_language(self, message: str) -> str:
        """Advanced natural language pre-processing for better SQL generation"""
        try:
            enhanced_message = message.lower().strip()
            
            # Advanced temporal expressions - convert to specific time references
            import datetime
            import re
            current_year = datetime.datetime.now().year
            current_month = datetime.datetime.now().month
            
            # Handle specific month names (January, February, etc.)
            month_names = {
                'january': 1, 'jan': 1, 'february': 2, 'feb': 2, 'march': 3, 'mar': 3,
                'april': 4, 'apr': 4, 'may': 5, 'june': 6, 'jun': 6,
                'july': 7, 'jul': 7, 'august': 8, 'aug': 8, 'september': 9, 'sep': 9, 'sept': 9,
                'october': 10, 'oct': 10, 'november': 11, 'nov': 11, 'december': 12, 'dec': 12
            }
            
            # Enhanced pattern matching for dates
            for month_name, month_num in month_names.items():
                # Handle "January 2024", "Jan 2024", "January, 2024"
                pattern = rf'\b{month_name}[,\s]+(\d{{4}})\b'
                enhanced_message = re.sub(pattern, f'month {month_num} and year \\1', enhanced_message)
                
                # Handle "2024 January", "2024 Jan"  
                pattern = rf'\b(\d{{4}})[,\s]+{month_name}\b'
                enhanced_message = re.sub(pattern, f'month {month_num} and year \\1', enhanced_message)
                
                # Handle just month name (assume current year)
                if f' {month_name}' in enhanced_message and 'month' not in enhanced_message:
                    enhanced_message = enhanced_message.replace(f' {month_name}', f' month {month_num} and year {current_year}')
            
            # Handle numeric dates like "9/2024", "09/2024", "9-2024"
            enhanced_message = re.sub(r'\b(\d{1,2})[/-](\d{4})\b', r'month \1 and year \2', enhanced_message)
            
            # Handle year references "in 2024", "for 2024", "during 2024"
            enhanced_message = re.sub(r'\b(?:in|for|during|from)\s+(\d{4})\b', r'year \1', enhanced_message)
            
            # Replace temporal expressions with specific values
            temporal_replacements = {
                'this year': f'year {current_year}',
                'current year': f'year {current_year}', 
                'this month': f'month {current_month} and year {current_year}',
                'current month': f'month {current_month} and year {current_year}',
                'last year': f'year {current_year - 1}',
                'previous year': f'year {current_year - 1}',
                'last month': f'month {current_month - 1 if current_month > 1 else 12} and year {current_year if current_month > 1 else current_year - 1}',
                'previous month': f'month {current_month - 1 if current_month > 1 else 12} and year {current_year if current_month > 1 else current_year - 1}',
                'ytd': f'year {current_year}',
                'year to date': f'year {current_year}',
                'past 12 months': f'year {current_year - 1} and year {current_year}',
                'last 12 months': f'year {current_year - 1} and year {current_year}',
                'past year': f'year {current_year - 1}',
                # Quarters
                'q1': 'month IN (1, 2, 3)',
                'q2': 'month IN (4, 5, 6)', 
                'q3': 'month IN (7, 8, 9)',
                'q4': 'month IN (10, 11, 12)',
                'first quarter': 'month IN (1, 2, 3)',
                'second quarter': 'month IN (4, 5, 6)',
                'third quarter': 'month IN (7, 8, 9)',
                'fourth quarter': 'month IN (10, 11, 12)',
                # Seasonal references
                'spring': 'month IN (3, 4, 5)',
                'summer': 'month IN (6, 7, 8)', 
                'autumn': 'month IN (9, 10, 11)',
                'fall': 'month IN (9, 10, 11)',
                'winter': 'month IN (12, 1, 2)'
            }
            
            # Apply temporal replacements
            for temporal_phrase, replacement in temporal_replacements.items():
                enhanced_message = enhanced_message.replace(temporal_phrase, replacement)
            
            # Enhanced synonym replacements for better SQL generation
            synonym_replacements = {
                # Revenue/sales synonyms
                'revenue': 'sales', 'income': 'sales', 'earnings': 'sales', 'turnover': 'sales',
                'profit': 'sales', 'proceeds': 'sales', 'receipts': 'sales', 'takings': 'sales',
                
                # Product synonyms
                'items': 'products', 'goods': 'products', 'merchandise': 'products',
                'articles': 'products', 'stock': 'products', 'inventory': 'products',
                'skus': 'products', 'catalog': 'products',
                
                # Reseller/customer synonyms
                'customers': 'resellers', 'clients': 'resellers', 'partners': 'resellers',
                'retailers': 'resellers', 'vendors': 'resellers', 'distributors': 'resellers',
                'outlets': 'resellers', 'stores': 'resellers', 'shops': 'resellers',
                
                # Quantity/volume synonyms
                'volume': 'quantity', 'units': 'quantity', 'pieces': 'quantity',
                'count': 'quantity', 'amount': 'quantity', 'number': 'quantity',
                
                # Performance indicators
                'best performing': 'top', 'highest selling': 'top', 'most popular': 'top',
                'best selling': 'top', 'most successful': 'top', 'leading': 'top',
                'worst performing': 'bottom', 'lowest selling': 'bottom', 'least popular': 'bottom',
                'poorest': 'bottom', 'weakest': 'bottom',
                
                # Aggregation terms
                'sum of': 'total', 'total of': 'total', 'aggregate': 'total',
                'combined': 'total', 'overall': 'total', 'grand total': 'total'
            }
            
            # Apply synonym replacements
            for synonym, replacement in synonym_replacements.items():
                enhanced_message = enhanced_message.replace(synonym, replacement)
            
            # Enhanced business context patterns
            business_patterns = {
                # Comparison requests
                r'compare\s+(\w+)\s+(?:to|with|vs|versus)\s+(\w+)': r'show comparison between \1 and \2',
                r'(\w+)\s+(?:vs|versus)\s+(\w+)': r'compare \1 with \2',
                
                # Trend analysis
                r'trend(?:s)?\s+(?:for|of|in)\s+(\w+)': r'show sales_eur and quantity by month and year for \1',
                r'how\s+(?:is|are)\s+(\w+)\s+trending': r'show trend analysis for \1',
                
                # Performance analysis
                r'performance\s+(?:of|for)\s+(\w+)': r'show sales_eur and quantity for \1',
                r'how\s+(?:well|good)\s+(?:is|are)\s+(\w+)\s+(?:doing|performing)': r'show performance metrics for \1',
                
                # Growth analysis  
                r'growth\s+(?:in|of|for)\s+(\w+)': r'show month over month sales growth for \1',
                r'(?:year|yearly)\s+(?:over|on)\s+(?:year|yearly)\s+growth': r'compare this year to last year',
            }
            
            # Apply business pattern replacements
            for pattern, replacement in business_patterns.items():
                enhanced_message = re.sub(pattern, replacement, enhanced_message)
            
            # Add helpful context for common business questions
            business_context_additions = {
                'profitability': 'Show sales_eur and quantity breakdown for',
                'performance': 'Show sales_eur and quantity metrics for',
                'trends': 'Show sales_eur by month and year for',
                'analysis': 'Show detailed breakdown of',
                'breakdown': 'Show grouped data for',
                'comparison': 'Show comparative data for',
                'insights': 'Show detailed sales_eur analysis for',
                'metrics': 'Show key performance indicators for',
                'dashboard': 'Show comprehensive overview of',
                'report': 'Show detailed summary of'
            }
            
            # Add business context
            for context_word, addition in business_context_additions.items():
                if context_word in enhanced_message:
                    enhanced_message = enhanced_message.replace(context_word, addition)
            
            # Handle complex query structures
            complex_patterns = {
                # "What" questions
                r'what\s+(?:are|is)\s+my\s+': '',
                r'what\s+(?:are|is)\s+the\s+': '',
                
                # "Show me" patterns  
                r'show\s+me\s+': '',
                r'display\s+': '',
                r'list\s+': '',
                
                # "How much/many" patterns
                r'how\s+much\s+': 'total ',
                r'how\s+many\s+': 'count of ',
                
                # "Which" questions
                r'which\s+(\w+)\s+(?:is|are)\s+': 'top \1 ',
                r'which\s+(\w+)\s+': 'top \1 '
            }
            
            # Apply complex pattern replacements  
            for pattern, replacement in complex_patterns.items():
                enhanced_message = re.sub(pattern, replacement, enhanced_message)
            
            print(f"Enhanced message: '{message}' -> '{enhanced_message}'")
            return enhanced_message
            
        except Exception as e:
            logger.error(f"Error enhancing natural language: {e}")
            return message  # Return original if enhancement fails
    
    def _clean_sql_query(self, sql_query: str) -> str:
        """Clean and validate SQL query"""
        # Remove markdown code blocks if present
        sql_query = re.sub(r'```sql\s*\n?', '', sql_query)
        sql_query = re.sub(r'```\s*$', '', sql_query)
        
        # Remove extra whitespace
        sql_query = sql_query.strip()
        
        # Ensure it ends with semicolon
        if not sql_query.endswith(';'):
            sql_query += ';'
            
        return sql_query
    
    def _is_query_safe(self, sql_query: str) -> bool:
        """Validate that the SQL query is safe to execute"""
        sql_upper = sql_query.upper()
        
        # Check for dangerous operations
        dangerous_keywords = [
            'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 
            'TRUNCATE', 'GRANT', 'REVOKE', 'EXEC', 'EXECUTE',
            'CALL', 'PROCEDURE', 'FUNCTION'
        ]
        
        for keyword in dangerous_keywords:
            if f' {keyword} ' in sql_upper or sql_upper.startswith(keyword):
                return False
        
        # Must be a SELECT statement
        if not sql_upper.strip().startswith('SELECT'):
            return False
            
        return True
    
    def _add_user_filter(self, sql_query: str, user_id: str) -> str:
        """Add user filtering to ensure data isolation"""
        # The system prompt should already include proper user filtering with JOINs
        # Just replace the %s placeholder with the actual user_id
        if '%s' in sql_query:
            # For now, replace %s with a placeholder since we'll use parameterized queries
            return sql_query
        else:
            # If the query doesn't have user filtering, add it
            # This is a fallback in case the AI doesn't include proper filtering
            if 'FROM sellout_entries2' in sql_query and 'JOIN uploads' not in sql_query:
                # Add the user filter join
                sql_query = sql_query.replace(
                    'FROM sellout_entries2',
                    'FROM sellout_entries2 se JOIN uploads u ON se.upload_id = u.id'
                )
                if 'WHERE' in sql_query:
                    sql_query = sql_query.replace('WHERE', 'WHERE u.user_id = %s AND')
                else:
                    sql_query = sql_query.replace(';', ' WHERE u.user_id = %s;')
            return sql_query
    
    def _format_results(self, results: List[Dict]) -> List[Dict]:
        """Format query results for display"""
        if not results:
            return []
        
        # Convert any datetime objects to strings
        formatted_results = []
        for row in results:
            formatted_row = {}
            for key, value in row.items():
                if hasattr(value, 'isoformat'):  # datetime object
                    formatted_row[key] = value.isoformat()
                else:
                    formatted_row[key] = value
            formatted_results.append(formatted_row)
        
        return formatted_results
    
    async def _generate_response(self, original_question: str, results: List[Dict], sql_query: str = None, question_type: str = 'show_table') -> str:
        """Generate natural language response based on query results"""
        try:
            print(f"📝 RESPONSE GEN: Question: '{original_question}'")
            print(f"📝 RESPONSE GEN: Results count: {len(results)}")
            print(f"📝 RESPONSE GEN: Question type: {question_type}")
            
            if not results:
                print(f"📝 RESPONSE GEN: No results - returning 'no data' message")
                return "I couldn't find any data matching your query. Please try a different question."
            
            if results:
                print(f"📝 RESPONSE GEN: Sample result structure: {list(results[0].keys())}")
            
            # Generate response based on question type
            if question_type == 'direct_answer':
                print(f"📝 RESPONSE GEN: Using direct_answer logic")
                # Provide direct conversational answers
                return self._generate_direct_answer(original_question, results)
            else:
                print(f"📝 RESPONSE GEN: Using contextual_summary logic")
                # Generate contextual summary for table display
                summary = self._generate_contextual_summary(original_question, results, sql_query)
                return summary
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"I found {len(results)} records matching your query."
    
    def _generate_direct_answer(self, question: str, results: List[Dict]) -> str:
        """Generate direct conversational answers for simple questions"""
        question_lower = question.lower()
        
        if not results:
            return "I don't have any data to answer that question."
        
        # Total sales questions
        if any(word in question_lower for word in ['total sales', 'total revenue', 'how much total']):
            if 'total_sales_eur' in results[0]:
                total = results[0].get('total_sales_eur', 0)
                return f"Your total sales are €{total:,.2f}."
            elif 'sales_eur' in results[0]:
                total_sales = sum(row.get('sales_eur', 0) or 0 for row in results)
                return f"Your total sales are €{total_sales:,.2f}."
        
        # Count questions
        if any(phrase in question_lower for phrase in ['how many', 'count of', 'number of']):
            if 'total_count' in results[0]:
                count = results[0].get('total_count', 0)
                if 'record' in question_lower:
                    return f"You have {count:,} records in your database."
                elif 'sale' in question_lower:
                    return f"You have {count:,} sales records."
                else:
                    return f"The count is {count:,}."
            else:
                return f"I found {len(results):,} items."
        
        # Top/best questions
        if any(phrase in question_lower for phrase in ['top', 'best', 'highest']) and any(phrase in question_lower for phrase in ['reseller', 'customer', 'client']):
            if 'reseller' in results[0] and ('total_sales' in results[0] or 'total_sales_eur' in results[0]):
                top_reseller = results[0]
                sales_key = 'total_sales' if 'total_sales' in results[0] else 'total_sales_eur'
                return f"Your top reseller is {top_reseller['reseller']} with €{top_reseller[sales_key]:,.2f} in sales."
        
        if any(phrase in question_lower for phrase in ['top', 'best', 'highest']) and any(phrase in question_lower for phrase in ['product', 'item']):
            if 'functional_name' in results[0] and ('total_sales' in results[0] or 'total_sales_eur' in results[0]):
                top_product = results[0]
                sales_key = 'total_sales' if 'total_sales' in results[0] else 'total_sales_eur'
                return f"Your top selling product is {top_product['functional_name']} with €{top_product[sales_key]:,.2f} in sales."
        
        # Which questions
        if question_lower.startswith('which '):
            if 'reseller' in question_lower and 'reseller' in results[0]:
                if 'total_sales' in results[0] or 'total_sales_eur' in results[0]:
                    top_item = results[0]
                    sales_key = 'total_sales' if 'total_sales' in results[0] else 'total_sales_eur'
                    return f"The answer is {top_item['reseller']} with €{top_item[sales_key]:,.2f} in sales."
                else:
                    return f"The answer is {results[0]['reseller']}."
            elif 'product' in question_lower and 'functional_name' in results[0]:
                if 'total_sales' in results[0] or 'total_sales_eur' in results[0]:
                    top_item = results[0]
                    sales_key = 'total_sales' if 'total_sales' in results[0] else 'total_sales_eur'
                    return f"The answer is {top_item['functional_name']} with €{top_item[sales_key]:,.2f} in sales."
                else:
                    return f"The answer is {results[0]['functional_name']}."
        
        # What questions
        if question_lower.startswith('what '):
            if 'total' in question_lower and 'sales_eur' in results[0]:
                total_sales = sum(row.get('sales_eur', 0) or 0 for row in results)
                return f"The total is €{total_sales:,.2f}."
            elif 'total_sales_eur' in results[0]:
                return f"The total is €{results[0]['total_sales_eur']:,.2f}."
        
        # How much questions
        if question_lower.startswith('how much'):
            if 'total_sales_eur' in results[0]:
                return f"€{results[0]['total_sales_eur']:,.2f}."
            elif 'sales_eur' in results[0]:
                total_sales = sum(row.get('sales_eur', 0) or 0 for row in results)
                return f"€{total_sales:,.2f}."
        
        # Default direct answer
        if len(results) == 1:
            result = results[0]
            if 'total_sales_eur' in result:
                return f"The amount is €{result['total_sales_eur']:,.2f}."
            elif 'reseller' in result:
                return f"The answer is {result['reseller']}."
            elif 'functional_name' in result:
                return f"The answer is {result['functional_name']}."
            elif 'total_count' in result:
                return f"The count is {result['total_count']:,}."
        
        # If we can't give a specific direct answer, fall back to summary
        return f"Based on your data, I found {len(results)} relevant items."
    
    def _generate_contextual_summary(self, question: str, results: List[Dict], sql_query: str = None) -> str:
        """Generate intelligent contextual responses based on question type and results"""
        question_lower = question.lower()
        
        # Check if this is a total sales query
        if any(word in question_lower for word in ['total', 'sum', 'overall']) and 'sales' in question_lower:
            if 'total_sales_eur' in results[0]:
                total = results[0].get('total_sales_eur', 0)
                return f"The total sales across all data is €{total:,.2f}. Here are the results:"
            elif 'sales_eur' in results[0]:
                total_sales = sum(row.get('sales_eur', 0) or 0 for row in results)
                return f"The total sales from the selected data is €{total_sales:,.2f} across {len(results)} records. Here are the results:"
        
        # Check if this is a reseller query
        elif any(word in question_lower for word in ['reseller', 'customer', 'client']) and any(word in question_lower for word in ['top', 'best', 'highest', 'by']):
            if 'reseller' in results[0] and ('total_sales' in results[0] or 'total_sales_eur' in results[0]):
                top_reseller = results[0]
                sales_key = 'total_sales' if 'total_sales' in results[0] else 'total_sales_eur'
                return f"The top reseller is {top_reseller['reseller']} with €{top_reseller[sales_key]:,.2f} in sales. I found {len(results)} resellers in total. Here are the results:"
        
        # Check if this is a product query  
        elif any(word in question_lower for word in ['product', 'item', 'sku']) and any(word in question_lower for word in ['top', 'best', 'highest', 'popular', 'selling']):
            if 'functional_name' in results[0] and ('total_sales' in results[0] or 'total_sales_eur' in results[0]):
                top_product = results[0]
                sales_key = 'total_sales' if 'total_sales' in results[0] else 'total_sales_eur'
                return f"The top selling product is {top_product['functional_name']} with €{top_product[sales_key]:,.2f} in sales. I found {len(results)} products in total. Here are the results:"
        
        # Check if this is a count query
        elif 'count' in question_lower or 'how many' in question_lower:
            if 'total_count' in results[0]:
                count = results[0].get('total_count', 0)
                return f"There are {count:,} records in total."
        
        # Check if this is a time-based query
        elif any(word in question_lower for word in ['month', 'year', 'time', 'period', 'date']):
            if 'year' in results[0] and 'month' in results[0]:
                years = set(row.get('year') for row in results if row.get('year'))
                months = set(row.get('month') for row in results if row.get('month'))
                return f"I found {len(results)} records covering {len(years)} year(s) and {len(months)} month(s). Here are the results:"
        
        # Check if this is asking for lists of items
        elif any(word in question_lower for word in ['show', 'list', 'what are']):
            if 'functional_name' in results[0]:
                unique_products = len(set(row.get('functional_name') for row in results if row.get('functional_name')))
                return f"I found {unique_products} different products in {len(results)} records. Here are the results:"
            elif 'reseller' in results[0]:
                unique_resellers = len(set(row.get('reseller') for row in results if row.get('reseller')))
                return f"I found data from {unique_resellers} different resellers in {len(results)} records. Here are the results:"
        
        # Default comprehensive summary
        summary = f"I found {len(results)} records. "
        
        # Add specific insights based on the data structure
        if results and isinstance(results[0], dict):
            first_row = results[0]
            
            # Add sales information if available
            if 'sales_eur' in first_row:
                total_sales = sum(row.get('sales_eur', 0) or 0 for row in results)
                summary += f"Total sales value: €{total_sales:,.2f}. "
            
            # Add reseller information if available
            if 'reseller' in first_row:
                unique_resellers = len(set(row.get('reseller') for row in results if row.get('reseller')))
                summary += f"Data from {unique_resellers} reseller(s). "
            
            # Add product information if available
            if 'functional_name' in first_row:
                unique_products = len(set(row.get('functional_name') for row in results if row.get('functional_name')))
                summary += f"Covering {unique_products} different product(s). "
        
        # Show sample information
        if len(results) <= 5:
            summary += "Here are all the results:"
        else:
            summary += "Here are the results:"
        
        return summary
    
    async def _get_conversation_context(self, session_id: str) -> List[Dict]:
        """Get recent conversation context for a session"""
        try:
            query = """
            SELECT message_type, content, created_at
            FROM chat_messages 
            WHERE session_id = %s 
            ORDER BY created_at DESC 
            LIMIT 10
            """
            return await self.db_service.fetch_all(query, (session_id,))
        except Exception as e:
            logger.error(f"Error fetching conversation context: {e}")
            return []
    
    async def _log_chat_activity(
        self,
        user_id: str,
        session_id: Optional[str],
        user_message: str,
        sql_query: str,
        results_count: int,
        response_text: str
    ):
        """Log chat activity to database"""
        try:
            # Create session if it doesn't exist
            if not session_id:
                session_id = await self._create_chat_session(user_id)
            
            # Log user message
            await self.db_service.execute(
                """
                INSERT INTO chat_messages 
                (session_id, user_id, message_type, content, sql_query, query_result, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (session_id, user_id, 'user', user_message, None, None, datetime.now())
            )
            
            # Log assistant response
            query_result = {"results_count": results_count, "sql_query": sql_query}
            await self.db_service.execute(
                """
                INSERT INTO chat_messages 
                (session_id, user_id, message_type, content, sql_query, query_result, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (session_id, user_id, 'assistant', response_text, sql_query, json.dumps(query_result), datetime.now())
            )
            
        except Exception as e:
            logger.error(f"Error logging chat activity: {e}")
    
    async def _create_chat_session(self, user_id: str) -> str:
        """Create a new chat session"""
        try:
            result = await self.db_service.execute(
                """
                INSERT INTO chat_sessions (user_id, session_name, created_at)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (user_id, f"Chat Session {datetime.now().strftime('%Y-%m-%d %H:%M')}", datetime.now())
            )
            return result['id'] if result else None
        except Exception as e:
            logger.error(f"Error creating chat session: {e}")
            raise AppException(f"Failed to create chat session: {str(e)}", 500)
    
    async def get_chat_history(self, session_id: str, user_id: str) -> List[Dict]:
        """Get chat history for a session"""
        try:
            query = """
            SELECT 
                message_type,
                content,
                sql_query,
                query_result,
                created_at
            FROM chat_messages 
            WHERE session_id = %s AND user_id = %s
            ORDER BY created_at ASC
            """
            return await self.db_service.fetch_all(query, (session_id, user_id))
        except Exception as e:
            logger.error(f"Error fetching chat history: {e}")
            raise AppException(f"Failed to fetch chat history: {str(e)}", 500)
    
    async def clear_chat_session(self, session_id: str, user_id: str) -> bool:
        """Clear all messages in a chat session"""
        try:
            await self.db_service.execute(
                "DELETE FROM chat_messages WHERE session_id = %s AND user_id = %s",
                (session_id, user_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error clearing chat session: {e}")
            raise AppException(f"Failed to clear chat session: {str(e)}", 500)
    
    # ========================================
    # SQL TEMPLATE FUNCTIONS - Based on sql_queries.md
    # ========================================
    
    def _extract_query_parameters(self, enhanced_message: str, original_message: str) -> Dict[str, Any]:
        """Extract parameters like year, month, limit, product names, etc. from messages"""
        import re
        params = {}
        
        # Extract year
        year_match = re.search(r'year (\d{4})', enhanced_message)
        if year_match:
            params['year'] = int(year_match.group(1))
        
        # Extract month  
        month_match = re.search(r'month (\d{1,2})', enhanced_message)
        if month_match:
            params['month'] = int(month_match.group(1))
        
        # Extract quarter
        if 'month IN (' in enhanced_message:
            if '(1, 2, 3)' in enhanced_message:
                params['quarter'] = 'Q1'
                params['quarter_months'] = [1, 2, 3]
            elif '(4, 5, 6)' in enhanced_message:
                params['quarter'] = 'Q2'
                params['quarter_months'] = [4, 5, 6]
            elif '(7, 8, 9)' in enhanced_message:
                params['quarter'] = 'Q3'
                params['quarter_months'] = [7, 8, 9]
            elif '(10, 11, 12)' in enhanced_message:
                params['quarter'] = 'Q4'
                params['quarter_months'] = [10, 11, 12]
        
        # Extract limit/top N
        top_match = re.search(r'top (\d+)', enhanced_message.lower())
        if top_match:
            params['limit'] = int(top_match.group(1))
        elif 'top' in enhanced_message.lower():
            params['limit'] = 10  # Default top 10
        
        # Extract specific names for comparison
        if 'galilu' in enhanced_message.lower() and 'boxnox' in enhanced_message.lower():
            params['compare_resellers'] = ['Galilu', 'BoxNox']
        
        # Extract product name filters
        if 'bibbi' in enhanced_message.lower():
            params['product_filter'] = 'bibbi'
        
        return params
    
    # ========== FLEXIBLE INTENT DETECTION METHODS ==========
    
    def _is_product_analysis_query(self, enhanced_lower: str, original_lower: str) -> bool:
        """Check if this is a product analysis query with flexible matching"""
        product_words = ['product', 'products', 'item', 'items', 'functional_name']
        analysis_words = ['top', 'best', 'breakdown', 'selling', 'analysis', 'which', 'what']
        
        has_product = any(word in enhanced_lower for word in product_words)
        has_analysis = any(word in enhanced_lower for word in analysis_words)
        
        # Also check original message for different phrasing
        has_product_orig = any(word in original_lower for word in product_words)
        has_analysis_orig = any(word in original_lower for word in analysis_words)
        
        result = (has_product and has_analysis) or (has_product_orig and has_analysis_orig)
        if result:
            print(f"🛍️ PRODUCT ANALYSIS: product={has_product or has_product_orig}, analysis={has_analysis or has_analysis_orig}")
        return result
    
    def _is_product_performance_query(self, enhanced_lower: str, original_lower: str) -> bool:
        """Check if this is a product performance query"""
        product_words = ['product', 'products', 'item', 'items']
        performance_words = ['performance', 'units', 'quantity', 'volume', 'sold']
        
        has_product = any(word in enhanced_lower for word in product_words) or any(word in original_lower for word in product_words)
        has_performance = any(word in enhanced_lower for word in performance_words) or any(word in original_lower for word in performance_words)
        
        return has_product and has_performance
    
    def _is_price_analysis_query(self, enhanced_lower: str, original_lower: str) -> bool:
        """Check if this is a price analysis query"""
        price_words = ['price', 'pricing', 'average', 'cost', 'value']
        
        return any(word in enhanced_lower for word in price_words) or any(word in original_lower for word in price_words)
    
    def _is_monthly_trends_query(self, enhanced_lower: str, original_lower: str) -> bool:
        """Check if this is a monthly trends query"""
        monthly_words = ['monthly', 'month', 'months', 'trends', 'trend', 'month by month']
        
        return any(word in enhanced_lower for word in monthly_words) or any(word in original_lower for word in monthly_words)
    
    def _is_quarterly_analysis_query(self, enhanced_lower: str, original_lower: str) -> bool:
        """Check if this is a quarterly analysis query"""
        quarterly_words = ['quarterly', 'quarter', 'q1', 'q2', 'q3', 'q4']
        
        return any(word in enhanced_lower for word in quarterly_words) or any(word in original_lower for word in quarterly_words)
    
    def _is_yearly_analysis_query(self, enhanced_lower: str, original_lower: str) -> bool:
        """Check if this is a yearly analysis query"""
        yearly_words = ['yearly', 'annual', 'year over year', 'year']
        
        return any(word in enhanced_lower for word in yearly_words) or any(word in original_lower for word in yearly_words)
    
    def _is_reseller_analysis_query(self, enhanced_lower: str, original_lower: str) -> bool:
        """Check if this is a reseller analysis query"""
        reseller_words = ['reseller', 'resellers', 'customer', 'customers', 'client', 'clients']
        analysis_words = ['top', 'best', 'breakdown', 'analysis', 'which', 'who']
        
        has_reseller = any(word in enhanced_lower for word in reseller_words) or any(word in original_lower for word in reseller_words)
        has_analysis = any(word in enhanced_lower for word in analysis_words) or any(word in original_lower for word in analysis_words)
        
        result = has_reseller and has_analysis
        if result:
            print(f"👥 RESELLER ANALYSIS: reseller={has_reseller}, analysis={has_analysis}")
        return result
    
    def _is_reseller_performance_query(self, enhanced_lower: str, original_lower: str) -> bool:
        """Check if this is a reseller performance query"""
        reseller_words = ['reseller', 'resellers', 'customer', 'customers']
        performance_words = ['performance', 'breakdown', 'analysis']
        
        has_reseller = any(word in enhanced_lower for word in reseller_words) or any(word in original_lower for word in reseller_words)
        has_performance = any(word in enhanced_lower for word in performance_words) or any(word in original_lower for word in performance_words)
        
        return has_reseller and has_performance
    
    def _is_comparison_query(self, enhanced_lower: str, original_lower: str) -> bool:
        """Check if this is a comparison query"""
        comparison_words = ['compare', 'vs', 'versus', 'comparison', 'against']
        
        return any(word in enhanced_lower for word in comparison_words) or any(word in original_lower for word in comparison_words)
    
    def _get_product_analysis_sql(self, params: Dict[str, Any]) -> str:
        """Generate product analysis SQL - Query #1 from sql_queries.md"""
        limit = params.get('limit', 20)
        year_filter = f" AND year = {params['year']}" if params.get('year') else ""
        month_filter = f" AND month = {params['month']}" if params.get('month') else ""
        
        product_filter = ""
        if params.get('product_filter'):
            product_filter = f" AND functional_name ILIKE '%{params['product_filter']}%'"
        
        return f"""
        SELECT functional_name AS product, 
               SUM(sales_eur) AS total_sales, 
               SUM(quantity) AS total_units,
               COUNT(*) AS transactions
        FROM sellout_entries2 se 
        JOIN uploads u ON se.upload_id = u.id 
        WHERE u.user_id = %s{year_filter}{month_filter}{product_filter}
        GROUP BY functional_name 
        ORDER BY total_sales DESC 
        LIMIT {limit};
        """
    
    def _get_product_quantity_sql(self, params: Dict[str, Any]) -> str:
        """Generate product quantity analysis - Query #11 from sql_queries.md"""
        limit = params.get('limit', 20)
        year_filter = f" AND year = {params['year']}" if params.get('year') else ""
        
        return f"""
        SELECT functional_name AS product, 
               SUM(quantity) AS total_units_sold,
               SUM(sales_eur) AS total_sales
        FROM sellout_entries2 se 
        JOIN uploads u ON se.upload_id = u.id 
        WHERE u.user_id = %s{year_filter}
        GROUP BY functional_name 
        ORDER BY total_units_sold DESC
        LIMIT {limit};
        """
    
    def _get_average_price_sql(self, params: Dict[str, Any]) -> str:
        """Generate average price analysis - Query #6 from sql_queries.md"""
        limit = params.get('limit', 20)
        
        return f"""
        SELECT functional_name AS product,
               SUM(sales_eur) / NULLIF(SUM(quantity), 0) AS avg_price_per_unit,
               SUM(sales_eur) AS total_sales,
               SUM(quantity) AS total_units
        FROM sellout_entries2 se 
        JOIN uploads u ON se.upload_id = u.id 
        WHERE u.user_id = %s
        GROUP BY functional_name 
        ORDER BY avg_price_per_unit DESC
        LIMIT {limit};
        """
    
    def _get_monthly_trends_sql(self, params: Dict[str, Any]) -> str:
        """Generate monthly trends analysis - Query #8 from sql_queries.md"""
        year_filter = f" AND year = {params['year']}" if params.get('year') else ""
        
        return f"""
        SELECT year, month, 
               SUM(sales_eur) AS total_sales,
               SUM(quantity) AS total_units,
               COUNT(DISTINCT functional_name) AS unique_products,
               COUNT(*) AS transactions
        FROM sellout_entries2 se 
        JOIN uploads u ON se.upload_id = u.id 
        WHERE u.user_id = %s{year_filter}
        GROUP BY year, month 
        ORDER BY year DESC, month DESC
        LIMIT 24;
        """
    
    def _get_quarterly_analysis_sql(self, params: Dict[str, Any]) -> str:
        """Generate quarterly analysis - Query #3 from sql_queries.md"""
        year_filter = f" AND year = {params['year']}" if params.get('year') else ""
        
        quarter_filter = ""
        if params.get('quarter_months'):
            months = ', '.join(map(str, params['quarter_months']))
            quarter_filter = f" AND month IN ({months})"
        
        return f"""
        SELECT year,
               CASE 
                 WHEN month IN (1,2,3) THEN 'Q1'
                 WHEN month IN (4,5,6) THEN 'Q2'
                 WHEN month IN (7,8,9) THEN 'Q3'
                 WHEN month IN (10,11,12) THEN 'Q4'
               END AS quarter,
               SUM(sales_eur) AS total_sales,
               SUM(quantity) AS total_units,
               COUNT(*) AS transactions
        FROM sellout_entries2 se 
        JOIN uploads u ON se.upload_id = u.id 
        WHERE u.user_id = %s{year_filter}{quarter_filter}
        GROUP BY year, quarter 
        ORDER BY year DESC, quarter DESC;
        """
    
    def _get_yearly_analysis_sql(self, params: Dict[str, Any]) -> str:
        """Generate year-over-year analysis - Query #5 from sql_queries.md"""
        return """
        SELECT year,
               SUM(sales_eur) AS yearly_sales,
               SUM(quantity) AS yearly_units,
               COUNT(DISTINCT functional_name) AS unique_products,
               COUNT(DISTINCT reseller) AS unique_resellers,
               COUNT(*) AS transactions
        FROM sellout_entries2 se 
        JOIN uploads u ON se.upload_id = u.id 
        WHERE u.user_id = %s
        GROUP BY year 
        ORDER BY year DESC;
        """
    
    def _get_reseller_analysis_sql(self, params: Dict[str, Any]) -> str:
        """Generate reseller analysis - Query #7 from sql_queries.md"""
        limit = params.get('limit', 20)
        year_filter = f" AND year = {params['year']}" if params.get('year') else ""
        
        return f"""
        SELECT reseller, 
               SUM(sales_eur) AS total_sales,
               SUM(quantity) AS total_units,
               COUNT(*) AS transactions,
               COUNT(DISTINCT functional_name) AS unique_products
        FROM sellout_entries2 se 
        JOIN uploads u ON se.upload_id = u.id 
        WHERE u.user_id = %s{year_filter}
        GROUP BY reseller 
        ORDER BY total_sales DESC
        LIMIT {limit};
        """
    
    def _get_reseller_product_analysis_sql(self, params: Dict[str, Any]) -> str:
        """Generate reseller-product breakdown - Query #14 from sql_queries.md"""
        limit = params.get('limit', 50)
        
        return f"""
        SELECT reseller, functional_name AS product, 
               SUM(sales_eur) AS total_sales,
               SUM(quantity) AS total_units,
               COUNT(*) AS transactions
        FROM sellout_entries2 se 
        JOIN uploads u ON se.upload_id = u.id 
        WHERE u.user_id = %s
        GROUP BY reseller, functional_name 
        ORDER BY reseller, total_sales DESC
        LIMIT {limit};
        """
    
    def _get_comparative_analysis_sql(self, params: Dict[str, Any]) -> str:
        """Generate comparative analysis for specific resellers"""
        if params.get('compare_resellers'):
            resellers = "', '".join(params['compare_resellers'])
            return f"""
            SELECT reseller,
                   SUM(sales_eur) AS total_sales,
                   SUM(quantity) AS total_units,
                   COUNT(*) AS transactions,
                   COUNT(DISTINCT functional_name) AS unique_products,
                   SUM(sales_eur) / NULLIF(SUM(quantity), 0) AS avg_price_per_unit
            FROM sellout_entries2 se 
            JOIN uploads u ON se.upload_id = u.id 
            WHERE u.user_id = %s AND reseller IN ('{resellers}')
            GROUP BY reseller 
            ORDER BY total_sales DESC;
            """
        else:
            # Generic comparison query
            return self._get_reseller_analysis_sql(params)
    
    def _get_time_filtered_sales_sql(self, params: Dict[str, Any]) -> str:
        """Generate time-filtered sales query"""
        month = params.get('month')
        year = params.get('year')
        
        return f"""
        SELECT SUM(sales_eur) AS total_sales_eur,
               SUM(quantity) AS total_units,
               COUNT(*) AS transactions,
               COUNT(DISTINCT functional_name) AS unique_products,
               COUNT(DISTINCT reseller) AS unique_resellers
        FROM sellout_entries2 se 
        JOIN uploads u ON se.upload_id = u.id 
        WHERE u.user_id = %s AND month = {month} AND year = {year};
        """
    
    def _get_yearly_sales_sql(self, params: Dict[str, Any]) -> str:
        """Generate yearly sales query"""
        year = params.get('year')
        
        return f"""
        SELECT year, 
               SUM(sales_eur) AS total_sales_eur,
               SUM(quantity) AS total_units,
               COUNT(*) AS transactions,
               COUNT(DISTINCT functional_name) AS unique_products,
               COUNT(DISTINCT reseller) AS unique_resellers
        FROM sellout_entries2 se 
        JOIN uploads u ON se.upload_id = u.id 
        WHERE u.user_id = %s AND year = {year}
        GROUP BY year;
        """
    
    def _get_total_sales_sql(self, params: Dict[str, Any]) -> str:
        """Generate total sales query (fallback)"""
        return """
        SELECT SUM(sales_eur) AS total_sales_eur,
               SUM(quantity) AS total_units,
               COUNT(*) AS transactions,
               COUNT(DISTINCT functional_name) AS unique_products,
               COUNT(DISTINCT reseller) AS unique_resellers
        FROM sellout_entries2 se 
        JOIN uploads u ON se.upload_id = u.id 
        WHERE u.user_id = %s;
        """

    # ========================================================================
    # CHAT2DB-INSPIRED MULTI-PATTERN SQL GENERATION METHODS
    # ========================================================================
    
    def _calculate_pattern_confidence(self, sql_query: str, original_message: str, method: str) -> float:
        """
        Calculate confidence score for a generated SQL pattern.
        Higher score means better match between query intent and SQL structure.
        """
        try:
            confidence = 0.0
            message_lower = original_message.lower()
            sql_lower = sql_query.lower()
            
            # Base confidence based on method
            method_confidence = {
                'intent_based': 0.7,
                'context_aware': 0.8,
                'template_variation': 0.6,
                'fallback': 0.3
            }
            confidence = method_confidence.get(method, 0.5)
            
            # Keyword matching bonus
            query_keywords = {
                'product': ['functional_name', 'product'],
                'reseller': ['reseller', 'customer', 'client'],
                'time': ['year', 'month', 'date'],
                'sales': ['sales_eur', 'sum(sales_eur)'],
                'top': ['order by', 'limit'],
                'breakdown': ['group by'],
                'compare': ['group by', 'reseller', 'functional_name']
            }
            
            for intent_word, sql_patterns in query_keywords.items():
                if intent_word in message_lower:
                    for pattern in sql_patterns:
                        if pattern in sql_lower:
                            confidence += 0.1
                            break
            
            # SQL complexity assessment
            if 'group by' in sql_lower:
                confidence += 0.1  # Analytical queries are often better
            if 'order by' in sql_lower:
                confidence += 0.1  # Sorted results are usually desired
            if 'limit' in sql_lower:
                confidence += 0.05  # Performance-conscious
            
            # Penalize basic queries for complex questions
            if len(message_lower.split()) > 5 and 'sum(' in sql_lower and 'group by' not in sql_lower:
                confidence -= 0.2  # Complex question shouldn't get simple aggregation
                
            # Cap confidence at 1.0
            return min(confidence, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating pattern confidence: {e}")
            return 0.5  # Default moderate confidence

    async def _generate_context_aware_sql(self, enhanced_message: str, original_message: str, user_id: str) -> str:
        """
        Generate SQL using enhanced schema context (Chat2DB-inspired).
        Uses database schema information to create more accurate queries.
        """
        try:
            # Get enhanced schema information with user context
            schema_info = await self._get_enhanced_schema_with_stats(user_id)
            
            # Extract parameters
            params = self._extract_query_parameters(enhanced_message, original_message)
            message_lower = original_message.lower()
            
            # Determine query intent with schema awareness
            if any(word in message_lower for word in ['product', 'item', 'functional_name']):
                # Product-focused query with schema context
                if 'top' in message_lower or 'best' in message_lower:
                    return """
                    SELECT functional_name,
                           SUM(sales_eur) as total_sales,
                           SUM(quantity) as total_units,
                           COUNT(*) as transactions,
                           ROUND(SUM(sales_eur) / NULLIF(SUM(quantity), 0), 2) as avg_price_per_unit
                    FROM sellout_entries2 se 
                    JOIN uploads u ON se.upload_id = u.id 
                    WHERE u.user_id = %s
                    GROUP BY functional_name 
                    ORDER BY total_sales DESC
                    LIMIT 15;
                    """
            
            elif any(word in message_lower for word in ['reseller', 'customer', 'client']):
                # Reseller-focused query
                if 'top' in message_lower or 'best' in message_lower:
                    return """
                    SELECT reseller,
                           SUM(sales_eur) as total_sales,
                           SUM(quantity) as total_units,
                           COUNT(*) as transactions,
                           COUNT(DISTINCT functional_name) as unique_products
                    FROM sellout_entries2 se 
                    JOIN uploads u ON se.upload_id = u.id 
                    WHERE u.user_id = %s
                    GROUP BY reseller 
                    ORDER BY total_sales DESC
                    LIMIT 15;
                    """
            
            elif any(word in message_lower for word in ['month', 'year', '2024', '2025', 'trend']):
                # Time-based analysis - check if specific year is requested
                year_param = params.get('year')
                if year_param:
                    return f"""
                    SELECT year, month,
                           SUM(sales_eur) as monthly_sales,
                           SUM(quantity) as monthly_units,
                           COUNT(DISTINCT functional_name) as products_sold,
                           COUNT(DISTINCT reseller) as active_resellers
                    FROM sellout_entries2 se 
                    JOIN uploads u ON se.upload_id = u.id 
                    WHERE u.user_id = %s AND year = {year_param}
                    GROUP BY year, month 
                    ORDER BY year DESC, month DESC
                    LIMIT 12;
                    """
                else:
                    return """
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
                    """
            
            # Fallback to enhanced total with context
            return """
            SELECT 'Total Sales Summary' as summary_type,
                   SUM(sales_eur) as total_sales,
                   SUM(quantity) as total_units,
                   COUNT(*) as total_transactions,
                   COUNT(DISTINCT functional_name) as unique_products,
                   COUNT(DISTINCT reseller) as unique_resellers,
                   ROUND(SUM(sales_eur) / NULLIF(COUNT(*), 0), 2) as avg_transaction_value
            FROM sellout_entries2 se 
            JOIN uploads u ON se.upload_id = u.id 
            WHERE u.user_id = %s;
            """
            
        except Exception as e:
            logger.error(f"Error in context-aware SQL generation: {e}")
            # Fallback to basic intent generation
            return self._generate_sql_from_intent(enhanced_message, original_message)

    def _generate_template_variation_sql(self, enhanced_message: str, original_message: str) -> str:
        """
        Generate SQL using template variations (Chat2DB-style).
        Creates business-logic focused variations of common query patterns.
        """
        try:
            message_lower = original_message.lower()
            params = self._extract_query_parameters(enhanced_message, original_message)
            
            # Business insight templates with variations
            if any(word in message_lower for word in ['best', 'top', 'highest']):
                if 'product' in message_lower:
                    # Top products with business insights
                    return """
                    SELECT functional_name as product,
                           SUM(sales_eur) as revenue,
                           SUM(quantity) as units_sold,
                           COUNT(DISTINCT reseller) as reseller_count,
                           ROUND(SUM(sales_eur) / NULLIF(SUM(quantity), 0), 2) as avg_unit_price,
                           ROUND(SUM(sales_eur) / NULLIF(COUNT(DISTINCT reseller), 0), 2) as avg_revenue_per_reseller
                    FROM sellout_entries2 se 
                    JOIN uploads u ON se.upload_id = u.id 
                    WHERE u.user_id = %s AND functional_name IS NOT NULL
                    GROUP BY functional_name 
                    HAVING SUM(sales_eur) > 0
                    ORDER BY revenue DESC
                    LIMIT 10;
                    """
                
                elif any(word in message_lower for word in ['customer', 'reseller', 'client']):
                    # Top customers with business metrics
                    return """
                    SELECT reseller as customer,
                           SUM(sales_eur) as total_revenue,
                           SUM(quantity) as total_units,
                           COUNT(DISTINCT functional_name) as product_variety,
                           COUNT(*) as transaction_frequency,
                           ROUND(SUM(sales_eur) / NULLIF(COUNT(*), 0), 2) as avg_order_value
                    FROM sellout_entries2 se 
                    JOIN uploads u ON se.upload_id = u.id 
                    WHERE u.user_id = %s AND reseller IS NOT NULL
                    GROUP BY reseller 
                    HAVING SUM(sales_eur) > 0
                    ORDER BY total_revenue DESC
                    LIMIT 15;
                    """
            
            elif any(word in message_lower for word in ['trend', 'analysis', 'breakdown']):
                # Analytical breakdown template
                return """
                SELECT 
                    CASE 
                        WHEN month IN (1,2,3) THEN CONCAT(year, ' Q1')
                        WHEN month IN (4,5,6) THEN CONCAT(year, ' Q2')
                        WHEN month IN (7,8,9) THEN CONCAT(year, ' Q3')
                        WHEN month IN (10,11,12) THEN CONCAT(year, ' Q4')
                    END as quarter,
                    SUM(sales_eur) as quarterly_sales,
                    SUM(quantity) as quarterly_units,
                    COUNT(DISTINCT functional_name) as unique_products,
                    COUNT(DISTINCT reseller) as active_resellers
                FROM sellout_entries2 se 
                JOIN uploads u ON se.upload_id = u.id 
                WHERE u.user_id = %s
                GROUP BY year, 
                    CASE 
                        WHEN month IN (1,2,3) THEN 1
                        WHEN month IN (4,5,6) THEN 2
                        WHEN month IN (7,8,9) THEN 3
                        WHEN month IN (10,11,12) THEN 4
                    END
                ORDER BY year DESC, 
                    CASE 
                        WHEN month IN (1,2,3) THEN 1
                        WHEN month IN (4,5,6) THEN 2
                        WHEN month IN (7,8,9) THEN 3
                        WHEN month IN (10,11,12) THEN 4
                    END DESC
                LIMIT 8;
                """
            
            elif any(word in message_lower for word in ['compare', 'vs', 'versus']):
                # Comparison template
                return """
                SELECT functional_name as product,
                       reseller,
                       SUM(sales_eur) as sales,
                       SUM(quantity) as units,
                       ROUND(SUM(sales_eur) / NULLIF(SUM(quantity), 0), 2) as unit_price
                FROM sellout_entries2 se 
                JOIN uploads u ON se.upload_id = u.id 
                WHERE u.user_id = %s
                GROUP BY functional_name, reseller
                HAVING SUM(sales_eur) > 0
                ORDER BY functional_name, sales DESC
                LIMIT 50;
                """
            
            # Default enhanced summary template
            return """
            SELECT 'Business Overview' as metric_type,
                   SUM(sales_eur) as total_revenue,
                   SUM(quantity) as total_units_sold,
                   COUNT(*) as total_transactions,
                   COUNT(DISTINCT functional_name) as products_in_catalog,
                   COUNT(DISTINCT reseller) as active_partners,
                   ROUND(SUM(sales_eur) / NULLIF(SUM(quantity), 0), 2) as avg_unit_value,
                   ROUND(SUM(sales_eur) / NULLIF(COUNT(*), 0), 2) as avg_transaction_size
            FROM sellout_entries2 se 
            JOIN uploads u ON se.upload_id = u.id 
            WHERE u.user_id = %s;
            """
            
        except Exception as e:
            logger.error(f"Error in template variation SQL generation: {e}")
            return self._get_total_sales_sql({})

    async def _execute_query_with_self_correction(
        self, 
        message: str, 
        user_id: str, 
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Chat2DB-inspired self-correcting query execution.
        Tries multiple query patterns if the first one fails.
        """
        try:
            print("🔄 CHAT2DB SELF-CORRECTION: Starting query execution with fallbacks")
            
            # Generate multiple SQL patterns
            sql_result = await self._generate_multi_pattern_sql(message, user_id, session_id)
            all_patterns = sql_result.get('all_patterns', [])
            
            # Sort patterns by confidence (highest first)
            sorted_patterns = sorted(all_patterns, key=lambda x: x['confidence'], reverse=True)
            
            patterns_tried = 0
            last_error = None
            
            for i, pattern in enumerate(sorted_patterns):
                patterns_tried += 1
                print(f"🔄 ATTEMPT {patterns_tried}: Trying {pattern['method']} (confidence: {pattern['confidence']:.2f})")
                
                try:
                    sql_query = pattern['sql']
                    
                    # Validate query safety
                    if not self._is_query_safe(sql_query):
                        print(f"⚠️ SKIPPED: Query failed safety validation")
                        continue
                    
                    # Add user filtering
                    filtered_query = self._add_user_filter(sql_query, user_id)
                    
                    # Execute the query
                    print(f"📊 EXECUTING: {filtered_query[:100]}...")
                    
                    if '%s' in filtered_query:
                        results = await self.db_service.fetch_all(filtered_query, (user_id,))
                    else:
                        results = await self.db_service.fetch_all(filtered_query)
                    
                    # Check if query returned meaningful results
                    if results and len(results) > 0:
                        print(f"✅ SUCCESS: Query returned {len(results)} results")
                        return {
                            'success': True,
                            'results': results,
                            'final_query': filtered_query,
                            'method': pattern['method'],
                            'patterns_tried': patterns_tried,
                            'confidence': pattern['confidence']
                        }
                    elif results is not None and len(results) == 0:
                        # Query succeeded but returned no data - this is valid
                        print(f"✅ SUCCESS: Query executed but returned no data (valid)")
                        return {
                            'success': True,
                            'results': [],
                            'final_query': filtered_query,
                            'method': pattern['method'],
                            'patterns_tried': patterns_tried,
                            'confidence': pattern['confidence']
                        }
                    else:
                        print(f"⚠️ EMPTY: Query returned no results, trying next pattern...")
                        continue
                        
                except Exception as e:
                    print(f"❌ FAILED: {pattern['method']} - {str(e)}")
                    last_error = e
                    continue
            
            # If all patterns failed, try a simple fallback query
            print(f"🔄 FINAL FALLBACK: All {patterns_tried} patterns failed, trying basic total sales")
            
            try:
                fallback_sql = self._get_total_sales_sql({})
                filtered_fallback = self._add_user_filter(fallback_sql, user_id)
                
                if '%s' in filtered_fallback:
                    fallback_results = await self.db_service.fetch_all(filtered_fallback, (user_id,))
                else:
                    fallback_results = await self.db_service.fetch_all(filtered_fallback)
                
                if fallback_results is not None:
                    print(f"✅ FALLBACK SUCCESS: Returned {len(fallback_results)} results")
                    return {
                        'success': True,
                        'results': fallback_results,
                        'final_query': filtered_fallback,
                        'method': 'fallback_total_sales',
                        'patterns_tried': patterns_tried + 1,
                        'confidence': 0.3
                    }
            except Exception as fallback_error:
                print(f"❌ FALLBACK FAILED: {fallback_error}")
                last_error = fallback_error
            
            # Complete failure
            error_message = f"I tried {patterns_tried + 1} different approaches but couldn't execute your query successfully."
            if last_error:
                error_message += f" The last error was: {str(last_error)}"
            error_message += " Please try rephrasing your question or ask for help with available data."
            
            return {
                'success': False,
                'results': [],
                'final_query': None,
                'method': 'all_failed',
                'patterns_tried': patterns_tried + 1,
                'error_message': error_message,
                'failed_query': sql_result.get('sql_query', 'unknown')
            }
            
        except Exception as e:
            logger.error(f"Error in self-correcting query execution: {e}")
            return {
                'success': False,
                'results': [],
                'final_query': None,
                'method': 'system_error',
                'patterns_tried': 1,
                'error_message': f"System error during query execution: {str(e)}",
                'failed_query': 'system_error'
            }

    async def _get_enhanced_schema_with_stats(self, user_id: str = None) -> Dict[str, Any]:
        """
        Get enhanced database schema with Chat2DB-style statistics and relationships.
        Includes table stats, column distributions, and business context.
        """
        try:
            print("📊 CHAT2DB SCHEMA ENHANCEMENT: Gathering table statistics...")
            
            # Start with basic schema
            try:
                basic_schema = await self.db_service.get_database_schema()
            except:
                basic_schema = self._get_fallback_schema()
            
            # Enhance with statistics and business context
            enhanced_schema = {
                "tables": {},
                "relationships": [],
                "sample_data": {},
                "statistics": {},
                "business_context": {}
            }
            
            # Get enhanced statistics for sellout_entries2 (main table)
            try:
                stats_query = """
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
                """
                
                stats_result = await self.db_service.fetch_all(stats_query)
                
                if stats_result and len(stats_result) > 0:
                    stats = stats_result[0]
                    enhanced_schema["statistics"]["sellout_entries2"] = {
                        "total_records": stats.get("total_records", 0),
                        "unique_products": stats.get("unique_products", 0),
                        "unique_resellers": stats.get("unique_resellers", 0),
                        "unique_time_periods": stats.get("unique_time_periods", 0),
                        "sales_range": {
                            "min": float(stats.get("min_sales", 0)) if stats.get("min_sales") else 0,
                            "max": float(stats.get("max_sales", 0)) if stats.get("max_sales") else 0,
                            "avg": float(stats.get("avg_sales", 0)) if stats.get("avg_sales") else 0,
                            "total": float(stats.get("total_sales", 0)) if stats.get("total_sales") else 0
                        },
                        "quantity_range": {
                            "min": int(stats.get("min_quantity", 0)) if stats.get("min_quantity") else 0,
                            "max": int(stats.get("max_quantity", 0)) if stats.get("max_quantity") else 0,
                            "avg": float(stats.get("avg_quantity", 0)) if stats.get("avg_quantity") else 0,
                            "total": int(stats.get("total_quantity", 0)) if stats.get("total_quantity") else 0
                        },
                        "time_range": {
                            "earliest_year": int(stats.get("earliest_year", 2024)) if stats.get("earliest_year") else 2024,
                            "latest_year": int(stats.get("latest_year", 2024)) if stats.get("latest_year") else 2024
                        }
                    }
                    print(f"📊 Gathered statistics: {stats.get('total_records', 0)} total records")
                
            except Exception as e:
                print(f"⚠️ Could not gather table statistics: {e}")
                enhanced_schema["statistics"]["sellout_entries2"] = {
                    "total_records": "unknown",
                    "note": "Statistics unavailable"
                }
            
            # Get top products for business context
            try:
                # Add user filtering if user_id is available
                if user_id:
                    top_products_query = """
                    SELECT functional_name, 
                           SUM(sales_eur) as total_sales,
                           SUM(quantity) as total_quantity
                    FROM sellout_entries2 se 
                    JOIN uploads u ON se.upload_id = u.id
                    WHERE functional_name IS NOT NULL AND u.user_id = %s
                    GROUP BY functional_name 
                    ORDER BY total_sales DESC 
                    LIMIT 5;
                    """
                    top_products = await self.db_service.fetch_all(top_products_query, (user_id,))
                else:
                    top_products_query = """
                    SELECT functional_name, 
                           SUM(sales_eur) as total_sales,
                           SUM(quantity) as total_quantity
                    FROM sellout_entries2 se 
                    JOIN uploads u ON se.upload_id = u.id
                    WHERE functional_name IS NOT NULL
                    GROUP BY functional_name 
                    ORDER BY total_sales DESC 
                    LIMIT 5;
                    """
                    top_products = await self.db_service.fetch_all(top_products_query)
                enhanced_schema["business_context"]["top_products"] = [
                    {
                        "name": product.get("functional_name"),
                        "total_sales": float(product.get("total_sales", 0)) if product.get("total_sales") else 0,
                        "total_quantity": int(product.get("total_quantity", 0)) if product.get("total_quantity") else 0
                    }
                    for product in top_products[:5]
                ]
                print(f"📊 Found {len(top_products)} top products for context")
                
            except Exception as e:
                print(f"⚠️ Could not gather top products: {e}")
            
            # Get top resellers for business context
            try:
                # Add user filtering if user_id is available
                if user_id:
                    top_resellers_query = """
                    SELECT reseller, 
                           SUM(sales_eur) as total_sales,
                           COUNT(DISTINCT functional_name) as product_count
                    FROM sellout_entries2 se 
                    JOIN uploads u ON se.upload_id = u.id
                    WHERE reseller IS NOT NULL AND u.user_id = %s
                    GROUP BY reseller 
                    ORDER BY total_sales DESC 
                    LIMIT 5;
                    """
                    top_resellers = await self.db_service.fetch_all(top_resellers_query, (user_id,))
                else:
                    top_resellers_query = """
                    SELECT reseller, 
                           SUM(sales_eur) as total_sales,
                           COUNT(DISTINCT functional_name) as product_count
                    FROM sellout_entries2 se 
                    JOIN uploads u ON se.upload_id = u.id
                    WHERE reseller IS NOT NULL
                    GROUP BY reseller 
                    ORDER BY total_sales DESC 
                    LIMIT 5;
                    """
                    top_resellers = await self.db_service.fetch_all(top_resellers_query)
                enhanced_schema["business_context"]["top_resellers"] = [
                    {
                        "name": reseller.get("reseller"),
                        "total_sales": float(reseller.get("total_sales", 0)) if reseller.get("total_sales") else 0,
                        "product_count": int(reseller.get("product_count", 0)) if reseller.get("product_count") else 0
                    }
                    for reseller in top_resellers[:5]
                ]
                print(f"📊 Found {len(top_resellers)} top resellers for context")
                
            except Exception as e:
                print(f"⚠️ Could not gather top resellers: {e}")
            
            # Copy basic schema tables and enhance
            enhanced_schema["tables"] = basic_schema.get("tables", {})
            enhanced_schema["relationships"] = basic_schema.get("relationships", [])
            enhanced_schema["sample_data"] = basic_schema.get("sample_data", {})
            
            # Add table metadata for better context
            if "sellout_entries2" in enhanced_schema["tables"]:
                enhanced_schema["tables"]["sellout_entries2"]["business_purpose"] = "Primary sales transaction data"
                enhanced_schema["tables"]["sellout_entries2"]["key_metrics"] = ["sales_eur", "quantity", "functional_name", "reseller"]
                enhanced_schema["tables"]["sellout_entries2"]["analysis_dimensions"] = ["time (year/month)", "product", "reseller", "geography"]
            
            if "uploads" in enhanced_schema["tables"]:
                enhanced_schema["tables"]["uploads"]["business_purpose"] = "File upload tracking and user data isolation"
                enhanced_schema["tables"]["uploads"]["key_relationship"] = "Links to sellout_entries2 via upload_id"
            
            print(f"✅ Enhanced schema complete with statistics and business context")
            return enhanced_schema
            
        except Exception as e:
            logger.error(f"Error creating enhanced schema: {e}")
            print(f"❌ Enhanced schema failed, falling back to basic schema: {e}")
            # Fallback to basic schema
            try:
                return await self.db_service.get_database_schema()
            except:
                return self._get_fallback_schema()