"""
Layer 3: Orchestration Layer - Main Implementation
Coordinates pipeline execution and workflow management

Includes maker_checker validation for risk-based operation approval.
"""

import asyncio
import time
from typing import Any, Callable, Dict, List, Optional

from ..core.base import AIRequest, AIResponse, LayerInterface, TaskStatus, StateStore
from ..core.config import AIConfig
from ..core.logging import get_logger
from ..core.exceptions import OrchestrationError, PipelineError

from .validator import OrchestrationValidator, classify_risk, create_validator


class OrchestrationLayer(LayerInterface):
    """
    Layer 3: Orchestration Layer

    Responsibilities:
    - Execute multi-step pipelines
    - Coordinate parallel and sequential workflows
    - Manage checkpoints and rollbacks
    - Handle retries and error recovery
    - Schedule and trigger workflows
    """

    def __init__(self, config: AIConfig = None):
        super().__init__("orchestration", config.orchestration if config else {})
        self.config = config or AIConfig()
        self.logger = get_logger("ai_os.layer3")

        # Next layer callback (Layer 4: Agents)
        self._next_layer: Optional[Callable] = None

        # Configuration
        orch_config = self.config.orchestration
        self._max_parallel = orch_config.get("max_parallel_pipelines", 5)
        self._checkpoint_enabled = orch_config.get("checkpoint_enabled", True)
        self._default_timeout = orch_config.get("timeout_default", 300)

        # State management
        self._state_store: Optional[StateStore] = None

        # Active pipelines
        self._active_pipelines: Dict[str, Dict] = {}

        # Workflow registry
        self._workflows: Dict[str, 'Pipeline'] = {}

        # Execution semaphore
        self._semaphore = asyncio.Semaphore(self._max_parallel)

        # Validation (maker_checker integration)
        validation_config = orch_config.get("validation", {})
        self._validator = create_validator(
            enabled=validation_config.get("enabled", True),
            auto_approve_level=validation_config.get("auto_approve_level", "medium")
        )

    async def initialize(self) -> bool:
        """Initialize the orchestration layer"""
        self.logger.info("Initializing Orchestration Layer...")

        # Initialize state store
        self._state_store = StateStore()

        # Register built-in workflows
        self._register_builtin_workflows()

        self._initialized = True
        self._healthy = True
        self.logger.info("Orchestration Layer initialized")
        return True

    async def shutdown(self) -> bool:
        """Shutdown the orchestration layer"""
        self.logger.info("Shutting down Orchestration Layer...")

        # Wait for active pipelines to complete (with timeout)
        if self._active_pipelines:
            self.logger.info(f"Waiting for {len(self._active_pipelines)} active pipelines...")
            await asyncio.sleep(5)  # Give pipelines time to complete

        self._initialized = False
        return True

    def set_next_layer(self, callback: Callable):
        """Set the callback to the next layer (Layer 4: Agents)"""
        self._next_layer = callback

    def register_workflow(self, name: str, workflow: 'Pipeline'):
        """Register a named workflow"""
        self._workflows[name] = workflow
        self.logger.info(f"Registered workflow: {name}")

    def _register_builtin_workflows(self):
        """Register built-in workflow templates"""
        from .pipeline import PipelineBuilder

        # Simple single-agent workflow
        single_agent = (
            PipelineBuilder("single_agent")
            .description("Execute with single agent")
            .step("execute", "Execute the request with the designated agent")
            .build()
        )
        self._workflows["single_agent"] = single_agent

        # Multi-agent collaboration workflow
        multi_agent = (
            PipelineBuilder("multi_agent")
            .description("Collaborate across multiple agents")
            .step("primary", "Execute with primary agent")
            .step("secondary", "Enhance with secondary agents", parallel=True)
            .step("synthesize", "Synthesize results")
            .build()
        )
        self._workflows["multi_agent"] = multi_agent

    async def process(self, request: AIRequest) -> AIResponse:
        """
        Process a request through the orchestration layer

        Steps:
        1. Determine execution strategy
        2. Create or select pipeline
        3. Execute pipeline with checkpoints
        4. Handle errors and retries
        5. Return aggregated response
        """
        start_time = time.time()
        self.logger.layer_start("L3:Orchestration", request.request_id, request.content[:50])

        try:
            async with self._semaphore:
                # Step 1: Determine execution strategy
                strategy = self._determine_strategy(request)

                # Step 2: Create checkpoint
                checkpoint_id = None
                if self._checkpoint_enabled:
                    checkpoint_id = self._create_checkpoint(request)

                # Step 3: Validate request (maker_checker)
                approved, validation_msg, validation_result = self._validator.validate(request, strategy)
                if not approved:
                    self.logger.warning(f"Request {request.request_id[:8]} rejected by validator: {validation_msg}")
                    return AIResponse(
                        request_id=request.request_id,
                        success=False,
                        content=f"Request rejected by validation: {validation_msg}",
                        status=TaskStatus.FAILED,
                        executed_by="L3:Orchestration:Validator",
                        artifacts={"validation_result": validation_result.__dict__ if validation_result else None}
                    )

                # Step 4: Execute based on strategy
                try:
                    if strategy["type"] == "workflow":
                        response = await self._execute_workflow(request, strategy)
                    elif strategy["type"] == "pipeline":
                        response = await self._execute_pipeline(request, strategy)
                    else:
                        # Simple single-step execution
                        response = await self._execute_single(request)

                except Exception as e:
                    # Handle error with possible rollback
                    self.logger.error(f"Execution failed: {e}")

                    if checkpoint_id and self._checkpoint_enabled:
                        self._rollback_checkpoint(checkpoint_id)

                    raise

                # Add layer trace
                response.layer_trace.insert(0, "L3:Orchestration")

                duration_ms = (time.time() - start_time) * 1000
                response.duration_ms = duration_ms
                self._update_stats(response.success, duration_ms)

                self.logger.layer_end("L3:Orchestration", request.request_id, response.success, duration_ms)
                return response

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self._update_stats(False, duration_ms)
            self.logger.error(f"Orchestration Layer error: {e}")

            return AIResponse.error_response(
                request_id=request.request_id,
                error=str(e),
                executed_by="L3:Orchestration"
            )

    def _determine_strategy(self, request: AIRequest) -> Dict[str, Any]:
        """
        Determine execution strategy based on request

        Returns strategy specification
        """
        classification = request.classification or {}

        # Check for explicit workflow
        if request.target_workflow:
            return {
                "type": "workflow",
                "workflow_name": request.target_workflow
            }

        # Check complexity for multi-step
        complexity = classification.get("complexity", "simple")
        requires_multi = classification.get("requires_multi_agent", False)

        if complexity == "complex" or requires_multi:
            return {
                "type": "pipeline",
                "agents": classification.get("suggested_agents", [request.target_agent or "claude"])
            }

        # Default: single execution
        return {
            "type": "single",
            "agent": request.target_agent or "claude"
        }

    async def _execute_single(self, request: AIRequest) -> AIResponse:
        """Execute a single-step request"""
        if self._next_layer:
            return await self._next_layer(request)

        return AIResponse.error_response(
            request_id=request.request_id,
            error="No agent layer configured",
            executed_by="L3:Orchestration"
        )

    async def _execute_workflow(
        self,
        request: AIRequest,
        strategy: Dict
    ) -> AIResponse:
        """Execute a named workflow"""
        workflow_name = strategy.get("workflow_name")

        if workflow_name not in self._workflows:
            raise OrchestrationError(f"Unknown workflow: {workflow_name}")

        workflow = self._workflows[workflow_name]

        # Track active pipeline
        self._active_pipelines[request.request_id] = {
            "workflow": workflow_name,
            "started": time.time(),
            "status": "running"
        }

        try:
            result = await self._run_pipeline(workflow, request)

            self._active_pipelines[request.request_id]["status"] = "completed"
            return result

        finally:
            # Cleanup after delay
            asyncio.create_task(self._cleanup_pipeline(request.request_id))

    async def _execute_pipeline(
        self,
        request: AIRequest,
        strategy: Dict
    ) -> AIResponse:
        """Execute a dynamic pipeline"""
        from .pipeline import PipelineBuilder

        agents = strategy.get("agents", ["claude"])

        # Build dynamic pipeline
        builder = PipelineBuilder(f"dynamic_{request.request_id[:8]}")

        if len(agents) == 1:
            builder.step("execute", f"Execute with {agents[0]}", agent=agents[0])
        else:
            # Primary agent
            builder.step("primary", f"Execute with {agents[0]}", agent=agents[0])

            # Secondary agents - continue even if they fail, 10s timeout (they're enhancements)
            for i, agent in enumerate(agents[1:], 1):
                builder.step(f"secondary_{i}", f"Enhance with {agent}", agent=agent, continue_on_error=True, timeout=10)

            # Synthesis step
            builder.step("synthesize", "Combine results", agent=agents[0])

        pipeline = builder.build()

        # Track and execute
        self._active_pipelines[request.request_id] = {
            "pipeline": "dynamic",
            "agents": agents,
            "started": time.time(),
            "status": "running"
        }

        try:
            result = await self._run_pipeline(pipeline, request)
            self._active_pipelines[request.request_id]["status"] = "completed"
            return result
        finally:
            asyncio.create_task(self._cleanup_pipeline(request.request_id))

    async def _run_pipeline(
        self,
        pipeline: 'Pipeline',
        request: AIRequest
    ) -> AIResponse:
        """Execute a pipeline"""
        context = request.context.copy()
        context["request_content"] = request.content
        context["target_agent"] = request.target_agent

        step_results = []
        current_result = None

        for step in pipeline.steps:
            self.logger.pipeline_step(step.name, "running")

            # Create step request
            step_request = AIRequest(
                request_id=f"{request.request_id}_{step.name}",
                content=step.prompt or request.content,
                request_type=request.request_type,
                source=request.source,
                context=context,
                target_agent=step.agent or request.target_agent,
                parent_id=request.request_id
            )

            # Execute step with timeout
            if self._next_layer:
                try:
                    step_response = await asyncio.wait_for(
                        self._next_layer(step_request),
                        timeout=step.timeout
                    )
                except asyncio.TimeoutError:
                    self.logger.warning(f"Step '{step.name}' timed out after {step.timeout}s")
                    step_response = AIResponse.error_response(
                        request_id=step_request.request_id,
                        error=f"Timeout after {step.timeout}s"
                    )
            else:
                step_response = AIResponse.error_response(
                    request_id=step_request.request_id,
                    error="No agent layer"
                )

            step_results.append({
                "step": step.name,
                "success": step_response.success,
                "content": step_response.content,
                "duration_ms": step_response.duration_ms
            })

            # Update context with step output
            context[step.name] = step_response.content
            current_result = step_response

            if not step_response.success and not step.continue_on_error:
                self.logger.pipeline_step(step.name, "failed")
                break

            self.logger.pipeline_step(step.name, "completed")

        # Build final response
        # Success if primary/first step succeeded (secondary failures are OK if continue_on_error)
        primary_result = next((r for r in step_results if r["step"] in ["primary", "execute"]), None)
        if primary_result:
            final_success = primary_result["success"]
        else:
            # Fallback: success if first step succeeded
            final_success = step_results[0]["success"] if step_results else False

        return AIResponse(
            request_id=request.request_id,
            success=final_success,
            content=current_result.content if current_result else None,
            status=TaskStatus.SUCCESS if final_success else TaskStatus.FAILED,
            steps_completed=len([r for r in step_results if r["success"]]),
            total_steps=len(pipeline.steps),
            executed_by="L3:Orchestration",
            artifacts={"step_results": step_results}
        )

    def _create_checkpoint(self, request: AIRequest) -> str:
        """Create a checkpoint before execution"""
        if self._state_store:
            return self._state_store.checkpoint(f"pre_{request.request_id[:8]}")
        return ""

    def _rollback_checkpoint(self, checkpoint_id: str):
        """Rollback to a checkpoint"""
        if self._state_store and checkpoint_id:
            self._state_store.rollback(checkpoint_id)

    async def _cleanup_pipeline(self, request_id: str, delay: float = 60):
        """Clean up pipeline tracking after delay"""
        await asyncio.sleep(delay)
        if request_id in self._active_pipelines:
            del self._active_pipelines[request_id]

    def get_active_pipelines(self) -> List[Dict]:
        """Get list of active pipelines"""
        return [
            {"request_id": rid, **info}
            for rid, info in self._active_pipelines.items()
        ]

    def list_workflows(self) -> List[str]:
        """List registered workflows"""
        return list(self._workflows.keys())
