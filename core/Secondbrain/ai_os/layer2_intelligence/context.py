"""
Layer 2: Context Manager
Maintains conversation and session context
"""

import time
from collections import deque
from typing import Any, Dict, List, Optional

from ..core.config import AIConfig
from ..core.logging import get_logger


class ContextManager:
    """
    Manages conversation and session context

    Responsibilities:
    - Store conversation history per session
    - Extract relevant context for requests
    - Manage context window limits
    - Handle context expiration
    """

    def __init__(self, config: AIConfig = None):
        self.config = config or AIConfig()
        self.logger = get_logger("ai_os.context")

        # Configuration
        intelligence_config = self.config.intelligence
        context_config = intelligence_config.get("context_manager", {})

        self._max_context_length = context_config.get("max_context_length", 32000)
        self._history_depth = context_config.get("history_depth", 10)
        self._context_ttl = 3600  # 1 hour default

        # Session storage
        self._sessions: Dict[str, Dict] = {}

        # Global context (shared across sessions)
        self._global_context: Dict[str, Any] = {}

    def get_context(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get context for a session

        Args:
            session_id: Session identifier (None for global context only)

        Returns:
            Combined context dictionary
        """
        context = {}

        # Add global context
        context.update(self._global_context)

        # Add session context if available
        if session_id and session_id in self._sessions:
            session = self._sessions[session_id]

            # Check if session is expired
            if time.time() - session.get("last_activity", 0) > self._context_ttl:
                self._expire_session(session_id)
            else:
                context["session"] = {
                    "id": session_id,
                    "history": list(session.get("history", [])),
                    "variables": session.get("variables", {}),
                    "last_activity": session.get("last_activity")
                }

        return context

    def add_interaction(
        self,
        session_id: str,
        user_input: str,
        response: Any
    ):
        """
        Add an interaction to session history

        Args:
            session_id: Session identifier
            user_input: User's input
            response: System's response
        """
        if not session_id:
            return

        # Initialize session if needed
        if session_id not in self._sessions:
            self._sessions[session_id] = {
                "created": time.time(),
                "last_activity": time.time(),
                "history": deque(maxlen=self._history_depth),
                "variables": {}
            }

        session = self._sessions[session_id]
        session["last_activity"] = time.time()

        # Add to history
        interaction = {
            "timestamp": time.time(),
            "user": self._truncate(str(user_input), 1000),
            "response": self._truncate(str(response), 2000)
        }
        session["history"].append(interaction)

        # Extract and store any variables mentioned
        self._extract_variables(session, user_input)

    def set_variable(
        self,
        session_id: str,
        key: str,
        value: Any
    ):
        """Set a session variable"""
        if session_id not in self._sessions:
            self._sessions[session_id] = {
                "created": time.time(),
                "last_activity": time.time(),
                "history": deque(maxlen=self._history_depth),
                "variables": {}
            }

        self._sessions[session_id]["variables"][key] = value
        self._sessions[session_id]["last_activity"] = time.time()

    def get_variable(
        self,
        session_id: str,
        key: str,
        default: Any = None
    ) -> Any:
        """Get a session variable"""
        if session_id not in self._sessions:
            return default

        return self._sessions[session_id].get("variables", {}).get(key, default)

    def set_global(self, key: str, value: Any):
        """Set a global context variable"""
        self._global_context[key] = value

    def get_global(self, key: str, default: Any = None) -> Any:
        """Get a global context variable"""
        return self._global_context.get(key, default)

    def get_history(
        self,
        session_id: str,
        limit: int = None
    ) -> List[Dict]:
        """Get conversation history for a session"""
        if session_id not in self._sessions:
            return []

        history = list(self._sessions[session_id].get("history", []))

        if limit:
            return history[-limit:]
        return history

    def clear_session(self, session_id: str):
        """Clear a session's context"""
        if session_id in self._sessions:
            del self._sessions[session_id]

    def _expire_session(self, session_id: str):
        """Expire an old session"""
        self.logger.debug(f"Expiring session: {session_id}")
        if session_id in self._sessions:
            del self._sessions[session_id]

    def _truncate(self, text: str, max_length: int) -> str:
        """Truncate text to max length"""
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."

    def _extract_variables(self, session: Dict, text: str):
        """Extract and store mentioned variables/entities"""
        # Simple entity extraction
        # In production, this could use NER or other NLP

        # Look for quoted strings
        import re
        quoted = re.findall(r'"([^"]+)"', text)
        for i, q in enumerate(quoted):
            session["variables"][f"quoted_{i}"] = q

        # Look for file paths
        paths = re.findall(r'[/\\][\w./\\-]+', text)
        for i, p in enumerate(paths):
            session["variables"][f"path_{i}"] = p

        # Look for URLs
        urls = re.findall(r'https?://[^\s]+', text)
        for i, u in enumerate(urls):
            session["variables"][f"url_{i}"] = u

    def get_relevant_context(
        self,
        session_id: str,
        query: str,
        max_tokens: int = 4000
    ) -> str:
        """
        Get relevant context for a query (for prompt augmentation)

        This is a simplified implementation. In production, this could
        use embeddings and semantic search.
        """
        context_parts = []

        # Add recent history
        history = self.get_history(session_id, limit=3)
        if history:
            context_parts.append("Recent conversation:")
            for h in history:
                context_parts.append(f"  User: {h['user'][:200]}")
                context_parts.append(f"  Response: {h['response'][:300]}")

        # Add relevant variables
        session = self._sessions.get(session_id, {})
        variables = session.get("variables", {})
        if variables:
            context_parts.append("\nKnown values:")
            for key, value in list(variables.items())[:5]:
                context_parts.append(f"  {key}: {str(value)[:100]}")

        # Join and truncate
        context = "\n".join(context_parts)
        return self._truncate(context, max_tokens * 4)  # ~4 chars per token

    def cleanup_expired(self):
        """Clean up all expired sessions"""
        current_time = time.time()
        expired = [
            sid for sid, session in self._sessions.items()
            if current_time - session.get("last_activity", 0) > self._context_ttl
        ]

        for sid in expired:
            self._expire_session(sid)

        return len(expired)

    def get_stats(self) -> Dict[str, Any]:
        """Get context manager statistics"""
        return {
            "active_sessions": len(self._sessions),
            "global_context_keys": len(self._global_context),
            "total_history_items": sum(
                len(s.get("history", []))
                for s in self._sessions.values()
            )
        }
