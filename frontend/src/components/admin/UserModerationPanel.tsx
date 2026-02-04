import { useState, useEffect } from 'react';
import { adminAPI } from '../../api/admin';
import type { AdminUserDetail } from '../../api/admin';

interface UserModerationPanelProps {
  anonymousId: string;
}

const UserModerationPanel = ({ anonymousId }: UserModerationPanelProps) => {
  const [user, setUser] = useState<AdminUserDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showBanConfirm, setShowBanConfirm] = useState(false);
  const [banReason, setBanReason] = useState('');
  const [banning, setBanning] = useState(false);

  useEffect(() => {
    fetchUserDetails();
  }, [anonymousId]);

  const fetchUserDetails = async () => {
    try {
      setLoading(true);
      setError(null);
      const userData = await adminAPI.getUserDetail(anonymousId);
      setUser(userData);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to load user details');
    } finally {
      setLoading(false);
    }
  };

  const handleBanUser = async () => {
    if (!user) return;

    try {
      setBanning(true);
      setError(null);
      await adminAPI.banUser(anonymousId, { reason: banReason });
      // Refresh user details
      await fetchUserDetails();
      setShowBanConfirm(false);
      setBanReason('');
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to ban user');
    } finally {
      setBanning(false);
    }
  };

  if (loading) {
    return <div className="user-moderation-loading">Loading user details...</div>;
  }

  if (error) {
    return <div className="user-moderation-error">{error}</div>;
  }

  if (!user) {
    return <div className="user-moderation-error">User not found</div>;
  }

  return (
    <div className="user-moderation-panel">
      <div className="user-moderation-header">
        <h4>User Profile</h4>
        {user.is_active ? (
          <span className="user-status user-active">Active</span>
        ) : (
          <span className="user-status user-banned">Banned</span>
        )}
      </div>

      <div className="user-moderation-section">
        <h5>Profile Information</h5>
        <div className="user-detail-row">
          <span className="user-detail-label">Anonymous ID:</span>
          <span className="user-detail-value">{user.anonymous_id}</span>
        </div>
        <div className="user-detail-row">
          <span className="user-detail-label">Age:</span>
          <span className="user-detail-value">{user.age}</span>
        </div>
        <div className="user-detail-row">
          <span className="user-detail-label">Relationship Intent:</span>
          <span className="user-detail-value">{user.relationship_intent}</span>
        </div>
        <div className="user-detail-row">
          <span className="user-detail-label">Interests:</span>
          <span className="user-detail-value">
            {user.interests.length > 0 ? user.interests.join(', ') : 'None'}
          </span>
        </div>
        <div className="user-detail-row">
          <span className="user-detail-label">Hobbies:</span>
          <span className="user-detail-value">
            {user.hobbies.length > 0 ? user.hobbies.join(', ') : 'None'}
          </span>
        </div>
        <div className="user-detail-row">
          <span className="user-detail-label">Personality Tags:</span>
          <span className="user-detail-value">
            {user.personality_tags.length > 0 ? user.personality_tags.join(', ') : 'None'}
          </span>
        </div>
        {user.bio && (
          <div className="user-detail-row">
            <span className="user-detail-label">Bio:</span>
            <span className="user-detail-value">{user.bio}</span>
          </div>
        )}
      </div>

      <div className="user-moderation-section">
        <h5>Activity Statistics</h5>
        <div className="user-stats-grid">
          <div className="user-stat">
            <span className="stat-value">{user.reports_received_count}</span>
            <span className="stat-label">Reports Received</span>
          </div>
          <div className="user-stat">
            <span className="stat-value">{user.reports_made_count}</span>
            <span className="stat-label">Reports Made</span>
          </div>
          <div className="user-stat">
            <span className="stat-value">{user.messages_sent_count}</span>
            <span className="stat-label">Messages Sent</span>
          </div>
          <div className="user-stat">
            <span className="stat-value">{user.matches_count}</span>
            <span className="stat-label">Active Matches</span>
          </div>
        </div>
      </div>

      <div className="user-moderation-section">
        <h5>Account Information</h5>
        <div className="user-detail-row">
          <span className="user-detail-label">Date Joined:</span>
          <span className="user-detail-value">
            {new Date(user.date_joined).toLocaleDateString()}
          </span>
        </div>
        <div className="user-detail-row">
          <span className="user-detail-label">Last Login:</span>
          <span className="user-detail-value">
            {user.last_login ? new Date(user.last_login).toLocaleString() : 'Never'}
          </span>
        </div>
      </div>

      {user.is_active && (
        <div className="user-moderation-actions">
          {!showBanConfirm ? (
            <button
              className="ban-user-btn"
              onClick={() => setShowBanConfirm(true)}
            >
              Ban User
            </button>
          ) : (
            <div className="ban-confirm">
              <h5>Confirm Ban</h5>
              <p>Are you sure you want to ban this user?</p>
              <textarea
                placeholder="Reason for ban (optional)"
                value={banReason}
                onChange={(e) => setBanReason(e.target.value)}
                className="ban-reason-input"
              />
              <div className="ban-confirm-actions">
                <button
                  className="ban-confirm-btn"
                  onClick={handleBanUser}
                  disabled={banning}
                >
                  {banning ? 'Banning...' : 'Confirm Ban'}
                </button>
                <button
                  className="ban-cancel-btn"
                  onClick={() => {
                    setShowBanConfirm(false);
                    setBanReason('');
                  }}
                  disabled={banning}
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default UserModerationPanel;
