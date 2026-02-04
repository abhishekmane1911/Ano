import { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { User, Camera } from 'lucide-react';

interface AnonymousAvatarProps {
  currentAvatar?: string | null;
  onImageSelect: (file: File) => void;
  isEditable?: boolean;
  size?: 'small' | 'medium' | 'large';
}

const AnonymousAvatar = ({
  currentAvatar,
  onImageSelect,
  isEditable = true,
  size = 'medium',
}: AnonymousAvatarProps) => {
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const sizeClasses = {
    small: 'w-12 h-12',
    medium: 'w-24 h-24',
    large: 'w-40 h-40'
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (!['image/jpeg', 'image/png', 'image/gif'].includes(file.type)) {
        alert('Invalid file type. Only JPEG, PNG, and GIF are allowed.');
        return;
      }
      if (file.size > 5 * 1024 * 1024) {
        alert('File size too large. Maximum size is 5MB.');
        return;
      }

      const reader = new FileReader();
      reader.onloadend = () => setPreviewUrl(reader.result as string);
      reader.readAsDataURL(file);
      onImageSelect(file);
    }
  };

  return (
    <div className="relative group">
      <motion.div 
        className={`relative rounded-full overflow-hidden border-4 border-white/20 dark:border-white/10 shadow-2xl ${sizeClasses[size]} bg-gray-100 dark:bg-gray-800 flex items-center justify-center`}
        whileHover={isEditable ? { scale: 1.05 } : {}}
        onClick={() => isEditable && fileInputRef.current?.click()}
      >
        {(previewUrl || currentAvatar) ? (
          <img src={previewUrl || currentAvatar || ''} alt="Profile avatar" className="w-full h-full object-cover" />
        ) : (
          <User className="text-gray-400 w-1/2 h-1/2" />
        )}
        
        {isEditable && (
          <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col items-center justify-center cursor-pointer backdrop-blur-[2px]">
            <Camera className="text-white mb-1" size={size === 'small' ? 12 : 24} />
            {size !== 'small' && <span className="text-white text-[10px] font-medium uppercase tracking-wider">Edit</span>}
          </div>
        )}
      </motion.div>
      <input 
        ref={fileInputRef} 
        type="file" 
        className="hidden" 
        accept="image/jpeg,image/jpg,image/png,image/gif" 
        onChange={handleFileChange} 
      />
    </div>
  );
};

export default AnonymousAvatar;