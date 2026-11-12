import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import AuthBrandHeader from './AuthBrandHeader';
import { Eye, EyeOff, AlertCircle, CheckCircle, Loader2, ArrowRight, Shield } from 'lucide-react';

export default function LoginPage({ onSwitchToRegister }) {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage('');
    setSuccessMessage('');

    const trimmedEmail = email.trim();
    if (!trimmedEmail) {
      setErrorMessage('Please enter your work email address.');
      return;
    }
    if (!password) {
      setErrorMessage('Please enter your account password.');
      return;
    }

    setIsLoading(true);
    try {
      await login({
        email: trimmedEmail,
        password,
        remember_me: rememberMe,
      });
      setSuccessMessage('Authentication verified. Loading your dashboard...');
    } catch (err) {
      setErrorMessage(err.message || 'Invalid email or password. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col justify-center items-center py-12 px-4 sm:px-6 lg:px-8 bg-[#0B0F19] text-[#F8FAFC] selection:bg-[#6366F1] selection:text-[#F8FAFC]">
      {/* Restrained developer-grade top ambient glow */}
      <div 
        className="fixed inset-0 pointer-events-none opacity-40"
        style={{
          background: 'radial-gradient(ellipse 80% 50% at 50% -20%, rgba(99, 102, 241, 0.12), transparent 70%)'
        }}
        aria-hidden="true"
      />

      <div className="w-full max-w-[420px] relative z-10 space-y-6">
        {/* Unified Brand Header */}
        <AuthBrandHeader subtitle="Intelligent Website Audit & Quality Assurance" />

        {/* Login Form Card */}
        <div className="bg-[#111827] border border-[#263244] rounded-xl p-6 sm:p-8 shadow-2xl shadow-black/50 space-y-5">
          <div className="space-y-1">
            <h1 className="text-xl font-semibold tracking-tight text-[#F8FAFC]">
              Welcome Back
            </h1>
            <p className="text-xs text-[#94A3B8] font-normal leading-relaxed">
              Sign in to audit, analyze, and improve website quality.
            </p>
          </div>

          {/* Error Feedback Banner */}
          {errorMessage && (
            <div
              role="alert"
              className="p-3 rounded-lg bg-[#EF4444]/10 border border-[#EF4444]/30 text-[#EF4444] text-xs flex items-start gap-2.5 leading-relaxed"
            >
              <AlertCircle className="w-4 h-4 text-[#EF4444] shrink-0 mt-0.5" />
              <span className="font-medium">{errorMessage}</span>
            </div>
          )}

          {/* Success Feedback Banner */}
          {successMessage && (
            <div
              role="status"
              className="p-3 rounded-lg bg-[#22C55E]/10 border border-[#22C55E]/30 text-[#22C55E] text-xs flex items-center gap-2.5"
            >
              <CheckCircle className="w-4 h-4 text-[#22C55E] shrink-0" />
              <span className="font-medium">{successMessage}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4" noValidate>
            {/* Email Field */}
            <div className="space-y-1.5">
              <label
                htmlFor="login-email"
                className="block text-xs font-medium text-[#F8FAFC] tracking-wide"
              >
                Email address
              </label>
              <input
                id="login-email"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  setErrorMessage('');
                }}
                placeholder="name@company.com"
                className="w-full px-3.5 py-2.5 rounded-lg border border-[#263244] bg-[#151D2B] text-[#F8FAFC] placeholder-[#64748B] text-xs sm:text-sm font-normal focus:outline-none focus:border-[#6366F1] focus:ring-1 focus:ring-[#6366F1] transition-all duration-150"
              />
            </div>

            {/* Password Field */}
            <div className="space-y-1.5">
              <label
                htmlFor="login-password"
                className="block text-xs font-medium text-[#F8FAFC] tracking-wide"
              >
                Password
              </label>
              <div className="relative">
                <input
                  id="login-password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value);
                    setErrorMessage('');
                  }}
                  placeholder="Enter your password"
                  className="w-full pl-3.5 pr-10 py-2.5 rounded-lg border border-[#263244] bg-[#151D2B] text-[#F8FAFC] placeholder-[#64748B] text-xs sm:text-sm font-normal focus:outline-none focus:border-[#6366F1] focus:ring-1 focus:ring-[#6366F1] transition-all duration-150"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-[#94A3B8] hover:text-[#F8FAFC] transition-colors cursor-pointer"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Remember Me Session Option */}
            <div className="flex items-center justify-between pt-1">
              <label className="flex items-center gap-2 cursor-pointer select-none group">
                <input
                  id="login-remember"
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="w-3.5 h-3.5 rounded border border-[#263244] bg-[#151D2B] text-[#6366F1] focus:ring-1 focus:ring-[#6366F1] focus:ring-offset-0 focus:outline-none cursor-pointer accent-[#6366F1] transition-colors"
                />
                <span className="text-xs text-[#94A3B8] group-hover:text-[#F8FAFC] font-normal transition-colors">
                  Remember this session
                </span>
              </label>
              <span className="text-[10px] font-mono text-[#64748B] uppercase tracking-wider">
                HttpOnly
              </span>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-lg font-medium text-xs sm:text-sm text-[#F8FAFC] bg-[#6366F1] hover:bg-[#5558E6] active:bg-[#4F46E5] transition-all duration-150 shadow-sm shadow-[#6366F1]/20 border border-transparent focus:ring-2 focus:ring-[#6366F1]/40 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer mt-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin text-[#F8FAFC]" />
                  <span>Signing In...</span>
                </>
              ) : (
                <>
                  <span>Sign In</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Navigation to Registration */}
          <div className="pt-4 border-t border-[#263244] text-center">
            <p className="text-xs text-[#94A3B8]">
              Don't have an account?{' '}
              <button
                type="button"
                onClick={onSwitchToRegister}
                className="text-[#6366F1] hover:text-[#818CF8] hover:underline font-medium transition-colors cursor-pointer"
              >
                Create an account
              </button>
            </p>
          </div>
        </div>

        {/* Security Infrastructure Note */}
        <div className="flex items-center justify-center gap-1.5 text-[11px] text-[#94A3B8]/80 font-normal">
          <Shield className="w-3.5 h-3.5 text-[#22C55E]" />
          <span>Argon2id encryption · Multi-layer SSRF defense · Zero data leakage</span>
        </div>
      </div>
    </div>
  );
}
