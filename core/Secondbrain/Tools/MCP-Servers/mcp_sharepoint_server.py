import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""
SharePoint MCP Server
Model Context Protocol server for SharePoint List operations

Provides tools for BA Agent and other agents to interact with:
- Projects list
- Tasks list
- Tickets list
- TimeEntries list

Authentication via Microsoft Graph API with Azure AD tokens
"""
import json
import os
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import aiohttp


@dataclass
class SharePointConfig:
    """Configuration for SharePoint connection"""
    site_id: str
    graph_api_base: str = "https://graph.microsoft.com/v1.0"
    lists: Dict[str, str] = None  # list_name -> list_id mapping

    def __post_init__(self):
        if self.lists is None:
            self.lists = {}


class SharePointMCPServer:
    """
    MCP Server for SharePoint List Operations

    Tools:
    - get_projects: Fetch projects from SharePoint
    - get_tasks: Fetch tasks from SharePoint
    - get_tickets: Fetch tickets from SharePoint
    - get_time_entries: Fetch time entries from SharePoint
    - create_item: Create new item in a list
    - update_item: Update existing item
    - delete_item: Delete item from list
    - search_items: Search across lists
    - get_list_analytics: Get aggregated analytics for a list
    """

    def __init__(self, config: SharePointConfig = None):
        self.config = config or SharePointConfig(
            site_id=os.getenv(
                "SHAREPOINT_SITE_ID",
                "oberaconnect.sharepoint.com,3894a9a1-76ac-4955-88b2-a1d335f35f78,522e18b4-c876-4c61-b74b-53adb0e6ddef"
            )
        )
        self.access_token = None
        self._session = None

        # List column mappings for proper field access
        self.list_schemas = {
            "Projects": {
                "display_name": "Projects",
                "key_field": "Title",  # SharePoint uses Title for ProjectName
                "fields": {
                    "ProjectName": "Title",
                    "Description": "Description",
                    "Status": "Status",
                    "Priority": "Priority",
                    "AssignedTo": "AssignedTo",
                    "Customer": "Customer",
                    "DueDate": "DueDate",
                    "StartDate": "StartDate",
                    "EndDate": "EndDate",
                    "PercentComplete": "PercentComplete",
                    "BudgetHours": "BudgetHours",
                    "HoursSpent": "HoursSpent",
                    "SOW": "SOW",
                    "DocumentUrl": "DocumentUrl",
                    "DocumentName": "DocumentName"
                }
            },
            "Tasks": {
                "display_name": "Tasks",
                "key_field": "Title",
                "fields": {
                    "Title": "Title",
                    "Description": "Description",
                    "Status": "Status",
                    "Priority": "Priority",
                    "AssignedTo": "AssignedTo",
                    "DueDate": "DueDate",
                    "ProjectId": "ProjectId",
                    "ProjectName": "ProjectName",
                    "TicketId": "TicketId",
                    "EstimatedHours": "EstimatedHours",
                    "DevOpsWorkItemId": "DevOpsWorkItemId",
                    "DevOpsWorkItemUrl": "DevOpsWorkItemUrl",
                    "DocumentUrl": "DocumentUrl",
                    "DocumentName": "DocumentName"
                }
            },
            "Tickets": {
                "display_name": "Tickets",
                "key_field": "Title",
                "fields": {
                    "TicketTitle": "Title",
                    "Description": "Description",
                    "Status": "Status",
                    "Priority": "Priority",
                    "AssignedTo": "AssignedTo",
                    "Customer": "Customer",
                    "DueDate": "DueDate",
                    "Source": "Source",
                    "SLAStatus": "SLAStatus",
                    "TimeSpent": "TimeSpent",
                    "ResolutionNotes": "ResolutionNotes",
                    "ProjectId": "ProjectId",
                    "ProjectName": "ProjectName",
                    "DevOpsWorkItemId": "DevOpsWorkItemId",
                    "DevOpsWorkItemUrl": "DevOpsWorkItemUrl",
                    "DocumentUrl": "DocumentUrl",
                    "DocumentName": "DocumentName"
                }
            },
            "TimeEntries": {
                "display_name": "TimeEntries",
                "key_field": "Title",
                "fields": {
                    "Employee": "Employee",
                    "EntryDate": "EntryDate",
                    "Hours": "Hours",
                    "WorkType": "WorkType",
                    "ProjectId": "ProjectId",
                    "ProjectType": "ProjectType",
                    "ProjectName": "ProjectName",
                    "Description": "Description",
                    "Billable": "Billable"
                }
            }
        }

        # Define available tools
        self.tools = {
            "get_projects": {
                "description": "Fetch all projects from SharePoint",
                "parameters": {
                    "status_filter": "Optional status filter (e.g., 'In Progress')",
                    "limit": "Maximum number of items to return"
                }
            },
            "get_tasks": {
                "description": "Fetch tasks from SharePoint, optionally filtered by project",
                "parameters": {
                    "project_id": "Optional project ID to filter by",
                    "status_filter": "Optional status filter",
                    "assignee": "Optional assignee filter"
                }
            },
            "get_tickets": {
                "description": "Fetch tickets from SharePoint",
                "parameters": {
                    "status_filter": "Optional status filter",
                    "priority_filter": "Optional priority filter"
                }
            },
            "get_time_entries": {
                "description": "Fetch time entries from SharePoint",
                "parameters": {
                    "date_from": "Start date (YYYY-MM-DD)",
                    "date_to": "End date (YYYY-MM-DD)",
                    "employee": "Optional employee filter",
                    "project_id": "Optional project ID filter"
                }
            },
            "get_project_with_tasks": {
                "description": "Get a project with all its related tasks",
                "parameters": {
                    "project_id": "The project ID"
                }
            },
            "get_list_analytics": {
                "description": "Get aggregated analytics for a SharePoint list",
                "parameters": {
                    "list_name": "Name of the list (Projects, Tasks, Tickets, TimeEntries)",
                    "group_by": "Field to group by"
                }
            },
            "search_items": {
                "description": "Search across SharePoint lists",
                "parameters": {
                    "query": "Search query string",
                    "list_name": "Optional specific list to search"
                }
            },
            "create_task": {
                "description": "Create a new task linked to a project",
                "parameters": {
                    "title": "Task title",
                    "project_id": "Project ID to link to",
                    "assignee": "Person to assign to",
                    "due_date": "Due date (YYYY-MM-DD)",
                    "priority": "Priority (Low, Medium, High, Critical)",
                    "description": "Task description"
                }
            },
            "update_task_status": {
                "description": "Update a task's status",
                "parameters": {
                    "task_id": "Task SharePoint ID",
                    "status": "New status"
                }
            },
            "log_time_entry": {
                "description": "Log a time entry for work performed",
                "parameters": {
                    "employee": "Employee name",
                    "hours": "Hours worked",
                    "date": "Date of work (YYYY-MM-DD)",
                    "project_id": "Project or ticket ID",
                    "description": "Work description",
                    "billable": "Whether billable (true/false)"
                }
            }
        }

    def set_access_token(self, token: str):
        """Set the Microsoft Graph API access token"""
        self.access_token = token

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def _make_request(
        self,
        method: str,
        url: str,
        data: Dict = None
    ) -> Dict[str, Any]:
        """Make authenticated request to Graph API"""
        if not self.access_token:
            return {"success": False, "error": "No access token set"}

        session = await self._get_session()
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        try:
            async with session.request(method, url, headers=headers, json=data) as response:
                if response.status == 429:
                    # Rate limited
                    retry_after = int(response.headers.get("Retry-After", 5))
                    await asyncio.sleep(retry_after)
                    return await self._make_request(method, url, data)

                if response.status >= 400:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": f"API error {response.status}: {error_text}"
                    }

                if method == "DELETE":
                    return {"success": True}

                result = await response.json()
                return {"success": True, "data": result}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def discover_lists(self) -> Dict[str, str]:
        """Discover SharePoint list IDs"""
        url = f"{self.config.graph_api_base}/sites/{self.config.site_id}/lists"
        result = await self._make_request("GET", url)

        if not result.get("success"):
            return {}

        lists = result.get("data", {}).get("value", [])
        discovered = {}

        for lst in lists:
            display_name = lst.get("displayName", "")
            list_id = lst.get("id", "")

            # Match against known lists
            for list_name in self.list_schemas.keys():
                if display_name.lower() == list_name.lower():
                    discovered[list_name] = list_id
                    self.config.lists[list_name] = list_id

        return discovered

    async def _fetch_list_items(
        self,
        list_name: str,
        filter_query: str = None,
        top: int = 200
    ) -> List[Dict]:
        """Fetch items from a SharePoint list"""
        list_id = self.config.lists.get(list_name)
        if not list_id:
            # Try to discover lists first
            await self.discover_lists()
            list_id = self.config.lists.get(list_name)
            if not list_id:
                return []

        url = f"{self.config.graph_api_base}/sites/{self.config.site_id}/lists/{list_id}/items?expand=fields&$top={top}"

        if filter_query:
            url += f"&$filter={filter_query}"

        all_items = []
        next_link = url

        while next_link:
            result = await self._make_request("GET", next_link)

            if not result.get("success"):
                break

            data = result.get("data", {})
            items = data.get("value", [])
            all_items.extend(items)

            next_link = data.get("@odata.nextLink")

        return all_items

    def _transform_item(self, item: Dict, list_name: str) -> Dict:
        """Transform SharePoint item to standard format"""
        fields = item.get("fields", {})
        schema = self.list_schemas.get(list_name, {}).get("fields", {})

        transformed = {
            "id": str(item.get("id", "")),
            "sharePointId": item.get("id"),
            "etag": item.get("@odata.etag"),
            "createdDateTime": item.get("createdDateTime"),
            "lastModifiedDateTime": item.get("lastModifiedDateTime"),
            "fields": {}
        }

        # Map fields
        for our_field, sp_field in schema.items():
            value = fields.get(sp_field, fields.get(our_field))
            if value is not None:
                # Handle dates
                if "Date" in our_field and isinstance(value, str) and "T" in value:
                    value = value.split("T")[0]
                transformed["fields"][our_field] = value

        return transformed

    # ========================================================================
    # TOOL IMPLEMENTATIONS
    # ========================================================================

    async def execute_tool(self, tool_name: str, arguments: Dict) -> Dict[str, Any]:
        """Execute a tool by name"""
        tool_method = getattr(self, f"tool_{tool_name}", None)

        if tool_method is None:
            return {"success": False, "error": f"Unknown tool: {tool_name}"}

        try:
            result = await tool_method(**arguments)
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def tool_get_projects(
        self,
        status_filter: str = None,
        limit: int = 200
    ) -> Dict[str, Any]:
        """Get projects from SharePoint"""
        items = await self._fetch_list_items("Projects", top=limit)

        projects = [self._transform_item(item, "Projects") for item in items]

        # Apply filter
        if status_filter:
            projects = [
                p for p in projects
                if p.get("fields", {}).get("Status") == status_filter
            ]

        return {
            "success": True,
            "projects": projects,
            "count": len(projects)
        }

    async def tool_get_tasks(
        self,
        project_id: str = None,
        status_filter: str = None,
        assignee: str = None
    ) -> Dict[str, Any]:
        """Get tasks from SharePoint"""
        items = await self._fetch_list_items("Tasks")

        tasks = [self._transform_item(item, "Tasks") for item in items]

        # Apply filters
        if project_id:
            tasks = [
                t for t in tasks
                if str(t.get("fields", {}).get("ProjectId")) == str(project_id)
            ]

        if status_filter:
            tasks = [
                t for t in tasks
                if t.get("fields", {}).get("Status") == status_filter
            ]

        if assignee:
            tasks = [
                t for t in tasks
                if assignee.lower() in (t.get("fields", {}).get("AssignedTo", "") or "").lower()
            ]

        return {
            "success": True,
            "tasks": tasks,
            "count": len(tasks)
        }

    async def tool_get_tickets(
        self,
        status_filter: str = None,
        priority_filter: str = None
    ) -> Dict[str, Any]:
        """Get tickets from SharePoint"""
        items = await self._fetch_list_items("Tickets")

        tickets = [self._transform_item(item, "Tickets") for item in items]

        if status_filter:
            tickets = [
                t for t in tickets
                if t.get("fields", {}).get("Status") == status_filter
            ]

        if priority_filter:
            tickets = [
                t for t in tickets
                if t.get("fields", {}).get("Priority") == priority_filter
            ]

        return {
            "success": True,
            "tickets": tickets,
            "count": len(tickets)
        }

    async def tool_get_time_entries(
        self,
        date_from: str = None,
        date_to: str = None,
        employee: str = None,
        project_id: str = None
    ) -> Dict[str, Any]:
        """Get time entries from SharePoint"""
        items = await self._fetch_list_items("TimeEntries")

        entries = [self._transform_item(item, "TimeEntries") for item in items]

        # Date filtering
        if date_from:
            from_date = datetime.fromisoformat(date_from)
            entries = [
                e for e in entries
                if e.get("fields", {}).get("EntryDate") and
                   datetime.fromisoformat(e["fields"]["EntryDate"]) >= from_date
            ]

        if date_to:
            to_date = datetime.fromisoformat(date_to)
            entries = [
                e for e in entries
                if e.get("fields", {}).get("EntryDate") and
                   datetime.fromisoformat(e["fields"]["EntryDate"]) <= to_date
            ]

        if employee:
            entries = [
                e for e in entries
                if employee.lower() in (e.get("fields", {}).get("Employee", "") or "").lower()
            ]

        if project_id:
            entries = [
                e for e in entries
                if str(e.get("fields", {}).get("ProjectId")) == str(project_id)
            ]

        return {
            "success": True,
            "time_entries": entries,
            "count": len(entries)
        }

    async def tool_get_project_with_tasks(
        self,
        project_id: str
    ) -> Dict[str, Any]:
        """Get a project with all its related tasks"""
        # Get project
        projects_result = await self.tool_get_projects()
        project = None

        for p in projects_result.get("projects", []):
            if str(p.get("id")) == str(project_id):
                project = p
                break

        if not project:
            return {"success": False, "error": "Project not found"}

        # Get related tasks
        tasks_result = await self.tool_get_tasks(project_id=project_id)

        return {
            "success": True,
            "project": project,
            "tasks": tasks_result.get("tasks", []),
            "task_count": tasks_result.get("count", 0)
        }

    async def tool_get_list_analytics(
        self,
        list_name: str,
        group_by: str = "Status"
    ) -> Dict[str, Any]:
        """Get aggregated analytics for a list"""
        if list_name not in self.list_schemas:
            return {"success": False, "error": f"Unknown list: {list_name}"}

        items = await self._fetch_list_items(list_name)
        transformed = [self._transform_item(item, list_name) for item in items]

        # Group by specified field
        groups = {}
        for item in transformed:
            value = item.get("fields", {}).get(group_by, "Unknown")
            if value not in groups:
                groups[value] = {"count": 0, "items": []}
            groups[value]["count"] += 1
            groups[value]["items"].append(item.get("id"))

        return {
            "success": True,
            "list_name": list_name,
            "total_items": len(transformed),
            "grouped_by": group_by,
            "groups": {
                k: {"count": v["count"]}
                for k, v in groups.items()
            }
        }

    async def tool_create_task(
        self,
        title: str,
        project_id: str = None,
        assignee: str = None,
        due_date: str = None,
        priority: str = "Medium",
        description: str = ""
    ) -> Dict[str, Any]:
        """Create a new task"""
        list_id = self.config.lists.get("Tasks")
        if not list_id:
            await self.discover_lists()
            list_id = self.config.lists.get("Tasks")

        if not list_id:
            return {"success": False, "error": "Tasks list not found"}

        # Get project name if project_id provided
        project_name = None
        if project_id:
            proj_result = await self.tool_get_projects()
            for p in proj_result.get("projects", []):
                if str(p.get("id")) == str(project_id):
                    project_name = p.get("fields", {}).get("ProjectName")
                    break

        url = f"{self.config.graph_api_base}/sites/{self.config.site_id}/lists/{list_id}/items"

        data = {
            "fields": {
                "Title": title,
                "Status": "Not Started",
                "Priority": priority,
                "AssignedTo": assignee or "",
                "DueDate": due_date,
                "ProjectId": project_id or "",
                "ProjectName": project_name or "",
                "Description": description
            }
        }

        result = await self._make_request("POST", url, data)

        if result.get("success"):
            return {
                "success": True,
                "task": self._transform_item(result.get("data", {}), "Tasks"),
                "message": f"Task '{title}' created successfully"
            }

        return result

    async def tool_update_task_status(
        self,
        task_id: str,
        status: str
    ) -> Dict[str, Any]:
        """Update a task's status"""
        list_id = self.config.lists.get("Tasks")
        if not list_id:
            return {"success": False, "error": "Tasks list not found"}

        url = f"{self.config.graph_api_base}/sites/{self.config.site_id}/lists/{list_id}/items/{task_id}"

        data = {
            "fields": {
                "Status": status
            }
        }

        result = await self._make_request("PATCH", url, data)

        if result.get("success"):
            return {
                "success": True,
                "message": f"Task {task_id} updated to status: {status}"
            }

        return result

    async def tool_log_time_entry(
        self,
        employee: str,
        hours: float,
        date: str,
        project_id: str = None,
        description: str = "",
        billable: bool = True
    ) -> Dict[str, Any]:
        """Log a time entry"""
        list_id = self.config.lists.get("TimeEntries")
        if not list_id:
            await self.discover_lists()
            list_id = self.config.lists.get("TimeEntries")

        if not list_id:
            return {"success": False, "error": "TimeEntries list not found"}

        # Get project name if project_id provided
        project_name = "General"
        if project_id:
            proj_result = await self.tool_get_projects()
            for p in proj_result.get("projects", []):
                if str(p.get("id")) == str(project_id):
                    project_name = p.get("fields", {}).get("ProjectName", "General")
                    break

        url = f"{self.config.graph_api_base}/sites/{self.config.site_id}/lists/{list_id}/items"

        data = {
            "fields": {
                "Title": f"{employee} - {date}",
                "Employee": employee,
                "EntryDate": date,
                "Hours": hours,
                "WorkType": "Project",
                "ProjectId": project_id or "",
                "ProjectName": project_name,
                "Description": description,
                "Billable": billable
            }
        }

        result = await self._make_request("POST", url, data)

        if result.get("success"):
            return {
                "success": True,
                "time_entry": self._transform_item(result.get("data", {}), "TimeEntries"),
                "message": f"Logged {hours}h for {employee} on {date}"
            }

        return result

    async def tool_search_items(
        self,
        query: str,
        list_name: str = None
    ) -> Dict[str, Any]:
        """Search across SharePoint lists"""
        results = []
        query_lower = query.lower()

        lists_to_search = [list_name] if list_name else list(self.list_schemas.keys())

        for lst in lists_to_search:
            if lst not in self.list_schemas:
                continue

            items = await self._fetch_list_items(lst)
            transformed = [self._transform_item(item, lst) for item in items]

            # Simple text search
            for item in transformed:
                fields = item.get("fields", {})
                # Search in all string fields
                for key, value in fields.items():
                    if isinstance(value, str) and query_lower in value.lower():
                        results.append({
                            "list": lst,
                            "item": item,
                            "matched_field": key
                        })
                        break

        return {
            "success": True,
            "query": query,
            "results": results,
            "count": len(results)
        }

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools"""
        return [
            {
                "name": name,
                "description": info["description"],
                "parameters": info["parameters"]
            }
            for name, info in self.tools.items()
        ]

    async def close(self):
        """Close the session"""
        if self._session and not self._session.closed:
            await self._session.close()


# ============================================================================
# SYNCHRONOUS WRAPPER FOR NON-ASYNC CONTEXTS
# ============================================================================

class SharePointMCPServerSync:
    """Synchronous wrapper for SharePointMCPServer"""

    def __init__(self, config: SharePointConfig = None):
        self._async_server = SharePointMCPServer(config)

    def set_access_token(self, token: str):
        self._async_server.set_access_token(token)

    def execute_tool(self, tool_name: str, arguments: Dict) -> Dict[str, Any]:
        """Execute tool synchronously"""
        return asyncio.run(self._async_server.execute_tool(tool_name, arguments))

    def get_projects(self, **kwargs) -> Dict[str, Any]:
        return asyncio.run(self._async_server.tool_get_projects(**kwargs))

    def get_tasks(self, **kwargs) -> Dict[str, Any]:
        return asyncio.run(self._async_server.tool_get_tasks(**kwargs))

    def get_tickets(self, **kwargs) -> Dict[str, Any]:
        return asyncio.run(self._async_server.tool_get_tickets(**kwargs))

    def get_time_entries(self, **kwargs) -> Dict[str, Any]:
        return asyncio.run(self._async_server.tool_get_time_entries(**kwargs))


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

def main():
    """CLI entry point for SharePoint MCP Server"""
    import argparse

    parser = argparse.ArgumentParser(description="SharePoint MCP Server")
    parser.add_argument("--list-tools", action="store_true", help="List available tools")
    parser.add_argument("--discover", action="store_true", help="Discover SharePoint lists")

    args = parser.parse_args()

    server = SharePointMCPServer()

    if args.list_tools:
        print("Available Tools:")
        print(json.dumps(server.get_available_tools(), indent=2))

    elif args.discover:
        print("Note: Set access token first to discover lists")
        print("Available list schemas:")
        for name, schema in server.list_schemas.items():
            print(f"  - {name}: {list(schema['fields'].keys())}")

    else:
        print("SharePoint MCP Server")
        print("=" * 60)
        print("\nUsage:")
        print("  --list-tools   List available tools")
        print("  --discover     Show list schemas")
        print("\nTools available:", list(server.tools.keys()))


if __name__ == "__main__":
    main()
