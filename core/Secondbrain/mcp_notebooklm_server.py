"""
MCP Server: NotebookLM Operations
Handles NotebookLM analysis workflow

NOTE: Since NotebookLM doesn't have a public API yet, this server provides:
1. Structured workflow for manual NotebookLM operations
2. Placeholders for future API integration
3. Feedback loop management
4. Analysis query templates
"""
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from anthropic import Anthropic

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL


class NotebookLMMCPServer:
    """
    MCP Server for NotebookLM workflow
    
    Provides tools for:
    - prepare_notes_for_upload
    - generate_analysis_queries
    - process_feedback (from NotebookLM insights)
    - create_improvement_plan
    - simulate_analysis (using Claude until NBL API available)
    """
    
    def __init__(self):
        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
        self.feedback_history = Path("./notebooklm_feedback/")
        self.feedback_history.mkdir(parents=True, exist_ok=True)
        
    def get_tools(self) -> List[Dict]:
        """Return MCP tool definitions"""
        return [
            {
                "name": "prepare_notes_export",
                "description": "Prepare notes for NotebookLM upload",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "note_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of note IDs to export"
                        },
                        "export_format": {
                            "type": "string",
                            "enum": ["markdown", "txt"],
                            "default": "markdown"
                        }
                    },
                    "required": ["note_ids"]
                }
            },
            {
                "name": "generate_analysis_queries",
                "description": "Generate smart queries for NotebookLM based on notes",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "note_summaries": {
                            "type": "array",
                            "description": "Summaries of notes to analyze"
                        },
                        "focus_areas": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "What to focus on (consistency, gaps, patterns)"
                        }
                    }
                }
            },
            {
                "name": "simulate_notebooklm_analysis",
                "description": "Simulate NotebookLM analysis using Claude (until API available)",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "notes_content": {
                            "type": "array",
                            "description": "Content of notes to analyze"
                        },
                        "analysis_type": {
                            "type": "string",
                            "enum": ["consistency", "patterns", "gaps", "comprehensive"],
                            "default": "comprehensive"
                        }
                    },
                    "required": ["notes_content"]
                }
            },
            {
                "name": "process_feedback",
                "description": "Process NotebookLM feedback into actionable items",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "raw_feedback": {
                            "type": "string",
                            "description": "Raw insights from NotebookLM"
                        },
                        "feedback_source": {
                            "type": "string",
                            "enum": ["manual", "simulated"],
                            "default": "manual"
                        }
                    },
                    "required": ["raw_feedback"]
                }
            },
            {
                "name": "create_improvement_plan",
                "description": "Create improvement plan from feedback",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "feedback_items": {
                            "type": "array",
                            "description": "Processed feedback items"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["critical", "high", "medium", "low"],
                            "default": "high"
                        }
                    },
                    "required": ["feedback_items"]
                }
            },
            {
                "name": "get_feedback_history",
                "description": "Get historical feedback and improvements",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "days_back": {"type": "integer", "default": 7}
                    }
                }
            },
            {
                "name": "export_for_notebooklm",
                "description": "Export notes to a format ready for NotebookLM upload",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "notes": {"type": "array"},
                        "output_dir": {"type": "string"}
                    },
                    "required": ["notes"]
                }
            }
        ]
    
    def execute_tool(self, tool_name: str, arguments: Dict) -> Dict[str, Any]:
        """Execute a tool and return results"""
        
        try:
            if tool_name == "prepare_notes_export":
                note_ids = arguments["note_ids"]
                export_format = arguments.get("export_format", "markdown")
                
                # Prepare export package
                export_data = {
                    "note_ids": note_ids,
                    "format": export_format,
                    "timestamp": datetime.now().isoformat(),
                    "instructions": self._get_upload_instructions()
                }
                
                return {
                    "success": True,
                    "export_data": export_data,
                    "message": "Notes prepared for NotebookLM upload"
                }
            
            elif tool_name == "generate_analysis_queries":
                summaries = arguments.get("note_summaries", [])
                focus_areas = arguments.get("focus_areas", ["consistency", "gaps", "patterns"])
                
                queries = self._generate_smart_queries(summaries, focus_areas)
                
                return {
                    "success": True,
                    "queries": queries,
                    "count": len(queries)
                }
            
            elif tool_name == "simulate_notebooklm_analysis":
                notes_content = arguments["notes_content"]
                analysis_type = arguments.get("analysis_type", "comprehensive")
                
                analysis = self._simulate_analysis(notes_content, analysis_type)
                
                return {
                    "success": True,
                    "analysis": analysis,
                    "source": "simulated"
                }
            
            elif tool_name == "process_feedback":
                raw_feedback = arguments["raw_feedback"]
                feedback_source = arguments.get("feedback_source", "manual")
                
                processed = self._process_feedback(raw_feedback)
                
                # Save feedback
                self._save_feedback(processed, feedback_source)
                
                return {
                    "success": True,
                    "processed_feedback": processed
                }
            
            elif tool_name == "create_improvement_plan":
                feedback_items = arguments["feedback_items"]
                priority = arguments.get("priority", "high")
                
                plan = self._create_plan(feedback_items, priority)
                
                return {
                    "success": True,
                    "improvement_plan": plan
                }
            
            elif tool_name == "get_feedback_history":
                days_back = arguments.get("days_back", 7)
                history = self._get_history(days_back)
                
                return {
                    "success": True,
                    "history": history
                }
            
            elif tool_name == "export_for_notebooklm":
                notes = arguments["notes"]
                output_dir = Path(arguments.get("output_dir", "./notebooklm_exports"))
                output_dir.mkdir(parents=True, exist_ok=True)
                
                # Create export files
                export_files = []
                for i, note in enumerate(notes):
                    filename = output_dir / f"note_{i+1}_{note.get('id', 'unknown')}.md"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(note.get('content', ''))
                    export_files.append(str(filename))
                
                # Create instructions file
                instructions_file = output_dir / "UPLOAD_INSTRUCTIONS.md"
                with open(instructions_file, 'w', encoding='utf-8') as f:
                    f.write(self._get_upload_instructions())
                
                return {
                    "success": True,
                    "export_files": export_files,
                    "instructions": str(instructions_file),
                    "total_notes": len(notes)
                }
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_smart_queries(
        self, 
        summaries: List[str], 
        focus_areas: List[str]
    ) -> List[Dict]:
        """Generate analysis queries based on note summaries"""
        
        queries = []
        
        if "consistency" in focus_areas:
            queries.extend([
                {
                    "query": "What terminology is used inconsistently across these documents?",
                    "purpose": "Identify terminology conflicts"
                },
                {
                    "query": "What concepts appear with different definitions or descriptions?",
                    "purpose": "Find concept inconsistencies"
                },
                {
                    "query": "Are there any contradictions in process descriptions?",
                    "purpose": "Detect process conflicts"
                }
            ])
        
        if "gaps" in focus_areas:
            queries.extend([
                {
                    "query": "What topics are mentioned but not fully documented?",
                    "purpose": "Identify documentation gaps"
                },
                {
                    "query": "What processes reference undocumented steps or procedures?",
                    "purpose": "Find missing process documentation"
                },
                {
                    "query": "What acronyms or terms are used without definition?",
                    "purpose": "Identify undefined terms"
                }
            ])
        
        if "patterns" in focus_areas:
            queries.extend([
                {
                    "query": "What themes or patterns emerge across these documents?",
                    "purpose": "Identify common themes"
                },
                {
                    "query": "What are the relationships between different processes or concepts?",
                    "purpose": "Map concept relationships"
                },
                {
                    "query": "What standards or best practices are implied but not explicitly stated?",
                    "purpose": "Extract implicit knowledge"
                }
            ])
        
        return queries
    
    def _simulate_analysis(
        self, 
        notes_content: List[str], 
        analysis_type: str
    ) -> Dict:
        """
        Simulate NotebookLM analysis using Claude
        This is temporary until NotebookLM API becomes available
        """
        
        # Combine notes content
        combined_content = "\n\n---\n\n".join(notes_content[:10])  # Limit to prevent token overflow
        
        analysis_prompts = {
            "consistency": "Analyze these documents for terminology and concept consistency. Identify conflicts, inconsistencies, and areas needing standardization.",
            "patterns": "Identify patterns, themes, and relationships across these documents. What common structures or approaches emerge?",
            "gaps": "Identify gaps in documentation. What topics are mentioned but not explained? What processes have missing steps?",
            "comprehensive": "Provide comprehensive analysis covering: 1) Consistency issues, 2) Patterns and themes, 3) Documentation gaps, 4) Recommendations for improvement."
        }
        
        prompt = f"""{analysis_prompts.get(analysis_type, analysis_prompts['comprehensive'])}

DOCUMENTS:
{combined_content}

Provide your analysis in JSON format:
{{
    "consistency_issues": [
        {{"issue": "...", "affected_docs": [...], "recommendation": "..."}}
    ],
    "patterns": [
        {{"pattern": "...", "significance": "...", "examples": [...]}}
    ],
    "gaps": [
        {{"gap": "...", "priority": "high|medium|low", "suggestion": "..."}}
    ],
    "overall_insights": "...",
    "recommendations": [...]
}}

RESPOND ONLY WITH VALID JSON."""
        
        try:
            response = self.client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=800,  # REDUCED from 4000 - forces concise analysis
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            response_text = response.content[0].text.strip()
            
            # Clean JSON
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            analysis = json.loads(response_text.strip())
            analysis['analysis_type'] = analysis_type
            analysis['timestamp'] = datetime.now().isoformat()
            
            return analysis
            
        except Exception as e:
            return {
                "error": str(e),
                "analysis_type": analysis_type
            }
    
    def _process_feedback(self, raw_feedback: str) -> Dict:
        """Process raw feedback into structured actions"""
        
        prompt = f"""Process this feedback from knowledge base analysis into actionable items.

FEEDBACK:
{raw_feedback}

Structure it into:
{{
    "terminology_changes": [
        {{"from": "old term", "to": "new term", "reason": "...", "affected_notes": [...]}}
    ],
    "content_updates": [
        {{"note_id": "...", "update_type": "clarify|expand|standardize", "description": "..."}}
    ],
    "new_documentation_needed": [
        {{"topic": "...", "priority": "high|medium|low", "rationale": "..."}}
    ],
    "linking_improvements": [
        {{"note_a": "...", "note_b": "...", "relationship": "..."}}
    ],
    "process_improvements": [
        {{"area": "...", "current_issue": "...", "proposed_fix": "..."}}
    ]
}}

RESPOND ONLY WITH VALID JSON."""
        
        try:
            response = self.client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=600,  # REDUCED from 3000 - forces concise feedback
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            response_text = response.content[0].text.strip()
            
            # Clean JSON
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            processed = json.loads(response_text.strip())
            processed['processed_at'] = datetime.now().isoformat()
            
            return processed
            
        except Exception as e:
            return {
                "error": str(e),
                "raw_feedback": raw_feedback
            }
    
    def _create_plan(self, feedback_items: List[Dict], priority: str) -> Dict:
        """Create improvement plan from feedback"""
        
        plan = {
            "created_at": datetime.now().isoformat(),
            "priority": priority,
            "immediate_actions": [],
            "short_term_actions": [],
            "long_term_actions": [],
            "estimated_impact": {}
        }
        
        # Categorize actions
        for item in feedback_items:
            if item.get("priority") == "high" or "critical" in str(item).lower():
                plan["immediate_actions"].append(item)
            elif item.get("priority") == "medium":
                plan["short_term_actions"].append(item)
            else:
                plan["long_term_actions"].append(item)
        
        return plan
    
    def _save_feedback(self, processed_feedback: Dict, source: str):
        """Save feedback to history"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.feedback_history / f"feedback_{source}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(processed_feedback, f, indent=2)
    
    def _get_history(self, days_back: int) -> List[Dict]:
        """Get feedback history"""
        cutoff = datetime.now().timestamp() - (days_back * 86400)
        history = []
        
        for feedback_file in self.feedback_history.glob("feedback_*.json"):
            if feedback_file.stat().st_mtime > cutoff:
                with open(feedback_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data['file'] = feedback_file.name
                    history.append(data)
        
        return sorted(history, key=lambda x: x.get('processed_at', ''), reverse=True)
    
    def _get_upload_instructions(self) -> str:
        """Get instructions for uploading to NotebookLM"""
        return """# NotebookLM Upload Instructions

## Step 1: Access NotebookLM
1. Go to https://notebooklm.google.com
2. Sign in with your Google account
3. Click "New Notebook"

## Step 2: Upload Notes
1. Click "Add Source"
2. Select "Upload File"
3. Upload the exported markdown files (up to 50 sources)
4. Wait for processing to complete

## Step 3: Run Analysis Queries
Use the provided queries to analyze your knowledge base:

### Consistency Queries:
- "What terminology is used inconsistently across these documents?"
- "What concepts appear with different definitions?"
- "Are there contradictions in process descriptions?"

### Gap Analysis:
- "What topics are mentioned but not fully documented?"
- "What processes reference undocumented steps?"
- "What terms are used without definition?"

### Pattern Recognition:
- "What themes emerge across these documents?"
- "What relationships exist between concepts?"
- "What standards are implied but not stated?"

## Step 4: Export Insights
1. Copy NotebookLM's responses
2. Save to a text file
3. Provide to the NotebookLM Agent for processing

## Step 5: Generate Audio Overview (Optional)
- Click "Audio Overview" in NotebookLM
- Download the AI-generated podcast
- Share with team for knowledge review
"""


# MCP Server entry point
def create_server():
    """Create and return the MCP server instance"""
    return NotebookLMMCPServer()


if __name__ == "__main__":
    # Test the MCP server
    server = create_server()
    
    print("NotebookLM MCP Server")
    print(f"Available tools: {len(server.get_tools())}")
    
    for tool in server.get_tools():
        print(f"  - {tool['name']}: {tool['description']}")
    
    # Test generating queries
    result = server.execute_tool(
        "generate_analysis_queries",
        {
            "note_summaries": ["Process doc 1", "Process doc 2"],
            "focus_areas": ["consistency", "gaps"]
        }
    )
    print(f"\nGenerated queries: {len(result.get('queries', []))}")
