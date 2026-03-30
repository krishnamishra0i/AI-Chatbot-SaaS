// Main Layout wrapper for AI Solutions Dashboard
import React from 'react';

const AILayout = ({ children, currentTab, setCurrentTab, onNavigate }) => {
  const tabs = [
    { id: 'overview', label: 'Overview', icon: 'dashboard' },
    { id: 'chatbots', label: 'Chatbots', icon: 'forum' },
    { id: 'api-keys', label: 'API Keys', icon: 'vpn_key' },
    { id: 'usage', label: 'Usage', icon: 'bar_chart' },
  ];

  return (
    <div className="min-h-screen bg-background font-body text-on-background">
      {/* TopAppBar */}
      <header className="bg-white/70 dark:bg-slate-900/70 backdrop-blur-md border-b border-white/20 dark:border-slate-800/50 shadow-sm sticky top-0 z-50">
        <div className="flex justify-between items-center w-full px-6 py-4 max-w-7xl mx-auto">
          <div className="flex items-center gap-3">
            {onNavigate && (
              <button
                onClick={() => onNavigate('home')}
                className="inline-flex items-center gap-1 rounded-lg border border-slate-200 bg-white/80 px-3 py-1.5 text-xs font-semibold text-slate-700 transition-colors hover:bg-slate-100"
                aria-label="Back to home"
                title="Back to Home"
              >
                <span className="material-symbols-outlined text-base">arrow_back</span>
                Home
              </button>
            )}
            <span className="material-symbols-outlined text-cyan-500 dark:text-cyan-400 text-2xl">
              smart_toy
            </span>
            <h1 className="text-xl font-bold text-cyan-600 dark:text-cyan-400 font-headline">
              AI Solutions
            </h1>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-8">
            {tabs.map((tab) => (
              <a
                key={tab.id}
                onClick={() => setCurrentTab(tab.id)}
                className={`text-[14px] font-headline font-semibold transition-colors cursor-pointer ${
                  currentTab === tab.id
                    ? 'text-cyan-600 dark:text-cyan-400 border-b-2 border-cyan-500 pb-1'
                    : 'text-slate-500 dark:text-slate-400 hover:text-cyan-500 dark:hover:text-cyan-300'
                }`}
              >
                {tab.label}
              </a>
            ))}
          </nav>

          <div className="flex items-center gap-4">
            <button className="material-symbols-outlined text-on-surface-variant hover:text-primary transition-colors">
              notifications
            </button>
            <div className="w-10 h-10 rounded-full bg-secondary-container flex items-center justify-center overflow-hidden border-2 border-white shadow-sm">
              <img
                alt="User Profile"
                className="w-full h-full object-cover"
                src="https://lh3.googleusercontent.com/aida-public/AB6AXuAb4OP-yutlRglvqYTreYMNRWFTcP3G_KQuMWqyr0C1pfCnai-v-pIfTT_HwDYv5HhaqSO2WPrUtKp2kAk-q38Glg3tw4YD1NsorhbgUHLW0j2bYlNzaEHQ19sfTg9fKd6BhNMMIy4KEJ2lHXi3o47d5EP67l7kgUA6IsuPBetDA2kfI8eBPN1x7sIO57dOiJC_e6g0QcEkRvhUL7nvyxlYYHN_PDsaDWqWtXtoaXYBg2RCDoxo5XnWw-xwq8hHElFYVuRLI48fNq98"
              />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">{children}</main>

      {/* Bottom Navigation Bar (Mobile Only) */}
      <nav className="fixed bottom-0 left-0 w-full z-50 flex justify-around items-center px-4 pb-6 pt-3 bg-white/80 dark:bg-slate-900/80 backdrop-blur-lg border-t border-white/30 dark:border-slate-800/50 shadow-[0_-4px_20px_rgba(0,0,0,0.05)] md:hidden rounded-t-[32px]">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setCurrentTab(tab.id)}
            className={`flex flex-col items-center justify-center px-5 py-2 rounded-full transition-all active:scale-90 ${
              currentTab === tab.id
                ? 'bg-cyan-50 dark:bg-cyan-900/30 text-cyan-600 dark:text-cyan-300'
                : 'text-slate-500 dark:text-slate-400 hover:bg-slate-100/50 dark:hover:bg-slate-800/50'
            }`}
          >
            <span className="material-symbols-outlined text-xl">{tab.icon}</span>
            <span className="text-[11px] font-medium font-['Plus_Jakarta_Sans'] mt-1">{tab.label}</span>
          </button>
        ))}
      </nav>
    </div>
  );
};

export default AILayout;
