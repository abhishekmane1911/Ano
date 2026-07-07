import { useEffect, useState } from 'react';
import { RefreshCw, Search, Users } from 'lucide-react';
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
      setTimeout(() => setIsRefreshing(false), 400);
    }
  };


  useEffect(() => {
    loadChatrooms();
  }, []);


  return (
    <div className="h-full flex flex-col bg-zinc-900 mobile:rounded-none md:rounded-lg border border-zinc-800 overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3.5 mobile:px-3 border-b border-zinc-800 flex items-center justify-between">
        <div className="min-w-0">
          <h2 className="text-sm font-semibold text-zinc-100">ChatRooms</h2>
          <p className="text-xs text-zinc-500 mt-0.5">{chatrooms.length} rooms</p>
        </div>
        <div className="flex gap-0.5 flex-shrink-0">
          {onOpenSearch && (
            <button
              onClick={onOpenSearch}
              className="p-1.5 hover:bg-zinc-800 rounded-md text-zinc-400 hover:text-zinc-300 transition-colors tap-target"
              title="Search"
            >
              <Search size={16} strokeWidth={1.75} />
            </button>
          )}
          <button
            onClick={loadChatrooms}
            className="p-1.5 hover:bg-zinc-800 rounded-md text-zinc-400 hover:text-zinc-300 transition-colors tap-target"
            title="Refresh"
          >
            <RefreshCw size={16} strokeWidth={1.75} className={isRefreshing ? 'animate-spin' : ''} />
          </button>
        </div>
      </div>


      {/* List */}
      <div className="flex-1 overflow-y-auto custom-scrollbar px-2 py-2 mobile:px-1.5">
        {loading ? (
          <div className="space-y-1 px-1">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-16 bg-zinc-800 rounded-md animate-pulse" />
            ))}
          </div>
        ) : chatrooms.length === 0 ? (
          <p className="text-sm text-zinc-500 text-center py-8">No rooms yet</p>
        ) : (
          chatrooms.map(room => {
            const active = activeId === room.id;
            return (
              <button
                key={room.id}
                onClick={() => onSelectChatroom(room.id)}
                className={`w-full text-left relative px-3 py-2.5 rounded-md transition-colors tap-target border-l-2 ${active
                  ? 'border-l-blue-500 bg-zinc-800/60'
                  : 'border-l-transparent hover:bg-zinc-800/40'
                  }`}
              >
                <div className="flex justify-between items-start gap-2 mb-0.5 w-full">
                  <h3
                    className={`font-medium text-sm truncate text-left flex-1 ${active ? 'text-zinc-50' : 'text-zinc-300'
                      }`}
                  >
                    {room.name}
                  </h3>
                  {(room.unread_count ?? 0) > 0 && (
                    <span className="bg-blue-600 text-white text-[10px] font-semibold px-1.5 py-0.5 rounded-full min-w-[18px] text-center flex-shrink-0 leading-none">
                      {room.unread_count}
                    </span>
                  )}
                </div>
              </button>
            );
          })
        )}
      </div>
    </div>
  );
};


export default ChatroomList;