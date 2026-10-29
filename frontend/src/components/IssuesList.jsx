import React, { useState } from 'react';
import IssueCard from './IssueCard';
import { CheckCircle } from 'lucide-react';

export default function IssuesList({ issues = [] }) {
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedSeverity, setSelectedSeverity] = useState('All');

  const categories = ['All', 'SEO', 'Accessibility', 'Performance', 'Security', 'Functionality'];
  const severities = ['All', 'Critical', 'High', 'Medium', 'Low', 'Info'];

  const filteredIssues = issues.filter((issue) => {
    const matchCat = selectedCategory === 'All' || issue.category === selectedCategory;
    const matchSev = selectedSeverity === 'All' || issue.severity === selectedSeverity;
    return matchCat && matchSev;
  });

  return (
    <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <h3 className="text-base font-extrabold text-slate-900 flex items-center gap-2">
            <span>Detected Technical Issues</span>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-blue-600 text-white shadow-xs">
              {filteredIssues.length}
            </span>
          </h3>
          <p className="text-xs text-slate-500 mt-0.5 font-medium">
            Normalized findings enhanced by AI reasoning & evidence prioritization.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Category Filter */}
          <div className="flex items-center space-x-1 bg-slate-100 p-1 rounded-xl border border-slate-200 text-xs">
            <span className="text-slate-500 px-2 font-bold">Category:</span>
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-2.5 py-1 rounded-lg font-bold transition cursor-pointer ${
                  selectedCategory === cat
                    ? 'bg-slate-900 text-white shadow-xs'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/60'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>

          {/* Severity Filter */}
          <div className="flex items-center space-x-1 bg-slate-100 p-1 rounded-xl border border-slate-200 text-xs">
            <span className="text-slate-500 px-2 font-bold">Severity:</span>
            {severities.map((sev) => (
              <button
                key={sev}
                onClick={() => setSelectedSeverity(sev)}
                className={`px-2.5 py-1 rounded-lg font-bold transition cursor-pointer ${
                  selectedSeverity === sev
                    ? 'bg-slate-900 text-white shadow-xs'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/60'
                }`}
              >
                {sev}
              </button>
            ))}
          </div>
        </div>
      </div>

      {filteredIssues.length === 0 ? (
        <div className="p-8 text-center space-y-3 bg-slate-50 rounded-xl border border-slate-200">
          <CheckCircle className="w-10 h-10 text-emerald-500 mx-auto" />
          <h4 className="text-sm font-bold text-slate-900">No Issues Discovered</h4>
          <p className="text-xs text-slate-500 max-w-sm mx-auto font-medium">
            No technical findings matched the selected category and severity filter criteria.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredIssues.map((issue, idx) => (
            <IssueCard key={issue.id || idx} issue={issue} />
          ))}
        </div>
      )}
    </div>
  );
}

