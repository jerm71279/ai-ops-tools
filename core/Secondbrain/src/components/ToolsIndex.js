import React, { useState, useEffect } from 'react';
import {
    Search, Database, Cpu, FileText, Play, Tool, Info, Code, BookOpen
} from 'react-feather';
import { TOOLS_INDEX, filterTools, showToolDetails, viewToolCode, showToolDocs, runTool } from '../utils/toolsIndexUtils';
import { showNotification } from '../utils/timeReportsUtils'; // Reusing showNotification
import ToolDetailModal from './modals/ToolDetailModal'; // Import ToolDetailModal

function ToolsIndex() {
    const [toolSearchInput, setToolSearchInput] = useState('');
    const [filteredToolCategories, setFilteredToolCategories] = useState(TOOLS_INDEX);
    const [showToolDetailModal, setShowToolDetailModal] = useState(false);
    const [selectedToolName, setSelectedToolName] = useState(null);

    useEffect(() => {
        setFilteredToolCategories(filterTools(TOOLS_INDEX, toolSearchInput));
    }, [toolSearchInput]);

    // Icon mapping for dynamic rendering
    const iconMap = {
        database: Database,
        cpu: Cpu,
        'file-text': FileText,
        play: Play,
        tool: Tool,
        info: Info,
        code: Code,
        'book-open': BookOpen,
        search: Search // If search icon is needed elsewhere
    };

    const handleToolClick = (tool) => {
        setSelectedToolName(tool.name);
        setShowToolDetailModal(true);
    };

    const handleCloseToolDetailModal = () => {
        setShowToolDetailModal(false);
        setSelectedToolName(null);
    };


    return (
        <div className="tab-pane fade show active" id="tools-panel" role="tabpanel" aria-labelledby="tab-tools">
            <div className="toolbar d-flex flex-wrap align-items-center justify-content-between mb-3">
                <div className="input-group flex-grow-1 me-2">
                    <span className="input-group-text"><Search size={16} /></span>
                    <input
                        type="text"
                        className="form-control"
                        placeholder="Search tools..."
                        value={toolSearchInput}
                        onChange={(e) => setToolSearchInput(e.target.value)}
                    />
                </div>
                {/* No other actions in toolbar for now, based on original HTML */}
            </div>

            <div className="tools-categories row">
                {Object.keys(filteredToolCategories).length === 0 ? (
                    <div className="col-12 text-center p-5">
                        <Tool size={48} className="text-muted mb-3" />
                        <h3 className="text-dark mb-2">No Tools Found</h3>
                        <p className="text-muted">Try adjusting your search filters.</p>
                    </div>
                ) : (
                    Object.entries(filteredToolCategories).map(([categoryName, categoryData]) => {
                        const IconComponent = iconMap[categoryData.icon] || Tool; // Fallback to generic Tool icon
                        return (
                            <div key={categoryName} className="col-md-6 col-lg-4 mb-4">
                                <div className="card h-100">
                                    <div className="card-header d-flex align-items-center">
                                        <IconComponent size={20} className="me-2 text-primary" />
                                        <h5 className="mb-0">{categoryName}</h5>
                                    </div>
                                    <ul className="list-group list-group-flush">
                                        {categoryData.tools.map(tool => (
                                            <li key={tool.name} className="list-group-item d-flex justify-content-between align-items-center">
                                                <div>
                                                    <h6 className="mb-0">{tool.name}</h6>
                                                    <small className="text-muted">{tool.desc}</small>
                                                </div>
                                                <button className="btn btn-sm btn-outline-secondary" onClick={() => handleToolClick(tool)}>
                                                    <Info size={14} /> Details
                                                </button>
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            </div>
                        );
                    })
                )}
            </div>

            <ToolDetailModal
                show={showToolDetailModal}
                onClose={handleCloseToolDetailModal}
                toolName={selectedToolName}
            />
        </div>
    );
}

export default ToolsIndex;