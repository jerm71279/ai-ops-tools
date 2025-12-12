import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Login from './components/Login';
import TimeReports from './components/TimeReports'; // Import TimeReports
import { initializeMsal, msalInstance } from './auth';

import Projects from './components/Projects'; // Import Projects component

import TodoList from './components/TodoList'; // Import TodoList component

import Calendar from './components/Calendar'; // Import Calendar component

import ToolsIndex from './components/ToolsIndex'; // Import ToolsIndex component
import TaskKanban from './components/TaskKanban'; // Import TaskKanban component

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  const [isTeamsContext, setIsTeamsContext] = useState(false);

  // Get initial tab from URL parameter (for Teams integration)
  const getInitialTab = () => {
    const urlParams = new URLSearchParams(window.location.search);
    const tabParam = urlParams.get('tab');
    const validTabs = ['projects', 'timereports', 'todos', 'calendar', 'kanban', 'tools'];
    return validTabs.includes(tabParam) ? tabParam : 'projects';
  };

  const [activeTab, setActiveTab] = useState(getInitialTab());

  useEffect(() => {
    const initialize = async () => {
      // Check if running inside Teams
      if (window.microsoftTeams) {
        try {
          await window.microsoftTeams.app.initialize();
          setIsTeamsContext(true);
        } catch (e) {
          // Not in Teams context
        }
      }

      const authResult = await initializeMsal();
      if (authResult) {
        setIsAuthenticated(authResult.isAuthenticated);
        setCurrentUser(authResult.currentUser);
      }
    };
    initialize();
  }, []);

  if (!isAuthenticated) {
    return <Login />;
  }

  return (
    <div>
      <Header />
      <div className="container-fluid mt-3"> {/* Added margin-top for spacing */}
        <ul className="nav nav-pills mb-3" role="tablist">
          <li className="nav-item" role="presentation">
            <button
              className={`nav-link ${activeTab === 'projects' ? 'active' : ''}`}
              onClick={() => setActiveTab('projects')}
              type="button"
              role="tab"
              aria-selected={activeTab === 'projects'}
            >
              Projects
            </button>
          </li>
          <li className="nav-item" role="presentation">
            <button
              className={`nav-link ${activeTab === 'timereports' ? 'active' : ''}`}
              onClick={() => setActiveTab('timereports')}
              type="button"
              role="tab"
              aria-selected={activeTab === 'timereports'}
            >
              Time Reports
            </button>
          </li>
          <li className="nav-item" role="presentation">
            <button
              className={`nav-link ${activeTab === 'todos' ? 'active' : ''}`}
              onClick={() => setActiveTab('todos')}
              type="button"
              role="tab"
              aria-selected={activeTab === 'todos'}
            >
              To-Do List
            </button>
          </li>
          <li className="nav-item" role="presentation">
            <button
              className={`nav-link ${activeTab === 'calendar' ? 'active' : ''}`}
              onClick={() => setActiveTab('calendar')}
              type="button"
              role="tab"
              aria-selected={activeTab === 'calendar'}
            >
              Calendar
            </button>
          </li>
          <li className="nav-item" role="presentation">
            <button
              className={`nav-link ${activeTab === 'kanban' ? 'active' : ''}`}
              onClick={() => setActiveTab('kanban')}
              type="button"
              role="tab"
              aria-selected={activeTab === 'kanban'}
            >
              Task Board
            </button>
          </li>
          <li className="nav-item" role="presentation">
            <button
              className={`nav-link ${activeTab === 'tools' ? 'active' : ''}`}
              onClick={() => setActiveTab('tools')}
              type="button"
              role="tab"
              aria-selected={activeTab === 'tools'}
            >
              Tools Index
            </button>
          </li>
        </ul>

        <div className="tab-content">
          {activeTab === 'projects' && <Projects />}
          {activeTab === 'timereports' && <TimeReports />}
          {activeTab === 'todos' && <TodoList />}
          {activeTab === 'calendar' && <Calendar />}
          {activeTab === 'kanban' && <TaskKanban />}
          {activeTab === 'tools' && <ToolsIndex />} {/* Render ToolsIndex component */}
        </div>
      </div>
    </div>
  );
}

export default App;