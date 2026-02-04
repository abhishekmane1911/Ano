import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { MessageCircle } from 'lucide-react';
import type { Match } from '../../api/matchmaking';

interface MatchNotificationProps {
  match: Match;
  onClose: () => void;
}

const MatchNotification: React.FC<MatchNotificationProps> = ({ match, onClose }) => {
  const navigate = useNavigate();

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/80 backdrop-blur-md p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.8, y: 50 }}
        animate={{ scale: 1, y: 0 }}
        exit={{ scale: 0.8, y: 50 }}
        className="w-full max-w-sm bg-white dark:bg-gray-800 rounded-3xl shadow-2xl overflow-hidden relative"
        onClick={e => e.stopPropagation()}
      >
        {/* Background Sparkles (CSS or SVG) could go here */}
        
        <div className="p-8 text-center">
          <motion.div 
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", delay: 0.2 }}
            className="w-24 h-24 mx-auto bg-gradient-to-tr from-pink-500 to-orange-500 rounded-full flex items-center justify-center text-4xl shadow-lg shadow-pink-500/30 mb-6"
          >
            🎉
          </motion.div>

          <h2 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-pink-500 to-orange-500 mb-2">It's a Match!</h2>
          <p className="text-gray-500 dark:text-gray-400 mb-8">You and this person liked each other.</p>

          <div className="flex flex-col gap-3">
            <button 
              onClick={() => { onClose(); navigate(`/matches/${match.id}/chat`); }}
              className="w-full py-3.5 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl font-bold shadow-lg shadow-indigo-500/30 flex items-center justify-center gap-2 hover:scale-105 transition-transform"
            >
              <MessageCircle size={20} /> Say Hello
            </button>
            <button 
              onClick={onClose}
              className="w-full py-3.5 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-xl font-bold hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
            >
              Keep Swiping
            </button>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default MatchNotification;