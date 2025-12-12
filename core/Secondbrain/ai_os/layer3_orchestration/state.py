"""
Layer 3: State Machine
DAG-based workflow state management with checkpointing and parallel execution
"""

import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

from ..core.logging import get_logger


class NodeStatus(Enum):
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


class BranchCondition(Enum):
    """Conditions for branching logic"""
    ALWAYS = "always"
    ON_SUCCESS = "on_success"
    ON_FAILURE = "on_failure"
    ON_CONDITION = "on_condition"


@dataclass
class DAGNode:
    """A node in the workflow DAG"""
    id: str
    name: str
    dependencies: Set[str] = field(default_factory=set)
    status: NodeStatus = NodeStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Execution configuration
    executor: Optional[Callable] = None
    agent: Optional[str] = None
    prompt: Optional[str] = None
    timeout: int = 300

    # Retry configuration
    max_retries: int = 3
    retry_count: int = 0
    retry_delay: float = 1.0

    # Branching
    branch_condition: BranchCondition = BranchCondition.ALWAYS
    condition_func: Optional[Callable] = None

    @property
    def duration_ms(self) -> Optional[float]:
        """Calculate execution duration"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds() * 1000
        return None

    @property
    def can_retry(self) -> bool:
        """Check if node can be retried"""
        return self.retry_count < self.max_retries


class StateMachine:
    """
    DAG-based state machine for workflow execution

    Manages:
    - Node dependencies and execution order
    - Parallel execution of independent nodes
    - Checkpointing and recovery
    - State transitions and validation
    - Retry logic with exponential backoff
    - Conditional branching
    """

    def __init__(self, workflow_id: str, checkpoint_path: Optional[Path] = None):
        self.workflow_id = workflow_id
        self.logger = get_logger("ai_os.state_machine")

        # DAG structure
        self._nodes: Dict[str, DAGNode] = {}
        self._checkpoints: List[Dict] = []
        self._checkpoint_path = checkpoint_path or Path("./ai_os_checkpoints")
        self._checkpoint_path.mkdir(parents=True, exist_ok=True)

        # Execution state
        self._started = False
        self._completed = False
        self._cancelled = False
        self._current_checkpoint: Optional[str] = None

        # Execution control
        self._max_parallel = 5
        self._semaphore: Optional[asyncio.Semaphore] = None

        # Results collection
        self._results: Dict[str, Any] = {}

    def add_node(
        self,
        node_id: str,
        name: str,
        dependencies: List[str] = None,
        executor: Callable = None,
        agent: str = None,
        prompt: str = None,
        max_retries: int = 3,
        timeout: int = 300,
        branch_condition: BranchCondition = BranchCondition.ALWAYS,
        condition_func: Callable = None
    ):
        """Add a node to the DAG"""
        self._nodes[node_id] = DAGNode(
            id=node_id,
            name=name,
            dependencies=set(dependencies) if dependencies else set(),
            executor=executor,
            agent=agent,
            prompt=prompt,
            max_retries=max_retries,
            timeout=timeout,
            branch_condition=branch_condition,
            condition_func=condition_func
        )

    def get_ready_nodes(self) -> List[str]:
        """Get nodes that are ready to execute (all dependencies met)"""
        ready = []

        for node_id, node in self._nodes.items():
            if node.status != NodeStatus.PENDING:
                continue

            # Check all dependencies are completed
            deps_met = all(
                self._nodes.get(dep, DAGNode("", "")).status == NodeStatus.COMPLETED
                for dep in node.dependencies
            )

            if not deps_met:
                continue

            # Check branching conditions
            if node.branch_condition == BranchCondition.ON_SUCCESS:
                # All dependencies must have succeeded
                deps_success = all(
                    self._nodes.get(dep, DAGNode("", "")).status == NodeStatus.COMPLETED
                    for dep in node.dependencies
                )
                if not deps_success:
                    self._skip_node(node_id, "Dependencies did not succeed")
                    continue

            elif node.branch_condition == BranchCondition.ON_FAILURE:
                # At least one dependency must have failed
                any_failed = any(
                    self._nodes.get(dep, DAGNode("", "")).status == NodeStatus.FAILED
                    for dep in node.dependencies
                )
                if not any_failed:
                    self._skip_node(node_id, "No dependency failures")
                    continue

            elif node.branch_condition == BranchCondition.ON_CONDITION:
                # Evaluate custom condition
                if node.condition_func:
                    try:
                        if not node.condition_func(self._results):
                            self._skip_node(node_id, "Condition not met")
                            continue
                    except Exception as e:
                        self._skip_node(node_id, f"Condition error: {e}")
                        continue

            ready.append(node_id)

        return ready

    def _skip_node(self, node_id: str, reason: str):
        """Skip a node due to branching"""
        if node_id in self._nodes:
            self._nodes[node_id].status = NodeStatus.SKIPPED
            self._nodes[node_id].error = reason
            self._nodes[node_id].completed_at = datetime.now()

    async def execute(
        self,
        executor: Callable[[DAGNode, Dict[str, Any]], Any] = None,
        max_parallel: int = 5
    ) -> Dict[str, Any]:
        """
        Execute the DAG with parallel processing

        Args:
            executor: Async function to execute each node
            max_parallel: Maximum concurrent executions

        Returns:
            Dict with execution results and status
        """
        self._started = True
        self._semaphore = asyncio.Semaphore(max_parallel)
        start_time = datetime.now()

        self.logger.info(f"Starting DAG execution: {self.workflow_id}")

        try:
            while not self.is_complete() and not self._cancelled:
                ready_nodes = self.get_ready_nodes()

                if not ready_nodes:
                    # No nodes ready but not complete - check for deadlock
                    running = [n for n in self._nodes.values() if n.status == NodeStatus.RUNNING]
                    if not running:
                        self.logger.warning("Possible deadlock detected - no ready or running nodes")
                        break

                    # Wait for running nodes
                    await asyncio.sleep(0.1)
                    continue

                # Execute ready nodes in parallel
                tasks = [
                    self._execute_node(node_id, executor)
                    for node_id in ready_nodes
                ]

                await asyncio.gather(*tasks, return_exceptions=True)

            # Create final checkpoint
            self.checkpoint()

            end_time = datetime.now()
            duration_ms = (end_time - start_time).total_seconds() * 1000

            return {
                "workflow_id": self.workflow_id,
                "success": self.is_successful(),
                "completed": self.is_complete(),
                "cancelled": self._cancelled,
                "duration_ms": duration_ms,
                "results": self._results,
                "node_states": {
                    node_id: {
                        "status": node.status.value,
                        "duration_ms": node.duration_ms
                    }
                    for node_id, node in self._nodes.items()
                }
            }

        except Exception as e:
            self.logger.error(f"DAG execution error: {e}")
            return {
                "workflow_id": self.workflow_id,
                "success": False,
                "error": str(e),
                "results": self._results
            }

    async def _execute_node(
        self,
        node_id: str,
        executor: Callable = None
    ):
        """Execute a single node with retry logic"""
        node = self._nodes.get(node_id)
        if not node:
            return

        async with self._semaphore:
            while node.can_retry:
                try:
                    self.mark_running(node_id)

                    # Determine executor
                    node_executor = node.executor or executor
                    if not node_executor:
                        raise ValueError(f"No executor for node {node_id}")

                    # Execute with timeout
                    result = await asyncio.wait_for(
                        node_executor(node, self._results),
                        timeout=node.timeout
                    )

                    self.mark_completed(node_id, result)
                    self._results[node_id] = result
                    return

                except asyncio.TimeoutError:
                    node.retry_count += 1
                    if node.can_retry:
                        delay = node.retry_delay * (2 ** node.retry_count)
                        self.logger.warning(
                            f"Node {node_id} timed out, retry {node.retry_count}/{node.max_retries} in {delay}s"
                        )
                        node.status = NodeStatus.PENDING
                        await asyncio.sleep(delay)
                    else:
                        self.mark_failed(node_id, f"Timeout after {node.max_retries} retries")

                except Exception as e:
                    node.retry_count += 1
                    if node.can_retry:
                        delay = node.retry_delay * (2 ** node.retry_count)
                        self.logger.warning(
                            f"Node {node_id} failed: {e}, retry {node.retry_count}/{node.max_retries}"
                        )
                        node.status = NodeStatus.PENDING
                        await asyncio.sleep(delay)
                    else:
                        self.mark_failed(node_id, str(e))

    def cancel(self):
        """Cancel the workflow execution"""
        self._cancelled = True
        for node in self._nodes.values():
            if node.status in (NodeStatus.PENDING, NodeStatus.READY):
                node.status = NodeStatus.CANCELLED

    def mark_running(self, node_id: str):
        """Mark a node as running"""
        if node_id in self._nodes:
            self._nodes[node_id].status = NodeStatus.RUNNING
            self._nodes[node_id].started_at = datetime.now()

    def mark_completed(self, node_id: str, result: Any = None):
        """Mark a node as completed"""
        if node_id in self._nodes:
            self._nodes[node_id].status = NodeStatus.COMPLETED
            self._nodes[node_id].result = result
            self._nodes[node_id].completed_at = datetime.now()

    def mark_failed(self, node_id: str, error: str):
        """Mark a node as failed"""
        if node_id in self._nodes:
            self._nodes[node_id].status = NodeStatus.FAILED
            self._nodes[node_id].error = error
            self._nodes[node_id].completed_at = datetime.now()

    def is_complete(self) -> bool:
        """Check if all nodes are completed or failed"""
        return all(
            node.status in (NodeStatus.COMPLETED, NodeStatus.FAILED, NodeStatus.SKIPPED)
            for node in self._nodes.values()
        )

    def is_successful(self) -> bool:
        """Check if workflow completed successfully"""
        return all(
            node.status == NodeStatus.COMPLETED
            for node in self._nodes.values()
        )

    def checkpoint(self, persist: bool = True) -> str:
        """Create a checkpoint of current state"""
        checkpoint_id = f"cp_{self.workflow_id}_{len(self._checkpoints)}_{datetime.now().strftime('%H%M%S')}"

        checkpoint = {
            "id": checkpoint_id,
            "workflow_id": self.workflow_id,
            "timestamp": datetime.now().isoformat(),
            "nodes": {
                node_id: {
                    "status": node.status.value,
                    "result": self._serialize_result(node.result),
                    "error": node.error,
                    "retry_count": node.retry_count,
                    "agent": node.agent,
                    "prompt": node.prompt,
                    "dependencies": list(node.dependencies)
                }
                for node_id, node in self._nodes.items()
            },
            "results": {k: self._serialize_result(v) for k, v in self._results.items()},
            "started": self._started,
            "completed": self._completed,
            "cancelled": self._cancelled
        }

        self._checkpoints.append(checkpoint)
        self._current_checkpoint = checkpoint_id

        # Persist to disk
        if persist:
            checkpoint_file = self._checkpoint_path / f"{checkpoint_id}.json"
            try:
                with open(checkpoint_file, 'w') as f:
                    json.dump(checkpoint, f, indent=2, default=str)
                self.logger.debug(f"Checkpoint persisted: {checkpoint_file}")
            except Exception as e:
                self.logger.warning(f"Failed to persist checkpoint: {e}")

        self.logger.debug(f"Checkpoint created: {checkpoint_id}")
        return checkpoint_id

    def _serialize_result(self, result: Any) -> Any:
        """Serialize result for checkpoint storage"""
        if result is None:
            return None
        if isinstance(result, (str, int, float, bool, list, dict)):
            return result
        return str(result)

    def restore(self, checkpoint_id: str) -> bool:
        """Restore state from a checkpoint (memory or disk)"""
        # Try from memory first
        for checkpoint in self._checkpoints:
            if checkpoint["id"] == checkpoint_id:
                return self._apply_checkpoint(checkpoint)

        # Try from disk
        checkpoint_file = self._checkpoint_path / f"{checkpoint_id}.json"
        if checkpoint_file.exists():
            try:
                with open(checkpoint_file, 'r') as f:
                    checkpoint = json.load(f)
                return self._apply_checkpoint(checkpoint)
            except Exception as e:
                self.logger.error(f"Failed to load checkpoint from disk: {e}")
                return False

        self.logger.warning(f"Checkpoint not found: {checkpoint_id}")
        return False

    def _apply_checkpoint(self, checkpoint: Dict) -> bool:
        """Apply a checkpoint to current state"""
        try:
            for node_id, state in checkpoint["nodes"].items():
                if node_id in self._nodes:
                    self._nodes[node_id].status = NodeStatus(state["status"])
                    self._nodes[node_id].result = state.get("result")
                    self._nodes[node_id].error = state.get("error")
                    self._nodes[node_id].retry_count = state.get("retry_count", 0)

            self._results = checkpoint.get("results", {})
            self._started = checkpoint.get("started", False)
            self._completed = checkpoint.get("completed", False)
            self._cancelled = checkpoint.get("cancelled", False)

            self.logger.debug(f"Restored from checkpoint: {checkpoint['id']}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to apply checkpoint: {e}")
            return False

    @classmethod
    def from_checkpoint(cls, checkpoint_path: Path, checkpoint_id: str) -> Optional['StateMachine']:
        """Create a StateMachine from a persisted checkpoint"""
        checkpoint_file = checkpoint_path / f"{checkpoint_id}.json"
        if not checkpoint_file.exists():
            return None

        try:
            with open(checkpoint_file, 'r') as f:
                checkpoint = json.load(f)

            workflow_id = checkpoint.get("workflow_id", checkpoint_id)
            sm = cls(workflow_id, checkpoint_path)

            # Recreate nodes
            for node_id, state in checkpoint["nodes"].items():
                sm.add_node(
                    node_id=node_id,
                    name=node_id,
                    dependencies=state.get("dependencies", []),
                    agent=state.get("agent"),
                    prompt=state.get("prompt")
                )

            # Apply state
            sm._apply_checkpoint(checkpoint)
            return sm

        except Exception as e:
            get_logger("ai_os.state_machine").error(f"Failed to load from checkpoint: {e}")
            return None

    def get_state(self) -> Dict[str, Any]:
        """Get current state summary"""
        return {
            "workflow_id": self.workflow_id,
            "nodes": {
                node_id: {
                    "name": node.name,
                    "status": node.status.value,
                    "dependencies": list(node.dependencies),
                    "result": str(node.result)[:100] if node.result else None,
                    "error": node.error
                }
                for node_id, node in self._nodes.items()
            },
            "completed": self.is_complete(),
            "successful": self.is_successful(),
            "checkpoints": len(self._checkpoints)
        }

    def visualize(self) -> str:
        """Generate ASCII visualization of DAG"""
        lines = [f"Workflow: {self.workflow_id}", "=" * 40]

        status_symbols = {
            NodeStatus.PENDING: "○",
            NodeStatus.READY: "◐",
            NodeStatus.RUNNING: "●",
            NodeStatus.COMPLETED: "✓",
            NodeStatus.FAILED: "✗",
            NodeStatus.SKIPPED: "-"
        }

        for node_id, node in self._nodes.items():
            symbol = status_symbols.get(node.status, "?")
            deps = f" <- {', '.join(node.dependencies)}" if node.dependencies else ""
            lines.append(f"  {symbol} {node.name}{deps}")

        return "\n".join(lines)
