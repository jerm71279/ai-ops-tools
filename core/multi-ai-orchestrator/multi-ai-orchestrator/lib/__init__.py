"""
Multi-AI Orchestrator Library
"""

from .ai_clients import (
    AIProvider,
    AIResponse,
    BaseAIClient,
    ClaudeCLI,
    GeminiCLI,
    FaraCLI,
    AIClientFactory,
    select_best_client
)

from .orchestrator import (
    Pipeline,
    PipelineStep,
    PipelineResult,
    PipelineBuilder,
    StepStatus,
    create_portal_to_config_pipeline,
    create_log_analysis_pipeline,
    create_sop_capture_pipeline
)

__all__ = [
    # Clients
    "AIProvider",
    "AIResponse", 
    "BaseAIClient",
    "ClaudeCLI",
    "GeminiCLI",
    "FaraCLI",
    "AIClientFactory",
    "select_best_client",
    
    # Orchestration
    "Pipeline",
    "PipelineStep",
    "PipelineResult",
    "PipelineBuilder",
    "StepStatus",
    
    # Templates
    "create_portal_to_config_pipeline",
    "create_log_analysis_pipeline",
    "create_sop_capture_pipeline"
]
