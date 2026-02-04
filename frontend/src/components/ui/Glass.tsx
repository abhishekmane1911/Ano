import { motion } from 'framer-motion';
import { AlertCircle } from 'lucide-react';

// --- Glass Card Wrapper ---
export const GlassCard = ({ children, className = '', ...props }: any) => (
  <motion.div 
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    className={`relative overflow-hidden bg-white/10 dark:bg-black/20 backdrop-blur-xl border border-white/20 dark:border-white/10 shadow-[0_8px_32px_0_rgba(31,38,135,0.07)] rounded-2xl ${className}`}
    {...props}
  >
    {/* Shine effect */}
    <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/40 to-transparent opacity-50" />
    {children}
  </motion.div>
);

// --- Glass Input Field ---
export const GlassInput = ({ label, error, icon: Icon, ...props }: any) => (
  <div className="group relative z-0 w-full mb-6">
    <input
      {...props}
      className={`block py-3 px-4 w-full text-base text-gray-900 dark:text-white bg-white/5 dark:bg-black/20 border-2 rounded-xl appearance-none focus:outline-none focus:ring-0 transition-all peer ${
        error 
        ? 'border-red-400/50 focus:border-red-500' 
        : 'border-white/10 dark:border-white/5 focus:border-indigo-500/50 dark:focus:border-indigo-400/50'
      }`}
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
export const RadioCard = ({ selected, value, label, icon: Icon, onChange, name }: any) => (
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
        {Icon}
      </div>
      <span className={`text-sm font-medium ${selected === value ? 'text-indigo-600 dark:text-indigo-300' : 'text-gray-600 dark:text-gray-400'}`}>
        {label}
      </span>
    </motion.div>
  </label>
);