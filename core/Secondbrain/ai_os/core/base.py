"""
AI Operating System - Base Classes and Interfaces
"""

import uuid
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from queue import Queue, Empty
from threading import Lock
from typing import Any, Dict, List, Optional, Callable, Union


class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"
    RETRYING = "retrying"


@dataclass
class AIRequest:
    """
    Unified request object that flows through all layers
    """
    # Core fields
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    request_type: str = "general"

    # Metadata
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    source: str = "cli"  # cli, api, webhook, trigger
    user_id: Optional[str] = None
    session_id: Optional[str] = None

    # Execution hints
    priority: TaskPriority = TaskPriority.NORMAL
    timeout: int = 300  # seconds
    max_retries: int = 3

    # Context and data
    context: Dict[str, Any] = field(default_factory=dict)
    attachments: List[str] = field(default_factory=list)

    # Routing hints (populated by Layer 2)
    target_agent: Optional[str] = None
    target_workflow: Optional[str] = None
    classification: Optional[Dict] = None

    # Tracing
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    parent_id: Optional[str] = None

    def to_dict(self) -> Dict:
        result = asdict(self)
        result['priority'] = self.priority.value
        return result

    @classmethod
    def from_dict(cls, data: Dict) -> 'AIRequest':
        if 'priority' in data and isinstance(data['priority'], int):
            data['priority'] = TaskPriority(data['priority'])
        return cls(**data)


@dataclass
class AIResponse:
    """
    Unified response object returned from all layers
    """
    # Core fields
    request_id: str
    success: bool
    content: Any = None
    error: Optional[str] = None

    # Metadata
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    duration_ms: float = 0

    # Execution details
    status: TaskStatus = TaskStatus.SUCCESS
    steps_completed: int = 0
    total_steps: int = 0

    # Agent/Layer info
    executed_by: str = "unknown"
    layer_trace: List[str] = field(default_factory=list)

    # Additional outputs
    artifacts: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        result = asdict(self)
        result['status'] = self.status.value
        return result

    @classmethod
    def error_response(cls, request_id: str, error: str, executed_by: str = "unknown") -> 'AIResponse':
        return cls(
            request_id=request_id,
            success=False,
            error=error,
            status=TaskStatus.FAILED,
            executed_by=executed_by
        )


class LayerInterface(ABC):
    """
    Abstract base class for all AI OS layers
    Each layer implements this interface for consistent behavior
    """

    def __init__(self, layer_name: str, config: Dict = None):
        self.layer_name = layer_name
        self.config = config or {}
        self._initialized = False
        self._healthy = True
        self._stats = {
            "requests_processed": 0,
            "requests_failed": 0,
            "avg_duration_ms": 0
        }

    @abstractmethod
    async def process(self, request: AIRequest) -> AIResponse:
        """
        Process a request through this layer
        Must be implemented by each layer
        """
        pass

    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize the layer (load models, connect to services, etc.)
        """
        pass

    @abstractmethod
    async def shutdown(self) -> bool:
        """
        Gracefully shutdown the layer
        """
        pass

    def health_check(self) -> Dict[str, Any]:
        """
        Check layer health status
        """
        return {
            "layer": self.layer_name,
            "healthy": self._healthy,
            "initialized": self._initialized,
            "stats": self._stats
        }

    def _update_stats(self, success: bool, duration_ms: float):
        """Update layer statistics"""
        self._stats["requests_processed"] += 1
        if not success:
            self._stats["requests_failed"] += 1

        # Rolling average
        n = self._stats["requests_processed"]
        current_avg = self._stats["avg_duration_ms"]
        self._stats["avg_duration_ms"] = (current_avg * (n - 1) + duration_ms) / n


class MessageBus:
    """
    Inter-layer communication bus
    Enables async message passing between layers
    """

    def __init__(self):
        self._queues: Dict[str, Queue] = {}
        self._subscribers: Dict[str, List[Callable]] = {}
        self._lock = Lock()

    def register_layer(self, layer_name: str):
        """Register a layer with the message bus"""
        with self._lock:
            if layer_name not in self._queues:
                self._queues[layer_name] = Queue()
                self._subscribers[layer_name] = []

    def send(self, from_layer: str, to_layer: str, message: Dict):
        """Send message between layers"""
        envelope = {
            "id": str(uuid.uuid4()),
            "from": from_layer,
            "to": to_layer,
            "timestamp": datetime.now().isoformat(),
            "payload": message
        }

        if to_layer in self._queues:
            self._queues[to_layer].put(envelope)

            # Notify subscribers
            for callback in self._subscribers.get(to_layer, []):
                try:
                    callback(envelope)
                except Exception:
                    pass

        return envelope["id"]

    def receive(self, layer_name: str, timeout: float = None) -> Optional[Dict]:
        """Receive message for a layer"""
        if layer_name not in self._queues:
            return None

        try:
            return self._queues[layer_name].get(timeout=timeout)
        except Empty:
            return None

    def subscribe(self, layer_name: str, callback: Callable):
        """Subscribe to messages for a layer"""
        with self._lock:
            if layer_name in self._subscribers:
                self._subscribers[layer_name].append(callback)

    def broadcast(self, from_layer: str, message: Dict):
        """Broadcast message to all layers"""
        for layer_name in self._queues:
            if layer_name != from_layer:
                self.send(from_layer, layer_name, message)


class StateStore:
    """
    Persistent state storage for the AI OS
    Provides checkpoint/rollback capabilities
    """

    def __init__(self, store_path: Union[str, Path] = "./ai_os_state"):
        self.store_path = Path(store_path)
        self.store_path.mkdir(parents=True, exist_ok=True)
        self._state: Dict[str, Any] = {}
        self._checkpoints: Dict[str, Dict] = {}
        self._lock = Lock()

        # Load existing state
        self._load_state()

    def _load_state(self):
        """Load state from disk"""
        state_file = self.store_path / "state.json"
        if state_file.exists():
            with open(state_file, 'r') as f:
                self._state = json.load(f)

    def _save_state(self):
        """Persist state to disk"""
        state_file = self.store_path / "state.json"
        with open(state_file, 'w') as f:
            json.dump(self._state, f, indent=2, default=str)

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from state"""
        return self._state.get(key, default)

    def set(self, key: str, value: Any, persist: bool = True):
        """Set value in state"""
        with self._lock:
            self._state[key] = value
            if persist:
                self._save_state()

    def delete(self, key: str):
        """Delete key from state"""
        with self._lock:
            if key in self._state:
                del self._state[key]
                self._save_state()

    def checkpoint(self, checkpoint_id: str = None) -> str:
        """Create a checkpoint of current state"""
        checkpoint_id = checkpoint_id or str(uuid.uuid4())[:8]
        with self._lock:
            self._checkpoints[checkpoint_id] = {
                "timestamp": datetime.now().isoformat(),
                "state": self._state.copy()
            }

            # Persist checkpoint
            checkpoint_file = self.store_path / f"checkpoint_{checkpoint_id}.json"
            with open(checkpoint_file, 'w') as f:
                json.dump(self._checkpoints[checkpoint_id], f, indent=2, default=str)

        return checkpoint_id

    def rollback(self, checkpoint_id: str) -> bool:
        """Rollback to a checkpoint"""
        if checkpoint_id not in self._checkpoints:
            # Try loading from disk
            checkpoint_file = self.store_path / f"checkpoint_{checkpoint_id}.json"
            if checkpoint_file.exists():
                with open(checkpoint_file, 'r') as f:
                    self._checkpoints[checkpoint_id] = json.load(f)
            else:
                return False

        with self._lock:
            self._state = self._checkpoints[checkpoint_id]["state"].copy()
            self._save_state()

        return True

    def list_checkpoints(self) -> List[Dict]:
        """List all available checkpoints"""
        checkpoints = []
        for f in self.store_path.glob("checkpoint_*.json"):
            checkpoint_id = f.stem.replace("checkpoint_", "")
            with open(f, 'r') as file:
                data = json.load(file)
                checkpoints.append({
                    "id": checkpoint_id,
                    "timestamp": data.get("timestamp"),
                    "file": str(f)
                })
        return sorted(checkpoints, key=lambda x: x["timestamp"], reverse=True)
