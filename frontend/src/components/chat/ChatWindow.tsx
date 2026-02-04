import { useEffect, useRef, useState, useCallback } from 'react';
import { ArrowLeft, MoreVertical, Wifi, WifiOff } from 'lucide-react';
import { useChatStore } from '../../stores/chatStore';
import { useProfileStore } from '../../stores/profileStore';
import { chatApi } from '../../api/chat';
import { profileAPI } from '../../api/profile'; // Import profileAPI
import { chatWebSocket } from '../../services/websocket';
import MessageBubble from './MessageBubble';
import MessageInput from './MessageInput';
import { TypingIndicator, PinnedMessages } from './ChatComponents';
import MediaViewer from './MediaViewer';
import { ReportModal, BlockConfirmation } from '../safety';

interface ChatWindowProps {
  chatroomId: string;
  onBack?: () => void;
}

const ChatWindow: React.FC<ChatWindowProps> = ({ chatroomId, onBack }) => {
  const { messages, setMessages, prependMessages, updateMessage, currentChatroom, isConnected, resetUnreadCount } =
    useChatStore();
  
  // Get setProfile to ensure we can fetch it if missing
  const { profile, setProfile } = useProfileStore();

  const [loadingMore, setLoadingMore] = useState(false);
  const [hasMoreMessages, setHasMoreMessages] = useState(true);
  const [mediaViewer, setMediaViewer] = useState<{ url: string; type: 'image' | 'video' } | null>(null);
  const [showReportModal, setShowReportModal] = useState(false);
  const [showBlockModal, setShowBlockModal] = useState(false);
  const [selectedUserId, setSelectedUserId] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const prevHeightRef = useRef<number>(0);

  // 1. CRITICAL: Ensure Profile is Loaded (Fixes alignment on refresh)
  useEffect(() => {
    const initProfile = async () => {
      if (!profile) {
        try {
          const p = await profileAPI.getMyProfile();
          setProfile(p);
        } catch (error) {
          console.error("Failed to load profile for chat alignment", error);
        }
      }
    };
    initProfile();
  }, [profile, setProfile]);

  // 2. Initialize Chat Room
  useEffect(() => {
    setHasMoreMessages(true);
    loadMessages(1, true);
    resetUnreadCount(chatroomId);
    chatWebSocket.connect(chatroomId);
    return () => chatWebSocket.disconnect();
  }, [chatroomId]);

  // 3. Auto-scroll logic (Smart)
  useEffect(() => {
    if (containerRef.current) {
      const { scrollHeight, scrollTop, clientHeight } = containerRef.current;
      // Only auto-scroll if user is already near the bottom
      const isNearBottom = scrollHeight - scrollTop - clientHeight < 200;
      if (isNearBottom) scrollToBottom();
    }
  }, [messages[chatroomId]]);

  const loadMessages = async (page: number, isInitial = false) => {
    try {
      setLoadingMore(true);
      const res = await chatApi.getChatroomMessages(chatroomId, page);
      setHasMoreMessages(res.next !== null);

      if (isInitial) {
        setMessages(chatroomId, res.results);
        setTimeout(scrollToBottom, 100);
      } else {
        prependMessages(chatroomId, res.results);
        if (containerRef.current) {
          // Maintain scroll position after loading older messages
          containerRef.current.scrollTop = containerRef.current.scrollHeight - prevHeightRef.current;
        }
      }
    } catch (err) {
      console.error(err);
      setHasMoreMessages(false);
    } finally {
      setLoadingMore(false);
    }
  };

  const handleScroll = useCallback(() => {
    if (!containerRef.current || loadingMore || !hasMoreMessages) return;
    if (containerRef.current.scrollTop < 100) {
      prevHeightRef.current = containerRef.current.scrollHeight;
      const currentCount = messages[chatroomId]?.length || 0;
      loadMessages(Math.ceil(currentCount / 50) + 1);
    }
  }, [loadingMore, hasMoreMessages, chatroomId, messages]);

  const scrollToBottom = () => messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  const chatroomMessages = messages[chatroomId] || [];

  const handlePinMessage = async (messageId: string) => {
    try {
      const updatedMessage = await chatApi.pinMessage(messageId);
      updateMessage(chatroomId, updatedMessage);
    } catch (error) {
      console.error('Failed to pin/unpin message:', error);
    }
  };

  return (
    // Clean, professional container (No excessive glass effects)
    <div className="flex flex-col h-full bg-white dark:bg-gray-900 md:rounded-2xl shadow-xl border border-gray-200 dark:border-gray-800 overflow-hidden">
      
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 bg-white/95 dark:bg-gray-900/95 backdrop-blur-sm border-b border-gray-100 dark:border-gray-800 z-20">
        <div className="flex items-center gap-4">
          {onBack && (
            <button
              onClick={onBack}
              className="md:hidden p-2 -ml-2 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition-colors"
            >
              <ArrowLeft size={20} />
            </button>
          )}
          <div>
            <h2 className="font-bold text-gray-900 dark:text-white flex items-center gap-2 text-lg">
              {currentChatroom?.name}
              {!isConnected && <WifiOff size={16} className="text-red-500" />}
            </h2>
            <p className="text-xs text-gray-500 dark:text-gray-400 truncate max-w-[200px] md:max-w-md">
              {currentChatroom?.description || "Welcome to the chat room"}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {isConnected ? (
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-100 dark:border-emerald-800/50">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"/>
              <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-600 dark:text-emerald-400">Live</span>
            </div>
          ) : (
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-red-50 dark:bg-red-900/20 border border-red-100 dark:border-red-800/50">
              <span className="text-[11px] font-bold uppercase tracking-wider text-red-600 dark:text-red-400">Offline</span>
            </div>
          )}
          <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors">
            <MoreVertical size={20} />
          </button>
        </div>
      </div>

      <PinnedMessages
        messages={chatroomMessages}
        onMessageClick={(id: string) =>
          document.getElementById(`msg-${id}`)?.scrollIntoView({ behavior: 'smooth', block: 'center' })
        }
      />

      {/* Messages Area */}
      <div
        ref={containerRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto p-4 space-y-1 bg-[#f0f2f5] dark:bg-[#0b101a] scroll-smooth custom-scrollbar"
      >
        {loadingMore && (
          <div className="flex justify-center py-4">
            <div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
          </div>
        )}

        {chatroomMessages.map((msg, i) => {
          // Robust ID check
          const isOwn = !!profile && msg.sender_id === profile.anonymous_id;
          const showAvatar = !isOwn && (i === 0 || chatroomMessages[i - 1].sender_id !== msg.sender_id);

          return (
            <div
              key={msg.id}
              id={`msg-${msg.id}`}
              className={`flex ${isOwn ? 'justify-end' : 'justify-start'} ${!showAvatar && !isOwn ? 'ml-9' : ''} mb-1`}
            >
              <MessageBubble
                message={msg}
                isOwnMessage={isOwn}
                showAvatar={showAvatar}
                onEdit={(id, content) => chatWebSocket.editMessage(id, content)}
                onDelete={id => chatWebSocket.deleteMessage(id)}
                onReact={(id, emoji) => chatWebSocket.reactToMessage(id, emoji)}
                onPin={handlePinMessage}
                onReport={() => {
                  setSelectedUserId(msg.sender_id);
                  setShowReportModal(true);
                }}
                onBlock={() => {
                  setSelectedUserId(msg.sender_id);
                  setShowBlockModal(true);
                }}
                onMediaClick={(url, type) => setMediaViewer({ url, type })}
              />
            </div>
          );
        })}
        <div ref={messagesEndRef} />
      </div>

      {/* Footer / Input */}
      <div className="p-3 md:p-4 bg-white dark:bg-gray-900 border-t border-gray-100 dark:border-gray-800 z-20">
        <TypingIndicator chatroomId={chatroomId} />
        <MessageInput
          onSendMessage={async (content, file) => {
            if (file) {
              try {
                const { media_url } = await chatApi.uploadMedia(chatroomId, file);
                await chatApi.sendMessage(chatroomId, content, 'image', media_url);
              } catch (error) {
                console.error('Failed to upload file:', error);
                alert('Failed to upload file.');
              }
            } else {
              chatWebSocket.sendMessage(content);
            }
          }}
          onTypingStart={() => chatWebSocket.startTyping()}
          onTypingStop={() => chatWebSocket.stopTyping()}
          disabled={!isConnected}
        />
      </div>

      {/* Modals */}
      {mediaViewer && (
        <MediaViewer
          mediaUrl={mediaViewer.url}
          mediaType={mediaViewer.type}
          onClose={() => setMediaViewer(null)}
        />
      )}
      {showReportModal && selectedUserId && (
        <ReportModal
          reportedUserId={selectedUserId}
          reportedUserName="Anonymous User"
          onClose={() => setShowReportModal(false)}
          onSuccess={() => setShowReportModal(false)}
        />
      )}
      {showBlockModal && selectedUserId && (
        <BlockConfirmation
          blockedUserId={selectedUserId}
          blockedUserName="Anonymous User"
          onClose={() => setShowBlockModal(false)}
          onSuccess={() => setShowBlockModal(false)}
        />
      )}
    </div>
  );
};

export default ChatWindow;