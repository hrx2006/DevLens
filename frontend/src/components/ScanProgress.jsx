import React from 'react';
import { CheckCircle2, Loader2, Circle } from 'lucide-react';

export default function ScanProgress({ stage }) {
  // stages: 'idle', 'validating', 'crawling', 'seo', 'accessibility', 'performance', 'security', 'functionality', 'ai', 'completed'

  const steps = [
    { key: 'validating', label: 'SSRF & URL Check' },
    { key: 'crawling', label: 'Web Crawler' },
    { key: 'seo', label: 'SEO Scanner' },
    { key: 'accessibility', label: 'Accessibility' },
    { key: 'performance', label: 'Performance' },
    { key: 'security', label: 'Security' },
    { key: 'functionality', label: 'Functionality' },
    { key: 'ai', label: 'AI Reasoning' },
    { key: 'completed', label: 'Complete' },
  ];

  const getStepStatus = (stepKey, index) => {
    const stageOrder = [
      'validating',
      'crawling',
      'seo',
      'accessibility',
      'performance',
      'security',
      'functionality',
      'ai',
      'completed',
    ];
    const currentIndex = stageOrder.indexOf(stage);

    if (stage === 'completed') return 'done';
    if (currentIndex === -1) return 'pending';
    if (index < currentIndex) return 'done';
    if (index === currentIndex) return 'active';
    return 'pending';
  };

  return (
    <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-extrabold text-slate-900">Live Audit Execution Pipeline</h3>
        <span className="text-xs text-blue-600 font-mono font-bold flex items-center gap-1.5 bg-blue-50 px-3 py-1 rounded-full border border-blue-200">
          {stage !== 'completed' && <Loader2 className="w-3.5 h-3.5 animate-spin text-blue-600" />}
          {stage === 'completed' ? '✓ Audit Completed' : 'Processing Stage...'}
        </span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 lg:grid-cols-9 gap-2">
        {steps.map((step, idx) => {
          const status = getStepStatus(step.key, idx);
          return (
            <div
              key={step.key}
              className={`flex items-center space-x-1.5 p-2.5 rounded-xl border text-[11px] font-semibold transition ${
                status === 'done'
                  ? 'bg-emerald-50 border-emerald-200 text-emerald-800'
                  : status === 'active'
                  ? 'bg-slate-900 border-slate-800 text-white shadow-sm ring-1 ring-blue-500'
                  : 'bg-slate-50 border-slate-200 text-slate-400'
              }`}
            >
              {status === 'done' && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0" />}
              {status === 'active' && <Loader2 className="w-3.5 h-3.5 text-blue-400 animate-spin flex-shrink-0" />}
              {status === 'pending' && <Circle className="w-3.5 h-3.5 text-slate-300 flex-shrink-0" />}
              <span className="truncate">{step.label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
