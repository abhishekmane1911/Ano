import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Smile, Edit2, Trash2, Check, X, ThumbsUp, ThumbsDown, MoreHorizontal, Flag, Ban, Pin } from 'lucide-react';
import type { Message } from '../../stores/chatStore';
import MessageReactions from './MessageReactions';

const getTierColors = (tier?: string) => {
  switch (tier) {
    case 'Campus Legend': return 'border-amber-500/50 text-amber-400 bg-amber-500/10';
    case 'Senior': return 'border-indigo-500/50 text-indigo-400 bg-indigo-500/10';
    case 'Sophomore': return 'border-emerald-500/50 text-emerald-400 bg-emerald-500/10';
    case 'Fresher': 
    default: 
      return 'border-zinc-700 text-zinc-400 bg-zinc-800/80';
  }
};

interface MessageBubbleProps {
  message: Message;
  isOwnMessage: boolean;
  showAvatar: boolean;
  onEdit: (id: string, content: string) => void;
  onDelete: (id: string) => void;
  onReact: (id: string, emoji: string) => void;
  onPin: (id: string, isPinned: boolean) => void;
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
        <div className="w-7 h-7 rounded-full bg-zinc-800 flex items-center justify-center text-[9px] text-zinc-400 font-semibold select-none">
          {message.sender_id.slice(0, 2).toUpperCase()}
        </div>
      </div>

      {/* Bubble Container */}
      <div className={`flex flex-col gap-1 ${isOwnMessage ? 'items-end' : 'items-start'}`}>
        {showAvatar && !isOwnMessage && (
          <div className="flex items-center gap-1.5 ml-1">
            <span className="text-[11px] font-medium text-zinc-500">
              {message.sender_id.slice(0, 8)}
            </span>
            {message.sender_tier && (
              <span className={`text-[9px] font-semibold px-1.5 py-[1px] rounded ${getTierColors(message.sender_tier)} border`}>
                {message.sender_tier}
              </span>
            )}
          </div>
        )}

        <div className={`relative px-3.5 py-2 text-[14px] leading-relaxed rounded-xl ${isOwnMessage
            ? 'bg-blue-600 text-white rounded-tr-sm'
            : 'bg-zinc-800 text-zinc-100 rounded-tl-sm border border-zinc-700'
          }`}>
          {message.is_pinned && (
            <div className="absolute -top-2 right-2 bg-zinc-900 text-zinc-400 text-[9px] font-medium px-1.5 py-0.5 rounded-full flex items-center gap-1 border border-zinc-700">
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
                    <img src={message.media_url} alt="Attachment" className="max-w-full h-auto max-h-[300px] object-cover bg-zinc-900" />
                  ) : (
                    <video src={message.media_url} className="max-w-full h-auto max-h-[300px]" controls />
                  )}
                </div>
              )}
            </>
          )}

          <div className={`flex items-center justify-end gap-1 mt-1 select-none ${isOwnMessage ? 'text-blue-100/80' : 'text-zinc-500'}`}>
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
                  ? 'text-emerald-400 bg-emerald-900/20'
                  : 'text-zinc-500'
                }`}>
                <ThumbsUp size={10} /> {upvotes}
              </span>
            )}
            {downvotes > 0 && (
              <span className={`flex items-center gap-1 text-[11px] font-medium px-1.5 py-0.5 rounded ${userVote === 'downvote'
                  ? 'text-red-400 bg-red-900/20'
                  : 'text-zinc-500'
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
        <div className="flex items-center bg-zinc-800 rounded-full shadow-sm border border-zinc-700 p-0.5">
          {/* Emoji Trigger */}
          <div className="relative" ref={emojiPickerRef}>
            <button
              onClick={() => setShowEmojiPicker(!showEmojiPicker)}
              className="p-1.5 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-700 rounded-full transition-colors"
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
                  className="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 bg-zinc-800 shadow-md rounded-lg border border-zinc-700 p-2 z-50 w-48"
                >
                  <div className="grid grid-cols-4 gap-1">
                    {commonEmojis.map((emoji) => (
                      <button
                        key={emoji}
                        onClick={() => handleEmojiSelect(emoji)}
                        className="p-1.5 hover:bg-zinc-700 rounded text-lg transition-colors text-center"
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
                ? 'bg-emerald-900/20 text-emerald-400'
                : 'text-zinc-400 hover:text-emerald-500 hover:bg-zinc-700'
              }`}
            title="Upvote"
          >
            <ThumbsUp size={14} />
          </button>
          <button
            onClick={() => onVote(message.id, 'downvote')}
            className={`p-1.5 rounded-full transition-colors ${userVote === 'downvote'
                ? 'bg-red-900/20 text-red-400'
                : 'text-zinc-400 hover:text-red-500 hover:bg-zinc-700'
              }`}
            title="Downvote"
          >
            <ThumbsDown size={14} />
          </button>

          {isOwnMessage ? (
            <>
              <button onClick={() => setIsEditing(true)} className="p-1.5 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-700 rounded-full transition-colors">
                <Edit2 size={14} />
              </button>
              <button onClick={() => onDelete(message.id)} className="p-1.5 text-zinc-400 hover:text-red-500 hover:bg-zinc-700 rounded-full transition-colors">
                <Trash2 size={14} />
              </button>
            </>
          ) : (
            <div className="relative group/menu">
              <button className="p-1.5 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-700 rounded-full">
                <MoreHorizontal size={15} />
              </button>
              <div className="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 hidden group-hover/menu:flex flex-col bg-zinc-800 shadow-md rounded-lg overflow-hidden border border-zinc-700 min-w-[130px] z-50">
                <button onClick={onReport} className="flex items-center gap-2 px-3 py-2.5 hover:bg-zinc-700 text-xs text-zinc-300 whitespace-nowrap font-medium transition-colors">
                  <Flag size={12} /> Report message
                </button>
                <button onClick={onBlock} className="flex items-center gap-2 px-3 py-2.5 hover:bg-zinc-700 text-xs text-red-500 whitespace-nowrap font-medium transition-colors">
                  <Ban size={12} /> Block user
                </button>
              </div>
            </div>
          )}

          <button
            onClick={() => onPin(message.id, message.is_pinned)}
            className={`p-1.5 rounded-full transition-colors ${message.is_pinned
                ? 'text-zinc-200 hover:bg-zinc-700'
                : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-700'
              }`}
            title={message.is_pinned ? "Unpin message" : "Pin message"}
          >
            <Pin size={14} className={message.is_pinned ? "fill-current" : ""} />
          </button>
        </div>
      </div>
    </motion.div>
  );
};

export default MessageBubble;