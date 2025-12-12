"""
Agent Orchestrator
Coordinates between all agents with MoE (Mixture of Experts) routing

Agents:
- Obsidian Manager: Knowledge base operator
- NotebookLM Analyst: Knowledge base strategist
- BA Agent: Business Analytics agent
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from queue import Queue
import time

from mcp_obsidian_server import ObsidianMCPServer
from mcp_notebooklm_server import NotebookLMMCPServer

# Import BA Agent and MoE Router
try:
    from agent_ba import BAAgent
    BA_AGENT_AVAILABLE = True
except ImportError:
    BA_AGENT_AVAILABLE = False
    print("Warning: BA Agent not available")

try:
    from moe_router import MoERouter
    MOE_ROUTER_AVAILABLE = True
except ImportError:
    MOE_ROUTER_AVAILABLE = False
    print("Warning: MoE Router not available")


class AgentOrchestrator:
    """
    Coordinates multi-agent system with MoE routing
    - Manages message passing between agents
    - Schedules workflows
    - Tracks agent status
    - Handles errors and escalation
    - Routes tasks via MoE
    """

    def __init__(self, gemini_api_key: str = None):
        # Initialize MCP servers
        self.obsidian_server = ObsidianMCPServer()
        self.notebooklm_server = NotebookLMMCPServer()

        # Initialize BA Agent if available
        self.ba_agent = None
        if BA_AGENT_AVAILABLE:
            self.ba_agent = BAAgent(gemini_api_key=gemini_api_key)
            print("BA Agent initialized")

        # Initialize MoE Router if available
        self.moe_router = None
        if MOE_ROUTER_AVAILABLE:
            self.moe_router = MoERouter(gemini_api_key=gemini_api_key)
            print("MoE Router initialized")

        # Message queues
        self.message_queue = {
            "agent_obsidian": Queue(),
            "agent_notebooklm": Queue(),
            "agent_ba": Queue()
        }

        # Agent status
        self.agents = {
            "agent_obsidian": {
                "status": "ready",
                "last_active": None,
                "tasks_completed": 0,
                "tasks_failed": 0,
                "description": "Knowledge base operator"
            },
            "agent_notebooklm": {
                "status": "ready",
                "last_active": None,
                "tasks_completed": 0,
                "tasks_failed": 0,
                "description": "Knowledge base strategist"
            },
            "agent_ba": {
                "status": "ready" if BA_AGENT_AVAILABLE else "unavailable",
                "last_active": None,
                "tasks_completed": 0,
                "tasks_failed": 0,
                "description": "Business Analytics agent"
            }
        }
        
        # Logs
        self.log_dir = Path("./orchestrator_logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.message_log = self.log_dir / "messages.jsonl"
        self.activity_log = self.log_dir / "activity.log"
    
    def send_message(
        self, 
        from_agent: str, 
        to_agent: str, 
        message: Dict[str, Any]
    ):
        """Send message between agents"""
        
        # Add metadata
        message_envelope = {
            "id": f"msg_{datetime.now().timestamp()}",
            "from": from_agent,
            "to": to_agent,
            "timestamp": datetime.now().isoformat(),
            "message": message
        }
        
        # Queue message
        self.message_queue[to_agent].put(message_envelope)
        
        # Log
        self._log_message(message_envelope)
        
        print(f"📨 Message: {from_agent} → {to_agent} ({message.get('type')})")
    
    def receive_message(self, agent_id: str, timeout: int = 0) -> Optional[Dict]:
        """Receive message for an agent"""
        try:
            if timeout > 0:
                message = self.message_queue[agent_id].get(timeout=timeout)
            else:
                if not self.message_queue[agent_id].empty():
                    message = self.message_queue[agent_id].get_nowait()
                else:
                    return None
            
            print(f"📬 Message received by {agent_id}")
            return message
        except:
            return None
    
    def execute_obsidian_tool(
        self, 
        tool_name: str, 
        arguments: Dict
    ) -> Dict[str, Any]:
        """Execute tool via Obsidian MCP server"""
        
        print(f"🔧 Obsidian tool: {tool_name}")
        result = self.obsidian_server.execute_tool(tool_name, arguments)
        
        self._update_agent_status("agent_obsidian", success=result.get("success", False))
        
        return result
    
    def execute_notebooklm_tool(
        self,
        tool_name: str,
        arguments: Dict
    ) -> Dict[str, Any]:
        """Execute tool via NotebookLM MCP server"""

        print(f"🔧 NotebookLM tool: {tool_name}")
        result = self.notebooklm_server.execute_tool(tool_name, arguments)

        self._update_agent_status("agent_notebooklm", success=result.get("success", False))

        return result

    def execute_ba_task(
        self,
        task_type: str,
        arguments: Dict = None
    ) -> Dict[str, Any]:
        """Execute task via BA Agent"""

        if not self.ba_agent:
            return {"success": False, "error": "BA Agent not available"}

        print(f"📊 BA Agent task: {task_type}")
        arguments = arguments or {}

        try:
            if task_type == "project_health":
                from dataclasses import asdict
                result = self.ba_agent.analyze_project_health(
                    project_id=arguments.get("project_id")
                )
                return {"success": True, "result": asdict(result)}

            elif task_type == "resource_utilization":
                from dataclasses import asdict
                result = self.ba_agent.analyze_resource_utilization(
                    date_range_days=arguments.get("days", 30)
                )
                return {"success": True, "result": asdict(result)}

            elif task_type == "time_report":
                from dataclasses import asdict
                result = self.ba_agent.analyze_time_reports(
                    group_by=arguments.get("group_by", "project"),
                    date_range_days=arguments.get("days", 30)
                )
                return {"success": True, "result": asdict(result)}

            elif task_type == "executive_summary":
                from dataclasses import asdict
                result = self.ba_agent.generate_executive_summary()
                return {"success": True, "result": asdict(result)}

            elif task_type == "quote":
                from dataclasses import asdict
                result = self.ba_agent.generate_quote(
                    task_description=arguments.get("description", ""),
                    complexity=arguments.get("complexity", "medium"),
                    include_buffer=arguments.get("include_buffer", True)
                )
                return {"success": True, "result": asdict(result)}

            else:
                return {"success": False, "error": f"Unknown BA task: {task_type}"}

        except Exception as e:
            self._update_agent_status("agent_ba", success=False)
            return {"success": False, "error": str(e)}

        self._update_agent_status("agent_ba", success=True)

    def route_task(
        self,
        task_description: str,
        data: Dict = None
    ) -> Dict[str, Any]:
        """
        Route a task using MoE Router to the best agent

        This is the main entry point for intelligent task routing
        """

        if not self.moe_router:
            return {"success": False, "error": "MoE Router not available"}

        print(f"\n{'='*60}")
        print(f"🧠 MoE Routing: {task_description[:50]}...")
        print(f"{'='*60}")

        # Get routing decision
        routing = self.moe_router.route_to_best_agent(task_description, context=data)
        agent_id = routing["agent_id"]

        print(f"➡️ Routed to: {routing['agent_name']}")
        print(f"📁 Category: {routing['category']}")
        print(f"💯 Confidence: {routing['confidence']}")

        result = {
            "routing": routing,
            "success": False,
            "result": None,
            "error": None
        }

        # Execute with appropriate agent
        try:
            if agent_id == "agent_ba" and self.ba_agent:
                # Set data if provided
                if data:
                    self.ba_agent.set_data(
                        projects=data.get("projects"),
                        tasks=data.get("tasks"),
                        tickets=data.get("tickets"),
                        time_entries=data.get("time_entries")
                    )

                # Determine task type from category
                category = routing["category"]
                if "project" in category or "health" in category:
                    ba_result = self.execute_ba_task("project_health")
                elif "utilization" in category or "resource" in category:
                    ba_result = self.execute_ba_task("resource_utilization")
                elif "time" in category or "tracking" in category:
                    ba_result = self.execute_ba_task("time_report")
                elif "quote" in category or "estimate" in category:
                    ba_result = self.execute_ba_task("quote", {"description": task_description})
                else:
                    ba_result = self.execute_ba_task("executive_summary")

                result["result"] = ba_result
                result["success"] = ba_result.get("success", False)

            elif agent_id == "agent_obsidian":
                # Route to Obsidian for knowledge management
                result["result"] = {"message": "Task routed to Obsidian Manager"}
                result["success"] = True

            elif agent_id == "agent_notebooklm":
                # Route to NotebookLM for analysis
                result["result"] = {"message": "Task routed to NotebookLM Analyst"}
                result["success"] = True

            else:
                result["error"] = f"Unknown agent: {agent_id}"

        except Exception as e:
            result["error"] = str(e)

        return result
    
    def run_workflow(
        self, 
        agent_id: str, 
        workflow_name: str, 
        context: Dict = None
    ) -> Dict[str, Any]:
        """
        Run a predefined workflow for an agent
        
        This is a simplified orchestration - in production, would be more sophisticated
        """
        
        print(f"\n{'='*60}")
        print(f"🚀 Running workflow: {workflow_name} (Agent: {agent_id})")
        print(f"{'='*60}\n")
        
        workflow_result = {
            "workflow": workflow_name,
            "agent": agent_id,
            "started": datetime.now().isoformat(),
            "steps_completed": [],
            "success": False
        }
        
        try:
            if agent_id == "agent_obsidian":
                if workflow_name == "daily_consistency_check":
                    result = self._run_obsidian_daily_check()
                elif workflow_name == "process_document":
                    result = self._run_obsidian_process_doc(context)
                elif workflow_name == "apply_feedback":
                    result = self._run_obsidian_apply_feedback(context)
                else:
                    result = {"success": False, "error": "Unknown workflow"}
            
            elif agent_id == "agent_notebooklm":
                if workflow_name == "daily_analysis":
                    result = self._run_notebooklm_daily_analysis(context)
                elif workflow_name == "weekly_review":
                    result = self._run_notebooklm_weekly_review()
                else:
                    result = {"success": False, "error": "Unknown workflow"}
            
            else:
                result = {"success": False, "error": "Unknown agent"}
            
            workflow_result["result"] = result
            workflow_result["success"] = result.get("success", False)
            workflow_result["completed"] = datetime.now().isoformat()
            
        except Exception as e:
            workflow_result["error"] = str(e)
            workflow_result["success"] = False
        
        # Log workflow
        self._log_workflow(workflow_result)
        
        return workflow_result
    
    # ========================================================================
    # WORKFLOW IMPLEMENTATIONS
    # ========================================================================
    
    def _run_obsidian_daily_check(self) -> Dict:
        """Run daily consistency check workflow"""
        
        steps = []
        
        # Step 1: Get recent notes
        result = self.execute_obsidian_tool(
            "get_recent_notes",
            {"days": 1}
        )
        steps.append({"step": "get_recent_notes", "success": result.get("success")})
        
        if not result.get("success"):
            return {"success": False, "steps": steps}
        
        recent_notes = result.get("notes", [])
        
        # Step 2: Generate consistency report
        result = self.execute_obsidian_tool(
            "get_consistency_report",
            {}
        )
        steps.append({"step": "get_consistency_report", "success": result.get("success")})
        
        # Step 3: Send to NotebookLM Agent for analysis
        self.send_message(
            from_agent="agent_obsidian",
            to_agent="agent_notebooklm",
            message={
                "type": "analysis_request",
                "data": {
                    "notes": recent_notes,
                    "consistency_report": result.get("report"),
                    "priority": "daily_routine",
                    "focus_areas": ["consistency", "gaps"]
                }
            }
        )
        steps.append({"step": "send_analysis_request", "success": True})
        
        return {
            "success": True,
            "steps": steps,
            "notes_processed": len(recent_notes)
        }
    
    def _run_obsidian_process_doc(self, context: Dict) -> Dict:
        """Process a document workflow"""
        # Implementation would call document_processor and pipeline
        return {"success": True, "message": "Document processed"}
    
    def _run_obsidian_apply_feedback(self, context: Dict) -> Dict:
        """Apply feedback from NotebookLM Agent"""
        
        feedback = context.get("feedback", {})
        steps = []
        
        # Process terminology changes
        for term_change in feedback.get("terminology_changes", []):
            # Search for old term
            result = self.execute_obsidian_tool(
                "search_notes",
                {"query": term_change.get("from")}
            )
            steps.append({"step": f"search_{term_change.get('from')}", "success": result.get("success")})
            
            # Update each note (simplified - would iterate through results)
            # Implementation details would go here
        
        return {
            "success": True,
            "steps": steps,
            "changes_applied": len(steps)
        }
    
    def _run_notebooklm_daily_analysis(self, context: Dict) -> Dict:
        """Run daily analysis workflow"""
        
        steps = []
        
        # Step 1: Get notes from context (sent by Obsidian Agent)
        notes = context.get("data", {}).get("notes", [])
        
        # Step 2: Simulate analysis
        result = self.execute_notebooklm_tool(
            "simulate_notebooklm_analysis",
            {
                "notes_content": [n.get("content", "") for n in notes[:10]],
                "analysis_type": "consistency"
            }
        )
        steps.append({"step": "simulate_analysis", "success": result.get("success")})
        
        if not result.get("success"):
            return {"success": False, "steps": steps}
        
        analysis = result.get("analysis", {})
        
        # Step 3: Process feedback
        result = self.execute_notebooklm_tool(
            "process_feedback",
            {
                "raw_feedback": json.dumps(analysis),
                "feedback_source": "simulated"
            }
        )
        steps.append({"step": "process_feedback", "success": result.get("success")})
        
        processed_feedback = result.get("processed_feedback", {})
        
        # Step 4: Send feedback to Obsidian Agent
        self.send_message(
            from_agent="agent_notebooklm",
            to_agent="agent_obsidian",
            message={
                "type": "analysis_results",
                "feedback": processed_feedback,
                "priority": "daily"
            }
        )
        steps.append({"step": "send_feedback", "success": True})
        
        return {
            "success": True,
            "steps": steps,
            "issues_found": len(analysis.get("consistency_issues", []))
        }
    
    def _run_notebooklm_weekly_review(self) -> Dict:
        """Run weekly review workflow"""
        # Implementation would be more comprehensive
        return {"success": True, "message": "Weekly review complete"}
    
    # ========================================================================
    # SCHEDULING
    # ========================================================================
    
    def schedule_daily_tasks(self):
        """Schedule daily tasks for both agents"""
        
        print("\n" + "="*60)
        print("🕐 Running Daily Tasks")
        print("="*60)
        
        # Obsidian: Daily consistency check
        self.run_workflow("agent_obsidian", "daily_consistency_check")
        
        # Wait for analysis request message
        time.sleep(2)
        
        # NotebookLM: Receive and process
        message = self.receive_message("agent_notebooklm")
        if message:
            self.run_workflow(
                "agent_notebooklm",
                "daily_analysis",
                context=message.get("message", {})
            )
        
        # Wait for feedback
        time.sleep(2)
        
        # Obsidian: Apply feedback
        message = self.receive_message("agent_obsidian")
        if message:
            self.run_workflow(
                "agent_obsidian",
                "apply_feedback",
                context=message.get("message", {})
            )
    
    def schedule_weekly_tasks(self):
        """Schedule weekly tasks"""
        
        print("\n" + "="*60)
        print("📅 Running Weekly Tasks")
        print("="*60)
        
        self.run_workflow("agent_notebooklm", "weekly_review")
    
    # ========================================================================
    # UTILITIES
    # ========================================================================
    
    def _update_agent_status(self, agent_id: str, success: bool):
        """Update agent status after task"""
        self.agents[agent_id]["last_active"] = datetime.now().isoformat()
        if success:
            self.agents[agent_id]["tasks_completed"] += 1
        else:
            self.agents[agent_id]["tasks_failed"] += 1
    
    def _log_message(self, message: Dict):
        """Log message to file"""
        with open(self.message_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(message) + '\n')
    
    def _log_workflow(self, workflow: Dict):
        """Log workflow execution"""
        log_entry = f"[{datetime.now().isoformat()}] Workflow: {workflow['workflow']} - Success: {workflow['success']}\n"
        with open(self.activity_log, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    
    def get_status(self) -> Dict:
        """Get orchestrator status"""
        return {
            "agents": self.agents,
            "message_queues": {
                agent: queue.qsize()
                for agent, queue in self.message_queue.items()
            },
            "timestamp": datetime.now().isoformat()
        }


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main orchestration loop"""
    
    print("="*60)
    print("🤖 Agent Orchestrator Starting")
    print("="*60)
    
    orchestrator = AgentOrchestrator()
    
    print("\n✅ Orchestrator initialized")
    print(f"Status: {json.dumps(orchestrator.get_status(), indent=2)}")
    
    # Example: Run daily tasks
    orchestrator.schedule_daily_tasks()
    
    print("\n✅ Daily tasks complete")
    print(f"Final status: {json.dumps(orchestrator.get_status(), indent=2)}")


if __name__ == "__main__":
    main()
