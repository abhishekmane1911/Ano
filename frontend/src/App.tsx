import { BrowserRouter as Router, Routes, Route, Navigate, useLocation, Link } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { MessageCircle, Shield, ArrowRight, Star } from 'lucide-react';
import { useEffect } from 'react';
import { useAuthStore } from './stores/authStore';
import { Navigation, ToastContainer, PageTransition } from './components/common';
import { useToastStore } from './hooks/useToast';
import LandingPage from './components/auth/LandingPage';
import SignupForm from './components/auth/SignupForm';
import LoginForm from './components/auth/LoginForm';
import EmailVerification from './components/auth/EmailVerification';
import PasswordResetRequest from './components/auth/PasswordResetRequest';
import PasswordResetConfirm from './components/auth/PasswordResetConfirm';

import ProfileEditor from './components/profile/ProfileEditor';
import ChatPage from './components/chat/ChatPage';
import { SafetySettings } from './components/safety';
import { AdminDashboard } from './components/admin';
import ReputationDemo from './components/reputation/ReputationDemo';
import { ReputationStats } from './components/reputation/ReputationComponents';
import { useReputationStore } from './stores/reputationStore';
import { reputationApi } from './api/reputation';
import { profileAPI } from './api/profile';
import { reportsAPI } from './api/reports';
import { useChatStore } from './stores/chatStore';
import { useProfileStore } from './stores/profileStore';
import './App.css';

// Protected route component
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated } = useAuthStore();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
};

// Admin-only route component
const AdminRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated, user } = useAuthStore();

  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  if (!user?.isAdmin) {
    return <Navigate to="/" />;
  }

  return <>{children}</>;
};

// Public route component (redirect to home if already authenticated)
const PublicRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated } = useAuthStore();
  return !isAuthenticated ? <>{children}</> : <Navigate to="/" />;
};

function AnimatedRoutes() {
  const location = useLocation();
  const { isAuthenticated, user } = useAuthStore();
  const { myReputation, setMyReputation } = useReputationStore();
  const { profile, setProfile } = useProfileStore();
  const { setBlockedUsers } = useChatStore();

  useEffect(() => {
    if (isAuthenticated) {
      if (!myReputation) {
        reputationApi.getMyReputation().then(setMyReputation).catch(() => { });
      }
      if (!profile) {
        profileAPI.getMyProfile().then(setProfile).catch(() => { });
      }
      reportsAPI.getBlockedUsers().then((blocks) => {
        setBlockedUsers(blocks.map(b => b.anonymous_id));
      }).catch(() => { });
    }
  }, [isAuthenticated, myReputation, setMyReputation, profile, setProfile, setBlockedUsers]);

  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        {/* Public routes */}
        <Route path="/landing" element={<PublicRoute><PageTransition><LandingPage /></PageTransition></PublicRoute>} />
        <Route path="/signup" element={<PublicRoute><PageTransition><SignupForm /></PageTransition></PublicRoute>} />
        <Route path="/login" element={<PublicRoute><PageTransition><LoginForm /></PageTransition></PublicRoute>} />
        <Route path="/verify-email" element={<PageTransition><EmailVerification /></PageTransition>} />
        <Route path="/password-reset" element={<PageTransition><PasswordResetRequest /></PageTransition>} />
        <Route path="/password-reset-confirm" element={<PageTransition><PasswordResetConfirm /></PageTransition>} />

        {/* Protected routes */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <PageTransition>
                <div className="min-h-screen bg-slate-50 dark:bg-slate-950 pt-24 pb-12 px-4 md:px-8 flex flex-col items-center font-sans">
                  <div className="w-full max-w-5xl">


                    <div className="mb-8">
                      <h1 className="text-2xl font-semibold text-slate-900 dark:text-white tracking-tight">
                        Dashboard
                      </h1>
                      <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                        Welcome back. Here is your overview.
                      </p>
                    </div>

                    {/* Reputation Panel */}
                    <div className="mb-8 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-sm">
                      {/* <h2 className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-6">
                        Reputation Overview
                      </h2> */}
                      {myReputation ? (
                        <ReputationStats data={{
                          score: myReputation.reputation_score,
                          tier: myReputation.rank_tier,
                          level: myReputation.level,
                          xpForNextLevel: myReputation.xp_for_next_level,
                          totalUpvotesReceived: myReputation.total_upvotes_received,
                          totalDownvotesReceived: myReputation.total_downvotes_received,
                        }} />
                      ) : (
                        <div className="text-sm text-slate-400 dark:text-slate-500 animate-pulse py-4">
                          Loading statistics...
                        </div>
                      )}
                    </div>

                    {/* Action Modules */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {/* Chat Module */}
                      <Link to="/chat" className="group block h-full">
                        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-sm hover:border-blue-500/50 dark:hover:border-blue-500/50 transition-colors h-full flex flex-col">
                          <div className="w-10 h-10 bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 rounded-lg flex items-center justify-center mb-4">
                            <MessageCircle size={20} strokeWidth={2} />
                          </div>
                          <h3 className="font-medium text-slate-900 dark:text-white mb-1">Chatrooms</h3>
                          <p className="text-sm text-slate-500 dark:text-slate-400 flex-1">
                            Join live public discussions and connect with others.
                          </p>
                          <div className="mt-4 flex items-center text-sm text-blue-600 dark:text-blue-400 font-medium group-hover:gap-1.5 transition-all">
                            Open <ArrowRight size={16} className="ml-1" />
                          </div>
                        </div>
                      </Link>

                      {/* Safety Module */}
                      <Link to="/safety" className="group block h-full">
                        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-sm hover:border-slate-400 dark:hover:border-slate-600 transition-colors h-full flex flex-col">
                          <div className="w-10 h-10 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 rounded-lg flex items-center justify-center mb-4">
                            <Shield size={20} strokeWidth={2} />
                          </div>
                          <h3 className="font-medium text-slate-900 dark:text-white mb-1">Safety & Privacy</h3>
                          <p className="text-sm text-slate-500 dark:text-slate-400 flex-1">
                            Review guidelines and manage your blocks and reports.
                          </p>
                        </div>
                      </Link>

                      {/* Reputation Info Module */}
                      <Link to="/reputation-demo" className="group block h-full">
                        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-sm hover:border-slate-400 dark:hover:border-slate-600 transition-colors h-full flex flex-col">
                          <div className="w-10 h-10 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 rounded-lg flex items-center justify-center mb-4">
                            <Star size={20} strokeWidth={2} />
                          </div>
                          <h3 className="font-medium text-slate-900 dark:text-white mb-1">Reputation Rules</h3>
                          <p className="text-sm text-slate-500 dark:text-slate-400 flex-1">
                            Learn how the leveling and progression system works.
                          </p>
                        </div>
                      </Link>
                    </div>

                  </div>
                </div>
                {/* --- END DASHBOARD UI --- */}
              </PageTransition>
            </ProtectedRoute>
          }
        />

        <Route path="/profile" element={<ProtectedRoute><PageTransition><ProfileEditor /></PageTransition></ProtectedRoute>} />
        <Route path="/chat" element={<ProtectedRoute><PageTransition><ChatPage /></PageTransition></ProtectedRoute>} />
        <Route path="/chat/:roomId" element={<ProtectedRoute><PageTransition><ChatPage /></PageTransition></ProtectedRoute>} />
        <Route path="/safety" element={<ProtectedRoute><PageTransition><SafetySettings /></PageTransition></ProtectedRoute>} />
        <Route path="/admin" element={<AdminRoute><PageTransition><AdminDashboard /></PageTransition></AdminRoute>} />
        <Route path="/reputation-demo" element={<ProtectedRoute><PageTransition><ReputationDemo /></PageTransition></ProtectedRoute>} />

        {/* Default redirect */}
        <Route path="*" element={isAuthenticated ? <Navigate to="/" replace /> : <Navigate to="/landing" replace />} />
      </Routes>
    </AnimatePresence>
  );
}

function App() {
  const { toasts, removeToast } = useToastStore();
  const { isLoading } = useAuthStore();
  const location = useLocation();

  const noNavbarPages = ['/landing', '/signup', '/login', '/password-reset', '/password-reset-confirm'];
  const fullHeightPages = ['/chat'];
  const needsNavbarPadding = !noNavbarPages.includes(location.pathname);
  const needsFullHeight = fullHeightPages.some(page => location.pathname.startsWith(page));

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-950">
        <div className="flex flex-col items-center gap-4">
          <div className="animate-spin rounded-full h-8 w-8 border-[3px] border-slate-200 border-t-blue-600 dark:border-slate-800 dark:border-t-blue-500"></div>
          <p className="text-sm text-slate-500 dark:text-slate-400 font-medium">Loading workspace...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <Navigation />
      <main className={needsFullHeight ? 'main-content-full-height' : (needsNavbarPadding ? 'main-content' : '')}>
        <AnimatedRoutes />
      </main>
      <ToastContainer toasts={toasts} onClose={removeToast} />
    </>
  );
}

function AppWrapper() {
  return (
    <Router>
      <App />
    </Router>
  );
}

export default AppWrapper;