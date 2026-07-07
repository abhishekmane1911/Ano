import { useEffect, useRef, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Shield, CheckCheck } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useMatchmakingStore } from '../../stores/matchmakingStore';
import { useProfileStore } from '../../stores/profileStore';
import { useAuthStore } from '../../stores/authStore';
import { matchmakingAPI } from '../../api/matchmaking';
import { profileAPI } from '../../api/profile';
import MessageInput from '../chat/MessageInput';
import MediaViewer from '../chat/MediaViewer';
import { ReportModal, BlockConfirmation } from '../safety';

const MatchChat: React.FC = () => {
  const { matchId } = useParams<{ matchId: string }>();
  const navigate = useNavigate();
  const {
    matchMessages,
    currentMatch,
    setCurrentMatch,
    setMatchMessages,
    prependMatchMessages,
    addMatchMessage,
    isConnected,
    typingUsers,
  } = useMatchmakingStore();
  
  const { profile, setProfile } = useProfileStore();

  const [loadingMessages, setLoadingMessages] = useState(true);
  const [loadingProfile, setLoadingProfile] = useState(false);
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [showReportModal, setShowReportModal] = useState(false);
  const [showBlockModal, setShowBlockModal] = useState(false);
  const [mediaViewer, setMediaViewer] = useState<{ url: string; type: 'image' | 'video' } | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // 1. Ensure Profile is Loaded (Critical for ID comparison)
  useEffect(() => {
    const initProfile = async () => {
      if (!profile) {
        setLoadingProfile(true);
        try {
          const p = await profileAPI.getMyProfile();
          setProfile(p);
        } catch (error) {
          console.error("Failed to load profile for chat alignment", error);
        } finally {
          setLoadingProfile(false);
        }
      }
    };
    initProfile();
  }, [profile, setProfile]);

  // 2. Load Chat Data
  useEffect(() => {
    if (!matchId) return;
    loadMatchDetails();
    loadMessages(1, true);
    connectWebSocket();
    return () => disconnectWebSocket();
  }, [matchId]);

  const loadMatchDetails = async () => {
    if (!matchId) return;
    try {
      const match = await matchmakingAPI.getMatchDetail(matchId);
      setCurrentMatch(match);
    } catch (err) { console.error(err); }
  };

  const loadMessages = async (page: number, isInitial = false) => {
    if (!matchId) return;
    try {
      if (isInitial) setLoadingMessages(true);
      const res = await matchmakingAPI.getMatchMessages(matchId, page);
      if (isInitial) {
        setMatchMessages(matchId, res.results);
        scrollToBottom();
      } else {
        prependMatchMessages(matchId, res.results);
      }
    } catch (err) { console.error(err); } 
    finally { if (isInitial) setLoadingMessages(false); }
  };

  const scrollToBottom = (smooth = false) => {
    setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: smooth ? 'smooth' : 'auto' });
    }, 100);
  };

  const connectWebSocket = () => {
    if (!matchId) return;
    const token = useAuthStore.getState().accessToken;
    const url = `${import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000/ws'}/match/${matchId}/?token=${token}`;
    const socket = new WebSocket(url);
    
    socket.onopen = () => useMatchmakingStore.getState().setConnected(true);
    socket.onmessage = (e) => {
        const data = JSON.parse(e.data);
        if (data.type === 'message.receive') {
          // Add message to store
          addMatchMessage(matchId, data.message);
          scrollToBottom(true);
        } else if (data.type === 'typing.start') {
          useMatchmakingStore.getState().addTypingUser(matchId, data.profile_id);
        } else if (data.type === 'typing.stop') {
          useMatchmakingStore.getState().removeTypingUser(matchId, data.profile_id);
        }
    };
    socket.onclose = () => {
        useMatchmakingStore.getState().setConnected(false);
    };
    setWs(socket);
  };

  const disconnectWebSocket = () => {
     ws?.close();
     setWs(null);
     useMatchmakingStore.getState().setConnected(false);
  };

  const handleSendMessage = async (content: string, file?: File) => {
    if (!matchId) return;
    
    if (file) {
      try {
        const { media_url } = await matchmakingAPI.uploadMatchMedia(matchId, file);
        await matchmakingAPI.sendMatchMessage(matchId, content, 'image', media_url);
      } catch (error) {
        alert('Failed to upload file.');
      }
    } else {
      if (ws?.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'message.send', content }));
      }
    }
  };

  const handleTypingStart = () => ws?.readyState === WebSocket.OPEN && ws.send(JSON.stringify({ type: 'typing.start' }));
  const handleTypingStop = () => ws?.readyState === WebSocket.OPEN && ws.send(JSON.stringify({ type: 'typing.stop' }));

  const messages = matchMessages[matchId || ''] || [];
  const isTyping = (typingUsers[matchId || ''] || []).some(u => u.profile_id !== profile?.anonymous_id);

  // Loading state covering both Messages AND Profile
  if ((!profile && loadingProfile) || loadingMessages) {
    return (
      <div className="w-full h-screen bg-[#f3f4f6] dark:bg-[#0f172a] pt-24 flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="relative w-full h-screen overflow-hidden bg-[#f3f4f6] dark:bg-[#0f172a] pt-24">
      <div className="absolute inset-0 pointer-events-none opacity-40 dark:opacity-20 bg-[radial-gradient(#cbd5e1_1px,transparent_1px)] [background-size:20px_20px]" />

      <div className="relative z-10 w-full h-full max-w-4xl mx-auto flex flex-col px-0 md:px-4 pb-0 md:pb-4">
        <div className="flex flex-col h-full bg-white dark:bg-gray-900 md:rounded-2xl shadow-2xl overflow-hidden border border-gray-200 dark:border-gray-800">
          
          {/* HEADER */}
          <div className="flex-none px-4 py-3 bg-white/90 dark:bg-gray-900/90 backdrop-blur-md border-b border-gray-100 dark:border-gray-800 z-20 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <button 
                onClick={() => navigate('/matchmaking')}
                className="p-2 -ml-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-600 dark:text-gray-300 transition-colors"
              >
                <ArrowLeft size={22} />
              </button>
              
              <div className="flex items-center gap-3">
                <div className="relative">
                  <div className="w-10 h-10 rounded-full bg-gray-200 dark:bg-gray-700 overflow-hidden">
                    {currentMatch?.other_profile.avatar ? (
                      <img src={currentMatch.other_profile.avatar} className="w-full h-full object-cover" alt="User" />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-gray-400">
                        <span className="text-xl">👤</span>
                      </div>
                    )}
                  </div>
                  {isConnected && (
                    <span className="absolute bottom-0 right-0 w-3 h-3 bg-green-500 border-2 border-white dark:border-gray-900 rounded-full"></span>
                  )}
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 dark:text-white text-sm leading-tight">
                    Anonymous User
                  </h3>
                  <p className="text-xs text-green-600 dark:text-green-400 font-medium">
                    {isConnected ? 'Online' : 'Offline'}
                  </p>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-1">
              <button 
                onClick={() => setShowReportModal(true)}
                className="p-2 rounded-full hover:bg-red-50 dark:hover:bg-red-900/20 text-gray-400 hover:text-red-500 transition-colors"
              >
                <Shield size={20} />
              </button>
            </div>
          </div>

          {/* MESSAGES LIST */}
          <div 
            ref={containerRef}
            className="flex-1 overflow-y-auto p-4 space-y-1 bg-[#f0f2f5] dark:bg-[#0b101a] scroll-smooth"
          >
            {messages.map((msg, index) => {
              // --- FIXED ALIGNMENT LOGIC ---
              const myId = String(profile?.anonymous_id || '');
              const senderId = String(msg.sender_anonymous_id || msg.sender || '');
              
              let isOwn;
              
              // 1. PRIMARY CHECK: Compare IDs. This is the source of truth.
              if (myId && senderId) {
                isOwn = myId === senderId;
              } 
              // 2. FALLBACK: Use flag ONLY if IDs are missing (shouldn't happen)
              else {
                isOwn = msg.is_own_message ?? false;
              }

              // Grouping logic 
              const prevSender = index > 0 
                ? (messages[index-1].sender_anonymous_id || messages[index-1].sender) 
                : 'start';
              const currSender = msg.sender_anonymous_id || msg.sender;
              const isSequence = index > 0 && String(prevSender) === String(currSender);

              return (
                <motion.div 
                  key={msg.id || index}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`flex w-full ${isOwn ? 'justify-end' : 'justify-start'} ${isSequence ? 'mt-1' : 'mt-4'}`}
                >
                  <div className={`max-w-[75%] md:max-w-[60%] flex flex-col ${isOwn ? 'items-end' : 'items-start'}`}>
                    
                    <div 
                      className={`relative px-4 py-2 text-[15px] leading-relaxed shadow-sm
                        ${isOwn 
                          ? 'bg-blue-600 text-white rounded-[20px] rounded-tr-md' 
                          : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-[20px] rounded-tl-md'
                        }
                      `}
                    >
                      {msg.message_type === 'image' && msg.media_url && (
                        <div className="mb-2 -mx-2 -mt-2 overflow-hidden rounded-t-[18px]">
                          <img 
                            src={msg.media_url} 
                            alt="Media" 
                            onClick={() => setMediaViewer({ url: msg.media_url!, type: 'image' })}
                            className="w-full h-auto cursor-pointer hover:opacity-95 transition-opacity" 
                          />
                        </div>
                      )}

                      {msg.content && <p className="whitespace-pre-wrap">{msg.content}</p>}

                      <div className={`text-[10px] mt-1 flex items-center justify-end gap-1 opacity-80 ${isOwn ? 'text-blue-100' : 'text-gray-400'}`}>
                        <span>
                          {new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                        {isOwn && <CheckCheck size={12} />}
                      </div>
                    </div>
                  </div>
                </motion.div>
              );
            })}
            <div ref={messagesEndRef} />
          </div>

          <AnimatePresence>
            {isTyping && (
              <motion.div 
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 10 }}
                className="absolute bottom-20 left-6 z-30 bg-white dark:bg-gray-800 px-3 py-2 rounded-full shadow-lg border border-gray-100 dark:border-gray-700 flex items-center gap-2"
              >
                <div className="flex gap-1">
                  <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" />
                  <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce delay-100" />
                  <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce delay-200" />
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          <div className="flex-none bg-white dark:bg-gray-900 p-3 md:p-4 border-t border-gray-100 dark:border-gray-800 z-20">
            <MessageInput 
              onSendMessage={handleSendMessage}
              onTypingStart={handleTypingStart}
              onTypingStop={handleTypingStop}
              disabled={!isConnected}
            />
          </div>
        </div>
      </div>

      {mediaViewer && (
        <MediaViewer
          mediaUrl={mediaViewer.url}
          mediaType={mediaViewer.type}
          onClose={() => setMediaViewer(null)}
        />
      )}
      
      {showReportModal && currentMatch && (
        <ReportModal 
          reportedUserId={currentMatch.other_profile.anonymous_id} 
          onClose={() => setShowReportModal(false)} 
        />
      )}
      
      {showBlockModal && currentMatch && (
        <BlockConfirmation 
          blockedUserId={currentMatch.other_profile.anonymous_id} 
          onClose={() => setShowBlockModal(false)} 
        />
      )}
    </div>
  );
};

export default MatchChat;