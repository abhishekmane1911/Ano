import { motion } from 'framer-motion';
import { useProfileStore } from '../../stores/profileStore';
import type { MessageReaction } from '../../stores/chatStore';

interface MessageReactionsProps {
  reactions?: MessageReaction[];
  reactionCount?: Record<string, number>;
  onReact: (emoji: string) => void;
  isOwn: boolean;
}

export default function MessageReactions({ reactions = [], reactionCount = {}, onReact, isOwn }: MessageReactionsProps) {
  const { profile } = useProfileStore();
  
  if (!reactionCount || Object.keys(reactionCount).length === 0) return null;

  // Check if current user has reacted with this emoji
  const hasUserReacted = (emoji: string): boolean => {
    if (!profile?.anonymous_id) return false;
    return reactions.some(r => r.emoji === emoji && r.profile_id === profile.anonymous_id);
  };

  return (
    <div className={`flex flex-wrap gap-1 mt-1 ${isOwn ? 'justify-end' : 'justify-start'}`}>
      {Object.entries(reactionCount).map(([emoji, count]: [string, any]) => {
        const userReacted = hasUserReacted(emoji);
        
        return (
          <motion.button
            key={emoji}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={() => onReact(emoji)}
            className={`flex items-center gap-1 px-2 py-0.5 rounded-full text-xs transition-all ${
              userReacted
                ? 'bg-indigo-100 dark:bg-indigo-900/30 border-2 border-indigo-400 dark:border-indigo-600'
                : 'bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:border-indigo-300 dark:hover:border-indigo-700'
            }`}
          >
            <span>{emoji}</span>
            <span className={`font-bold ${userReacted ? 'text-indigo-600 dark:text-indigo-400' : 'text-gray-600 dark:text-gray-300'}`}>
              {count}
            </span>
          </motion.button>
        );
      })}
    </div>
  );
}