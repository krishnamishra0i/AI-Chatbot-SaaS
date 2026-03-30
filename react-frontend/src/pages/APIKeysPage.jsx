// API Keys Management Page
import React, { useState } from 'react';

const APIKeysPage = () => {
  const [apiKeys, setApiKeys] = useState([
    {
      id: 1,
      name: 'Production_Main_App',
      created: 'Oct 12, 2023',
      key: 'sk-•••••••••••••4k2j',
      icon: 'terminal',
    },
    {
      id: 2,
      name: 'Staging_Testing',
      created: 'Jan 05, 2024',
      key: 'sk-•••••••••••••9m1s',
      icon: 'science',
    },
    {
      id: 3,
      name: 'Data_Warehouse_Sync',
      created: 'Mar 18, 2024',
      key: 'sk-•••••••••••••2z8h',
      icon: 'webhook',
    },
  ]);

  const copyToClipboard = (key) => {
    navigator.clipboard.writeText(key);
    alert('API Key copied to clipboard!');
  };

  return (
    <div className="pb-24 md:pb-0">
      {/* Header Section */}
      <header className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-10">
        <div>
          <nav className="flex items-center gap-2 text-sm text-on-surface-variant font-label mb-2">
            <span>Account</span>
            <span className="material-symbols-outlined text-sm">chevron_right</span>
            <span className="text-primary font-medium">API Keys</span>
          </nav>
          <h1 className="text-4xl md:text-5xl font-headline font-extrabold tracking-tight text-on-background">
            API Keys
          </h1>
          <p className="text-on-surface-variant mt-2 max-w-xl font-body">
            Manage your application credentials. These keys allow your software to interact with our AI models securely.
          </p>
        </div>
        <button className="bg-primary-container text-on-primary-container px-6 py-3 rounded-full font-label font-bold flex items-center gap-2 shadow-lg shadow-primary-container/20 hover:scale-[1.02] active:scale-95 transition-all w-full md:w-auto justify-center">
          <span className="material-symbols-outlined">add</span>
          Generate New Key
        </button>
      </header>

      {/* Main Content: Bento Grid Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Key Management List */}
        <div className="lg:col-span-8 space-y-4">
          <div className="glass-card rounded-lg p-1 overflow-hidden bg-white/40 backdrop-blur-md border border-white/30">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="text-on-surface-variant border-b border-outline-variant/30 bg-surface-container-low/30">
                    <th className="px-6 py-4 font-headline font-semibold text-sm">Key Name</th>
                    <th className="px-6 py-4 font-headline font-semibold text-sm">Created</th>
                    <th className="px-6 py-4 font-headline font-semibold text-sm">API Key</th>
                    <th className="px-6 py-4 font-headline font-semibold text-sm text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-outline-variant/10">
                  {apiKeys.map((apiKey) => (
                    <tr key={apiKey.id} className="hover:bg-surface-container-low/50 transition-colors">
                      <td className="px-6 py-5">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-full bg-secondary-container/20 flex items-center justify-center">
                            <span className="material-symbols-outlined text-secondary text-sm">
                              {apiKey.icon}
                            </span>
                          </div>
                          <span className="font-semibold text-on-surface">{apiKey.name}</span>
                        </div>
                      </td>
                      <td className="px-6 py-5 text-sm text-on-surface-variant">{apiKey.created}</td>
                      <td className="px-6 py-5">
                        <div className="flex items-center gap-2 group cursor-pointer">
                          <code className="bg-surface-container text-secondary px-3 py-1 rounded-full text-xs font-mono">
                            {apiKey.key}
                          </code>
                          <button
                            onClick={() => copyToClipboard(apiKey.key)}
                            className="material-symbols-outlined text-sm text-on-surface-variant group-hover:text-secondary active:scale-90 transition-all"
                            title="Copy Key"
                          >
                            content_copy
                          </button>
                        </div>
                      </td>
                      <td className="px-6 py-5 text-right">
                        <button className="material-symbols-outlined text-on-surface-variant hover:text-error transition-colors">
                          delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Info Banner */}
          <div className="bg-secondary-container/10 border border-secondary-container/30 p-6 rounded-lg flex gap-4 items-start">
            <span className="material-symbols-outlined text-secondary">info</span>
            <div>
              <h4 className="font-headline font-bold text-secondary mb-1">
                Key Security Best Practices
              </h4>
              <p className="text-sm text-on-secondary-container leading-relaxed">
                Do not share your API keys in public repositories or client-side code. If you suspect a key has
                been compromised, rotate it immediately by generating a new one and deleting the old.
              </p>
            </div>
          </div>
        </div>

        {/* Stats/Context Cards Sidebar */}
        <div className="lg:col-span-4 space-y-6">
          {/* Usage Card */}
          <div className="glass-card rounded-lg p-6 relative overflow-hidden group bg-white/40 backdrop-blur-md border border-white/30">
            <div className="absolute top-0 right-0 p-8 opacity-10 transform translate-x-4 -translate-y-4">
              <span className="material-symbols-outlined text-[80px]" style={{ fontVariationSettings: "'FILL' 1" }}>
                bolt
              </span>
            </div>
            <h3 className="font-headline font-bold text-lg mb-4">Total API Calls</h3>
            <div className="flex items-end gap-2 mb-2">
              <span className="text-4xl font-extrabold text-on-background">128.4k</span>
              <span className="text-primary font-bold text-sm mb-1">+14% vs last mo</span>
            </div>
            <div className="w-full bg-surface-container-high rounded-full h-2 mb-4 overflow-hidden">
              <div className="bg-primary h-full rounded-full" style={{ width: '72%' }} />
            </div>
            <p className="text-xs text-on-surface-variant uppercase tracking-widest font-bold">
              Quota: 175k / Month
            </p>
          </div>

          {/* Active Endpoints */}
          <div className="bg-white rounded-lg p-6 shadow-sm border border-outline-variant/20">
            <h3 className="font-headline font-bold text-lg mb-4">Active Endpoints</h3>
            <div className="space-y-4">
              {[
                { name: 'Text Analysis V4', status: 'Live' },
                { name: 'Image Generation', status: 'Live' },
                { name: 'Audio Transcribe', status: 'Idle' },
              ].map((endpoint, idx) => (
                <div key={idx} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span
                      className={`w-2 h-2 rounded-full ${
                        endpoint.status === 'Live'
                          ? 'bg-primary ring-4 ring-primary-container/20'
                          : 'bg-outline'
                      }`}
                    />
                    <span className="text-sm font-medium">{endpoint.name}</span>
                  </div>
                  <span className="text-xs font-mono text-on-surface-variant">{endpoint.status}</span>
                </div>
              ))}
            </div>
            <button className="w-full mt-6 py-2 rounded-full border border-primary text-primary font-label text-sm font-semibold hover:bg-primary/5 transition-colors">
              View Dashboard
            </button>
          </div>

          {/* Visual Banner */}
          <div className="rounded-lg h-48 relative overflow-hidden group">
            <img
              alt="Data Visualization"
              className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700"
              src="https://lh3.googleusercontent.com/aida-public/AB6AXuCBLy1qH8RyciE1minS8fIqLk5dXq2UIhNwpemaxr92YT3EWK5lEdCCJ-H8lnPcCMg91HYtElVz0eV09aNdyo2RYK6PeAeHGB68CUJt8ZmG6MAL41-rB6q2pkZitQh_aueP5lLd62lE_eO26leqOqicNlVoVog2v1Xe2c73Bpq1O6cr6v3S8diWZasWesxJaLkPf1cyokwln9njr_e3mBoxaDCcijGCRg71LOZDoxE5VA8WH2Yu7FMIoLGCAILSZiN8m1aToFEViTW0"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent flex items-end p-4">
              <p className="text-white text-sm font-headline font-semibold">Integrate our SDKs in minutes</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default APIKeysPage;
