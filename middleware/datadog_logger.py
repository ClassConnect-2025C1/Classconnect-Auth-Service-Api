import json
import socket
import time
import os
from typing import Dict, List, Any, Optional
import httpx
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

class LogEntry:
    def __init__(
        self,
        message: str,
        status: Optional[str] = None,
        service: str = "",
        hostname: str = "",
        source: str = "",
        tags: Optional[List[str]] = None,
        timestamp: Optional[int] = None,
        attributes: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status = status
        self.service = service
        self.hostname = hostname
        self.source = source
        self.tags = tags or []
        self.timestamp = timestamp or int(time.time() * 1000)  # Unix timestamp in milliseconds
        self.attributes = attributes or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message": self.message,
            "status": self.status,
            "service": self.service,
            "hostname": self.hostname,
            "ddsource": self.source,
            "ddtags": ",".join(self.tags) if self.tags else None,
            "timestamp": self.timestamp,
            "attributes": self.attributes
        }

class DatadogLogger:
    def __init__(
        self,
        api_key: str,
        source: str = "python",
        service: str = "classconnect-auth-api",
        hostname: Optional[str] = None,
        site: Optional[str] = None
    ):
        self.api_key = api_key
        self.source = source
        self.service = service
        self.hostname = hostname or socket.gethostname()
        self.site = site or os.getenv("DATADOG_SITE", "us5.datadoghq.com")
        self.http_client = httpx.AsyncClient(timeout=5.0)

    async def info(self, message: str, attributes: Optional[Dict[str, Any]] = None, tags: Optional[List[str]] = None) -> None:
        await self.log(message, "info", attributes, tags)

    async def error(self, message: str, attributes: Optional[Dict[str, Any]] = None, tags: Optional[List[str]] = None) -> None:
        await self.log(message, "error", attributes, tags)

    async def warn(self, message: str, attributes: Optional[Dict[str, Any]] = None, tags: Optional[List[str]] = None) -> None:
        await self.log(message, "warning", attributes, tags)

    async def log(self, message: str, status: str, attributes: Optional[Dict[str, Any]] = None, tags: Optional[List[str]] = None) -> None:
        entry = LogEntry(
            message=message,
            status=status,
            service=self.service,
            hostname=self.hostname,
            source=self.source,
            tags=tags,
            attributes=attributes
        )
        await self.send_logs([entry])

    async def send_logs(self, logs: List[LogEntry]) -> None:
        payload = json.dumps([log.to_dict() for log in logs])
        print(f"Sending logs to Datadog: {payload}")

        url = f"https://http-intake.logs.{self.site}/api/v2/logs"
        headers = {
            "Content-Type": "application/json",
            "DD-API-KEY": self.api_key
        }

        try:
            response = await self.http_client.post(url, headers=headers, content=payload)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            print(f"Error from Datadog API: status code {e.response.status_code}, body: {e.response.text}")
        except Exception as e:
            print(f"Error sending logs: {str(e)}")

    async def close(self):
        await self.http_client.aclose()

class DatadogLoggerMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, dd_logger: DatadogLogger):
        super().__init__(app)
        self.dd_logger = dd_logger

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        try:
            response = await call_next(request)
            status_code = response.status_code
            status = "info" if status_code < 400 else "error"
        except Exception as exc:
            status_code = 500
            status = "error"
            raise exc
        finally:
            process_time = time.time() - start_time
            
            attributes = {
                "request": {
                    "method": request.method,
                    "url": str(request.url),
                    "headers": dict(request.headers),
                    "client": request.client.host if request.client else None,
                },
                "response": {
                    "status_code": status_code,
                    "process_time_ms": round(process_time * 1000, 2)
                }
            }
            
            # Log the request
            await self.dd_logger.log(
                message=f"{request.method} {request.url.path} - {status_code}",
                status=status,
                attributes=attributes,
                tags=[f"method:{request.method}", f"status_code:{status_code}"]
            )
        
        return response

def setup_datadog_logging(app: FastAPI, api_key: str) -> DatadogLogger:
    if not api_key:
        print("Warning: Datadog API key not provided. Logging to Datadog is disabled.")
        return None
    
    dd_logger = DatadogLogger(api_key=api_key)
    app.add_middleware(DatadogLoggerMiddleware, dd_logger=dd_logger)
    
    @app.on_event("shutdown")
    async def shutdown_logger():
        await dd_logger.close()
    
    return dd_logger