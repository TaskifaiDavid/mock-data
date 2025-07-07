from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
from app.services.chat_service import ChatService
from app.services.auth_service import get_current_user
from app.models.auth import UserInDB
from app.utils.exceptions import AppException

logger = logging.getLogger(__name__)

router = APIRouter()

class ChatQueryRequest(BaseModel):
    message: str
    sessionId: Optional[str] = None
    userId: Optional[str] = None

class ChatQueryResponse(BaseModel):
    success: bool
    message: str
    sqlQuery: Optional[str] = None
    results: List[Dict[str, Any]] = []
    resultsCount: int = 0
    timestamp: str
    sessionId: Optional[str] = None
    error: Optional[str] = None

class ChatHistoryResponse(BaseModel):
    messages: List[Dict[str, Any]]
    sessionId: str
    totalMessages: int

@router.post("/query", response_model=ChatQueryResponse)
async def send_chat_query(
    request: ChatQueryRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Process natural language query and return SQL results
    """
    try:
        logger.info(f"Processing chat query for user {current_user.email}: {request.message[:100]}...")
        
        # Initialize chat service
        chat_service = ChatService()
        
        # Process the query
        result = await chat_service.process_query(
            user_id=current_user.id,
            message=request.message,
            session_id=request.sessionId
        )
        
        return ChatQueryResponse(
            success=result["success"],
            message=result["message"],
            sqlQuery=result.get("sql_query"),
            results=result["results"],
            resultsCount=result["results_count"],
            timestamp=result["timestamp"],
            sessionId=request.sessionId,
            error=result.get("error")
        )
        
    except AppException as e:
        logger.error(f"Chat service error: {e}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error in chat query: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/history/{session_id}", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get chat history for a specific session
    """
    try:
        logger.info(f"Fetching chat history for session {session_id} and user {current_user.email}")
        
        # Initialize chat service
        chat_service = ChatService()
        
        # Get chat history
        messages = await chat_service.get_chat_history(session_id, current_user.id)
        
        # Format messages for frontend
        formatted_messages = []
        for msg in messages:
            formatted_msg = {
                "type": msg["message_type"],
                "content": msg["content"],
                "timestamp": msg["created_at"].isoformat() if hasattr(msg["created_at"], 'isoformat') else str(msg["created_at"]),
                "sqlQuery": msg.get("sql_query"),
                "queryResult": msg.get("query_result")
            }
            formatted_messages.append(formatted_msg)
        
        return ChatHistoryResponse(
            messages=formatted_messages,
            sessionId=session_id,
            totalMessages=len(formatted_messages)
        )
        
    except AppException as e:
        logger.error(f"Chat service error: {e}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error fetching chat history: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/clear/{session_id}")
async def clear_chat_session(
    session_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Clear all messages in a chat session
    """
    try:
        logger.info(f"Clearing chat session {session_id} for user {current_user.email}")
        
        # Initialize chat service
        chat_service = ChatService()
        
        # Clear the session
        success = await chat_service.clear_chat_session(session_id, current_user.id)
        
        return {
            "success": success,
            "message": "Chat session cleared successfully",
            "sessionId": session_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except AppException as e:
        logger.error(f"Chat service error: {e}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error clearing chat session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/sessions")
async def get_chat_sessions(
    current_user: UserInDB = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0
):
    """
    Get all chat sessions for the current user
    """
    try:
        from app.services.db_service import DatabaseService
        
        db_service = DatabaseService()
        
        # Query chat sessions
        query = """
        SELECT 
            cs.id,
            cs.session_name,
            cs.created_at,
            cs.updated_at,
            COUNT(cm.id) as message_count
        FROM chat_sessions cs
        LEFT JOIN chat_messages cm ON cs.id = cm.session_id
        WHERE cs.user_id = %s 
        GROUP BY cs.id, cs.session_name, cs.created_at, cs.updated_at
        ORDER BY cs.updated_at DESC 
        LIMIT %s OFFSET %s
        """
        
        sessions = await db_service.fetch_all(query, (current_user.id, limit, offset))
        
        # Format sessions for frontend
        formatted_sessions = []
        for session in sessions:
            formatted_session = {
                "id": session["id"],
                "name": session["session_name"],
                "messageCount": session["message_count"],
                "createdAt": session["created_at"].isoformat() if hasattr(session["created_at"], 'isoformat') else str(session["created_at"]),
                "updatedAt": session["updated_at"].isoformat() if hasattr(session["updated_at"], 'isoformat') else str(session["updated_at"])
            }
            formatted_sessions.append(formatted_session)
        
        return {
            "sessions": formatted_sessions,
            "total": len(formatted_sessions),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error fetching chat sessions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/schema")
async def get_database_schema(
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get database schema information for the chat interface
    """
    try:
        from app.services.db_service import DatabaseService
        
        db_service = DatabaseService()
        
        # Get schema information for sellout_entries2 table
        schema_query = """
        SELECT 
            column_name,
            data_type,
            is_nullable,
            column_default
        FROM information_schema.columns 
        WHERE table_name = 'sellout_entries2'
        AND table_schema = 'public'
        ORDER BY ordinal_position
        """
        
        columns = await db_service.fetch_all(schema_query)
        
        # Get sample data to show data patterns
        sample_query = """
        SELECT se.*
        FROM sellout_entries2 se
        JOIN uploads u ON se.upload_id = u.id
        WHERE u.user_id = %s
        ORDER BY se.created_at DESC
        LIMIT 5
        """
        
        sample_data = await db_service.fetch_all(sample_query, (current_user.id,))
        
        return {
            "tableName": "sellout_entries2",
            "columns": columns,
            "sampleData": sample_data,
            "description": "Main table containing sales data entries from various resellers"
        }
        
    except Exception as e:
        logger.error(f"Error fetching database schema: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")