#!/usr/bin/env python3
"""
Tests for Multi-AI Orchestrator
"""

import pytest
import sys
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestAIClients:
    """Test AI client wrappers"""
    
    def test_ai_provider_enum(self):
        """Test AIProvider enum values"""
        from lib import AIProvider
        
        assert AIProvider.CLAUDE.value == "claude"
        assert AIProvider.GEMINI.value == "gemini"
        assert AIProvider.FARA.value == "fara"
    
    def test_ai_response_dataclass(self):
        """Test AIResponse dataclass"""
        from lib import AIResponse, AIProvider
        
        response = AIResponse(
            provider=AIProvider.CLAUDE,
            success=True,
            content="Test content",
            raw_output="Test output"
        )
        
        assert response.success is True
        assert response.content == "Test content"
        assert response.provider == AIProvider.CLAUDE
    
    def test_select_best_client(self):
        """Test automatic client selection"""
        from lib import select_best_client, AIProvider
        
        # Claude tasks
        assert select_best_client("code_generation") == AIProvider.CLAUDE
        assert select_best_client("config_generation") == AIProvider.CLAUDE
        assert select_best_client("documentation") == AIProvider.CLAUDE
        
        # Gemini tasks
        assert select_best_client("long_document_analysis") == AIProvider.GEMINI
        assert select_best_client("video_analysis") == AIProvider.GEMINI
        
        # Fara tasks
        assert select_best_client("web_automation") == AIProvider.FARA
        assert select_best_client("portal_automation") == AIProvider.FARA
        
        # Default to Claude
        assert select_best_client("unknown_task") == AIProvider.CLAUDE


class TestOrchestrator:
    """Test pipeline orchestrator"""
    
    def test_pipeline_builder(self):
        """Test fluent pipeline builder"""
        from lib import PipelineBuilder, AIProvider
        
        pipeline = (
            PipelineBuilder("test_pipeline")
            .description("Test description")
            .claude_step("step1", "Test prompt 1")
            .gemini_step("step2", "Test prompt 2")
            .build()
        )
        
        assert pipeline.name == "test_pipeline"
        assert pipeline.description == "Test description"
        assert len(pipeline.steps) == 2
        assert pipeline.steps[0].provider == AIProvider.CLAUDE
        assert pipeline.steps[1].provider == AIProvider.GEMINI
    
    def test_pipeline_step_creation(self):
        """Test PipelineStep dataclass"""
        from lib import PipelineStep, AIProvider
        
        step = PipelineStep(
            name="test_step",
            provider=AIProvider.CLAUDE,
            prompt_template="Test {variable}",
            description="Test step"
        )
        
        assert step.name == "test_step"
        assert step.provider == AIProvider.CLAUDE
        assert "{variable}" in step.prompt_template


class TestWorkflows:
    """Test pre-built workflows"""
    
    def test_list_workflows(self):
        """Test listing available workflows"""
        from workflows import list_available_workflows
        
        workflows = list_available_workflows()
        
        assert "customer_onboarding" in workflows
        assert "incident_analysis" in workflows
        assert "sop_from_portal" in workflows
        assert len(workflows) >= 5
    
    def test_get_workflow_invalid(self):
        """Test getting invalid workflow raises error"""
        from workflows import get_workflow
        
        with pytest.raises(ValueError):
            get_workflow("nonexistent_workflow")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
