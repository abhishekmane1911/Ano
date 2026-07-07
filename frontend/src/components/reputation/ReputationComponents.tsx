import { motion, AnimatePresence } from 'framer-motion';
import { Star, TrendingUp, Award, Crown } from 'lucide-react';
import { useEffect } from 'react';

export type RankTier = 'Fresher' | 'Sophomore' | 'Senior' | 'Campus Legend';

export interface ReputationData {
  score: number;
  tier: RankTier;
  level: number;
  xpForNextLevel: number;
  totalUpvotesReceived: number;
  totalDownvotesReceived: number;
}

const TIER_CONFIG = {
  'Fresher': {
    color: 'text-green-500',
    bgColor: 'bg-green-500/10',
    borderColor: 'border-green-500/30',
    icon: <Star size={16} />,
    minScore: 0,
  },
  'Sophomore': {
    color: 'text-blue-500',
    bgColor: 'bg-blue-500/10',
    borderColor: 'border-blue-500/30',
    icon: <TrendingUp size={16} />,
    minScore: 100,
  },
  'Senior': {
    color: 'text-purple-500',
    bgColor: 'bg-purple-500/10',
    borderColor: 'border-purple-500/30',
    icon: <Award size={16} />,
    minScore: 500,
  },
  'Campus Legend': {
    color: 'text-yellow-500',
    bgColor: 'bg-yellow-500/10',
    borderColor: 'border-yellow-500/30',
    icon: <Crown size={16} />,
    minScore: 2000,
  },
};

interface ReputationBadgeProps {
  tier: RankTier;
  score: number;
  showProgress?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const ReputationBadge = ({
  tier,
  score,
  showProgress = false,
  size = 'md',
  className = ''
}: ReputationBadgeProps) => {
  const config = TIER_CONFIG[tier];

  const sizeClasses = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1.5 text-sm',
    lg: 'px-4 py-2 text-base'
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      className={`inline-flex items-center gap-2 rounded-full backdrop-blur-md border ${config.bgColor} ${config.borderColor} ${config.color} ${sizeClasses[size]} font-medium ${className}`}
    >
      {config.icon}
      <span>{tier}</span>
      {showProgress && (
        <span className="text-xs opacity-75">({score} XP)</span>
      )}
    </motion.div>
  );
};

interface TierProgressBarProps {
  currentScore: number;
  tier: RankTier;
  level: number;
  xpForNextLevel: number;
  className?: string;
}

export const TierProgressBar = ({
  currentScore,
  tier,
  level,
  xpForNextLevel,
  className = ''
}: TierProgressBarProps) => {
  const config = TIER_CONFIG[tier];
  // Backend: level N means you passed (N-1) thresholds
  // Entry threshold for current level = 100 * 1.5^(level-1)  
  // Exit threshold (next level entry) = 100 * 1.5^level
  // xpForNextLevel from API = next_level_xp - current_score (remaining XP)
  const currentLevelThreshold = level > 1 ? 100 * Math.pow(1.5, level - 1) : (level === 1 ? 100 : 0);
  const progressInLevel = Math.max(0, currentScore - currentLevelThreshold);
  const xpNeededForLevel = progressInLevel + xpForNextLevel; // total XP span of this level
  const progressPercentage = xpNeededForLevel > 0 ? Math.min((progressInLevel / xpNeededForLevel) * 100, 100) : 100;

  return (
    <div className={`space-y-2 ${className}`}>
      <div className="flex items-center justify-between text-sm">
        <div className="flex items-center gap-2">
          <span className={`font-medium ${config.color}`}>Level {level}</span>
          <ReputationBadge tier={tier} score={currentScore} size="sm" />
        </div>
        <span className="text-gray-500 dark:text-gray-400">
          {Math.round(progressInLevel)} / {Math.round(xpNeededForLevel)} XP
        </span>
      </div>

      <div className="relative h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
        <motion.div
          className={`absolute top-0 left-0 h-full rounded-full ${config.bgColor.replace('/10', '/50')}`}
          initial={{ width: 0 }}
          animate={{ width: `${progressPercentage}%` }}
          transition={{ duration: 1, ease: 'easeOut' }}
        />

        {/* Shine effect */}
        <div className="absolute top-0 left-0 right-0 h-full bg-gradient-to-r from-transparent via-white/20 to-transparent animate-pulse" />
      </div>

      <div className="text-xs text-gray-500 dark:text-gray-400 text-center">
        {Math.round(xpForNextLevel)} XP to next level
      </div>
    </div>
  );
};

interface RankUpAnimationProps {
  isVisible: boolean;
  newTier: RankTier;
  newLevel: number;
  onComplete?: () => void;
}

export const RankUpAnimation = ({
  isVisible,
  newTier,
  newLevel,
  onComplete
}: RankUpAnimationProps) => {
  const config = TIER_CONFIG[newTier];

  useEffect(() => {
    if (isVisible && onComplete) {
      const timer = setTimeout(onComplete, 3000);
      return () => clearTimeout(timer);
    }
  }, [isVisible, onComplete]);

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
        >
          <motion.div
            initial={{ scale: 0.5, opacity: 0, y: 50 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.5, opacity: 0, y: -50 }}
            className="bg-white/10 dark:bg-black/20 backdrop-blur-xl border border-white/20 dark:border-white/10 rounded-3xl p-8 text-center max-w-md mx-4"
          >
            {/* Animated icon */}
            <motion.div
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ delay: 0.2, type: 'spring', bounce: 0.5 }}
              className={`w-20 h-20 mx-auto mb-6 rounded-full ${config.bgColor} ${config.borderColor} border-2 flex items-center justify-center ${config.color}`}
            >
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
              >
                {config.icon}
              </motion.div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                Rank Up!
              </h2>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                You've reached Level {newLevel}
              </p>
              <ReputationBadge tier={newTier} score={0} size="lg" />
            </motion.div>

            <div className="absolute inset-0 pointer-events-none">
              {[...Array(12)].map((_, i) => (
                <motion.div
                  key={i}
                  className="absolute w-2 h-2 bg-yellow-400 rounded-full"
                  initial={{
                    opacity: 0,
                    x: '50%',
                    y: '50%',
                    scale: 0
                  }}
                  animate={{
                    opacity: [0, 1, 0],
                    x: `${50 + (Math.cos(i * 30 * Math.PI / 180) * 100)}%`,
                    y: `${50 + (Math.sin(i * 30 * Math.PI / 180) * 100)}%`,
                    scale: [0, 1, 0]
                  }}
                  transition={{
                    duration: 2,
                    delay: 0.5 + (i * 0.1),
                    ease: 'easeOut'
                  }}
                />
              ))}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

// Reputation Stats Component
interface ReputationStatsProps {
  data: ReputationData;
  className?: string;
}

export const ReputationStats = ({ data, className = '' }: ReputationStatsProps) => {
  return (
    <div className={`space-y-4 ${className}`}>
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Reputation
        </h3>
        <ReputationBadge tier={data.tier} score={data.score} showProgress />
      </div>

      <TierProgressBar
        currentScore={data.score}
        tier={data.tier}
        level={data.level}
        xpForNextLevel={data.xpForNextLevel}
      />

      <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-200 dark:border-gray-700">
        <div className="text-center">
          <div className="flex items-center justify-center gap-1 text-green-500 mb-1">
            <TrendingUp size={16} />
            <span className="font-semibold">{data.totalUpvotesReceived}</span>
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400">Upvotes</p>
        </div>

        <div className="text-center">
          <div className="flex items-center justify-center gap-1 text-red-500 mb-1">
            <TrendingUp size={16} className="rotate-180" />
            <span className="font-semibold">{data.totalDownvotesReceived}</span>
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400">Downvotes</p>
        </div>
      </div>
    </div>
  );
};

// Compact Reputation Display (for headers, cards, etc.)
interface CompactReputationProps {
  tier: RankTier;
  level: number;
  className?: string;
}

export const CompactReputation = ({
  tier,
  level,
  className = ''
}: CompactReputationProps) => {
  const config = TIER_CONFIG[tier];

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <div className={`w-6 h-6 rounded-full ${config.bgColor} ${config.borderColor} border flex items-center justify-center ${config.color}`}>
        {config.icon}
      </div>
      <div className="text-sm">
        <span className="font-medium text-gray-900 dark:text-white">Lv.{level}</span>
        <span className={`ml-1 ${config.color}`}>{tier}</span>
      </div>
    </div>
  );
};

// Reputation Leaderboard Item Component
interface LeaderboardItemProps {
  rank: number;
  username: string;
  tier: RankTier;
  score: number;
  level: number;
  isCurrentUser?: boolean;
  className?: string;
}

export const LeaderboardItem = ({
  rank,
  username,
  tier,
  score,
  level,
  isCurrentUser = false,
  className = ''
}: LeaderboardItemProps) => {
  const config = TIER_CONFIG[tier];

  const getRankIcon = () => {
    switch (rank) {
      case 1:
        return <Crown className="text-yellow-500" size={20} />;
      case 2:
        return <Award className="text-gray-400" size={20} />;
      case 3:
        return <Award className="text-orange-500" size={20} />;
      default:
        return <span className="text-gray-500 font-bold">#{rank}</span>;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className={`flex items-center gap-4 p-4 rounded-xl backdrop-blur-md border transition-all ${isCurrentUser
        ? 'bg-indigo-500/10 border-indigo-500/30 ring-2 ring-indigo-500/20'
        : 'bg-white/5 dark:bg-black/20 border-white/10 dark:border-white/5 hover:bg-white/10 dark:hover:bg-black/30'
        } ${className}`}
    >
      <div className="flex-shrink-0 w-8 flex justify-center">
        {getRankIcon()}
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <p className={`font-medium truncate ${isCurrentUser ? 'text-indigo-600 dark:text-indigo-400' : 'text-gray-900 dark:text-white'}`}>
            {username} {isCurrentUser && <span className="text-xs">(You)</span>}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <CompactReputation tier={tier} level={level} />
        </div>
      </div>

      <div className="text-right">
        <div className={`font-bold ${config.color}`}>{score}</div>
        <div className="text-xs text-gray-500 dark:text-gray-400">XP</div>
      </div>
    </motion.div>
  );
};