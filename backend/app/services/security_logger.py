"""
Security event logging service for comprehensive audit trails.
Logs all authentication and authorization events for security monitoring.
"""

import logging
import json
from typing import Optional, Dict, Any
from datetime import datetime
from supabase import create_client, Client
from app.utils.config import get_settings
from app.models.auth import SecurityEvent


class SecurityLogger:
    """
    Centralized security event logging for audit trails and monitoring.
    Logs to both application logs and database for comprehensive tracking.
    """
    
    def __init__(self):
        settings = get_settings()
        self.logger = logging.getLogger("security_audit")
        
        # Set up security logger with dedicated handler
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - SECURITY - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        
        # Database connection for security events
        if settings.environment == "development" or "placeholder" in settings.supabase_url:
            self.supabase = None
            self.dev_mode = True
        else:
            # Use anon client for security logging (no sensitive operations)
            self.supabase: Client = create_client(
                settings.supabase_url,
                settings.supabase_anon_key
            )
            self.dev_mode = False
    
    async def log_login_attempt(
        self, 
        email: str, 
        success: bool,
        user_id: Optional[str] = None,
        client_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        error_details: Optional[str] = None
    ):
        """Log login attempt with detailed context"""
        event = SecurityEvent(
            event_type="login_attempt",
            user_id=user_id,
            email=email,
            client_id=client_id,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            details={
                "error": error_details,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        await self._log_security_event(event)
    
    async def log_token_validation(
        self,
        user_id: Optional[str] = None,
        email: Optional[str] = None,
        client_id: Optional[str] = None,
        success: bool = True,
        token_version: Optional[str] = None,
        ip_address: Optional[str] = None,
        error_details: Optional[str] = None
    ):
        """Log token validation events"""
        event = SecurityEvent(
            event_type="token_validation",
            user_id=user_id,
            email=email,
            client_id=client_id,
            success=success,
            details={
                "token_version": token_version,
                "error": error_details,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        await self._log_security_event(event)
    
    async def log_authorization_check(
        self,
        user_id: str,
        email: str,
        client_id: Optional[str] = None,
        resource: Optional[str] = None,
        action: Optional[str] = None,
        success: bool = True,
        ip_address: Optional[str] = None,
        error_details: Optional[str] = None
    ):
        """Log authorization check events"""
        event = SecurityEvent(
            event_type="authorization_check",
            user_id=user_id,
            email=email,
            client_id=client_id,
            ip_address=ip_address,
            success=success,
            details={
                "resource": resource,
                "action": action,
                "error": error_details,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        await self._log_security_event(event)
    
    async def log_service_role_usage(
        self,
        operation: str,
        user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        warning: bool = True
    ):
        """Log service role usage (should be minimized)"""
        event = SecurityEvent(
            event_type="service_role_usage",
            user_id=user_id,
            success=True,
            details={
                "operation": operation,
                "warning": "Service role used - review for security",
                "details": details or {},
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        if warning:
            self.logger.warning(f"SERVICE ROLE USAGE: {operation} - {details}")
        
        await self._log_security_event(event)
    
    async def log_user_registration(
        self,
        email: str,
        user_id: Optional[str] = None,
        client_id: Optional[str] = None,
        success: bool = True,
        ip_address: Optional[str] = None,
        error_details: Optional[str] = None
    ):
        """Log user registration events"""
        event = SecurityEvent(
            event_type="user_registration",
            user_id=user_id,
            email=email,
            client_id=client_id,
            ip_address=ip_address,
            success=success,
            details={
                "error": error_details,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        await self._log_security_event(event)
    
    async def log_organization_access(
        self,
        user_id: str,
        email: str,
        client_id: str,
        organization_name: str,
        access_granted: bool,
        ip_address: Optional[str] = None,
        error_details: Optional[str] = None
    ):
        """Log organization access attempts"""
        event = SecurityEvent(
            event_type="organization_access",
            user_id=user_id,
            email=email,
            client_id=client_id,
            ip_address=ip_address,
            success=access_granted,
            details={
                "organization_name": organization_name,
                "error": error_details,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        await self._log_security_event(event)
    
    async def log_suspicious_activity(
        self,
        activity_type: str,
        user_id: Optional[str] = None,
        email: Optional[str] = None,
        client_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log suspicious security activities"""
        event = SecurityEvent(
            event_type="suspicious_activity",
            user_id=user_id,
            email=email,
            client_id=client_id,
            ip_address=ip_address,
            success=False,
            details={
                "activity_type": activity_type,
                "details": details or {},
                "severity": "high",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        self.logger.warning(f"SUSPICIOUS ACTIVITY: {activity_type} - User: {email} - Details: {details}")
        await self._log_security_event(event)
    
    async def _log_security_event(self, event: SecurityEvent):
        """Internal method to log security event to both logs and database"""
        try:
            # Always log to application logs
            log_message = (
                f"{event.event_type.upper()} - "
                f"User: {event.email or 'unknown'} - "
                f"Success: {event.success} - "
                f"Client: {event.client_id or 'none'} - "
                f"Details: {json.dumps(event.details)}"
            )
            
            if event.success:
                self.logger.info(log_message)
            else:
                self.logger.warning(log_message)
            
            # Store to database if available
            if not self.dev_mode and self.supabase:
                await self._store_security_event_to_db(event)
                
        except Exception as e:
            # Never fail on logging errors, but log the failure
            self.logger.error(f"Failed to log security event: {str(e)}")
    
    async def _store_security_event_to_db(self, event: SecurityEvent):
        """Store security event to database for audit trail"""
        try:
            # Create security_events table if it doesn't exist (could be done in migration)
            event_data = {
                "event_type": event.event_type,
                "user_id": event.user_id,
                "email": event.email,
                "client_id": event.client_id,
                "ip_address": event.ip_address,
                "user_agent": event.user_agent,
                "success": event.success,
                "details": event.details,
                "created_at": event.timestamp.isoformat()
            }
            
            # Store to security_events table (would need to be created in migration)
            # For now, we'll just log it as structured data
            self.logger.info(f"SECURITY_DB_EVENT: {json.dumps(event_data)}")
            
        except Exception as e:
            self.logger.error(f"Failed to store security event to database: {str(e)}")
    
    def get_client_info(self, request) -> Dict[str, Optional[str]]:
        """Extract client information from request for logging"""
        try:
            return {
                "ip_address": self._get_client_ip(request),
                "user_agent": request.headers.get("user-agent")
            }
        except Exception:
            return {"ip_address": None, "user_agent": None}
    
    def _get_client_ip(self, request) -> Optional[str]:
        """Extract client IP address from request"""
        try:
            # Check for forwarded headers (behind proxy/load balancer)
            forwarded_for = request.headers.get("x-forwarded-for")
            if forwarded_for:
                return forwarded_for.split(",")[0].strip()
            
            # Check other proxy headers
            real_ip = request.headers.get("x-real-ip")
            if real_ip:
                return real_ip.strip()
            
            # Fallback to direct client IP
            return getattr(request.client, "host", None)
            
        except Exception:
            return None


# Global security logger instance
security_logger = SecurityLogger()