import { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Star } from 'lucide-react';

interface InterestSelectorProps {
  label: string;
  selectedItems: string[];
  onChange: (items: string[]) => void;
  placeholder?: string;
  suggestions?: string[];
}

const InterestSelector = ({
  label,
  selectedItems = [],
  onChange,
  placeholder = 'Type and press Enter to add',
  suggestions = [],
}: InterestSelectorProps) => {
  const [inputValue, setInputValue] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleAddItem = (item: string) => {
    const trimmedItem = item.trim();
    if (trimmedItem && !selectedItems.includes(trimmedItem)) {
      onChange([...selectedItems, trimmedItem]);
      setInputValue('');
      setShowSuggestions(false);
    }
  };

  const handleRemoveItem = (itemToRemove: string) => {
    onChange(selectedItems.filter((item) => item !== itemToRemove));
  };

  const filteredSuggestions = suggestions.filter((suggestion) =>
    !selectedItems.includes(suggestion) &&
    suggestion.toLowerCase().includes(inputValue.toLowerCase())
  );

  return (
    <div className="mb-6">
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 ml-1">{label}</label>
      
      {/* Selected Tags Area */}
      <div className="flex flex-wrap gap-2 mb-3 min-h-[32px]">
        <AnimatePresence>
          {selectedItems.map((item) => (
            <motion.span
              key={item}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.5 }}
              className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-indigo-500/10 text-indigo-700 dark:text-indigo-300 border border-indigo-500/20 backdrop-blur-md"
            >
              {item}
              <button
                type="button"
                onClick={() => handleRemoveItem(item)}
                className="ml-2 hover:bg-indigo-500/20 rounded-full p-0.5 transition-colors"
                aria-label={`Remove ${item}`}
              >
                <X size={12} />
              </button>
            </motion.span>
          ))}
        </AnimatePresence>
      </div>

      {/* Input Area */}
      <div className="relative">
        <div className="relative">
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => {
              setInputValue(e.target.value);
              setShowSuggestions(true);
            }}
            onFocus={() => setShowSuggestions(true)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                handleAddItem(inputValue);
              }
            }}
            onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
            className="w-full pl-10 pr-4 py-3 bg-white/5 dark:bg-black/20 border-2 border-white/10 dark:border-white/5 rounded-xl focus:border-indigo-500/50 focus:outline-none transition-colors text-gray-900 dark:text-white placeholder-gray-500"
            placeholder={placeholder}
          />
          <div className="absolute left-3 top-3.5 text-gray-400">
            <Star size={18} />
          </div>
        </div>

        {/* Glass Dropdown */}
        <AnimatePresence>
          {showSuggestions && inputValue.length > 0 && filteredSuggestions.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="absolute z-50 w-full mt-2 overflow-hidden bg-white/90 dark:bg-gray-900/90 backdrop-blur-xl border border-white/20 rounded-xl shadow-xl max-h-48 overflow-y-auto custom-scrollbar"
            >
              {filteredSuggestions.map((suggestion) => (
                <button
                  key={suggestion}
                  type="button"
                  onClick={() => handleAddItem(suggestion)}
                  className="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-indigo-500/10 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors flex items-center justify-between group"
                >
                  {suggestion}
                  <span className="opacity-0 group-hover:opacity-100 text-xs uppercase font-bold tracking-wider">Add +</span>
                </button>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default InterestSelector;