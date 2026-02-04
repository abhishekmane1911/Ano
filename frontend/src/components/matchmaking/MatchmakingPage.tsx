import { useState } from 'react';
import { motion } from 'framer-motion';
import SwipeInterface from './SwipeInterface';
import MatchList from './MatchList';

const MatchmakingPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'swipe' | 'matches'>('swipe');

  return (
    <div className="relative w-full h-screen overflow-hidden bg-[#f3f4f6] dark:bg-[#0f172a] pt-24">
      
      {/* Dynamic Background (Consistent with ChatPage) */}
      <div className="absolute inset-0 pointer-events-none z-0">
        <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-indigo-50/50 via-white/50 to-purple-50/50 dark:from-indigo-950/30 dark:via-gray-950/80 dark:to-purple-950/30" />
      </div>

      <div className="relative z-10 w-full h-full max-w-4xl mx-auto flex flex-col px-4 pb-4">
        
        {/* Professional Segmented Control */}
        <div className="flex-shrink-0 flex justify-center mb-6">
          <div className="bg-gray-200 dark:bg-gray-800 p-1 rounded-lg inline-flex">
            <button
              onClick={() => setActiveTab('swipe')}
              className={`px-6 py-2 rounded-md text-sm font-medium transition-all ${
                activeTab === 'swipe' 
                  ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm' 
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              Discover
            </button>
            <button
              onClick={() => setActiveTab('matches')}
              className={`px-6 py-2 rounded-md text-sm font-medium transition-all ${
                activeTab === 'matches' 
                  ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm' 
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              Matches
            </button>
          </div>
        </div>

        {/* Content Area */}
        <div className="flex-1 min-h-0 relative">
          {activeTab === 'swipe' ? <SwipeInterface /> : <MatchList />}
        </div>
      </div>
    </div>
  );
};

export default MatchmakingPage;