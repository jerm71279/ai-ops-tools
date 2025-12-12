#!/usr/bin/env python3
"""
Agentic RAG - Claude-powered agent with tool use for complex queries
Enables multi-step reasoning and data retrieval for sophisticated queries
"""
import os
import json
from typing import List, Dict, Any, Optional
from anthropic import Anthropic
from structured_store import StructuredStore
from vector_store import VectorStore
from pathlib import Path
from config import CHROMA_DB_DIR, OBSIDIAN_VAULT_PATH


class AgenticRAG:
    """Agent-based RAG system with tool use for complex queries"""

    def __init__(self, structured_store: StructuredStore, vector_store: VectorStore):
        self.structured_store = structured_store
        self.vector_store = vector_store
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        # Define tools available to the agent
        self.tools = [
            {
                "name": "count_customers",
                "description": "Get the total count of customers in the database. Use this for questions like 'how many customers' or 'total customers'.",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "list_customers",
                "description": "Get a list of customer names. Use limit parameter to control how many to return.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of customers to return (default 20)",
                            "default": 20
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "get_customer_details",
                "description": "Get detailed information about a specific customer including their projects and tickets.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "customer_name": {
                            "type": "string",
                            "description": "The name of the customer to look up"
                        }
                    },
                    "required": ["customer_name"]
                }
            },
            {
                "name": "count_projects",
                "description": "Get the count of projects, optionally filtered by status.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "description": "Optional status filter (e.g., 'In Progress', 'Not Started', 'Completed')"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "get_project_stats",
                "description": "Get project statistics including breakdown by status and customer.",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "count_tickets",
                "description": "Get the total count of tickets in the system.",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_summary_stats",
                "description": "Get overall summary statistics for the entire system (customers, projects, tickets, documents, employees).",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "search_customers",
                "description": "Search for customers by name (partial match).",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "search_term": {
                            "type": "string",
                            "description": "The search term to match against customer names"
                        }
                    },
                    "required": ["search_term"]
                }
            },
            {
                "name": "semantic_search",
                "description": "Search documents using semantic similarity. Use this for finding relevant documentation, procedures, or information about specific topics.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query"
                        },
                        "n_results": {
                            "type": "integer",
                            "description": "Number of results to return (default 5)",
                            "default": 5
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "run_sql_query",
                "description": "Run a custom SQL query against the structured database. Tables: customers, projects, tickets, employees, documents. Use for complex aggregations or filters not covered by other tools.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "sql": {
                            "type": "string",
                            "description": "The SQL query to execute (SELECT only)"
                        }
                    },
                    "required": ["sql"]
                }
            }
        ]

    def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """Execute a tool and return the result as a string"""
        try:
            if tool_name == "count_customers":
                # Count only folder-based customers for accuracy
                result = self.structured_store.query(
                    "SELECT COUNT(*) as count FROM customers WHERE source = 'folder'"
                )
                return f"Customer count: {result[0]['count']}"

            elif tool_name == "list_customers":
                limit = tool_input.get("limit", 20)
                customers = self.structured_store.query(
                    "SELECT name FROM customers WHERE source = 'folder' ORDER BY name LIMIT ?",
                    (limit,)
                )
                names = [c['name'] for c in customers]
                return f"Customers ({len(names)}): " + ", ".join(names)

            elif tool_name == "get_customer_details":
                name = tool_input.get("customer_name")
                details = self.structured_store.get_customer_details(name)
                if details:
                    return json.dumps(details, indent=2, default=str)
                return f"Customer '{name}' not found"

            elif tool_name == "count_projects":
                status = tool_input.get("status")
                count = self.structured_store.count_projects(status)
                if status:
                    return f"Projects with status '{status}': {count}"
                return f"Total projects: {count}"

            elif tool_name == "get_project_stats":
                stats = self.structured_store.get_project_stats()
                return json.dumps(stats, indent=2, default=str)

            elif tool_name == "count_tickets":
                result = self.structured_store.query("SELECT COUNT(*) as count FROM tickets")
                return f"Total tickets: {result[0]['count']}"

            elif tool_name == "get_summary_stats":
                stats = self.structured_store.get_summary_stats()
                return json.dumps(stats, indent=2, default=str)

            elif tool_name == "search_customers":
                term = tool_input.get("search_term")
                results = self.structured_store.search_customers(term)
                if results:
                    names = [r['name'] for r in results[:10]]
                    return f"Found {len(results)} customers matching '{term}': " + ", ".join(names)
                return f"No customers found matching '{term}'"

            elif tool_name == "semantic_search":
                query = tool_input.get("query")
                n_results = tool_input.get("n_results", 5)
                results = self.vector_store.semantic_search(query, n_results=n_results)
                if results:
                    summaries = []
                    for i, r in enumerate(results[:5]):
                        title = r.get('metadata', {}).get('title', 'Untitled')
                        content = r.get('content', '')[:300]
                        summaries.append(f"{i+1}. {title}: {content}...")
                    return "Search results:\n" + "\n".join(summaries)
                return "No relevant documents found"

            elif tool_name == "run_sql_query":
                sql = tool_input.get("sql", "").strip()
                # Security check - only allow SELECT
                if not sql.upper().startswith("SELECT"):
                    return "Error: Only SELECT queries are allowed"
                results = self.structured_store.query(sql)
                if results:
                    return json.dumps(results[:20], indent=2, default=str)
                return "No results"

            else:
                return f"Unknown tool: {tool_name}"

        except Exception as e:
            return f"Tool error: {str(e)}"

    def query(self, user_query: str, max_iterations: int = 8) -> Dict[str, Any]:
        """
        Process a complex query using the agent with tool use

        Returns dict with:
        - answer: The final answer
        - tool_calls: List of tools used
        - reasoning: The agent's reasoning process
        """
        messages = [
            {
                "role": "user",
                "content": f"""You are a helpful assistant for Obera Connect, an IT managed services company.
Answer the following question using the available tools. Be precise and factual.

IMPORTANT GUIDELINES:
- Use get_summary_stats for overall system statistics
- Use count_customers for customer counts (returns 38 real customers from SharePoint folders)
- Use list_customers to see customer names
- Use search_customers ONLY if looking for a specific customer by name
- Use semantic_search for documentation/procedure questions
- Use run_sql_query only for complex queries not covered by other tools
- After gathering data, provide a clear final answer - don't keep searching endlessly

Question: {user_query}

Use the tools to gather the information you need, then provide a clear, concise answer."""
            }
        ]

        tool_calls = []
        iterations = 0

        while iterations < max_iterations:
            iterations += 1

            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                tools=self.tools,
                messages=messages
            )

            # Check if we're done (no more tool use)
            if response.stop_reason == "end_turn":
                # Extract final text response
                final_answer = ""
                for block in response.content:
                    if hasattr(block, 'text'):
                        final_answer = block.text
                        break

                return {
                    "answer": final_answer,
                    "tool_calls": tool_calls,
                    "iterations": iterations
                }

            # Process tool use blocks
            tool_use_blocks = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_use_blocks.append(block)

            if not tool_use_blocks:
                # No tool use, get text response
                final_answer = ""
                for block in response.content:
                    if hasattr(block, 'text'):
                        final_answer = block.text
                        break
                return {
                    "answer": final_answer,
                    "tool_calls": tool_calls,
                    "iterations": iterations
                }

            # Add assistant response to messages
            messages.append({
                "role": "assistant",
                "content": response.content
            })

            # Execute tools and collect results
            tool_results = []
            for tool_block in tool_use_blocks:
                tool_name = tool_block.name
                tool_input = tool_block.input

                # Execute the tool
                result = self.execute_tool(tool_name, tool_input)
                tool_calls.append({
                    "tool": tool_name,
                    "input": tool_input,
                    "result": result[:500]  # Truncate for logging
                })

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_block.id,
                    "content": result
                })

            # Add tool results to messages
            messages.append({
                "role": "user",
                "content": tool_results
            })

        return {
            "answer": "Max iterations reached. Please try a simpler query.",
            "tool_calls": tool_calls,
            "iterations": iterations
        }


def main():
    """Test the agentic RAG system"""
    db_path = CHROMA_DB_DIR.parent / "structured.db"
    structured_store = StructuredStore(db_path)
    vector_store = VectorStore(CHROMA_DB_DIR)

    agent = AgenticRAG(structured_store, vector_store)

    test_queries = [
        "How many customers does Obera have?",
        "Give me a summary of all system statistics",
        "What is the status breakdown of projects?",
        "Search for information about firewall configuration",
    ]

    print("=" * 70)
    print("Agentic RAG Test")
    print("=" * 70)

    for query in test_queries:
        print(f"\n{'='*70}")
        print(f"Query: {query}")
        print("-" * 70)

        result = agent.query(query)

        print(f"Answer: {result['answer'][:500]}...")
        print(f"\nTools used: {len(result['tool_calls'])}")
        for tc in result['tool_calls']:
            print(f"  - {tc['tool']}: {tc['input']}")
        print(f"Iterations: {result['iterations']}")


if __name__ == "__main__":
    main()
