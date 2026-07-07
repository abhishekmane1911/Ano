import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Edit2, Trash2, Pin, Flag, Ban, Smile, MoreHorizontal, Check, X, PinOff, ThumbsUp, ThumbsDown } from 'lucide-react';
import type { Message } from '../../stores/chatStore';
import MessageReactions from './MessageReactions';

interface MessageBubbleProps {
  message: Message;
  isOwnMessage: boolean;
  showAvatar: boolean;
  onEdit: (id: string, content: string) => void;
  onDelete: (id: string) => void;
  onReact: (id: string, emoji: string) => void;
  onPin: (id: string) => void;
  onVote: (id: string, type: 'upvote' | 'downvote') => void;
  onReport: () => void;
  onBlock: () => void;
  onMediaClick: (url: string, type: 'image' | 'video') => void;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({
  message, isOwnMessage, showAvatar, onEdit, onDelete, onReact, onPin, onVote, onReport, onBlock, onMediaClick
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState(message.content);
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const emojiPickerRef = useRef<HTMLDivElement>(null);

  const commonEmojis = ['❤️', '👍', '😂', '😮', '😢', '🙏', '🎉', '🔥'];

  const handleSave = () => {
    if (editContent.trim()) {
      onEdit(message.id, editContent);
      setIsEditing(false);
    }
  };

  const handleEmojiSelect = (emoji: string) => {
    onReact(message.id, emoji);
    setShowEmojiPicker(false);
  };

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (emojiPickerRef.current && !emojiPickerRef.current.contains(event.target as Node)) {
        setShowEmojiPicker(false);
      }
    };
    if (showEmojiPicker) document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showEmojiPicker]);

  const upvotes = message.ranking?.upvotes ?? message.upvotes ?? 0;
  const downvotes = message.ranking?.downvotes ?? message.downvotes ?? 0;
  const userVote = message.ranking?.user_vote ?? message.user_vote ?? null;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.15 }}
      className={`group relative max-w-[85%] md:max-w-[65%] flex gap-2 ${isOwnMessage ? 'flex-row-reverse' : 'flex-row'}`}
    >
      {/* Avatar */}
      <div className={`w-7 h-7 flex-shrink-0 flex items-end ${!showAvatar ? 'opacity-0' : ''}`}>
        <div className="w-7 h-7 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-[9px] text-slate-500 dark:text-slate-400 font-semibold select-none">
          {message.sender_id.slice(0, 2).toUpperCase()}
        </div>
      </div>

      {/* Bubble Container */}
      <div className={`flex flex-col gap-1 ${isOwnMessage ? 'items-end' : 'items-start'}`}>
        {showAvatar && !isOwnMessage && (
          <span className="text-[11px] font-medium text-slate-400 dark:text-slate-500 ml-1">
            {message.sender_id.slice(0, 8)}
          </span>
        )}

        <div className={`relative px-3.5 py-2 text-[14px] leading-relaxed rounded-xl ${isOwnMessage
            ? 'bg-blue-600 text-white rounded-tr-sm'
            : 'bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 rounded-tl-sm border border-slate-200 dark:border-slate-700'
          }`}>
          {message.is_pinned && (
            <div className="absolute -top-2 right-2 bg-white dark:bg-slate-900 text-slate-500 dark:text-slate-400 text-[9px] font-medium px-1.5 py-0.5 rounded-full flex items-center gap-1 border border-slate-200 dark:border-slate-700">
              <Pin size={8} /> Pinned
            </div>
          )}

          {isEditing ? (
            <div className="flex flex-col gap-2 min-w-[220px]">
              <textarea
                value={editContent}
                onChange={(e) => setEditContent(e.target.value)}
                className="w-full bg-white/15 dark:bg-black/20 rounded-md p-2 text-sm focus:outline-none focus:ring-1 focus:ring-white/40 resize-none"
                rows={2}
                autoFocus
              />
              <div className="flex justify-end gap-2">
                <button onClick={() => setIsEditing(false)} className="p-1 hover:bg-white/10 rounded"><X size={14} /></button>
                <button onClick={handleSave} className="p-1 hover:bg-white/10 rounded"><Check size={14} /></button>
              </div>
            </div>
          ) : (
            <>
              <div className="whitespace-pre-wrap break-words min-w-[2rem]">
                {message.content}
              </div>

              {message.media_url && (
                <div
                  className="mt-2 -mx-1 rounded-md overflow-hidden cursor-pointer hover:opacity-95 transition-opacity"
                  onClick={() => onMediaClick(message.media_url!, message.message_type as any)}
                >
                  {message.message_type === 'image' ? (
                    <img src={message.media_url} alt="Attachment" className="max-w-full h-auto max-h-[300px] object-cover bg-slate-100 dark:bg-slate-900" />
                  ) : (
                    <video src={message.media_url} className="max-w-full h-auto max-h-[300px]" controls />
                  )}
                </div>
              )}
            </>
          )}

          <div className={`flex items-center justify-end gap-1 mt-1 select-none ${isOwnMessage ? 'text-blue-100/80' : 'text-slate-400'}`}>
            {message.is_edited && <span className="text-[9px] italic">edited</span>}
            <span className="text-[10px] tabular-nums">
              {new Date(message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </span>
            {isOwnMessage && <Check size={12} className="opacity-80" />}
          </div>
        </div>

        {/* Vote counts shown below bubble */}
        {(upvotes > 0 || downvotes > 0) && (
          <div className="flex items-center gap-1.5 px-1">
            {upvotes > 0 && (
              <span className={`flex items-center gap-1 text-[11px] font-medium px-1.5 py-0.5 rounded ${userVote === 'upvote'
                  ? 'text-emerald-700 bg-emerald-50 dark:text-emerald-400 dark:bg-emerald-900/20'
                  : 'text-slate-400'
                }`}>
                <ThumbsUp size={10} /> {upvotes}
              </span>
            )}
            {downvotes > 0 && (
              <span className={`flex items-center gap-1 text-[11px] font-medium px-1.5 py-0.5 rounded ${userVote === 'downvote'
                  ? 'text-red-700 bg-red-50 dark:text-red-400 dark:bg-red-900/20'
                  : 'text-slate-400'
                }`}>
                <ThumbsDown size={10} /> {downvotes}
              </span>
            )}
          </div>
        )}

        <MessageReactions
          reactions={message.reactions}
          reactionCount={message.reaction_count}
          onReact={(emoji: string) => onReact(message.id, emoji)}
          isOwn={isOwnMessage}
        />
      </div>

      {/* Hover Actions Menu */}
      <div className={`flex items-center self-center opacity-0 group-hover:opacity-100 transition-opacity duration-150 ${isOwnMessage ? 'mr-1' : 'ml-1'}`}>
        <div className="flex items-center bg-white dark:bg-slate-800 rounded-full shadow-sm border border-slate-200 dark:border-slate-700 p-0.5">
          {/* Emoji Trigger */}
          <div className="relative" ref={emojiPickerRef}>
            <button
              onClick={() => setShowEmojiPicker(!showEmojiPicker)}
              className="p-1.5 text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-700 rounded-full transition-colors"
            >
              <Smile size={15} />
            </button>

            <AnimatePresence>
              {showEmojiPicker && (
                <motion.div
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 6 }}
                  transition={{ duration: 0.12 }}
                  className="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 bg-white dark:bg-slate-800 shadow-md rounded-lg border border-slate-200 dark:border-slate-700 p-2 z-50 w-48"
                >
                  <div className="grid grid-cols-4 gap-1">
                    {commonEmojis.map((emoji) => (
                      <button
                        key={emoji}
                        onClick={() => handleEmojiSelect(emoji)}
                        className="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-700 rounded text-lg transition-colors text-center"
                      >
                        {emoji}
                      </button>
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Vote buttons */}
          <button
            onClick={() => onVote(message.id, 'upvote')}
            className={`p-1.5 rounded-full transition-colors ${userVote === 'upvote'
                ? 'text-emerald-600 bg-emerald-50 dark:bg-emerald-900/20'
                : 'text-slate-400 hover:text-emerald-600 hover:bg-slate-50 dark:hover:bg-slate-700'
              }`}
            title="Upvote"
          >
            <ThumbsUp size={14} />
          </button>
          <button
            onClick={() => onVote(message.id, 'downvote')}
            className={`p-1.5 rounded-full transition-colors ${userVote === 'downvote'
                ? 'text-red-600 bg-red-50 dark:bg-red-900/20'
                : 'text-slate-400 hover:text-red-600 hover:bg-slate-50 dark:hover:bg-slate-700'
              }`}
            title="Downvote"
          >
            <ThumbsDown size={14} />
          </button>

          {isOwnMessage ? (
            <>
              <button onClick={() => setIsEditing(true)} className="p-1.5 text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-700 rounded-full transition-colors">
                <Edit2 size={14} />
              </button>
              <button onClick={() => onDelete(message.id)} className="p-1.5 text-slate-400 hover:text-red-600 hover:bg-slate-50 dark:hover:bg-slate-700 rounded-full transition-colors">
                <Trash2 size={14} />
              </button>
            </>
          ) : (
            <div className="relative group/menu">
              <button className="p-1.5 text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-700 rounded-full">
                <MoreHorizontal size={15} />
              </button>
              <div className="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 hidden group-hover/menu:flex flex-col bg-white dark:bg-slate-800 shadow-md rounded-lg overflow-hidden border border-slate-200 dark:border-slate-700 min-w-[130px] z-50">
                <button onClick={onReport} className="flex items-center gap-2 px-3 py-2.5 hover:bg-slate-50 dark:hover:bg-slate-700 text-xs text-slate-600 dark:text-slate-300 whitespace-nowrap font-medium transition-colors">
                  <Flag size={12} /> Report message
                </button>
                <button onClick={onBlock} className="flex items-center gap-2 px-3 py-2.5 hover:bg-slate-50 dark:hover:bg-slate-700 text-xs text-red-600 whitespace-nowrap font-medium transition-colors">
                  <Ban size={12} /> Block user
                </button>
              </div>
            </div>
          )}

          <button
            onClick={() => onPin(message.id)}
            className={`p-1.5 rounded-full transition-colors ${message.is_pinned
                ? 'text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-700'
                : 'text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-700'
              }`}
            title={message.is_pinned ? 'Unpin message' : 'Pin message'}
          >
            {message.is_pinned ? <PinOff size={14} /> : <Pin size={14} />}
          </button>
        </div>
      </div>
    </motion.div>
  );
};

export default MessageBubble;