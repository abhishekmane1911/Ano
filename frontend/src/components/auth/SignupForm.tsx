import { useState, type FormEvent } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Mail, Lock, User, ArrowRight, Loader2, AlertCircle, CheckCircle2 } from 'lucide-react';
import { authAPI } from '../../api/auth';

const SignupForm = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    password_confirm: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@iiti\.ac\.in$/;
    return emailRegex.test(email);
  };

  const validatePassword = (password: string): string[] => {
    const errors: string[] = [];
    if (password.length < 8) errors.push('At least 8 characters');
    if (!/[A-Z]/.test(password)) errors.push('One uppercase letter');
    if (!/[a-z]/.test(password)) errors.push('One lowercase letter');
    if (!/[0-9]/.test(password)) errors.push('One number');
    return errors;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errors[name] || errors.general) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[name];
        delete newErrors.general;
        return newErrors;
      });
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setErrors({});
    setSuccessMessage('');

    // Validation
    if (!validateEmail(formData.email)) {
      setErrors({ email: 'Must be a valid @iiti.ac.in address' });
      return;
    }

    const passwordErrors = validatePassword(formData.password);
    if (passwordErrors.length > 0) {
      setErrors({ password: passwordErrors.join('. ') });
      return;
    }

    if (formData.password !== formData.password_confirm) {
      setErrors({ password_confirm: 'Passwords do not match' });
      return;
    }

    setIsLoading(true);

    try {
      await authAPI.register(formData);
      setSuccessMessage('Registration successful! Please verify your email.');
      setTimeout(() => navigate('/login'), 3000);
    } catch (err: any) {
      const response = err.response;
      if (response?.data?.error?.details) {
        setErrors(response.data.error.details);
      } else if (response?.data?.error?.message) {
        setErrors({ general: response.data.error.message });
      } else {
        setErrors({ general: 'Registration failed. Please try again.' });
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-zinc-950 p-4 pt-18 relative overflow-hidden">
      
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="w-full max-w-md bg-zinc-900 rounded-3xl border border-zinc-800 p-8 relative z-10 shadow-sm"
      >
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-zinc-50 mb-2">Create Account</h1>
          <p className="text-zinc-400">Join the exclusive IIT Indore community</p>
        </div>

        <AnimatePresence>
          {successMessage && (
            <motion.div 
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-6 p-4 bg-emerald-900/20 border border-emerald-800 rounded-xl flex items-start gap-3"
            >
              <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-emerald-400">{successMessage}</p>
            </motion.div>
          )}

          {errors.general && (
            <motion.div 
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-6 p-4 bg-red-900/20 border border-red-800 rounded-xl flex items-start gap-3"
            >
              <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-400">{errors.general}</p>
            </motion.div>
          )}
        </AnimatePresence>

        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Email Field */}
          <div className="space-y-1.5">
            <label className="text-sm font-medium text-zinc-300 ml-1">Institute Email</label>
            <div className="relative group">
              <div className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500 group-focus-within:text-blue-500 transition-colors">
                <Mail size={20} />
              </div>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="your.name@iiti.ac.in"
                className={`w-full pl-10 pr-4 py-3 bg-zinc-800/50 border rounded-xl outline-none transition-all ${
                  errors.email 
                    ? 'border-red-500 focus:border-red-500' 
                    : 'border-zinc-700 focus:border-blue-500'
                } text-zinc-100 placeholder-zinc-500`}
              />
            </div>
            {errors.email && <p className="text-xs text-red-500 ml-1">{errors.email}</p>}
          </div>

          {/* Username Field */}
          <div className="space-y-1.5">
            <label className="text-sm font-medium text-zinc-300 ml-1">Username</label>
            <div className="relative group">
              <div className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500 group-focus-within:text-blue-500 transition-colors">
                <User size={20} />
              </div>
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleChange}
                placeholder="Choose a unique username"
                className={`w-full pl-10 pr-4 py-3 bg-zinc-800/50 border rounded-xl outline-none transition-all ${
                  errors.username 
                    ? 'border-red-500 focus:border-red-500' 
                    : 'border-zinc-700 focus:border-blue-500'
                } text-zinc-100 placeholder-zinc-500`}
              />
            </div>
            {errors.username && <p className="text-xs text-red-500 ml-1">{errors.username}</p>}
          </div>

          {/* Password Field */}
          <div className="space-y-1.5">
            <label className="text-sm font-medium text-zinc-300 ml-1">Password</label>
            <div className="relative group">
              <div className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500 group-focus-within:text-blue-500 transition-colors">
                <Lock size={20} />
              </div>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="Create a strong password"
                className={`w-full pl-10 pr-4 py-3 bg-zinc-800/50 border rounded-xl outline-none transition-all ${
                  errors.password 
                    ? 'border-red-500 focus:border-red-500' 
                    : 'border-zinc-700 focus:border-blue-500'
                } text-zinc-100 placeholder-zinc-500`}
              />
            </div>
            {errors.password && <p className="text-xs text-red-500 ml-1">{errors.password}</p>}
          </div>

          {/* Confirm Password Field */}
          <div className="space-y-1.5">
            <label className="text-sm font-medium text-zinc-300 ml-1">Confirm Password</label>
            <div className="relative group">
              <div className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500 group-focus-within:text-blue-500 transition-colors">
                <Lock size={20} />
              </div>
              <input
                type="password"
                name="password_confirm"
                value={formData.password_confirm}
                onChange={handleChange}
                placeholder="Repeat your password"
                className={`w-full pl-10 pr-4 py-3 bg-zinc-800/50 border rounded-xl outline-none transition-all ${
                  errors.password_confirm 
                    ? 'border-red-500 focus:border-red-500' 
                    : 'border-zinc-700 focus:border-blue-500'
                } text-zinc-100 placeholder-zinc-500`}
              />
            </div>
            {errors.password_confirm && <p className="text-xs text-red-500 ml-1">{errors.password_confirm}</p>}
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-semibold py-3.5 rounded-xl transition-all disabled:opacity-70 disabled:cursor-not-allowed transform active:scale-[0.99] mt-6"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Creating Account...</span>
              </>
            ) : (
              <>
                <span>Sign Up</span>
                <ArrowRight className="w-5 h-5" />
              </>
            )}
          </button>
        </form>

        <div className="mt-8 text-center">
          <p className="text-zinc-500 text-sm">
            Already have an account?{' '}
            <Link 
              to="/login" 
              className="text-blue-400 font-semibold hover:text-blue-300 transition-colors"
            >
              Sign in
            </Link>
          </p>
        </div>
      </motion.div>
    </div>
  );
};

export default SignupForm;