import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import AuthBrandHeader from './AuthBrandHeader';
import { Eye, EyeOff, AlertCircle, CheckCircle, Loader2, ArrowRight, Check, Shield } from 'lucide-react';

export default function RegisterPage({ onSwitchToLogin }) {
  const { register } = useAuth();
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  // Password validation rules aligned strictly with backend security validators
  const hasMinLength = password.length >= 8;
  const hasLetter = /[a-zA-Z]/.test(password);
  const hasNumberOrSymbol = /[\d!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]/.test(password);
  const hasMixedCase = /[a-z]/.test(password) && /[A-Z]/.test(password);
  const isMatch = password.length > 0 && confirmPassword.length > 0 && password === confirmPassword;

  // Dynamic strength score (0 to 4) using requested color tokens
  const computeStrength = () => {
    if (!password) return { score: 0, label: '', color: 'bg-[#263244]' };
    let score = 0;
    if (hasMinLength) score++;
    if (hasLetter) score++;
    if (hasNumberOrSymbol) score++;
    if (hasMixedCase || password.length >= 12) score++;

    if (score <= 1) return { score: 1, label: 'Weak', color: 'bg-[#EF4444]' };
    if (score === 2) return { score: 2, label: 'Fair', color: 'bg-[#F59E0B]' };
    if (score === 3) return { score: 3, label: 'Good', color: 'bg-[#6366F1]' };
    return { score: 4, label: 'Strong', color: 'bg-[#22C55E]' };
  };

  const strength = computeStrength();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage('');
    setSuccessMessage('');

    const trimmedName = fullName.trim();
    const trimmedEmail = email.trim();

    if (!trimmedName || trimmedName.length < 2) {
      setErrorMessage('Please enter your full name (at least 2 characters).');
      return;
    }

    if (!trimmedEmail) {
      setErrorMessage('Please enter a valid work email address.');
      return;
    }

    if (!hasMinLength) {
      setErrorMessage('Password must be at least 8 characters long.');
      return;
    }

    if (!hasLetter || !hasNumberOrSymbol) {
      setErrorMessage('Password must contain at least one letter and at least one number or special symbol.');
      return;
    }

    if (password !== confirmPassword) {
      setErrorMessage('Passwords do not match. Please verify both password entries.');
      return;
    }

    setIsLoading(true);
    try {
      await register({
        full_name: trimmedName,
        email: trimmedEmail,
        password,
        confirm_password: confirmPassword,
      });
      setSuccessMessage('Account created successfully. Loading your dashboard...');
    } catch (err) {
      setErrorMessage(err.message || 'Registration failed. Please try a different email address.');
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

      <div className="w-full max-w-[440px] relative z-10 space-y-6">
        {/* Unified Brand Header */}
        <AuthBrandHeader subtitle="Intelligent Website Audit & Quality Assurance" />

        {/* Register Form Card */}
        <div className="bg-[#111827] border border-[#263244] rounded-xl p-6 sm:p-8 shadow-2xl shadow-black/50 space-y-5">
          <div className="space-y-1">
            <h1 className="text-xl font-semibold tracking-tight text-[#F8FAFC]">
              Create Your Account
            </h1>
            <p className="text-xs text-[#94A3B8] font-normal leading-relaxed">
              Start auditing website performance, security, and accessibility.
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
            {/* Full Name Field */}
            <div className="space-y-1.5">
              <label
                htmlFor="register-fullname"
                className="block text-xs font-medium text-[#F8FAFC] tracking-wide"
              >
                Full name
              </label>
              <input
                id="register-fullname"
                name="fullName"
                type="text"
                autoComplete="name"
                required
                value={fullName}
                onChange={(e) => {
                  setFullName(e.target.value);
                  setErrorMessage('');
                }}
                placeholder="Alex Morgan"
                className="w-full px-3.5 py-2.5 rounded-lg border border-[#263244] bg-[#151D2B] text-[#F8FAFC] placeholder-[#64748B] text-xs sm:text-sm font-normal focus:outline-none focus:border-[#6366F1] focus:ring-1 focus:ring-[#6366F1] transition-all duration-150"
              />
            </div>

            {/* Email Field */}
            <div className="space-y-1.5">
              <label
                htmlFor="register-email"
                className="block text-xs font-medium text-[#F8FAFC] tracking-wide"
              >
                Work email address
              </label>
              <input
                id="register-email"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  setErrorMessage('');
                }}
                placeholder="alex@company.com"
                className="w-full px-3.5 py-2.5 rounded-lg border border-[#263244] bg-[#151D2B] text-[#F8FAFC] placeholder-[#64748B] text-xs sm:text-sm font-normal focus:outline-none focus:border-[#6366F1] focus:ring-1 focus:ring-[#6366F1] transition-all duration-150"
              />
            </div>

            {/* Password Field */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label
                  htmlFor="register-password"
                  className="block text-xs font-medium text-[#F8FAFC] tracking-wide"
                >
                  Password
                </label>
                {password && (
                  <span className="text-[11px] font-mono text-[#94A3B8]">
                    Strength:{' '}
                    <span
                      className={`font-semibold ${
                        strength.score === 1
                          ? 'text-[#EF4444]'
                          : strength.score === 2
                          ? 'text-[#F59E0B]'
                          : strength.score === 3
                          ? 'text-[#6366F1]'
                          : 'text-[#22C55E]'
                      }`}
                    >
                      {strength.label}
                    </span>
                  </span>
                )}
              </div>
              <div className="relative">
                <input
                  id="register-password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="new-password"
                  required
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value);
                    setErrorMessage('');
                  }}
                  placeholder="Create a strong password"
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

              {/* Dynamic 4-Segment Strength Indicator */}
              {password && (
                <div className="pt-1 space-y-1.5">
                  <div className="grid grid-cols-4 gap-1.5">
                    {[1, 2, 3, 4].map((level) => (
                      <div
                        key={level}
                        className={`h-1 rounded-full transition-all duration-300 ${
                          strength.score >= level ? strength.color : 'bg-[#263244]'
                        }`}
                      />
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Confirm Password Field */}
            <div className="space-y-1.5">
              <label
                htmlFor="register-confirmpassword"
                className="block text-xs font-medium text-[#F8FAFC] tracking-wide"
              >
                Confirm password
              </label>
              <div className="relative">
                <input
                  id="register-confirmpassword"
                  name="confirmPassword"
                  type={showConfirmPassword ? 'text' : 'password'}
                  autoComplete="new-password"
                  required
                  value={confirmPassword}
                  onChange={(e) => {
                    setConfirmPassword(e.target.value);
                    setErrorMessage('');
                  }}
                  placeholder="Confirm your password"
                  className="w-full pl-3.5 pr-10 py-2.5 rounded-lg border border-[#263244] bg-[#151D2B] text-[#F8FAFC] placeholder-[#64748B] text-xs sm:text-sm font-normal focus:outline-none focus:border-[#6366F1] focus:ring-1 focus:ring-[#6366F1] transition-all duration-150"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  aria-label={showConfirmPassword ? 'Hide confirm password' : 'Show confirm password'}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-[#94A3B8] hover:text-[#F8FAFC] transition-colors cursor-pointer"
                >
                  {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Security Requirements Checklist Card */}
            <div className="p-3 rounded-lg bg-[#151D2B] border border-[#263244] space-y-1.5 text-[11px]">
              <div className="text-[10px] uppercase font-mono tracking-wider text-[#94A3B8] font-semibold mb-1">
                Security Requirements
              </div>
              <div className={`flex items-center gap-2 ${hasMinLength ? 'text-[#22C55E]' : 'text-[#94A3B8]'}`}>
                <div className={`w-3.5 h-3.5 rounded flex items-center justify-center shrink-0 ${hasMinLength ? 'text-[#22C55E]' : 'text-[#64748B]'}`}>
                  <Check className="w-3 h-3" />
                </div>
                <span>At least 8 characters</span>
              </div>
              <div className={`flex items-center gap-2 ${hasLetter ? 'text-[#22C55E]' : 'text-[#94A3B8]'}`}>
                <div className={`w-3.5 h-3.5 rounded flex items-center justify-center shrink-0 ${hasLetter ? 'text-[#22C55E]' : 'text-[#64748B]'}`}>
                  <Check className="w-3 h-3" />
                </div>
                <span>Contains at least one letter</span>
              </div>
              <div className={`flex items-center gap-2 ${hasNumberOrSymbol ? 'text-[#22C55E]' : 'text-[#94A3B8]'}`}>
                <div className={`w-3.5 h-3.5 rounded flex items-center justify-center shrink-0 ${hasNumberOrSymbol ? 'text-[#22C55E]' : 'text-[#64748B]'}`}>
                  <Check className="w-3 h-3" />
                </div>
                <span>Contains a number or special symbol</span>
              </div>
              {confirmPassword.length > 0 && (
                <div className={`flex items-center gap-2 ${isMatch ? 'text-[#22C55E]' : 'text-[#EF4444]'}`}>
                  <div className={`w-3.5 h-3.5 rounded flex items-center justify-center shrink-0 ${isMatch ? 'text-[#22C55E]' : 'text-[#EF4444]'}`}>
                    <Check className="w-3 h-3" />
                  </div>
                  <span>{isMatch ? 'Passwords match' : 'Passwords do not match'}</span>
                </div>
              )}
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
                  <span>Creating Account...</span>
                </>
              ) : (
                <>
                  <span>Create Account</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Navigation to Login */}
          <div className="pt-4 border-t border-[#263244] text-center">
            <p className="text-xs text-[#94A3B8]">
              Already have an account?{' '}
              <button
                type="button"
                onClick={onSwitchToLogin}
                className="text-[#6366F1] hover:text-[#818CF8] hover:underline font-medium transition-colors cursor-pointer"
              >
                Sign In
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
