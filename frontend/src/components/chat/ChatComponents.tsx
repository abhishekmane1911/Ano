import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Pin } from 'lucide-react';
import { useChatStore } from '../../stores/chatStore';

// --- Typing Indicator ---
export const TypingIndicator = ({ chatroomId }: { chatroomId: string }) => {
  const { typingUsers } = useChatStore();
  const [users, setUsers] = useState<string[]>([]);

  useEffect(() => {
    const interval = setInterval(() => {
      const active = (typingUsers[chatroomId] || [])
        .filter(u => Date.now() - u.timestamp < 5000)
        .map(u => u.profile_id);
      setUsers(active);
    }, 1000);
    return () => clearInterval(interval);
  }, [typingUsers, chatroomId]);

  if (users.length === 0) return <div className="h-5" />;

  return (
    <div className="flex items-center gap-2 text-xs text-slate-400 dark:text-slate-500 h-5 pl-1">
      <div className="flex gap-0.5">
        {[0, 1, 2].map(i => (
          <motion.span
            key={i}
            animate={{ opacity: [0.3, 1, 0.3] }}
            transition={{ duration: 1.2, repeat: Infinity, delay: i * 0.15 }}
            className="w-1 h-1 bg-slate-400 rounded-full"
          />
        ))}
      </div>
      <span>{users.length === 1 ? 'Someone is typing' : 'Several people are typing'}</span>
    </div>
  );
};

// --- Pinned Messages Widget ---
export const PinnedMessages = ({ messages, onMessageClick }: any) => {
  const [isOpen, setIsOpen] = useState(false);
  const pinned = messages.filter((m: any) => m.is_pinned && !m.is_deleted);

  if (pinned.length === 0) return null;

  return (
    <div className="px-4 mobile:px-3 pt-2">
      <div className="border border-slate-200 dark:border-slate-800 rounded-md overflow-hidden">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="w-full flex items-center justify-between px-3 py-2 text-left hover:bg-slate-50 dark:hover:bg-slate-800/40 transition-colors"
        >
          <div className="flex items-center gap-1.5 text-xs font-medium text-slate-600 dark:text-slate-400">
            <Pin size={12} strokeWidth={1.75} />
            <span>{pinned.length} pinned</span>
          </div>
          <span className="text-xs text-slate-400">{isOpen ? 'Hide' : 'Show'}</span>
        </button>

        <AnimatePresence initial={false}>
          {isOpen && (
            <motion.div
              initial={{ height: 0 }}
              animate={{ height: 'auto' }}
              exit={{ height: 0 }}
              transition={{ duration: 0.15 }}
              className="overflow-hidden border-t border-slate-200 dark:border-slate-800"
            >
              {pinned.map((msg: any) => (
                <div
                  key={msg.id}
                  onClick={() => onMessageClick(msg.id)}
                  className="px-3 py-2.5 hover:bg-slate-50 dark:hover:bg-slate-800/40 transition-colors text-sm text-slate-600 dark:text-slate-300 border-b border-slate-100 dark:border-slate-800 last:border-0 cursor-pointer"
                >
                  <div className="flex justify-between text-xs text-slate-400 mb-0.5">
                    <span>{msg.sender_id.slice(0, 8)}</span>
                    <span>{new Date(msg.created_at).toLocaleDateString()}</span>
                  </div>
                  <p className="line-clamp-2">{msg.content}</p>
                </div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};