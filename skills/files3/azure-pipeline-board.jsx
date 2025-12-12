import React, { useState, useMemo } from 'react';
import { Search, Filter, ChevronDown, ChevronRight, CheckCircle2, Clock, AlertCircle, Circle, Pause, ArrowRight } from 'lucide-react';

const initialServices = [
  // Identity & Access - Phase 1
  { id: 'IAM-001', name: 'Microsoft Entra ID', category: 'Identity & Access', phase: 1, priority: 'Critical', labStatus: 'Not Started', oberaStatus: 'Not Started', customerStatus: 'Not Started', dependencies: [], notes: 'Foundation for all Azure services' },
  { id: 'IAM-002', name: 'Entra ID P1/P2', category: 'Identity & Access', phase: 1, priority: 'Critical', labStatus: 'Not Started', oberaStatus: 'Not Started', customerStatus: 'Not Started', dependencies: ['IAM-001'], notes: 'Conditional Access, Identity Protection' },
  { id: 'IAM-003', name: 'Entra Connect / Cloud Sync', category: 'Identity & Access', phase: 1, priority: 'High', labStatus: 'Not Started', oberaStatus: 'Not Started', customerStatus: 'Not Started', dependencies: ['IAM-001'], notes: 'Hybrid identity sync' },
  { id: 'IAM-004', name: 'Privileged Identity Management', category: 'Identity & Access', phase: 2, priority: 'High', labStatus: 'Not Started', oberaStatus: 'Not Started', customerStatus: 'Not Started', dependencies: ['IAM-002'], notes: 'Just-in-time privileged access' },
  
  // Security
  { id: 'SEC-001', name: 'Defender for Endpoint', category: 'Security', phase: 1, priority: 'Critical', labStatus: 'Not Started', oberaStatus: 'Not Started', customerStatus: 'Not Started', dependencies: ['IAM-001', 'EPM-001'], notes: 'EDR/XDR, integrates with Intune' },
  { id: 'SEC-002', name: 'Defender for Office 365', category: 'Security', phase: 1, priority: 'Critical', labStatus: 'Not Started', oberaStatus: 'Not Started', customerStatus: 'Not Started', dependencies: ['IAM-001'], notes: 'Email security, anti-phishing' },
  { id: 'SEC-003', name: 'Defender for Identity', category: 'Security', phase: 1, priority: 'High', labStatus: 'Not Started', oberaStatus: 'Not Started', customerStatus: 'Not Started', dependencies: ['IAM-003'], notes: 'Protects on-prem AD' },
  { id: 'SEC-004', name: 'Defender for Cloud', category: 'Security', phase: 2, priority: 'High', labStatus: 'Not Started', oberaStatus: 'Not Started', customerStatus: 'Not Started', dependencies: ['MON-001'], notes: 'CSPM + workload protection' },
  { id: 'SEC-005', name: 'Microsoft Sentinel', category: 'Security', phase: 2, priority: 'Critical', labStatus: 'Not Started', oberaStatus: 'Not Started', customerStatus: 'Not Started', dependencies: ['MON-002'], notes: 'SIEM/SOAR - Major MSP opportunity' },
  { id: 'SEC-006', name: 'Azure Key Vault', category: 'Security', phase: 2, priority: 'High', labStatus: 'Not Started', oberaStatus: 'Not Started', customerStatus: 'Not Started', dependencies: ['IAM-001'], notes: 'Secrets, keys, certificates' },
  
  // Endpoint Management
  { id: 'EPM-001', name: 'Microsoft Intune', category: 'Endpoint Mgmt', phase: 1, priority: 'Critical', labStatus: 'Not Started', oberaStatus: 'Not Started', customerStatus: 'Not Started', dependencies: ['IAM-001'], notes: 'MDM/MAM for all devices' },
  { id: 'EPM-002', name: 'Windows Autopilot', category: 'Endpoint Mgmt', phase: 1, priority: 'High', labStatus: 'Not Started', oberaStatus: 'Not Started', customerStatus: 'Not Started', dependencies: ['EPM-001'], notes: 'Zero-touch provisioning' },
  { id: 'EPM-003', name: 'Windows 365 Cloud PC', category: 'Endpoint Mgmt', phase: 2, priority: 'High', labStatus: 'Not Started', oberaStatus: 'Not Started', customerStatus: 'Not Started', dependencies: ['IAM-001', 'EPM-001'], notes: 'Fixed-price cloud desktops' },
  
  // Virtual Desktop
  { id: 'VDI-001', name: 'Azure Virtual Desktop', category: 'Virtual Desktop', phase: 3, priority: 'High', labStatus: 'Not Started', oberaStatus: 'Not Started', customerStatus: 'Not Started', dependencies: ['NET-001', 'STR-001', 'IAM-001'], notes: 'Full VDI solution' },
  { id: 'VDI-002', name: 'Nerdio Manager for MSP', category: 'Virtual Desktop', phase: 2, priority: 'High', labStatus: 'Not Started', oberaStatus: 'Not Started', customerStatus: 'Not Started', dependencies: ['EPM-003'], notes: 'Third-party AVD automation' },
  
  // Networking
  { id: 'NET-001', name: 'Azure Virtual Network', category: 'Networking', phase: 1, priority: 'Critical', labStatus: 'Not Started', oberaStatus: 'Not Started', customerStatus: 'Not Started', dependencies: [], notes: 'Foundation: subnets, NSGs' },
  { id: 'NET-002', name: 'Azure VPN Gateway', category: 'Networking', phase: 1, priority: 'Critical', labStatus: 'Not Started', oberaStatus: 'Not Started', customerStatus: 'Not Started', dependencies: ['NET-001'], notes: 'Site-to-site VPN' },
  { id: 'NET-003', name: 'Azure DNS', category: 'Networking', phase: 1, priority: 'High', labStatus: 'Not Started', oberaStatus: 'Not Started', customerStatus: 'Not Started', dependencies: ['NET-001'], notes: 'DNS hosting, private zones' },
  { id: 'NET-004', name: 'Azure Bastion', category: 'Networking', phase: 2, priority: 'High', labStatus: 'Not Started', oberaStatus: 'Not Started', customerStatus: 'Not Started', dependencies: ['NET-001'], notes: 'Secure RDP/SSH' },
  { id: 'NET-005', name: 'Azure Private Link', category: 'Networking', phase: 2, priority: 'High', labStatus: 'Not Started', oberaStatus: 'Not Started', customerStatus: 'Not Started', dependencies: ['NET-001'], notes: 'Private access to PaaS' },
  
  // Compute
  { id: 'CMP-001', name: 'Azure Virtual Machines', category: 'Compute', phase: 1, priority: 'Critical', labStatus: 'Not Started', oberaStatus: 'Not Started', customerStatus: 'Not Started', dependencies: ['NET-001', 'STR-003'], notes: 'IaaS VMs' },
  { id: 'CMP-002', name: 'Reserved Instances', category: 'Compute', phase: 1, priority: 'High', labStatus: 'Not Started', oberaStatus: 'Not Started', customerStatus: 'Not Started', dependencies: ['CMP-001'], notes: '30-72% savings' },
  
  // Storage
  { id: 'STR-001', name: 'Azure Blob Storage', category: 'Storage', phase: 1, priority: 'Critical', labStatus: 'Not Started', oberaStatus: 'Not Started', customerStatus: 'Not Started', dependencies: ['IAM-001'], notes: 'Object storage, tiering' },
  { id: 'STR-002', name: 'Azure Files', category: 'Storage', phase: 1, priority: 'High', labStatus: 'Not Started', oberaStatus: 'Not Started', customerStatus: 'Not Started', dependencies: ['IAM-001', 'NET-001'], notes: 'Managed SMB/NFS shares' },
  { id: 'STR-003', name: 'Azure Managed Disks', category: 'Storage', phase: 1, priority: 'Critical', labStatus: 'Not Started', oberaStatus: 'Not Started', customerStatus: 'Not Started', dependencies: [], notes: 'Block storage for VMs' },
  { id: 'STR-004', name: 'Azure File Sync', category: 'Storage', phase: 2, priority: 'High', labStatus: 'Not Started', oberaStatus: 'Not Started', customerStatus: 'Not Started', dependencies: ['STR-002'], notes: 'Sync on-prem to Azure' },
  
  // Backup & DR
  { id: 'BDR-001', name: 'Azure Backup', category: 'Backup & DR', phase: 1, priority: 'Critical', labStatus: 'Not Started', oberaStatus: 'Not Started', customerStatus: 'Not Started', dependencies: ['BDR-002'], notes: 'Native backup for VMs, SQL' },
  { id: 'BDR-002', name: 'Recovery Services Vault', category: 'Backup & DR', phase: 1, priority: 'Critical', labStatus: 'Not Started', oberaStatus: 'Not Started', customerStatus: 'Not Started', dependencies: [], notes: 'Central backup management' },
  { id: 'BDR-003', name: 'Azure Site Recovery', category: 'Backup & DR', phase: 2, priority: 'High', labStatus: 'Not Started', oberaStatus: 'Not Started', customerStatus: 'Not Started', dependencies: ['BDR-002', 'NET-001'], notes: 'DR orchestration' },
  
  // Monitoring
  { id: 'MON-001', name: 'Azure Monitor', category: 'Monitoring', phase: 1, priority: 'Critical', labStatus: 'Not Started', oberaStatus: 'Not Started', customerStatus: 'Not Started', dependencies: [], notes: 'Metrics, logs, alerts' },
  { id: 'MON-002', name: 'Log Analytics Workspace', category: 'Monitoring', phase: 1, priority: 'Critical', labStatus: 'Not Started', oberaStatus: 'Not Started', customerStatus: 'Not Started', dependencies: ['MON-001'], notes: 'Central log aggregation' },
  { id: 'MON-003', name: 'Azure Lighthouse', category: 'Monitoring', phase: 1, priority: 'Critical', labStatus: 'Not Started', oberaStatus: 'Not Started', customerStatus: 'Not Started', dependencies: ['IAM-001'], notes: 'Multi-tenant MSP management' },
  { id: 'MON-004', name: 'Azure Cost Management', category: 'Monitoring', phase: 1, priority: 'Critical', labStatus: 'Not Started', oberaStatus: 'Not Started', customerStatus: 'Not Started', dependencies: [], notes: 'Cost analysis and optimization' },
  { id: 'MON-005', name: 'Azure Arc', category: 'Monitoring', phase: 2, priority: 'High', labStatus: 'Not Started', oberaStatus: 'Not Started', customerStatus: 'Not Started', dependencies: ['MON-001'], notes: 'Manage on-prem from Azure' },
  
  // Migration
  { id: 'MIG-001', name: 'Azure Migrate', category: 'Migration', phase: 1, priority: 'Critical', labStatus: 'Not Started', oberaStatus: 'Not Started', customerStatus: 'Not Started', dependencies: [], notes: 'Discovery, assessment, migration' },
  
  // Databases
  { id: 'DB-001', name: 'Azure SQL Database', category: 'Databases', phase: 2, priority: 'High', labStatus: 'Not Started', oberaStatus: 'Not Started', customerStatus: 'Not Started', dependencies: ['NET-001'], notes: 'Managed SQL Server PaaS' },
  { id: 'DB-002', name: 'SQL Server on Azure VMs', category: 'Databases', phase: 2, priority: 'High', labStatus: 'Not Started', oberaStatus: 'Not Started', customerStatus: 'Not Started', dependencies: ['CMP-001'], notes: 'Full SQL Server IaaS' },
];

const statusConfig = {
  'Not Started': { color: 'bg-gray-100 text-gray-600', icon: Circle },
  'In Progress': { color: 'bg-amber-100 text-amber-700', icon: Clock },
  'Testing': { color: 'bg-blue-100 text-blue-700', icon: AlertCircle },
  'Complete': { color: 'bg-green-100 text-green-700', icon: CheckCircle2 },
  'Blocked': { color: 'bg-red-100 text-red-700', icon: Pause },
};

const phaseColors = {
  1: 'bg-green-50 border-green-200',
  2: 'bg-amber-50 border-amber-200',
  3: 'bg-rose-50 border-rose-200',
  4: 'bg-blue-50 border-blue-200',
};

const priorityColors = {
  'Critical': 'bg-red-500',
  'High': 'bg-orange-400',
  'Medium': 'bg-yellow-400',
  'Low': 'bg-gray-400',
};

export default function AzurePipelineBoard() {
  const [services, setServices] = useState(initialServices);
  const [selectedPhase, setSelectedPhase] = useState('all');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedCards, setExpandedCards] = useState({});
  const [viewMode, setViewMode] = useState('kanban');

  const categories = useMemo(() => 
    ['all', ...new Set(services.map(s => s.category))], 
    [services]
  );

  const filteredServices = useMemo(() => {
    return services.filter(s => {
      const phaseMatch = selectedPhase === 'all' || s.phase === parseInt(selectedPhase);
      const categoryMatch = selectedCategory === 'all' || s.category === selectedCategory;
      const searchMatch = searchTerm === '' || 
        s.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        s.id.toLowerCase().includes(searchTerm.toLowerCase());
      return phaseMatch && categoryMatch && searchMatch;
    });
  }, [services, selectedPhase, selectedCategory, searchTerm]);

  const updateStatus = (id, stage, newStatus) => {
    setServices(prev => prev.map(s => 
      s.id === id ? { ...s, [stage]: newStatus } : s
    ));
  };

  const toggleExpand = (id) => {
    setExpandedCards(prev => ({ ...prev, [id]: !prev[id] }));
  };

  const getStageServices = (stage, status) => {
    return filteredServices.filter(s => s[stage] === status);
  };

  const stats = useMemo(() => {
    const total = filteredServices.length;
    const labComplete = filteredServices.filter(s => s.labStatus === 'Complete').length;
    const oberaComplete = filteredServices.filter(s => s.oberaStatus === 'Complete').length;
    const customerReady = filteredServices.filter(s => s.customerStatus === 'Complete').length;
    return { total, labComplete, oberaComplete, customerReady };
  }, [filteredServices]);

  const ServiceCard = ({ service }) => {
    const isExpanded = expandedCards[service.id];
    const StatusIcon = statusConfig[service.labStatus].icon;
    
    return (
      <div className={`border rounded-lg p-3 mb-2 ${phaseColors[service.phase]} shadow-sm`}>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${priorityColors[service.priority]}`} />
              <span className="text-xs text-gray-500 font-mono">{service.id}</span>
            </div>
            <h4 className="font-medium text-sm mt-1">{service.name}</h4>
            <p className="text-xs text-gray-500">{service.category}</p>
          </div>
          <button onClick={() => toggleExpand(service.id)} className="p-1">
            {isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
          </button>
        </div>
        
        {isExpanded && (
          <div className="mt-3 pt-3 border-t border-gray-200 space-y-2">
            <p className="text-xs text-gray-600">{service.notes}</p>
            
            <div className="space-y-1">
              <div className="flex items-center justify-between text-xs">
                <span className="text-gray-500">Lab:</span>
                <select 
                  value={service.labStatus}
                  onChange={(e) => updateStatus(service.id, 'labStatus', e.target.value)}
                  className={`text-xs px-2 py-1 rounded ${statusConfig[service.labStatus].color}`}
                >
                  {Object.keys(statusConfig).map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-gray-500">Obera:</span>
                <select 
                  value={service.oberaStatus}
                  onChange={(e) => updateStatus(service.id, 'oberaStatus', e.target.value)}
                  className={`text-xs px-2 py-1 rounded ${statusConfig[service.oberaStatus].color}`}
                >
                  {Object.keys(statusConfig).map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-gray-500">Customer:</span>
                <select 
                  value={service.customerStatus}
                  onChange={(e) => updateStatus(service.id, 'customerStatus', e.target.value)}
                  className={`text-xs px-2 py-1 rounded ${statusConfig[service.customerStatus].color}`}
                >
                  {Object.keys(statusConfig).map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
            </div>
            
            {service.dependencies.length > 0 && (
              <div className="text-xs">
                <span className="text-gray-500">Dependencies: </span>
                <span className="font-mono text-gray-600">{service.dependencies.join(', ')}</span>
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  const KanbanColumn = ({ title, stage, status, count }) => {
    const columnServices = getStageServices(stage, status);
    const StatusIcon = statusConfig[status].icon;
    
    return (
      <div className="flex-1 min-w-[280px] bg-gray-50 rounded-lg p-3">
        <div className="flex items-center gap-2 mb-3">
          <StatusIcon size={16} className={statusConfig[status].color.split(' ')[1]} />
          <h3 className="font-semibold text-sm">{title}</h3>
          <span className="bg-gray-200 text-gray-600 text-xs px-2 py-0.5 rounded-full">{count}</span>
        </div>
        <div className="space-y-2 max-h-[500px] overflow-y-auto">
          {columnServices.map(s => <ServiceCard key={s.id} service={s} />)}
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <div className="max-w-full mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-4 mb-4">
          <h1 className="text-2xl font-bold text-gray-800">OberaConnect Azure Pipeline Board</h1>
          <p className="text-gray-500 text-sm">Lab → Production → Customer Offering Pipeline</p>
          
          {/* Stats */}
          <div className="grid grid-cols-4 gap-4 mt-4">
            <div className="bg-gray-50 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-gray-800">{stats.total}</div>
              <div className="text-xs text-gray-500">Total Services</div>
            </div>
            <div className="bg-green-50 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-green-700">{stats.labComplete}</div>
              <div className="text-xs text-gray-500">Lab Complete</div>
            </div>
            <div className="bg-blue-50 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-blue-700">{stats.oberaComplete}</div>
              <div className="text-xs text-gray-500">Obera Complete</div>
            </div>
            <div className="bg-purple-50 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-purple-700">{stats.customerReady}</div>
              <div className="text-xs text-gray-500">Customer Ready</div>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm p-4 mb-4">
          <div className="flex flex-wrap gap-4 items-center">
            <div className="flex items-center gap-2">
              <Search size={16} className="text-gray-400" />
              <input
                type="text"
                placeholder="Search services..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="border rounded px-3 py-1.5 text-sm w-48"
              />
            </div>
            
            <div className="flex items-center gap-2">
              <Filter size={16} className="text-gray-400" />
              <select
                value={selectedPhase}
                onChange={(e) => setSelectedPhase(e.target.value)}
                className="border rounded px-3 py-1.5 text-sm"
              >
                <option value="all">All Phases</option>
                <option value="1">Phase 1</option>
                <option value="2">Phase 2</option>
                <option value="3">Phase 3</option>
                <option value="4">Phase 4</option>
              </select>
            </div>
            
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="border rounded px-3 py-1.5 text-sm"
            >
              {categories.map(c => (
                <option key={c} value={c}>{c === 'all' ? 'All Categories' : c}</option>
              ))}
            </select>

            <div className="flex gap-1 ml-auto">
              <button
                onClick={() => setViewMode('kanban')}
                className={`px-3 py-1.5 text-sm rounded ${viewMode === 'kanban' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100'}`}
              >
                Kanban
              </button>
              <button
                onClick={() => setViewMode('pipeline')}
                className={`px-3 py-1.5 text-sm rounded ${viewMode === 'pipeline' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100'}`}
              >
                Pipeline
              </button>
            </div>
          </div>
          
          {/* Phase Legend */}
          <div className="flex gap-4 mt-3 text-xs">
            <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-green-200" /> Phase 1</span>
            <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-amber-200" /> Phase 2</span>
            <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-rose-200" /> Phase 3</span>
            <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-blue-200" /> Phase 4</span>
            <span className="mx-2">|</span>
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-red-500" /> Critical</span>
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-orange-400" /> High</span>
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-yellow-400" /> Medium</span>
          </div>
        </div>

        {/* Board Views */}
        {viewMode === 'kanban' ? (
          <div className="space-y-6">
            {/* Lab Stage */}
            <div>
              <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
                <span className="bg-purple-100 text-purple-700 px-2 py-1 rounded text-sm">Stage 1</span>
                Lab Tenant Development
              </h2>
              <div className="flex gap-4 overflow-x-auto pb-2">
                <KanbanColumn title="Not Started" stage="labStatus" status="Not Started" count={getStageServices('labStatus', 'Not Started').length} />
                <KanbanColumn title="In Progress" stage="labStatus" status="In Progress" count={getStageServices('labStatus', 'In Progress').length} />
                <KanbanColumn title="Testing" stage="labStatus" status="Testing" count={getStageServices('labStatus', 'Testing').length} />
                <KanbanColumn title="Complete" stage="labStatus" status="Complete" count={getStageServices('labStatus', 'Complete').length} />
              </div>
            </div>

            {/* Obera Stage */}
            <div>
              <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
                <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded text-sm">Stage 2</span>
                Obera Tenant Production
              </h2>
              <div className="flex gap-4 overflow-x-auto pb-2">
                <KanbanColumn title="Not Started" stage="oberaStatus" status="Not Started" count={getStageServices('oberaStatus', 'Not Started').length} />
                <KanbanColumn title="In Progress" stage="oberaStatus" status="In Progress" count={getStageServices('oberaStatus', 'In Progress').length} />
                <KanbanColumn title="Testing" stage="oberaStatus" status="Testing" count={getStageServices('oberaStatus', 'Testing').length} />
                <KanbanColumn title="Complete" stage="oberaStatus" status="Complete" count={getStageServices('oberaStatus', 'Complete').length} />
              </div>
            </div>

            {/* Customer Stage */}
            <div>
              <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
                <span className="bg-green-100 text-green-700 px-2 py-1 rounded text-sm">Stage 3</span>
                Customer Offering
              </h2>
              <div className="flex gap-4 overflow-x-auto pb-2">
                <KanbanColumn title="Not Started" stage="customerStatus" status="Not Started" count={getStageServices('customerStatus', 'Not Started').length} />
                <KanbanColumn title="In Progress" stage="customerStatus" status="In Progress" count={getStageServices('customerStatus', 'In Progress').length} />
                <KanbanColumn title="Testing" stage="customerStatus" status="Testing" count={getStageServices('customerStatus', 'Testing').length} />
                <KanbanColumn title="Complete" stage="customerStatus" status="Complete" count={getStageServices('customerStatus', 'Complete').length} />
              </div>
            </div>
          </div>
        ) : (
          /* Pipeline View */
          <div className="bg-white rounded-lg shadow-sm p-4">
            <div className="space-y-2">
              {filteredServices.map(service => (
                <div key={service.id} className={`flex items-center gap-2 p-3 rounded-lg ${phaseColors[service.phase]}`}>
                  <span className={`w-2 h-2 rounded-full ${priorityColors[service.priority]}`} />
                  <span className="font-mono text-xs text-gray-500 w-16">{service.id}</span>
                  <span className="font-medium text-sm w-48">{service.name}</span>
                  <span className="text-xs text-gray-500 w-28">{service.category}</span>
                  
                  <div className="flex items-center gap-1 flex-1">
                    <span className={`text-xs px-2 py-1 rounded ${statusConfig[service.labStatus].color}`}>
                      Lab: {service.labStatus}
                    </span>
                    <ArrowRight size={14} className="text-gray-400" />
                    <span className={`text-xs px-2 py-1 rounded ${statusConfig[service.oberaStatus].color}`}>
                      Obera: {service.oberaStatus}
                    </span>
                    <ArrowRight size={14} className="text-gray-400" />
                    <span className={`text-xs px-2 py-1 rounded ${statusConfig[service.customerStatus].color}`}>
                      Customer: {service.customerStatus}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
