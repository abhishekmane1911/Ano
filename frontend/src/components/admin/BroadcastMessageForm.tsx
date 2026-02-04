import { useState } from 'react';
import { adminAPI } from '../../api/admin';

const BroadcastMessageForm = () => {
  const [content, setContent] = useState('');
  const [chatroomId, setChatroomId] = useState('');
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!content.trim()) {
      setError('Message content cannot be empty');
      return;
    }

    try {
      setSending(true);
      setError(null);
      setSuccess(null);

      const data = {
        content: content.trim(),
        ...(chatroomId.trim() && { chatroom_id: chatroomId.trim() }),
      };

      const response = await adminAPI.broadcastMessage(data);
      setSuccess(response.message);
      setContent('');
      setChatroomId('');
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to send broadcast message');
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="broadcast-form-container">
      <div className="broadcast-header">
        <h2>Broadcast Message</h2>
        <p className="broadcast-subtitle">
          Send a message to all chatrooms or a specific chatroom
        </p>
      </div>

      <form onSubmit={handleSubmit} className="broadcast-form">
        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}

        <div className="form-group">
          <label htmlFor="content">Message Content *</label>
          <textarea
            id="content"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Enter your broadcast message..."
            className="broadcast-textarea"
            rows={6}
            maxLength={1000}
            required
          />
          <span className="char-count">
            {content.length} / 1000 characters
          </span>
        </div>

        <div className="form-group">
          <label htmlFor="chatroomId">Chatroom ID (Optional)</label>
          <input
            type="text"
            id="chatroomId"
            value={chatroomId}
            onChange={(e) => setChatroomId(e.target.value)}
            placeholder="Leave empty to broadcast to all chatrooms"
            className="broadcast-input"
          />
          <span className="input-hint">
            Enter a specific chatroom UUID to send to that chatroom only
          </span>
        </div>

        <div className="broadcast-actions">
          <button
            type="submit"
            className="broadcast-submit-btn"
            disabled={sending || !content.trim()}
          >
            {sending ? 'Sending...' : 'Send Broadcast'}
          </button>
          <button
            type="button"
            className="broadcast-clear-btn"
            onClick={() => {
              setContent('');
              setChatroomId('');
              setError(null);
              setSuccess(null);
            }}
            disabled={sending}
          >
            Clear
          </button>
        </div>
      </form>

      <div className="broadcast-info">
        <h3>Broadcast Information</h3>
        <ul>
          <li>Messages will be marked with [ADMIN BROADCAST] prefix</li>
          <li>Messages will appear as system messages in chatrooms</li>
          <li>If no chatroom ID is specified, the message will be sent to all active chatrooms</li>
          <li>Maximum message length is 1000 characters</li>
        </ul>
      </div>
    </div>
  );
};

export default BroadcastMessageForm;
