import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Search, Clock, Pin, User, MessageSquare } from 'lucide-react';

interface SearchResult {
  id: string;
  chatroom: string | null;
  chatroom_name: string | null;
  match_id: string | null;
  sender_id: string;
  content: string;
  highlighted_content: string;
  message_type: string;
  is_pinned: boolean;
  created_at: string;
}

interface SearchResultsProps {
  query: string;
  results: SearchResult[];
  count: number;
  loading?: boolean;
  onResultClick?: (result: SearchResult) => void;
}

const SearchResults: React.FC<SearchResultsProps> = ({
  query,
  results,
  count,
  loading = false,
  onResultClick,
}) => {
  const navigate = useNavigate();

  const handleResultClick = (result: SearchResult) => {
    if (onResultClick) {
      onResultClick(result);
    } else {
      if (result.chatroom) {
        navigate(`/chat/${result.chatroom}`, { state: { messageId: result.id } });
      } else if (result.match_id) {
        navigate(`/matchmaking`, { state: { matchId: result.match_id, messageId: result.id } });
      }
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  // Loading State
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-full py-12">
        <div className="w-10 h-10 border-4 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin mb-4" />
        <p className="text-gray-500 dark:text-gray-400 animate-pulse">Searching the archives...</p>
      </div>
    );
  }

  // Empty State (Initial)
  if (!query) {
    return (
      <div className="flex flex-col items-center justify-center h-full py-12 text-gray-400 dark:text-gray-500">
        <div className="bg-gray-100 dark:bg-white/5 p-4 rounded-full mb-4">
          <Search size={32} />
        </div>
        <p className="text-lg font-medium text-gray-600 dark:text-gray-300">Start typing to search</p>
        <p className="text-sm">Find messages, specific users, or topics.</p>
      </div>
    );
  }

  // No Results
  if (count === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full py-12 text-gray-400 dark:text-gray-500">
        <div className="bg-red-50 dark:bg-red-900/10 p-4 rounded-full mb-4 text-red-400">
          <Search size={32} />
        </div>
        <p className="text-lg font-medium text-gray-600 dark:text-gray-300">No results found</p>
        <p className="text-sm">We couldn't find anything matching "{query}"</p>
      </div>
    );
  }

  // Results List
  return (
    <div className="p-4">
      <div className="mb-4 px-2 flex items-center justify-between text-xs font-semibold text-gray-500 uppercase tracking-wider">
        <span>{count} result{count !== 1 ? 's' : ''} found</span>
      </div>
      
      <div className="space-y-2">
        {results.map((result, index) => (
          <motion.div
            key={result.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            onClick={() => handleResultClick(result)}
            className="group p-4 bg-white dark:bg-white/5 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 border border-gray-100 dark:border-white/10 hover:border-indigo-200 dark:hover:border-indigo-500/30 rounded-xl cursor-pointer transition-all duration-200"
          >
            {/* Header: Location & Time */}
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-1.5 text-xs font-medium text-indigo-600 dark:text-indigo-400">
                {result.match_id ? <User size={12}/> : <MessageSquare size={12}/>}
                <span>{result.chatroom_name || 'Private Chat'}</span>
              </div>
              <div className="flex items-center gap-1 text-[10px] text-gray-400">
                <Clock size={10} />
                {formatDate(result.created_at)}
              </div>
            </div>

            {/* Content Highlight */}
            <div 
              className="text-sm text-gray-800 dark:text-gray-200 line-clamp-2 leading-relaxed [&>em]:not-italic [&>em]:bg-yellow-200/50 [&>em]:dark:bg-yellow-500/30 [&>em]:text-yellow-800 [&>em]:dark:text-yellow-200 [&>em]:px-0.5 [&>em]:rounded"
              dangerouslySetInnerHTML={{ __html: result.highlighted_content }}
            />

            {/* Footer: Sender & Badges */}
            <div className="flex items-center gap-3 mt-3 pt-3 border-t border-gray-100 dark:border-white/5">
               <div className="flex items-center gap-1.5 text-xs text-gray-500">
                 <div className="w-5 h-5 rounded-full bg-gradient-to-tr from-gray-200 to-gray-300 dark:from-gray-700 dark:to-gray-600 flex items-center justify-center text-[8px] font-bold text-gray-600 dark:text-gray-300">
                   {result.sender_id.slice(0, 2)}
                 </div>
                 <span>{result.sender_id.slice(0, 8)}...</span>
               </div>
               
               {result.is_pinned && (
                 <span className="flex items-center gap-1 text-[10px] bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-500 px-1.5 py-0.5 rounded-full font-medium">
                   <Pin size={8} /> Pinned
                 </span>
               )}
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default SearchResults;