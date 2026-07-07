import { useState, useRef } from 'react';
import EmojiPicker, { type EmojiClickData } from 'emoji-picker-react';
import { Send, Smile, X, Image as ImageIcon } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface MessageInputProps {
  onSendMessage: (content: string, file?: File) => void;
  onTypingStart: () => void;
  onTypingStop: () => void;
  disabled?: boolean;
  canUploadImages?: boolean;
}

const MessageInput: React.FC<MessageInputProps> = ({ onSendMessage, onTypingStart, onTypingStop, disabled, canUploadImages = true }) => {
  const [message, setMessage] = useState('');
  const [showEmoji, setShowEmoji] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [filePreview, setFilePreview] = useState<string | null>(null);
  const typingTimeoutRef = useRef<number | null>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSend = () => {
    if ((message.trim() || selectedFile) && !disabled) {
      onSendMessage(message.trim() || 'Image', selectedFile || undefined);
      setMessage('');
      setSelectedFile(null);
      setFilePreview(null);
      if (inputRef.current) inputRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);
    onTypingStart();
    if (typingTimeoutRef.current) clearTimeout(typingTimeoutRef.current);
    typingTimeoutRef.current = setTimeout(onTypingStop, 2000);

    e.target.style.height = 'auto';
    e.target.style.height = `${e.target.scrollHeight}px`;
  };

  const onEmojiClick = (emojiData: EmojiClickData) => {
    setMessage((prev) => prev + emojiData.emoji);
    setShowEmoji(false);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (!canUploadImages) {
        alert('You need to reach Senior tier to upload images! Earn reputation by chatting.');
        return;
      }

      if (!file.type.startsWith('image/')) {
        alert('Please select an image file');
        return;
      }

      if (file.size > 5 * 1024 * 1024) {
        alert('File size must be less than 5MB');
        return;
      }

      setSelectedFile(file);

      const reader = new FileReader();
      reader.onloadend = () => {
        setFilePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    setFilePreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const canSend = (message.trim() || selectedFile) && !disabled;

  return (
    <div className="relative">
      <AnimatePresence>
        {showEmoji && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            transition={{ duration: 0.12 }}
            className="absolute bottom-full mb-3 left-0 z-50 shadow-md rounded-lg overflow-hidden border border-slate-200 dark:border-slate-700"
          >
            <EmojiPicker onEmojiClick={onEmojiClick} />
          </motion.div>
        )}
      </AnimatePresence>

      {/* File Preview */}
      {filePreview && (
        <div className="mb-2 relative inline-block">
          <img
            src={filePreview}
            alt="Preview"
            className="max-h-32 rounded-md border border-slate-200 dark:border-slate-700"
          />
          <button
            onClick={handleRemoveFile}
            className="absolute -top-2 -right-2 p-1 bg-slate-900 text-white rounded-full hover:bg-slate-700 transition-colors"
          >
            <X size={14} />
          </button>
        </div>
      )}

      <div className="flex items-end gap-1 bg-slate-50 dark:bg-slate-800/60 p-1.5 rounded-lg border border-slate-200 dark:border-slate-700 transition-colors focus-within:border-slate-300 dark:focus-within:border-slate-600">
        <div className="flex gap-0.5 mb-0.5">
          <button
            onClick={() => setShowEmoji(!showEmoji)}
            className="p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-md transition-colors"
            title="Add emoji"
          >
            <Smile size={18} />
          </button>
          <button
            onClick={() => {
              if (canUploadImages) {
                fileInputRef.current?.click();
              } else {
                alert('You need to reach Senior tier to upload images! Earn reputation by getting upvotes.');
              }
            }}
            className={`p-2 rounded-md transition-colors ${canUploadImages ? 'text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700' : 'text-slate-300 dark:text-slate-600 cursor-not-allowed'}`}
            title={canUploadImages ? "Attach image" : "Reach Senior tier to unlock image uploads"}
          >
            <ImageIcon size={18} />
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileSelect}
            className="hidden"
          />
        </div>

        <textarea
          ref={inputRef}
          value={message}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder={selectedFile ? "Add a caption..." : "Message"}
          disabled={disabled}
          rows={1}
          className="flex-1 bg-transparent border-none focus:ring-0 text-sm text-slate-800 dark:text-slate-100 placeholder-slate-400 py-2.5 max-h-32 min-h-[40px] resize-none custom-scrollbar"
        />

        <button
          onClick={handleSend}
          disabled={!canSend}
          className={`p-2 rounded-md mb-0.5 transition-colors ${canSend
              ? 'bg-blue-600 text-white hover:bg-blue-700'
              : 'bg-slate-200 dark:bg-slate-700 text-slate-400 cursor-not-allowed'
            }`}
        >
          <Send size={16} />
        </button>
      </div>
    </div>
  );
};

export default MessageInput;