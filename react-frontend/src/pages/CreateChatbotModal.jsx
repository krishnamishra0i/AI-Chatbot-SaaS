// Create Chatbot Modal/Page
import React, { useState } from 'react';

// Voice mapping: frontend labels to backend voice IDs
const VOICE_MAPPING = {
  male: 'en-US-GuyNeural',
  female: 'en-US-AriaNeural',
};

// Model mapping: frontend display to backend model names
const MODEL_MAPPING = {
  'GPT-4o (Omni) - Fastest & Smartest': 'gpt-4o',
  'Claude 3.5 Sonnet - Creative & Precise': 'claude-3.5-sonnet',
  'Llama 3 70B - Open Source Excellence': 'llama-3-70b',
  'Mistral Large - High Performance': 'mistral-large',
};

const CreateChatbotModal = ({ isOpen, onClose, onCreate }) => {
  const defaultModel = 'GPT-4o (Omni) - Fastest & Smartest';
  
  const [formData, setFormData] = useState({
    name: '',
    model: defaultModel,
    personality: '',
    voice: 'male',
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Map form data to backend schema
    const backendData = {
      name: formData.name,
      llm_model: MODEL_MAPPING[formData.model] || 'gpt-4o',
      system_prompt: formData.personality,
      voice_id: VOICE_MAPPING[formData.voice] || 'en-US-GuyNeural',
      temperature: 0.7,
      max_tokens: 1024,
    };
    
    onCreate(backendData);
    // Reset to default (preserve model if needed)
    setFormData({ name: '', model: defaultModel, personality: '', voice: 'male' });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div className="glass-panel w-full max-w-4xl rounded-lg shadow-2xl relative z-10 overflow-hidden flex flex-col md:flex-row my-8 md:my-0 bg-white/70 backdrop-blur-md">
        {/* Left Side: Visual/Context */}
        <div className="w-full md:w-5/12 bg-secondary/5 p-8 flex flex-col justify-between border-r border-white/20">
          <div>
            <div className="inline-flex items-center justify-center w-12 h-12 bg-secondary-container rounded-full mb-6">
              <span className="material-symbols-outlined text-white">rocket_launch</span>
            </div>
            <h2 className="text-2xl font-headline font-bold text-on-background mb-4">Deploy an Intelligence</h2>
            <p className="text-on-surface-variant text-sm leading-relaxed mb-8">
              Configure your autonomous agent with custom personalities, advanced language models, and natural voice
              synthesis.
            </p>

            <div className="space-y-4">
              <div className="flex items-start gap-4 p-4 rounded-lg bg-white/40 border border-white/60">
                <span className="material-symbols-outlined text-secondary">neurology</span>
                <div>
                  <p className="text-xs font-bold text-secondary uppercase tracking-wider">Brain</p>
                  <p className="text-sm font-medium">Neural Architecture Tuning</p>
                </div>
              </div>

              <div className="flex items-start gap-4 p-4 rounded-lg bg-white/40 border border-white/60">
                <span className="material-symbols-outlined text-primary">record_voice_over</span>
                <div>
                  <p className="text-xs font-bold text-primary uppercase tracking-wider">Voice</p>
                  <p className="text-sm font-medium">HD Synthesis Engine</p>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-8 rounded-lg overflow-hidden relative aspect-video">
            <img
              className="w-full h-full object-cover"
              alt="AI neural network visualization"
              src="https://lh3.googleusercontent.com/aida-public/AB6AXuAjGQgEPOAJzYkZ2qA2-h-zT3AjDDnIi124PBwuSnjPC6FkiYnwslyps8OImX4v3YJ7TUZxzyIlLF_CE2XTfH_fSyCjjZEzHdAJQcnp8gRpyxNh9z3nbwaeRkNBmcrLWYgM51rsujI1uBzepfsN_uXk1wOqmy2KRwGauFHqCTvYYeVzQ_-4yYxZFcxL5du_I9PFOqwVMEthB_ceAbcPwjwrD4hTPGacnWFYMMMtOCk7tdAyEDdhVxb0vfYmSo_c9pDALOnG49X6YGLb"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-secondary/40 to-transparent" />
          </div>
        </div>

        {/* Right Side: Form Content */}
        <div className="w-full md:w-7/12 p-8 md:p-12">
          <div className="flex justify-between items-center mb-8">
            <h3 className="text-xl font-headline font-bold">New Configuration</h3>
            <button
              onClick={onClose}
              className="p-2 hover:bg-slate-100 rounded-full transition-colors active:scale-95"
            >
              <span className="material-symbols-outlined text-outline">close</span>
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Chatbot Name */}
            <div className="space-y-2">
              <label className="text-sm font-label font-semibold text-on-surface-variant flex items-center gap-2">
                <span className="material-symbols-outlined text-xs">badge</span>
                Chatbot Name
              </label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                placeholder="e.g. Nexus Prime"
                className="w-full px-4 py-3 rounded-full border border-outline-variant focus:ring-2 focus:ring-secondary focus:border-secondary bg-white/50 backdrop-blur-sm transition-all"
                required
              />
            </div>

            {/* LLM Model Selection */}
            <div className="space-y-2">
              <label className="text-sm font-label font-semibold text-on-surface-variant flex items-center gap-2">
                <span className="material-symbols-outlined text-xs">memory</span>
                LLM Model Architecture
              </label>
              <div className="relative">
                <select
                  name="model"
                  value={formData.model}
                  onChange={handleChange}
                  className="w-full px-4 py-3 rounded-full border border-outline-variant appearance-none focus:ring-2 focus:ring-secondary focus:border-secondary bg-white/50 backdrop-blur-sm transition-all pr-12"
                >
                  <option>GPT-4o (Omni) - Fastest & Smartest</option>
                  <option>Claude 3.5 Sonnet - Creative & Precise</option>
                  <option>Llama 3 70B - Open Source Excellence</option>
                  <option>Mistral Large - High Performance</option>
                </select>
                <span className="material-symbols-outlined absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-outline">
                  expand_more
                </span>
              </div>
            </div>

            {/* Personality Description */}
            <div className="space-y-2">
              <label className="text-sm font-label font-semibold text-on-surface-variant flex items-center gap-2">
                <span className="material-symbols-outlined text-xs">psychology</span>
                Personality Description
              </label>
              <textarea
                name="personality"
                value={formData.personality}
                onChange={handleChange}
                placeholder="Describe how the AI should behave, its tone, and core knowledge..."
                rows="3"
                className="w-full px-4 py-3 rounded-lg border border-outline-variant focus:ring-2 focus:ring-secondary focus:border-secondary bg-white/50 backdrop-blur-sm transition-all resize-none"
              />
            </div>

            {/* Voice Synthesis Options */}
            <div className="space-y-3">
              <label className="text-sm font-label font-semibold text-on-surface-variant flex items-center gap-2">
                <span className="material-symbols-outlined text-xs">settings_voice</span>
                Voice Synthesis
              </label>
              <div className="grid grid-cols-2 gap-3">
                {[
                  { id: 'male', label: 'Male (Alpha)' },
                  { id: 'female', label: 'Female (Luna)' },
                ].map((voice) => (
                  <button
                    key={voice.id}
                    type="button"
                    onClick={() =>
                      setFormData((prev) => ({
                        ...prev,
                        voice: voice.id,
                      }))
                    }
                    className={`flex items-center gap-3 p-3 rounded-full border-2 transition-all ${
                      formData.voice === voice.id
                        ? 'border-secondary bg-secondary/10 text-secondary'
                        : 'border-outline-variant hover:border-secondary hover:bg-secondary/5'
                    }`}
                  >
                    <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>
                      person_play
                    </span>
                    <span className="text-xs font-bold">{voice.label}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Buttons */}
            <div className="flex items-center justify-end gap-4 pt-6 border-t border-slate-200">
              <button
                type="button"
                onClick={onClose}
                className="px-6 py-3 rounded-full font-label font-semibold text-on-surface-variant hover:bg-slate-100 transition-colors active:scale-95"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-8 py-3 rounded-full font-label font-bold bg-secondary text-white shadow-lg shadow-secondary/20 hover:brightness-110 active:scale-95 transition-all flex items-center gap-2"
              >
                <span>Create Chatbot</span>
                <span className="material-symbols-outlined text-sm">arrow_forward</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default CreateChatbotModal;
