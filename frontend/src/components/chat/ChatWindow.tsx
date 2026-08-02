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
  const [pinModalMessageId, setPinModalMessageId] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const prevHeightRef = useRef<number>(0);
  const initialScrollDone = useRef<boolean>(false);
  const scrollCooldownRef = useRef<boolean>(false);

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

  const [sortMode, setSortMode] = useState<'live' | 'top'>('live');

  useEffect(() => {
    resetUnreadCount(chatroomId);
    chatWebSocket.connect(chatroomId);
    return () => chatWebSocket.disconnect();
  }, [chatroomId]);

  useEffect(() => {
    initialScrollDone.current = false;
    setHasMoreMessages(true);
    loadMessages(1, true, sortMode);
  }, [chatroomId, sortMode]);

  useEffect(() => {
    if (containerRef.current && sortMode === 'live') {
      const { scrollHeight, scrollTop, clientHeight } = containerRef.current;
      const isNearBottom = scrollHeight - scrollTop - clientHeight < 200;
      if (isNearBottom) scrollToBottom();
    }
  }, [messages[chatroomId], sortMode]);

  const loadMessages = async (page: number, isInitial = false, currentSortMode: 'live' | 'top') => {
    try {
      setLoadingMore(true);
      const ordering = currentSortMode === 'top' ? 'wilson_score' : 'created_at';
      const res = await chatApi.getChatroomMessages(chatroomId, page, 50, ordering);
      setHasMoreMessages(res.next !== null);

      const messagesToSet = currentSortMode === 'live' ? res.results.reverse() : res.results;

      if (isInitial) {
        setMessages(chatroomId, messagesToSet);
        if (currentSortMode === 'live') {
          setTimeout(() => {
            scrollToBottom(false);
            initialScrollDone.current = true;
          }, 100);
        } else {
          setTimeout(() => {
            if (containerRef.current) containerRef.current.scrollTop = 0;
            initialScrollDone.current = true;
          }, 100);
        }
      } else {
        if (currentSortMode === 'live') {
          // Capture height BEFORE prepend so the DOM hasn't changed yet
          const heightBefore = containerRef.current?.scrollHeight ?? 0;
          prependMessages(chatroomId, messagesToSet);
          // Restore position after the DOM has updated
          requestAnimationFrame(() => {
            if (containerRef.current) {
              containerRef.current.scrollTop = containerRef.current.scrollHeight - heightBefore;
            }
          });
        } else {
          const existing = useChatStore.getState().messages[chatroomId] || [];
          setMessages(chatroomId, [...existing, ...messagesToSet]);
        }
      }
    } catch (err) {
      console.error(err);
      setHasMoreMessages(false);
    } finally {
      setLoadingMore(false);
      // Block scroll handler briefly so the position restore doesn't retrigger a load
      scrollCooldownRef.current = true;
      setTimeout(() => { scrollCooldownRef.current = false; }, 300);
    }
  };

  const handleScroll = useCallback(() => {
    if (!initialScrollDone.current || scrollCooldownRef.current || !containerRef.current || loadingMore || !hasMoreMessages) return;
    
    if (sortMode === 'live') {
      if (containerRef.current.scrollTop < 100) {
        prevHeightRef.current = containerRef.current.scrollHeight;
        const currentCount = messages[chatroomId]?.length || 0;
        loadMessages(Math.ceil(currentCount / 50) + 1, false, sortMode);
      }
    } else {
      const { scrollHeight, scrollTop, clientHeight } = containerRef.current;
      if (scrollHeight - scrollTop - clientHeight < 100) {
        const currentCount = messages[chatroomId]?.length || 0;
        loadMessages(Math.ceil(currentCount / 50) + 1, false, sortMode);
      }
    }
  }, [loadingMore, hasMoreMessages, chatroomId, messages, sortMode]);

  const scrollToBottom = (smooth = true) => messagesEndRef.current?.scrollIntoView({ behavior: smooth ? 'smooth' : 'auto' });
  const chatroomMessages = messages[chatroomId] || [];

  const handlePinMessage = async (messageId: string, isPinned: boolean) => {
    if (isPinned) {
      try {
        const updatedMessage = await chatApi.pinMessage(messageId);
        updateMessage(chatroomId, updatedMessage);
      } catch (error) {
        console.error('Failed to unpin message:', error);
      }
    } else {
      setPinModalMessageId(messageId);
    }
  };

  const submitPin = async (durationHours: number) => {
    if (!pinModalMessageId) return;
    try {
      const updatedMessage = await chatApi.pinMessage(pinModalMessageId, durationHours);
      updateMessage(chatroomId, updatedMessage);
      setPinModalMessageId(null);
    } catch (error) {
      console.error('Failed to pin message:', error);
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
    } catch (error: any) {
      const errorMsg = error.response?.data?.error;

      if (errorMsg) {
        useToastStore.getState().addToast(
          errorMsg,
          'warning'
        );
      } else if (error === '403' || error.response?.status === 403) {
        useToastStore.getState().addToast(
          'You need Sophomore tier to vote. Earn more reputation!',
          'warning'
        );
      } else {
        useToastStore.getState().addToast(
          'Failed to vote. Please try again later.',
          'error'
        );
        // console.error('Failed to vote:', error);
      }
    }
  };

  return (
    <div className="flex flex-col h-full bg-zinc-900 mobile:rounded-none md:rounded-lg border border-zinc-800 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 mobile:px-3 py-3.5 border-b border-zinc-800">
        <div className="flex items-center gap-3 min-w-0 flex-1">
          {onBack && (
            <button
              onClick={onBack}
              className="md:hidden p-1.5 -ml-1.5 text-zinc-500 hover:bg-zinc-800 rounded-md transition-colors tap-target"
            >
              <ArrowLeft size={18} strokeWidth={1.75} />
            </button>
          )}
          <div className="min-w-0 flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4">
            <div>
              <h2 className="font-semibold text-sm text-zinc-100 truncate">
                {currentChatroom?.name}
              </h2>
              <p className="text-xs text-zinc-500 truncate hidden sm:block">
                {currentChatroom?.description || 'Welcome to the chat room'}
              </p>
            </div>
            
            <div className="flex items-center bg-zinc-950 border border-zinc-800 rounded-lg p-0.5">
              <button
                onClick={() => setSortMode('live')}
                className={`px-3 py-1 text-[11px] font-medium rounded-md transition-colors ${sortMode === 'live' ? 'bg-zinc-800 text-zinc-100' : 'text-zinc-500 hover:text-zinc-300'}`}
              >
                Live
              </button>
              <button
                onClick={() => setSortMode('top')}
                className={`px-3 py-1 text-[11px] font-medium rounded-md transition-colors flex items-center gap-1 ${sortMode === 'top' ? 'bg-zinc-800 text-zinc-100' : 'text-zinc-500 hover:text-zinc-300'}`}
              >
                Top <span className="text-[10px] text-amber-500">★</span>
              </button>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3 flex-shrink-0">
          <div className="flex items-center gap-1.5 text-xs">
            <span className={`w-1.5 h-1.5 rounded-full ${isConnected ? 'bg-emerald-500' : 'bg-zinc-600'}`} />
            <span className="text-zinc-500">
              {isConnected ? 'Online' : 'Reconnecting…'}
            </span>
          </div>
          <button className="p-1.5 hover:bg-zinc-800 rounded-md text-zinc-400 hover:text-zinc-300 transition-colors tap-target">
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
        className="flex-1 overflow-y-auto p-4 mobile:p-3 space-y-1 bg-zinc-950/40 scroll-smooth custom-scrollbar"
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
      <div className="p-3 mobile:p-2 md:p-3 bg-zinc-900 border-t border-zinc-800 safe-area-inset-bottom">
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
      {/* Pin Duration Modal */}
      {pinModalMessageId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl max-w-sm w-full p-5 space-y-4">
            <h3 className="text-lg font-medium text-zinc-100">Pin Duration</h3>
            <p className="text-sm text-zinc-400">
              How long should this message be pinned in the chat?
            </p>
            <div className="flex flex-col gap-2">
              <button onClick={() => submitPin(1)} className="p-3 text-left bg-zinc-950 hover:bg-zinc-800 rounded-lg text-sm font-medium transition-colors">
                1 Hour
              </button>
              <button onClick={() => submitPin(24)} className="p-3 text-left bg-zinc-950 hover:bg-zinc-800 rounded-lg text-sm font-medium transition-colors">
                1 Day
              </button>
              <button onClick={() => submitPin(168)} className="p-3 text-left bg-zinc-950 hover:bg-zinc-800 rounded-lg text-sm font-medium transition-colors">
                1 Week
              </button>
              <button onClick={() => submitPin(720)} className="p-3 text-left bg-zinc-950 hover:bg-zinc-800 rounded-lg text-sm font-medium transition-colors">
                1 Month
              </button>
            </div>
            <button
              onClick={() => setPinModalMessageId(null)}
              className="w-full p-2.5 mt-2 bg-zinc-800 hover:bg-zinc-700 rounded-lg text-sm font-medium transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatWindow;