import { useState } from 'react';
import { adminAPI } from '../../api/admin';
import type { AdminReport } from '../../api/admin';
import UserModerationPanel from './UserModerationPanel.tsx';

interface ReportDetailProps {
  report: AdminReport;
  onUpdate: (updatedReport: AdminReport) => void;
}

const ReportDetail = ({ report, onUpdate }: ReportDetailProps) => {
  const [updating, setUpdating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showReportedUser, setShowReportedUser] = useState(false);
  const [showReporterUser, setShowReporterUser] = useState(false);

  const handleStatusChange = async (newStatus: 'pending' | 'reviewed' | 'resolved') => {
    try {
      setUpdating(true);
      setError(null);
      const updatedReport = await adminAPI.updateReport(report.id, { status: newStatus });
      onUpdate(updatedReport);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to update report status');
    } finally {
      setUpdating(false);
    }
  };

  return (
    <div className="report-detail">
      <div className="report-detail-header">
        <h3>Report Details</h3>
        <span className={`status-badge status-${report.status}`}>
          {report.status}
        </span>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="report-detail-section">
        <h4>Report Information</h4>
        <div className="detail-row">
          <span className="detail-label">Report ID:</span>
          <span className="detail-value">{report.id}</span>
        </div>
        <div className="detail-row">
          <span className="detail-label">Reason:</span>
          <span className={`reason-badge reason-${report.reason}`}>
            {report.reason}
          </span>
        </div>
        <div className="detail-row">
          <span className="detail-label">Created:</span>
          <span className="detail-value">
            {new Date(report.created_at).toLocaleString()}
          </span>
        </div>
        {report.reviewed_at && (
          <>
            <div className="detail-row">
              <span className="detail-label">Reviewed:</span>
              <span className="detail-value">
                {new Date(report.reviewed_at).toLocaleString()}
              </span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Reviewed By:</span>
              <span className="detail-value">{report.reviewed_by_email || 'N/A'}</span>
            </div>
          </>
        )}
      </div>

      <div className="report-detail-section">
        <h4>Description</h4>
        <p className="report-description-full">{report.description}</p>
      </div>

      <div className="report-detail-section">
        <h4>Users Involved</h4>
        <div className="user-info-row">
          <div className="user-info">
            <span className="user-label">Reporter:</span>
            <span className="user-id">{report.reporter_anonymous_id}</span>
            <button
              className="view-user-btn"
              onClick={() => setShowReporterUser(!showReporterUser)}
            >
              {showReporterUser ? 'Hide Details' : 'View Details'}
            </button>
          </div>
          {showReporterUser && (
            <UserModerationPanel anonymousId={report.reporter_anonymous_id} />
          )}
        </div>
        <div className="user-info-row">
          <div className="user-info">
            <span className="user-label">Reported User:</span>
            <span className="user-id">{report.reported_anonymous_id}</span>
            <button
              className="view-user-btn"
              onClick={() => setShowReportedUser(!showReportedUser)}
            >
              {showReportedUser ? 'Hide Details' : 'View Details'}
            </button>
          </div>
          {showReportedUser && (
            <UserModerationPanel anonymousId={report.reported_anonymous_id} />
          )}
        </div>
      </div>

      <div className="report-detail-section">
        <h4>Update Status</h4>
        <div className="status-actions">
          <button
            className="status-btn status-btn-pending"
            onClick={() => handleStatusChange('pending')}
            disabled={updating || report.status === 'pending'}
          >
            Mark as Pending
          </button>
          <button
            className="status-btn status-btn-reviewed"
            onClick={() => handleStatusChange('reviewed')}
            disabled={updating || report.status === 'reviewed'}
          >
            Mark as Reviewed
          </button>
          <button
            className="status-btn status-btn-resolved"
            onClick={() => handleStatusChange('resolved')}
            disabled={updating || report.status === 'resolved'}
          >
            Mark as Resolved
          </button>
        </div>
      </div>
    </div>
  );
};

export default ReportDetail;
