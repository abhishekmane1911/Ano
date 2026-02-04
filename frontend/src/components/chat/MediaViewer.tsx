import { useEffect } from 'react';
import './Chat.css';

interface MediaViewerProps {
  mediaUrl: string;
  mediaType: 'image' | 'video';
  onClose: () => void;
}

const MediaViewer: React.FC<MediaViewerProps> = ({ mediaUrl, mediaType, onClose }) => {
  useEffect(() => {
    // Close on Escape key
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    
    // Prevent body scroll when viewer is open
    document.body.style.overflow = 'hidden';

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'auto';
    };
  }, [onClose]);

  return (
    <div className="media-viewer-overlay" onClick={onClose}>
      <div className="media-viewer-container" onClick={(e) => e.stopPropagation()}>
        <button className="media-viewer-close" onClick={onClose} title="Close (Esc)">
          ✕
        </button>

        <div className="media-viewer-content">
          {mediaType === 'image' ? (
            <img src={mediaUrl} alt="Full size" className="media-viewer-image" />
          ) : (
            <video src={mediaUrl} controls className="media-viewer-video" />
          )}
        </div>

        <div className="media-viewer-actions">
          <a
            href={mediaUrl}
            download
            className="media-viewer-download"
            onClick={(e) => e.stopPropagation()}
          >
            Download
          </a>
        </div>
      </div>
    </div>
  );
};

export default MediaViewer;
