import React, { useState } from 'react';
import { Search, Play, Sparkles, AlertCircle } from 'lucide-react';

export default function UrlInput({ onStartAudit, isLoading }) {
  const [url, setUrl] = useState('');
  const [error, setError] = useState('');

  const validateUrlFormat = (input) => {
    if (!input || !input.trim()) return "Please enter a website URL.";
    const trimmed = input.trim();
    if (trimmed.toLowerCase() === "demo.local" || trimmed.toLowerCase() === "demo") return "";
    if (!trimmed.startsWith("http://") && !trimmed.startsWith("https://")) {
      return "Please enter a valid HTTP/HTTPS website URL (e.g., https://example.com).";
    }
    return "";
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const valError = validateUrlFormat(url);
    if (valError) {
      setError(valError);
      return;
    }
    setError('');
    onStartAudit(url.trim());
  };

  const handleDemoClick = () => {
    setUrl("demo.local");
    setError('');
    onStartAudit("demo.local");
  };

  return (
    <div className="bg-slate-900 text-white p-6 sm:p-7 rounded-2xl shadow-xl border border-slate-800 relative overflow-hidden">
      {/* Decorative gradient blur in background */}
      <div className="absolute -right-20 -top-20 w-60 h-60 bg-blue-600/10 rounded-full blur-3xl pointer-events-none"></div>
      
      <form onSubmit={handleSubmit} className="space-y-4 relative z-10">
        <div className="flex items-center justify-between">
          <label className="block text-sm font-semibold text-slate-200">
            Target Website URL Audit
          </label>
          <span className="text-xs text-slate-400 font-medium hidden sm:inline-block">
            Deterministic Scanners + Gemini AI Analysis
          </span>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-grow">
            <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
              <Search className="w-5 h-5 text-slate-400" />
            </div>
            <input
              type="text"
              value={url}
              onChange={(e) => { setUrl(e.target.value); setError(''); }}
              placeholder="https://example.com or enter URL"
              disabled={isLoading}
              className="w-full pl-10 pr-4 py-3 bg-slate-950/90 border border-slate-700/90 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm font-medium transition"
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="flex items-center justify-center space-x-2 px-6 py-3 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-semibold rounded-xl shadow-lg shadow-blue-600/30 transition duration-150 whitespace-nowrap text-sm cursor-pointer"
          >
            <Play className="w-4 h-4 fill-current" />
            <span>{isLoading ? 'Auditing...' : 'Start Audit'}</span>
          </button>
        </div>

        {error && (
          <div className="flex items-center space-x-2 text-rose-300 text-xs bg-rose-950/50 p-3 rounded-xl border border-rose-800/60">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <div className="pt-3 flex flex-wrap items-center justify-between gap-3 text-xs text-slate-400 border-t border-slate-800/80">
          <span>Evaluate live web applications or test our built-in sample website target:</span>
          <button
            type="button"
            onClick={handleDemoClick}
            disabled={isLoading}
            className="inline-flex items-center space-x-1.5 px-3.5 py-1.5 bg-indigo-950/80 hover:bg-indigo-900 text-indigo-300 rounded-lg border border-indigo-700/50 transition text-xs font-semibold cursor-pointer"
          >
            <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
            <span>Test Built-In Demo Website</span>
          </button>
        </div>
      </form>
    </div>
  );
}
