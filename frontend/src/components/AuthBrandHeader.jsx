import React from 'react';

export default function AuthBrandHeader({ subtitle = "Intelligent Website Audit & Quality Assurance" }) {
  return (
    <div className="flex flex-col items-center text-center space-y-3">
      {/* Precision Developer Brand Icon */}
      <div className="flex items-center justify-center w-11 h-11 rounded-xl bg-[#151D2B] border border-[#263244] shadow-sm text-[#6366F1]">
        <svg
          className="w-5 h-5 text-[#6366F1]"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.75"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          {/* Central inspection core */}
          <circle cx="12" cy="12" r="3" />
          {/* Engineering viewfinder bracket frame */}
          <path d="M3 8V5a2 2 0 0 1 2-2h3" />
          <path d="M16 3h3a2 2 0 0 1 2 2v3" />
          <path d="M21 16v3a2 2 0 0 1-2 2h-3" />
          <path d="M8 21H5a2 2 0 0 1-2-2v-3" />
          {/* Audit crosshair ticks */}
          <line x1="12" y1="1.5" x2="12" y2="3.5" />
          <line x1="12" y1="20.5" x2="12" y2="22.5" />
          <line x1="1.5" y1="12" x2="3.5" y2="12" />
          <line x1="20.5" y1="12" x2="22.5" y2="12" />
        </svg>
      </div>

      <div>
        <div className="flex items-center justify-center gap-1.5">
          <span className="text-lg font-semibold tracking-tight text-[#F8FAFC]">DevLens</span>
          <span className="text-[10px] font-mono uppercase px-1.5 py-0.5 rounded bg-[#151D2B] border border-[#263244] text-[#6366F1] font-semibold tracking-wider">
            AI
          </span>
        </div>
        <p className="text-xs text-[#94A3B8] font-normal mt-1">
          {subtitle}
        </p>
      </div>
    </div>
  );
}
