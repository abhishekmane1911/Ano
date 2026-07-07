import { useState, type FormEvent } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Mail, Lock, ArrowRight, Loader2, AlertCircle } from 'lucide-react';
import { authAPI } from '../../api/auth';
import { useAuthStore } from '../../stores/authStore';

const LoginForm = () => {
  const navigate = useNavigate();
  const { login } = useAuthStore();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    remember_me: false,
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
    // Clear error for this field when user starts typing
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
    setIsLoading(true);

    try {
      const response = await authAPI.login(formData);
      
      login(
        {
          id: response.user.id,
          email: response.user.email,
          isVerified: response.user.is_verified,
        },
        response.access
      );

      if (response.user.is_verified) {
        navigate('/');
      } else {
        navigate('/verify-email');
      }
    } catch (err: any) {
      const response = err.response;
      if (response?.status === 429) {
        setErrors({
          general: 'Too many login attempts. Please try again later.',
        });
      } else if (response?.data?.error?.details) {
        setErrors(response.data.error.details);
      } else if (response?.data?.error?.message) {
        setErrors({ general: response.data.error.message });
      } else {
        setErrors({ general: 'Login failed. Please check your credentials.' });
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-zinc-950 p-4 relative overflow-hidden">
      
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="w-full max-w-md bg-zinc-900 rounded-3xl border border-zinc-800 p-8 relative z-10 shadow-sm"
      >
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-zinc-50 mb-2">Welcome Back</h1>
          <p className="text-zinc-400">Sign in to continue to Ano</p>
        </div>

        {errors.general && (
          <motion.div 
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="mb-6 p-4 bg-red-900/20 border border-red-800 rounded-xl flex items-start gap-3"
          >
            <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-red-400">{errors.general}</p>
          </motion.div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label htmlFor="email" className="text-sm font-medium text-zinc-300 ml-1">
              Institute Email
            </label>
            <div className="relative group">
              <div className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500 group-focus-within:text-blue-500 transition-colors">
                <Mail size={20} />
              </div>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="your.name@iiti.ac.in"
                required
                className={`w-full pl-10 pr-4 py-3 bg-zinc-800/50 border rounded-xl outline-none transition-all ${
                  errors.email 
                    ? 'border-red-500 focus:border-red-500' 
                    : 'border-zinc-700 focus:border-blue-500'
                } text-zinc-100 placeholder-zinc-500`}
              />
            </div>
            {errors.email && <p className="text-xs text-red-500 ml-1">{errors.email}</p>}
          </div>

          <div className="space-y-2">
            <div className="flex justify-between items-center px-1">
              <label htmlFor="password" className="text-sm font-medium text-zinc-300">
                Password
              </label>
              <Link 
                to="/password-reset" 
                className="text-xs font-medium text-blue-400 hover:text-blue-300 transition-colors"
              >
                Forgot password?
              </Link>
            </div>
            <div className="relative group">
              <div className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500 group-focus-within:text-blue-500 transition-colors">
                <Lock size={20} />
              </div>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="Enter your password"
                required
                className={`w-full pl-10 pr-4 py-3 bg-zinc-800/50 border rounded-xl outline-none transition-all ${
                  errors.password 
                    ? 'border-red-500 focus:border-red-500' 
                    : 'border-zinc-700 focus:border-blue-500'
                } text-zinc-100 placeholder-zinc-500`}
              />
            </div>
            {errors.password && <p className="text-xs text-red-500 ml-1">{errors.password}</p>}
          </div>

          <div className="flex items-center">
            <label className="flex items-center gap-2 cursor-pointer group">
              <div className="relative flex items-center">
                <input
                  type="checkbox"
                  name="remember_me"
                  checked={formData.remember_me}
                  onChange={handleChange}
                  className="peer h-5 w-5 cursor-pointer appearance-none rounded-md border border-zinc-600 bg-zinc-800 checked:border-blue-500 checked:bg-blue-500 transition-all"
                />
                <svg
                  className="pointer-events-none absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-3.5 h-3.5 text-white opacity-0 peer-checked:opacity-100 transition-opacity"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth="3"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <span className="text-sm text-zinc-400 group-hover:text-zinc-200 transition-colors">
                Remember me
              </span>
            </label>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-semibold py-3.5 rounded-xl transition-all disabled:opacity-70 disabled:cursor-not-allowed transform active:scale-[0.99]"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Signing In...</span>
              </>
            ) : (
              <>
                <span>Sign In</span>
                <ArrowRight className="w-5 h-5" />
              </>
            )}
          </button>
        </form>

        <div className="mt-8 text-center">
          <p className="text-zinc-500 text-sm">
            Don't have an account?{' '}
            <Link 
              to="/signup" 
              className="text-blue-400 font-semibold hover:text-blue-300 transition-colors"
            >
              Create account
            </Link>
          </p>
        </div>
      </motion.div>
    </div>
  );
};

export default LoginForm;