import React from 'react';

export default function ScoreGauge({ score }) {
  const rounded = Math.round(score || 0);

  let colorClass = "text-emerald-600 border-emerald-500 bg-emerald-50/80";
  let badgeText = "Good Health";

  if (rounded < 60) {
    colorClass = "text-rose-600 border-rose-500 bg-rose-50/80";
    badgeText = "Needs Critical Attention";
  } else if (rounded < 80) {
    colorClass = "text-amber-600 border-amber-500 bg-amber-50/80";
    badgeText = "Moderate Health";
  }

  return (
    <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col items-center justify-center text-center space-y-3 h-full">
      <span className="text-xs uppercase tracking-wider text-slate-500 font-bold">
        Overall Health Score
      </span>

      <div className={`relative flex items-center justify-center w-36 h-36 rounded-full border-4 ${colorClass} shadow-md`}>
        <div className="flex flex-col items-center">
          <span className="text-5xl font-extrabold tracking-tight text-slate-900">
            {rounded}
          </span>
          <span className="text-xs text-slate-500 font-bold">/ 100</span>
        </div>
      </div>

      <div className={`px-3 py-1 rounded-full text-xs font-bold border ${colorClass}`}>
        {badgeText}
      </div>

      <p className="text-xs text-slate-500 max-w-xs font-medium">
        Calculated from 5 active deterministic categories (SEO, Accessibility, Performance, Security, Functionality).
      </p>
    </div>
  );
}

