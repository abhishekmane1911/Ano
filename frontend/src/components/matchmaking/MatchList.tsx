import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { MessageCircle, Clock, Sparkles, ChevronRight } from 'lucide-react';
import { useMatchmakingStore } from '../../stores/matchmakingStore';
import { matchmakingAPI } from '../../api/matchmaking';

const MatchList: React.FC = () => {
  const navigate = useNavigate();
  const { matches, setMatches, setLoading, setError, isLoading } = useMatchmakingStore();

  useEffect(() => {
    loadMatches();
  }, []);

  const loadMatches = async () => {
    try {
      setLoading(true);
      setError(null);
      const matchesData = await matchmakingAPI.getMatches();
      setMatches(matchesData);
    } catch (err: any) {
      console.error('Failed to load matches:', err);
      setError(err.response?.data?.error || 'Failed to load matches');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    const diff = Date.now() - new Date(dateString).getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days} days ago`;
    return new Date(dateString).toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <div className="w-10 h-10 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin mb-4" />
        <p className="text-gray-500 dark:text-gray-400 text-sm font-medium">Loading matches...</p>
      </div>
    );
  }
  
  if (matches.length === 0) {
    return (
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="flex flex-col items-center justify-center py-24 px-4 text-center"
      >
        <div className="w-24 h-24 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mb-6 shadow-inner">
          <Sparkles className="w-10 h-10 text-gray-400 dark:text-gray-500" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">No matches yet</h2>
        <p className="text-gray-500 dark:text-gray-400 max-w-sm mx-auto mb-8 leading-relaxed">
          Start swiping in the Discover tab to find people who share your interests!
        </p>
      </motion.div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pb-20">
      {matches.map((match, i) => {
        // Combine interests and hobbies for a quick preview
        const tags = [
          ...(match.other_profile.interests || []), 
          ...(match.other_profile.hobbies || [])
        ].slice(0, 3);

        return (
          <motion.div
            key={match.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
            onClick={() => navigate(`/matches/${match.id}/chat`)}
            className="group relative bg-white dark:bg-gray-900 rounded-2xl p-5 shadow-sm hover:shadow-xl border border-gray-200 dark:border-gray-800 transition-all duration-300 cursor-pointer"
          >
            {/* Top Row: Avatar & Info */}
            <div className="flex items-start gap-4 mb-4">
              <div className="relative flex-shrink-0">
                <div className="w-16 h-16 rounded-full bg-gray-100 dark:bg-gray-800 overflow-hidden border border-gray-100 dark:border-gray-700">
                  {match.other_profile.avatar ? (
                    <img 
                      src={match.other_profile.avatar} 
                      alt="Match" 
                      className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110" 
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-2xl">👤</div>
                  )}
                </div>
                {/* Online Status Indicator (Optional/Static for now) */}
                <div className="absolute bottom-0 right-0 w-3.5 h-3.5 bg-green-500 border-2 border-white dark:border-gray-900 rounded-full" />
              </div>

              <div className="flex-1 min-w-0 pt-1">
                <div className="flex items-center justify-between">
                  <h3 className="font-bold text-lg text-gray-900 dark:text-white truncate">
                    Anonymous
                  </h3>
                  <span className="text-[10px] font-medium px-2 py-0.5 bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400 rounded-full">
                    {match.other_profile.age}
                  </span>
                </div>
                
                <p className="text-sm text-indigo-600 dark:text-indigo-400 font-medium mb-0.5 capitalize">
                  {match.other_profile.relationship_intent}
                </p>
                
                <div className="flex items-center gap-1.5 text-xs text-gray-400">
                  <Clock size={12} />
                  <span>Matched {formatDate(match.matched_at)}</span>
                </div>
              </div>
            </div>

            {/* Middle: Tags */}
            <div className="flex flex-wrap gap-2 mb-6 h-8 overflow-hidden">
              {tags.length > 0 ? (
                tags.map((tag, idx) => (
                  <span 
                    key={idx} 
                    className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-gray-50 dark:bg-gray-800/50 text-gray-600 dark:text-gray-300 border border-gray-100 dark:border-gray-700/50"
                  >
                    #{tag}
                  </span>
                ))
              ) : (
                <span className="text-xs text-gray-400 italic">No tags shared</span>
              )}
              {tags.length === 3 && (
                <span className="text-xs text-gray-400 self-center">...</span>
              )}
            </div>

            {/* Bottom: Action */}
            <div className="flex items-center justify-between pt-4 border-t border-gray-100 dark:border-gray-800">
              <span className="text-xs font-medium text-gray-400 group-hover:text-gray-600 dark:group-hover:text-gray-300 transition-colors">
                Start a conversation
              </span>
              <button className="flex items-center justify-center w-10 h-10 rounded-full bg-indigo-50 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400 group-hover:bg-indigo-600 group-hover:text-white transition-all duration-300">
                <MessageCircle size={18} className="ml-0.5" />
              </button>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
};

export default MatchList;