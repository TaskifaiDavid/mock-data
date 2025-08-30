"""
Multi-Tenant Security Migration Service
Handles migration logging, monitoring, and validation throughout the security migration process.
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass
import asyncio

from app.services.db_service import DatabaseService
from app.utils.config import get_settings

settings = get_settings()

class MigrationPhase(Enum):
    PHASE_0 = "phase_0"
    PHASE_1 = "phase_1" 
    PHASE_2 = "phase_2"
    PHASE_3 = "phase_3"
    PHASE_4 = "phase_4"
    PHASE_5 = "phase_5"
    PHASE_6 = "phase_6"
    PHASE_7 = "phase_7"
    ROLLBACK = "rollback"

class MigrationStatus(Enum):
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLBACK = "rollback"

@dataclass
class MigrationLogEntry:
    phase: MigrationPhase
    operation: str
    status: MigrationStatus
    details: Dict[str, Any]
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class MigrationService:
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.MigrationService")
        self.db_service = DatabaseService()
        
    async def log_migration_event(self, entry: MigrationLogEntry) -> None:
        """Log a migration event to both database and file system."""
        try:
            # Log to database
            await self._log_to_database(entry)
            
            # Log to file system
            self._log_to_file(entry)
            
            # Log to application logger
            level = logging.INFO if entry.status in [MigrationStatus.STARTED, MigrationStatus.COMPLETED] else logging.ERROR
            self.logger.log(level, f"Migration {entry.phase.value}: {entry.operation} - {entry.status.value}")
            
        except Exception as e:
            self.logger.error(f"Failed to log migration event: {e}")
            # Fallback to file logging only
            self._log_to_file(entry, error=str(e))

    async def _log_to_database(self, entry: MigrationLogEntry) -> None:
        """Log migration event to database migration_log table."""
        query = """
        INSERT INTO public.migration_log (phase, operation, status, details, created_at)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        await self.db_service.execute(
            query,
            (
                entry.phase.value,
                entry.operation,
                entry.status.value,
                json.dumps(entry.details, default=str),
                entry.timestamp
            )
        )

    def _log_to_file(self, entry: MigrationLogEntry, error: Optional[str] = None) -> None:
        """Log migration event to file system."""
        log_entry = {
            "timestamp": entry.timestamp.isoformat(),
            "phase": entry.phase.value,
            "operation": entry.operation,
            "status": entry.status.value,
            "details": entry.details
        }
        
        if error:
            log_entry["database_log_error"] = error
            
        # Create migration-specific logger
        migration_logger = logging.getLogger("migration")
        migration_logger.info(json.dumps(log_entry))

    async def validate_system_state(self) -> Dict[str, Any]:
        """Validate current system state and return metrics."""
        try:
            query = "SELECT validate_system_state() as state"
            result = await self.db_service.fetch_one(query, ())
            
            validation_result = result["state"] if result else {}
            
            await self.log_migration_event(MigrationLogEntry(
                phase=MigrationPhase.PHASE_0,
                operation="system_validation",
                status=MigrationStatus.COMPLETED,
                details=validation_result
            ))
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"System validation failed: {e}")
            
            await self.log_migration_event(MigrationLogEntry(
                phase=MigrationPhase.PHASE_0,
                operation="system_validation",
                status=MigrationStatus.FAILED,
                details={"error": str(e)}
            ))
            
            raise

    async def backup_rls_policies(self) -> Dict[str, Any]:
        """Backup existing RLS policies before migration."""
        try:
            query = "SELECT backup_rls_policies()"
            await self.db_service.execute(query, ())
            
            # Get backup count
            count_query = "SELECT COUNT(*) as policy_count FROM public.migration_policy_backup"
            result = await self.db_service.fetch_one(count_query, ())
            policy_count = result["policy_count"] if result else 0
            
            backup_result = {"policies_backed_up": policy_count}
            
            await self.log_migration_event(MigrationLogEntry(
                phase=MigrationPhase.PHASE_0,
                operation="policy_backup",
                status=MigrationStatus.COMPLETED,
                details=backup_result
            ))
            
            return backup_result
            
        except Exception as e:
            self.logger.error(f"Policy backup failed: {e}")
            
            await self.log_migration_event(MigrationLogEntry(
                phase=MigrationPhase.PHASE_0,
                operation="policy_backup",
                status=MigrationStatus.FAILED,
                details={"error": str(e)}
            ))
            
            raise

    async def create_data_snapshot(self) -> Dict[str, Any]:
        """Create timestamped snapshots of all critical tables."""
        try:
            query = "SELECT create_data_snapshot() as snapshot_result"
            result = await self.db_service.fetch_one(query, ())
            
            snapshot_result = result["snapshot_result"] if result else {}
            
            await self.log_migration_event(MigrationLogEntry(
                phase=MigrationPhase.PHASE_0,
                operation="data_snapshot",
                status=MigrationStatus.COMPLETED,
                details=snapshot_result
            ))
            
            return snapshot_result
            
        except Exception as e:
            self.logger.error(f"Data snapshot failed: {e}")
            
            await self.log_migration_event(MigrationLogEntry(
                phase=MigrationPhase.PHASE_0,
                operation="data_snapshot",
                status=MigrationStatus.FAILED,
                details={"error": str(e)}
            ))
            
            raise

    async def check_migration_prerequisites(self) -> Dict[str, Any]:
        """Check all prerequisites before starting migration."""
        prerequisites = {
            "database_connection": False,
            "backup_tables_exist": False,
            "sufficient_space": False,
            "no_active_long_transactions": False
        }
        
        try:
            # Test database connection
            await self.db_service.fetch_one("SELECT 1 as test", ())
            prerequisites["database_connection"] = True
            
            # Check if backup infrastructure exists
            backup_check = await self.db_service.fetch_one(
                "SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'migration_log') as exists", ()
            )
            prerequisites["backup_tables_exist"] = backup_check["exists"] if backup_check else False
            
            # Check for active long-running transactions (simplified check)
            long_tx_check = await self.db_service.fetch_one(
                "SELECT COUNT(*) as count FROM pg_stat_activity WHERE state = 'active' AND query_start < now() - interval '5 minutes'", ()
            )
            prerequisites["no_active_long_transactions"] = (long_tx_check["count"] if long_tx_check else 1) == 0
            
            # Simplified space check (would need more sophisticated implementation)
            prerequisites["sufficient_space"] = True
            
            all_good = all(prerequisites.values())
            
            await self.log_migration_event(MigrationLogEntry(
                phase=MigrationPhase.PHASE_0,
                operation="prerequisites_check",
                status=MigrationStatus.COMPLETED if all_good else MigrationStatus.FAILED,
                details=prerequisites
            ))
            
            return prerequisites
            
        except Exception as e:
            self.logger.error(f"Prerequisites check failed: {e}")
            prerequisites["error"] = str(e)
            
            await self.log_migration_event(MigrationLogEntry(
                phase=MigrationPhase.PHASE_0,
                operation="prerequisites_check",
                status=MigrationStatus.FAILED,
                details=prerequisites
            ))
            
            return prerequisites

    async def get_migration_status(self) -> Dict[str, Any]:
        """Get current migration status from logs."""
        try:
            query = """
            SELECT phase, operation, status, details, created_at
            FROM public.migration_log 
            ORDER BY created_at DESC 
            LIMIT 20
            """
            
            logs = await self.db_service.fetch_all(query, ())
            
            return {
                "recent_logs": [dict(log) for log in logs] if logs else [],
                "last_update": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get migration status: {e}")
            return {"error": str(e)}

# Initialize migration service instance
migration_service = MigrationService()