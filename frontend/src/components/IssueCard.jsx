import React, { useState } from 'react';
import { AlertTriangle, ChevronDown, ChevronUp, Cpu, Lightbulb, Code2 } from 'lucide-react';

export default function IssueCard({ issue }) {
  const [expanded, setExpanded] = useState(true);

  const getSeverityBadge = (severity) => {
    switch (severity) {
      case 'Critical':
        return 'bg-rose-100 text-rose-800 border-rose-200';
      case 'High':
        return 'bg-amber-100 text-amber-800 border-amber-200';
      case 'Medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'Low':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      default:
        return 'bg-slate-100 text-slate-700 border-slate-200';
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden transition hover:shadow-md">
      <div
        onClick={() => setExpanded(!expanded)}
        className="p-4 sm:p-5 flex items-center justify-between cursor-pointer select-none bg-slate-50/70 hover:bg-slate-100/80 transition"
      >
        <div className="flex items-start space-x-3">
          <div className="mt-0.5 p-2 rounded-xl bg-amber-100 border border-amber-200 text-amber-700">
            <AlertTriangle className="w-4 h-4" />
          </div>

          <div>
            <div className="flex flex-wrap items-center gap-2">
              <h4 className="text-base font-extrabold text-slate-900">{issue.title}</h4>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-slate-900 text-white shadow-xs">
                {issue.category}
              </span>
              <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold border ${getSeverityBadge(issue.severity)}`}>
                Severity: {issue.severity}
              </span>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-indigo-50 text-indigo-700 border border-indigo-200">
                Priority: {issue.priority}
              </span>
            </div>
            <p className="text-xs text-slate-600 font-medium mt-1 line-clamp-1">{issue.description}</p>
          </div>
        </div>

        <button className="text-slate-400 hover:text-slate-700 p-1">
          {expanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
        </button>
      </div>

      {expanded && (
        <div className="p-4 sm:p-5 border-t border-slate-200 space-y-4 text-xs bg-white">
          {/* Evidence */}
          <div className="space-y-1.5">
            <div className="flex items-center space-x-1.5 font-bold text-slate-700 uppercase tracking-wider text-[11px]">
              <Code2 className="w-3.5 h-3.5 text-blue-600" />
              <span>Technical Evidence</span>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 font-mono text-emerald-400 break-all shadow-sm">
              {issue.evidence || "No specific snippet evidence provided by scanner."}
            </div>
          </div>

          {/* AI Insight */}
          <div className="space-y-2 p-4 rounded-xl bg-slate-900 text-slate-100 border border-indigo-950 shadow-md">
            <div className="flex items-center justify-between flex-wrap gap-2">
              <div className="flex items-center space-x-1.5 font-bold text-blue-400 uppercase tracking-wider text-[11px]">
                <Cpu className="w-3.5 h-3.5 text-blue-400" />
                <span>AI Reasoning & Root Cause</span>
              </div>
              <span className="text-[10px] text-slate-400 font-mono bg-slate-800/90 px-2 py-0.5 rounded-md border border-slate-700">
                Engine: {issue.ai_source || 'Deterministic Fallback Engine'}
              </span>
            </div>
            <p className="text-slate-200 leading-relaxed font-normal">
              <strong className="text-blue-300 font-semibold">Explanation: </strong>
              {issue.ai_explanation || issue.description}
            </p>
            {issue.root_cause && (
              <p className="text-slate-200 leading-relaxed font-normal">
                <strong className="text-blue-300 font-semibold">Likely Root Cause: </strong>
                {issue.root_cause}
              </p>
            )}
            {issue.user_impact && (
              <p className="text-slate-200 leading-relaxed font-normal">
                <strong className="text-blue-300 font-semibold">User & Indexing Impact: </strong>
                {issue.user_impact}
              </p>
            )}
          </div>

          {/* Recommendation */}
          <div className="space-y-1.5">
            <div className="flex items-center space-x-1.5 font-bold text-emerald-700 uppercase tracking-wider text-[11px]">
              <Lightbulb className="w-3.5 h-3.5 text-emerald-600" />
              <span>Developer Recommendation</span>
            </div>
            <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-900 font-medium leading-relaxed">
              {issue.recommendation}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

