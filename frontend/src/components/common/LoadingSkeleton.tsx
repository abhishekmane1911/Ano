import { motion } from 'framer-motion';
import './LoadingSkeleton.css';

interface LoadingSkeletonProps {
  variant?: 'text' | 'circular' | 'rectangular' | 'card';
  width?: string | number;
  height?: string | number;
  className?: string;
}

export const LoadingSkeleton = ({
  variant = 'text',
  width,
  height,
  className = '',
}: LoadingSkeletonProps) => {
  const getVariantClass = () => {
    switch (variant) {
      case 'circular':
        return 'skeleton-circular';
      case 'rectangular':
        return 'skeleton-rectangular';
      case 'card':
        return 'skeleton-card';
      default:
        return 'skeleton-text';
    }
  };

  const style = {
    width: width || (variant === 'circular' ? '40px' : '100%'),
    height: height || (variant === 'text' ? '1em' : variant === 'circular' ? '40px' : '200px'),
  };

  return (
    <motion.div
      className={`skeleton ${getVariantClass()} ${className}`}
      style={style}
      initial={{ opacity: 0.6 }}
      animate={{ opacity: [0.6, 1, 0.6] }}
      transition={{
        duration: 1.5,
        repeat: Infinity,
        ease: 'easeInOut',
      }}
    />
  );
};

interface MessageSkeletonProps {
  count?: number;
}

export const MessageSkeleton = ({ count = 3 }: MessageSkeletonProps) => {
  return (
    <div className="message-skeleton-container">
      {Array.from({ length: count }).map((_, index) => (
        <div key={index} className="message-skeleton">
          <LoadingSkeleton variant="circular" width={40} height={40} />
          <div className="message-skeleton-content">
            <LoadingSkeleton width="30%" height="1em" />
            <LoadingSkeleton width="80%" height="1em" />
            <LoadingSkeleton width="60%" height="1em" />
          </div>
        </div>
      ))}
    </div>
  );
};

interface ProfileCardSkeletonProps {
  count?: number;
}

export const ProfileCardSkeleton = ({ count = 1 }: ProfileCardSkeletonProps) => {
  return (
    <div className="profile-card-skeleton-container">
      {Array.from({ length: count }).map((_, index) => (
        <div key={index} className="profile-card-skeleton">
          <LoadingSkeleton variant="rectangular" height="300px" />
          <div className="profile-card-skeleton-content">
            <LoadingSkeleton width="60%" height="1.5em" />
            <LoadingSkeleton width="40%" height="1em" />
            <div className="profile-card-skeleton-tags">
              <LoadingSkeleton width="80px" height="24px" />
              <LoadingSkeleton width="100px" height="24px" />
              <LoadingSkeleton width="90px" height="24px" />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

interface ListSkeletonProps {
  count?: number;
}

export const ListSkeleton = ({ count = 5 }: ListSkeletonProps) => {
  return (
    <div className="list-skeleton-container">
      {Array.from({ length: count }).map((_, index) => (
        <div key={index} className="list-skeleton-item">
          <LoadingSkeleton variant="circular" width={48} height={48} />
          <div className="list-skeleton-content">
            <LoadingSkeleton width="70%" height="1.2em" />
            <LoadingSkeleton width="50%" height="0.9em" />
          </div>
        </div>
      ))}
    </div>
  );
};
