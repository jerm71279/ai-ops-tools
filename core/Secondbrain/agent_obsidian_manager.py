"""
Agent 1: Obsidian Knowledge Base Manager

ROLE: Primary knowledge base maintainer
RESPONSIBILITY: Process documents, maintain consistency, manage vault structure

This agent uses the Obsidian MCP Server to manage the knowledge base
"""

# ============================================================================
# AGENT IDENTITY
# ============================================================================

AGENT_NAME = "Obsidian Manager"
AGENT_ID = "agent_obsidian"
VERSION = "1.0.0"

CORE_RESPONSIBILITIES = [
    "Process incoming documents into structured notes",
    "Maintain knowledge base consistency",
    "Manage vault organization and structure",
    "Index notes in vector store",
    "Respond to NotebookLM Agent feedback",
    "Generate consistency reports"
]

# ============================================================================
# MCP TOOLS AVAILABLE
# ============================================================================

AVAILABLE_TOOLS = [
    "create_note",           # Create new notes
    "update_note",           # Update existing notes
    "search_notes",          # Search vault
    "semantic_search",       # Vector search
    "get_note_content",      # Read notes
    "list_all_concepts",     # Get concepts
    "get_consistency_report",# Generate reports
    "get_recent_notes"       # Get recent work
]

# ============================================================================
# WORKFLOWS
# ============================================================================

WORKFLOWS = {
    
    # Workflow 1: Process New Document
    "process_document": {
        "trigger": "New document arrives in input folder",
        "steps": [
            {
                "step": 1,
                "action": "Extract content from document",
                "tool": "document_processor",
                "output": "raw_content"
            },
            {
                "step": 2,
                "action": "Get existing concepts for context",
                "tool": "list_all_concepts",
                "output": "existing_concepts"
            },
            {
                "step": 3,
                "action": "Semantic search for similar notes",
                "tool": "semantic_search",
                "input": "raw_content[:500]",  # First 500 chars
                "output": "similar_notes"
            },
            {
                "step": 4,
                "action": "Structure content with Claude",
                "tool": "claude_processor",
                "input": ["raw_content", "existing_concepts", "similar_notes"],
                "output": "structured_note"
            },
            {
                "step": 5,
                "action": "Check consistency",
                "tool": "claude_processor.check_consistency",
                "input": "structured_note",
                "output": "consistency_check"
            },
            {
                "step": 6,
                "action": "Create note in vault",
                "tool": "create_note",
                "input": "structured_note",
                "output": "note_created"
            },
            {
                "step": 7,
                "action": "Log consistency issues if any",
                "condition": "consistency_check has issues",
                "output": "issues_logged"
            }
        ],
        "success_criteria": "Note created, indexed, consistency checked",
        "failure_handling": "Log error, move to manual review folder"
    },
    
    # Workflow 2: Daily Consistency Check
    "daily_consistency_check": {
        "trigger": "Scheduled daily (end of day)",
        "steps": [
            {
                "step": 1,
                "action": "Get recent notes (last 24 hours)",
                "tool": "get_recent_notes",
                "params": {"days": 1},
                "output": "todays_notes"
            },
            {
                "step": 2,
                "action": "Generate consistency report",
                "tool": "get_consistency_report",
                "output": "consistency_report"
            },
            {
                "step": 3,
                "action": "Prepare notes for NotebookLM analysis",
                "tool": "prepare_export",
                "input": "todays_notes",
                "output": "export_package"
            },
            {
                "step": 4,
                "action": "Send export package to NotebookLM Agent",
                "tool": "agent_communication",
                "recipient": "agent_notebooklm",
                "message": {
                    "type": "analysis_request",
                    "data": "export_package",
                    "priority": "daily_routine"
                }
            }
        ],
        "success_criteria": "Report generated, notes exported, request sent",
        "next_action": "Wait for NotebookLM Agent feedback"
    },
    
    # Workflow 3: Apply Feedback from NotebookLM Agent
    "apply_feedback": {
        "trigger": "Receive feedback from NotebookLM Agent",
        "steps": [
            {
                "step": 1,
                "action": "Parse feedback message",
                "input": "feedback_message",
                "output": "parsed_feedback"
            },
            {
                "step": 2,
                "action": "Prioritize actions",
                "logic": "Sort by priority: critical > high > medium > low",
                "output": "prioritized_actions"
            },
            {
                "step": 3,
                "action": "Process terminology changes",
                "iterate": "feedback.terminology_changes",
                "for_each": {
                    "search": "Find all notes using old term",
                    "tool": "search_notes",
                    "update": "Update term in each note",
                    "tool": "update_note"
                },
                "output": "terms_updated"
            },
            {
                "step": 4,
                "action": "Create missing documentation",
                "iterate": "feedback.new_documentation_needed",
                "for_each": {
                    "create": "Create placeholder note",
                    "tool": "create_note",
                    "tag": "needs-content"
                },
                "output": "placeholders_created"
            },
            {
                "step": 5,
                "action": "Update linking",
                "iterate": "feedback.linking_improvements",
                "for_each": {
                    "update": "Add links between notes",
                    "tool": "update_note"
                },
                "output": "links_updated"
            },
            {
                "step": 6,
                "action": "Send completion report to NotebookLM Agent",
                "tool": "agent_communication",
                "recipient": "agent_notebooklm",
                "message": {
                    "type": "feedback_applied",
                    "summary": "terms_updated + placeholders_created + links_updated"
                }
            }
        ],
        "success_criteria": "All feedback actions processed",
        "metrics": "Track: terms updated, notes created, links added"
    },
    
    # Workflow 4: Batch Update (for major consistency fixes)
    "batch_update": {
        "trigger": "Manual trigger or critical consistency issue",
        "steps": [
            {
                "step": 1,
                "action": "Get update specification",
                "input": "update_spec",  # What to update, how to update it
                "validate": "Ensure spec is safe and reversible"
            },
            {
                "step": 2,
                "action": "Create backup",
                "tool": "vault_backup",
                "output": "backup_path"
            },
            {
                "step": 3,
                "action": "Search affected notes",
                "tool": "search_notes",
                "input": "update_spec.search_criteria",
                "output": "affected_notes"
            },
            {
                "step": 4,
                "action": "Apply updates",
                "iterate": "affected_notes",
                "for_each": {
                    "tool": "update_note",
                    "log": "changes_made"
                },
                "output": "update_results"
            },
            {
                "step": 5,
                "action": "Verify updates",
                "tool": "get_consistency_report",
                "validate": "Check if issue resolved"
            },
            {
                "step": 6,
                "action": "Send report to NotebookLM Agent",
                "message": {
                    "type": "batch_update_complete",
                    "notes_affected": "count",
                    "changes": "summary"
                }
            }
        ],
        "success_criteria": "All updates applied, consistency improved",
        "rollback": "If validation fails, restore from backup"
    },
    
    # Workflow 5: Export for External Use
    "export_documentation": {
        "trigger": "Request for formal documentation",
        "steps": [
            {
                "step": 1,
                "action": "Get notes by concept or tag",
                "tool": "search_notes",
                "input": "export_criteria",
                "output": "notes_to_export"
            },
            {
                "step": 2,
                "action": "Order notes logically",
                "logic": "Organize by hierarchy or flow"
            },
            {
                "step": 3,
                "action": "Format for target (PDF, DOCX, etc)",
                "tool": "document_generator"
            },
            {
                "step": 4,
                "action": "Export to output location"
            }
        ],
        "success_criteria": "Document exported in requested format"
    }
}

# ============================================================================
# DECISION LOGIC
# ============================================================================

DECISION_RULES = {
    "when_to_create_concept_note": {
        "condition": "Concept appears in 3+ notes without definition",
        "action": "Create dedicated concept note"
    },
    
    "when_to_flag_for_review": {
        "conditions": [
            "Consistency score < 0.7",
            "Terminology conflicts > 5",
            "Missing critical links > 10"
        ],
        "action": "Flag for human review, notify NotebookLM Agent"
    },
    
    "when_to_trigger_batch_update": {
        "condition": "Same issue appears in 10+ notes",
        "action": "Suggest batch update to NotebookLM Agent"
    },
    
    "note_type_determination": {
        "rules": [
            {"if": "contains process steps", "then": "note_type = process"},
            {"if": "defines concept", "then": "note_type = concept"},
            {"if": "general information", "then": "note_type = processed"}
        ]
    }
}

# ============================================================================
# COMMUNICATION PROTOCOL with NotebookLM Agent
# ============================================================================

MESSAGE_TYPES = {
    "analysis_request": {
        "from": "agent_obsidian",
        "to": "agent_notebooklm",
        "payload": {
            "notes": "List of note IDs",
            "priority": "daily_routine | weekly_review | critical",
            "focus_areas": ["consistency", "gaps", "patterns"]
        },
        "expected_response": "analysis_results"
    },
    
    "feedback_applied": {
        "from": "agent_obsidian",
        "to": "agent_notebooklm",
        "payload": {
            "feedback_id": "str",
            "actions_taken": "summary",
            "metrics": "dict of changes"
        }
    },
    
    "critical_issue": {
        "from": "agent_obsidian",
        "to": "agent_notebooklm",
        "payload": {
            "issue_type": "consistency | structure | data_quality",
            "severity": "critical | high | medium",
            "details": "description",
            "affected_notes": "list"
        },
        "expected_response": "guidance"
    },
    
    "status_report": {
        "from": "agent_obsidian",
        "to": "agent_notebooklm",
        "payload": {
            "period": "daily | weekly",
            "notes_processed": "int",
            "consistency_score": "float",
            "issues_resolved": "int",
            "pending_issues": "int"
        }
    }
}

# ============================================================================
# PERFORMANCE METRICS
# ============================================================================

METRICS_TO_TRACK = {
    "daily": [
        "notes_processed",
        "consistency_score",
        "terminology_conflicts",
        "missing_links",
        "processing_time_avg"
    ],
    
    "weekly": [
        "total_notes_in_vault",
        "concepts_documented",
        "consistency_improvement",
        "feedback_actions_completed",
        "user_queries_answered"  # from RAG
    ],
    
    "monthly": [
        "knowledge_base_growth",
        "consistency_trend",
        "documentation_completeness",
        "agent_efficiency"
    ]
}

# ============================================================================
# ERROR HANDLING
# ============================================================================

ERROR_RESPONSES = {
    "note_creation_failed": {
        "action": "Log error, move to manual review",
        "notify": "human operator",
        "retry": False
    },
    
    "consistency_check_failed": {
        "action": "Skip consistency check, proceed with creation",
        "log": "warning",
        "retry": False
    },
    
    "communication_failure": {
        "action": "Queue message for retry",
        "retry": True,
        "max_retries": 3,
        "backoff": "exponential"
    },
    
    "vault_corruption": {
        "action": "STOP all operations",
        "notify": "human operator immediately",
        "severity": "critical"
    }
}

# ============================================================================
# INITIALIZATION
# ============================================================================

def initialize_agent():
    """Initialize the Obsidian Manager Agent"""
    return {
        "name": AGENT_NAME,
        "id": AGENT_ID,
        "version": VERSION,
        "status": "ready",
        "mcp_servers": ["obsidian_server", "vector_store"],
        "partner_agent": "agent_notebooklm"
    }


if __name__ == "__main__":
    agent = initialize_agent()
    print(f"Agent: {agent['name']} (v{agent['version']})")
    print(f"Status: {agent['status']}")
    print(f"\nCore Responsibilities ({len(CORE_RESPONSIBILITIES)}):")
    for resp in CORE_RESPONSIBILITIES:
        print(f"  - {resp}")
    print(f"\nWorkflows Available ({len(WORKFLOWS)}):")
    for workflow_name in WORKFLOWS.keys():
        print(f"  - {workflow_name}")
