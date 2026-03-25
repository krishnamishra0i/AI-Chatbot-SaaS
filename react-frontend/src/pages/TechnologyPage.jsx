import React, { useState } from 'react';
import './TechnologyPage.css';

const TechnologyPage = ({ onNavigate = () => {}, onLaunchDemo = () => {} }) => {
  const [copiedSnippet, setCopiedSnippet] = useState(false);

  const pipelineStages = [
    {
      id: 1,
      title: 'Audio Ingest',
      subtitle: 'Live Stream',
      icon: 'mic_external_on',
      color: 'brand-emerald',
      glassDark: false,
    },
    {
      id: 2,
      title: 'Neural STT',
      subtitle: 'DeepGram Pro',
      icon: 'waves',
      color: 'brand-blue',
      glassDark: false,
    },
    {
      id: 3,
      title: 'Athena Core',
      subtitle: 'Logic Layer',
      icon: 'neurology',
      color: 'core',
      glassDark: true,
      isCoreNode: true,
    },
    {
      id: 4,
      title: 'Viseme Sync',
      subtitle: 'Zero Latency',
      icon: 'face_6',
      color: 'brand-blue',
      glassDark: false,
    },
    {
      id: 5,
      title: 'UE5 Render',
      subtitle: 'Pixel Stream',
      icon: 'deployed_code',
      color: 'brand-emerald',
      glassDark: false,
    },
  ];

  const productOptions = [
    {
      icon: 'widgets',
      title: 'Prebuilt Widget',
      description: 'Fastest deployment with a simple iframe or JS snippet. Ready in under 5 minutes.',
      badge: 'LOW CODE',
      featured: false,
    },
    {
      icon: 'dns',
      title: 'Hosted Pipeline',
      description: 'Customize the full UI experience while we handle the heavy GPU orchestration.',
      badge: 'CUSTOM UI',
      featured: true,
    },
    {
      icon: 'terminal',
      title: 'Self-Managed',
      description: 'Total stack control. Deploy in your own VPC for absolute data sovereignty.',
      badge: 'FULL CONTROL',
      featured: false,
    },
  ];

  const comparisonFeatures = [
    {
      feature: 'Ultra-low Latency Video',
      prebuilt: true,
      hosted: true,
      managed: true,
    },
    {
      feature: 'Custom Avatar Uploads',
      prebuilt: false,
      hosted: true,
      managed: true,
    },
    {
      feature: 'Proprietary LLM Connect',
      prebuilt: false,
      hosted: true,
      managed: true,
    },
    {
      feature: 'Dedicated GPU Infrastructure',
      prebuilt: false,
      hosted: false,
      managed: true,
    },
  ];

  const codeSnippet = `const options = {
  method: 'POST',
  headers: {
    'X-API-Key': '<api-key>',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    agent_image_url: 'https://cdn.lemonslice.com/agents/custom_agent.png',
    agent_prompt: 'A friendly and smiling person.',
    transport_type: 'livekit',
    properties: {
      livekit_url: 'wss://lemonslice-pb123.livekit.cloud',
      livekit_token: 'eyJhbGciOiJIUzI1NiIsInR5...'
    }
  })
};`;

  const handleCopySnippet = () => {
    navigator.clipboard.writeText(codeSnippet);
    setCopiedSnippet(true);
    setTimeout(() => setCopiedSnippet(false), 2000);
  };

  return (
    <div className="bg-background font-body text-on-surface min-h-screen">
      {/* TopAppBar */}
      <header className="fixed top-0 w-full z-50 bg-white/60 backdrop-blur-xl border-b border-white/20">
        <div className="flex items-center justify-between px-6 py-4 max-w-7xl mx-auto">
          <div className="flex items-center gap-2">
            <span
              className="material-symbols-outlined text-brand-emerald"
              style={{ fontSize: '32px', fontVariationSettings: "'FILL' 1" }}
            >
              dataset_lock
            </span>
            <span className="text-2xl font-extrabold tracking-tight text-slate-900 font-headline">
              AIVision
            </span>
          </div>
          <nav className="hidden md:flex items-center gap-8">
            <button
              onClick={() => onNavigate('technology')}
              className="text-brand-emerald font-bold font-label transition-colors"
            >
              Technology
            </button>
            <a href="#" className="text-slate-500 hover:text-brand-emerald transition-colors font-label font-medium">
              Pricing
            </a>
            <a href="#" className="text-slate-500 hover:text-brand-emerald transition-colors font-label font-medium">
              Documentation
            </a>
          </nav>
          <div className="flex items-center gap-4">
            <button className="bg-slate-900 text-white px-5 py-2 rounded-full text-sm font-bold font-label active:scale-95 transition-all">
              Console
            </button>
          </div>
        </div>
      </header>

      <main className="pt-24 pb-12 px-4 max-w-7xl mx-auto space-y-32">
        {/* Hero Section */}
        <section className="text-center py-16 px-6 relative overflow-hidden">
          <div className="absolute -top-24 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-brand-emerald/10 blur-[120px] -z-10 rounded-full"></div>
          <h1 className="text-5xl md:text-7xl font-extrabold font-headline text-on-background tracking-tighter mb-6">
            The <span className="gradient-text">Athena</span> Pipeline
          </h1>
          <p className="text-lg md:text-xl text-outline max-w-2xl mx-auto leading-relaxed font-medium">
            Proprietary real-time engine translating speech to hyper-realistic 3D interaction in under 120ms.
          </p>
        </section>

        {/* Pipeline Visual */}
        <section className="relative">
          <div className="flex flex-col gap-12 md:flex-row md:justify-between items-center relative py-12">
            {/* Connector Line (Desktop) */}
            <div className="hidden md:block absolute top-[44px] left-0 w-full h-[2px] bg-gradient-to-r from-transparent via-brand-emerald/30 to-transparent -z-10"></div>

            {/* Pipeline Stages */}
            {pipelineStages.map((stage) => (
              <div key={stage.id} className="flex flex-col items-center group w-full md:w-1/5">
                {stage.isCoreNode ? (
                  <>
                    <div className="absolute -inset-4 bg-brand-emerald/20 blur-2xl rounded-full opacity-0 group-hover:opacity-100 transition-opacity"></div>
                    <div className="w-24 h-24 rounded-3xl bg-slate-900 flex items-center justify-center text-white shadow-2xl group-hover:scale-110 group-hover:-translate-y-2 transition-all duration-500 ring-4 ring-brand-emerald/20 relative z-10">
                      <span className="material-symbols-outlined text-5xl text-brand-emerald" style={{ fontVariationSettings: "'FILL' 1" }}>
                        {stage.icon}
                      </span>
                    </div>
                    <div className="mt-6 text-center">
                      <h4 className="font-headline font-extrabold text-on-surface text-lg">{stage.title}</h4>
                      <p className="text-[11px] text-brand-emerald font-bold font-label uppercase tracking-widest mt-1">
                        {stage.subtitle}
                      </p>
                    </div>
                  </>
                ) : (
                  <>
                    <div
                      className={`w-20 h-20 rounded-2xl glass-card flex items-center justify-center shadow-2xl group-hover:scale-110 group-hover:-translate-y-2 transition-all duration-500 ${
                        stage.color === 'brand-emerald' ? 'text-brand-emerald' : 'text-brand-blue'
                      }`}
                    >
                      <span className="material-symbols-outlined text-4xl">{stage.icon}</span>
                    </div>
                    <div className="mt-6 text-center">
                      <h4 className="font-headline font-extrabold text-on-surface">{stage.title}</h4>
                      <p className={`text-[11px] font-bold font-label uppercase tracking-widest mt-1 ${stage.color === 'brand-emerald' ? 'text-brand-emerald' : 'text-outline'}`}>
                        {stage.subtitle}
                      </p>
                    </div>
                  </>
                )}
              </div>
            ))}
          </div>
        </section>

        {/* Build with our API Section */}
        <section className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div className="space-y-6">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-brand-emerald/10 text-brand-emerald rounded-full text-xs font-bold font-label uppercase tracking-widest">
              <span className="material-symbols-outlined text-sm">code</span>
              Developer First
            </div>
            <h2 className="text-4xl font-extrabold font-headline text-on-background leading-tight">
              Build with our <span className="text-brand-blue">Next-Gen</span> API
            </h2>
            <p className="text-lg text-outline leading-relaxed">
              Integrate high-fidelity AI avatars into your own platform in minutes. Our REST API and SDKs provide full control over agent behavior, transport protocols, and visual properties.
            </p>
            <div className="flex flex-wrap gap-4 pt-4">
              <button className="bg-slate-900 text-white px-8 py-4 rounded-full font-bold font-label hover:shadow-lg hover:shadow-slate-900/20 active:scale-95 transition-all flex items-center gap-2">
                Get API Key <span className="material-symbols-outlined text-xl">arrow_right_alt</span>
              </button>
              <button className="bg-white border border-slate-200 text-slate-900 px-8 py-4 rounded-full font-bold font-label hover:bg-slate-50 transition-all flex items-center gap-2">
                Read the docs <span className="material-symbols-outlined text-xl">menu_book</span>
              </button>
            </div>
          </div>

          {/* Code Block */}
          <div className="glass-dark rounded-2xl overflow-hidden shadow-2xl border border-white/10 group">
            {/* Code Window Header */}
            <div className="bg-slate-800/50 px-6 py-3 flex items-center justify-between border-b border-white/5">
              <div className="flex gap-2">
                <div className="w-3 h-3 rounded-full bg-red-500/50"></div>
                <div className="w-3 h-3 rounded-full bg-yellow-500/50"></div>
                <div className="w-3 h-3 rounded-full bg-green-500/50"></div>
              </div>
              <span className="text-[10px] text-slate-400 font-mono uppercase tracking-widest">POST /v1/agents/spawn</span>
            </div>

            {/* Syntax Highlighted Code */}
            <div className="p-6 font-mono text-[13px] leading-relaxed overflow-x-auto">
              <pre className="text-slate-300 whitespace-pre-wrap break-words">{codeSnippet}</pre>
            </div>

            {/* Copy Button */}
            <div className="px-6 py-4 bg-slate-800/20 border-t border-white/5 flex justify-end">
              <button
                onClick={handleCopySnippet}
                className="text-slate-400 hover:text-white transition-colors flex items-center gap-2 text-xs font-bold font-label"
              >
                <span className="material-symbols-outlined text-sm">{copiedSnippet ? 'check' : 'content_copy'}</span>
                {copiedSnippet ? 'Copied!' : 'Copy Snippet'}
              </button>
            </div>
          </div>
        </section>

        {/* Product Selection Section */}
        <section className="space-y-16">
          <div className="text-center space-y-4">
            <h2 className="text-4xl font-extrabold font-headline text-on-background">Choose your integration level</h2>
            <p className="text-outline font-medium max-w-xl mx-auto">From no-code widgets to full-scale enterprise infra.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {productOptions.map((option, idx) => (
              <div
                key={idx}
                className={`p-10 rounded-2xl flex flex-col items-center text-center space-y-6 transition-all ${
                  option.featured
                    ? 'bg-slate-900 scale-105 shadow-[0_30px_60px_-12px_rgba(0,200,151,0.25)] relative group overflow-hidden'
                    : 'glass-card hover:shadow-2xl hover:shadow-brand-emerald/10 group'
                }`}
              >
                {option.featured && (
                  <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-brand-emerald to-brand-blue"></div>
                )}

                <div
                  className={`w-16 h-16 rounded-2xl flex items-center justify-center transition-colors duration-500 ${
                    option.featured
                      ? 'bg-brand-emerald text-white shadow-lg shadow-brand-emerald/20'
                      : option.icon === 'widgets'
                      ? 'bg-brand-emerald/10 text-brand-emerald group-hover:bg-brand-emerald group-hover:text-white'
                      : 'bg-brand-blue/10 text-brand-blue group-hover:bg-brand-blue group-hover:text-white'
                  }`}
                >
                  <span className="material-symbols-outlined text-4xl">{option.icon}</span>
                </div>

                <h3 className={`text-2xl font-extrabold font-headline ${option.featured ? 'text-white' : ''}`}>
                  {option.title}
                </h3>

                <p className={`text-sm leading-relaxed font-medium ${option.featured ? 'text-slate-400' : 'text-outline'}`}>
                  {option.description}
                </p>

                <div className={`w-full h-px ${option.featured ? 'bg-white/10' : 'bg-slate-200/50'} my-2`}></div>

                <span
                  className={`px-4 py-1.5 rounded-full text-[10px] font-black tracking-tighter uppercase ${
                    option.featured ? 'bg-brand-emerald/20 text-brand-emerald' : 'bg-slate-100 text-slate-500'
                  }`}
                >
                  {option.badge}
                </span>
              </div>
            ))}
          </div>
        </section>

        {/* Comparison Table */}
        <section>
          <div className="glass-card rounded-3xl overflow-hidden border border-slate-200/50 shadow-xl">
            <table className="w-full text-left">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200/60">
                  <th className="px-8 py-6 font-headline text-slate-900 font-extrabold">Service Matrix</th>
                  <th className="px-8 py-6 font-headline text-slate-900 font-extrabold text-center">Prebuilt</th>
                  <th className="px-8 py-6 font-headline text-brand-emerald font-extrabold text-center">Hosted</th>
                  <th className="px-8 py-6 font-headline text-slate-900 font-extrabold text-center">Managed</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {comparisonFeatures.map((row, idx) => (
                  <tr key={idx} className="hover:bg-slate-50/50 transition-colors">
                    <td className="px-8 py-5 font-label text-sm font-semibold text-slate-600">{row.feature}</td>
                    <td className="px-8 py-5 text-center">
                      {row.prebuilt ? (
                        <span className="material-symbols-outlined text-brand-emerald font-bold">check_circle</span>
                      ) : (
                        <span className="material-symbols-outlined text-slate-300">block</span>
                      )}
                    </td>
                    <td className="px-8 py-5 text-center">
                      {row.hosted ? (
                        <span className="material-symbols-outlined text-brand-emerald font-bold">check_circle</span>
                      ) : (
                        <span className="material-symbols-outlined text-slate-300">block</span>
                      )}
                    </td>
                    <td className="px-8 py-5 text-center">
                      {row.managed ? (
                        <span className="material-symbols-outlined text-brand-emerald font-bold">check_circle</span>
                      ) : (
                        <span className="material-symbols-outlined text-slate-300">block</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* Call to Action */}
        <section className="bg-slate-900 rounded-[2.5rem] p-16 text-center text-white relative overflow-hidden group">
          <div className="absolute inset-0 opacity-40 bg-[radial-gradient(circle_at_50%_50%,#00c897_0%,transparent_70%)] group-hover:scale-110 transition-transform duration-1000"></div>
          <div className="relative z-10 space-y-8 max-w-2xl mx-auto">
            <h2 className="text-4xl md:text-5xl font-headline font-black tracking-tighter">
              Ready to redefine conversational experiences?
            </h2>
            <p className="text-slate-400 font-medium">Join 2,000+ developers building with AIVision.</p>
            <div className="flex flex-col sm:flex-row justify-center gap-4">
              <button
                onClick={() => onNavigate('auth')}
                className="bg-brand-emerald hover:bg-white hover:text-brand-emerald text-slate-900 px-10 py-5 rounded-full font-bold font-label transition-all transform active:scale-95 shadow-xl shadow-brand-emerald/20"
              >
                Create Free Account
              </button>
              <button className="bg-white/5 hover:bg-white/10 text-white backdrop-blur-md border border-white/10 px-10 py-5 rounded-full font-bold font-label transition-all active:scale-95">
                Book a Demo
              </button>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="w-full border-t border-slate-200 bg-white mt-32">
        <div className="flex flex-col md:flex-row justify-between items-center px-8 py-12 gap-8 max-w-7xl mx-auto">
          <div className="flex items-center gap-2">
            <span
              className="material-symbols-outlined text-brand-emerald"
              style={{ fontSize: '28px', fontVariationSettings: "'FILL' 1" }}
            >
              dataset_lock
            </span>
            <span className="font-bold text-slate-900 font-headline text-xl">AIVision</span>
          </div>
          <div className="flex gap-8 font-label text-sm font-bold text-slate-500">
            <a href="#" className="hover:text-brand-emerald transition-colors">
              Status
            </a>
            <a href="#" className="hover:text-brand-emerald transition-colors">
              Security
            </a>
            <a href="#" className="hover:text-brand-emerald transition-colors">
              API Reference
            </a>
            <a href="#" className="hover:text-brand-emerald transition-colors">
              Github
            </a>
          </div>
          <p className="text-slate-400 text-[11px] font-bold font-label uppercase tracking-widest">© 2024 AIVision. Build the future.</p>
        </div>
      </footer>
    </div>
  );
};

export default TechnologyPage;
