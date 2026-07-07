import { motion, AnimatePresence } from 'framer-motion';
import { AlertCircle, X } from 'lucide-react';
import type { ReactNode, ButtonHTMLAttributes, HTMLAttributes } from 'react';

// --- Glass Card Wrapper ---
interface GlassCardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  blur?: number;
  opacity?: number;
  className?: string;
}

export const GlassCard = ({ children, className = '', blur = 12, opacity = 10, ...props }: GlassCardProps) => (
  <motion.div 
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    className={`relative overflow-hidden bg-white/${opacity} dark:bg-black/20 backdrop-blur-${blur === 12 ? 'xl' : blur === 8 ? 'lg' : 'md'} border border-white/20 dark:border-white/10 shadow-[0_8px_32px_0_rgba(31,38,135,0.07)] rounded-2xl ${className}`}
    {...props}
  >
    {/* Shine effect */}
    <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/40 to-transparent opacity-50" />
    {children}
  </motion.div>
);

// --- Glass Modal ---
interface GlassModalProps {
  isOpen: boolean;
  onClose: () => void;
  children: ReactNode;
  title?: string;
  className?: string;
}

export const GlassModal = ({ isOpen, onClose, children, title, className = '' }: GlassModalProps) => (
  <AnimatePresence>
    {isOpen && (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center p-4"
        onClick={onClose}
      >
        {/* Backdrop */}
        <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" />
        
        {/* Modal Content */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9, y: 20 }}
          className={`relative w-full max-w-md max-h-[90vh] overflow-hidden bg-white/10 dark:bg-black/20 backdrop-blur-xl border border-white/20 dark:border-white/10 shadow-[0_8px_32px_0_rgba(31,38,135,0.07)] rounded-2xl ${className}`}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Shine effect */}
          <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/40 to-transparent opacity-50" />
          
          {/* Header */}
          {title && (
            <div className="flex items-center justify-between p-6 border-b border-white/10">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">{title}</h2>
              <button
                onClick={onClose}
                className="p-2 rounded-lg hover:bg-white/10 dark:hover:bg-white/5 transition-colors"
              >
                <X size={20} className="text-gray-500 dark:text-gray-400" />
              </button>
            </div>
          )}
          
          {/* Content */}
          <div className="p-6 overflow-y-auto">
            {children}
          </div>
        </motion.div>
      </motion.div>
    )}
  </AnimatePresence>
);

// --- Glass Button ---
interface GlassButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const GlassButton = ({ 
  children, 
  variant = 'primary', 
  size = 'md', 
  className = '', 
  disabled,
  ...props 
}: GlassButtonProps) => {
  const baseClasses = "relative overflow-hidden backdrop-blur-md border transition-all duration-200 font-medium rounded-xl focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed";
  
  const variantClasses = {
    primary: "bg-indigo-500/20 border-indigo-500/30 text-indigo-600 dark:text-indigo-400 hover:bg-indigo-500/30 focus:ring-indigo-500/50",
    secondary: "bg-white/10 dark:bg-black/20 border-white/20 dark:border-white/10 text-gray-900 dark:text-white hover:bg-white/20 dark:hover:bg-black/30 focus:ring-white/50",
    ghost: "bg-transparent border-transparent text-gray-700 dark:text-gray-300 hover:bg-white/10 dark:hover:bg-white/5 focus:ring-gray-500/50"
  };
  
  const sizeClasses = {
    sm: "px-3 py-2 text-sm",
    md: "px-4 py-2.5 text-base",
    lg: "px-6 py-3 text-lg"
  };

  return (
    <motion.button
      whileHover={{ scale: disabled ? 1 : 1.02 }}
      whileTap={{ scale: disabled ? 1 : 0.98 }}
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
      disabled={disabled}
      {...props}
    >
      {/* Shine effect */}
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/40 to-transparent opacity-50" />
      {children}
    </motion.button>
  );
};

// --- Glass Input Field ---
interface GlassInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
  icon?: React.ComponentType<{ size?: number }>;
}

export const GlassInput = ({ label, error, icon: Icon, className = '', ...props }: GlassInputProps) => (
  <div className="group relative z-0 w-full mb-6">
    <input
      {...props}
      className={`block py-3 px-4 w-full text-base text-gray-900 dark:text-white bg-white/5 dark:bg-black/20 border-2 rounded-xl appearance-none focus:outline-none focus:ring-0 transition-all peer ${
        error 
        ? 'border-red-400/50 focus:border-red-500' 
        : 'border-white/10 dark:border-white/5 focus:border-indigo-500/50 dark:focus:border-indigo-400/50'
      } ${className}`}
      placeholder=" " 
    />
    <label className={`absolute text-sm duration-300 transform -translate-y-4 scale-75 top-2 z-10 origin-[0] bg-transparent px-2 peer-placeholder-shown:px-4 peer-focus:px-2 peer-placeholder-shown:scale-100 peer-placeholder-shown:translate-y-3 peer-focus:scale-75 peer-focus:-translate-y-4 left-1 ${
      error ? 'text-red-400' : 'text-gray-500 dark:text-gray-400 peer-focus:text-indigo-600 dark:peer-focus:text-indigo-400'
    }`}>
      <span className="flex items-center gap-2">
        {Icon && <Icon size={14} />} {label}
      </span>
    </label>
    {error && (
      <motion.p 
        initial={{ opacity: 0, x: -10 }}
        animate={{ opacity: 1, x: 0 }}
        className="mt-1 text-xs text-red-400 flex items-center gap-1 pl-1"
      >
        <AlertCircle size={12} /> {error}
      </motion.p>
    )}
  </div>
);

// --- Glass Radio Card (for Relationships) ---
interface RadioCardProps {
  selected: string;
  value: string;
  label: string;
  icon: ReactNode;
  onChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  name: string;
}

export const RadioCard = ({ selected, value, label, icon, onChange, name }: RadioCardProps) => (
  <label className="cursor-pointer relative flex-1">
    <input 
      type="radio" 
      name={name} 
      value={value} 
      checked={selected === value} 
      onChange={onChange}
      className="sr-only" 
    />
    <motion.div 
      animate={{ 
        backgroundColor: selected === value ? 'rgba(99, 102, 241, 0.2)' : 'rgba(255, 255, 255, 0.05)',
        borderColor: selected === value ? 'rgba(99, 102, 241, 0.5)' : 'rgba(255, 255, 255, 0.1)',
      }}
      className="p-4 rounded-xl border-2 flex flex-col items-center gap-2 text-center transition-colors hover:bg-white/10 dark:hover:bg-white/5"
    >
      <div className={`p-2 rounded-full ${selected === value ? 'bg-indigo-500 text-white' : 'bg-gray-200 dark:bg-gray-800 text-gray-500'}`}>
        {icon}
      </div>
      <span className={`text-sm font-medium ${selected === value ? 'text-indigo-600 dark:text-indigo-300' : 'text-gray-600 dark:text-gray-400'}`}>
        {label}
      </span>
    </motion.div>
  </label>
);