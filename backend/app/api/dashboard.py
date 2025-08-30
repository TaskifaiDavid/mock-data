from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, HttpUrl, validator
from typing import List, Dict, Any, Optional
import logging
import re
from datetime import datetime
from app.api.auth import get_current_user
from app.models.auth import UserInDB
from app.utils.exceptions import AppException

logger = logging.getLogger(__name__)

router = APIRouter()

class DashboardConfig(BaseModel):
    dashboardName: str
    dashboardType: str
    dashboardUrl: HttpUrl
    authenticationMethod: str = "none"
    authenticationConfig: Optional[Dict[str, Any]] = {}
    permissions: Optional[List[str]] = []
    isActive: bool = True
    
    @validator('dashboardName')
    def validate_dashboard_name(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError('Dashboard name must be at least 3 characters long')
        if len(v) > 100:
            raise ValueError('Dashboard name cannot exceed 100 characters')
        return v.strip()
    
    @validator('dashboardType')
    def validate_dashboard_type(cls, v):
        allowed_types = ['looker', 'google_analytics', 'tableau', 'power_bi', 'custom']
        if v not in allowed_types:
            raise ValueError(f'Dashboard type must be one of: {", ".join(allowed_types)}')
        return v
    
    @validator('dashboardUrl')
    def validate_dashboard_url(cls, v):
        url_str = str(v)
        
        # Basic URL validation
        if not url_str.startswith(('http://', 'https://')):
            raise ValueError('Dashboard URL must start with http:// or https://')
        
        # Google Looker Studio specific validation
        if 'lookerstudio.google.com' in url_str:
            if '/reporting/' not in url_str and '/embed/reporting/' not in url_str:
                raise ValueError('Google Looker Studio URL must contain /reporting/ or /embed/reporting/')
                
        return v

class DashboardConfigResponse(BaseModel):
    id: str
    dashboardName: str
    dashboardType: str
    dashboardUrl: str
    authenticationMethod: str
    authenticationConfig: Dict[str, Any]
    permissions: List[str]
    isActive: bool
    createdAt: str
    updatedAt: str

@router.get("/configs")
async def get_dashboard_configs(
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get all dashboard configurations for the current user
    """
    try:
        # Validate user context first
        if not current_user or not current_user.id:
            logger.error("Invalid user context in get_dashboard_configs")
            raise HTTPException(status_code=401, detail="Invalid user authentication")
        
        logger.info(f"Getting dashboard configs for user {current_user.email}")
        
        from app.services.db_service import DatabaseService
        
        # Initialize database service with user authentication
        db_service = DatabaseService()
        
        # Check if we're in development mode
        if hasattr(db_service, 'dev_mode') and db_service.dev_mode:
            logger.info("Using development mode for dashboard configs")
            # In dev mode, use persistent global mock storage
            from app.services.db_service import _mock_dashboard_configs
            
            # Get user's dashboards from mock storage
            user_dashboards = []
            for dashboard_id, dashboard in _mock_dashboard_configs.items():
                if dashboard.get('user_id') == current_user.id:
                    formatted_config = {
                        "id": dashboard_id,
                        "dashboardName": dashboard["dashboard_name"],
                        "dashboardType": dashboard["dashboard_type"], 
                        "dashboardUrl": dashboard["dashboard_url"],
                        "authenticationMethod": dashboard.get("authentication_method", "none"),
                        "authenticationConfig": dashboard.get("authentication_config", {}),
                        "permissions": dashboard.get("permissions", []),
                        "isActive": dashboard.get("is_active", True),
                        "createdAt": dashboard.get("created_at"),
                        "updatedAt": dashboard.get("updated_at")
                    }
                    user_dashboards.append(formatted_config)
            
            logger.info(f"Fetched {len(user_dashboards)} dashboard configs for user {current_user.email} (dev mode)")
            return {
                "configs": user_dashboards,
                "total": len(user_dashboards)
            }
        
        # Production mode - query Supabase database
        try:
            # Use service key to bypass RLS in development mode with mock auth
            supabase_client = db_service.service_supabase if hasattr(db_service, 'service_supabase') else db_service.supabase
            result = supabase_client.table("dashboard_configs").select("*").eq("user_id", current_user.id).order("created_at", desc=True).execute()
            
            # Format configs for frontend
            formatted_configs = []
            for config in result.data or []:
                formatted_config = {
                    "id": config["id"],
                    "dashboardName": config["dashboard_name"],
                    "dashboardType": config["dashboard_type"],
                    "dashboardUrl": config["dashboard_url"],
                    "authenticationMethod": config.get("authentication_method", "none"),
                    "authenticationConfig": config.get("authentication_config", {}),
                    "permissions": config.get("permissions", []),
                    "isActive": config.get("is_active", True),
                    "createdAt": config["created_at"],
                    "updatedAt": config["updated_at"]
                }
                formatted_configs.append(formatted_config)
            
            logger.info(f"Fetched {len(formatted_configs)} dashboard configs for user {current_user.email}")
            
            return {
                "configs": formatted_configs,
                "total": len(formatted_configs)
            }
        
        except Exception as db_error:
            logger.error(f"Database error: {str(db_error)}")
            # Return empty list with warning instead of failing
            return {
                "configs": [],
                "total": 0,
                "warning": "Unable to fetch dashboards from database"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching dashboard configs for user {current_user.id}: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        
        # Provide more specific error messages
        if "permission denied" in str(e).lower():
            raise HTTPException(status_code=403, detail="Insufficient permissions to access dashboard configurations")
        elif "connection" in str(e).lower() or "timeout" in str(e).lower():
            raise HTTPException(status_code=503, detail="Database connection issue. Please try again.")
        elif "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Dashboard configurations not found")
        else:
            raise HTTPException(status_code=500, detail="Failed to fetch dashboard configurations")

@router.post("/configs") 
async def create_dashboard_config(
    config: DashboardConfig,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Create a new dashboard configuration
    """
    try:
        # Validate user context first
        if not current_user or not current_user.id:
            logger.error("Invalid user context in create_dashboard_config")
            raise HTTPException(status_code=401, detail="Invalid user authentication")
        
        logger.info(f"Creating dashboard config for user {current_user.email}: {config.dashboardName}")
        
        from app.services.db_service import DatabaseService
        import uuid
        
        # Initialize database service
        db_service = DatabaseService()
        now = datetime.now()
        dashboard_id = str(uuid.uuid4())
        
        # Prepare dashboard data
        dashboard_data = {
            "id": dashboard_id,
            "user_id": current_user.id,
            "dashboard_name": config.dashboardName,
            "dashboard_type": config.dashboardType,
            "dashboard_url": str(config.dashboardUrl),
            "authentication_method": config.authenticationMethod,
            "authentication_config": config.authenticationConfig or {},
            "permissions": config.permissions or [],
            "is_active": config.isActive,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        }
        
        # Check if we're in development mode
        if hasattr(db_service, 'dev_mode') and db_service.dev_mode:
            logger.info("Using development mode for dashboard creation")
            # In dev mode, use persistent global mock storage
            from app.services.db_service import _mock_dashboard_configs
            
            # Store in mock storage
            _mock_dashboard_configs[dashboard_id] = dashboard_data
            logger.info(f"Created dashboard config {dashboard_id} for user {current_user.email} (dev mode)")
        else:
            # Production mode - insert into Supabase database
            try:
                # Use service key to bypass RLS in development mode with mock auth
                supabase_client = db_service.service_supabase if hasattr(db_service, 'service_supabase') else db_service.supabase
                result = supabase_client.table("dashboard_configs").insert(dashboard_data).execute()
                
                if not result.data:
                    raise HTTPException(status_code=500, detail="Failed to create dashboard configuration")
                
                logger.info(f"Created dashboard config {dashboard_id} for user {current_user.email}")
            except Exception as db_error:
                logger.error(f"Database error creating dashboard: {str(db_error)}")
                raise HTTPException(status_code=500, detail=f"Database error: {str(db_error)}")
        
        # Return the created config
        created_config = {
            "id": dashboard_id,
            "dashboardName": config.dashboardName,
            "dashboardType": config.dashboardType,
            "dashboardUrl": str(config.dashboardUrl),
            "authenticationMethod": config.authenticationMethod,
            "authenticationConfig": config.authenticationConfig or {},
            "permissions": config.permissions or [],
            "isActive": config.isActive,
            "createdAt": now.isoformat(),
            "updatedAt": now.isoformat()
        }
        
        return {
            "success": True,
            "config": created_config,
            "message": "Dashboard configuration created successfully"
        }
        
    except HTTPException:
        raise
    except ValueError as e:
        # Handle Pydantic validation errors
        logger.warning(f"Validation error creating dashboard config for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=422, detail=f"Validation error: {str(e)}")
    except Exception as e:
        logger.error(f"Error creating dashboard config for user {current_user.id}: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        
        # Provide more specific error messages
        if "duplicate" in str(e).lower() or "unique constraint" in str(e).lower():
            raise HTTPException(status_code=409, detail="A dashboard with this name already exists")
        elif "permission denied" in str(e).lower():
            raise HTTPException(status_code=403, detail="Insufficient permissions to create dashboard")
        elif "connection" in str(e).lower() or "timeout" in str(e).lower():
            raise HTTPException(status_code=503, detail="Database connection issue. Please try again.")
        else:
            raise HTTPException(status_code=500, detail="Failed to create dashboard configuration")

@router.put("/configs/{config_id}")
async def update_dashboard_config(
    config_id: str,
    config: DashboardConfig,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Update an existing dashboard configuration
    """
    try:
        # Validate user context first
        if not current_user or not current_user.id:
            logger.error("Invalid user context in update_dashboard_config")
            raise HTTPException(status_code=401, detail="Invalid user authentication")
        
        logger.info(f"Updating dashboard config {config_id} for user {current_user.email}")
        
        from app.services.db_service import DatabaseService
        
        # Initialize database service
        db_service = DatabaseService()
        now = datetime.now()
        
        # Prepare update data
        update_data = {
            "dashboard_name": config.dashboardName,
            "dashboard_type": config.dashboardType,
            "dashboard_url": str(config.dashboardUrl),
            "authentication_method": config.authenticationMethod,
            "authentication_config": config.authenticationConfig or {},
            "permissions": config.permissions or [],
            "is_active": config.isActive,
            "updated_at": now.isoformat()
        }
        
        # Check if we're in development mode
        if hasattr(db_service, 'dev_mode') and db_service.dev_mode:
            logger.info("Using development mode for dashboard update")
            from app.services.db_service import _mock_dashboard_configs
            
            # Check if dashboard exists and belongs to user
            if config_id not in _mock_dashboard_configs:
                raise HTTPException(status_code=404, detail="Dashboard configuration not found")
            
            existing_dashboard = _mock_dashboard_configs[config_id]
            if existing_dashboard.get('user_id') != current_user.id:
                raise HTTPException(status_code=403, detail="Access denied")
            
            # Update the dashboard
            _mock_dashboard_configs[config_id].update(update_data)
            logger.info(f"Updated dashboard config {config_id} for user {current_user.email} (dev mode)")
        else:
            # Production mode - update in Supabase database
            try:
                # Use service key to bypass RLS in development mode with mock auth
                supabase_client = db_service.service_supabase if hasattr(db_service, 'service_supabase') else db_service.supabase
                result = supabase_client.table("dashboard_configs").update(update_data).eq("id", config_id).eq("user_id", current_user.id).execute()
                
                if not result.data:
                    raise HTTPException(status_code=404, detail="Dashboard configuration not found")
                
                logger.info(f"Updated dashboard config {config_id} for user {current_user.email}")
            except Exception as db_error:
                logger.error(f"Database error updating dashboard: {str(db_error)}")
                raise HTTPException(status_code=500, detail=f"Database error: {str(db_error)}")
        
        return {
            "success": True,
            "message": "Dashboard configuration updated successfully",
            "updatedAt": now.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating dashboard config {config_id} for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update dashboard configuration")

@router.delete("/configs/{config_id}")
async def delete_dashboard_config(
    config_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Delete a dashboard configuration
    """
    try:
        # Validate user context first
        if not current_user or not current_user.id:
            logger.error("Invalid user context in delete_dashboard_config")
            raise HTTPException(status_code=401, detail="Invalid user authentication")
        
        logger.info(f"Deleting dashboard config {config_id} for user {current_user.email}")
        
        from app.services.db_service import DatabaseService
        
        # Initialize database service
        db_service = DatabaseService()
        
        # Check if we're in development mode
        if hasattr(db_service, 'dev_mode') and db_service.dev_mode:
            logger.info("Using development mode for dashboard deletion")
            from app.services.db_service import _mock_dashboard_configs
            
            # Check if dashboard exists and belongs to user
            if config_id not in _mock_dashboard_configs:
                raise HTTPException(status_code=404, detail="Dashboard configuration not found")
            
            existing_dashboard = _mock_dashboard_configs[config_id]
            if existing_dashboard.get('user_id') != current_user.id:
                raise HTTPException(status_code=403, detail="Access denied")
            
            # Delete the dashboard
            del _mock_dashboard_configs[config_id]
            logger.info(f"Deleted dashboard config {config_id} for user {current_user.email} (dev mode)")
        else:
            # Production mode - delete from Supabase database
            try:
                # Use service key to bypass RLS in development mode with mock auth
                supabase_client = db_service.service_supabase if hasattr(db_service, 'service_supabase') else db_service.supabase
                result = supabase_client.table("dashboard_configs").delete().eq("id", config_id).eq("user_id", current_user.id).execute()
                
                if not result.data:
                    raise HTTPException(status_code=404, detail="Dashboard configuration not found")
                
                logger.info(f"Deleted dashboard config {config_id} for user {current_user.email}")
            except Exception as db_error:
                logger.error(f"Database error deleting dashboard: {str(db_error)}")
                raise HTTPException(status_code=500, detail=f"Database error: {str(db_error)}")
        
        return {
            "success": True,
            "message": "Dashboard configuration deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting dashboard config {config_id} for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete dashboard configuration")

@router.get("/configs/{config_id}")
async def get_dashboard_config(
    config_id: str,
    current_user: UserInDB = Depends(get_current_user),
    authorization: Optional[str] = Header(None)
):
    """
    Get a specific dashboard configuration
    """
    try:
        from app.services.db_service import DatabaseService
        
        # Validate user context first
        if not current_user or not current_user.id:
            logger.error("Invalid user context in get_dashboard_config")
            raise HTTPException(status_code=401, detail="Invalid user authentication")
        
        # Extract token from authorization header for user-scoped client
        token = None
        if authorization and authorization.startswith("Bearer "):
            try:
                token = authorization.split(" ")[1]
            except IndexError:
                logger.error("Malformed authorization header")
                raise HTTPException(status_code=401, detail="Invalid authorization header")
        
        if not token:
            logger.error("No user token provided for dashboard config retrieval")
            raise HTTPException(status_code=401, detail="User token required")
            
        db_service = DatabaseService(user_token=token)
        
        # Verify database service is properly configured
        if hasattr(db_service, 'dev_mode') and db_service.dev_mode:
            logger.info(f"Using development mode for dashboard configs for user {current_user.id}")
        elif not db_service.user_token:
            logger.error("DatabaseService not initialized with user token in production mode")
            raise HTTPException(status_code=500, detail="Database service configuration error")
        
        # Verify supabase client exists
        if not db_service.supabase:
            logger.error("DatabaseService supabase client not initialized")
            raise HTTPException(status_code=500, detail="Database service not available")
        
        # Query specific dashboard configuration with RLS enforcement
        # Use service key to bypass RLS in development mode with mock auth
        supabase_client = db_service.service_supabase if hasattr(db_service, 'service_supabase') else db_service.supabase
        result = supabase_client.table("dashboard_configs").select("*").eq("id", config_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Dashboard configuration not found")
        
        config = result.data[0]
        
        # Format config for frontend
        formatted_config = {
            "id": config["id"],
            "dashboardName": config["dashboard_name"],
            "dashboardType": config["dashboard_type"],
            "dashboardUrl": config["dashboard_url"],
            "authenticationMethod": config["authentication_method"],
            "authenticationConfig": config["authentication_config"] or {},
            "permissions": config["permissions"] or [],
            "isActive": config["is_active"],
            "createdAt": config["created_at"],
            "updatedAt": config["updated_at"]
        }
        
        return formatted_config
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching dashboard config {config_id} for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch dashboard configuration")