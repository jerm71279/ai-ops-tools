# Azure AD + Microsoft 365 MCP Server Plan

## Overview

Create an MCP server for unified Azure AD/Entra ID and Microsoft 365 management across multiple tenants, with intelligent authentication handling and session management.

## Location

`/home/mavrick/AZ_Subs/mcp_azure_server/`

## File Structure

```
mcp_azure_server/
├── __init__.py
├── server.py                 # Main FastMCP server entry point
├── config.py                 # Configuration management
├── requirements.txt
├── auth/
│   ├── __init__.py
│   ├── token_manager.py      # MSAL token acquisition/refresh/caching
│   └── tenant_context.py     # Multi-tenant session management
├── clients/
│   ├── __init__.py
│   └── graph_client.py       # Microsoft Graph API async client
├── tools/
│   ├── __init__.py
│   ├── session_tools.py      # Tenant switching, auth status
│   ├── azure_ad_tools.py     # Apps, users, groups, SPs
│   └── sharepoint_tools.py   # Sites, permissions
├── models/
│   ├── __init__.py
│   └── tenant.py             # Tenant configuration dataclass
└── utils/
    ├── __init__.py
    └── env_loader.py         # Load tenant .env files
```

## Tools to Implement

### Session Management
| Tool | Description |
|------|-------------|
| `get_auth_status` | Current auth status across tenants |
| `switch_tenant` | Switch active tenant context |
| `list_tenants` | List all configured tenants |
| `authenticate_interactive` | Browser-based Azure login |
| `authenticate_device_code` | CLI-friendly device code flow |
| `refresh_auth` | Force token refresh |

### Azure AD / Entra ID
| Tool | Description |
|------|-------------|
| `list_app_registrations` | List apps (filter, pagination) |
| `search_app_registrations` | Search apps by name/ID |
| `get_app_registration` | Detailed app info + URLs |
| `get_app_permissions` | API permissions for an app |
| `list_users` | List tenant users |
| `search_users` | Search by name/email |
| `get_user` | User details |
| `list_groups` | List groups |
| `get_group_members` | Group membership |
| `list_service_principals` | List SPs |

### SharePoint/M365
| Tool | Description |
|------|-------------|
| `list_sharepoint_sites` | List all sites |
| `get_sharepoint_site` | Site details |
| `get_site_permissions` | Site permissions |
| `graph_api_call` | Generic Graph API call |

## Authentication Design

**Token Storage**: Per-tenant in existing config dirs
```
/home/mavrick/AZ_Subs/Obera/.mcp_tokens/
    token_cache.bin     # MSAL cache
    auth_state.json     # Auth method, expiry
```

**Scopes**:
- `Application.Read.All` - App registrations
- `User.Read.All` - Users
- `Group.Read.All` - Groups
- `Directory.Read.All` - Directory
- `Sites.Read.All` - SharePoint

**Flow**: Auto-refresh tokens, fall back to re-auth when expired

## Integration Points

**Reads from**: Existing `.env` files in `/home/mavrick/AZ_Subs/`
**Pattern from**: `/home/mavrick/Projects/Secondbrain/mcp_sharepoint_server.py`
**Coordinates with**: `mcp-integration-overseer` agent

## Dependencies

```
mcp>=1.23.0          # Official MCP SDK
msal>=1.28.0         # Microsoft Auth
aiohttp>=3.9.0       # Async HTTP
python-dotenv>=1.0.0 # Env loading
pydantic>=2.0.0      # Validation
```

## Implementation Steps

1. **Create project structure** - directories, pyproject.toml, requirements.txt
2. **Implement tenant discovery** - `utils/env_loader.py` to read existing .env files
3. **Implement token manager** - `auth/token_manager.py` with MSAL
4. **Implement Graph client** - `clients/graph_client.py` async HTTP
5. **Implement session tools** - `get_auth_status`, `switch_tenant`, `list_tenants`
6. **Implement Azure AD tools** - App registrations, users, groups
7. **Implement SharePoint tools** - Sites, permissions
8. **Create FastMCP server** - `server.py` with tool registration
9. **Configure Claude Code** - Add MCP server config
10. **Test end-to-end** - Verify all tools work

## Claude Code Configuration

Add to MCP config:
```json
{
  "mcpServers": {
    "azure-m365-server": {
      "command": "python",
      "args": ["-m", "mcp_azure_server.server"],
      "cwd": "/home/mavrick/AZ_Subs/mcp_azure_server"
    }
  }
}
```

## Critical Files

- `/home/mavrick/Projects/Secondbrain/mcp_sharepoint_server.py` - Pattern reference
- `/home/mavrick/AZ_Subs/Obera/.env` - Tenant config format
- `/home/mavrick/AZ_Subs/az-tenant.sh` - Tenant switching reference
