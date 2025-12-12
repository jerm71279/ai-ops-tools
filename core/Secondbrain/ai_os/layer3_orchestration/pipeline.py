"""
Layer 3: Pipeline Definition and Builder
Defines pipeline structure and provides fluent builder
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class PipelineStep:
    """A single step in a pipeline"""
    name: str
    description: str = ""
    prompt: Optional[str] = None
    agent: Optional[str] = None

    # Execution options
    timeout: int = 300
    retry_count: int = 1
    continue_on_error: bool = False
    parallel: bool = False

    # Conditional execution
    condition: Optional[Callable[[Dict], bool]] = None

    # Post-processing
    post_processor: Optional[Callable[[Any], Any]] = None


@dataclass
class Pipeline:
    """Pipeline definition"""
    name: str
    description: str = ""
    steps: List[PipelineStep] = field(default_factory=list)

    # Pipeline options
    stop_on_failure: bool = True
    max_duration: int = 3600  # 1 hour max

    def add_step(self, step: PipelineStep) -> 'Pipeline':
        """Add a step to the pipeline"""
        self.steps.append(step)
        return self

    def get_step(self, name: str) -> Optional[PipelineStep]:
        """Get step by name"""
        for step in self.steps:
            if step.name == name:
                return step
        return None


class PipelineBuilder:
    """
    Fluent builder for creating pipelines

    Example:
        pipeline = (
            PipelineBuilder("my_workflow")
            .description("My custom workflow")
            .step("step1", "First step", agent="claude")
            .step("step2", "Second step", agent="gemini", parallel=True)
            .build()
        )
    """

    def __init__(self, name: str):
        self._pipeline = Pipeline(name=name)
        self._current_step: Optional[PipelineStep] = None

    def description(self, desc: str) -> 'PipelineBuilder':
        """Set pipeline description"""
        self._pipeline.description = desc
        return self

    def step(
        self,
        name: str,
        description: str = "",
        prompt: str = None,
        agent: str = None,
        timeout: int = 300,
        retry_count: int = 1,
        continue_on_error: bool = False,
        parallel: bool = False,
        condition: Callable = None,
        post_processor: Callable = None
    ) -> 'PipelineBuilder':
        """Add a step to the pipeline"""
        step = PipelineStep(
            name=name,
            description=description,
            prompt=prompt,
            agent=agent,
            timeout=timeout,
            retry_count=retry_count,
            continue_on_error=continue_on_error,
            parallel=parallel,
            condition=condition,
            post_processor=post_processor
        )
        self._pipeline.add_step(step)
        self._current_step = step
        return self

    def with_timeout(self, timeout: int) -> 'PipelineBuilder':
        """Set timeout for current step"""
        if self._current_step:
            self._current_step.timeout = timeout
        return self

    def with_retries(self, count: int) -> 'PipelineBuilder':
        """Set retry count for current step"""
        if self._current_step:
            self._current_step.retry_count = count
        return self

    def continue_on_error(self) -> 'PipelineBuilder':
        """Allow pipeline to continue if current step fails"""
        if self._current_step:
            self._current_step.continue_on_error = True
        return self

    def when(self, condition: Callable[[Dict], bool]) -> 'PipelineBuilder':
        """Set condition for current step"""
        if self._current_step:
            self._current_step.condition = condition
        return self

    def then(self, post_processor: Callable[[Any], Any]) -> 'PipelineBuilder':
        """Set post-processor for current step"""
        if self._current_step:
            self._current_step.post_processor = post_processor
        return self

    def stop_on_failure(self, stop: bool = True) -> 'PipelineBuilder':
        """Set whether pipeline stops on first failure"""
        self._pipeline.stop_on_failure = stop
        return self

    def max_duration(self, seconds: int) -> 'PipelineBuilder':
        """Set maximum pipeline duration"""
        self._pipeline.max_duration = seconds
        return self

    def build(self) -> Pipeline:
        """Build and return the pipeline"""
        return self._pipeline


# Pre-built pipeline templates
def customer_onboarding_pipeline() -> Pipeline:
    """Template: Customer onboarding workflow"""
    return (
        PipelineBuilder("customer_onboarding")
        .description("Complete customer onboarding workflow")
        .step(
            "extract_info",
            "Extract customer information from portal",
            agent="fara"
        )
        .step(
            "generate_network_config",
            "Generate network configuration",
            prompt="Generate MikroTik/SonicWall config from: {extract_info}",
            agent="claude"
        )
        .step(
            "create_documentation",
            "Create onboarding documentation",
            prompt="Create onboarding docs from: {generate_network_config}",
            agent="claude"
        )
        .step(
            "update_knowledge_base",
            "Update knowledge base",
            agent="obsidian"
        )
        .build()
    )


def incident_analysis_pipeline() -> Pipeline:
    """Template: Incident analysis workflow"""
    return (
        PipelineBuilder("incident_analysis")
        .description("Analyze incident and generate remediation")
        .step(
            "analyze_logs",
            "Analyze log files",
            agent="gemini"
        )
        .with_timeout(600)  # 10 minutes for large logs
        .step(
            "correlate_events",
            "Correlate events across sources",
            prompt="Correlate events from: {analyze_logs}",
            agent="claude"
        )
        .step(
            "generate_remediation",
            "Generate remediation scripts",
            prompt="Generate remediation for: {correlate_events}",
            agent="claude"
        )
        .step(
            "create_report",
            "Create incident report",
            prompt="Create incident report from analysis: {correlate_events}, remediation: {generate_remediation}",
            agent="claude"
        )
        .build()
    )


def sop_creation_pipeline() -> Pipeline:
    """Template: SOP creation workflow"""
    return (
        PipelineBuilder("sop_creation")
        .description("Capture and document SOP")
        .step(
            "capture_workflow",
            "Capture workflow steps from portal",
            agent="fara"
        )
        .step(
            "generate_sop",
            "Generate SOP document",
            prompt="Generate Scribe-style SOP from: {capture_workflow}",
            agent="claude"
        )
        .step(
            "store_sop",
            "Store SOP in knowledge base",
            agent="obsidian"
        )
        .build()
    )
