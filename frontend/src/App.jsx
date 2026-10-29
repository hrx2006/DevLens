import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import UrlInput from './components/UrlInput';
import ScanProgress from './components/ScanProgress';
import ScoreGauge from './components/ScoreGauge';
import CategoryCards from './components/CategoryCards';
import IssuesList from './components/IssuesList';
import AuditHistory from './components/AuditHistory';
import FutureScopeNotice from './components/FutureScopeNotice';
import LoginPage from './components/LoginPage';
import RegisterPage from './components/RegisterPage';
import { useAuth } from './context/AuthContext';
import {
  runAudit,
  fetchAuditHistory,
  fetchAuditDetail,
  deleteAudit,
  rerunAudit,
  downloadAuditPdf,
} from './services/api';
import {
  AlertCircle,
  CheckCircle,
  Info,
  FileDown,
  RotateCw,
  Trash2,
  ExternalLink,
  Cpu,
  Loader2,
} from 'lucide-react';

export default function App() {
  const { user, isAuthenticated, isLoadingAuth } = useAuth();
  const [authView, setAuthView] = useState('login'); // 'login' | 'register'
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isLoading, setIsLoading] = useState(false);
  const [isExportingPdf, setIsExportingPdf] = useState(false);
  const [scanStage, setScanStage] = useState('idle');
  const [currentAudit, setCurrentAudit] = useState(null);
  const [history, setHistory] = useState([]);
  const [errorMessage, setErrorMessage] = useState('');
  const [infoMessage, setInfoMessage] = useState('');

  // Reload history whenever user authentication state changes or on initial mount
  useEffect(() => {
    loadHistory();
  }, [isAuthenticated, user?.id]);

  const loadHistory = async (searchQuery = '') => {
    try {
      const data = await fetchAuditHistory(searchQuery);
      setHistory(data || []);
    } catch (err) {
      console.error('Failed to load audit history:', err);
    }
  };

  const handleStartAudit = async (targetUrl) => {
    setIsLoading(true);
    setErrorMessage('');
    setInfoMessage('');
    setCurrentAudit(null);

    // Live sequential progress stage transitions
    setScanStage('validating');
    await new Promise((r) => setTimeout(r, 300));

    setScanStage('crawling');
    await new Promise((r) => setTimeout(r, 500));

    setScanStage('seo');
    await new Promise((r) => setTimeout(r, 300));

    setScanStage('accessibility');
    await new Promise((r) => setTimeout(r, 300));

    setScanStage('performance');
    await new Promise((r) => setTimeout(r, 300));

    setScanStage('security');
    await new Promise((r) => setTimeout(r, 300));

    setScanStage('functionality');
    await new Promise((r) => setTimeout(r, 300));

    setScanStage('ai');

    try {
      const auditResult = await runAudit(targetUrl);
      setScanStage('completed');
      setCurrentAudit(auditResult);
      setActiveTab('dashboard');
      await loadHistory();
      setInfoMessage(`Audit scan completed successfully for ${auditResult.url}`);
    } catch (err) {
      setScanStage('idle');
      setErrorMessage(err.message || 'An unexpected error occurred during the audit scan.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectAuditFromHistory = async (auditId) => {
    setIsLoading(true);
    setErrorMessage('');
    try {
      const detail = await fetchAuditDetail(auditId);
      setCurrentAudit(detail);
      setActiveTab('dashboard');
    } catch (err) {
      setErrorMessage(err.message || 'Failed to load audit details.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRerunAudit = async (auditId) => {
    if (!isAuthenticated) {
      setErrorMessage('Please sign in to rerun saved audits.');
      return;
    }
    setIsLoading(true);
    setErrorMessage('');
    setInfoMessage('');
    try {
      const newAudit = await rerunAudit(auditId);
      setCurrentAudit(newAudit);
      setActiveTab('dashboard');
      await loadHistory();
      setInfoMessage(`Audit rerun completed for ${newAudit.url}`);
    } catch (err) {
      setErrorMessage(err.message || 'Failed to rerun audit.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteAudit = async (auditId) => {
    if (!isAuthenticated) {
      setErrorMessage('Please sign in to delete saved audits.');
      return;
    }
    try {
      await deleteAudit(auditId);
      if (currentAudit && currentAudit.id === auditId) {
        setCurrentAudit(null);
      }
      await loadHistory();
      setInfoMessage(`Audit #${auditId} deleted successfully.`);
    } catch (err) {
      setErrorMessage(err.message || 'Failed to delete audit.');
    }
  };

  const handleDownloadPdf = async (auditId) => {
    if (!isAuthenticated) {
      setErrorMessage('Please sign in or create an account to export downloadable PDF reports.');
      return;
    }
    setIsExportingPdf(true);
    try {
      await downloadAuditPdf(auditId);
      setInfoMessage('PDF audit report downloaded successfully.');
    } catch (err) {
      setErrorMessage(err.message || 'Failed to generate PDF report.');
    } finally {
      setIsExportingPdf(false);
    }
  };

  // 1. Initial Authentication Verification Loading Splash (prevents any flash of protected content)
  if (isLoadingAuth) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-slate-900 text-white p-4 selection:bg-blue-500 selection:text-white">
        <div className="flex flex-col items-center space-y-4 max-w-sm text-center">
          <div className="p-4 rounded-2xl bg-blue-600/20 border border-blue-500/30 text-blue-400 shadow-2xl animate-pulse">
            <Cpu className="w-10 h-10" />
          </div>
          <div className="space-y-1">
            <h1 className="text-xl font-black tracking-tight text-white">
              DevLens <span className="text-blue-400">AI</span>
            </h1>
            <p className="text-xs text-slate-400 font-medium">
              Verifying secure authentication session...
            </p>
          </div>
          <div className="pt-2 flex items-center space-x-2 text-xs text-blue-400 font-semibold">
            <Loader2 className="w-4 h-4 animate-spin text-blue-400" />
            <span>Establishing credentials...</span>
          </div>
        </div>
      </div>
    );
  }

  // 2. Login-First Guard: Unauthenticated users MUST authenticate before viewing the dashboard
  if (!isAuthenticated) {
    if (authView === 'register') {
      return <RegisterPage onSwitchToLogin={() => setAuthView('login')} />;
    }
    return <LoginPage onSwitchToRegister={() => setAuthView('register')} />;
  }

  // 3. Protected Dashboard: Rendered strictly for authenticated sessions
  return (
    <div className="min-h-screen flex flex-col bg-slate-100/80 text-slate-900 font-sans">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      <main className="flex-grow max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Error Notification */}
        {errorMessage && (
          <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center justify-between shadow-sm">
            <div className="flex items-center space-x-3">
              <AlertCircle className="w-5 h-5 text-rose-600 flex-shrink-0" />
              <div>
                <strong className="font-semibold">Audit Notice: </strong>
                <span>{errorMessage}</span>
              </div>
            </div>
            <button
              onClick={() => setErrorMessage('')}
              className="text-rose-600 hover:text-rose-800 font-bold px-2 cursor-pointer"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Info Notification */}
        {infoMessage && (
          <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-center justify-between shadow-sm">
            <div className="flex items-center space-x-3">
              <CheckCircle className="w-5 h-5 text-emerald-600 flex-shrink-0" />
              <span>{infoMessage}</span>
            </div>
            <button
              onClick={() => setInfoMessage('')}
              className="text-emerald-600 hover:text-emerald-800 font-bold px-2 cursor-pointer"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* URL Input Form */}
        <UrlInput onStartAudit={handleStartAudit} isLoading={isLoading} />

        {/* Scanner Pipeline Progress */}
        {(isLoading || scanStage !== 'idle') && <ScanProgress stage={scanStage} />}

        {/* Dashboard View */}
        {activeTab === 'dashboard' && (
          <div className="space-y-8">
            {currentAudit ? (
              <>
                {/* Score & Metadata Overview */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-stretch">
                  <div className="lg:col-span-1">
                    <ScoreGauge score={currentAudit.overall_score} />
                  </div>

                  <div className="lg:col-span-2 bg-white p-6 rounded-2xl border border-slate-200 flex flex-col justify-between space-y-4 shadow-sm">
                    <div>
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <span className="text-xs uppercase tracking-wider font-bold text-slate-500">
                          Target Website Metadata
                        </span>
                        <div className="flex items-center space-x-2">
                          <span className="px-3 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200">
                            Audit Completed
                          </span>

                          {/* Quick Action: PDF Export */}
                          <button
                            onClick={() => handleDownloadPdf(currentAudit.id)}
                            disabled={isExportingPdf}
                            className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold bg-slate-900 hover:bg-slate-800 text-white shadow-xs transition disabled:opacity-50 cursor-pointer"
                          >
                            <FileDown className="w-3.5 h-3.5" />
                            <span>{isExportingPdf ? 'Exporting...' : 'Export PDF'}</span>
                          </button>

                          {/* Quick Action: Rerun */}
                          <button
                            onClick={() => handleRerunAudit(currentAudit.id)}
                            title="Rerun Audit"
                            className="p-1.5 rounded-full bg-slate-100 text-slate-700 hover:bg-emerald-600 hover:text-white transition cursor-pointer"
                          >
                            <RotateCw className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>

                      <h2 className="text-xl font-extrabold text-slate-900 mt-2 break-all">
                        {currentAudit.url}
                      </h2>
                      <p className="text-xs text-slate-500 mt-1 font-medium">
                        Audited on {new Date(currentAudit.created_at).toLocaleString()} | Audit ID #{currentAudit.id}
                      </p>
                    </div>

                    {/* Quick Metric Pills */}
                    <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 pt-4 border-t border-slate-100 text-center">
                      <div className="p-2.5 rounded-xl bg-slate-900 text-white shadow-xs border border-slate-800">
                        <span className="block text-[10px] text-slate-400 font-medium">SEO</span>
                        <span className="text-base font-extrabold text-white mt-0.5 block">
                          {Math.round(currentAudit.seo_score || 0)}
                        </span>
                      </div>
                      <div className="p-2.5 rounded-xl bg-slate-900 text-white shadow-xs border border-slate-800">
                        <span className="block text-[10px] text-slate-400 font-medium">Accessibility</span>
                        <span className="text-base font-extrabold text-white mt-0.5 block">
                          {Math.round(currentAudit.accessibility_score || 0)}
                        </span>
                      </div>
                      <div className="p-2.5 rounded-xl bg-slate-900 text-white shadow-xs border border-slate-800">
                        <span className="block text-[10px] text-slate-400 font-medium">Performance</span>
                        <span className="text-base font-extrabold text-white mt-0.5 block">
                          {Math.round(currentAudit.performance_score || 0)}
                        </span>
                      </div>
                      <div className="p-2.5 rounded-xl bg-slate-900 text-white shadow-xs border border-slate-800">
                        <span className="block text-[10px] text-slate-400 font-medium">Security</span>
                        <span className="text-base font-extrabold text-white mt-0.5 block">
                          {Math.round(currentAudit.security_score || 0)}
                        </span>
                      </div>
                      <div className="p-2.5 rounded-xl bg-slate-900 text-white shadow-xs border border-slate-800 col-span-2 sm:col-span-1">
                        <span className="block text-[10px] text-slate-400 font-medium">Functionality</span>
                        <span className="text-base font-extrabold text-white mt-0.5 block">
                          {Math.round(currentAudit.functionality_score || 0)}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* 5-Category Detailed Cards */}
                <CategoryCards
                  seoScore={currentAudit.seo_score}
                  accessibilityScore={currentAudit.accessibility_score}
                  performanceScore={currentAudit.performance_score}
                  securityScore={currentAudit.security_score}
                  functionalityScore={currentAudit.functionality_score}
                />

                {/* Findings & AI Reasoning List */}
                <IssuesList issues={currentAudit.issues || []} />
              </>
            ) : (
              <div className="bg-white p-12 rounded-2xl border border-slate-200 text-center space-y-4 shadow-sm">
                <div className="w-16 h-16 rounded-2xl bg-blue-50 border border-blue-200 text-blue-600 flex items-center justify-center mx-auto shadow-inner">
                  <Info className="w-8 h-8" />
                </div>
                <h3 className="text-lg font-bold text-slate-900">Ready to Audit Target Website</h3>
                <p className="text-xs text-slate-600 max-w-md mx-auto leading-relaxed">
                  Enter a target website URL in the search bar above or click{' '}
                  <strong className="text-slate-900">"Test Built-In Demo Website"</strong> to run an automated
                  evaluation across SEO, Accessibility, Performance, Security, and Functionality.
                </p>
              </div>
            )}

            <FutureScopeNotice />
          </div>
        )}

        {/* Audit History Tab */}
        {activeTab === 'history' && (
          <AuditHistory
            history={history}
            onSelectAudit={handleSelectAuditFromHistory}
            onRerunAudit={handleRerunAudit}
            onDeleteAudit={handleDeleteAudit}
            onDownloadPdf={handleDownloadPdf}
            onSearch={loadHistory}
          />
        )}
      </main>

      <footer className="border-t border-slate-800 bg-slate-900 py-6 text-center text-xs text-slate-400 font-medium">
        <p>DevLens AI — Intelligent Website Audit & Quality Assurance Platform</p>
      </footer>
    </div>
  );
}
