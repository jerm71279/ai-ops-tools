"""
Layer 1: Webhook Handlers
Receive and process webhooks from external systems
"""

import asyncio
import hashlib
import hmac
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from ..core.base import AIRequest, AIResponse, TaskPriority
from ..core.logging import get_logger


class WebhookSource(Enum):
    """Supported webhook sources"""
    GITHUB = "github"
    AZURE_DEVOPS = "azure_devops"
    SLACK = "slack"
    MS_TEAMS = "ms_teams"
    NINJAONE = "ninjaone"
    CUSTOM = "custom"


@dataclass
class WebhookConfig:
    """Configuration for a webhook endpoint"""
    source: WebhookSource
    path: str
    secret: Optional[str] = None
    enabled: bool = True
    auto_respond: bool = False
    response_template: Optional[str] = None
    priority: TaskPriority = TaskPriority.NORMAL
    # Custom field mappings
    content_field: str = "content"
    context_fields: List[str] = field(default_factory=list)


@dataclass
class WebhookEvent:
    """Parsed webhook event"""
    id: str
    source: WebhookSource
    event_type: str
    payload: Dict[str, Any]
    headers: Dict[str, str]
    received_at: datetime = field(default_factory=datetime.now)
    signature_valid: bool = True


class WebhookHandler:
    """
    Webhook Handler for AI OS

    Receives webhooks from external systems and converts them to AI requests.
    Supports:
    - GitHub (issues, PRs, comments)
    - Azure DevOps (work items, pipelines)
    - Slack (messages, commands)
    - MS Teams (messages)
    - NinjaOne (alerts, tickets)
    - Custom webhooks
    """

    def __init__(self, process_callback: Callable = None):
        self.logger = get_logger("ai_os.webhooks")
        self.process_callback = process_callback

        # Registered webhook configs
        self._configs: Dict[str, WebhookConfig] = {}

        # Event history (for debugging/audit)
        self._event_history: List[WebhookEvent] = []
        self._max_history = 100

        # Register default configurations
        self._register_defaults()

    def _register_defaults(self):
        """Register default webhook configurations"""
        # GitHub webhooks
        self.register_webhook(WebhookConfig(
            source=WebhookSource.GITHUB,
            path="/webhooks/github",
            content_field="issue.body",
            context_fields=["action", "repository.full_name", "sender.login"]
        ))

        # Slack webhooks
        self.register_webhook(WebhookConfig(
            source=WebhookSource.SLACK,
            path="/webhooks/slack",
            content_field="text",
            context_fields=["channel", "user", "team"]
        ))

        # NinjaOne webhooks
        self.register_webhook(WebhookConfig(
            source=WebhookSource.NINJAONE,
            path="/webhooks/ninjaone",
            content_field="alert.message",
            context_fields=["device.name", "organization.name", "alert.severity"],
            priority=TaskPriority.HIGH
        ))

        # Generic custom webhook
        self.register_webhook(WebhookConfig(
            source=WebhookSource.CUSTOM,
            path="/webhooks/custom",
            content_field="content"
        ))

    def register_webhook(self, config: WebhookConfig):
        """Register a webhook configuration"""
        self._configs[config.path] = config
        self.logger.info(f"Registered webhook: {config.source.value} at {config.path}")

    def set_processor(self, callback: Callable):
        """Set the callback for processing requests"""
        self.process_callback = callback

    async def handle_webhook(
        self,
        path: str,
        headers: Dict[str, str],
        body: bytes,
        query_params: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """
        Handle an incoming webhook

        Args:
            path: Webhook endpoint path
            headers: HTTP headers
            body: Raw request body
            query_params: URL query parameters

        Returns:
            Response dict with status and message
        """
        # Find matching config
        config = self._configs.get(path)
        if not config:
            return {"status": 404, "error": "Webhook endpoint not found"}

        if not config.enabled:
            return {"status": 503, "error": "Webhook endpoint disabled"}

        try:
            # Parse body
            payload = json.loads(body.decode('utf-8')) if body else {}
        except json.JSONDecodeError:
            return {"status": 400, "error": "Invalid JSON payload"}

        # Validate signature if configured
        if config.secret:
            if not self._validate_signature(config, headers, body):
                self.logger.warning(f"Invalid webhook signature for {path}")
                return {"status": 401, "error": "Invalid signature"}

        # Parse event
        event = self._parse_event(config, headers, payload)
        self._record_event(event)

        self.logger.info(f"Received webhook: {event.source.value} - {event.event_type}")

        # Convert to AI request
        request = self._create_request(config, event, query_params or {})

        # Process request
        if self.process_callback:
            try:
                response = await self.process_callback(request)
                return {
                    "status": 200,
                    "accepted": True,
                    "request_id": request.request_id,
                    "success": response.success,
                    "content": response.content if config.auto_respond else None
                }
            except Exception as e:
                self.logger.error(f"Webhook processing error: {e}")
                return {"status": 500, "error": str(e)}

        return {"status": 202, "accepted": True, "request_id": request.request_id}

    def _validate_signature(
        self,
        config: WebhookConfig,
        headers: Dict[str, str],
        body: bytes
    ) -> bool:
        """Validate webhook signature"""
        if config.source == WebhookSource.GITHUB:
            # GitHub uses X-Hub-Signature-256
            signature = headers.get("X-Hub-Signature-256", "")
            if signature.startswith("sha256="):
                expected = "sha256=" + hmac.new(
                    config.secret.encode(),
                    body,
                    hashlib.sha256
                ).hexdigest()
                return hmac.compare_digest(signature, expected)

        elif config.source == WebhookSource.SLACK:
            # Slack uses X-Slack-Signature
            timestamp = headers.get("X-Slack-Request-Timestamp", "")
            signature = headers.get("X-Slack-Signature", "")
            basestring = f"v0:{timestamp}:{body.decode()}"
            expected = "v0=" + hmac.new(
                config.secret.encode(),
                basestring.encode(),
                hashlib.sha256
            ).hexdigest()
            return hmac.compare_digest(signature, expected)

        # Default: simple HMAC-SHA256
        signature = headers.get("X-Signature", headers.get("X-Webhook-Signature", ""))
        expected = hmac.new(config.secret.encode(), body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(signature, expected)

    def _parse_event(
        self,
        config: WebhookConfig,
        headers: Dict[str, str],
        payload: Dict
    ) -> WebhookEvent:
        """Parse webhook payload into event"""
        # Determine event type based on source
        if config.source == WebhookSource.GITHUB:
            event_type = headers.get("X-GitHub-Event", "unknown")
        elif config.source == WebhookSource.SLACK:
            event_type = payload.get("type", payload.get("event", {}).get("type", "message"))
        elif config.source == WebhookSource.AZURE_DEVOPS:
            event_type = payload.get("eventType", "unknown")
        elif config.source == WebhookSource.NINJAONE:
            event_type = payload.get("type", payload.get("alertType", "alert"))
        else:
            event_type = payload.get("event_type", payload.get("type", "custom"))

        return WebhookEvent(
            id=headers.get("X-Request-ID", headers.get("X-Correlation-ID", "")),
            source=config.source,
            event_type=event_type,
            payload=payload,
            headers=dict(headers)
        )

    def _create_request(
        self,
        config: WebhookConfig,
        event: WebhookEvent,
        query_params: Dict
    ) -> AIRequest:
        """Create AI request from webhook event"""
        # Extract content using field path
        content = self._extract_field(event.payload, config.content_field)

        # Build context from configured fields
        context = {
            "webhook_source": event.source.value,
            "webhook_event": event.event_type,
            "webhook_id": event.id
        }

        for field_path in config.context_fields:
            value = self._extract_field(event.payload, field_path)
            if value is not None:
                # Use last part of path as key
                key = field_path.split(".")[-1]
                context[key] = value

        # Add query params to context
        context.update(query_params)

        return AIRequest(
            content=content or f"Webhook event: {event.event_type}",
            request_type="webhook",
            source=f"webhook:{event.source.value}",
            priority=config.priority,
            context=context
        )

    def _extract_field(self, data: Dict, field_path: str) -> Any:
        """Extract nested field value using dot notation"""
        parts = field_path.split(".")
        current = data

        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return None

            if current is None:
                return None

        return current

    def _record_event(self, event: WebhookEvent):
        """Record event in history"""
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history = self._event_history[-self._max_history:]

    def get_event_history(self, limit: int = 20) -> List[Dict]:
        """Get recent webhook events"""
        events = self._event_history[-limit:]
        return [
            {
                "id": e.id,
                "source": e.source.value,
                "event_type": e.event_type,
                "received_at": e.received_at.isoformat(),
                "signature_valid": e.signature_valid
            }
            for e in reversed(events)
        ]

    def get_registered_webhooks(self) -> List[Dict]:
        """List registered webhook endpoints"""
        return [
            {
                "path": config.path,
                "source": config.source.value,
                "enabled": config.enabled,
                "has_secret": config.secret is not None
            }
            for config in self._configs.values()
        ]


# Integration with aiohttp API server
def register_webhook_routes(app, webhook_handler: WebhookHandler):
    """Register webhook routes with aiohttp app"""
    try:
        from aiohttp import web
    except ImportError:
        return

    async def handle_webhook(request: web.Request) -> web.Response:
        path = request.path
        headers = dict(request.headers)
        body = await request.read()
        query = dict(request.query)

        result = await webhook_handler.handle_webhook(path, headers, body, query)
        status = result.pop("status", 200)
        return web.json_response(result, status=status)

    # Register routes for all configured webhooks
    for path in webhook_handler._configs.keys():
        app.router.add_post(path, handle_webhook)

    # Webhook management endpoints
    async def list_webhooks(request: web.Request) -> web.Response:
        return web.json_response({
            "webhooks": webhook_handler.get_registered_webhooks()
        })

    async def webhook_history(request: web.Request) -> web.Response:
        limit = int(request.query.get("limit", 20))
        return web.json_response({
            "events": webhook_handler.get_event_history(limit)
        })

    app.router.add_get("/webhooks", list_webhooks)
    app.router.add_get("/webhooks/history", webhook_history)
