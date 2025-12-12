"""
Layer 4: Secondbrain Agent Wrappers
Wraps existing Secondbrain agents for AI OS integration
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ..core.base import AIRequest, AIResponse, TaskStatus
from ..core.logging import get_logger
from .base_agent import BaseAgent


class ObsidianManagerAgent(BaseAgent):
    """
    Wrapper for existing Obsidian Manager agent
    Integrates with mcp_obsidian_server.py
    """

    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.name = "ObsidianManager"
        self.description = "Knowledge base operations via Obsidian vault"
        self.capabilities = ["knowledge", "notes", "search", "organization", "tagging"]
        self.strengths = ["knowledge management", "note organization", "semantic search"]

        self.logger = get_logger("ai_os.agent.obsidian")
        self._mcp_server = None

    async def initialize(self) -> bool:
        """Initialize with existing MCP server"""
        try:
            from mcp_obsidian_server import ObsidianMCPServer
            self._mcp_server = ObsidianMCPServer()
            self._initialized = True
            self._healthy = True
            self.logger.info("Obsidian Manager agent initialized")
            return True
        except ImportError as e:
            self.logger.warning(f"Could not import ObsidianMCPServer: {e}")
            self._initialized = True
            self._healthy = False
            return True

    async def execute(self, request: AIRequest) -> AIResponse:
        """Execute Obsidian operations"""
        if not self._mcp_server:
            return AIResponse.error_response(
                request_id=request.request_id,
                error="Obsidian MCP server not available",
                executed_by="ObsidianManager"
            )

        try:
            # Determine tool based on request
            content = request.content.lower()
            tool_name = "search_notes"  # default
            arguments = {}

            if "create" in content or "add note" in content:
                tool_name = "create_note"
                arguments = {
                    "title": request.context.get("title", "New Note"),
                    "content": request.content,
                    "folder": request.context.get("folder", "inbox")
                }
            elif "search" in content or "find" in content:
                tool_name = "search_notes"
                arguments = {"query": request.content}
            elif "recent" in content or "latest" in content:
                tool_name = "get_recent_notes"
                arguments = {"days": request.context.get("days", 7)}
            elif "consistency" in content or "check" in content:
                tool_name = "get_consistency_report"
                arguments = {}

            result = self._mcp_server.execute_tool(tool_name, arguments)

            return AIResponse(
                request_id=request.request_id,
                success=result.get("success", False),
                content=result,
                status=TaskStatus.SUCCESS if result.get("success") else TaskStatus.FAILED,
                executed_by="ObsidianManager"
            )

        except Exception as e:
            return AIResponse.error_response(
                request_id=request.request_id,
                error=str(e),
                executed_by="ObsidianManager"
            )

    async def shutdown(self) -> bool:
        self._mcp_server = None
        return True


class BAAgent(BaseAgent):
    """
    Wrapper for existing Business Analytics agent
    Integrates with agent_ba.py and SharePoint MCP server
    """

    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.name = "BusinessAnalyst"
        self.description = "Business analytics, project health, quotes, SharePoint document search"
        self.capabilities = ["analytics", "reporting", "quotes", "metrics", "project_health", "sharepoint", "document_search"]
        self.strengths = ["business analytics", "report generation", "project metrics", "time tracking", "SharePoint search"]

        self.logger = get_logger("ai_os.agent.ba")
        self._ba_agent = None
        self._sharepoint_server = None

    async def initialize(self) -> bool:
        """Initialize with existing BA agent and SharePoint MCP"""
        # Initialize BA agent
        try:
            from agent_ba import BAAgent as OriginalBAAgent
            self._ba_agent = OriginalBAAgent()
            self.logger.info("BA agent initialized")
        except ImportError as e:
            self.logger.warning(f"Could not import BAAgent: {e}")

        # Initialize SharePoint MCP server
        try:
            from mcp_sharepoint_server import SharePointMCPServer
            self._sharepoint_server = SharePointMCPServer()
            self.logger.info("SharePoint MCP server connected to BA agent")
        except ImportError as e:
            self.logger.warning(f"Could not import SharePointMCPServer: {e}")

        self._initialized = True
        self._healthy = self._ba_agent is not None or self._sharepoint_server is not None
        return True

    async def execute(self, request: AIRequest) -> AIResponse:
        """Execute BA operations including SharePoint document search"""
        try:
            content = request.content.lower()
            result = None

            # Check for SharePoint-related queries FIRST
            if self._is_sharepoint_query(content):
                return await self._handle_sharepoint_query(request)

            # If no BA agent for other operations, return error
            if not self._ba_agent:
                return AIResponse.error_response(
                    request_id=request.request_id,
                    error="BA agent not available for this operation",
                    executed_by="BusinessAnalyst"
                )

            # Route to appropriate BA function
            if "project health" in content or "health check" in content:
                result = self._ba_agent.analyze_project_health(
                    project_id=request.context.get("project_id")
                )
            elif "utilization" in content or "resource" in content:
                result = self._ba_agent.analyze_resource_utilization(
                    date_range_days=request.context.get("days", 30)
                )
            elif "time" in content or "hours" in content:
                result = self._ba_agent.analyze_time_reports(
                    group_by=request.context.get("group_by", "project"),
                    date_range_days=request.context.get("days", 30)
                )
            elif "quote" in content or "estimate" in content:
                result = self._ba_agent.generate_quote(
                    task_description=request.content,
                    complexity=request.context.get("complexity", "medium")
                )
            else:
                result = self._ba_agent.generate_executive_summary()

            # Convert dataclass to dict if needed
            if hasattr(result, '__dataclass_fields__'):
                from dataclasses import asdict
                result = asdict(result)

            return AIResponse(
                request_id=request.request_id,
                success=True,
                content=result,
                status=TaskStatus.SUCCESS,
                executed_by="BusinessAnalyst"
            )

        except Exception as e:
            return AIResponse.error_response(
                request_id=request.request_id,
                error=str(e),
                executed_by="BusinessAnalyst"
            )

    def _is_sharepoint_query(self, content: str) -> bool:
        """Check if query is SharePoint-related"""
        sharepoint_keywords = [
            "sharepoint", "customer folder", "document library",
            "checklist", "onboarding", "new customer"
        ]
        # Must have sharepoint OR (customer + folder/document)
        has_sharepoint = "sharepoint" in content
        has_customer_docs = ("customer" in content and
                           any(w in content for w in ["folder", "document", "file", "checklist"]))
        return has_sharepoint or has_customer_docs

    async def _handle_sharepoint_query(self, request: AIRequest) -> AIResponse:
        """Handle SharePoint document search queries"""
        if not self._sharepoint_server:
            return AIResponse.error_response(
                request_id=request.request_id,
                error="SharePoint MCP server not available",
                executed_by="BusinessAnalyst"
            )

        try:
            content = request.content.lower()

            # Extract search parameters from the query
            search_query = request.content  # Use original case for search

            # Try to extract customer name (look for capitalized words after "for")
            customer_name = request.context.get("customer")
            if not customer_name:
                # Simple extraction: look for proper nouns
                import re
                # Look for pattern like "for CustomerName" or "CustomerName folder"
                match = re.search(r'for\s+([A-Z][a-zA-Z]+)', request.content)
                if match:
                    customer_name = match.group(1)

            # Determine the tool to use - SharePoint MCP uses "search_items"
            tool_name = "search_items"
            arguments = {"query": search_query}

            # Add customer context to search
            if customer_name:
                # Include customer name in query for better results
                arguments["query"] = f"{customer_name} {search_query}"
                self.logger.info(f"SharePoint search: customer={customer_name}, query={search_query[:50]}")

            # Execute SharePoint search (handle both async and sync servers)
            if hasattr(self._sharepoint_server, 'execute_tool'):
                result = self._sharepoint_server.execute_tool(tool_name, arguments)
                # If result is a coroutine, await it
                if asyncio.iscoroutine(result):
                    result = await result
            elif hasattr(self._sharepoint_server, 'search'):
                result = self._sharepoint_server.search(**arguments)
                if asyncio.iscoroutine(result):
                    result = await result
            else:
                # Fallback: list files in customer folder
                if hasattr(self._sharepoint_server, 'list_files'):
                    result = self._sharepoint_server.list_files(
                        folder_path=arguments.get("folder_path", "/Customers")
                    )
                    if asyncio.iscoroutine(result):
                        result = await result
                else:
                    result = {"error": "No search method available", "query": search_query}

            return AIResponse(
                request_id=request.request_id,
                success=True,
                content={
                    "operation": "sharepoint_search",
                    "customer": customer_name,
                    "query": search_query,
                    "results": result
                },
                status=TaskStatus.SUCCESS,
                executed_by="BusinessAnalyst:SharePoint"
            )

        except Exception as e:
            self.logger.error(f"SharePoint query failed: {e}")
            return AIResponse.error_response(
                request_id=request.request_id,
                error=f"SharePoint search failed: {str(e)}",
                executed_by="BusinessAnalyst:SharePoint"
            )

    async def shutdown(self) -> bool:
        self._ba_agent = None
        self._sharepoint_server = None
        return True


class NotebookLMAgent(BaseAgent):
    """
    Wrapper for existing NotebookLM Analyst agent
    Integrates with mcp_notebooklm_server.py
    """

    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.name = "NotebookLMAnalyst"
        self.description = "Knowledge analysis and pattern detection"
        self.capabilities = ["analysis", "patterns", "feedback", "synthesis"]
        self.strengths = ["knowledge analysis", "pattern detection", "feedback generation"]

        self.logger = get_logger("ai_os.agent.notebooklm")
        self._mcp_server = None

    async def initialize(self) -> bool:
        """Initialize with existing MCP server"""
        try:
            from mcp_notebooklm_server import NotebookLMMCPServer
            self._mcp_server = NotebookLMMCPServer()
            self._initialized = True
            self._healthy = True
            self.logger.info("NotebookLM agent initialized")
            return True
        except ImportError as e:
            self.logger.warning(f"Could not import NotebookLMMCPServer: {e}")
            self._initialized = True
            self._healthy = False
            return True

    async def execute(self, request: AIRequest) -> AIResponse:
        """Execute NotebookLM operations"""
        if not self._mcp_server:
            return AIResponse.error_response(
                request_id=request.request_id,
                error="NotebookLM MCP server not available",
                executed_by="NotebookLMAnalyst"
            )

        try:
            content = request.content.lower()
            tool_name = "simulate_notebooklm_analysis"
            arguments = {}

            if "analyze" in content or "analysis" in content:
                tool_name = "simulate_notebooklm_analysis"
                arguments = {
                    "notes_content": request.context.get("notes", []),
                    "analysis_type": request.context.get("analysis_type", "general")
                }
            elif "feedback" in content:
                tool_name = "process_feedback"
                arguments = {
                    "raw_feedback": request.content,
                    "feedback_source": "user"
                }
            elif "query" in content or "question" in content:
                tool_name = "generate_analysis_queries"
                arguments = {"note_content": request.content}

            result = self._mcp_server.execute_tool(tool_name, arguments)

            return AIResponse(
                request_id=request.request_id,
                success=result.get("success", False),
                content=result,
                status=TaskStatus.SUCCESS if result.get("success") else TaskStatus.FAILED,
                executed_by="NotebookLMAnalyst"
            )

        except Exception as e:
            return AIResponse.error_response(
                request_id=request.request_id,
                error=str(e),
                executed_by="NotebookLMAnalyst"
            )

    async def shutdown(self) -> bool:
        self._mcp_server = None
        return True
