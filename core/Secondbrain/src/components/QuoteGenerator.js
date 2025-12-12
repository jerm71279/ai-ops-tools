import React, { useState } from 'react';
import {
    Calculator, Clock, DollarSign, FileText, Download,
    AlertCircle, CheckCircle, User, Briefcase
} from 'react-feather';
import { useNotification } from '../contexts/NotificationContext';

// Employee billable rates
const BILLABLE_RATES = {
    'Mavrick Faison': 150,
    'Patrick McFarland': 135,
    'Robbie McFarland': 200,
    'Default': 125
};

// Complexity factors
const COMPLEXITY_HOURS = {
    'simple': { min: 1, typical: 2, max: 4, label: 'Simple' },
    'low': { min: 2, typical: 4, max: 8, label: 'Low' },
    'medium': { min: 4, typical: 8, max: 16, label: 'Medium' },
    'high': { min: 8, typical: 24, max: 40, label: 'High' },
    'complex': { min: 24, typical: 40, max: 80, label: 'Complex' },
    'enterprise': { min: 40, typical: 80, max: 160, label: 'Enterprise' }
};

// Work type multipliers
const WORK_TYPES = {
    'development': { multiplier: 1.0, label: 'Development' },
    'design': { multiplier: 0.9, label: 'Design' },
    'consulting': { multiplier: 1.1, label: 'Consulting' },
    'support': { multiplier: 0.8, label: 'Support' },
    'training': { multiplier: 0.85, label: 'Training' },
    'documentation': { multiplier: 0.7, label: 'Documentation' },
    'project_management': { multiplier: 1.0, label: 'Project Management' }
};

function QuoteGenerator({ onQuoteGenerated }) {
    const { showNotification } = useNotification();

    // Form state
    const [projectName, setProjectName] = useState('');
    const [description, setDescription] = useState('');
    const [complexity, setComplexity] = useState('medium');
    const [workType, setWorkType] = useState('development');
    const [assignee, setAssignee] = useState('');
    const [includeBuffer, setIncludeBuffer] = useState(true);
    const [bufferPercent, setBufferPercent] = useState(15);
    const [customHours, setCustomHours] = useState('');

    // Quote result
    const [quote, setQuote] = useState(null);

    // Line items for detailed quotes
    const [lineItems, setLineItems] = useState([
        { description: '', hours: 0, rate: 125 }
    ]);

    const calculateQuote = () => {
        if (!projectName.trim()) {
            showNotification('Please enter a project name', 'warning');
            return;
        }

        const complexityData = COMPLEXITY_HOURS[complexity];
        const workTypeData = WORK_TYPES[workType];
        const rate = BILLABLE_RATES[assignee] || BILLABLE_RATES['Default'];

        // Base hours
        let baseHours = {
            min: complexityData.min * workTypeData.multiplier,
            typical: complexityData.typical * workTypeData.multiplier,
            max: complexityData.max * workTypeData.multiplier
        };

        // Override with custom hours if provided
        if (customHours && parseFloat(customHours) > 0) {
            const custom = parseFloat(customHours);
            baseHours = {
                min: custom * 0.8,
                typical: custom,
                max: custom * 1.3
            };
        }

        // Apply buffer
        const bufferMultiplier = includeBuffer ? (1 + bufferPercent / 100) : 1;
        const finalHours = {
            min: Math.round(baseHours.min * bufferMultiplier * 10) / 10,
            typical: Math.round(baseHours.typical * bufferMultiplier * 10) / 10,
            max: Math.round(baseHours.max * bufferMultiplier * 10) / 10
        };

        // Calculate line items total if present
        const lineItemsTotal = lineItems.reduce((sum, item) => sum + (item.hours * item.rate), 0);

        // Calculate costs
        const costs = {
            min: Math.round(finalHours.min * rate),
            typical: Math.round(finalHours.typical * rate),
            max: Math.round(finalHours.max * rate),
            lineItemsTotal: lineItemsTotal
        };

        const generatedQuote = {
            projectName,
            description,
            complexity: complexityData.label,
            workType: workTypeData.label,
            assignee: assignee || 'Team Average',
            hourlyRate: rate,
            estimatedHours: finalHours,
            estimatedCost: costs,
            bufferIncluded: includeBuffer,
            bufferPercent: includeBuffer ? bufferPercent : 0,
            lineItems: lineItems.filter(item => item.hours > 0),
            generatedAt: new Date().toISOString(),
            validUntil: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString() // 30 days
        };

        setQuote(generatedQuote);

        if (onQuoteGenerated) {
            onQuoteGenerated(generatedQuote);
        }

        showNotification('Quote generated successfully', 'success');
    };

    const addLineItem = () => {
        setLineItems([...lineItems, { description: '', hours: 0, rate: BILLABLE_RATES['Default'] }]);
    };

    const updateLineItem = (index, field, value) => {
        const updated = [...lineItems];
        updated[index][field] = field === 'hours' || field === 'rate' ? parseFloat(value) || 0 : value;
        setLineItems(updated);
    };

    const removeLineItem = (index) => {
        if (lineItems.length > 1) {
            setLineItems(lineItems.filter((_, i) => i !== index));
        }
    };

    const exportQuote = () => {
        if (!quote) return;

        const content = `
QUOTE ESTIMATE
==============

Project: ${quote.projectName}
Generated: ${new Date(quote.generatedAt).toLocaleDateString()}
Valid Until: ${new Date(quote.validUntil).toLocaleDateString()}

DESCRIPTION
-----------
${quote.description || 'No description provided'}

PARAMETERS
----------
Complexity: ${quote.complexity}
Work Type: ${quote.workType}
Assigned To: ${quote.assignee}
Hourly Rate: $${quote.hourlyRate}
Buffer: ${quote.bufferIncluded ? `${quote.bufferPercent}%` : 'None'}

ESTIMATE
--------
Hours (Minimum): ${quote.estimatedHours.min}
Hours (Typical): ${quote.estimatedHours.typical}
Hours (Maximum): ${quote.estimatedHours.max}

Cost (Minimum): $${quote.estimatedCost.min.toLocaleString()}
Cost (Typical): $${quote.estimatedCost.typical.toLocaleString()}
Cost (Maximum): $${quote.estimatedCost.max.toLocaleString()}

${quote.lineItems.length > 0 ? `
LINE ITEMS
----------
${quote.lineItems.map(item => `- ${item.description}: ${item.hours}h @ $${item.rate}/hr = $${(item.hours * item.rate).toLocaleString()}`).join('\n')}
Line Items Total: $${quote.estimatedCost.lineItemsTotal.toLocaleString()}
` : ''}

---
Generated by OberaConnect Engineering Command Center
        `.trim();

        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `quote_${quote.projectName.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.txt`;
        a.click();
        URL.revokeObjectURL(url);

        showNotification('Quote exported', 'success');
    };

    const resetForm = () => {
        setProjectName('');
        setDescription('');
        setComplexity('medium');
        setWorkType('development');
        setAssignee('');
        setIncludeBuffer(true);
        setBufferPercent(15);
        setCustomHours('');
        setQuote(null);
        setLineItems([{ description: '', hours: 0, rate: 125 }]);
    };

    return (
        <div className="quote-generator">
            <div className="row">
                {/* Input Form */}
                <div className="col-lg-6 mb-4">
                    <div className="card">
                        <div className="card-header">
                            <Calculator size={18} className="me-2" />
                            Quote Parameters
                        </div>
                        <div className="card-body">
                            {/* Project Name */}
                            <div className="mb-3">
                                <label className="form-label">
                                    <Briefcase size={14} className="me-1" />
                                    Project Name <span className="text-danger">*</span>
                                </label>
                                <input
                                    type="text"
                                    className="form-control"
                                    value={projectName}
                                    onChange={(e) => setProjectName(e.target.value)}
                                    placeholder="Enter project or task name"
                                />
                            </div>

                            {/* Description */}
                            <div className="mb-3">
                                <label className="form-label">
                                    <FileText size={14} className="me-1" />
                                    Description
                                </label>
                                <textarea
                                    className="form-control"
                                    rows="2"
                                    value={description}
                                    onChange={(e) => setDescription(e.target.value)}
                                    placeholder="Brief description of the work"
                                />
                            </div>

                            <div className="row">
                                {/* Complexity */}
                                <div className="col-md-6 mb-3">
                                    <label className="form-label">Complexity</label>
                                    <select
                                        className="form-select"
                                        value={complexity}
                                        onChange={(e) => setComplexity(e.target.value)}
                                    >
                                        {Object.entries(COMPLEXITY_HOURS).map(([key, data]) => (
                                            <option key={key} value={key}>
                                                {data.label} ({data.min}-{data.max}h)
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                {/* Work Type */}
                                <div className="col-md-6 mb-3">
                                    <label className="form-label">Work Type</label>
                                    <select
                                        className="form-select"
                                        value={workType}
                                        onChange={(e) => setWorkType(e.target.value)}
                                    >
                                        {Object.entries(WORK_TYPES).map(([key, data]) => (
                                            <option key={key} value={key}>{data.label}</option>
                                        ))}
                                    </select>
                                </div>
                            </div>

                            <div className="row">
                                {/* Assignee */}
                                <div className="col-md-6 mb-3">
                                    <label className="form-label">
                                        <User size={14} className="me-1" />
                                        Assigned To
                                    </label>
                                    <select
                                        className="form-select"
                                        value={assignee}
                                        onChange={(e) => setAssignee(e.target.value)}
                                    >
                                        <option value="">Team Average ($125/hr)</option>
                                        {Object.entries(BILLABLE_RATES).filter(([k]) => k !== 'Default').map(([name, rate]) => (
                                            <option key={name} value={name}>{name} (${rate}/hr)</option>
                                        ))}
                                    </select>
                                </div>

                                {/* Custom Hours Override */}
                                <div className="col-md-6 mb-3">
                                    <label className="form-label">
                                        <Clock size={14} className="me-1" />
                                        Custom Hours (override)
                                    </label>
                                    <input
                                        type="number"
                                        className="form-control"
                                        value={customHours}
                                        onChange={(e) => setCustomHours(e.target.value)}
                                        placeholder="Leave empty for auto"
                                        min="0"
                                        step="0.5"
                                    />
                                </div>
                            </div>

                            {/* Buffer */}
                            <div className="row align-items-center mb-3">
                                <div className="col-auto">
                                    <div className="form-check">
                                        <input
                                            type="checkbox"
                                            className="form-check-input"
                                            id="includeBuffer"
                                            checked={includeBuffer}
                                            onChange={(e) => setIncludeBuffer(e.target.checked)}
                                        />
                                        <label className="form-check-label" htmlFor="includeBuffer">
                                            Include Buffer
                                        </label>
                                    </div>
                                </div>
                                {includeBuffer && (
                                    <div className="col-auto">
                                        <div className="input-group input-group-sm">
                                            <input
                                                type="number"
                                                className="form-control"
                                                style={{ width: '70px' }}
                                                value={bufferPercent}
                                                onChange={(e) => setBufferPercent(parseInt(e.target.value) || 0)}
                                                min="0"
                                                max="50"
                                            />
                                            <span className="input-group-text">%</span>
                                        </div>
                                    </div>
                                )}
                            </div>

                            {/* Line Items */}
                            <div className="mb-3">
                                <label className="form-label">Line Items (optional)</label>
                                {lineItems.map((item, index) => (
                                    <div key={index} className="input-group input-group-sm mb-2">
                                        <input
                                            type="text"
                                            className="form-control"
                                            placeholder="Description"
                                            value={item.description}
                                            onChange={(e) => updateLineItem(index, 'description', e.target.value)}
                                        />
                                        <input
                                            type="number"
                                            className="form-control"
                                            placeholder="Hours"
                                            style={{ maxWidth: '80px' }}
                                            value={item.hours || ''}
                                            onChange={(e) => updateLineItem(index, 'hours', e.target.value)}
                                            min="0"
                                            step="0.5"
                                        />
                                        <span className="input-group-text">h @</span>
                                        <input
                                            type="number"
                                            className="form-control"
                                            placeholder="Rate"
                                            style={{ maxWidth: '80px' }}
                                            value={item.rate || ''}
                                            onChange={(e) => updateLineItem(index, 'rate', e.target.value)}
                                            min="0"
                                        />
                                        <button
                                            className="btn btn-outline-danger"
                                            onClick={() => removeLineItem(index)}
                                            disabled={lineItems.length === 1}
                                        >
                                            &times;
                                        </button>
                                    </div>
                                ))}
                                <button
                                    className="btn btn-sm btn-outline-secondary"
                                    onClick={addLineItem}
                                >
                                    + Add Line Item
                                </button>
                            </div>

                            {/* Actions */}
                            <div className="d-flex gap-2">
                                <button
                                    className="btn btn-primary"
                                    onClick={calculateQuote}
                                >
                                    <Calculator size={14} className="me-1" />
                                    Generate Quote
                                </button>
                                <button
                                    className="btn btn-outline-secondary"
                                    onClick={resetForm}
                                >
                                    Reset
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Quote Result */}
                <div className="col-lg-6 mb-4">
                    <div className="card">
                        <div className="card-header d-flex justify-content-between align-items-center">
                            <span>
                                <DollarSign size={18} className="me-2" />
                                Quote Estimate
                            </span>
                            {quote && (
                                <button
                                    className="btn btn-sm btn-outline-primary"
                                    onClick={exportQuote}
                                >
                                    <Download size={14} className="me-1" />
                                    Export
                                </button>
                            )}
                        </div>
                        <div className="card-body">
                            {!quote ? (
                                <div className="text-center text-muted py-5">
                                    <Calculator size={48} className="mb-3 opacity-25" />
                                    <p>Fill in the parameters and click Generate Quote</p>
                                </div>
                            ) : (
                                <>
                                    {/* Project Info */}
                                    <div className="mb-4">
                                        <h5 className="mb-1">{quote.projectName}</h5>
                                        {quote.description && (
                                            <p className="text-muted small mb-2">{quote.description}</p>
                                        )}
                                        <div className="d-flex flex-wrap gap-2">
                                            <span className="badge bg-secondary">{quote.complexity}</span>
                                            <span className="badge bg-info">{quote.workType}</span>
                                            <span className="badge bg-primary">{quote.assignee}</span>
                                        </div>
                                    </div>

                                    {/* Estimate Ranges */}
                                    <div className="row g-3 mb-4">
                                        <div className="col-4">
                                            <div className="card bg-light text-center">
                                                <div className="card-body py-2">
                                                    <small className="text-muted d-block">Minimum</small>
                                                    <span className="fw-bold">{quote.estimatedHours.min}h</span>
                                                    <br />
                                                    <span className="text-success">${quote.estimatedCost.min.toLocaleString()}</span>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="col-4">
                                            <div className="card bg-primary text-white text-center">
                                                <div className="card-body py-2">
                                                    <small className="d-block opacity-75">Typical</small>
                                                    <span className="fw-bold fs-5">{quote.estimatedHours.typical}h</span>
                                                    <br />
                                                    <span>${quote.estimatedCost.typical.toLocaleString()}</span>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="col-4">
                                            <div className="card bg-light text-center">
                                                <div className="card-body py-2">
                                                    <small className="text-muted d-block">Maximum</small>
                                                    <span className="fw-bold">{quote.estimatedHours.max}h</span>
                                                    <br />
                                                    <span className="text-danger">${quote.estimatedCost.max.toLocaleString()}</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Details */}
                                    <table className="table table-sm mb-4">
                                        <tbody>
                                            <tr>
                                                <td className="text-muted">Hourly Rate</td>
                                                <td className="text-end">${quote.hourlyRate}/hr</td>
                                            </tr>
                                            <tr>
                                                <td className="text-muted">Buffer</td>
                                                <td className="text-end">
                                                    {quote.bufferIncluded ? (
                                                        <span className="text-success">
                                                            <CheckCircle size={14} className="me-1" />
                                                            {quote.bufferPercent}%
                                                        </span>
                                                    ) : (
                                                        <span className="text-warning">
                                                            <AlertCircle size={14} className="me-1" />
                                                            None
                                                        </span>
                                                    )}
                                                </td>
                                            </tr>
                                            <tr>
                                                <td className="text-muted">Valid Until</td>
                                                <td className="text-end">
                                                    {new Date(quote.validUntil).toLocaleDateString()}
                                                </td>
                                            </tr>
                                        </tbody>
                                    </table>

                                    {/* Line Items if present */}
                                    {quote.lineItems.length > 0 && (
                                        <div className="mb-3">
                                            <h6>Line Items</h6>
                                            <table className="table table-sm table-striped">
                                                <thead>
                                                    <tr>
                                                        <th>Description</th>
                                                        <th className="text-end">Hours</th>
                                                        <th className="text-end">Amount</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {quote.lineItems.map((item, i) => (
                                                        <tr key={i}>
                                                            <td>{item.description}</td>
                                                            <td className="text-end">{item.hours}h</td>
                                                            <td className="text-end">
                                                                ${(item.hours * item.rate).toLocaleString()}
                                                            </td>
                                                        </tr>
                                                    ))}
                                                    <tr className="table-secondary">
                                                        <td><strong>Line Items Total</strong></td>
                                                        <td></td>
                                                        <td className="text-end">
                                                            <strong>${quote.estimatedCost.lineItemsTotal.toLocaleString()}</strong>
                                                        </td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </div>
                                    )}

                                    {/* Disclaimer */}
                                    <div className="alert alert-info py-2 small mb-0">
                                        <AlertCircle size={14} className="me-1" />
                                        This is an estimate only. Actual time and cost may vary based on
                                        requirements, scope changes, and unforeseen complexities.
                                    </div>
                                </>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default QuoteGenerator;
