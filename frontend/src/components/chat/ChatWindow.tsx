import { useEffect, useRef, useState, useCallback } from 'react';
import { ArrowLeft, MoreVertical } from 'lucide-react';
import { useChatStore } from '../../stores/chatStore';
import { useProfileStore } from '../../stores/profileStore';
import { useReputationStore } from '../../stores/reputationStore';
import { useToastStore } from '../../hooks/useToast';
import { chatApi } from '../../api/chat';
import { reputationApi } from '../../api/reputation';
import { profileAPI } from '../../api/profile';
import { chatWebSocket } from '../../services/websocket';
import MessageBubble from './MessageBubble';
import MessageInput from './MessageInput';
import { TypingIndicator, PinnedMessages } from './ChatComponents';
import MediaViewer from './MediaViewer';
import { ReportModal, BlockConfirmation } from '../safety';
import { RankUpAnimation } from '../reputation/ReputationComponents';

interface ChatWindowProps {
  chatroomId: string;
  onBack?: () => void;
}

const ChatWindow: React.FC<ChatWindowProps> = ({ chatroomId, onBack }) => {
  const { messages, setMessages, prependMessages, updateMessage, currentChatroom, isConnected, resetUnreadCount } =
    useChatStore();

  const { profile, setProfile } = useProfileStore();
  const { myReputation, rankUpEvent, clearRankUpEvent, setMyReputation } = useReputationStore();

  const [loadingMore, setLoadingMore] = useState(false);
  const [hasMoreMessages, setHasMoreMessages] = useState(true);
  const [mediaViewer, setMediaViewer] = useState<{ url: string; type: 'image' | 'video' } | null>(null);
  const [showReportModal, setShowReportModal] = useState(false);
  const [showBlockModal, setShowBlockModal] = useState(false);
  const [selectedUserId, setSelectedUserId] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const prevHeightRef = useRef<number>(0);

  useEffect(() => {
    const initProfile = async () => {
      if (!profile) {
        try {
          const p = await profileAPI.getMyProfile();
          setProfile(p);
        } catch (error) {
          console.error('Failed to load profile for chat alignment', error);
        }
      }
    };
    initProfile();
  }, [profile, setProfile]);

  useEffect(() => {
    if (!myReputation) {
      reputationApi.getMyReputation().then(setMyReputation).catch(() => { });
    }
  }, [myReputation, setMyReputation]);

  useEffect(() => {
    setHasMoreMessages(true);
    loadMessages(1, true);
    resetUnreadCount(chatroomId);
    chatWebSocket.connect(chatroomId);
    return () => chatWebSocket.disconnect();
  }, [chatroomId]);

  useEffect(() => {
    if (containerRef.current) {
      const { scrollHeight, scrollTop, clientHeight } = containerRef.current;
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
        setMessages(chatroomId, res.results.reverse());
        setTimeout(scrollToBottom, 100);
      } else {
        prependMessages(chatroomId, res.results.reverse());
        if (containerRef.current) {
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

  const handleVote = async (messageId: string, voteType: 'upvote' | 'downvote') => {
    try {
      const result = await reputationApi.vote(messageId, voteType);
      if (result.success && result.ranking_data) {
        useChatStore.getState().updateVote(
          chatroomId,
          messageId,
          result.ranking_data.upvotes,
          result.ranking_data.downvotes,
          result.vote_type ?? null
        );
      } else if (!result.success) {
        useToastStore.getState().addToast(
          result.error || 'You need Sophomore tier to vote. Earn more reputation!',
          'warning'
        );
      }
    } catch (error) {
      console.error('Failed to vote:', error);
    }
  };

  return (
    <div className="flex flex-col h-full bg-white dark:bg-slate-900 mobile:rounded-none md:rounded-lg border border-slate-200 dark:border-slate-800 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 mobile:px-3 py-3.5 border-b border-slate-100 dark:border-slate-800">
        <div className="flex items-center gap-3 min-w-0 flex-1">
          {onBack && (
            <button
              onClick={onBack}
              className="md:hidden p-1.5 -ml-1.5 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-md transition-colors tap-target"
            >
              <ArrowLeft size={18} strokeWidth={1.75} />
            </button>
          )}
          <div className="min-w-0">
            <h2 className="font-semibold text-sm text-slate-900 dark:text-slate-100 truncate">
              {currentChatroom?.name}
            </h2>
            <p className="text-xs text-slate-400 dark:text-slate-500 truncate">
              {currentChatroom?.description || 'Welcome to the chat room'}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 flex-shrink-0">
          <div className="flex items-center gap-1.5 text-xs">
            <span className={`w-1.5 h-1.5 rounded-full ${isConnected ? 'bg-emerald-500' : 'bg-slate-300 dark:bg-slate-600'}`} />
            <span className="text-slate-400 dark:text-slate-500">
              {isConnected ? 'Online' : 'Reconnecting…'}
            </span>
          </div>
          <button className="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-md text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors tap-target">
            <MoreVertical size={18} strokeWidth={1.75} />
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
        className="flex-1 overflow-y-auto p-4 mobile:p-3 space-y-1 bg-slate-50 dark:bg-slate-950/40 scroll-smooth custom-scrollbar"
      >
        {loadingMore && (
          <div className="flex justify-center py-3">
            <div className="w-4 h-4 border-2 border-slate-300 border-t-slate-500 rounded-full animate-spin" />
          </div>
        )}

        {chatroomMessages.map((msg, i) => {
          const isOwn = !!profile && msg.sender_id === profile.anonymous_id;
          const showAvatar = !isOwn && (i === 0 || chatroomMessages[i - 1].sender_id !== msg.sender_id);

          return (
            <div
              key={msg.id}
              id={`msg-${msg.id}`}
              className={`flex ${isOwn ? 'justify-end' : 'justify-start'} ${!showAvatar && !isOwn ? 'ml-9 mobile:ml-8' : ''} mb-1`}
            >
              <MessageBubble
                message={msg}
                isOwnMessage={isOwn}
                showAvatar={showAvatar}
                onEdit={(id, content) => chatWebSocket.editMessage(id, content)}
                onDelete={id => chatWebSocket.deleteMessage(id)}
                onReact={(id, emoji) => chatWebSocket.reactToMessage(id, emoji)}
                onPin={handlePinMessage}
                onVote={handleVote}
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
      <div className="p-3 mobile:p-2 md:p-3 bg-white dark:bg-slate-900 border-t border-slate-100 dark:border-slate-800 safe-area-inset-bottom">
        <TypingIndicator chatroomId={chatroomId} />
        <MessageInput
          onSendMessage={async (content, file) => {
            if (file) {
              try {
                const { media_url } = await chatApi.uploadMedia(chatroomId, file);
                await chatApi.sendMessage(chatroomId, content, 'image', media_url);
              } catch (error: any) {
                console.error('Failed to upload file:', error);
                const errorMessage = error.response?.data?.error || 'Failed to upload image. Please try again.';
                useToastStore.getState().addToast(errorMessage, 'error');
              }
            } else {
              chatWebSocket.sendMessage(content);
            }
          }}
          onTypingStart={() => chatWebSocket.startTyping()}
          onTypingStop={() => chatWebSocket.stopTyping()}
          disabled={!isConnected}
          canUploadImages={myReputation?.rank_tier === 'Senior' || myReputation?.rank_tier === 'Campus Legend'}
        />
      </div>

      {/* Modals */}
      {mediaViewer && (
        <MediaViewer mediaUrl={mediaViewer.url} mediaType={mediaViewer.type} onClose={() => setMediaViewer(null)} />
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
      <RankUpAnimation
        isVisible={!!rankUpEvent}
        newTier={rankUpEvent?.newTier ?? 'Fresher'}
        newLevel={rankUpEvent?.newLevel ?? 1}
        onComplete={clearRankUpEvent}
      />
    </div>
  );
};

export default ChatWindow;