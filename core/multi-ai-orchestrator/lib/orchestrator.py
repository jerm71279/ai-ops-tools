#!/usr/bin/env python3
"""
Pipeline Orchestrator
Chain multiple AI CLI tools together for complex workflows

Author: OberaConnect Engineering
Version: 1.0.0
"""

import json
import logging
import time
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable, Union
from pathlib import Path
from enum import Enum
from datetime import datetime
import traceback

from .ai_clients import (
    AIProvider, AIResponse, BaseAIClient, 
    AIClientFactory, select_best_client,
    ClaudeCLI, GeminiCLI, FaraCLI
)

logger = logging.getLogger(__name__)


class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class PipelineStep:
    """A single step in a pipeline"""
    name: str
    provider: AIProvider
    prompt_template: str
    description: str = ""
    
    # Execution options
    timeout: int = 300
    retry_count: int = 1
    retry_delay: int = 5
    
    # Input/output handling
    input_key: Optional[str] = None  # Key from previous step's output
    output_key: str = "result"       # Key to store this step's output
    
    # Conditional execution
    condition: Optional[Callable[[Dict], bool]] = None
    
    # Provider-specific options
    provider_options: Dict[str, Any] = field(default_factory=dict)
    
    # Post-processing
    post_processor: Optional[Callable[[str], Any]] = None


@dataclass
class PipelineResult:
    """Result of a complete pipeline execution"""
    pipeline_name: str
    success: bool
    steps_completed: int
    total_steps: int
    outputs: Dict[str, Any]
    step_results: List[Dict[str, Any]]
    duration_seconds: float
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "pipeline_name": self.pipeline_name,
            "success": self.success,
            "steps_completed": self.steps_completed,
            "total_steps": self.total_steps,
            "outputs": self.outputs,
            "step_results": self.step_results,
            "duration_seconds": self.duration_seconds,
            "error": self.error,
            "timestamp": datetime.now().isoformat()
        }
    
    def save(self, path: Union[str, Path]):
        """Save result to JSON file"""
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2, default=str)


class Pipeline:
    """
    Pipeline orchestrator for chaining AI CLI tools
    
    Example:
        pipeline = Pipeline("customer_onboarding")
        pipeline.add_step(PipelineStep(
            name="extract_portal_data",
            provider=AIProvider.FARA,
            prompt_template="Go to {portal_url} and extract customer information",
        ))
        pipeline.add_step(PipelineStep(
            name="generate_config",
            provider=AIProvider.CLAUDE,
            prompt_template="Generate MikroTik config from: {extract_portal_data}",
        ))
        result = pipeline.execute({"portal_url": "https://example.com"})
    """
    
    def __init__(
        self, 
        name: str, 
        description: str = "",
        output_dir: Optional[Path] = None,
        log_level: int = logging.INFO
    ):
        self.name = name
        self.description = description
        self.steps: List[PipelineStep] = []
        self.output_dir = output_dir or Path("./output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(level=log_level)
    
    def add_step(self, step: PipelineStep) -> "Pipeline":
        """Add a step to the pipeline (chainable)"""
        self.steps.append(step)
        return self
    
    def _format_prompt(self, template: str, context: Dict[str, Any]) -> str:
        """Format prompt template with context variables"""
        try:
            return template.format(**context)
        except KeyError as e:
            logger.warning(f"Missing context key: {e}")
            return template
    
    def _execute_step(
        self, 
        step: PipelineStep, 
        context: Dict[str, Any]
    ) -> tuple[bool, Any, Optional[str]]:
        """Execute a single pipeline step with retry logic"""
        
        # Check condition
        if step.condition and not step.condition(context):
            logger.info(f"Step '{step.name}' skipped (condition not met)")
            return True, None, None
        
        # Get appropriate client
        client = AIClientFactory.get_client(step.provider, timeout=step.timeout)
        
        if not client.is_available:
            return False, None, f"Provider {step.provider.value} is not available"
        
        # Format prompt
        prompt = self._format_prompt(step.prompt_template, context)
        
        # Execute with retries
        last_error = None
        for attempt in range(step.retry_count):
            try:
                logger.info(f"Executing step '{step.name}' (attempt {attempt + 1}/{step.retry_count})")
                
                # Execute based on provider type
                if step.provider == AIProvider.FARA:
                    response = client.execute(
                        task=prompt,
                        **step.provider_options
                    )
                else:
                    response = client.execute(
                        prompt=prompt,
                        **step.provider_options
                    )
                
                if response.success:
                    # Apply post-processor if defined
                    output = response.content
                    if step.post_processor:
                        output = step.post_processor(output)
                    
                    return True, output, None
                else:
                    last_error = response.error
                    
            except Exception as e:
                last_error = str(e)
                logger.error(f"Step '{step.name}' failed: {e}")
                logger.debug(traceback.format_exc())
            
            if attempt < step.retry_count - 1:
                logger.info(f"Retrying in {step.retry_delay} seconds...")
                time.sleep(step.retry_delay)
        
        return False, None, last_error
    
    def execute(
        self, 
        initial_context: Dict[str, Any] = None,
        stop_on_failure: bool = True
    ) -> PipelineResult:
        """
        Execute the complete pipeline
        
        Args:
            initial_context: Initial variables available to all steps
            stop_on_failure: If True, stop pipeline on first failure
        
        Returns:
            PipelineResult with all outputs and status
        """
        start_time = time.time()
        context = initial_context.copy() if initial_context else {}
        step_results = []
        steps_completed = 0
        
        logger.info(f"Starting pipeline '{self.name}' with {len(self.steps)} steps")
        
        for i, step in enumerate(self.steps):
            step_start = time.time()
            logger.info(f"[{i+1}/{len(self.steps)}] {step.name}: {step.description}")
            
            success, output, error = self._execute_step(step, context)
            step_duration = time.time() - step_start
            
            step_result = {
                "step_name": step.name,
                "provider": step.provider.value,
                "status": StepStatus.SUCCESS.value if success else StepStatus.FAILED.value,
                "duration_seconds": step_duration,
                "error": error
            }
            step_results.append(step_result)
            
            if success:
                steps_completed += 1
                if output is not None:
                    context[step.output_key] = output
                    # Also make available by step name
                    context[step.name] = output
            else:
                logger.error(f"Step '{step.name}' failed: {error}")
                if stop_on_failure:
                    break
        
        duration = time.time() - start_time
        all_success = steps_completed == len(self.steps)
        
        result = PipelineResult(
            pipeline_name=self.name,
            success=all_success,
            steps_completed=steps_completed,
            total_steps=len(self.steps),
            outputs=context,
            step_results=step_results,
            duration_seconds=duration,
            error=None if all_success else step_results[-1].get("error")
        )
        
        # Save result
        result_path = self.output_dir / f"{self.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        result.save(result_path)
        logger.info(f"Pipeline result saved to {result_path}")
        
        return result


class PipelineBuilder:
    """Fluent builder for creating pipelines"""
    
    def __init__(self, name: str):
        self.pipeline = Pipeline(name)
        self._current_step_options: Dict[str, Any] = {}
    
    def description(self, desc: str) -> "PipelineBuilder":
        self.pipeline.description = desc
        return self
    
    def output_dir(self, path: Union[str, Path]) -> "PipelineBuilder":
        self.pipeline.output_dir = Path(path)
        self.pipeline.output_dir.mkdir(parents=True, exist_ok=True)
        return self
    
    def step(
        self,
        name: str,
        provider: Union[AIProvider, str],
        prompt: str,
        **kwargs
    ) -> "PipelineBuilder":
        """Add a step to the pipeline"""
        if isinstance(provider, str):
            provider = AIProvider[provider.upper()]
        
        step = PipelineStep(
            name=name,
            provider=provider,
            prompt_template=prompt,
            **kwargs
        )
        self.pipeline.add_step(step)
        return self
    
    def claude_step(self, name: str, prompt: str, **kwargs) -> "PipelineBuilder":
        """Convenience method for adding a Claude step"""
        return self.step(name, AIProvider.CLAUDE, prompt, **kwargs)
    
    def gemini_step(self, name: str, prompt: str, **kwargs) -> "PipelineBuilder":
        """Convenience method for adding a Gemini step"""
        return self.step(name, AIProvider.GEMINI, prompt, **kwargs)
    
    def fara_step(self, name: str, task: str, **kwargs) -> "PipelineBuilder":
        """Convenience method for adding a Fara step"""
        return self.step(name, AIProvider.FARA, task, **kwargs)
    
    def build(self) -> Pipeline:
        """Build and return the pipeline"""
        return self.pipeline


# Pre-built pipeline templates
def create_portal_to_config_pipeline(
    name: str = "portal_to_config",
    portal_url: str = "",
    config_type: str = "mikrotik"
) -> Pipeline:
    """
    Template: Extract data from portal → Generate config
    
    Use case: Customer onboarding, vendor portal scraping
    """
    return (
        PipelineBuilder(name)
        .description(f"Extract data from portal and generate {config_type} configuration")
        .fara_step(
            name="extract_portal_data",
            task="Navigate to {portal_url}, extract all customer/network information, "
                 "and return it as structured JSON",
            description="Extract structured data from portal",
            provider_options={"url": portal_url}
        )
        .claude_step(
            name="generate_config",
            prompt="Based on the following extracted data:\n{extract_portal_data}\n\n"
                   f"Generate a complete {config_type} configuration with proper security settings.",
            description=f"Generate {config_type} config from extracted data"
        )
        .build()
    )


def create_log_analysis_pipeline(
    name: str = "log_analysis",
    log_path: str = ""
) -> Pipeline:
    """
    Template: Analyze large logs → Generate remediation scripts
    
    Use case: Incident response, performance troubleshooting
    """
    return (
        PipelineBuilder(name)
        .description("Analyze logs and generate remediation scripts")
        .gemini_step(
            name="analyze_logs",
            prompt="Analyze the following log file and identify:\n"
                   "1. Error patterns and root causes\n"
                   "2. Performance issues\n"
                   "3. Security concerns\n"
                   "4. Recommended actions\n\n"
                   "Format as structured JSON.",
            description="Deep analysis of log files",
            provider_options={"files": [log_path]}
        )
        .claude_step(
            name="generate_remediation",
            prompt="Based on this log analysis:\n{analyze_logs}\n\n"
                   "Generate:\n"
                   "1. Bash remediation scripts for each issue\n"
                   "2. Monitoring alerts to prevent recurrence\n"
                   "3. Documentation of root causes",
            description="Generate remediation scripts"
        )
        .build()
    )


def create_sop_capture_pipeline(
    name: str = "sop_capture",
    task_url: str = "",
    task_description: str = ""
) -> Pipeline:
    """
    Template: Capture portal workflow → Generate SOP documentation
    
    Use case: Documenting portal procedures for knowledge base
    """
    return (
        PipelineBuilder(name)
        .description("Capture workflow steps and generate SOP documentation")
        .fara_step(
            name="capture_workflow",
            task=f"Perform the following task while documenting each step: {task_description}. "
                 "Return a detailed list of all actions taken with screenshots.",
            description="Execute and capture workflow",
            provider_options={"url": task_url, "screenshot_dir": "./screenshots"}
        )
        .claude_step(
            name="generate_sop",
            prompt="Based on this captured workflow:\n{capture_workflow}\n\n"
                   "Generate a complete Standard Operating Procedure document including:\n"
                   "1. Purpose and scope\n"
                   "2. Prerequisites\n"
                   "3. Step-by-step instructions\n"
                   "4. Screenshots/visual aids references\n"
                   "5. Troubleshooting section\n"
                   "6. Revision history placeholder\n\n"
                   "Format in Markdown suitable for Scribe integration.",
            description="Generate SOP documentation"
        )
        .build()
    )
