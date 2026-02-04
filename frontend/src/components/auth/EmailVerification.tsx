import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Mail, CheckCircle2, XCircle, Loader2, ArrowLeft, RefreshCw } from 'lucide-react';
import { authAPI } from '../../api/auth';
import { useAuthStore } from '../../stores/authStore';

const EmailVerification = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { user, setUser } = useAuthStore();
  const [status, setStatus] = useState<'verifying' | 'success' | 'error' | 'pending'>('pending');
  const [message, setMessage] = useState('');
  const [isResending, setIsResending] = useState(false);

  useEffect(() => {
    const token = searchParams.get('token');
    if (token) {
      verifyEmail(token);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  const verifyEmail = async (token: string) => {
    setStatus('verifying');
    
    try {
      await authAPI.verifyEmail({ token });
      setStatus('success');
      setMessage('Email verified successfully!');

      if (user) {
        setUser({ ...user, isVerified: true });
      }

      setTimeout(() => {
        navigate('/profile/create');
      }, 2000);
    } catch (err: any) {
      setStatus('error');
      const errorMsg = err.response?.data?.error?.message || 'Verification link invalid or expired.';
      setMessage(errorMsg);
    }
  };

  const handleResendVerification = async () => {
    if (!user?.email) return;

    setIsResending(true);
    try {
      // Placeholder for resend logic
      // await authAPI.resendVerification(user.email);
      setMessage('Verification email resent! Please check your inbox.');
    } catch {
      setMessage('Failed to resend. Please try again later.');
    } finally {
      setIsResending(false);
    }
  };

  // Helper to render content based on status
  const renderContent = () => {
    switch (status) {
      case 'verifying':
        return (
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-center py-8"
          >
            <div className="relative w-20 h-20 mx-auto mb-6">
              <div className="absolute inset-0 border-4 border-indigo-100 dark:border-indigo-900 rounded-full"></div>
              <div className="absolute inset-0 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
              <Loader2 className="absolute inset-0 m-auto text-indigo-600 dark:text-indigo-400 w-8 h-8 animate-pulse" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Verifying...</h3>
            <p className="text-gray-500 dark:text-gray-400">Please wait while we secure your account.</p>
          </motion.div>
        );

      case 'success':
        return (
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-center py-8"
          >
            <div className="w-20 h-20 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mx-auto mb-6">
              <CheckCircle2 className="w-10 h-10 text-green-600 dark:text-green-400" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Verified!</h3>
            <p className="text-green-600 dark:text-green-400 mb-6">{message}</p>
            <p className="text-sm text-gray-400">Redirecting you to profile creation...</p>
          </motion.div>
        );

      case 'error':
        return (
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-center py-6"
          >
            <div className="w-20 h-20 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center mx-auto mb-6">
              <XCircle className="w-10 h-10 text-red-600 dark:text-red-400" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Verification Failed</h3>
            <p className="text-red-500 dark:text-red-400 mb-8">{message}</p>
            
            <button
              onClick={handleResendVerification}
              disabled={isResending}
              className="inline-flex items-center gap-2 px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-medium transition-colors disabled:opacity-50"
            >
              {isResending ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
              Resend Verification
            </button>
          </motion.div>
        );

      default: // 'pending'
        return (
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-center py-6"
          >
            <div className="w-20 h-20 bg-indigo-50 dark:bg-indigo-900/20 rounded-full flex items-center justify-center mx-auto mb-6 relative">
              <Mail className="w-10 h-10 text-indigo-600 dark:text-indigo-400" />
              <span className="absolute top-0 right-0 flex h-4 w-4">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-4 w-4 bg-red-500 border-2 border-white dark:border-gray-900"></span>
              </span>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Check your inbox</h3>
            <p className="text-gray-500 dark:text-gray-400 mb-6 max-w-xs mx-auto">
              We've sent a verification link to <br/>
              <span className="font-medium text-indigo-600 dark:text-indigo-400">{user?.email}</span>
            </p>
            
            <button
              onClick={handleResendVerification}
              disabled={isResending}
              className="text-sm text-gray-500 hover:text-indigo-600 dark:hover:text-indigo-400 underline decoration-dotted transition-colors disabled:opacity-50"
            >
              {isResending ? 'Sending...' : "Didn't receive the email? Click to resend"}
            </button>
          </motion.div>
        );
    }
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-[#f3f4f6] dark:bg-[#0f172a] p-4 relative overflow-hidden">
      
      {/* Ambient Background */}
      <div className="absolute top-[-10%] left-[-5%] w-[40%] h-[40%] bg-blue-500/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-5%] w-[40%] h-[40%] bg-purple-500/10 rounded-full blur-[120px] pointer-events-none" />

      <motion.div 
        layout
        className="w-full max-w-md bg-white dark:bg-gray-900 rounded-3xl shadow-2xl border border-gray-200 dark:border-gray-800 p-8 relative z-10"
      >
        <div className="mb-2 text-center">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Email Verification</h2>
        </div>

        <AnimatePresence mode="wait">
          <motion.div
            key={status}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
          >
            {renderContent()}
          </motion.div>
        </AnimatePresence>

        <div className="mt-8 pt-6 border-t border-gray-100 dark:border-gray-800 text-center">
          <Link 
            to="/login" 
            className="inline-flex items-center gap-2 text-sm font-medium text-gray-600 dark:text-gray-400 hover:text-indigo-600 dark:hover:text-white transition-colors group"
          >
            <ArrowLeft size={16} className="group-hover:-translate-x-1 transition-transform" />
            Back to Login
          </Link>
        </div>
      </motion.div>
    </div>
  );
};

export default EmailVerification;