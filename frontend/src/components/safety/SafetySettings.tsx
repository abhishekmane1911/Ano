import { useEffect, useState } from 'react';
import { ShieldAlert, ShieldCheck, Unlock, Loader2, RefreshCcw } from 'lucide-react';
import { reportsAPI } from '../../api/reports';
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
      const users = await reportsAPI.getBlockedUsers();
      setBlockedUsers(users || []);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to load blocked users.');
      setBlockedUsers([]);
    } finally {
      setLoading(false);
    }
  };

  const handleUnblock = async (anonymousId: string) => {
    if (!confirm('Are you sure you want to unblock this user? They will be able to interact with you again.')) return;

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

  const formatDate = (dateString: string) =>
    new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });

  return (
    <div className="min-h-screen w-full bg-zinc-950 pt-24 pb-12 px-4 sm:px-6 md:px-8 font-sans">
      <div className="w-full max-w-5xl mx-auto">

        {/* Header Section */}
        <div className="mb-8 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-xl font-semibold text-zinc-50 tracking-tight">
              Safety & Privacy
            </h1>
            <p className="text-sm text-zinc-400 mt-1">
              Manage your block list and review community guidelines.
            </p>
          </div>

          <button
            onClick={loadBlockedUsers}
            disabled={loading}
            className="inline-flex items-center justify-center gap-2 px-3 py-2 bg-zinc-900 border border-zinc-800 hover:border-zinc-700 text-zinc-300 rounded-lg text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
          >
            <RefreshCcw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

          {/* Main Blocked Users Panel */}
          <div className="md:col-span-2">
            <div className="bg-zinc-900 border border-zinc-800 rounded-xl shadow-sm overflow-hidden flex flex-col h-full">
              <div className="px-5 py-4 border-b border-zinc-800 bg-zinc-900/50 flex items-center justify-between">
                <h2 className="text-sm font-medium text-zinc-50">Blocked Users</h2>
                <span className="bg-zinc-800 text-zinc-400 text-xs font-medium px-2 py-0.5 rounded-full">
                  {blockedUsers.length}
                </span>
              </div>

              <div className="flex-1">
                {loading ? (
                  <div className="p-5 flex flex-col items-center justify-center h-48 text-zinc-500">
                    <Loader2 className="w-6 h-6 animate-spin mb-3 text-zinc-600" />
                    <span className="text-sm font-medium">Loading block list...</span>
                  </div>
                ) : error ? (
                  <div className="p-8 flex flex-col items-center text-center">
                    <div className="w-10 h-10 bg-red-500/10 text-red-500 rounded-full flex items-center justify-center mb-3">
                      <ShieldAlert className="w-5 h-5" />
                    </div>
                    <p className="text-sm font-medium text-zinc-100">{error}</p>
                    <button
                      onClick={loadBlockedUsers}
                      className="mt-4 text-sm font-medium text-blue-500 hover:underline"
                    >
                      Try again
                    </button>
                  </div>
                ) : blockedUsers.length === 0 ? (
                  <div className="p-12 flex flex-col items-center text-center">
                    <div className="w-12 h-12 bg-zinc-800/50 border border-zinc-800 text-zinc-500 rounded-full flex items-center justify-center mb-4">
                      <ShieldCheck className="w-6 h-6" />
                    </div>
                    <p className="text-sm font-medium text-zinc-100">
                      No blocked users
                    </p>
                    <p className="text-sm text-zinc-400 mt-1">
                      Your block list is completely empty.
                    </p>
                  </div>
                ) : (
                  <ul className="divide-y divide-zinc-800">
                    {blockedUsers.map((block) => (
                      <li
                        key={block.id}
                        className="flex items-center justify-between gap-4 p-5 hover:bg-zinc-800/40 transition-colors"
                      >
                        <div className="min-w-0 flex-1">
                          <p className="text-sm font-medium text-zinc-100 truncate">
                            Anonymous User
                          </p>
                          <div className="mt-1 flex items-center gap-2 text-xs text-zinc-500">
                            <span className="font-mono truncate">{block.anonymous_id}</span>
                            <span>•</span>
                            <span>{formatDate(block.blocked_at)}</span>
                          </div>
                        </div>

                        <button
                          onClick={() => handleUnblock(block.anonymous_id)}
                          disabled={unblockingId === block.anonymous_id}
                          className="flex-shrink-0 inline-flex items-center gap-1.5 px-3 py-1.5 bg-zinc-900 border border-zinc-700 hover:border-zinc-600 hover:text-red-400 text-zinc-300 rounded-md text-xs font-medium transition-colors disabled:opacity-50 shadow-sm"
                        >
                          {unblockingId === block.anonymous_id ? (
                            <Loader2 className="w-3.5 h-3.5 animate-spin" />
                          ) : (
                            <Unlock className="w-3.5 h-3.5" />
                          )}
                          Unblock
                        </button>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
          </div>

          {/* Guidelines Sidebar */}
          <div className="md:col-span-1">
            <div className="bg-zinc-900 border border-zinc-800 rounded-xl shadow-sm overflow-hidden h-fit">
              <div className="px-5 py-4 border-b border-zinc-800 bg-zinc-900/50">
                <h2 className="text-sm font-medium text-zinc-50">Community Guidelines</h2>
              </div>

              <div className="p-5 space-y-4">
                <div className="bg-zinc-800/50 p-3.5 rounded-lg border border-zinc-800/60">
                  <h3 className="text-sm font-medium text-zinc-100 mb-1">
                    Stay anonymous
                  </h3>
                  <p className="text-xs text-zinc-400 leading-relaxed">
                    Avoid sharing personal details like your real name, phone number, or specific location.
                  </p>
                </div>

                <div className="bg-zinc-800/50 p-3.5 rounded-lg border border-zinc-800/60">
                  <h3 className="text-sm font-medium text-zinc-100 mb-1">
                    Report behavior
                  </h3>
                  <p className="text-xs text-zinc-400 leading-relaxed">
                    If someone crosses a line or violates the rules, report and block them immediately.
                  </p>
                </div>

                <div className="bg-zinc-800/50 p-3.5 rounded-lg border border-zinc-800/60">
                  <h3 className="text-sm font-medium text-zinc-100 mb-1">
                    Be respectful
                  </h3>
                  <p className="text-xs text-zinc-400 leading-relaxed">
                    Harassment, abuse, bullying, and hate speech are strictly prohibited and will result in bans.
                  </p>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default SafetySettings;