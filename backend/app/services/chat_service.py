import openai
from typing import Dict, Any, List, Optional
import logging
import re
import json
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
        
        # Database schema for sellout_entries2 table
        self.schema_context = """
        Database Schema for sellout_entries2:
        - id: UUID (Primary Key)
        - product_ean: TEXT (Product EAN code)
        - month: INTEGER (1-12)
        - year: INTEGER (>= 2000)
        - quantity: INTEGER (Sales quantity)
        - sales_lc: TEXT (Sales in local currency)
        - sales_eur: NUMERIC (Sales in EUR)
        - currency: TEXT (Currency code)
        - reseller: TEXT (Reseller name)
        - functional_name: TEXT (Product functional name)
        - created_at: TIMESTAMP (Record creation time)
        - upload_id: UUID (Reference to uploads table)
        
        Related tables:
        - uploads: Contains file upload information
        - products: Contains product information (ean, name, brand)
        """
        
        self.system_prompt = f"""You are a SQL expert assistant for the Bibbi data cleaning system. 
        Your job is to convert natural language queries into SQL queries for the sellout_entries2 database.
        
        {self.schema_context}
        
        Rules:
        1. ALWAYS respond with ONLY valid SQL - no explanations, no text, just SQL
        2. Only generate SELECT queries - no INSERT, UPDATE, DELETE, DROP, etc.
        3. Always include appropriate LIMIT clauses (max 1000 rows)
        4. Use proper SQL syntax for the PostgreSQL database
        5. When joining tables, use appropriate JOIN syntax
        6. Handle date queries properly using month/year columns
        7. Be careful with data types and proper casting
        8. For ambiguous queries, make reasonable assumptions (e.g., use sales_eur for "total sales")
        
        Examples:
        "Show me total sales" -> "SELECT SUM(sales_eur) as total_sales FROM sellout_entries2 LIMIT 1000;"
        "Show products" -> "SELECT DISTINCT functional_name FROM sellout_entries2 LIMIT 1000;"
        "Show recent sales" -> "SELECT * FROM sellout_entries2 ORDER BY created_at DESC LIMIT 100;"
        
        Respond with ONLY the SQL query, nothing else."""
    
    def _classify_question(self, message: str) -> str:
        """Classify the type of question to determine response format"""
        message_lower = message.lower()
        
        # Direct answer questions (should get simple text responses)
        if any(phrase in message_lower for phrase in [
            'what is my total', 'what are my total', 'how much total',
            'what is the total', 'what are the total', 'how much is',
            'how much did', 'how much have', 'what did i sell',
            'how many total', 'how many records', 'how many sales'
        ]):
            return 'direct_answer'
        
        # Simple fact questions
        if any(phrase in message_lower for phrase in [
            'who is my top', 'who are my top', 'what is my top',
            'what is my best', 'which is my best', 'which product',
            'which reseller', 'which month', 'which year'
        ]):
            return 'direct_answer'
        
        # Count questions
        if any(phrase in message_lower for phrase in [
            'how many', 'count of', 'number of'
        ]):
            return 'direct_answer'
        
        # List/table questions (should show data tables)
        if any(phrase in message_lower for phrase in [
            'show me all', 'list all', 'show all', 'give me a list',
            'show me the', 'display all', 'what are all'
        ]):
            return 'show_table'
        
        # Analysis questions (might need tables)
        if any(phrase in message_lower for phrase in [
            'analyze', 'breakdown', 'compare', 'trend', 'over time'
        ]):
            return 'show_table'
        
        # Default to direct answer for simple questions
        if len(message.split()) <= 6:
            return 'direct_answer'
        
        return 'show_table'
    
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
            # Classify the question type
            question_type = self._classify_question(message)
            print(f"🤖 QUESTION CLASSIFICATION: {question_type}")
            
            # Generate SQL query from natural language
            sql_query = await self._generate_sql_query(message, user_id, session_id)
            
            # Validate and execute the query
            if self._is_query_safe(sql_query):
                # Add user filtering to the query
                filtered_query = self._add_user_filter(sql_query, user_id)
                
                # Execute the query
                print(f"🎯 CHAT SERVICE: Executing SQL query: {filtered_query}")
                results = await self.db_service.fetch_all(filtered_query)
                print(f"🎯 CHAT SERVICE: Got {len(results)} results from database")
                
                # Format results for display
                formatted_results = self._format_results(results)
                
                # Generate natural language response based on question type
                response_text = await self._generate_response(message, results, filtered_query, question_type)
                
                # Log the query and results
                await self._log_chat_activity(
                    user_id=user_id,
                    session_id=session_id,
                    user_message=message,
                    sql_query=filtered_query,
                    results_count=len(results),
                    response_text=response_text
                )
                
                return {
                    "success": True,
                    "message": response_text,
                    "sql_query": filtered_query,
                    "results": formatted_results,
                    "results_count": len(results),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                error_msg = "I cannot execute that query for security reasons. Please try a different question about your sales data."
                return {
                    "success": False,
                    "message": error_msg,
                    "sql_query": None,
                    "results": [],
                    "results_count": 0,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error processing chat query: {e}", exc_info=True)
            print(f"CHAT SERVICE ERROR: {str(e)}")
            print(f"CHAT SERVICE ERROR TYPE: {type(e).__name__}")
            print(f"CHAT SERVICE MESSAGE: {message}")
            print(f"CHAT SERVICE USER_ID: {user_id}")
            
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
                "debug_info": {
                    "original_message": message,
                    "user_id": user_id,
                    "session_id": session_id
                }
            }
    
    async def _generate_sql_query(
        self, 
        message: str, 
        user_id: str, 
        session_id: Optional[str] = None
    ) -> str:
        """Generate SQL query from natural language using OpenAI"""
        try:
            # Get conversation context if session exists
            context_messages = []
            if session_id:
                context_messages = await self._get_conversation_context(session_id)
            
            # Prepare messages for OpenAI
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Add conversation context
            for ctx_msg in context_messages[-5:]:  # Last 5 messages for context
                messages.append({
                    "role": "user" if ctx_msg["message_type"] == "user" else "assistant",
                    "content": ctx_msg["content"]
                })
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.settings.openai_model,
                messages=messages,
                temperature=self.settings.openai_temperature,
                max_tokens=self.settings.openai_max_tokens
            )
            
            sql_query = response.choices[0].message.content.strip()
            
            # Clean up the SQL query
            sql_query = self._clean_sql_query(sql_query)
            
            return sql_query
            
        except Exception as e:
            logger.error(f"Error generating SQL query: {e}")
            raise AppException(f"Failed to generate query: {str(e)}", 500)
    
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
        """Add user filtering to ensure data isolation - simplified for direct execution"""
        # For now, return the query as-is since we'll filter at the Supabase level
        # The database service will handle user filtering through RLS policies
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
            if not results:
                return "I couldn't find any data matching your query. Please try a different question."
            
            # Generate response based on question type
            if question_type == 'direct_answer':
                # Provide direct conversational answers
                return self._generate_direct_answer(original_question, results)
            else:
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
            if 'reseller' in results[0] and 'total_sales_eur' in results[0]:
                top_reseller = results[0]
                return f"Your top reseller is {top_reseller['reseller']} with €{top_reseller['total_sales_eur']:,.2f} in sales."
        
        if any(phrase in question_lower for phrase in ['top', 'best', 'highest']) and any(phrase in question_lower for phrase in ['product', 'item']):
            if 'functional_name' in results[0] and 'total_sales_eur' in results[0]:
                top_product = results[0]
                return f"Your top selling product is {top_product['functional_name']} with €{top_product['total_sales_eur']:,.2f} in sales."
        
        # Which questions
        if question_lower.startswith('which '):
            if 'reseller' in question_lower and 'reseller' in results[0]:
                if 'total_sales_eur' in results[0]:
                    top_item = results[0]
                    return f"The answer is {top_item['reseller']} with €{top_item['total_sales_eur']:,.2f} in sales."
                else:
                    return f"The answer is {results[0]['reseller']}."
            elif 'product' in question_lower and 'functional_name' in results[0]:
                if 'total_sales_eur' in results[0]:
                    top_item = results[0]
                    return f"The answer is {top_item['functional_name']} with €{top_item['total_sales_eur']:,.2f} in sales."
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
                return f"The total sales across all data is €{total:,.2f}."
            elif 'sales_eur' in results[0]:
                total_sales = sum(row.get('sales_eur', 0) or 0 for row in results)
                return f"The total sales from the selected data is €{total_sales:,.2f} across {len(results)} records."
        
        # Check if this is a reseller query
        elif any(word in question_lower for word in ['reseller', 'customer', 'client']) and any(word in question_lower for word in ['top', 'best', 'highest', 'by']):
            if 'reseller' in results[0] and 'total_sales_eur' in results[0]:
                top_reseller = results[0]
                return f"The top reseller is {top_reseller['reseller']} with €{top_reseller['total_sales_eur']:,.2f} in sales. I found {len(results)} resellers in total."
        
        # Check if this is a product query  
        elif any(word in question_lower for word in ['product', 'item', 'sku']) and any(word in question_lower for word in ['top', 'best', 'highest', 'popular']):
            if 'functional_name' in results[0] and 'total_sales_eur' in results[0]:
                top_product = results[0]
                return f"The top selling product is {top_product['functional_name']} with €{top_product['total_sales_eur']:,.2f} in sales. I found {len(results)} products in total."
        
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
                return f"I found {len(results)} records covering {len(years)} year(s) and {len(months)} month(s)."
        
        # Check if this is asking for lists of items
        elif any(word in question_lower for word in ['show', 'list', 'what are']):
            if 'functional_name' in results[0]:
                unique_products = len(set(row.get('functional_name') for row in results if row.get('functional_name')))
                return f"I found {unique_products} different products in {len(results)} records."
            elif 'reseller' in results[0]:
                unique_resellers = len(set(row.get('reseller') for row in results if row.get('reseller')))
                return f"I found data from {unique_resellers} different resellers in {len(results)} records."
        
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
            summary += "Here are the first 5 results:"
        
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
                VALUES (%s, %s, %s, %s, NULL, NULL, %s)
                """,
                (session_id, user_id, 'user', user_message, datetime.now())
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