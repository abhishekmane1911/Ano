import React from 'react';

interface LoadingSpinnerProps {
  size?: 'small' | 'medium' | 'large';
  variant?: 'spinner' | 'dots' | 'pulse';
  className?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'medium',
  variant = 'spinner',
  className = ''
}) => {
  const sizeClasses = {
    small: 'w-4 h-4',
    medium: 'w-6 h-6',
    large: 'w-8 h-8'
  };

  if (variant === 'dots') {
    return (
      <div className={`flex items-center gap-1 ${className}`}>
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className={`${i === 0 ? 'w-1.5 h-1.5' : 'w-2 h-2'} bg-indigo-500 rounded-full animate-bounce`}
            style={{ animationDelay: `${i * 0.15}s` }}
          />
        ))}
      </div>
    );
  }

  if (variant === 'pulse') {
    return (
      <div className={`relative flex items-center justify-center ${sizeClasses[size]} ${className}`}>
        <div className="absolute inset-0 rounded-full bg-indigo-500/20 animate-ping" />
        <div className="w-1/2 h-1/2 rounded-full bg-indigo-500 shadow-[0_0_12px_rgba(99,102,241,0.6)]" />
      </div>
    );
  }

  // Modern dual-ring spinner
  return (
    <div className={`relative ${sizeClasses[size]} ${className}`}>
      <div className="absolute inset-0 rounded-full border-2 border-zinc-200/20 dark:border-zinc-700/30" />
      <div className="absolute inset-0 rounded-full border-2 border-transparent border-t-indigo-500 border-r-indigo-500 animate-[spin_0.8s_linear_infinite]" />
    </div>
  );
};

interface SkeletonProps {
  className?: string;
  variant?: 'text' | 'rectangular' | 'circular';
  width?: string | number;
  height?: string | number;
  lines?: number;
}

export const Skeleton: React.FC<SkeletonProps> = ({
  className = '',
  variant = 'rectangular',
  width,
  height,
  lines = 1
}) => {
  const baseClasses = 'bg-zinc-200/50 dark:bg-zinc-800/50 animate-pulse overflow-hidden relative';

  const getVariantClasses = () => {
    switch (variant) {
      case 'text':
        return 'h-3 rounded-md';
      case 'circular':
        return 'rounded-full';
      case 'rectangular':
      default:
        return 'rounded-lg';
    }
  };

  const style = {
    width: typeof width === 'number' ? `${width}px` : width,
    height: typeof height === 'number' ? `${height}px` : height,
  };

  if (variant === 'text' && lines > 1) {
    return (
      <div className={`space-y-2.5 ${className}`}>
        {Array.from({ length: lines }).map((_, index) => (
          <div
            key={index}
            className={`${baseClasses} ${getVariantClasses()} ${index === lines - 1 ? 'w-2/3' : 'w-full'
              }`}
            style={index === 0 ? style : {}}
          />
        ))}
      </div>
    );
  }

  return (
    <div
      className={`${baseClasses} ${getVariantClasses()} ${className}`}
      style={style}
    >
      <div className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/10 to-transparent opacity-50" />
    </div>
  );
};

interface LoadingCardProps {
  className?: string;
  showAvatar?: boolean;
  lines?: number;
}

export const LoadingCard: React.FC<LoadingCardProps> = ({
  className = '',
  showAvatar = false,
  lines = 3
}) => {
  return (
    <div className={`p-5 bg-zinc-900/40 border border-zinc-800/80 rounded-xl shadow-sm ${className}`}>
      <div className="flex items-start gap-4">
        {showAvatar && (
          <Skeleton variant="circular" width={44} height={44} className="flex-shrink-0" />
        )}
        <div className="flex-1 space-y-3 pt-1">
          <Skeleton variant="text" lines={lines} />
        </div>
      </div>
    </div>
  );
};

interface LoadingListProps {
  items?: number;
  showAvatar?: boolean;
  className?: string;
}

export const LoadingList: React.FC<LoadingListProps> = ({
  items = 3,
  showAvatar = false,
  className = ''
}) => {
  return (
    <div className={`flex flex-col gap-3 ${className}`}>
      {Array.from({ length: items }).map((_, index) => (
        <LoadingCard
          key={index}
          showAvatar={showAvatar}
          lines={2}
          // Slight stagger effect on opacity if you render this dynamically
          className="opacity-90"
        />
      ))}
    </div>
  );
};

interface LoadingOverlayProps {
  isVisible: boolean;
  message?: string;
  children?: React.ReactNode;
}

export const LoadingOverlay: React.FC<LoadingOverlayProps> = ({
  isVisible,
  message = 'Loading workspace...',
  children
}) => {
  if (!isVisible) return <>{children}</>;

  return (
    <div className="relative w-full h-full">
      <div className="pointer-events-none opacity-40 blur-[2px] transition-all duration-300">
        {children}
      </div>
      <div className="absolute inset-0 flex items-center justify-center z-50">
        <div className="flex flex-col items-center gap-4 bg-zinc-950/80 p-6 rounded-2xl border border-zinc-800/50 backdrop-blur-md shadow-2xl">
          <LoadingSpinner size="large" variant="spinner" />
          <p className="text-xs font-medium text-zinc-400 tracking-wide uppercase">{message}</p>
        </div>
      </div>
    </div>
  );
};

interface ProgressBarProps {
  progress: number;
  className?: string;
  showLabel?: boolean;
  animated?: boolean;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  progress,
  className = '',
  showLabel = false,
  animated = true
}) => {
  const clampedProgress = Math.max(0, Math.min(100, progress));

  return (
    <div className={`w-full flex flex-col gap-2 ${className}`}>
      {showLabel && (
        <div className="flex justify-between items-center text-[10px] font-semibold text-zinc-500 uppercase tracking-wider">
          <span>Progress</span>
          <span className="text-zinc-300 tabular-nums">{Math.round(clampedProgress)}%</span>
        </div>
      )}
      <div className="w-full bg-zinc-200/50 dark:bg-zinc-800/50 h-1 rounded-full overflow-hidden flex">
        <div
          className="h-full bg-indigo-500 relative transition-all duration-700 ease-out"
          style={{ width: `${clampedProgress}%` }}
        >
          {animated && (
            <div className="absolute top-0 right-0 bottom-0 w-12 bg-gradient-to-l from-white/40 to-transparent" />
          )}
        </div>
      </div>
    </div>
  );
};

interface PulsingDotProps {
  className?: string;
  color?: 'primary' | 'success' | 'warning' | 'error';
}

export const PulsingDot: React.FC<PulsingDotProps> = ({
  className = '',
  color = 'primary'
}) => {
  const colorClasses = {
    primary: 'bg-indigo-500',
    success: 'bg-emerald-500',
    warning: 'bg-amber-500',
    error: 'bg-rose-500'
  };

  const shadowClasses = {
    primary: 'shadow-[0_0_8px_rgba(99,102,241,0.6)]',
    success: 'shadow-[0_0_8px_rgba(16,185,129,0.6)]',
    warning: 'shadow-[0_0_8px_rgba(245,158,11,0.6)]',
    error: 'shadow-[0_0_8px_rgba(244,63,94,0.6)]'
  };

  return (
    <div className={`relative flex items-center justify-center w-3 h-3 ${className}`}>
      <div className={`absolute w-full h-full ${colorClasses[color]} rounded-full animate-ping opacity-40`} />
      <div className={`w-1.5 h-1.5 ${colorClasses[color]} ${shadowClasses[color]} rounded-full`} />
    </div>
  );
};