import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { RefreshCw, Search, Users, MessageSquare } from 'lucide-react';
import { useChatStore } from '../../stores/chatStore';
import { chatApi } from '../../api/chat';

interface ChatroomListProps {
  onSelectChatroom: (chatroomId: string) => void;
  onOpenSearch?: () => void;
  activeId: string | null;
}

const ChatroomList: React.FC<ChatroomListProps> = ({ onSelectChatroom, onOpenSearch, activeId }) => {
  const { chatrooms, setChatrooms } = useChatStore();
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const loadChatrooms = async () => {
    try {
      setIsRefreshing(true);
      const rooms = await chatApi.getChatrooms();
      setChatrooms(rooms);
    } catch (err) {
      console.error('Failed to load chatrooms:', err);
    } finally {
      setLoading(false);
      setTimeout(() => setIsRefreshing(false), 500);
    }
  };

  useEffect(() => {
    loadChatrooms();
  }, []);

  return (
    <div className="h-full flex flex-col bg-white dark:bg-gray-900 md:rounded-2xl shadow-xl border border-gray-200 dark:border-gray-800 overflow-hidden">
      {/* Header */}
      <div className="p-5 border-b border-gray-100 dark:border-gray-800 flex items-center justify-between bg-white dark:bg-gray-900">
        <div>
          <h2 className="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            Messages
          </h2>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
            {chatrooms.length} active rooms
          </p>
        </div>
        <div className="flex gap-1">
          {onOpenSearch && (
            <button 
              onClick={onOpenSearch} 
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg text-gray-500 dark:text-gray-400 transition-colors"
              title="Search"
            >
              <Search size={18} />
            </button>
          )}
          <button 
            onClick={loadChatrooms}
            className={`p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg text-gray-500 dark:text-gray-400 transition-colors ${isRefreshing ? 'animate-spin' : ''}`}
            title="Refresh list"
          >
            <RefreshCw size={18} />
          </button>
        </div>
      </div>

      {/* List */}
      <div className="flex-1 overflow-y-auto custom-scrollbar p-3 space-y-1">
        {loading ? (
           [...Array(4)].map((_, i) => (
             <div key={i} className="h-20 bg-gray-100 dark:bg-gray-800 rounded-xl animate-pulse" />
           ))
        ) : (
          chatrooms.map((room) => (
            <motion.div
              key={room.id}
              initial={false}
              onClick={() => onSelectChatroom(room.id)}
              className={`group relative p-4 rounded-xl cursor-pointer transition-all duration-200 border ${
                activeId === room.id 
                  ? 'bg-indigo-50 dark:bg-indigo-900/10 border-indigo-200 dark:border-indigo-800/30' 
                  : 'bg-transparent border-transparent hover:bg-gray-50 dark:hover:bg-gray-800/50'
              }`}
            >
              <div className="flex justify-between items-start mb-1">
                <h3 className={`font-semibold text-sm ${activeId === room.id ? 'text-indigo-700 dark:text-indigo-300' : 'text-gray-900 dark:text-gray-100'}`}>
                  {room.name}
                </h3>
                {(room.unread_count ?? 0) > 0 && (
                  <span className="bg-indigo-600 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full min-w-[18px] text-center">
                    {room.unread_count}
                  </span>
                )}
              </div>
              
              <p className={`text-xs line-clamp-1 mb-2.5 ${activeId === room.id ? 'text-indigo-600/70 dark:text-indigo-400/70' : 'text-gray-500 dark:text-gray-400'}`}>
                {room.description}
              </p>
              
              <div className="flex items-center text-[10px] text-gray-400 gap-1.5">
                <div className="flex items-center gap-1 bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded">
                  <Users size={10} />
                  <span>{room.member_count}</span>
                </div>
                {activeId === room.id && <span className="text-indigo-500 font-medium ml-auto">Active</span>}
              </div>
            </motion.div>
          ))
        )}
      </div>
    </div>
  );
};

export default ChatroomList;