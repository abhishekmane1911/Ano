import { useState } from 'react';
import { 
  ReputationBadge, 
  TierProgressBar, 
  RankUpAnimation, 
  ReputationStats, 
  CompactReputation, 
  LeaderboardItem,
  type RankTier,
  type ReputationData 
} from './ReputationComponents';
import { GlassCard, GlassButton } from '../ui/Glass';
import { useToast } from '../../hooks/useToast';

const ReputationDemo = () => {
  const [showRankUp, setShowRankUp] = useState(false);
  const toast = useToast();

  // Sample reputation data
  const sampleData: ReputationData = {
    score: 150,
    tier: 'Sophomore',
    level: 3,
    xpForNextLevel: 337.5,
    totalUpvotesReceived: 45,
    totalDownvotesReceived: 8,
  };

  const leaderboardData = [
    { rank: 1, username: 'CampusLegend', tier: 'Campus Legend' as RankTier, score: 2500, level: 12 },
    { rank: 2, username: 'StudyBuddy', tier: 'Senior' as RankTier, score: 1800, level: 10 },
    { rank: 3, username: 'NightOwl', tier: 'Senior' as RankTier, score: 1200, level: 8 },
    { rank: 4, username: 'You', tier: 'Sophomore' as RankTier, score: 150, level: 3, isCurrentUser: true },
    { rank: 5, username: 'Freshman2024', tier: 'Fresher' as RankTier, score: 50, level: 1 },
  ];

  const handleRankUpDemo = () => {
    setShowRankUp(true);
    toast.reputation('Congratulations! You\'ve reached a new level!', 5000, {
      label: 'View Progress',
      onClick: () => console.log('View progress clicked')
    });
  };

  const handleModerationDemo = () => {
    toast.moderation('Content flagged for review. Please follow community guidelines.', 5000, {
      label: 'Learn More',
      onClick: () => console.log('Learn more clicked')
    });
  };

  return (
    <div className="min-h-screen bg-[#f3f4f6] dark:bg-[#0f172a] pt-24 pb-12 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Reputation System Demo
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-400">
            Explore the gamification features of the Ano platform
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Reputation Badges */}
          <GlassCard className="p-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Reputation Badges
            </h2>
            <div className="space-y-4">
              <div>
                <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Different Tiers</h3>
                <div className="flex flex-wrap gap-2">
                  <ReputationBadge tier="Fresher" score={50} />
                  <ReputationBadge tier="Sophomore" score={150} />
                  <ReputationBadge tier="Senior" score={800} />
                  <ReputationBadge tier="Campus Legend" score={2500} />
                </div>
              </div>
              
              <div>
                <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Different Sizes</h3>
                <div className="flex items-center gap-2">
                  <ReputationBadge tier="Sophomore" score={150} size="sm" />
                  <ReputationBadge tier="Sophomore" score={150} size="md" />
                  <ReputationBadge tier="Sophomore" score={150} size="lg" />
                </div>
              </div>
              
              <div>
                <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">With Progress</h3>
                <ReputationBadge tier="Sophomore" score={150} showProgress />
              </div>
            </div>
          </GlassCard>

          {/* Progress Bar */}
          <GlassCard className="p-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Progress Tracking
            </h2>
            <TierProgressBar
              currentScore={sampleData.score}
              tier={sampleData.tier}
              level={sampleData.level}
              xpForNextLevel={sampleData.xpForNextLevel}
            />
          </GlassCard>

          {/* Reputation Stats */}
          <GlassCard className="p-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Detailed Stats
            </h2>
            <ReputationStats data={sampleData} />
          </GlassCard>

          {/* Compact Display */}
          <GlassCard className="p-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Compact Display
            </h2>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <span className="text-sm text-gray-600 dark:text-gray-400">User Profile</span>
                <CompactReputation tier="Senior" level={8} />
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <span className="text-sm text-gray-600 dark:text-gray-400">Comment Author</span>
                <CompactReputation tier="Sophomore" level={3} />
              </div>
            </div>
          </GlassCard>

          {/* Interactive Demos */}
          <GlassCard className="p-6 lg:col-span-2">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Interactive Features
            </h2>
            <div className="flex flex-wrap gap-4">
              <GlassButton onClick={handleRankUpDemo} variant="primary">
                Trigger Rank Up Animation
              </GlassButton>
              <GlassButton onClick={handleModerationDemo} variant="secondary">
                Show Moderation Toast
              </GlassButton>
              <GlassButton 
                onClick={() => toast.success('Great job! You earned 5 XP for this post.')} 
                variant="ghost"
              >
                Show Success Toast
              </GlassButton>
            </div>
          </GlassCard>

          {/* Leaderboard */}
          <GlassCard className="p-6 lg:col-span-2">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Leaderboard
            </h2>
            <div className="space-y-3">
              {leaderboardData.map((item) => (
                <LeaderboardItem
                  key={item.rank}
                  rank={item.rank}
                  username={item.username}
                  tier={item.tier}
                  score={item.score}
                  level={item.level}
                  isCurrentUser={item.isCurrentUser}
                />
              ))}
            </div>
          </GlassCard>
        </div>

        {/* Rank Up Animation */}
        <RankUpAnimation
          isVisible={showRankUp}
          newTier="Senior"
          newLevel={5}
          onComplete={() => setShowRankUp(false)}
        />
      </div>
    </div>
  );
};

export default ReputationDemo;