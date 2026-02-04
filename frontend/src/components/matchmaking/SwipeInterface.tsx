import { useEffect, useState } from 'react';
import { motion, AnimatePresence, useMotionValue, useTransform } from 'framer-motion';
import { RefreshCw, Layers } from 'lucide-react';
import { useMatchmakingStore } from '../../stores/matchmakingStore';
import { matchmakingAPI } from '../../api/matchmaking';
import SwipeCard from './SwipeCard';
import MatchNotification from './MatchNotification';

const SwipeInterface: React.FC = () => {
  const {
    profiles,
    currentProfileIndex,
    setProfiles,
    removeCurrentProfile,
    addMatch,
    setLoading,
    setError,
    isLoading,
    error,
  } = useMatchmakingStore();

  const [swipeDirection, setSwipeDirection] = useState<'left' | 'right' | null>(null);
  const [newMatch, setNewMatch] = useState<any>(null);
  const [showMatchNotification, setShowMatchNotification] = useState(false);
  
  // Motion values for gesture tracking
  const x = useMotionValue(0);
  const rotate = useTransform(x, [-200, 200], [-15, 15]); // Subtler rotation
  const opacity = useTransform(x, [-200, -100, 0, 100, 200], [0.5, 1, 1, 1, 0.5]);
  const scale = useTransform(x, [-200, 0, 200], [0.95, 1, 0.95]);

  useEffect(() => {
    if (profiles.length === 0) loadProfiles();
  }, []);

  const loadProfiles = async () => {
    try {
      setLoading(true);
      setError(null);
      const profilesData = await matchmakingAPI.getProfiles();
      setProfiles(profilesData);
    } catch (err: any) {
      console.error('Failed to load profiles:', err);
      setError(err.response?.data?.error || 'Failed to load profiles');
    } finally {
      setLoading(false);
    }
  };

  const handleSwipe = async (direction: 'left' | 'right') => {
    const currentProfile = profiles[currentProfileIndex];
    if (!currentProfile) return;

    setSwipeDirection(direction);

    try {
      const response = await matchmakingAPI.swipe(currentProfile.anonymous_id, direction);

      if (response.is_match && response.match) {
        setNewMatch(response.match);
        setShowMatchNotification(true);
        addMatch(response.match);
      }

      setTimeout(() => {
        removeCurrentProfile();
        setSwipeDirection(null);
        x.set(0); // Reset motion value
      }, 200);
    } catch (err: any) {
      console.error('Failed to record swipe:', err);
      setError(err.response?.data?.error || 'Failed to record swipe');
      setSwipeDirection(null);
    }
  };

  const handleDragEnd = (_event: any, info: any) => {
    const threshold = 100;
    if (info.offset.x > threshold) {
      handleSwipe('right');
    } else if (info.offset.x < -threshold) {
      handleSwipe('left');
    }
  };

  const currentProfile = profiles[currentProfileIndex];

  // Loading State
  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-[600px] w-full">
        <div className="w-16 h-16 border-4 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin mb-4" />
        <p className="text-gray-500 dark:text-gray-400 font-medium">Finding people nearby...</p>
      </div>
    );
  }

  // Error State
  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-[600px] text-center p-6">
        <div className="bg-red-50 dark:bg-red-900/10 p-4 rounded-full mb-4 text-red-500">
          <RefreshCw size={32} />
        </div>
        <p className="text-red-500 mb-4">{error}</p>
        <button onClick={loadProfiles} className="px-6 py-2 bg-indigo-600 text-white rounded-xl shadow-lg hover:bg-indigo-700 transition-colors">
          Retry
        </button>
      </div>
    );
  }

  // Empty State
  if (!currentProfile) {
    return (
      <div className="flex flex-col items-center justify-center h-[600px] text-center p-6 bg-white/10 dark:bg-black/20 backdrop-blur-xl border border-white/20 dark:border-white/10 rounded-3xl shadow-xl">
        <div className="bg-gradient-to-tr from-indigo-100 to-purple-100 dark:from-indigo-900/30 dark:to-purple-900/30 p-6 rounded-full mb-6">
          <Layers size={48} className="text-indigo-600 dark:text-indigo-400" />
        </div>
        <h2 className="text-2xl font-bold text-gray-800 dark:text-white mb-2">That's everyone for now</h2>
        <p className="text-gray-500 dark:text-gray-400 mb-8 max-w-xs">Check back later for new profiles or update your preferences.</p>
        <button 
          onClick={loadProfiles} 
          className="flex items-center gap-2 px-8 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-full font-bold shadow-lg shadow-indigo-500/30 hover:scale-105 transition-transform"
        >
          <RefreshCw size={20} /> Refresh
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-[600px] w-full max-w-md mx-auto relative">
      <div className="absolute -top-10 text-sm font-medium text-gray-500 dark:text-gray-400">
         {profiles.length - currentProfileIndex} profile{profiles.length - currentProfileIndex !== 1 ? 's' : ''} remaining
      </div>

      <div className="relative w-full h-[600px]">
        <AnimatePresence mode="popLayout">
          {/* Active Card */}
          <motion.div
            key={currentProfile.anonymous_id}
            style={{ x, rotate, opacity, scale }}
            drag="x"
            dragConstraints={{ left: 0, right: 0 }}
            dragElastic={0.7}
            onDragEnd={handleDragEnd}
            initial={{ scale: 0.95, opacity: 0, y: 20 }}
            animate={{
              scale: 1,
              opacity: 1,
              y: 0,
              x: swipeDirection === 'left' ? -1000 : swipeDirection === 'right' ? 1000 : 0,
            }}
            exit={{ opacity: 0, scale: 0.95, transition: { duration: 0.2 } }}
            className="absolute inset-0 z-20 cursor-grab active:cursor-grabbing"
          >
            <SwipeCard
              profile={currentProfile}
              onSwipeLeft={() => handleSwipe('left')}
              onSwipeRight={() => handleSwipe('right')}
            />
          </motion.div>
        </AnimatePresence>

        {/* Background Card (Preview) */}
        {profiles[currentProfileIndex + 1] && (
          <div className="absolute inset-0 z-10 transform scale-[0.95] translate-y-4 opacity-60 pointer-events-none">
            <SwipeCard
              profile={profiles[currentProfileIndex + 1]}
              onSwipeLeft={() => {}}
              onSwipeRight={() => {}}
            />
          </div>
        )}
      </div>

      {showMatchNotification && newMatch && (
        <MatchNotification match={newMatch} onClose={() => { setShowMatchNotification(false); setNewMatch(null); }} />
      )}
    </div>
  );
};

export default SwipeInterface;