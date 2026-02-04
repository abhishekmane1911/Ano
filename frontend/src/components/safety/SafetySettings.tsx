import { useEffect, useState } from 'react';
// Minimized icons
import { RefreshCw } from 'lucide-react'; 
import { reportsAPI } from '../../api/reports';
import { useAuthStore } from '../../stores/authStore';
import type { Block } from '../../api/reports';

const SafetySettings: React.FC = () => {
  const [blockedUsers, setBlockedUsers] = useState<Block[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [unblockingId, setUnblockingId] = useState<string | null>(null);

  useEffect(() => {
    loadBlockedUsers();
  }, []);

  const loadBlockedUsers = async () => {
    setLoading(true);
    setError(null);
    try {
      console.log('Loading blocked users...');
      console.log('Auth token:', useAuthStore.getState().accessToken ? 'Present' : 'Missing');
      
      const users = await reportsAPI.getBlockedUsers();
      console.log('Blocked users response:', users);
      console.log('Response type:', typeof users);
      console.log('Is array?', Array.isArray(users));
      console.log('Users length:', users?.length);
      
      setBlockedUsers(users || []);
    } catch (err: any) {
      console.error('Error loading blocked users:', err);
      console.error('Error response:', err.response?.data);
      console.error('Error status:', err.response?.status);
      setError(err.response?.data?.error || 'Failed to load blocked users');
      setBlockedUsers([]);
    } finally {
      setLoading(false);
    }
  };

  const handleUnblock = async (anonymousId: string) => {
    if (!confirm('Are you sure you want to unblock this user?')) return;
    setUnblockingId(anonymousId);
    try {
      await reportsAPI.unblockUser(anonymousId);
      setBlockedUsers((prev) => prev.filter((block) => block.anonymous_id !== anonymousId));
    } catch (err: any) {
      alert(err.response?.data?.error || 'Failed to unblock user.');
    } finally {
      setUnblockingId(null);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    // ADDED pt-24 to fix top overlap
    <div className="min-h-screen bg-[#f3f4f6] dark:bg-[#0f172a] pt-24 pb-12">
      <div className="max-w-4xl mx-auto px-4">
        
        {/* Header - Simple & Professional */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Safety & Privacy</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Manage your blocked accounts and review community guidelines.
          </p>
        </div>

        <div className="space-y-6">
          {/* Blocked Users Section - Clean Card */}
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center bg-gray-50/50 dark:bg-gray-800/50">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                Blocked Users
              </h2>
              <button
                onClick={loadBlockedUsers}
                disabled={loading}
                className="text-gray-500 hover:text-gray-700 dark:text-gray-400 transition-colors"
                title="Refresh list"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              </button>
            </div>

            <div className="p-0">
              {loading ? (
                <div className="p-8 text-center text-gray-500 text-sm">Loading...</div>
              ) : error ? (
                <div className="p-8 text-center">
                  <p className="text-red-600 text-sm mb-2">{error}</p>
                  <button onClick={loadBlockedUsers} className="text-indigo-600 text-sm hover:underline">Try Again</button>
                </div>
              ) : blockedUsers.length === 0 ? (
                <div className="p-12 text-center">
                  <p className="text-gray-900 dark:text-white font-medium mb-1">No blocked users</p>
                  <p className="text-sm text-gray-500">You haven't blocked anyone yet.</p>
                </div>
              ) : (
                <div className="divide-y divide-gray-100 dark:divide-gray-700">
                  {blockedUsers.map((block) => (
                    <div key={block.id} className="flex items-center justify-between p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                      <div className="flex flex-col">
                        <span className="font-medium text-gray-900 dark:text-white text-sm">Anonymous User</span>
                        <span className="text-xs text-gray-500 font-mono mt-0.5">{block.anonymous_id}</span>
                        <span className="text-xs text-gray-400 mt-1">Blocked on {formatDate(block.blocked_at)}</span>
                      </div>
                      <button
                        onClick={() => handleUnblock(block.anonymous_id)}
                        disabled={unblockingId === block.anonymous_id}
                        className="px-3 py-1.5 text-xs font-medium text-red-600 bg-red-50 hover:bg-red-100 dark:bg-red-900/20 dark:text-red-400 dark:hover:bg-red-900/30 rounded-md transition-colors"
                      >
                        {unblockingId === block.anonymous_id ? 'Wait...' : 'Unblock'}
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Safety Tips - Simplified to text list */}
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Community Guidelines
            </h2>
            <ul className="space-y-4">
              <li className="flex gap-3">
                <span className="flex-shrink-0 w-1.5 h-1.5 rounded-full bg-indigo-500 mt-2"/>
                <div>
                  <h3 className="text-sm font-medium text-gray-900 dark:text-white">Stay Anonymous</h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">Never share personal information like your real name, phone number, or address in public rooms.</p>
                </div>
              </li>
              <li className="flex gap-3">
                <span className="flex-shrink-0 w-1.5 h-1.5 rounded-full bg-indigo-500 mt-2"/>
                <div>
                  <h3 className="text-sm font-medium text-gray-900 dark:text-white">Report Behavior</h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">If someone makes you uncomfortable, use the report feature immediately.</p>
                </div>
              </li>
              <li className="flex gap-3">
                <span className="flex-shrink-0 w-1.5 h-1.5 rounded-full bg-indigo-500 mt-2"/>
                <div>
                  <h3 className="text-sm font-medium text-gray-900 dark:text-white">Be Respectful</h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">Treat everyone with respect. Harassment and hate speech are not tolerated.</p>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SafetySettings;