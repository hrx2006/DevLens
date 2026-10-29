import React from 'react';
import { Layers, CheckCircle2, Cloud, Bell, Clock, Compass } from 'lucide-react';

export default function FutureScopeNotice() {
  const completed = [
    { title: 'Deterministic Security Scanner', desc: 'Passive SSL, HSTS, CSP, X-Frame, nosniff & mixed-content audits' },
    { title: 'Safe Functionality Scanner', desc: 'Dead anchor inspection, form action/method hygiene & GET password detection' },
    { title: 'Downloadable PDF Audit Reports', desc: 'Branded multi-page executive audit reports via ReportLab' },
    { title: 'Enterprise User Authentication', desc: 'Argon2id hashing, HttpOnly session cookies & strict data isolation' },
  ];

  const upcoming = [
    { icon: Clock, title: 'Scheduled Recurring Audits', desc: 'Automated weekly website quality monitoring' },
    { icon: Bell, title: 'Webhook & Slack Alerts', desc: 'Instant notifications on critical score drops' },
    { icon: Compass, title: 'Deep Multi-Page Crawl Engine', desc: 'Configurable sitemap.xml tree exploration' },
    { icon: Cloud, title: 'AWS / GCP Cloud Clusters', desc: 'Distributed scanning workers for high-volume auditing' },
  ];

  return (
    <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
      <div className="flex items-center space-x-2 text-slate-900">
        <div className="p-2 rounded-xl bg-blue-50 border border-blue-200 text-blue-600">
          <Layers className="w-5 h-5" />
        </div>
        <div>
          <h3 className="text-base font-extrabold text-slate-900">Platform Architecture & Roadmap</h3>
          <p className="text-xs text-slate-500 font-medium">
            Overview of recently delivered production modules and upcoming engineering milestones.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
        {/* Completed Modules */}
        <div className="p-4 rounded-2xl bg-emerald-50/50 border border-emerald-200 space-y-3">
          <h4 className="text-xs font-extrabold text-emerald-900 flex items-center gap-1.5 uppercase tracking-wider">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <span>Delivered & Active Modules</span>
          </h4>
          <div className="space-y-2.5">
            {completed.map((item) => (
              <div key={item.title} className="text-xs">
                <span className="font-bold text-slate-900">{item.title}: </span>
                <span className="text-slate-600 font-medium">{item.desc}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Upcoming Milestones */}
        <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-3">
          <h4 className="text-xs font-extrabold text-slate-700 flex items-center gap-1.5 uppercase tracking-wider">
            <Layers className="w-4 h-4 text-slate-500" />
            <span>Upcoming Roadmap Milestones</span>
          </h4>
          <div className="space-y-2.5">
            {upcoming.map((item) => {
              const Icon = item.icon;
              return (
                <div key={item.title} className="flex items-start space-x-2 text-xs">
                  <Icon className="w-4 h-4 text-slate-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <span className="font-bold text-slate-900">{item.title}: </span>
                    <span className="text-slate-500 font-medium">{item.desc}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
