// Local console-based notification for utility functions
function showNotification(message, type = 'info', duration = 5000) {
    console.log(`Notification (${type}): ${message}`);
}

// Utility functions and data for ToolsIndex component

export const TOOLS_INDEX = {
    'Data Processing & Import': {
        icon: 'database', // Changed from 'data' to feather icon name
        tools: [
            { name: 'sharepoint_importer.py', desc: 'Import documents from SharePoint' },
            { name: 'download_sharepoint.py', desc: 'Download files from SharePoint sites' },
            { name: 'download_all_sharepoint.py', desc: 'Bulk download all SharePoint content' },
            { name: 'slack_importer.py', desc: 'Import Slack channel exports' },
            { name: 'slab_importer.py', desc: 'Import documentation from Slab' },
            { name: 'process_batch.py', desc: 'Batch document processing pipeline' }
        ]
    },
    'Network & Call Flow': {
        icon: 'cpu', // Changed from 'network' to feather icon name
        tools: [
            { name: 'call_flow_processor.py', desc: 'Process customer call flow documents' },
            { name: 'call_flow_generator.py', desc: 'Generate call flow templates' },
            { name: 'call_flow_web.py', desc: 'Web interface for call flows' },
            { name: 'network_checklist.py', desc: 'Network installation checklist' }
        ]
    },
    'Document Management': {
        icon: 'file-text', // Changed from 'document' to feather icon name
        tools: [
            { name: 'document_processor.py', desc: 'Core document processing engine' },
            { name: 'claude_processor.py', desc: 'AI-powered document analysis' },
            { name: 'html_generator.py', desc: 'Generate HTML from documents' },
            { name: 'metadata_extractor.py', desc: 'Extract document metadata' },
            { name: 'suggest_links.py', desc: 'AI-suggested document links' }
        ]
    },
    'Automation & Scheduling': {
        icon: 'play', // Changed from 'automation' to feather icon name
        tools: [
            { name: 'daily_engineering_summary.py', desc: 'Generate daily email summaries' },
            { name: 'engineering_tracker.py', desc: 'Engineering projects/tickets API' },
            { name: 'contract_tracker.py', desc: 'Customer contract management' },
            { name: 'ee_team_dashboard.py', desc: 'EE Team dashboard backend' }
        ]
    },
    'AI Agents & MCP': {
        icon: 'cpu', // Changed from 'agent' to feather icon name
        tools: [
            { name: 'agent_orchestrator.py', desc: 'Multi-agent orchestration system' },
            { name: 'agent_notebooklm_analyst.py', desc: 'NotebookLM analysis agent' },
            { name: 'mcp_obsidian_server.py', desc: 'MCP server for Obsidian' },
            { name: 'query_brain.py', desc: 'RAG query engine' },
            { name: 'rag_web.py', desc: 'Web interface for RAG system' }
        ]
    },
    'Configuration & Utilities': {
        icon: 'tool', // Changed from 'config' to feather icon name
        tools: [
            { name: 'config.py', desc: 'Application configuration' },
            { name: 'vector_store.py', desc: 'ChromaDB vector storage' },
            { name: 'rebuild_index.py', desc: 'Rebuild search index' },
            { name: 'cleanup_vault.py', desc: 'Clean up Obsidian vault' }
        ]
    }
};

export const filterTools = (toolsIndex, searchTerm) => {
    if (!searchTerm) {
        return toolsIndex;
    }

    const filtered = {};
    const lowerCaseSearchTerm = searchTerm.toLowerCase();

    for (const category in toolsIndex) {
        const filteredTools = toolsIndex[category].tools.filter(tool =>
            tool.name.toLowerCase().includes(lowerCaseSearchTerm) ||
            tool.desc.toLowerCase().includes(lowerCaseSearchTerm)
        );
        if (filteredTools.length > 0) {
            filtered[category] = {
                ...toolsIndex[category],
                tools: filteredTools
            };
        }
    }
    return filtered;
};

// Placeholder for tool detail functions (will be implemented in component)
export const showToolDetails = (toolName, notificationHandler = showNotification) => {
    notificationHandler(`Showing details for: ${toolName}`, 'info');
    // This would typically open a modal or navigate to a detail page
};

export const viewToolCode = (toolName, notificationHandler = showNotification) => {
    notificationHandler(`Viewing code for: ${toolName}`, 'info');
};

export const showToolDocs = (toolName, notificationHandler = showNotification) => {
    notificationHandler(`Showing docs for: ${toolName}`, 'info');
};

export const runTool = (toolName, notificationHandler = showNotification) => {
    notificationHandler(`Running tool: ${toolName}`, 'info');
};