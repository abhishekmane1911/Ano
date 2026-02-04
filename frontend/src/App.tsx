import { BrowserRouter as Router, Routes, Route, Navigate, useLocation, Link } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { MessageCircle, Users, Shield, ArrowRight } from 'lucide-react'; // Added icons
import { useAuthStore } from './stores/authStore';
import { Navigation, ToastContainer, PageTransition } from './components/common';
import { useToastStore } from './hooks/useToast';
import LandingPage from './components/auth/LandingPage';
import SignupForm from './components/auth/SignupForm';
import LoginForm from './components/auth/LoginForm';
import EmailVerification from './components/auth/EmailVerification';
import PasswordResetRequest from './components/auth/PasswordResetRequest';
import PasswordResetConfirm from './components/auth/PasswordResetConfirm';
import ProfileCreation from './components/profile/ProfileCreation';
import ProfileEditor from './components/profile/ProfileEditor';
import ChatPage from './components/chat/ChatPage';
// import { MatchmakingPage, MatchChat } from './components/matchmaking';
import { SafetySettings } from './components/safety';
import { AdminDashboard } from './components/admin';
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

  console.log('Current route:', location.pathname);
  console.log('Is authenticated:', isAuthenticated);
  console.log('User:', user);

  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        {/* Public routes */}
        <Route
          path="/landing"
          element={
            <PublicRoute>
              <PageTransition>
                <LandingPage />
              </PageTransition>
            </PublicRoute>
          }
        />
        <Route
          path="/signup"
          element={
            <PublicRoute>
              <PageTransition>
                <SignupForm />
              </PageTransition>
            </PublicRoute>
          }
        />
        <Route
          path="/login"
          element={
            <PublicRoute>
              <PageTransition>
                <LoginForm />
              </PageTransition>
            </PublicRoute>
          }
        />
        <Route
          path="/verify-email"
          element={
            <PageTransition>
              <EmailVerification />
            </PageTransition>
          }
        />
        <Route
          path="/password-reset"
          element={
            <PublicRoute>
              <PageTransition>
                <PasswordResetRequest />
              </PageTransition>
            </PublicRoute>
          }
        />
        <Route
          path="/password-reset-confirm"
          element={
            <PublicRoute>
              <PageTransition>
                <PasswordResetConfirm />
              </PageTransition>
            </PublicRoute>
          }
        />

        {/* Protected routes */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <PageTransition>
                {/* --- MODERNIZED DASHBOARD UI --- */}
                <div className="min-h-screen bg-[#f3f4f6] dark:bg-[#0f172a] pt-24 pb-12 px-4 flex flex-col items-center">
                  
                  {/* Background Accents */}
                  <div className="fixed inset-0 overflow-hidden pointer-events-none">
                    <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-purple-500/5 rounded-full blur-[100px]" />
                    <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-indigo-500/5 rounded-full blur-[100px]" />
                  </div>

                  <div className="w-full max-w-5xl relative z-10">
                    
                    {/* Welcome Header */}
                    <motion.div 
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="text-center mb-12"
                    >
                      <h1 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-4 tracking-tight">
                        Welcome to <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600">Ano</span>
                      </h1>
                      <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
                        Your private space for anonymous connections. Join conversations, discover new friends, and be yourself.
                      </p>
                    </motion.div>

                    {/* Action Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
                      
                      {/* Chat Room Card */}
                      <Link to="/chat" className="group">
                        <motion.div 
                          whileHover={{ y: -5 }}
                          className="h-full bg-white dark:bg-gray-800 rounded-3xl p-8 border border-gray-200 dark:border-gray-700 shadow-xl hover:shadow-2xl hover:border-indigo-500/30 transition-all duration-300 relative overflow-hidden"
                        >
                          <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/10 rounded-full blur-3xl -mr-16 -mt-16 transition-all group-hover:bg-blue-500/20" />
                          
                          <div className="relative z-10">
                            <div className="w-14 h-14 bg-blue-100 dark:bg-blue-900/30 rounded-2xl flex items-center justify-center text-blue-600 dark:text-blue-400 mb-6 group-hover:scale-110 transition-transform duration-300">
                              <MessageCircle size={28} />
                            </div>
                            <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Public Chatrooms</h3>
                            <p className="text-gray-500 dark:text-gray-400 mb-6 line-clamp-2">
                              Jump into lively discussions. Share thoughts and connect with the community in real-time.
                            </p>
                            <div className="flex items-center gap-2 text-blue-600 dark:text-blue-400 font-semibold group-hover:gap-3 transition-all">
                              Start Chatting <ArrowRight size={18} />
                            </div>
                          </div>
                        </motion.div>
                      </Link>

                      {/* Matchmaking Card (Coming Soon / Disabled style if needed) */}
                      {/* Note: Kept link active as per original code, but styled appropriately */}
                      {/* <Link to="/matchmaking" className="group">
                        <motion.div 
                          whileHover={{ y: -5 }}
                          className="h-full bg-white dark:bg-gray-800 rounded-3xl p-8 border border-gray-200 dark:border-gray-700 shadow-xl hover:shadow-2xl hover:border-purple-500/30 transition-all duration-300 relative overflow-hidden"
                        >
                          <div className="absolute top-0 right-0 w-32 h-32 bg-purple-500/10 rounded-full blur-3xl -mr-16 -mt-16 transition-all group-hover:bg-purple-500/20" />
                          
                          <div className="relative z-10">
                            <div className="w-14 h-14 bg-purple-100 dark:bg-purple-900/30 rounded-2xl flex items-center justify-center text-purple-600 dark:text-purple-400 mb-6 group-hover:scale-110 transition-transform duration-300">
                              <Users size={28} />
                            </div>
                            <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Smart Matchmaking</h3>
                            <p className="text-gray-500 dark:text-gray-400 mb-6 line-clamp-2">
                              Discover people who share your interests and hobbies. Swipe to find your vibe.
                            </p>
                            <div className="flex items-center gap-2 text-purple-600 dark:text-purple-400 font-semibold group-hover:gap-3 transition-all">
                              Find Matches <ArrowRight size={18} />
                            </div>
                          </div>
                        </motion.div>
                      </Link> */}
                      
                      {/* Placeholder for when matchmaking is disabled or just to fill grid */}
                      <div className="group relative">
                         <motion.div 
                          className="h-full bg-white dark:bg-gray-800/50 rounded-3xl p-8 border border-gray-200 dark:border-gray-700/50 shadow-sm relative overflow-hidden opacity-60 grayscale hover:grayscale-0 transition-all cursor-not-allowed"
                        >
                          <div className="w-14 h-14 bg-gray-100 dark:bg-gray-700 rounded-2xl flex items-center justify-center text-gray-400 mb-6">
                              <Users size={28} />
                          </div>
                          <h3 className="text-2xl font-bold text-gray-400 dark:text-gray-500 mb-2">Matchmaking</h3>
                          <p className="text-gray-400 dark:text-gray-500 mb-4">
                            Temporarily unavailable while we improve the matching algorithm.
                          </p>
                          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-500">Coming Soon</span>
                        </motion.div>
                      </div>

                    </div>

                    {/* Safety Banner */}
                    <div className="mt-12 max-w-4xl mx-auto">
                      <Link to="/safety">
                        <motion.div 
                          whileHover={{ scale: 1.01 }}
                          className="bg-indigo-900/5 dark:bg-indigo-900/20 border border-indigo-100 dark:border-indigo-900/50 rounded-2xl p-6 flex items-center justify-between group cursor-pointer"
                        >
                          <div className="flex items-center gap-4">
                            <div className="p-3 bg-indigo-100 dark:bg-indigo-900/50 rounded-xl text-indigo-600 dark:text-indigo-400">
                              <Shield size={24} />
                            </div>
                            <div>
                              <h4 className="font-semibold text-gray-900 dark:text-white">Your Safety Matters</h4>
                              <p className="text-sm text-gray-600 dark:text-gray-400">Review our community guidelines and safety tools.</p>
                            </div>
                          </div>
                          <ArrowRight size={20} className="text-gray-400 group-hover:text-indigo-500 transition-colors" />
                        </motion.div>
                      </Link>
                    </div>

                  </div>
                </div>
                {/* --- END DASHBOARD UI --- */}
              </PageTransition>
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile/create"
          element={
            <ProtectedRoute>
              <PageTransition>
                <ProfileCreation />
              </PageTransition>
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile/edit"
          element={
            <ProtectedRoute>
              <PageTransition>
                <ProfileEditor />
              </PageTransition>
            </ProtectedRoute>
          }
        />
        <Route
          path="/chat"
          element={
            <ProtectedRoute>
              <PageTransition>
                <ChatPage />
              </PageTransition>
            </ProtectedRoute>
          }
        />
        {/* Matchmaking routes kept commented out as in original */}
        {/* <Route
          path="/matchmaking"
          element={
            <ProtectedRoute>
              <PageTransition>
                <MatchmakingPage />
              </PageTransition>
            </ProtectedRoute>
          }
        /> */}
        {/* <Route
          path="/matches/:matchId/chat"
          element={
            <ProtectedRoute>
              <PageTransition>
                <MatchChat />
              </PageTransition>
            </ProtectedRoute>
          }
        /> */}
        <Route
          path="/safety"
          element={
            <ProtectedRoute>
              <PageTransition>
                <SafetySettings />
              </PageTransition>
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin"
          element={
            <AdminRoute>
              <PageTransition>
                <AdminDashboard />
              </PageTransition>
            </AdminRoute>
          }
        />

        {/* Default redirect */}
        <Route 
          path="*" 
          element={
            isAuthenticated ? (
              <Navigate to="/" replace />
            ) : (
              <Navigate to="/landing" replace />
            )
          } 
        />
      </Routes>
    </AnimatePresence>
  );
}

function App() {
  const { toasts, removeToast } = useToastStore();
  const { isLoading } = useAuthStore();
  const location = useLocation();
  
  // Logic remains unchanged
  const noNavbarPages = ['/landing', '/signup', '/login', '/password-reset', '/password-reset-confirm'];
  const fullHeightPages = ['/chat'];
  const needsNavbarPadding = !noNavbarPages.includes(location.pathname);
  const needsFullHeight = fullHeightPages.some(page => location.pathname.startsWith(page));

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#f3f4f6] dark:bg-[#0f172a]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-indigo-500/30 border-t-indigo-500 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400 font-medium">Loading...</p>
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