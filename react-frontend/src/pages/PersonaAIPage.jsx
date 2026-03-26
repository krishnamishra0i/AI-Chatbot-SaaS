import React, { useState } from 'react';
import './PersonaAIPage.css';

const PersonaAIPage = ({ onNavigate = () => {}, onLaunchDemo = () => {} }) => {
  const [copiedSnippet, setCopiedSnippet] = useState(false);

  const pipelineStages = [
    {
      id: 1,
      title: 'Audio Ingest',
      subtitle: 'Direct Stream',
      icon: 'mic',
      color: 'purple',
      glassDark: false,
    },
    {
      id: 2,
      title: 'Neural STT',
      subtitle: 'Latency Optimized',
      icon: 'graphic_eq',
      color: 'indigo',
      glassDark: false,
    },
    {
      id: 3,
      title: 'PersonaAI Core',
      subtitle: 'Logic Layer',
      icon: 'psychology',
      color: 'core',
      glassDark: true,
      isCoreNode: true,
    },
    {
      id: 4,
      title: 'Viseme Sync',
      subtitle: 'Sync-Engine v3',
      icon: 'face_retouching_natural',
      color: 'violet',
      glassDark: false,
    },
    {
      id: 5,
      title: '3D Render',
      subtitle: 'Low Latency',
      icon: 'view_in_ar',
      color: 'fuchsia',
      glassDark: false,
    },
  ];

  const productOptions = [
    {
      icon: 'widgets',
      title: 'Web Widget',
      description: 'Embed with a single script tag. Pre-configured UI components for rapid launch.',
      badge: 'No-Code Ready',
      featured: false,
    },
    {
      icon: 'rocket_launch',
      title: 'Hosted API',
      description: 'Customizable UI with managed GPU orchestration. We handle the heavy lifting.',
      badge: 'Developer Choice',
      featured: true,
    },
    {
      icon: 'shield_with_house',
      title: 'Enterprise',
      description: 'Deploy on your private cloud. Maximum security and data sovereignty for scale.',
      badge: 'Self-Managed',
      featured: false,
    },
  ];

  const comparisonFeatures = [
    {
      feature: 'Sub-150ms Interaction',
      widget: true,
      hosted: true,
      managed: true,
    },
    {
      feature: 'Custom Avatar Library',
      widget: false,
      hosted: true,
      managed: true,
    },
    {
      feature: 'Private VPC Deployment',
      widget: false,
      hosted: false,
      managed: true,
    },
    {
      feature: 'Dedicated GPU Clusters',
      widget: false,
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
    agent_id: 'athena_premium',
    prompt: 'Support expert agent',
    transport: {
      type: 'livekit',
      url: 'wss://persona.cloud'
    }
  })
};`;

  const handleCopySnippet = () => {
    navigator.clipboard.writeText(codeSnippet);
    setCopiedSnippet(true);
    setTimeout(() => setCopiedSnippet(false), 2000);
  };

  return (
    <div className="bg-mesh font-body text-on-surface min-h-screen antialiased">
      {/* TopAppBar */}
      <header className="fixed top-0 w-full z-50 bg-gradient-to-r from-purple-50 to-indigo-50 backdrop-blur-xl border-b border-purple-200 shadow-md">
        <div className="flex justify-between items-center px-6 py-4 max-w-7xl mx-auto font-plus-jakarta-sans antialiased">
          <div className="flex items-center gap-4">
            <button
              onClick={() => onNavigate('home')}
              className="flex items-center justify-center p-2 rounded-full hover:bg-purple-200/60 transition-all text-purple-700 group shadow-md hover:shadow-lg"
              title="Back to Home"
            >
              <span className="material-symbols-outlined text-2xl font-bold group-hover:-translate-x-1 transition-transform">
                arrow_back
              </span>
            </button>
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-purple-600" style={{ fontVariationSettings: "'FILL' 1" }}>
                terminal
              </span>
              <span className="text-xl font-black tracking-tight text-purple-900">PersonaAI</span>
            </div>
          </div>
          <nav className="hidden md:flex items-center gap-8">
            <a className="text-purple-600 font-bold border-b-2 border-purple-600 pb-1" href="#technology">
              Technology
            </a>
            <a className="text-slate-600 hover:text-purple-600 transition-colors font-semibold" href="#api">
              API
            </a>
            <a className="text-slate-600 hover:text-purple-600 transition-colors font-semibold" href="#docs">
              Docs
            </a>
            <a className="text-slate-600 hover:text-purple-600 transition-colors font-semibold" href="#pricing">
              Pricing
            </a>
          </nav>
          <div className="flex items-center gap-4">
            <button className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-2.5 rounded-full text-sm font-black active:scale-95 duration-200 transition-all shadow-lg shadow-purple-600/30">
              Get Started
            </button>
          </div>
        </div>
      </header>

      <main className="pt-32 pb-24 px-4 max-w-7xl mx-auto space-y-40">
        {/* Hero Section */}
        <section className="text-center relative py-12 hero-gradient">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-5xl h-[500px] bg-gradient-to-r from-purple-300/30 via-indigo-300/30 to-violet-300/30 blur-[120px] -z-10 rounded-full"></div>
          <div className="inline-flex items-center gap-2 px-5 py-2.5 bg-purple-100 border border-purple-300 text-purple-700 rounded-full text-xs font-black font-label uppercase tracking-widest mb-10 shadow-inner-glow">
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-violet-500 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-violet-500"></span>
            </span>
            Real-time Rendering Engine v2.4
          </div>
          <h1 className="text-6xl md:text-8xl font-black font-headline text-slate-900 tracking-tighter mb-8 leading-[1.1]">
            Neural <span className="gradient-text-purple">Interaction</span>
            <br />
            Pipeline
          </h1>
          <p className="text-xl md:text-2xl text-slate-600 max-w-2xl mx-auto leading-relaxed font-semibold">
            Translate multi-modal input to hyper-realistic 3D agents with sub-120ms latency.
          </p>
        </section>

        {/* Pipeline Visual */}
        <section className="relative section-aura-blue">
          <div className="flex flex-col gap-12 lg:flex-row lg:justify-between items-start relative py-12">
            {/* Connector Line (Desktop) */}
            <div className="hidden lg:block absolute top-[52px] left-0 w-full h-[3px] bg-gradient-to-r from-transparent via-brand-peach/40 to-transparent -z-10"></div>

            {/* Pipeline Stages */}
            {pipelineStages.map((stage) => (
              <div key={stage.id} className="flex lg:flex-col items-center gap-6 lg:gap-0 group w-full lg:w-1/5">
                {stage.isCoreNode ? (
                  <>
                    <div className="absolute -inset-10 bg-brand-orange/20 blur-3xl rounded-full opacity-50 group-hover:opacity-100 transition-opacity"></div>
                    <div className="w-28 h-28 rounded-3xl bg-slate-900 flex items-center justify-center text-white shadow-premium group-hover:scale-110 group-hover:-translate-y-2 transition-all duration-500 ring-8 ring-violet-500/30 relative z-10">
                      <span
                        className="material-symbols-outlined text-5xl text-violet-400 icon-3d"
                        style={{ fontVariationSettings: "'FILL' 1" }}
                      >
                        {stage.icon}
                      </span>
                    </div>
                    <div className="lg:mt-8 text-left lg:text-center flex-1 lg:flex-none">
                      <h4 className="font-headline font-black text-slate-900 text-xl">{stage.title}</h4>
                      <p className="text-[11px] text-violet-600 font-black font-label uppercase tracking-widest mt-1">
                        {stage.subtitle}
                      </p>
                    </div>
                  </>
                ) : (
                  <>
                    <div
                      className={`w-24 h-24 rounded-2xl glass-card flex items-center justify-center shadow-premium group-hover:shadow-premium transition-all duration-500 relative group-stage`}
                      style={{
                        color: stage.color === 'purple' ? '#A855F7' : stage.color === 'indigo' ? '#6366F1' : stage.color === 'violet' ? '#7C3AED' : '#EC4899',
                      }}
                    >
                      <div
                        className="absolute inset-0 blur-xl opacity-0 group-hover:opacity-100 transition-opacity rounded-full"
                        style={{
                          background: stage.color === 'purple' ? 'rgba(168, 85, 247, 0.2)' : stage.color === 'indigo' ? 'rgba(99, 102, 241, 0.3)' : stage.color === 'violet' ? 'rgba(124, 58, 237, 0.3)' : 'rgba(236, 72, 153, 0.4)',
                        }}
                      ></div>
                      <span className="material-symbols-outlined text-4xl icon-3d relative z-10">{stage.icon}</span>
                    </div>
                    <div className="lg:mt-8 text-left lg:text-center flex-1 lg:flex-none">
                      <h4 className="font-headline font-extrabold text-slate-900 text-lg">{stage.title}</h4>
                      <p
                        className="text-[11px] font-bold font-label uppercase tracking-widest mt-1"
                        style={{
                          color: stage.color === 'purple' ? '#A855F7' : stage.color === 'indigo' ? '#6366F1' : stage.color === 'violet' ? '#7C3AED' : '#EC4899',
                        }}
                      >
                        {stage.subtitle}
                      </p>
                    </div>
                  </>
                )}
              </div>
            ))}
          </div>
        </section>

        {/* Developer Section */}
        <section className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          <div className="space-y-8">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-100 text-indigo-600 rounded-full text-xs font-black font-label uppercase tracking-widest border border-indigo-300">
              <span className="material-symbols-outlined text-sm">terminal</span> SDK &amp; API
            </div>
            <h2 className="text-5xl font-black font-headline text-slate-900 leading-[1.2] tracking-tight">
              Powerful <span className="text-violet-600">REST API</span> for Scale
            </h2>
            <p className="text-xl text-slate-600 leading-relaxed max-w-lg font-medium">
              Integrate hyper-realistic AI avatars with just a few lines of code. Support for WebRTC, LiveKit, and custom transport layers.
            </p>
            <div className="flex flex-wrap gap-4 pt-4">
              <button className="bg-violet-600 hover:bg-violet-700 text-white px-8 py-4 rounded-full font-black font-label hover:shadow-lg active:scale-95 transition-all flex items-center gap-2 shadow-lg shadow-violet-600/30">
                Get API Key <span className="material-symbols-outlined text-xl">arrow_forward</span>
              </button>
              <button className="bg-purple-100 border border-purple-300 text-purple-700 px-8 py-4 rounded-full font-black font-label hover:bg-purple-200 transition-all flex items-center gap-2 shadow-sm">
                Read Documentation <span className="material-symbols-outlined text-xl">menu_book</span>
              </button>
            </div>
          </div>

          {/* Code Block */}
          <div className="glass-dark rounded-[2.5rem] overflow-hidden group">
            {/* Code Window Header */}
            <div className="bg-slate-800/80 px-6 py-4 flex items-center justify-between border-b border-white/5">
              <div className="flex gap-2">
                <div className="w-3 h-3 rounded-full bg-rose-500/80"></div>
                <div className="w-3 h-3 rounded-full bg-violet-500/80 shadow-sm shadow-violet-500"></div>
                <div className="w-3 h-3 rounded-full bg-indigo-500/80 shadow-sm shadow-indigo-500"></div>
              </div>
              <span className="text-[10px] text-purple-400 font-mono uppercase tracking-[0.2em] font-bold">
                POST /v1/agents/spawn
              </span>
            </div>

            {/* Syntax Highlighted Code */}
            <div className="p-8 font-mono text-[14px] leading-relaxed overflow-x-auto">
              <pre className="text-slate-300 whitespace-pre-wrap break-words">{codeSnippet}</pre>
            </div>

            {/* Copy Button */}
            <div className="px-8 py-4 bg-slate-800/30 border-t border-white/5 flex justify-end">
              <button
                onClick={handleCopySnippet}
                className="text-purple-400 hover:text-violet-400 transition-colors flex items-center gap-2 text-xs font-black uppercase tracking-wider"
              >
                <span className="material-symbols-outlined text-sm">{copiedSnippet ? 'check' : 'content_copy'}</span>
                {copiedSnippet ? 'Copied!' : 'Copy Snippet'}
              </button>
            </div>
          </div>
        </section>

        {/* Product Options */}
        <section className="space-y-16 py-16 bg-purple-100/40 rounded-[4rem] relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-b from-purple-100/50 to-transparent -z-10"></div>
          <div className="absolute -top-20 -right-20 w-80 h-80 bg-indigo-300/20 blur-[120px] rounded-full"></div>
          <div className="absolute -bottom-20 -left-20 w-80 h-80 bg-violet-300/15 blur-[120px] rounded-full"></div>

          <div className="text-center space-y-4 px-6">
            <h2 className="text-4xl md:text-5xl font-black font-headline text-slate-900">Integration Tiers</h2>
            <p className="text-slate-600 font-bold text-lg max-w-2xl mx-auto">
              From rapid prototyping to global enterprise deployments.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 px-8">
            {productOptions.map((option, idx) => (
              <div
                key={idx}
                className={`p-12 rounded-[2.5rem] flex flex-col items-center text-center space-y-6 transition-all ${
                  option.featured
                    ? 'bg-slate-900 glass-dark border-violet-600/30 scale-105 shadow-premium relative overflow-hidden'
                    : 'glass-card border-purple-300/15 hover:-translate-y-2'
                } group`}
              >
                {option.featured && (
                  <div className="absolute top-0 left-0 w-full h-1.5 bg-gradient-to-r from-purple-600 via-violet-600 via-indigo-600 to-fuchsia-600"></div>
                )}

                <div
                  className={`w-20 h-20 rounded-2xl flex items-center justify-center transition-colors duration-500 relative ${
                    option.featured
                      ? `bg-violet-600 flex items-center justify-center text-slate-900 shadow-xl shadow-violet-600/50 ring-4 ring-violet-600/20`
                      : option.icon === 'widgets'
                      ? 'bg-purple-200/60 text-purple-700 group-hover:bg-purple-600 group-hover:text-white shadow-inner-glow'
                      : option.icon === 'shield_with_house'
                      ? 'bg-indigo-200/60 text-indigo-700 group-hover:bg-indigo-600 group-hover:text-white shadow-inner-glow'
                      : 'bg-violet-200/60 text-violet-700'
                  }`}
                >
                  <div className={`absolute inset-0 rounded-full opacity-0 group-hover:opacity-100 transition-opacity ${
                    option.featured ? '' :
                    option.icon === 'widgets' ? 'bg-purple-600/30 blur-xl' :
                    option.icon === 'shield_with_house' ? 'bg-indigo-600/40 blur-xl' :
                    'bg-violet-600/30 blur-xl'
                  }`}></div>
                  <span className="material-symbols-outlined text-4xl icon-3d relative z-10" style={{ fontVariationSettings: option.featured ? "'FILL' 1" : "'FILL' 0" }}>{option.icon}</span>
                </div>

                <h3 className={`text-2xl font-black font-headline ${option.featured ? 'text-white' : ''}`}>
                  {option.title}
                </h3>

                <p className={`text-slate-500 leading-relaxed font-bold ${option.featured ? 'text-slate-300' : ''}`}>
                  {option.description}
                </p>

                <div className="pt-4">
                  <span
                    className={`px-5 py-2 rounded-full text-[10px] font-black tracking-widest uppercase ${
                      option.featured
                        ? 'bg-violet-600 text-white shadow-lg shadow-violet-600/20'
                        : option.icon === 'widgets'
                        ? 'bg-purple-200/60 text-purple-700 border border-purple-300/40'
                        : 'bg-indigo-200/60 text-indigo-700 border border-indigo-300/40'
                    }`}
                  >
                    {option.badge}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Matrix Table */}
        <section className="section-aura-mint">
          <div className="glass-card rounded-[2.5rem] overflow-hidden border border-purple-300/60 shadow-premium">
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="bg-purple-100/30 border-b border-purple-300/50">
                    <th className="px-10 py-8 font-headline text-slate-900 font-black text-lg">Capabilities</th>
                    <th className="px-8 py-8 font-headline text-slate-500 font-black text-center">Widget</th>
                    <th className="px-8 py-8 font-headline text-purple-600 font-black text-center bg-purple-200/20">
                      Hosted API
                    </th>
                    <th className="px-8 py-8 font-headline text-slate-500 font-black text-center">Managed</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-purple-300/30">
                  {comparisonFeatures.map((row, idx) => (
                    <tr key={idx} className="hover:bg-purple-100/15 transition-colors">
                      <td className="px-10 py-6 font-label text-sm font-bold text-slate-700">{row.feature}</td>
                      <td className="px-8 py-6 text-center">
                        {row.widget ? (
                          <span className="material-symbols-outlined text-indigo-500 font-black scale-110">
                            check_circle
                          </span>
                        ) : (
                          <span className="material-symbols-outlined text-slate-300">cancel</span>
                        )}
                      </td>
                      <td className="px-8 py-6 text-center bg-purple-200/10">
                        {row.hosted ? (
                          <span className="material-symbols-outlined text-purple-600 font-black scale-110">
                            check_circle
                          </span>
                        ) : (
                          <span className="material-symbols-outlined text-slate-300">cancel</span>
                        )}
                      </td>
                      <td className="px-8 py-6 text-center">
                        {row.managed ? (
                          <span className="material-symbols-outlined text-violet-600 font-black scale-110">
                            check_circle
                          </span>
                        ) : (
                          <span className="material-symbols-outlined text-slate-300">cancel</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </section>

        {/* Call to Action */}
        <section className="bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 rounded-[3.5rem] p-16 md:p-24 text-center text-white relative overflow-hidden group border border-violet-600/30 shadow-premium">
          <div className="absolute inset-0 opacity-50 bg-[radial-gradient(circle_at_50%_50%,#A855F7_0%,#7C3AED_30%,#6366F1_60%,transparent_90%)] group-hover:scale-125 transition-transform duration-[4000ms]"></div>
          <div className="relative z-10 space-y-12 max-w-4xl mx-auto">
            <h2 className="text-5xl md:text-7xl font-headline font-black tracking-tighter leading-tight">
              Build the next generation of <br />
              <span className="gradient-text-purple">Conversational AI</span>
            </h2>
            <p className="text-slate-300 font-black text-xl md:text-2xl max-w-2xl mx-auto leading-relaxed">
              Join thousands of developers scaling their vision with PersonaAI.
            </p>
            <div className="flex flex-col sm:flex-row justify-center gap-6 pt-6">
              <button
                onClick={() => onNavigate('auth')}
                className="bg-indigo-500 hover:bg-indigo-600 text-white px-14 py-6 rounded-full font-black font-label transition-all transform active:scale-95 shadow-2xl shadow-indigo-500/40 text-lg"
              >
                Create Free Account
              </button>
              <button className="bg-white/10 hover:bg-white/20 text-white backdrop-blur-xl border border-white/20 px-14 py-6 rounded-full font-black font-label transition-all active:scale-95 text-lg">
                Book Architecture Call
              </button>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="w-full border-t border-purple-300/40 bg-purple-50/50 font-manrope text-sm">
        <div className="flex flex-col md:flex-row justify-between items-center px-8 py-14 gap-8 max-w-7xl mx-auto">
          <div className="flex items-center gap-3 transition-opacity hover:opacity-80">
            <span className="material-symbols-outlined text-purple-600 text-3xl" style={{ fontVariationSettings: "'FILL' 1" }}>
              terminal
            </span>
            <span className="text-xl font-black text-slate-900">PersonaAI</span>
          </div>
          <div className="flex flex-wrap justify-center gap-x-10 gap-y-4">
            <a className="text-slate-600 font-black hover:text-purple-600 transition-colors" href="#docs">
              Documentation
            </a>
            <a className="text-slate-600 font-black hover:text-purple-600 transition-colors" href="#api">
              API Reference
            </a>
            <a className="text-slate-600 font-black hover:text-purple-600 transition-colors" href="#changelog">
              Changelog
            </a>
            <a className="text-slate-600 font-black hover:text-purple-600 transition-colors" href="#status">
              Status
            </a>
            <a className="text-slate-600 font-black hover:text-purple-600 transition-colors" href="#privacy">
              Privacy
            </a>
          </div>
          <p className="text-slate-400 text-xs font-black uppercase tracking-widest">
            © 2024 PersonaAI. Built for the future.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default PersonaAIPage;
