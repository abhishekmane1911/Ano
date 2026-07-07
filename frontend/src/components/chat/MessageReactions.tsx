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

  const hasUserReacted = (emoji: string): boolean => {
    if (!profile?.anonymous_id) return false;
    return reactions.some(r => r.emoji === emoji && r.profile_id === profile.anonymous_id);
  };

  return (
    <div className={`flex flex-wrap gap-1 mt-0.5 ${isOwn ? 'justify-end' : 'justify-start'}`}>
      {Object.entries(reactionCount).map(([emoji, count]: [string, any]) => {
        const userReacted = hasUserReacted(emoji);

        return (
          <button
            key={emoji}
            onClick={() => onReact(emoji)}
            className={`flex items-center gap-1 px-1.5 py-0.5 rounded-md text-xs border transition-colors ${userReacted
                ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800'
                : 'bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600'
              }`}
          >
            <span className="text-[13px] leading-none">{emoji}</span>
            <span className={`font-medium ${userReacted ? 'text-blue-700 dark:text-blue-400' : 'text-slate-500 dark:text-slate-400'}`}>
              {count}
            </span>
          </button>
        );
      })}
    </div>
  );
}