import { useState, useEffect } from 'react';
import { adminAPI } from '../../api/admin';
import type { AdminPlatformMetrics } from '../../api/admin';

const PlatformMetrics = () => {
  const [metrics, setMetrics] = useState<AdminPlatformMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());

  const fetchMetrics = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await adminAPI.getPlatformMetrics();
      setMetrics(data);
      setLastRefresh(new Date());
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to load platform metrics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, []);

  if (loading && !metrics) {
    return <div className="metrics-loading">Loading platform metrics...</div>;
  }

  if (error) {
    return (
      <div className="metrics-error">
        <p>{error}</p>
        <button onClick={fetchMetrics} className="retry-btn">
          Retry
        </button>
      </div>
    );
  }

  if (!metrics) {
    return <div className="metrics-error">No metrics available</div>;
  }

  return (
    <div className="platform-metrics-container">
      <div className="metrics-header">
        <h2>Platform Metrics</h2>
        <div className="metrics-actions">
          <span className="last-refresh">
            Last updated: {lastRefresh.toLocaleTimeString()}
          </span>
          <button onClick={fetchMetrics} className="refresh-btn" disabled={loading}>
            {loading ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </div>

      <div className="metrics-grid">
        {/* User Metrics */}
        <div className="metrics-section">
          <h3>User Activity</h3>
          <div className="metrics-cards">
            <div className="metric-card">
              <div className="metric-value">{metrics.active_users_today}</div>
              <div className="metric-label">Active Today</div>
            </div>
            <div className="metric-card">
              <div className="metric-value">{metrics.active_users_week}</div>
              <div className="metric-label">Active This Week</div>
            </div>
            <div className="metric-card">
              <div className="metric-value">{metrics.total_users}</div>
              <div className="metric-label">Total Active Users</div>
            </div>
            <div className="metric-card">
              <div className="metric-value">{metrics.total_profiles}</div>
              <div className="metric-label">Total Profiles</div>
            </div>
          </div>
        </div>

        {/* Message Metrics */}
        <div className="metrics-section">
          <h3>Message Volume</h3>
          <div className="metrics-cards">
            <div className="metric-card">
              <div className="metric-value">{metrics.total_messages_today}</div>
              <div className="metric-label">Messages Today</div>
            </div>
            <div className="metric-card">
              <div className="metric-value">{metrics.total_messages_week}</div>
              <div className="metric-label">Messages This Week</div>
            </div>
            <div className="metric-card">
              <div className="metric-value">{metrics.total_messages}</div>
              <div className="metric-label">Total Messages</div>
            </div>
          </div>
        </div>

        {/* Engagement Metrics */}
        <div className="metrics-section">
          <h3>Platform Engagement</h3>
          <div className="metrics-cards">
            <div className="metric-card">
              <div className="metric-value">{metrics.total_matches}</div>
              <div className="metric-label">Active Matches</div>
            </div>
            <div className="metric-card">
              <div className="metric-value">{metrics.total_chatrooms}</div>
              <div className="metric-label">Active Chatrooms</div>
            </div>
          </div>
        </div>

        {/* Moderation Metrics */}
        <div className="metrics-section">
          <h3>Moderation</h3>
          <div className="metrics-cards">
            <div className="metric-card metric-card-warning">
              <div className="metric-value">{metrics.total_reports_pending}</div>
              <div className="metric-label">Pending Reports</div>
            </div>
            <div className="metric-card">
              <div className="metric-value">{metrics.total_reports}</div>
              <div className="metric-label">Total Reports</div>
            </div>
          </div>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="metrics-summary">
        <h3>Quick Stats</h3>
        <div className="summary-grid">
          <div className="summary-item">
            <span className="summary-label">Average Messages per User:</span>
            <span className="summary-value">
              {metrics.total_users > 0
                ? (metrics.total_messages / metrics.total_users).toFixed(2)
                : '0'}
            </span>
          </div>
          <div className="summary-item">
            <span className="summary-label">Match Rate:</span>
            <span className="summary-value">
              {metrics.total_profiles > 0
                ? ((metrics.total_matches / metrics.total_profiles) * 100).toFixed(1)
                : '0'}
              %
            </span>
          </div>
          <div className="summary-item">
            <span className="summary-label">Report Rate:</span>
            <span className="summary-value">
              {metrics.total_users > 0
                ? ((metrics.total_reports / metrics.total_users) * 100).toFixed(2)
                : '0'}
              %
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PlatformMetrics;
