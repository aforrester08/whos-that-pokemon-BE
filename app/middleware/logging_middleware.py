from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger = logging.getLogger(__name__)
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        logger.info(
            "Request processed",
            extra={
                "props": {
                    "method": request.method,
                    "url": str(request.url),
                    "process_time_ms": round(process_time * 1000, 2),
                    "client_host": request.client.host if request.client else None,
                    "status_code": response.status_code
                }
            }
        )
        
        return response