"""
Performance middleware to optimize responses
"""

import time
import gzip
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import Response as FastAPIResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)


class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware to optimize performance"""
    
    def __init__(self, app, min_compress_size: int = 1000):
        super().__init__(app)
        self.min_compress_size = min_compress_size
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Measure response time
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate response time
        process_time = time.time() - start_time
        
        # Add performance headers
        response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))
        response.headers["X-Cache-Status"] = "MISS"  # Can be improved with cache headers
        
        # Apply compression if needed
        if self._should_compress(response):
            response = await self._compress_response(response)
        
        # Performance log
        logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
        
        return response
    
    def _should_compress(self, response: Response) -> bool:
        """Determine if response should be compressed"""
        # Only compress successful responses
        if response.status_code not in [200, 201]:
            return False
        
        # Check content-type
        content_type = response.headers.get("content-type", "")
        if not any(ct in content_type for ct in ["application/json", "text/", "application/xml"]):
            return False
        
        # Check size
        content_length = response.headers.get("content-length")
        if content_length and int(content_length) < self.min_compress_size:
            return False
        
        return True
    
    async def _compress_response(self, response: Response) -> Response:
        """Compress response using gzip"""
        try:
            # Read content
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            
            # Compress
            compressed_body = gzip.compress(body)
            
            # Create new response
            compressed_response = FastAPIResponse(
                content=compressed_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
            
            # Add compression headers
            compressed_response.headers["Content-Encoding"] = "gzip"
            compressed_response.headers["Content-Length"] = str(len(compressed_body))
            
            return compressed_response
            
        except Exception as e:
            logger.warning(f"Error compressing response: {e}")
            return response


class CacheHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add cache headers"""
    
    def __init__(self, app, cache_ttl: int = 3600):
        super().__init__(app)
        self.cache_ttl = cache_ttl
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Only add cache headers for successful responses
        if response.status_code == 200:
            # Public cache by default
            response.headers["Cache-Control"] = f"public, max-age={self.cache_ttl}"
            
            # ETag based on timestamp (can be improved)
            etag = f'"{int(time.time())}"'
            response.headers["ETag"] = etag
            
            # Check If-None-Match
            if_none_match = request.headers.get("If-None-Match")
            if if_none_match == etag:
                return Response(status_code=304)
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for detailed request logging"""
    
    def __init__(self, app, log_level: str = "INFO"):
        super().__init__(app)
        self.log_level = log_level.upper()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url.path}")
        
        # Process request
        response = await call_next(request)
        
        # Calculate time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"Response: {response.status_code} - "
            f"{process_time:.3f}s - "
            f"Size: {response.headers.get('content-length', 'unknown')} bytes"
        )
        
        return response
