import React from 'react';
import { X, Info, Code, BookOpen, Play, Database, Cpu, FileText, Tool } from 'react-feather'; // Added Database, Cpu, FileText, Tool
import { useNotification } from '../../contexts/NotificationContext'; // Import useNotification
import { TOOLS_INDEX } from '../../utils/toolsIndexUtils'; // To get tool details from here

function ToolDetailModal({ show, onClose, toolName }) {
    const { showNotification } = useNotification(); // Get showNotification from context

    // Find the tool details from TOOLS_INDEX
    let toolDetails = null;
    let toolCategory = null;
    let IconComponent = Info; // Default icon

    for (const categoryName in TOOLS_INDEX) {
        const foundTool = TOOLS_INDEX[categoryName].tools.find(tool => tool.name === toolName);
        if (foundTool) {
            toolDetails = foundTool;
            toolCategory = categoryName;
            IconComponent = categoryName === 'Data Processing & Import' ? Database : // Need to import Database icon if I use it
                            categoryName === 'Network & Call Flow' ? Cpu :
                            categoryName === 'Document Management' ? FileText :
                            categoryName === 'Automation & Scheduling' ? Play :
                            categoryName === 'AI Agents & MCP' ? Cpu :
                            categoryName === 'Configuration & Utilities' ? Tool : Info;
            break;
        }
    }

    if (!show || !toolDetails) return null;

    const handleViewCode = () => {
        showNotification(`Viewing code for ${toolDetails.name}`, 'info');
        // Implement actual logic to display code
    };

    const handleShowDocs = () => {
        showNotification(`Showing docs for ${toolDetails.name}`, 'info');
        // Implement actual logic to display docs
    };

    const handleRunTool = () => {
        showNotification(`Running ${toolDetails.name}`, 'info');
        // Implement actual logic to run tool
    };

    return (
        <div className="modal-overlay" style={{ display: 'block' }}>
            <div className="modal" style={{ maxWidth: '500px' }} role="dialog" aria-modal="true" aria-labelledby="toolModalTitle">
                <div className="modal-header">
                    <h2 className="modal-title" id="toolModalTitle">
                        <IconComponent size={20} className="me-2 text-primary" />
                        {toolDetails.name}
                    </h2>
                    <button className="btn-close" onClick={onClose} aria-label="Close modal"></button>
                </div>
                <div className="modal-body">
                    <input type="hidden" id="currentToolName" value={toolDetails.name} />
                    <div className="mb-3">
                        <span className="badge bg-primary" id="toolModalCategory">{toolCategory}</span>
                    </div>
                    <p className="text-muted" id="toolModalDesc">{toolDetails.desc}</p>
                    <div id="toolModalDetails" className="bg-light p-3 rounded">
                        {/* Additional details like parameters, last run, etc. can go here */}
                        <p className="mb-0"><strong>Last Run:</strong> Never (mock)</p>
                        <p className="mb-0"><strong>Parameters:</strong> None (mock)</p>
                    </div>
                </div>
                <div className="modal-footer d-flex justify-content-between">
                    <div className="d-flex gap-2">
                        <button className="btn btn-secondary" onClick={handleViewCode}>
                            <Code size={14} className="me-1" /> View Code
                        </button>
                        <button className="btn btn-secondary" onClick={handleShowDocs}>
                            <BookOpen size={14} className="me-1" /> Docs
                        </button>
                    </div>
                    <button className="btn btn-primary" onClick={handleRunTool}>
                        <Play size={14} className="me-1" /> Run Tool
                    </button>
                </div>
            </div>
        </div>
    );
}

export default ToolDetailModal;