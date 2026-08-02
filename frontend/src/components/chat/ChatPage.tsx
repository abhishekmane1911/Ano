import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageSquare } from 'lucide-react';
import { useChatStore } from '../../stores/chatStore';
import { chatApi } from '../../api/chat';
import ChatroomList from './ChatroomList';
import ChatWindow from './ChatWindow';
import SearchModal from './SearchModal';
import { useIsMobile } from '../../hooks/useMediaQuery';

const ChatPage: React.FC = () => {
  const { setCurrentChatroom } = useChatStore();
  const [selectedChatroomId, setSelectedChatroomId] = useState<string | null>(null);
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const isMobile = useIsMobile();

  const { roomId } = useParams<{ roomId?: string }>();
  const navigate = useNavigate();

  useEffect(() => {
    if (roomId && roomId !== selectedChatroomId) {
      handleSelectChatroom(roomId, false);
    } else if (!roomId && selectedChatroomId) {
      setSelectedChatroomId(null);
      setCurrentChatroom(null);
    }
  }, [roomId]);

  const handleSelectChatroom = async (chatroomId: string, updateUrl = true) => {
    try {
      setSelectedChatroomId(chatroomId);
      if (updateUrl) navigate(`/chat/${chatroomId}`);
      const chatroom = await chatApi.getChatroom(chatroomId);
      setCurrentChatroom(chatroom);
    } catch (err) {
      console.error('Failed to load chatroom:', err);
    }
  };

  const handleBackToList = () => navigate('/chat');

  return (
    <div className="w-full h-screen bg-zinc-950 pt-24 mobile:pt-24">
      <div className="w-full h-full max-w-6xl mx-auto flex mobile:flex-col md:px-6 pb-4 mobile:pb-0 gap-4 mobile:gap-0">
        <AnimatePresence mode="wait">
          {(!isMobile || !selectedChatroomId) && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.15 }}
              className={`w-full md:w-72 lg:w-80 h-full flex-shrink-0 ${isMobile ? 'absolute inset-0 z-20 mobile:relative mobile:h-full' : ''
                }`}
            >
              <ChatroomList
                onSelectChatroom={handleSelectChatroom}
                onOpenSearch={() => setIsSearchOpen(true)}
                activeId={selectedChatroomId}
              />
            </motion.div>
          )}
        </AnimatePresence>

        {selectedChatroomId ? (
          <motion.div
            key={selectedChatroomId}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.12 }}
            className={`flex-1 h-full ${isMobile ? 'absolute inset-0 mobile:relative' : ''}`}
          >
            <ChatWindow chatroomId={selectedChatroomId} onBack={handleBackToList} />
          </motion.div>
        ) : (
          <div className="hidden md:flex flex-1 items-center justify-center h-full">
            <div className="text-center max-w-xs">
              <div className="w-10 h-10 mx-auto mb-4 rounded-lg border border-zinc-800 flex items-center justify-center text-zinc-500">
                <MessageSquare size={18} strokeWidth={1.75} />
              </div>
              <h2 className="text-base font-medium text-zinc-100 mb-1">
                No room selected
              </h2>
              <p className="text-sm text-zinc-400">
                Choose a room from the list to start chatting.
              </p>
            </div>
          </div>
        )}
      </div>
      <SearchModal isOpen={isSearchOpen} onClose={() => setIsSearchOpen(false)} />
    </div>
  );
};

export default ChatPage;