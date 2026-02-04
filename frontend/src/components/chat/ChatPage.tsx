import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useChatStore } from '../../stores/chatStore';
import { chatApi } from '../../api/chat';
import ChatroomList from './ChatroomList';
import ChatWindow from './ChatWindow';
import SearchModal from './SearchModal';
import { useIsMobile } from '../../hooks/useMediaQuery';

const ChatPage: React.FC = () => {
  const { setCurrentChatroom, currentChatroom } = useChatStore();
  const [selectedChatroomId, setSelectedChatroomId] = useState<string | null>(null);
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const isMobile = useIsMobile();

  // Handle browser back button or initial load state
  useEffect(() => {
    if (!currentChatroom) setSelectedChatroomId(null);
  }, [currentChatroom]);

  const handleSelectChatroom = async (chatroomId: string) => {
    try {
      // Optimistic selection for UI responsiveness
      setSelectedChatroomId(chatroomId);
      const chatroom = await chatApi.getChatroom(chatroomId);
      setCurrentChatroom(chatroom);
    } catch (err) {
      console.error('Failed to load chatroom:', err);
    }
  };

  const handleBackToList = () => {
    setSelectedChatroomId(null);
    setCurrentChatroom(null);
  };

  return (
    <div className="relative w-full h-screen overflow-hidden bg-[#f3f4f6] dark:bg-[#0f172a] pt-24">
      {' '}
      {/* Dynamic Background */}
      <div className="absolute inset-0 pointer-events-none z-0">
        <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-indigo-50/50 via-white/50 to-purple-50/50 dark:from-indigo-950/30 dark:via-gray-950/80 dark:to-purple-950/30" />
        <div className="absolute -top-[20%] -left-[10%] w-[50%] h-[50%] bg-purple-400/20 dark:bg-purple-600/10 rounded-full blur-[100px] animate-pulse" />
        <div className="absolute top-[40%] -right-[10%] w-[40%] h-[40%] bg-indigo-400/20 dark:bg-indigo-600/10 rounded-full blur-[100px]" />
      </div>
      <div className="relative z-10 w-full h-full max-w-7xl mx-auto flex md:px-6 pb-4 gap-6">
        {' '}
        {/* Sidebar - Chatroom List */}
        <AnimatePresence mode="wait">
          {(!isMobile || !selectedChatroomId) && (
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className={`w-full md:w-80 lg:w-96 h-full flex-shrink-0 ${isMobile ? 'absolute inset-0 z-20' : ''}`}
            >
              <ChatroomList
                onSelectChatroom={handleSelectChatroom}
                onOpenSearch={() => setIsSearchOpen(true)}
                activeId={selectedChatroomId}
              />
            </motion.div>
          )}
        </AnimatePresence>
        {/* Main Chat Window */}
        <AnimatePresence mode="wait">
          {selectedChatroomId ? (
            <motion.div
              key="chat-window"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ type: 'spring', stiffness: 300, damping: 30 }}
              className="flex-1 h-full relative z-10"
            >
              <ChatWindow chatroomId={selectedChatroomId} onBack={handleBackToList} />
            </motion.div>
          ) : (
            <div className="hidden md:flex flex-1 items-center justify-center h-full">
              <div className="text-center p-8 bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl">
                <div className="w-20 h-20 mx-auto mb-4 bg-gradient-to-tr from-indigo-500 to-purple-500 rounded-2xl flex items-center justify-center text-4xl shadow-lg shadow-indigo-500/20">
                  💬
                </div>
                <h2 className="text-2xl font-bold text-gray-800 dark:text-white mb-2">Ano Chat</h2>
                <p className="text-gray-500 dark:text-gray-400">
                  Select a room to start chatting anonymously.
                </p>
              </div>
            </div>
          )}
        </AnimatePresence>
      </div>
      <SearchModal isOpen={isSearchOpen} onClose={() => setIsSearchOpen(false)} />
    </div>
  );
};

export default ChatPage;
