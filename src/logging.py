import asyncio
import logging

error_logger = logging.getLogger("server.errors")
logger = logging.getLogger("server")

# Utility functions for enhanced error logging
def log_error_with_context(error: Exception, context: dict = None, include_traceback: bool = True):
    """Log an error with additional context and optional traceback."""
    error_id = f"ERR_{asyncio.get_event_loop().time() if asyncio.get_event_loop() else 'sync'}"

    context_str = ""
    if context:
        context_items = [f"{k}={v}" for k, v in context.items()]
        context_str = f" | Context: {', '.join(context_items)}"

    error_msg = f"[{error_id}] {str(error)}{context_str}"

    if include_traceback:
        error_logger.error(error_msg, exc_info=True)
        logger.error(f"{error_msg} - See error log for full traceback")
    else:
        error_logger.error(error_msg)
        logger.error(error_msg)

    return error_id

def log_api_error(service_name: str, operation: str, error: Exception, request_data: dict = None):
    """Log API-related errors with service and operation context."""
    context = {
        "service": service_name,
        "operation": operation,
        "error_type": type(error).__name__
    }

    if request_data:
        # Sanitize sensitive data
        safe_request = {k: v for k, v in request_data.items() if not any(sensitive in k.lower() for sensitive in ['key', 'token', 'password'])}
        context["request_data"] = safe_request

    error_id = log_error_with_context(error, context)
    logger.warning(f"API call failed: {service_name}.{operation} - Error ID: {error_id}")

    return error_id

def log_json_error(operation: str, raw_content: str, error: Exception):
    """Log JSON parsing errors with content preview."""
    content_preview = raw_content[:200] + "..." if len(raw_content) > 200 else raw_content
    context = {
        "operation": operation,
        "content_length": len(raw_content),
        "content_preview": content_preview.replace('\n', '\\n')
    }

    error_id = log_error_with_context(error, context, include_traceback=False)
    logger.warning(f"JSON parsing failed in {operation} - Error ID: {error_id}")

    return error_id