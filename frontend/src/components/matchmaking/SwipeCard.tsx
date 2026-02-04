import { useState } from 'react';
import { motion } from 'framer-motion';
import { Heart, X, Flag, Ban, Info } from 'lucide-react';
import type { Profile } from '../../api/profile';
import { ReportModal, BlockConfirmation } from '../safety';

interface SwipeCardProps {
  profile: Profile;
  onSwipeLeft: () => void;
  onSwipeRight: () => void;
  style?: React.CSSProperties;
}

const SwipeCard: React.FC<SwipeCardProps> = ({ profile, onSwipeLeft, onSwipeRight, style }) => {
  const [showReportModal, setShowReportModal] = useState(false);
  const [showBlockModal, setShowBlockModal] = useState(false);
  const [showInfo, setShowInfo] = useState(false);

  const getRelationshipIntentLabel = (intent: string) => {
    const labels: Record<string, string> = {
      friendship: '🤝 Friendship',
      dating: '💕 Dating',
      casual: '😊 Casual',
    };
    return labels[intent] || intent;
  };

  return (
    <>
      <div className="relative w-full h-full bg-white dark:bg-gray-800 rounded-3xl shadow-2xl overflow-hidden border border-gray-100 dark:border-gray-700" style={style}>
        {/* Main Image Area */}
        <div className="absolute inset-0 bg-gray-200 dark:bg-gray-700">
           {profile.avatar ? (
             <img src={profile.avatar} alt="Profile" className="w-full h-full object-cover" />
           ) : (
             <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-indigo-100 to-purple-100 dark:from-indigo-900 dark:to-purple-900">
               <span className="text-6xl">👤</span>
             </div>
           )}
           {/* Gradient Overlay for text readability */}
           <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent" />
        </div>

        {/* Floating Actions (Top) */}
        <div className="absolute top-4 right-4 z-10 flex gap-2">
           <button 
             onClick={(e) => { e.stopPropagation(); setShowReportModal(true); }}
             className="p-2 bg-black/20 hover:bg-black/40 backdrop-blur-md rounded-full text-white/70 hover:text-red-400 transition-colors"
           >
             <Flag size={18} />
           </button>
           <button 
             onClick={(e) => { e.stopPropagation(); setShowBlockModal(true); }}
             className="p-2 bg-black/20 hover:bg-black/40 backdrop-blur-md rounded-full text-white/70 hover:text-red-400 transition-colors"
           >
             <Ban size={18} />
           </button>
        </div>

        {/* Card Content (Bottom Glass) */}
        <div className="absolute bottom-0 left-0 right-0 p-6 text-white z-10">
           <div className="flex items-end justify-between mb-2">
             <div>
               <h2 className="text-3xl font-bold flex items-center gap-2">
                 Anonymous <span className="text-xl font-normal opacity-80">{profile.age}</span>
               </h2>
               <div className="inline-block px-3 py-1 mt-2 rounded-full bg-white/20 backdrop-blur-md text-sm font-medium border border-white/20">
                 {getRelationshipIntentLabel(profile.relationship_intent)}
               </div>
             </div>
             <button 
               onClick={(e) => { e.stopPropagation(); setShowInfo(!showInfo); }}
               className="p-2 bg-white/20 hover:bg-white/30 rounded-full transition-colors"
             >
               <Info size={24} />
             </button>
           </div>

           {/* Expanded Info Area */}
           <motion.div 
             initial={false}
             animate={{ height: showInfo ? 'auto' : 0, opacity: showInfo ? 1 : 0 }}
             className="overflow-hidden"
           >
             <div className="pt-4 pb-2 space-y-4">
               {profile.bio && <p className="text-sm opacity-90 leading-relaxed">{profile.bio}</p>}
               
               {profile.interests.length > 0 && (
                 <div className="flex flex-wrap gap-2">
                   {profile.interests.map(i => (
                     <span key={i} className="text-xs px-2 py-1 bg-indigo-500/40 rounded-md border border-indigo-400/30">#{i}</span>
                   ))}
                 </div>
               )}
             </div>
           </motion.div>

           {/* Swipe Actions */}
           <div className="flex justify-center gap-8 mt-6">
             <motion.button
               whileHover={{ scale: 1.1 }}
               whileTap={{ scale: 0.9 }}
               onClick={(e) => { e.stopPropagation(); onSwipeLeft(); }}
               className="w-16 h-16 rounded-full bg-white dark:bg-gray-800 text-red-500 shadow-xl flex items-center justify-center hover:bg-red-50 transition-colors"
             >
               <X size={32} strokeWidth={3} />
             </motion.button>
             <motion.button
               whileHover={{ scale: 1.1 }}
               whileTap={{ scale: 0.9 }}
               onClick={(e) => { e.stopPropagation(); onSwipeRight(); }}
               className="w-16 h-16 rounded-full bg-gradient-to-r from-pink-500 to-rose-500 text-white shadow-xl shadow-pink-500/40 flex items-center justify-center"
             >
               <Heart size={32} fill="currentColor" />
             </motion.button>
           </div>
        </div>
      </div>

      {showReportModal && <ReportModal reportedUserId={profile.anonymous_id} onClose={() => setShowReportModal(false)} onSuccess={onSwipeLeft} />}
      {showBlockModal && <BlockConfirmation blockedUserId={profile.anonymous_id} onClose={() => setShowBlockModal(false)} onSuccess={onSwipeLeft} />}
    </>
  );
};

export default SwipeCard;