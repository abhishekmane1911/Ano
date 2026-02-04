import { useState } from 'react';
import ReportsList from './ReportsList';
import PlatformMetrics from './PlatformMetrics';
import BroadcastMessageForm from './BroadcastMessageForm';
import './Admin.css';

type TabType = 'reports' | 'metrics' | 'broadcast';

const AdminDashboard = () => {
  const [activeTab, setActiveTab] = useState<TabType>('reports');

  return (
    <div className="admin-dashboard">
      <div className="admin-header">
        <h1>Admin Dashboard</h1>
        <p className="admin-subtitle">Manage reports, monitor platform health, and communicate with users</p>
      </div>

      <div className="admin-tabs">
        <button
          className={`admin-tab ${activeTab === 'reports' ? 'active' : ''}`}
          onClick={() => setActiveTab('reports')}
        >
          Reports
        </button>
        <button
          className={`admin-tab ${activeTab === 'metrics' ? 'active' : ''}`}
          onClick={() => setActiveTab('metrics')}
        >
          Platform Metrics
        </button>
        <button
          className={`admin-tab ${activeTab === 'broadcast' ? 'active' : ''}`}
          onClick={() => setActiveTab('broadcast')}
        >
          Broadcast Message
        </button>
      </div>

      <div className="admin-content">
        {activeTab === 'reports' && <ReportsList />}
        {activeTab === 'metrics' && <PlatformMetrics />}
        {activeTab === 'broadcast' && <BroadcastMessageForm />}
      </div>
    </div>
  );
};

export default AdminDashboard;
