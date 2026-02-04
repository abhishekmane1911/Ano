import { useState, useEffect } from 'react';
import { adminAPI } from '../../api/admin';
import type { AdminReport } from '../../api/admin';
import ReportDetail from './ReportDetail.tsx';

const ReportsList = () => {
  const [reports, setReports] = useState<AdminReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedReport, setSelectedReport] = useState<AdminReport | null>(null);
  const [statusFilter, setStatusFilter] = useState<'all' | 'pending' | 'reviewed' | 'resolved'>('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const fetchReports = async () => {
    try {
      setLoading(true);
      setError(null);
      const filterStatus = statusFilter === 'all' ? undefined : statusFilter;
      const response = await adminAPI.listReports(filterStatus, '-created_at', currentPage);
      setReports(response.results);
      setTotalPages(Math.ceil(response.count / 20));
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to load reports');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, [statusFilter, currentPage]);

  const handleReportUpdate = (updatedReport: AdminReport) => {
    setReports(reports.map(r => r.id === updatedReport.id ? updatedReport : r));
    setSelectedReport(updatedReport);
  };

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'pending':
        return 'status-badge status-pending';
      case 'reviewed':
        return 'status-badge status-reviewed';
      case 'resolved':
        return 'status-badge status-resolved';
      default:
        return 'status-badge';
    }
  };

  const getReasonBadgeClass = (reason: string) => {
    switch (reason) {
      case 'harassment':
        return 'reason-badge reason-harassment';
      case 'spam':
        return 'reason-badge reason-spam';
      case 'inappropriate':
        return 'reason-badge reason-inappropriate';
      default:
        return 'reason-badge reason-other';
    }
  };

  if (loading && reports.length === 0) {
    return <div className="admin-loading">Loading reports...</div>;
  }

  return (
    <div className="reports-list-container">
      <div className="reports-header">
        <h2>Reports Management</h2>
        <div className="reports-filters">
          <label>Filter by status:</label>
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value as any);
              setCurrentPage(1);
            }}
            className="filter-select"
          >
            <option value="all">All Reports</option>
            <option value="pending">Pending</option>
            <option value="reviewed">Reviewed</option>
            <option value="resolved">Resolved</option>
          </select>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="reports-layout">
        <div className="reports-list">
          {reports.length === 0 ? (
            <div className="no-reports">No reports found</div>
          ) : (
            reports.map((report) => (
              <div
                key={report.id}
                className={`report-item ${selectedReport?.id === report.id ? 'selected' : ''}`}
                onClick={() => setSelectedReport(report)}
              >
                <div className="report-item-header">
                  <span className={getStatusBadgeClass(report.status)}>
                    {report.status}
                  </span>
                  <span className={getReasonBadgeClass(report.reason)}>
                    {report.reason}
                  </span>
                </div>
                <div className="report-item-body">
                  <p className="report-ids">
                    <strong>Reporter:</strong> {report.reporter_anonymous_id.substring(0, 8)}...
                    <br />
                    <strong>Reported:</strong> {report.reported_anonymous_id.substring(0, 8)}...
                  </p>
                  <p className="report-description">
                    {report.description.substring(0, 100)}
                    {report.description.length > 100 ? '...' : ''}
                  </p>
                  <p className="report-date">
                    {new Date(report.created_at).toLocaleString()}
                  </p>
                </div>
              </div>
            ))
          )}
        </div>

        <div className="report-detail-panel">
          {selectedReport ? (
            <ReportDetail report={selectedReport} onUpdate={handleReportUpdate} />
          ) : (
            <div className="no-selection">Select a report to view details</div>
          )}
        </div>
      </div>

      {totalPages > 1 && (
        <div className="pagination">
          <button
            onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
            disabled={currentPage === 1}
            className="pagination-btn"
          >
            Previous
          </button>
          <span className="pagination-info">
            Page {currentPage} of {totalPages}
          </span>
          <button
            onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
            disabled={currentPage === totalPages}
            className="pagination-btn"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
};

export default ReportsList;
