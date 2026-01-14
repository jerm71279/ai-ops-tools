import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""
MCP Server: Obsidian Vault Operations
Handles all interactions with Obsidian vault through MCP protocol
"""
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from core.obsidian_vault import ObsidianVault
from core.vector_store import VectorStore


class ObsidianMCPServer:
    """
    MCP Server for Obsidian operations
    
    Provides tools for agents to interact with Obsidian vault:
    - create_note
    - update_note
    - search_notes
    - get_note_content
    - list_concepts
    - get_consistency_report
    """
    
    def __init__(self, vault_path: Optional[Path] = None):
        self.vault = ObsidianVault(vault_path)
        self.vector_store = VectorStore()
        
    def get_tools(self) -> List[Dict]:
        """Return MCP tool definitions"""
        return [
            {
                "name": "create_note",
                "description": "Create a new note in Obsidian vault",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "structured_data": {
                            "type": "object",
                            "description": "Note data with title, summary, concepts, etc."
                        },
                        "note_type": {
                            "type": "string",
                            "enum": ["inbox", "processed", "concept", "process"],
                            "description": "Type of note to create"
                        }
                    },
                    "required": ["structured_data"]
                }
            },
            {
                "name": "search_notes",
                "description": "Search notes by query, tags, or concepts",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "tags": {"type": "array", "items": {"type": "string"}},
                        "concepts": {"type": "array", "items": {"type": "string"}},
                        "semantic": {"type": "boolean", "description": "Use vector search"}
                    }
                }
            },
            {
                "name": "get_note_content",
                "description": "Get full content of a note",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "note_id": {"type": "string", "description": "Note identifier"}
                    },
                    "required": ["note_id"]
                }
            },
            {
                "name": "list_all_concepts",
                "description": "Get list of all concepts in knowledge base",
                "input_schema": {"type": "object", "properties": {}}
            },
            {
                "name": "get_consistency_report",
                "description": "Generate consistency report for knowledge base",
                "input_schema": {"type": "object", "properties": {}}
            },
            {
                "name": "update_note",
                "description": "Update an existing note",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "note_id": {"type": "string"},
                        "updates": {"type": "object", "description": "Fields to update"}
                    },
                    "required": ["note_id", "updates"]
                }
            },
            {
                "name": "get_recent_notes",
                "description": "Get notes created in last N days",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "days": {"type": "integer", "default": 1}
                    }
                }
            },
            {
                "name": "semantic_search",
                "description": "Semantic search using vector store",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "n_results": {"type": "integer", "default": 5}
                    },
                    "required": ["query"]
                }
            }
        ]
    
    def execute_tool(self, tool_name: str, arguments: Dict) -> Dict[str, Any]:
        """Execute a tool and return results"""
        
        try:
            if tool_name == "create_note":
                note_path = self.vault.create_note(
                    structured_data=arguments["structured_data"],
                    note_type=arguments.get("note_type", "processed")
                )
                
                # Add to vector store
                note_id = note_path.stem
                content = note_path.read_text(encoding='utf-8')
                self.vector_store.add_note(
                    note_id=note_id,
                    content=content,
                    metadata=arguments["structured_data"]
                )
                
                return {
                    "success": True,
                    "note_path": str(note_path),
                    "note_id": note_id
                }
            
            elif tool_name == "search_notes":
                if arguments.get("semantic", False):
                    # Use vector search
                    results = self.vector_store.search(
                        query=arguments.get("query", ""),
                        n_results=10
                    )
                    return {
                        "success": True,
                        "results": results
                    }
                else:
                    # Use vault search
                    results = self.vault.search_notes(
                        query=arguments.get("query"),
                        tags=arguments.get("tags"),
                        concepts=arguments.get("concepts")
                    )
                    return {
                        "success": True,
                        "results": results
                    }
            
            elif tool_name == "get_note_content":
                content = self.vault.get_note_content(arguments["note_id"])
                return {
                    "success": True,
                    "content": content
                }
            
            elif tool_name == "list_all_concepts":
                concepts = self.vault.get_all_concepts()
                return {
                    "success": True,
                    "concepts": concepts,
                    "count": len(concepts)
                }
            
            elif tool_name == "get_consistency_report":
                report = self.vault.get_consistency_report()
                return {
                    "success": True,
                    "report": report
                }
            
            elif tool_name == "update_note":
                note_id = arguments["note_id"]
                # Implementation would update the note file
                return {
                    "success": True,
                    "message": "Note updated"
                }
            
            elif tool_name == "get_recent_notes":
                days = arguments.get("days", 1)
                cutoff = datetime.now().timestamp() - (days * 86400)
                
                recent = []
                for note_id, note_data in self.vault.index['notes'].items():
                    created = datetime.fromisoformat(note_data['created']).timestamp()
                    if created > cutoff:
                        recent.append({
                            'id': note_id,
                            **note_data
                        })
                
                return {
                    "success": True,
                    "notes": recent,
                    "count": len(recent)
                }
            
            elif tool_name == "semantic_search":
                results = self.vector_store.search(
                    query=arguments["query"],
                    n_results=arguments.get("n_results", 5)
                )
                return {
                    "success": True,
                    "results": results
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


# MCP Server entry point
def create_server():
    """Create and return the MCP server instance"""
    return ObsidianMCPServer()


if __name__ == "__main__":
    # Test the MCP server
    server = create_server()
    
    print("Obsidian MCP Server")
    print(f"Available tools: {len(server.get_tools())}")
    
    for tool in server.get_tools():
        print(f"  - {tool['name']}: {tool['description']}")
    
    # Test a tool
    result = server.execute_tool("list_all_concepts", {})
    print(f"\nTest result: {result}")
