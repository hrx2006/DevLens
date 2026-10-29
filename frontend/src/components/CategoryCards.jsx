import React from 'react';
import { Search, Eye, Gauge, Shield, Wrench } from 'lucide-react';

export default function CategoryCards({
  seoScore = 0,
  accessibilityScore = 0,
  performanceScore = 0,
  securityScore = 0,
  functionalityScore = 0,
}) {
  const getScoreColor = (val) => {
    if (val >= 80) return 'text-emerald-700 border-emerald-300 bg-emerald-50';
    if (val >= 60) return 'text-amber-700 border-amber-300 bg-amber-50';
    return 'text-rose-700 border-rose-300 bg-rose-50';
  };

  const categories = [
    {
      title: 'SEO',
      score: seoScore,
      icon: Search,
      description: 'Title, meta tags, heading hierarchy & canonical URLs',
    },
    {
      title: 'Accessibility',
      score: accessibilityScore,
      icon: Eye,
      description: 'WCAG 2.2 image alts, input labels, button text & page language',
    },
    {
      title: 'Performance',
      score: performanceScore,
      icon: Gauge,
      description: 'Server latency, payload size & render-blocking scripts',
    },
    {
      title: 'Security',
      score: securityScore,
      icon: Shield,
      description: 'HTTPS, HSTS, CSP, X-Frame-Options, nosniff & mixed-content',
    },
    {
      title: 'Functionality',
      score: functionalityScore,
      icon: Wrench,
      description: 'Broken internal links, form method hygiene & password security',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
      {categories.map((cat) => {
        const Icon = cat.icon;
        const colorClass = getScoreColor(cat.score);
        return (
          <div
            key={cat.title}
            className="bg-white p-4.5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between space-y-3 hover:shadow-md transition"
          >
            <div className="flex items-center justify-between">
              <div className="p-2.5 rounded-xl bg-slate-900 text-blue-400 shadow-sm border border-slate-800">
                <Icon className="w-5 h-5" />
              </div>
              <span className={`px-2.5 py-1 rounded-full text-xs font-bold border ${colorClass}`}>
                {Math.round(cat.score || 0)} / 100
              </span>
            </div>

            <div>
              <h4 className="text-sm font-extrabold text-slate-900">{cat.title}</h4>
              <p className="text-xs text-slate-500 mt-1 font-medium leading-relaxed">
                {cat.description}
              </p>
            </div>

            <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden border border-slate-200/80">
              <div
                className={`h-full transition-all duration-500 rounded-full ${
                  cat.score >= 80 ? 'bg-emerald-500' : cat.score >= 60 ? 'bg-amber-500' : 'bg-rose-500'
                }`}
                style={{ width: `${Math.max(5, Math.min(100, cat.score || 0))}%` }}
              ></div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
