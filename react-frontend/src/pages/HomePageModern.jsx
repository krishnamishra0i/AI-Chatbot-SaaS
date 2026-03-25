import React from 'react';
import './HomePageModern.css';

const pipeline = [
  { icon: 'mic', title: 'User Voice', subtitle: 'Input Signal' },
  { icon: 'speech_to_text', title: 'STT Engine', subtitle: 'DeepGram v2' },
  { icon: 'psychology', title: 'LLM Logic', subtitle: 'Athena Core' },
  { icon: 'record_voice_over', title: 'Lip Sync', subtitle: 'Neural Match' },
  { icon: 'view_in_ar', title: '3D Output', subtitle: 'Unreal Engine 5' },
];

const testimonials = [
  {
    text: 'Athena AI transformed our customer support. The realism of the avatars is uncanny, and the latency is virtually nonexistent.',
    name: 'Sarah Chen',
    role: 'CTO, TechCorp',
    img: 'https://lh3.googleusercontent.com/aida-public/AB6AXuAwtoQumgCBzV0vcv1Lz0hao7Rbdbayait-bhEmD2pRaQ0-zQEcvlWK0GdahTaYJp4P7-XfADQNPoFOS9RLGlUt2kcAGX2DH2ov2lntrnGnXqxvLLFF7L1ul5NnYJE1CxZ1-A0qAdmIQknkmQ8LjD-dqHEFl15mWtbSSGPdJodbY9v4vXgK98kJS74MJw4vJs3CrqtQORr3otpGxB2md7JQURcysjpmfqYcAQAYuLNBroFRyqLMzzPKU7ue_W4_ETs_jtEAp1WwWxJu',
    rating: 5,
  },
  {
    text: 'Security was our #1 priority. Athena\'s on-premise deployment options and privacy-first approach made them the only choice for us.',
    name: 'Michael Rodriguez',
    role: 'Head of Innovation, GlobalBank',
    img: 'https://lh3.googleusercontent.com/aida-public/AB6AXuDCPlkpxiS_HaatEptJ8S0eZYfunykWyF_Agziy2G_FlCF8ixXuFGa3367wSqwyk0b_W_zwCa9KcqJGbAcM29kqQ0TMrmnQ2z9BDuD1vxnOSplCEBwOxAk1bQAKCRJqTcXjNSbVqFA_BLhF1MTYPIGiFJDBEEBmuDmm7Dzikqkt62q6Jtdz4EjYOkFwTPgvY7KZVDWw-Kgk4j9MIMZQ7N5xN9cXK-dx344tNsM6rNMUJNLv8TsT2itHFVKmHKlyTQ0zI027SsoocQz-',
    rating: 5,
  },
  {
    text: 'As a fast-growing startup, we needed a scalable solution. Athena\'s API is a developer\'s dream—intuitive and powerful.',
    name: 'Emily Watson',
    role: 'Founder, StartupHub',
    img: 'https://lh3.googleusercontent.com/aida-public/AB6AXuBJDG6G6ZWKW_I_YiCzo2U_jAxV06no_WFRArRUahUpsHCmDr3UTF70ogVLK94lLtLaYZ_5EpT8ROAXOgp-VVsvS9uysbM0PZZcaxUSQAviNIpXlBIsqrkbt9vplEk6VXKgREqwbnrk04Zm7stlWq4DL0mzJ5I1rEaUnIBNe_1GTdUU__RgbeNgTylk1XCf5h3ntfDBM_Z19CvK94VkbeJJZAlEk7bhzp3hZCLrzwhy9Jh4XbvvQTrqOb36C0yokKr6D5W_HIKjlPo1',
    rating: 5,
  },
];

const faqs = [
  {
    q: 'How does Athena achieve 120ms latency?',
    a: 'Athena utilizes a proprietary edge-computing mesh network that processes STT and TTS concurrently. Our custom LLM inference engine is optimized for streaming responses, allowing the avatar to begin lip-syncing before the entire sentence is even generated.',
  },
  {
    q: 'Can I use my own custom 3D characters?',
    a: 'Yes. Athena integrates seamlessly with Unreal Engine 5 via our LiveLink plugin. You can upload your custom MetaHumans or 3D models and map our neural animation rig to your character in minutes.',
  },
  {
    q: 'What industries is this platform built for?',
    a: 'While flexible, Athena is specifically engineered for Enterprise use-cases including banking, healthcare, high-end retail concierge services, and corporate training simulations.',
  },
];

export default function HomePageModern({ onNavigate, onLaunchDemo }) {
  return (
    <div className="athena-home bg-surface text-on-surface font-body selection:bg-primary-container selection:text-on-primary-container">
      {/* TopAppBar */}
      <header className="fixed top-0 w-full z-50 bg-slate-50/60 dark:bg-slate-950/60 backdrop-blur-xl shadow-[0px_20px_40px_rgba(11,28,48,0.06)] flex justify-between items-center px-8 h-20 max-w-full mx-auto">
        <div className="flex items-center gap-3">
          <span className="material-symbols-outlined text-emerald-600 dark:text-emerald-400 text-3xl">model_training</span>
          <h1 className="font-headline font-bold tracking-tight text-2xl font-black bg-gradient-to-br from-emerald-700 to-emerald-400 bg-clip-text text-transparent">Athena AI</h1>
        </div>
        <nav className="hidden md:flex items-center gap-8">
          <a className="font-headline font-bold tracking-tight text-emerald-700 dark:text-emerald-400 border-b-2 border-emerald-500 py-1" href="#top">Home</a>
          <button onClick={() => onNavigate('technology')} className="font-headline font-bold tracking-tight text-slate-600 dark:text-slate-400 hover:bg-emerald-50/50 transition-all px-2 rounded cursor-pointer">Technology</button>
          <a className="font-headline font-bold tracking-tight text-slate-600 dark:text-slate-400 hover:bg-emerald-50/50 transition-all px-2 rounded" href="#solutions">Solutions</a>
          <a className="font-headline font-bold tracking-tight text-slate-600 dark:text-slate-400 hover:bg-emerald-50/50 transition-all px-2 rounded" href="#pricing">Pricing</a>
        </nav>
        <div className="flex items-center gap-4">
          <button onClick={onLaunchDemo} className="px-6 py-2.5 bg-gradient-to-br from-primary to-primary-container text-on-primary rounded-full font-semibold hover:scale-95 duration-200 transition-all">Launch Demo</button>
          <div className="w-10 h-10 rounded-full bg-surface-container-high flex items-center justify-center overflow-hidden cursor-pointer" onClick={() => onNavigate('auth')}>
            <img alt="Profile" src="https://lh3.googleusercontent.com/aida-public/AB6AXuCyyGRWlqX9rGLQr9uduNyLLq48lNvcrK5eeTvtb9C3Hly7dg_5nWswNftgQmTNFg-u2BBUKwDEJ7wr2XxmehUNU_J3pJXVCYFo6-5eJn9yar3Zp0pHLe5WHP39uNakzRMwmM1Uk49xlI8X2fzN86ieIoWJqOeu49PUscrU3gFoKZwxFG2pkWG2jk_D6vMjAT-ZJyD9fItMuuzFN0sGtT-L2V2LL9gh7dX_JOaX8IBkfEDLoCNjCDWzr8pdPe3McgcjUfGeoDECMnbR" className="w-full h-full object-cover" />
          </div>
        </div>
      </header>

      <main className="pt-20">
        {/* Hero Section */}
        <section id="top" className="relative min-h-[795px] flex items-center overflow-hidden px-8">
          <div className="max-w-7xl mx-auto grid lg:grid-cols-2 gap-12 items-center w-full">
            <div className="z-10 space-y-8">
              <span className="bg-tertiary-fixed text-on-tertiary-fixed px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-widest font-label">The Future of Interaction</span>
              <h2 className="text-6xl md:text-7xl font-headline font-extrabold text-on-surface leading-[1.1] tracking-tight">
                Real-Time <span className="text-primary italic">AI Avatar</span> Conversations
              </h2>
              <p className="text-xl text-on-surface-variant max-w-xl leading-relaxed">
                Deploy photorealistic digital humans integrated with Unreal Engine 5. Experience human-like responsiveness with sub-120ms latency.
              </p>
              <div className="flex flex-wrap gap-4">
                <button onClick={() => onNavigate('auth')} className="px-8 py-4 bg-gradient-to-br from-primary to-primary-container text-on-primary rounded-full font-bold text-lg shadow-lg hover:shadow-primary/20 transition-all">Get Started Free</button>
                <button onClick={onLaunchDemo} className="px-8 py-4 bg-secondary-container text-on-secondary-container rounded-full font-bold text-lg hover:opacity-90 transition-all flex items-center gap-2">
                  <span className="material-symbols-outlined">play_circle</span>
                  Watch Showcase
                </button>
              </div>
              <div className="flex items-center gap-6 pt-4">
                <div className="flex -space-x-3">
                  <img alt="User 1" className="w-10 h-10 rounded-full border-2 border-surface object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuB0NeayM3WfLGA9BZ7dkOdJxwy5yc6GxAQhudl4wUgHCHgP9CZH193e8T2KnbUWespZ1QSc9YBjsxONHNJ-Cyv1qWk4FE-7eAmuKmbe1N9RBdQOg-ED8qhjQ-F8p3W2zvBp0uJRusN6cxtI5N4UU_arsex3KJnMUDgRM138Gtza2q_Bvmld4YFWQtsi8VhvAhGyJGcfKmyrJBv4OsKswSSs6iNQHPFscAXKt0-yBaGD5jpdZoUKOmiNr25M1rrt1IPTtyivyuvm87mn" />
                  <img alt="User 2" className="w-10 h-10 rounded-full border-2 border-surface object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuCVSBWqXYzCPa6uwtvaTNE8YeJBsPUK5T3o3dAtdqRGc3poaN3FPMFHgPp9FFzjDUjENCvzTypO4E7T9RN0FTvZGoqnYW0sXizCb8Moe6FQf3ITKfCZStAYL3-CAQgjBgOM86FzyFE5M-YFBuw-uiv1TCSN8Nr9fOB3JzIV5-vE6uPW3ZPt2-Vf7Wj6yZ9k7fTvDpjhj837tVZeeInPmAj-RW1Ird_MzPQ-OxSc1qbzaKPo88QWXdyQWlzl6sSwYIlS0CKndVeTQpdY" />
                  <img alt="User 3" className="w-10 h-10 rounded-full border-2 border-surface object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuAE8ONdIdBJQJIT55I5tiAaOII7ZcChqE5jbBysOwdkzWzdVyB6k03kGc4C6NQrkhMI_ui9it4AN19rli4Hoea4F691Fjp8w-4S9Q7iwGc3fma3NTcTBUMJJw4uj_0ZX7cjlBWH1eAzWhYHTMvtI-J9ih2fv7fVUj-EYXaemgplQrMSNHe_xq7gcn-KOyJlXAg7CU4C2z9M5RIFHyF27PI1k_tyk4dFxZ3P0cnKgxAx7E6mn8MuY4JbBWTHg4IwJ6LLLGKW2EqvMeSP" />
                </div>
                <p className="text-sm font-medium text-on-surface-variant">Trusted by <span className="text-primary font-bold">500+</span> Enterprise Partners</p>
              </div>
            </div>
            <div className="relative group">
              <div className="absolute -inset-4 bg-gradient-to-tr from-primary/20 to-secondary/20 rounded-xl blur-3xl opacity-50 group-hover:opacity-75 transition duration-1000"></div>
              <div className="relative bg-surface-container-lowest rounded-xl p-4 shadow-2xl overflow-hidden aspect-[4/5]">
                <img alt="AI Avatar" className="w-full h-full object-cover rounded-lg" src="https://lh3.googleusercontent.com/aida-public/AB6AXuCh53dTMVK1xx6xhwe-s4j-FvmeIc1NVbPV9pSZbp3PiBwCSipvY4eN2DkDIHvuDv94G3AirfYu3HVwkGCxbLb1cyIJp9Z4_xvILjo1sRrsyoqk_RGmuSebit8RCxZDah92rEO1pD8Hum-A-dCe5oSTw88bCbdJGQ-bwaDFzzZvcYmYTjTRTipqfdFCEqqmhrr6m5xK2VMgsuiLYx3uUbbmZZhvjM6gA3va1FQFTBXRu-kWl_CNPAdJFJQDWoUknP7zd-iR34gcrfGc" />
                <div className="absolute bottom-8 left-8 right-8 glass-card p-6 rounded-lg border border-outline-variant/10">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold text-primary font-label uppercase">Status: Live Sync</span>
                    <span className="flex h-2 w-2 rounded-full bg-primary-container animate-pulse"></span>
                  </div>
                  <p className="text-sm font-medium text-on-surface leading-tight italic">"Hello! I am Athena. How can I assist your enterprise operations today?"</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Technology Pipeline */}
        <section id="technology" className="py-24 bg-surface-container-low">
          <div className="max-w-7xl mx-auto px-8">
            <div className="text-center mb-16 space-y-4">
              <h3 className="text-4xl font-headline font-extrabold tracking-tight">The Athena Pipeline</h3>
              <p className="text-on-surface-variant max-w-2xl mx-auto">From human speech to cinematic 3D output in milliseconds.</p>
            </div>
            <div className="flex flex-col md:flex-row justify-between items-center gap-4 relative">
              <div className="absolute top-1/2 left-0 w-full h-0.5 bg-gradient-to-r from-primary/10 via-primary to-primary/10 -translate-y-1/2 hidden md:block"></div>
              {pipeline.map((step, idx) => (
                <React.Fragment key={step.title}>
                  <div className={`relative z-10 p-6 rounded-lg shadow-sm w-48 text-center group hover:scale-105 transition-transform ${idx === pipeline.length - 1 ? 'bg-primary text-on-primary shadow-xl' : 'bg-surface-container-lowest'}`}>
                    <div className={`w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 ${idx === pipeline.length - 1 ? 'bg-white/20' : 'bg-primary-container/20 group-hover:bg-primary-container transition-colors'}`}>
                      <span className={`material-symbols-outlined ${idx === pipeline.length - 1 ? 'text-on-primary' : 'text-primary group-hover:text-on-primary transition-colors'}`}>{step.icon}</span>
                    </div>
                    <h4 className="font-bold text-sm mb-1">{step.title}</h4>
                    <p className={`text-[10px] font-label uppercase ${idx === pipeline.length - 1 ? 'text-primary-fixed' : 'text-on-surface-variant'}`}>{step.subtitle}</p>
                  </div>
                  {idx < pipeline.length - 1 && <span className="material-symbols-outlined text-outline-variant md:hidden">arrow_downward</span>}
                </React.Fragment>
              ))}
            </div>
          </div>
        </section>

        {/* Feature Grid */}
        <section id="solutions" className="py-24 px-8">
          <div className="max-w-7xl mx-auto">
            <div className="grid grid-cols-1 md:grid-cols-4 grid-rows-2 gap-6 h-auto md:h-[600px]">
              <div className="md:col-span-2 md:row-span-2 bg-surface-container-lowest rounded-lg p-10 flex flex-col justify-between group overflow-hidden relative shadow-sm">
                <div className="z-10">
                  <span className="material-symbols-outlined text-primary text-4xl mb-6">verified_user</span>
                  <h4 className="text-3xl font-headline font-bold mb-4">Photorealistic Avatars</h4>
                  <p className="text-on-surface-variant text-lg">Our proprietary skin shader and hair system render digital humans that are indistinguishable from real video at 4K resolution.</p>
                </div>
              </div>
              <div className="md:col-span-1 bg-primary text-on-primary rounded-lg p-8 flex flex-col justify-center gap-4 hover:bg-on-primary-fixed-variant transition-colors">
                <span className="material-symbols-outlined text-3xl">bolt</span>
                <h4 className="text-xl font-bold">120ms Latency</h4>
                <p className="text-sm opacity-80">The world's fastest conversational loop from audio to visual.</p>
              </div>
              <div className="md:col-span-1 bg-secondary-container text-on-secondary-container rounded-lg p-8 flex flex-col justify-center gap-4">
                <span className="material-symbols-outlined text-3xl">language</span>
                <h4 className="text-xl font-bold">Global Scale</h4>
                <p className="text-sm opacity-80">Native support for 45+ languages and regional accents.</p>
              </div>
              <div className="md:col-span-2 bg-surface-container-high rounded-lg p-8 flex items-center justify-between group">
                <div className="max-w-[60%]">
                  <h4 className="text-xl font-bold mb-2">Privacy First Architecture</h4>
                  <p className="text-sm text-on-surface-variant">SOC2 Type II compliant with end-to-end encryption for all session data.</p>
                </div>
                <span className="material-symbols-outlined text-5xl text-primary/30 group-hover:text-primary transition-colors">shield_lock</span>
              </div>
            </div>
          </div>
        </section>

        {/* Stats */}
        <section className="py-20 bg-inverse-surface text-inverse-on-surface">
          <div className="max-w-7xl mx-auto px-8 grid grid-cols-2 lg:grid-cols-4 gap-12 text-center">
            <div className="space-y-2">
              <p className="text-5xl font-headline font-black text-primary-fixed">10M+</p>
              <p className="text-sm uppercase tracking-widest font-label opacity-70">Daily Conversations</p>
            </div>
            <div className="space-y-2">
              <p className="text-5xl font-headline font-black text-primary-fixed">99.9%</p>
              <p className="text-sm uppercase tracking-widest font-label opacity-70">Uptime SLA</p>
            </div>
            <div className="space-y-2">
              <p className="text-5xl font-headline font-black text-primary-fixed">50+</p>
              <p className="text-sm uppercase tracking-widest font-label opacity-70">Countries</p>
            </div>
            <div className="space-y-2">
              <p className="text-5xl font-headline font-black text-primary-fixed">45+</p>
              <p className="text-sm uppercase tracking-widest font-label opacity-70">Languages</p>
            </div>
          </div>
        </section>

        {/* Testimonials */}
        <section className="py-24 bg-surface">
          <div className="max-w-7xl mx-auto px-8">
            <div className="flex items-end justify-between mb-16">
              <div className="space-y-4">
                <span className="text-primary font-bold font-label uppercase tracking-widest text-xs">Testimonials</span>
                <h3 className="text-4xl font-headline font-extrabold">Enterprise Success Stories</h3>
              </div>
              <div className="flex gap-2">
                <button className="w-12 h-12 rounded-full bg-surface-container flex items-center justify-center hover:bg-primary-container transition-colors">
                  <span className="material-symbols-outlined">chevron_left</span>
                </button>
                <button className="w-12 h-12 rounded-full bg-surface-container flex items-center justify-center hover:bg-primary-container transition-colors">
                  <span className="material-symbols-outlined">chevron_right</span>
                </button>
              </div>
            </div>
            <div className="grid md:grid-cols-3 gap-8">
              {testimonials.map((t, idx) => (
                <div key={t.name} className={`bg-surface-container-lowest p-8 rounded-lg shadow-sm border-outline-variant/10 border-t-4 ${idx === 0 ? 'border-t-primary' : idx === 1 ? 'border-t-secondary' : 'border-t-tertiary'}`}>
                  <div className="flex gap-1 text-primary-container mb-6">
                    {[...Array(t.rating)].map((_, i) => (
                      <span key={i} className="material-symbols-outlined text-lg" style={{fontVariationSettings: "'FILL' 1"}}>star</span>
                    ))}
                  </div>
                  <p className="text-on-surface font-medium leading-relaxed mb-8 italic">"{t.text}"</p>
                  <div className="flex items-center gap-4">
                    <img alt={t.name} className="w-12 h-12 rounded-full object-cover" src={t.img} />
                    <div>
                      <h5 className="font-bold text-sm">{t.name}</h5>
                      <p className="text-xs text-on-surface-variant font-label">{t.role}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* FAQ */}
        <section className="py-24 bg-surface-container-low">
          <div className="max-w-3xl mx-auto px-8">
            <h3 className="text-4xl font-headline font-extrabold text-center mb-16 tracking-tight">Frequently Asked Questions</h3>
            <div className="space-y-4">
              {faqs.map((faq, idx) => (
                <details key={idx} className="group bg-surface-container-lowest rounded-lg overflow-hidden transition-all">
                  <summary className="list-none flex justify-between items-center p-6 cursor-pointer font-bold text-on-surface hover:bg-surface-container transition-colors">
                    {faq.q}
                    <span className="material-symbols-outlined group-open:rotate-180 transition-transform">expand_more</span>
                  </summary>
                  <div className="px-6 pb-6 text-on-surface-variant leading-relaxed">
                    {faq.a}
                  </div>
                </details>
              ))}
            </div>
          </div>
        </section>

        {/* CTA */}
        <section id="pricing" className="py-24 px-8 overflow-hidden">
          <div className="max-w-7xl mx-auto bg-gradient-to-br from-primary to-primary-container rounded-xl p-12 md:p-24 relative overflow-hidden flex flex-col items-center text-center">
            <div className="absolute top-0 right-0 w-96 h-96 bg-white/10 rounded-full -translate-y-1/2 translate-x-1/2 blur-3xl"></div>
            <div className="absolute bottom-0 left-0 w-96 h-96 bg-black/10 rounded-full translate-y-1/2 -translate-x-1/2 blur-3xl"></div>
            <h3 className="text-5xl md:text-6xl font-headline font-black text-on-primary mb-8 leading-tight z-10">Ready to build the<br/>future of engagement?</h3>
            <div className="flex flex-col sm:flex-row gap-4 z-10">
              <button onClick={() => onNavigate('auth')} className="px-10 py-5 bg-white text-primary rounded-full font-black text-xl hover:scale-105 transition-transform shadow-2xl">Start Free Trial</button>
              <button onClick={onLaunchDemo} className="px-10 py-5 bg-primary-container/20 border-2 border-white/30 text-white rounded-full font-black text-xl backdrop-blur-sm hover:bg-white/10 transition-colors">Book a Demo</button>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-slate-100 dark:bg-slate-900 w-full py-12">
        <div className="max-w-7xl mx-auto px-8 grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="space-y-6">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-emerald-600">model_training</span>
              <span className="font-bold text-emerald-600 text-xl font-headline">Athena AI</span>
            </div>
            <p className="text-slate-500 dark:text-slate-400 max-w-sm font-body">
              The leading enterprise platform for real-time digital human interaction. Powered by Unreal Engine and advanced neural processing.
            </p>
            <div className="flex gap-4">
              <a className="text-slate-400 hover:text-emerald-600" href="#socials"><span className="material-symbols-outlined">share</span></a>
              <a className="text-slate-400 hover:text-emerald-600" href="#website"><span className="material-symbols-outlined">public</span></a>
              <a className="text-slate-400 hover:text-emerald-600" href="#email"><span className="material-symbols-outlined">mail</span></a>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-8">
            <div className="space-y-4">
              <h6 className="font-headline font-bold text-slate-900 dark:text-slate-100">Product</h6>
              <nav className="flex flex-col gap-2">
                <a className="font-['Inter'] text-xs uppercase tracking-widest text-slate-500 dark:text-slate-400 hover:text-emerald-400 transition-colors" href="#docs">Documentation</a>
                <a className="font-['Inter'] text-xs uppercase tracking-widest text-slate-500 dark:text-slate-400 hover:text-emerald-400 transition-colors" href="#api">API Reference</a>
                <a className="font-['Inter'] text-xs uppercase tracking-widest text-slate-500 dark:text-slate-400 hover:text-emerald-400 transition-colors" href="#changelog">Changelog</a>
              </nav>
            </div>
            <div className="space-y-4">
              <h6 className="font-headline font-bold text-slate-900 dark:text-slate-100">Legal</h6>
              <nav className="flex flex-col gap-2">
                <a className="font-['Inter'] text-xs uppercase tracking-widest text-slate-500 dark:text-slate-400 hover:text-emerald-400 transition-colors" href="#security">Security</a>
                <a className="font-['Inter'] text-xs uppercase tracking-widest text-slate-500 dark:text-slate-400 hover:text-emerald-400 transition-colors" href="#privacy">Privacy Policy</a>
                <a className="font-['Inter'] text-xs uppercase tracking-widest text-slate-500 dark:text-slate-400 hover:text-emerald-400 transition-colors" href="#terms">Terms of Service</a>
              </nav>
            </div>
          </div>
          <div className="md:col-span-2 pt-8 border-t border-slate-200 dark:border-slate-800">
            <p className="font-['Inter'] text-xs uppercase tracking-widest text-slate-500 dark:text-slate-400">© 2024 Athena AI. Powered by Unreal Engine.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
