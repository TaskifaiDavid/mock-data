from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
from app.services.auth_service import get_current_user
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
        from app.services.db_service import DatabaseService
        
        db_service = DatabaseService()
        
        # Query dashboard configurations
        query = """
        SELECT 
            id,
            dashboard_name,
            dashboard_type,
            dashboard_url,
            authentication_method,
            authentication_config,
            permissions,
            is_active,
            created_at,
            updated_at
        FROM dashboard_configs 
        WHERE user_id = %s 
        ORDER BY created_at DESC
        """
        
        configs = await db_service.fetch_all(query, (current_user.id,))
        
        # Format configs for frontend
        formatted_configs = []
        for config in configs:
            formatted_config = {
                "id": config["id"],
                "dashboardName": config["dashboard_name"],
                "dashboardType": config["dashboard_type"],
                "dashboardUrl": config["dashboard_url"],
                "authenticationMethod": config["authentication_method"],
                "authenticationConfig": config["authentication_config"] or {},
                "permissions": config["permissions"] or [],
                "isActive": config["is_active"],
                "createdAt": config["created_at"].isoformat() if hasattr(config["created_at"], 'isoformat') else str(config["created_at"]),
                "updatedAt": config["updated_at"].isoformat() if hasattr(config["updated_at"], 'isoformat') else str(config["updated_at"])
            }
            formatted_configs.append(formatted_config)
        
        return {
            "configs": formatted_configs,
            "total": len(formatted_configs)
        }
        
    except Exception as e:
        logger.error(f"Error fetching dashboard configs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/configs")
async def create_dashboard_config(
    config: DashboardConfig,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Create a new dashboard configuration
    """
    try:
        from app.services.db_service import DatabaseService
        
        db_service = DatabaseService()
        
        # Insert new dashboard config
        query = """
        INSERT INTO dashboard_configs 
        (user_id, dashboard_name, dashboard_type, dashboard_url, 
         authentication_method, authentication_config, permissions, 
         is_active, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id, created_at, updated_at
        """
        
        now = datetime.now()
        result = await db_service.execute(
            query,
            (
                current_user.id,
                config.dashboardName,
                config.dashboardType,
                str(config.dashboardUrl),
                config.authenticationMethod,
                config.authenticationConfig,
                config.permissions,
                config.isActive,
                now,
                now
            )
        )
        
        if not result:
            logger.error("Database insert returned no result")
            raise HTTPException(status_code=500, detail="Failed to create dashboard configuration")
        
        # Return the created config
        created_config = {
            "id": result["id"],
            "dashboardName": config.dashboardName,
            "dashboardType": config.dashboardType,
            "dashboardUrl": str(config.dashboardUrl),
            "authenticationMethod": config.authenticationMethod,
            "authenticationConfig": config.authenticationConfig or {},
            "permissions": config.permissions or [],
            "isActive": config.isActive,
            "createdAt": result["created_at"] if isinstance(result["created_at"], str) else result["created_at"].isoformat(),
            "updatedAt": result["updated_at"] if isinstance(result["updated_at"], str) else result["updated_at"].isoformat()
        }
        
        logger.info(f"Created dashboard config {result['id']} for user {current_user.email}")
        
        return {
            "success": True,
            "config": created_config,
            "message": "Dashboard configuration created successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating dashboard config: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

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
        from app.services.db_service import DatabaseService
        
        db_service = DatabaseService()
        
        # Check if config exists and belongs to user
        check_query = """
        SELECT id FROM dashboard_configs 
        WHERE id = %s AND user_id = %s
        """
        
        existing = await db_service.fetch_one(check_query, (config_id, current_user.id))
        if not existing:
            raise HTTPException(status_code=404, detail="Dashboard configuration not found")
        
        # Update dashboard config
        update_query = """
        UPDATE dashboard_configs 
        SET 
            dashboard_name = %s,
            dashboard_type = %s,
            dashboard_url = %s,
            authentication_method = %s,
            authentication_config = %s,
            permissions = %s,
            is_active = %s,
            updated_at = %s
        WHERE id = %s AND user_id = %s
        RETURNING updated_at
        """
        
        now = datetime.now()
        result = await db_service.fetch_one(
            update_query,
            (
                config.dashboardName,
                config.dashboardType,
                str(config.dashboardUrl),
                config.authenticationMethod,
                config.authenticationConfig,
                config.permissions,
                config.isActive,
                now,
                config_id,
                current_user.id
            )
        )
        
        logger.info(f"Updated dashboard config {config_id} for user {current_user.email}")
        
        return {
            "success": True,
            "message": "Dashboard configuration updated successfully",
            "updatedAt": result["updated_at"].isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating dashboard config: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/configs/{config_id}")
async def delete_dashboard_config(
    config_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Delete a dashboard configuration
    """
    try:
        from app.services.db_service import DatabaseService
        
        db_service = DatabaseService()
        
        # Check if config exists and belongs to user, then delete
        delete_query = """
        DELETE FROM dashboard_configs 
        WHERE id = %s AND user_id = %s
        RETURNING id
        """
        
        result = await db_service.fetch_one(delete_query, (config_id, current_user.id))
        if not result:
            raise HTTPException(status_code=404, detail="Dashboard configuration not found")
        
        logger.info(f"Deleted dashboard config {config_id} for user {current_user.email}")
        
        return {
            "success": True,
            "message": "Dashboard configuration deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting dashboard config: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/configs/{config_id}")
async def get_dashboard_config(
    config_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get a specific dashboard configuration
    """
    try:
        from app.services.db_service import DatabaseService
        
        db_service = DatabaseService()
        
        # Query specific dashboard configuration
        query = """
        SELECT 
            id,
            dashboard_name,
            dashboard_type,
            dashboard_url,
            authentication_method,
            authentication_config,
            permissions,
            is_active,
            created_at,
            updated_at
        FROM dashboard_configs 
        WHERE id = %s AND user_id = %s
        """
        
        config = await db_service.fetch_one(query, (config_id, current_user.id))
        if not config:
            raise HTTPException(status_code=404, detail="Dashboard configuration not found")
        
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
            "createdAt": config["created_at"].isoformat() if hasattr(config["created_at"], 'isoformat') else str(config["created_at"]),
            "updatedAt": config["updated_at"].isoformat() if hasattr(config["updated_at"], 'isoformat') else str(config["updated_at"])
        }
        
        return formatted_config
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching dashboard config: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")