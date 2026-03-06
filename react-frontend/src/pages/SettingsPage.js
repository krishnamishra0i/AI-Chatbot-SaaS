import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { modelsAPI, ttsAPI, memoryAPI } from '../services/api';
import {
  Settings, Cpu, Mic, Volume2, Brain, Sliders,
  Trash2, Save, Check
} from 'lucide-react';

// ── Styled Components ──────────────────────────────────

const PageContainer = styled.div`
  min-height: 100vh;
  background: #0a0a0a;
  color: #fff;
  padding: 30px;
`;

const Header = styled.div`
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 30px;
`;

const Title = styled.h1`
  font-size: 28px; font-weight: 700;
  background: linear-gradient(135deg, #a78bfa, #06b6d4);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
`;

const BackBtn = styled.button`
  background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
  color: #fff; padding: 10px 20px; border-radius: 12px; cursor: pointer;
  transition: all 0.2s;
  &:hover { background: rgba(255,255,255,0.1); }
`;

const Grid = styled.div`
  display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
`;

const Card = styled.div`
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 16px; padding: 24px;
  transition: border-color 0.2s;
  &:hover { border-color: rgba(167,139,250,0.3); }
`;

const CardTitle = styled.h2`
  font-size: 18px; font-weight: 600; margin-bottom: 20px;
  display: flex; align-items: center; gap: 10px;
  svg { color: #a78bfa; }
`;

const Label = styled.label`
  display: block; font-size: 13px; color: rgba(255,255,255,0.5);
  margin-bottom: 6px; margin-top: 16px;
`;

const Select = styled.select`
  width: 100%; padding: 10px 14px; background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1); border-radius: 10px;
  color: #fff; font-size: 14px; outline: none;
  &:focus { border-color: #a78bfa; }
  option { background: #1a1a1a; }
`;



const RangeContainer = styled.div`
  display: flex; align-items: center; gap: 12px;
`;

const RangeInput = styled.input`
  flex: 1; accent-color: #a78bfa;
`;

const RangeValue = styled.span`
  font-size: 14px; color: #a78bfa; min-width: 50px; text-align: right;
`;

const TextArea = styled.textarea`
  width: 100%; padding: 12px 14px; background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1); border-radius: 10px;
  color: #fff; font-size: 14px; outline: none; min-height: 120px;
  resize: vertical; font-family: inherit;
  &:focus { border-color: #a78bfa; }
`;

const Toggle = styled.div`
  display: flex; align-items: center; gap: 10px; margin-top: 16px;
`;

const ToggleSwitch = styled.label`
  position: relative; width: 44px; height: 24px; cursor: pointer;
  input { opacity: 0; width: 0; height: 0; }
  span {
    position: absolute; inset: 0; background: rgba(255,255,255,0.1);
    border-radius: 24px; transition: 0.3s;
    &:before {
      content: ''; position: absolute; height: 18px; width: 18px;
      left: 3px; bottom: 3px; background: white; border-radius: 50%;
      transition: 0.3s;
    }
  }
  input:checked + span { background: #a78bfa; }
  input:checked + span:before { transform: translateX(20px); }
`;

const ToggleLabel = styled.span`
  font-size: 14px; color: rgba(255,255,255,0.7);
`;

const ProviderBadge = styled.span`
  display: inline-flex; padding: 3px 10px; border-radius: 20px;
  font-size: 11px; font-weight: 600; text-transform: uppercase;
  background: ${p => ({
    groq: 'rgba(249,115,22,0.15)',
    openai: 'rgba(16,185,129,0.15)',
    google: 'rgba(59,130,246,0.15)',
    mock: 'rgba(255,255,255,0.05)',
  }[p.$provider] || 'rgba(255,255,255,0.05)')};
  color: ${p => ({
    groq: '#f97316',
    openai: '#10b981',
    google: '#3b82f6',
    mock: 'rgba(255,255,255,0.4)',
  }[p.$provider] || 'rgba(255,255,255,0.4)')};
`;

const ModelCard = styled.div`
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px 16px; border-radius: 10px; cursor: pointer;
  background: ${p => p.$active ? 'rgba(167,139,250,0.1)' : 'rgba(255,255,255,0.02)'};
  border: 1px solid ${p => p.$active ? 'rgba(167,139,250,0.3)' : 'rgba(255,255,255,0.05)'};
  margin-bottom: 8px; transition: all 0.2s;
  &:hover { background: rgba(167,139,250,0.08); }
`;

const SaveBtn = styled.button`
  display: flex; align-items: center; gap: 8px;
  background: linear-gradient(135deg, #a78bfa, #06b6d4);
  color: #fff; border: none; padding: 12px 24px; border-radius: 12px;
  font-size: 14px; font-weight: 600; cursor: pointer; margin-top: 20px;
  transition: opacity 0.2s;
  &:hover { opacity: 0.9; }
  &:disabled { opacity: 0.5; cursor: not-allowed; }
`;

const StatusDot = styled.span`
  width: 8px; height: 8px; border-radius: 50%;
  background: ${p => p.$active ? '#22c55e' : '#ef4444'};
  display: inline-block; margin-right: 6px;
`;

const MemoryItem = styled.div`
  display: flex; justify-content: space-between; align-items: center;
  padding: 10px 14px; border-radius: 8px;
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.05);
  margin-bottom: 6px;
`;

// ── Main Component ──────────────────────────────────

export default function SettingsPage({ onNavigate }) {
  const [models, setModels] = useState([]);
  const [providers, setProviders] = useState([]);
  const [prompts, setPrompts] = useState([]);
  const [voiceCategories, setVoiceCategories] = useState({});
  const [memorySessions, setMemorySessions] = useState([]);
  const [saved, setSaved] = useState(false);

  // Settings state (persisted to localStorage)
  const [config, setConfig] = useState(() => {
    const saved = localStorage.getItem('athena_settings');
    return saved ? JSON.parse(saved) : {
      model: 'groq/llama-3.3-70b-versatile',
      temperature: 0.7,
      maxTokens: 1024,
      streaming: true,
      promptTemplate: 'avatar_conversational',
      customPrompt: '',
      emotion: 'neutral',
      voice: 'en-US-GuyNeural',
      ttsSpeed: '+0%',
      ttsPitch: '+0Hz',
      ttsEnabled: true,
      sttEnabled: false,
      avatarEnabled: true,
      expressionIntensity: 0.7,
      idleAnimation: true,
    };
  });

  const updateConfig = (key, value) => {
    setConfig(prev => ({ ...prev, [key]: value }));
  };

  const saveSettings = () => {
    localStorage.setItem('athena_settings', JSON.stringify(config));
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
    // Dispatch event for other components
    window.dispatchEvent(new CustomEvent('settings:updated', { detail: config }));
  };

  // Load data on mount
  useEffect(() => {
    Promise.allSettled([
      modelsAPI.list(),
      modelsAPI.providers(),
      modelsAPI.prompts(),
      ttsAPI.voiceCategories(),
      memoryAPI.listSessions(),
    ]).then(([modelsRes, providersRes, promptsRes, voicesRes, memoryRes]) => {
      if (modelsRes.status === 'fulfilled') setModels(modelsRes.value.data?.data || []);
      if (providersRes.status === 'fulfilled') setProviders(providersRes.value.data?.providers || []);
      if (promptsRes.status === 'fulfilled') setPrompts(promptsRes.value.data?.templates || []);
      if (voicesRes.status === 'fulfilled') setVoiceCategories(voicesRes.value.data || {});
      if (memoryRes.status === 'fulfilled') setMemorySessions(memoryRes.value.data?.sessions || []);
    });
  }, []);

  const clearMemory = async (sessionId) => {
    try {
      await memoryAPI.clearSession(sessionId);
      setMemorySessions(prev => prev.filter(s => s.session_id !== sessionId));
    } catch (e) { console.error(e); }
  };

  return (
    <PageContainer>
      <Header>
        <Title><Settings size={28} /> Platform Settings</Title>
        <BackBtn onClick={() => onNavigate('home')}>← Back to Home</BackBtn>
      </Header>

      <Grid>
        {/* ─── SECTION A: Model Management ─── */}
        <Card>
          <CardTitle><Cpu size={20} /> LLM Model Selection</CardTitle>

          <Label>Active Providers</Label>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {providers.map(p => (
              <ProviderBadge key={p.id} $provider={p.id}>
                <StatusDot $active={p.status === 'active'} />
                {p.name}
              </ProviderBadge>
            ))}
            {providers.length === 0 && (
              <ProviderBadge $provider="mock">
                <StatusDot $active={true} />
                Mock (No API keys)
              </ProviderBadge>
            )}
          </div>

          <Label>Select Model</Label>
          {models.map(m => (
            <ModelCard
              key={m.id}
              $active={config.model === m.id}
              onClick={() => updateConfig('model', m.id)}
            >
              <div>
                <div style={{ fontWeight: 600, fontSize: '14px' }}>{m.name}</div>
                <div style={{ fontSize: '12px', color: 'rgba(255,255,255,0.4)' }}>
                  {m.description || m.id} · {m.max_tokens?.toLocaleString()} tokens
                </div>
              </div>
              <ProviderBadge $provider={m.provider}>{m.provider}</ProviderBadge>
            </ModelCard>
          ))}

          <Label>Temperature</Label>
          <RangeContainer>
            <RangeInput
              type="range" min="0" max="2" step="0.1"
              value={config.temperature}
              onChange={e => updateConfig('temperature', parseFloat(e.target.value))}
            />
            <RangeValue>{config.temperature}</RangeValue>
          </RangeContainer>

          <Label>Max Tokens</Label>
          <RangeContainer>
            <RangeInput
              type="range" min="256" max="8192" step="256"
              value={config.maxTokens}
              onChange={e => updateConfig('maxTokens', parseInt(e.target.value))}
            />
            <RangeValue>{config.maxTokens}</RangeValue>
          </RangeContainer>

          <Toggle>
            <ToggleSwitch>
              <input type="checkbox" checked={config.streaming}
                onChange={e => updateConfig('streaming', e.target.checked)} />
              <span />
            </ToggleSwitch>
            <ToggleLabel>Enable Streaming</ToggleLabel>
          </Toggle>
        </Card>

        {/* ─── System Prompt / Personality ─── */}
        <Card>
          <CardTitle><Brain size={20} /> System Prompt & Personality</CardTitle>

          <Label>Prompt Template</Label>
          <Select
            value={config.promptTemplate}
            onChange={e => updateConfig('promptTemplate', e.target.value)}
          >
            {prompts.map(p => (
              <option key={p.id} value={p.id}>{p.id.replace(/_/g, ' ')}</option>
            ))}
          </Select>

          <Label>Emotion Modifier</Label>
          <Select
            value={config.emotion}
            onChange={e => updateConfig('emotion', e.target.value)}
          >
            <option value="neutral">Neutral</option>
            <option value="happy">Happy / Upbeat</option>
            <option value="empathetic">Empathetic / Caring</option>
            <option value="serious">Serious / Direct</option>
            <option value="excited">Excited / Energetic</option>
            <option value="calm">Calm / Reassuring</option>
          </Select>

          <Label>Custom System Prompt (overrides template)</Label>
          <TextArea
            value={config.customPrompt}
            onChange={e => updateConfig('customPrompt', e.target.value)}
            placeholder="Leave empty to use the selected template..."
          />
        </Card>

        {/* ─── SECTION C: Speech System ─── */}
        <Card>
          <CardTitle><Volume2 size={20} /> TTS (Text-to-Speech)</CardTitle>

          <Toggle>
            <ToggleSwitch>
              <input type="checkbox" checked={config.ttsEnabled}
                onChange={e => updateConfig('ttsEnabled', e.target.checked)} />
              <span />
            </ToggleSwitch>
            <ToggleLabel>Enable TTS</ToggleLabel>
          </Toggle>

          <Label>Voice</Label>
          <Select
            value={config.voice}
            onChange={e => updateConfig('voice', e.target.value)}
          >
            <optgroup label="Male Voices">
              {(voiceCategories.male || []).map(v => (
                <option key={v.id} value={v.id}>{v.name}</option>
              ))}
            </optgroup>
            <optgroup label="Female Voices">
              {(voiceCategories.female || []).map(v => (
                <option key={v.id} value={v.id}>{v.name}</option>
              ))}
            </optgroup>
          </Select>

          <Label>Speed</Label>
          <RangeContainer>
            <RangeInput
              type="range" min="-50" max="100" step="5"
              value={parseInt(config.ttsSpeed)}
              onChange={e => updateConfig('ttsSpeed', `${e.target.value >= 0 ? '+' : ''}${e.target.value}%`)}
            />
            <RangeValue>{config.ttsSpeed}</RangeValue>
          </RangeContainer>

          <Label>Pitch</Label>
          <RangeContainer>
            <RangeInput
              type="range" min="-50" max="50" step="5"
              value={parseInt(config.ttsPitch)}
              onChange={e => updateConfig('ttsPitch', `${e.target.value >= 0 ? '+' : ''}${e.target.value}Hz`)}
            />
            <RangeValue>{config.ttsPitch}</RangeValue>
          </RangeContainer>
        </Card>

        {/* ─── STT Settings ─── */}
        <Card>
          <CardTitle><Mic size={20} /> STT (Speech-to-Text)</CardTitle>

          <Toggle>
            <ToggleSwitch>
              <input type="checkbox" checked={config.sttEnabled}
                onChange={e => updateConfig('sttEnabled', e.target.checked)} />
              <span />
            </ToggleSwitch>
            <ToggleLabel>Enable STT (Voice Input)</ToggleLabel>
          </Toggle>

          <div style={{ marginTop: '16px', fontSize: '13px', color: 'rgba(255,255,255,0.4)' }}>
            <p>Engine: OpenAI Whisper (local)</p>
            <p>Model: base (~140MB, downloaded on first use)</p>
            <p>Supported: WAV, MP3, OGG, FLAC, M4A, WebM</p>
            <p style={{ marginTop: '10px', color: 'rgba(255,255,255,0.6)' }}>
              Microphone access required. Works best in Chrome/Edge.
            </p>
          </div>
        </Card>

        {/* ─── SECTION B: Avatar Settings ─── */}
        <Card>
          <CardTitle><Sliders size={20} /> Avatar & Lip Sync</CardTitle>

          <Toggle>
            <ToggleSwitch>
              <input type="checkbox" checked={config.avatarEnabled}
                onChange={e => updateConfig('avatarEnabled', e.target.checked)} />
              <span />
            </ToggleSwitch>
            <ToggleLabel>Enable Avatar</ToggleLabel>
          </Toggle>

          <Label>Expression Intensity</Label>
          <RangeContainer>
            <RangeInput
              type="range" min="0" max="1" step="0.1"
              value={config.expressionIntensity}
              onChange={e => updateConfig('expressionIntensity', parseFloat(e.target.value))}
            />
            <RangeValue>{Math.round(config.expressionIntensity * 100)}%</RangeValue>
          </RangeContainer>

          <Toggle>
            <ToggleSwitch>
              <input type="checkbox" checked={config.idleAnimation}
                onChange={e => updateConfig('idleAnimation', e.target.checked)} />
              <span />
            </ToggleSwitch>
            <ToggleLabel>Idle Animation</ToggleLabel>
          </Toggle>

          <div style={{ marginTop: '16px', fontSize: '13px', color: 'rgba(255,255,255,0.4)' }}>
            <p>Lip Sync: Phoneme-to-Viseme (MPEG-4 standard)</p>
            <p>Pipeline: LLM → Sentence Chunks → TTS → Visemes → Render</p>
            <p style={{ marginTop: '8px' }}>Target latency: &lt; 1.2s end-to-end</p>
          </div>
        </Card>

        {/* ─── SECTION E: Memory ─── */}
        <Card>
          <CardTitle><Brain size={20} /> Conversation Memory</CardTitle>

          <div style={{ fontSize: '13px', color: 'rgba(255,255,255,0.4)', marginBottom: '16px' }}>
            <p>Short-term: Last 20 conversation turns per session</p>
            <p>Context window: System prompt + history + current message</p>
          </div>

          <Label>Active Sessions ({memorySessions.length})</Label>
          {memorySessions.length === 0 && (
            <div style={{ fontSize: '13px', color: 'rgba(255,255,255,0.3)', padding: '10px 0' }}>
              No active sessions yet. Start chatting to create one.
            </div>
          )}
          {memorySessions.map(s => (
            <MemoryItem key={s.session_id}>
              <div>
                <div style={{ fontSize: '14px', fontWeight: 500 }}>{s.session_id}</div>
                <div style={{ fontSize: '12px', color: 'rgba(255,255,255,0.4)' }}>
                  {s.turns} turns · max {s.max_turns}
                </div>
              </div>
              <Trash2
                size={16}
                style={{ cursor: 'pointer', color: '#ef4444' }}
                onClick={() => clearMemory(s.session_id)}
              />
            </MemoryItem>
          ))}
        </Card>
      </Grid>

      <div style={{ display: 'flex', justifyContent: 'center', marginTop: '30px' }}>
        <SaveBtn onClick={saveSettings}>
          {saved ? <><Check size={18} /> Saved!</> : <><Save size={18} /> Save Settings</>}
        </SaveBtn>
      </div>
    </PageContainer>
  );
}
