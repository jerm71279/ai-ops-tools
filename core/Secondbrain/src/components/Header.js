import React from 'react';
import { Cpu, Search, RefreshCw } from 'react-feather';

function Header() {
  return (
    <header className="navbar navbar-expand-lg navbar-dark bg-dark">
      <div className="container-fluid">
        <a className="navbar-brand" href="#">
          <div className="logo-container">
            <div className="logo-icon">
              <Cpu size={26} />
            </div>
            <div>
              <h1>Engineering Command Center</h1>
              <span className="header-subtitle">OberaConnect Second Brain</span>
            </div>
          </div>
        </a>
        <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
          <span className="navbar-toggler-icon"></span>
        </button>
        <div className="collapse navbar-collapse" id="navbarSupportedContent">
          <ul className="navbar-nav me-auto mb-2 mb-lg-0">
          </ul>
          <div className="d-flex">
            <div className="global-search-container">
              <Search size={16} className="global-search-icon" />
              <input type="text" className="form-control" id="globalSearchInput" placeholder="Search projects, tasks, tickets..." />
              <div className="search-results-dropdown" id="searchResultsDropdown">
                <div className="search-loading" id="searchLoading" style={{ display: 'none' }}>
                  Searching...
                </div>
                <div id="searchResultsContent"></div>
              </div>
            </div>
            <div className="user-selector" style={{ display: 'flex', alignItems: 'center', gap: '8px', marginRight: '16px' }}>
              <div className="user-avatar" id="currentUserAvatar" style={{ width: '32px', height: '32px', borderRadius: '50%', background: 'var(--primary)', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px', fontWeight: '600' }}>?</div>
              <select id="currentUserSelect" className="form-select" style={{ minWidth: '150px', fontSize: '13px', padding: '6px 10px' }}>
                <option value="">Select Your Name...</option>
              </select>
            </div>
            <div className="header-time" id="currentTime"></div>
            <button className="btn btn-outline-secondary">
              <RefreshCw size={14} />
              Sync
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Header;