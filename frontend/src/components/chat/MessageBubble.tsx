import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Edit2, Trash2, Pin, Flag, Ban, Smile, MoreHorizontal, Check, X, PinOff } from 'lucide-react';
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
  onReport: () => void;
  onBlock: () => void;
  onMediaClick: (url: string, type: 'image' | 'video') => void;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ 
  message, isOwnMessage, showAvatar, onEdit, onDelete, onReact, onPin, onReport, onBlock, onMediaClick 
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

  // Close emoji picker when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (emojiPickerRef.current && !emojiPickerRef.current.contains(event.target as Node)) {
        setShowEmojiPicker(false);
      }
    };
    if (showEmojiPicker) document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showEmojiPicker]);

  return (
    <motion.div 
      initial={{ opacity: 0, y: 5 }}
      animate={{ opacity: 1, y: 0 }}
      className={`group relative max-w-[85%] md:max-w-[65%] flex gap-2 ${isOwnMessage ? 'flex-row-reverse' : 'flex-row'}`}
    >
      {/* Avatar */}
      <div className={`w-7 h-7 flex-shrink-0 flex items-end ${!showAvatar ? 'opacity-0' : ''}`}>
        <div className="w-7 h-7 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center text-[9px] text-gray-500 dark:text-gray-300 font-bold select-none">
           {message.sender_id.slice(0, 2).toUpperCase()}
        </div>
      </div>

      {/* Bubble Container */}
      <div className={`flex flex-col gap-1 ${isOwnMessage ? 'items-end' : 'items-start'}`}>
        {/* Name Label (Group Chat style) */}
        {showAvatar && !isOwnMessage && (
          <span className="text-[10px] font-medium text-gray-500 dark:text-gray-400 ml-1">
            {message.sender_id.slice(0, 8)}
          </span>
        )}

        <div className={`relative px-3.5 py-2 text-[15px] leading-relaxed shadow-sm transition-colors ${
          isOwnMessage 
            ? 'bg-indigo-600 text-white rounded-[18px] rounded-tr-sm' 
            : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-[18px] rounded-tl-sm border border-gray-200 dark:border-gray-700'
        }`}>
          {message.is_pinned && (
             <div className="absolute -top-2.5 right-2 bg-yellow-100 dark:bg-yellow-900/50 text-yellow-700 dark:text-yellow-500 text-[9px] font-bold px-1.5 py-0.5 rounded-full flex items-center gap-1 shadow-sm border border-yellow-200 dark:border-yellow-700">
               <Pin size={8} className="fill-current" /> PINNED
             </div>
          )}

          {isEditing ? (
            <div className="flex flex-col gap-2 min-w-[220px]">
              <textarea 
                value={editContent}
                onChange={(e) => setEditContent(e.target.value)}
                className="w-full bg-white/20 dark:bg-black/20 rounded-lg p-2 text-sm focus:outline-none focus:ring-1 focus:ring-white/50 resize-none"
                rows={2}
                autoFocus
              />
              <div className="flex justify-end gap-2">
                <button onClick={() => setIsEditing(false)} className="p-1 hover:bg-white/10 rounded"><X size={14}/></button>
                <button onClick={handleSave} className="p-1 hover:bg-white/10 rounded text-green-300"><Check size={14}/></button>
              </div>
            </div>
          ) : (
            <>
               <div className="whitespace-pre-wrap break-words min-w-[2rem]">
                  {message.content}
               </div>

               {message.media_url && (
                 <div className="mt-2 -mx-1 rounded-lg overflow-hidden cursor-pointer hover:opacity-95 transition-opacity" onClick={() => onMediaClick(message.media_url!, message.message_type as any)}>
                    {message.message_type === 'image' ? (
                       <img src={message.media_url} alt="Attachment" className="max-w-full h-auto max-h-[300px] object-cover bg-gray-100 dark:bg-gray-900" />
                    ) : (
                       <video src={message.media_url} className="max-w-full h-auto max-h-[300px]" controls />
                    )}
                 </div>
               )}
            </>
          )}

          {/* Meta Data */}
          <div className={`flex items-center justify-end gap-1 mt-1 select-none ${isOwnMessage ? 'text-indigo-100/70' : 'text-gray-400'}`}>
            {message.is_edited && <span className="text-[9px] italic">edited</span>}
            <span className="text-[10px] tabular-nums">{new Date(message.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
            {isOwnMessage && <Check size={12} className="opacity-80" />}
          </div>
        </div>

        <MessageReactions 
          reactions={message.reactions} 
          reactionCount={message.reaction_count} 
          onReact={(emoji: string) => onReact(message.id, emoji)}
          isOwn={isOwnMessage}
        />
      </div>

      {/* Hover Actions Menu */}
      <div className={`flex items-center self-center opacity-0 group-hover:opacity-100 transition-opacity duration-200 ${isOwnMessage ? 'mr-1' : 'ml-1'}`}>
         <div className="flex items-center bg-white dark:bg-gray-800 rounded-full shadow-lg border border-gray-100 dark:border-gray-700 p-0.5">
            {/* Emoji Trigger */}
            <div className="relative" ref={emojiPickerRef}>
              <button 
                onClick={() => setShowEmojiPicker(!showEmojiPicker)} 
                className="p-1.5 text-gray-400 hover:text-yellow-500 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-full transition-colors"
              >
                <Smile size={15} />
              </button>
              
              <AnimatePresence>
                {showEmojiPicker && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.9, y: 10 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.9, y: 10 }}
                    className="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 bg-white dark:bg-gray-800 shadow-xl rounded-xl border border-gray-100 dark:border-gray-700 p-2 z-50 w-48"
                  >
                    <div className="grid grid-cols-4 gap-1">
                      {commonEmojis.map((emoji) => (
                        <button
                          key={emoji}
                          onClick={() => handleEmojiSelect(emoji)}
                          className="p-1.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded text-lg transition-colors text-center"
                        >
                          {emoji}
                        </button>
                      ))}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
            
            {isOwnMessage ? (
              <>
                <button onClick={() => setIsEditing(true)} className="p-1.5 text-gray-400 hover:text-indigo-500 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-full transition-colors"><Edit2 size={14} /></button>
                <button onClick={() => onDelete(message.id)} className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-full transition-colors"><Trash2 size={14} /></button>
              </>
            ) : (
              <div className="relative group/menu">
                <button className="p-1.5 text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-full"><MoreHorizontal size={15} /></button>
                <div className="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 hidden group-hover/menu:flex flex-col bg-white dark:bg-gray-800 shadow-xl rounded-lg overflow-hidden border border-gray-100 dark:border-gray-700 min-w-[120px] z-50">
                   <button onClick={onReport} className="flex items-center gap-2 px-3 py-2.5 hover:bg-gray-50 dark:hover:bg-gray-700 text-xs text-gray-600 dark:text-gray-300 whitespace-nowrap font-medium transition-colors"><Flag size={12}/> Report Message</button>
                   <button onClick={onBlock} className="flex items-center gap-2 px-3 py-2.5 hover:bg-red-50 dark:hover:bg-red-900/20 text-xs text-red-500 whitespace-nowrap font-medium transition-colors"><Ban size={12}/> Block User</button>
                </div>
              </div>
            )}
            
            <button 
              onClick={() => onPin(message.id)} 
              className={`p-1.5 rounded-full transition-colors ${
                message.is_pinned 
                  ? 'text-yellow-500 hover:bg-yellow-50 dark:hover:bg-yellow-900/20' 
                  : 'text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
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