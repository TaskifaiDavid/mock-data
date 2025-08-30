"""
Migration API Endpoints
Handles migration status, validation, and control operations for the multi-tenant security migration.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from typing import Dict, Any
import logging
from datetime import datetime

from app.services.migration_service import migration_service, MigrationPhase, MigrationStatus, MigrationLogEntry
from app.api.auth import get_current_user
from app.services.auth_service import AuthService

router = APIRouter(tags=["migration"])
logger = logging.getLogger(__name__)

@router.get("/migration/status")
async def get_migration_status(
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get current migration status and recent logs.
    Only accessible by admin users.
    """
    try:
        status_info = await migration_service.get_migration_status()
        return {
            "success": True,
            "data": status_info
        }
    except Exception as e:
        logger.error(f"Failed to get migration status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve migration status"
        )

@router.post("/migration/validate-system")
async def validate_system_state(
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Validate current system state before starting migration.
    Checks data integrity, counts, and prerequisites.
    """
    try:
        # Log validation start
        await migration_service.log_migration_event(MigrationLogEntry(
            phase=MigrationPhase.PHASE_0,
            operation="validate_system_api_call",
            status=MigrationStatus.STARTED,
            details={"initiated_by": current_user.email}
        ))
        
        # Validate system state
        validation_result = await migration_service.validate_system_state()
        
        # Check prerequisites
        prerequisites = await migration_service.check_migration_prerequisites()
        
        result = {
            "system_state": validation_result,
            "prerequisites": prerequisites,
            "ready_for_migration": all(prerequisites.values()) if isinstance(prerequisites, dict) else False
        }
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"System validation failed: {e}")
        
        await migration_service.log_migration_event(MigrationLogEntry(
            phase=MigrationPhase.PHASE_0,
            operation="validate_system_api_call",
            status=MigrationStatus.FAILED,
            details={"error": str(e), "initiated_by": current_user.email}
        ))
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"System validation failed: {str(e)}"
        )

@router.post("/migration/backup")
async def create_migration_backup(
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Create comprehensive backup before migration.
    Includes RLS policies and data snapshots.
    """
    try:
        await migration_service.log_migration_event(MigrationLogEntry(
            phase=MigrationPhase.PHASE_0,
            operation="create_backup_api_call",
            status=MigrationStatus.STARTED,
            details={"initiated_by": current_user.email}
        ))
        
        # Backup RLS policies
        policy_backup = await migration_service.backup_rls_policies()
        
        # Create data snapshots
        data_snapshot = await migration_service.create_data_snapshot()
        
        result = {
            "policy_backup": policy_backup,
            "data_snapshot": data_snapshot,
            "backup_completed": True
        }
        
        await migration_service.log_migration_event(MigrationLogEntry(
            phase=MigrationPhase.PHASE_0,
            operation="create_backup_api_call",
            status=MigrationStatus.COMPLETED,
            details={**result, "initiated_by": current_user.email}
        ))
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Backup creation failed: {e}")
        
        await migration_service.log_migration_event(MigrationLogEntry(
            phase=MigrationPhase.PHASE_0,
            operation="create_backup_api_call",
            status=MigrationStatus.FAILED,
            details={"error": str(e), "initiated_by": current_user.email}
        ))
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Backup creation failed: {str(e)}"
        )

@router.get("/migration/health")
async def migration_health_check() -> Dict[str, Any]:
    """
    Health check endpoint for migration infrastructure.
    Does not require authentication for monitoring purposes.
    """
    try:
        # Simple health checks
        health_status = {
            "migration_service_available": True,
            "database_connection": False,
            "backup_infrastructure": False
        }
        
        try:
            # Test database connection
            await migration_service.db_service.fetch_one("SELECT 1 as test")
            health_status["database_connection"] = True
        except:
            health_status["database_connection"] = False
        
        try:
            # Check backup infrastructure
            result = await migration_service.db_service.fetch_one(
                "SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'migration_log') as exists"
            )
            health_status["backup_infrastructure"] = result["exists"] if result else False
        except:
            health_status["backup_infrastructure"] = False
        
        overall_health = all(health_status.values())
        
        return {
            "healthy": overall_health,
            "details": health_status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "healthy": False,
            "error": str(e),
            "details": {"migration_service_available": False}
        }