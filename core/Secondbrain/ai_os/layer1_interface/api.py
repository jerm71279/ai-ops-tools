"""
Layer 1: API Interface
REST API interface for the AI Operating System using aiohttp
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

try:
    from aiohttp import web
    from aiohttp.web import middleware
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    web = None

from ..core.base import AIRequest, AIResponse, TaskPriority
from ..core.logging import get_logger


class APIInterface:
    """
    REST API Interface for AI OS

    Provides HTTP API access to the AI Operating System using aiohttp.
    Features:
    - Full REST API with OpenAPI spec
    - WebSocket support for streaming responses
    - CORS handling
    - Authentication middleware hook
    - Async job queue for long-running tasks
    """

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 8080,
        process_callback: Callable = None,
        enable_cors: bool = True
    ):
        self.host = host
        self.port = port
        self.process_callback = process_callback
        self.logger = get_logger("ai_os.api")
        self._running = False
        self._enable_cors = enable_cors

        # Async job tracking
        self._async_jobs: Dict[str, Dict] = {}

        # aiohttp app
        self._app: Optional[web.Application] = None
        self._runner: Optional[web.AppRunner] = None

        # Callbacks for external status/info
        self._get_status_callback: Optional[Callable] = None
        self._get_agents_callback: Optional[Callable] = None
        self._get_workflows_callback: Optional[Callable] = None

    def set_processor(self, callback: Callable):
        """Set the callback for processing requests"""
        self.process_callback = callback

    def set_status_callback(self, callback: Callable):
        """Set callback to get system status"""
        self._get_status_callback = callback

    def set_agents_callback(self, callback: Callable):
        """Set callback to get available agents"""
        self._get_agents_callback = callback

    def set_workflows_callback(self, callback: Callable):
        """Set callback to get available workflows"""
        self._get_workflows_callback = callback

    async def handle_request(self, method: str, path: str, body: dict = None) -> dict:
        """
        Handle an HTTP request

        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path
            body: Request body (for POST/PUT)

        Returns:
            Response dictionary
        """
        try:
            # Route request
            if path == "/health":
                return self._health_check()
            elif path == "/process" and method == "POST":
                return await self._process_request(body)
            elif path == "/status":
                return await self._get_status()
            else:
                return {"error": "Not found", "status": 404}

        except Exception as e:
            self.logger.error(f"API error: {e}")
            return {"error": str(e), "status": 500}

    async def _process_request(self, body: dict) -> dict:
        """Process an AI request via API"""
        if not body:
            return {"error": "Request body required", "status": 400}

        # Create request from body
        request = AIRequest(
            content=body.get("content", ""),
            request_type=body.get("type", "general"),
            source="api",
            context=body.get("context", {}),
            user_id=body.get("user_id"),
            session_id=body.get("session_id")
        )

        if self.process_callback:
            response = await self.process_callback(request)
            return {
                "success": response.success,
                "content": response.content,
                "error": response.error,
                "request_id": response.request_id,
                "duration_ms": response.duration_ms,
                "artifacts": response.artifacts,
                "status": 200 if response.success else 500
            }

        return {"error": "No processor configured", "status": 503}

    async def _get_status(self) -> dict:
        """Get system status"""
        if self.process_callback:
            request = AIRequest(
                content="status",
                request_type="command",
                source="api"
            )
            response = await self.process_callback(request)
            return {
                "status": 200,
                "data": response.content
            }

        return {"status": 503, "error": "System not ready"}

    def _health_check(self) -> dict:
        """Simple health check"""
        return {
            "status": 200,
            "healthy": True,
            "service": "ai-os"
        }

    # ==================== aiohttp Server ====================

    async def start_server(self):
        """Start the HTTP server"""
        if not AIOHTTP_AVAILABLE:
            self.logger.warning("aiohttp not available - API server disabled")
            return

        self._app = web.Application(middlewares=[self._cors_middleware] if self._enable_cors else [])

        # Register routes
        self._register_routes()

        # Start server
        self._runner = web.AppRunner(self._app)
        await self._runner.setup()

        site = web.TCPSite(self._runner, self.host, self.port)
        await site.start()

        self._running = True
        self.logger.info(f"API server started on http://{self.host}:{self.port}")

    async def stop_server(self):
        """Stop the HTTP server"""
        if self._runner:
            await self._runner.cleanup()
        self._running = False
        self.logger.info("API server stopped")

    def _register_routes(self):
        """Register all API routes"""
        if not self._app:
            return

        # Core routes
        self._app.router.add_get("/health", self._handle_health)
        self._app.router.add_get("/", self._handle_root)
        self._app.router.add_get("/openapi.json", self._handle_openapi)

        # Process routes
        self._app.router.add_post("/process", self._handle_process)
        self._app.router.add_post("/process/async", self._handle_process_async)

        # Job management
        self._app.router.add_get("/jobs/{job_id}", self._handle_get_job)
        self._app.router.add_delete("/jobs/{job_id}", self._handle_cancel_job)
        self._app.router.add_get("/jobs", self._handle_list_jobs)

        # System info
        self._app.router.add_get("/status", self._handle_status)
        self._app.router.add_get("/agents", self._handle_agents)
        self._app.router.add_get("/workflows", self._handle_workflows)

        # WebSocket for streaming
        self._app.router.add_get("/ws", self._handle_websocket)

    @middleware
    async def _cors_middleware(self, request: web.Request, handler):
        """CORS middleware for cross-origin requests"""
        if request.method == "OPTIONS":
            response = web.Response()
        else:
            response = await handler(request)

        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response

    # ==================== Route Handlers ====================

    async def _handle_root(self, request: web.Request) -> web.Response:
        """Root endpoint with API info"""
        return web.json_response({
            "service": "AI Operating System API",
            "version": "1.0.0",
            "endpoints": [
                "GET /health",
                "GET /status",
                "POST /process",
                "POST /process/async",
                "GET /jobs/{job_id}",
                "GET /agents",
                "GET /workflows",
                "GET /ws (WebSocket)",
                "GET /openapi.json"
            ]
        })

    async def _handle_health(self, request: web.Request) -> web.Response:
        """Health check endpoint"""
        return web.json_response(self._health_check())

    async def _handle_status(self, request: web.Request) -> web.Response:
        """System status endpoint"""
        if self._get_status_callback:
            status = self._get_status_callback()
            return web.json_response({"status": 200, "data": status})
        return web.json_response({"status": 503, "error": "Status unavailable"}, status=503)

    async def _handle_agents(self, request: web.Request) -> web.Response:
        """List available agents"""
        if self._get_agents_callback:
            agents = self._get_agents_callback()
            return web.json_response({"status": 200, "agents": agents})
        return web.json_response({"status": 503, "error": "Agents unavailable"}, status=503)

    async def _handle_workflows(self, request: web.Request) -> web.Response:
        """List available workflows"""
        if self._get_workflows_callback:
            workflows = self._get_workflows_callback()
            return web.json_response({"status": 200, "workflows": workflows})
        return web.json_response({"status": 503, "error": "Workflows unavailable"}, status=503)

    async def _handle_process(self, request: web.Request) -> web.Response:
        """Synchronous process endpoint"""
        try:
            body = await request.json()
        except json.JSONDecodeError:
            return web.json_response({"error": "Invalid JSON"}, status=400)

        result = await self._process_request(body)
        status_code = result.pop("status", 200)
        return web.json_response(result, status=status_code)

    async def _handle_process_async(self, request: web.Request) -> web.Response:
        """Asynchronous process endpoint - returns job ID"""
        try:
            body = await request.json()
        except json.JSONDecodeError:
            return web.json_response({"error": "Invalid JSON"}, status=400)

        # Create job
        job_id = str(uuid.uuid4())
        self._async_jobs[job_id] = {
            "id": job_id,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "request": body,
            "result": None
        }

        # Start async processing
        asyncio.create_task(self._process_job(job_id, body))

        return web.json_response({
            "job_id": job_id,
            "status": "pending",
            "poll_url": f"/jobs/{job_id}"
        }, status=202)

    async def _process_job(self, job_id: str, body: dict):
        """Process an async job"""
        try:
            self._async_jobs[job_id]["status"] = "running"
            result = await self._process_request(body)
            self._async_jobs[job_id]["status"] = "completed"
            self._async_jobs[job_id]["result"] = result
            self._async_jobs[job_id]["completed_at"] = datetime.now().isoformat()
        except Exception as e:
            self._async_jobs[job_id]["status"] = "failed"
            self._async_jobs[job_id]["error"] = str(e)

    async def _handle_get_job(self, request: web.Request) -> web.Response:
        """Get job status"""
        job_id = request.match_info.get("job_id")
        if job_id not in self._async_jobs:
            return web.json_response({"error": "Job not found"}, status=404)
        return web.json_response(self._async_jobs[job_id])

    async def _handle_cancel_job(self, request: web.Request) -> web.Response:
        """Cancel a pending job"""
        job_id = request.match_info.get("job_id")
        if job_id not in self._async_jobs:
            return web.json_response({"error": "Job not found"}, status=404)

        job = self._async_jobs[job_id]
        if job["status"] in ("pending", "running"):
            job["status"] = "cancelled"
            return web.json_response({"status": "cancelled"})
        return web.json_response({"error": "Job cannot be cancelled"}, status=400)

    async def _handle_list_jobs(self, request: web.Request) -> web.Response:
        """List all jobs"""
        return web.json_response({
            "jobs": list(self._async_jobs.values())
        })

    async def _handle_openapi(self, request: web.Request) -> web.Response:
        """OpenAPI specification"""
        return web.json_response(self.get_openapi_spec())

    async def _handle_websocket(self, request: web.Request) -> web.WebSocketResponse:
        """WebSocket endpoint for streaming"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        self.logger.info("WebSocket connection established")

        try:
            async for msg in ws:
                if msg.type == web.WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        if data.get("type") == "process":
                            # Process and stream results
                            await self._stream_process(ws, data.get("content", ""), data)
                        elif data.get("type") == "ping":
                            await ws.send_json({"type": "pong"})
                    except json.JSONDecodeError:
                        await ws.send_json({"error": "Invalid JSON"})
                elif msg.type == web.WSMsgType.ERROR:
                    self.logger.error(f"WebSocket error: {ws.exception()}")
        finally:
            self.logger.info("WebSocket connection closed")

        return ws

    async def _stream_process(self, ws: web.WebSocketResponse, content: str, options: dict):
        """Stream processing results via WebSocket"""
        # Send processing start
        await ws.send_json({"type": "start", "content": content})

        # Process request
        body = {
            "content": content,
            "context": options.get("context", {}),
            "session_id": options.get("session_id")
        }
        result = await self._process_request(body)

        # Send result
        await ws.send_json({
            "type": "complete",
            "success": result.get("success", False),
            "content": result.get("content"),
            "duration_ms": result.get("duration_ms")
        })

    def get_openapi_spec(self) -> dict:
        """Get OpenAPI specification"""
        return {
            "openapi": "3.0.0",
            "info": {
                "title": "AI Operating System API",
                "version": "1.0.0",
                "description": "REST API for the OberaConnect AI Operating System"
            },
            "servers": [
                {"url": f"http://{self.host}:{self.port}", "description": "Local server"}
            ],
            "paths": {
                "/": {
                    "get": {
                        "summary": "API information",
                        "responses": {"200": {"description": "API info and available endpoints"}}
                    }
                },
                "/health": {
                    "get": {
                        "summary": "Health check",
                        "responses": {"200": {"description": "System is healthy"}}
                    }
                },
                "/status": {
                    "get": {
                        "summary": "Get system status",
                        "responses": {"200": {"description": "System status with layer health"}}
                    }
                },
                "/process": {
                    "post": {
                        "summary": "Process an AI request synchronously",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ProcessRequest"
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {"description": "Request processed successfully"},
                            "400": {"description": "Invalid request"},
                            "500": {"description": "Processing error"}
                        }
                    }
                },
                "/process/async": {
                    "post": {
                        "summary": "Process an AI request asynchronously",
                        "description": "Submits a request for async processing and returns a job ID",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ProcessRequest"}
                                }
                            }
                        },
                        "responses": {
                            "202": {
                                "description": "Job accepted",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/JobCreated"}
                                    }
                                }
                            }
                        }
                    }
                },
                "/jobs": {
                    "get": {
                        "summary": "List all jobs",
                        "responses": {"200": {"description": "List of all jobs"}}
                    }
                },
                "/jobs/{job_id}": {
                    "get": {
                        "summary": "Get job status",
                        "parameters": [
                            {"name": "job_id", "in": "path", "required": True, "schema": {"type": "string"}}
                        ],
                        "responses": {
                            "200": {"description": "Job details"},
                            "404": {"description": "Job not found"}
                        }
                    },
                    "delete": {
                        "summary": "Cancel a job",
                        "parameters": [
                            {"name": "job_id", "in": "path", "required": True, "schema": {"type": "string"}}
                        ],
                        "responses": {
                            "200": {"description": "Job cancelled"},
                            "400": {"description": "Cannot cancel job"},
                            "404": {"description": "Job not found"}
                        }
                    }
                },
                "/agents": {
                    "get": {
                        "summary": "List available AI agents",
                        "responses": {"200": {"description": "List of agents with capabilities"}}
                    }
                },
                "/workflows": {
                    "get": {
                        "summary": "List available workflows",
                        "responses": {"200": {"description": "List of workflow names"}}
                    }
                },
                "/ws": {
                    "get": {
                        "summary": "WebSocket endpoint for streaming",
                        "description": "Connect via WebSocket for real-time streaming responses"
                    }
                }
            },
            "components": {
                "schemas": {
                    "ProcessRequest": {
                        "type": "object",
                        "required": ["content"],
                        "properties": {
                            "content": {"type": "string", "description": "The request/prompt to process"},
                            "type": {"type": "string", "default": "general"},
                            "context": {"type": "object", "description": "Additional context"},
                            "session_id": {"type": "string", "description": "Session ID for context continuity"},
                            "target_agent": {"type": "string", "description": "Specific agent to use"},
                            "target_workflow": {"type": "string", "description": "Specific workflow to execute"}
                        }
                    },
                    "JobCreated": {
                        "type": "object",
                        "properties": {
                            "job_id": {"type": "string"},
                            "status": {"type": "string", "enum": ["pending"]},
                            "poll_url": {"type": "string"}
                        }
                    }
                }
            }
        }
