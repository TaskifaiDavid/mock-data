"""
Centralized logging configuration for the Data Cleaning Platform.
Provides environment-based logging levels and structured logging for monitoring.
"""

import logging
import sys
from typing import Optional
from datetime import datetime
from app.utils.config import get_settings


class StructuredLogger:
    """Enhanced logger with structured logging capabilities."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.settings = get_settings()
    
    def _log_with_context(self, level: int, message: str, **kwargs):
        """Log with additional context information."""
        extra_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "environment": self.settings.environment,
            **kwargs
        }
        
        # Add context to the message for structured logging
        if extra_data:
            self.logger.log(level, message, extra=extra_data)
        else:
            self.logger.log(level, message)
    
    def info(self, message: str, **kwargs):
        """Log info level message with context."""
        self._log_with_context(logging.INFO, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error level message with context."""
        self._log_with_context(logging.ERROR, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning level message with context."""
        self._log_with_context(logging.WARNING, message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug level message with context."""
        self._log_with_context(logging.DEBUG, message, **kwargs)
    
    def security_event(self, event_type: str, message: str, **kwargs):
        """Log security-related events with special formatting."""
        security_data = {
            "security_event": True,
            "event_type": event_type,
            **kwargs
        }
        self._log_with_context(logging.WARNING, f"SECURITY: {message}", **security_data)
    
    def performance_metric(self, operation: str, duration_ms: float, **kwargs):
        """Log performance metrics for monitoring."""
        perf_data = {
            "performance_metric": True,
            "operation": operation,
            "duration_ms": duration_ms,
            **kwargs
        }
        self._log_with_context(logging.INFO, f"PERF: {operation} took {duration_ms:.2f}ms", **perf_data)


def configure_application_logging():
    """Configure application-wide logging based on environment."""
    settings = get_settings()
    
    # Determine log level based on environment
    log_levels = {
        "development": logging.DEBUG,
        "staging": logging.INFO, 
        "production": logging.WARNING
    }
    
    log_level = log_levels.get(settings.environment, logging.INFO)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler for production
    if settings.environment == "production":
        file_handler = logging.FileHandler('app.log')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(file_handler)
        
        # Separate error log file
        error_handler = logging.FileHandler('errors.log')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(error_handler)
    
    # Configure third-party loggers to reduce noise
    external_loggers = [
        'uvicorn', 'fastapi', 'httpcore', 'httpx', 
        'supabase', 'openai', 'langchain'
    ]
    
    for logger_name in external_loggers:
        external_logger = logging.getLogger(logger_name)
        if settings.environment == "production":
            external_logger.setLevel(logging.WARNING)
        else:
            external_logger.setLevel(logging.INFO)
    
    # Log configuration completion
    app_logger = StructuredLogger(__name__)
    app_logger.info(
        "Logging configured successfully",
        environment=settings.environment,
        log_level=logging.getLevelName(log_level)
    )


def get_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance for the given name."""
    return StructuredLogger(name)


# Performance monitoring decorator
def log_performance(operation_name: str):
    """Decorator to log performance metrics for functions."""
    import functools
    import time
    
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            logger = get_logger(f"{func.__module__}.{func.__name__}")
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                logger.performance_metric(
                    operation_name,
                    duration_ms,
                    function_name=func.__name__
                )
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger.error(
                    f"Function {func.__name__} failed after {duration_ms:.2f}ms",
                    error_type=type(e).__name__,
                    error_message=str(e)
                )
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            logger = get_logger(f"{func.__module__}.{func.__name__}")
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                logger.performance_metric(
                    operation_name,
                    duration_ms,
                    function_name=func.__name__
                )
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger.error(
                    f"Function {func.__name__} failed after {duration_ms:.2f}ms",
                    error_type=type(e).__name__,
                    error_message=str(e)
                )
                raise
        
        # Return appropriate wrapper based on function type
        if hasattr(func, '__code__') and 'async' in str(func.__code__):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator