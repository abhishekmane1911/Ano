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

  if (users.length === 0) return <div className="h-6" />; // Preserve space

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400 h-6 pl-2"
    >
      <div className="flex gap-1">
        {[0, 1, 2].map(i => (
          <motion.div
            key={i}
            animate={{ y: [0, -4, 0] }}
            transition={{ duration: 0.6, repeat: Infinity, delay: i * 0.1 }}
            className="w-1.5 h-1.5 bg-indigo-400 rounded-full"
          />
        ))}
      </div>
      <span>
        {users.length === 1 ? 'Someone is typing...' : 'Several people are typing...'}
      </span>
    </motion.div>
  );
};

// --- Pinned Messages Widget ---
export const PinnedMessages = ({ messages, onMessageClick }: any) => {
  const [isOpen, setIsOpen] = useState(false);
  const pinned = messages.filter((m: any) => m.is_pinned && !m.is_deleted);

  if (pinned.length === 0) return null;

  return (
    <div className="relative z-10 px-4 pt-2">
      <motion.div 
        layout
        onClick={() => setIsOpen(!isOpen)}
        className="bg-yellow-50/80 dark:bg-yellow-900/20 backdrop-blur-sm border border-yellow-200 dark:border-yellow-700/50 rounded-xl overflow-hidden cursor-pointer"
      >
        <div className="flex items-center justify-between p-2 px-3">
          <div className="flex items-center gap-2 text-yellow-700 dark:text-yellow-500 text-xs font-bold uppercase tracking-wider">
            <Pin size={12} />
            <span>{pinned.length} Pinned</span>
          </div>
          <span className="text-yellow-600 text-xs">{isOpen ? 'Hide' : 'Show'}</span>
        </div>

        <AnimatePresence>
          {isOpen && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="border-t border-yellow-200/50"
            >
               {pinned.map((msg: any) => (
                 <div 
                   key={msg.id}
                   onClick={(e) => { e.stopPropagation(); onMessageClick(msg.id); }}
                   className="p-3 hover:bg-yellow-100/50 dark:hover:bg-yellow-900/30 transition-colors text-sm text-gray-700 dark:text-gray-300 border-b border-yellow-100/50 last:border-0"
                 >
                    <div className="flex justify-between text-xs text-gray-400 mb-1">
                      <span>{msg.sender_id.slice(0,8)}</span>
                      <span>{new Date(msg.created_at).toLocaleDateString()}</span>
                    </div>
                    <p className="line-clamp-2">{msg.content}</p>
                 </div>
               ))}
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
};