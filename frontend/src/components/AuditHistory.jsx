import React, { useState } from 'react';
import {
  History,
  ExternalLink,
  Calendar,
  Award,
  Search,
  Trash2,
  RotateCw,
  FileDown,
  AlertTriangle,
} from 'lucide-react';

export default function AuditHistory({
  history = [],
  onSelectAudit,
  onRerunAudit,
  onDeleteAudit,
  onDownloadPdf,
  onSearch,
}) {
  const [searchQuery, setSearchQuery] = useState('');
  const [deleteConfirmId, setDeleteConfirmId] = useState(null);

  const handleSearchChange = (e) => {
    const val = e.target.value;
    setSearchQuery(val);
    if (onSearch) {
      onSearch(val);
    }
  };

  const filteredHistory = history.filter((item) =>
    item.url.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-6">
      {/* Top Header & Search Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <h3 className="text-base font-extrabold text-slate-900 flex items-center gap-2">
            <History className="w-5 h-5 text-blue-600" />
            <span>Audit History Log</span>
          </h3>
          <p className="text-xs text-slate-500 mt-0.5 font-medium">
            Persisted website quality evaluations scoped to your account.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          {/* Search Input */}
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
              <Search className="w-3.5 h-3.5" />
            </div>
            <input
              type="text"
              value={searchQuery}
              onChange={handleSearchChange}
              placeholder="Search by URL..."
              className="pl-8 pr-3 py-1.5 rounded-xl border border-slate-200 bg-slate-50 focus:bg-white text-xs font-medium text-slate-800 focus:outline-hidden focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition w-48 sm:w-60"
            />
          </div>

          <span className="text-xs text-slate-600 font-mono font-bold bg-slate-100 px-3 py-1.5 rounded-xl border border-slate-200 whitespace-nowrap">
            Audits: {history.length}
          </span>
        </div>
      </div>

      {filteredHistory.length === 0 ? (
        <div className="p-12 text-center space-y-3 bg-slate-50 rounded-2xl border border-dashed border-slate-200">
          <History className="w-8 h-8 text-slate-400 mx-auto" />
          <h4 className="text-sm font-bold text-slate-800">No Audits Found</h4>
          <p className="text-xs text-slate-500 max-w-sm mx-auto font-medium">
            {searchQuery
              ? `No audits match the search term "${searchQuery}".`
              : 'You have not executed any website audits yet. Enter a URL above to start!'}
          </p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 uppercase tracking-wider font-bold">
                <th className="py-3.5 px-4 rounded-l-xl">ID</th>
                <th className="py-3.5 px-4">Target Website</th>
                <th className="py-3.5 px-4">Timestamp</th>
                <th className="py-3.5 px-4">Overall Score</th>
                <th className="py-3.5 px-4">Issues</th>
                <th className="py-3.5 px-4 text-right rounded-r-xl">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredHistory.map((item) => (
                <tr key={item.id} className="hover:bg-slate-50/80 transition">
                  <td className="py-3.5 px-4 font-mono font-bold text-slate-700">
                    #{item.id}
                  </td>
                  <td className="py-3.5 px-4 font-bold text-slate-900 max-w-xs truncate">
                    {item.url}
                  </td>
                  <td className="py-3.5 px-4 text-slate-500 font-medium">
                    <span className="flex items-center gap-1.5">
                      <Calendar className="w-3.5 h-3.5 text-slate-400" />
                      {new Date(item.created_at).toLocaleString()}
                    </span>
                  </td>
                  <td className="py-3.5 px-4">
                    <span
                      className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full font-bold border ${
                        item.overall_score >= 80
                          ? 'bg-emerald-100 text-emerald-800 border-emerald-200'
                          : item.overall_score >= 60
                          ? 'bg-amber-100 text-amber-800 border-amber-200'
                          : 'bg-rose-100 text-rose-800 border-rose-200'
                      }`}
                    >
                      <Award className="w-3 h-3" />
                      {Math.round(item.overall_score)} / 100
                    </span>
                  </td>
                  <td className="py-3.5 px-4 font-medium text-slate-600">
                    {item.issues_count !== undefined ? `${item.issues_count} findings` : 'Available'}
                  </td>
                  <td className="py-3.5 px-4 text-right">
                    <div className="flex items-center justify-end space-x-1.5">
                      {/* View Report */}
                      <button
                        onClick={() => onSelectAudit(item.id)}
                        title="View Full Report"
                        className="p-1.5 rounded-lg bg-blue-50 text-blue-600 hover:bg-blue-600 hover:text-white transition font-bold cursor-pointer"
                      >
                        <ExternalLink className="w-3.5 h-3.5" />
                      </button>

                      {/* Download PDF */}
                      <button
                        onClick={() => onDownloadPdf && onDownloadPdf(item.id)}
                        title="Download PDF Report"
                        className="p-1.5 rounded-lg bg-slate-100 text-slate-700 hover:bg-slate-900 hover:text-white transition cursor-pointer"
                      >
                        <FileDown className="w-3.5 h-3.5" />
                      </button>

                      {/* Rerun */}
                      <button
                        onClick={() => onRerunAudit && onRerunAudit(item.id)}
                        title="Rerun Audit"
                        className="p-1.5 rounded-lg bg-slate-100 text-slate-700 hover:bg-emerald-600 hover:text-white transition cursor-pointer"
                      >
                        <RotateCw className="w-3.5 h-3.5" />
                      </button>

                      {/* Delete */}
                      <button
                        onClick={() => setDeleteConfirmId(item.id)}
                        title="Delete Audit"
                        className="p-1.5 rounded-lg bg-rose-50 text-rose-600 hover:bg-rose-600 hover:text-white transition cursor-pointer"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {deleteConfirmId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/70 backdrop-blur-xs">
          <div className="bg-white rounded-2xl max-w-sm w-full p-6 space-y-4 shadow-xl border border-slate-200">
            <div className="flex items-center space-x-3 text-rose-600">
              <div className="p-2 rounded-xl bg-rose-100 text-rose-600">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <h4 className="text-base font-extrabold text-slate-900">Delete Audit #{deleteConfirmId}?</h4>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed font-medium">
              Are you sure you want to delete this website audit record? All associated findings and category metrics will be permanently removed.
            </p>
            <div className="flex items-center justify-end space-x-2 pt-2">
              <button
                onClick={() => setDeleteConfirmId(null)}
                className="px-3.5 py-2 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-100 transition cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={async () => {
                  const id = deleteConfirmId;
                  setDeleteConfirmId(null);
                  if (onDeleteAudit) await onDeleteAudit(id);
                }}
                className="px-4 py-2 rounded-xl text-xs font-bold text-white bg-rose-600 hover:bg-rose-700 transition cursor-pointer"
              >
                Confirm Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
