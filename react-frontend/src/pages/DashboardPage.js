// Dashboard — Chatbot management, API keys, usage analytics
import React, { useState, useEffect, useCallback } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import { chatbotsAPI, apiKeysAPI, usageAPI, modelsAPI } from '../services/api';
import ChatModalAdvanced from './ChatModalAdvanced';

// ── Styled Components ────────────────────────────────

const DashContainer = styled.div`
  min-height: 100vh;
  background: #0B0F19;
  color: #fff;
  font-family: 'Inter', sans-serif;
`;

const TopBar = styled.header`
  position: sticky;
  top: 0;
  background: rgba(11, 15, 25, 0.9);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255,255,255,0.05);
  padding: 16px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 100;
`;

const Logo = styled.div`
  font-size: 22px;
  font-weight: 800;
  background: linear-gradient(135deg, #8B5CF6, #3B82F6, #06B6D4);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  cursor: pointer;
`;

const UserInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
`;

const UserName = styled.span`
  font-size: 14px;
  color: rgba(255,255,255,0.7);
`;

const LogoutBtn = styled.button`
  padding: 8px 16px;
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 8px;
  color: #ef4444;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s;
  &:hover { background: rgba(239, 68, 68, 0.25); }
`;

const Content = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 24px;
`;

const Tabs = styled.div`
  display: flex;
  gap: 8px;
  margin-bottom: 32px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
  padding-bottom: 0;
`;

const Tab = styled.button`
  padding: 12px 24px;
  background: none;
  border: none;
  border-bottom: 2px solid ${p => p.$active ? '#8B5CF6' : 'transparent'};
  color: ${p => p.$active ? '#fff' : 'rgba(255,255,255,0.5)'};
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  &:hover { color: #fff; }
`;

const SectionTitle = styled.h2`
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 24px;
`;

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
`;

const Card = styled(motion.div)`
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 16px;
  padding: 24px;
  transition: all 0.3s;
  &:hover {
    border-color: rgba(139, 92, 246, 0.3);
    transform: translateY(-2px);
  }
`;

const StatCard = styled(Card)`
  text-align: center;
`;

const StatValue = styled.div`
  font-size: 36px;
  font-weight: 800;
  background: linear-gradient(135deg, #8B5CF6, #3B82F6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 8px;
`;

const StatLabel = styled.div`
  font-size: 14px;
  color: rgba(255,255,255,0.5);
`;

const Input = styled.input`
  width: 100%;
  padding: 12px 14px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 10px;
  color: #fff;
  font-size: 14px;
  margin-bottom: 12px;
  outline: none;
  box-sizing: border-box;
  &:focus { border-color: rgba(139, 92, 246, 0.5); }
  &::placeholder { color: rgba(255,255,255,0.3); }
`;

const Select = styled.select`
  width: 100%;
  padding: 12px 14px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 10px;
  color: #fff;
  font-size: 14px;
  margin-bottom: 12px;
  outline: none;
  box-sizing: border-box;
  option { background: #1a1f2e; }
`;

const TextArea = styled.textarea`
  width: 100%;
  padding: 12px 14px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 10px;
  color: #fff;
  font-size: 14px;
  margin-bottom: 12px;
  outline: none;
  resize: vertical;
  min-height: 80px;
  box-sizing: border-box;
  font-family: inherit;
  &:focus { border-color: rgba(139, 92, 246, 0.5); }
  &::placeholder { color: rgba(255,255,255,0.3); }
`;

const Btn = styled.button`
  padding: ${p => p.$size === 'sm' ? '8px 16px' : '12px 24px'};
  background: ${p => p.$variant === 'danger' ? 'rgba(239, 68, 68, 0.15)' :
    p.$variant === 'secondary' ? 'rgba(255,255,255,0.06)' :
    'linear-gradient(135deg, #8B5CF6, #3B82F6)'};
  border: 1px solid ${p => p.$variant === 'danger' ? 'rgba(239, 68, 68, 0.3)' :
    p.$variant === 'secondary' ? 'rgba(255,255,255,0.1)' : 'transparent'};
  border-radius: 10px;
  color: ${p => p.$variant === 'danger' ? '#ef4444' : '#fff'};
  font-size: ${p => p.$size === 'sm' ? '13px' : '14px'};
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  &:hover { transform: translateY(-1px); }
  &:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
`;

const Badge = styled.span`
  display: inline-block;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  background: ${p => p.$status === 'active' ? 'rgba(34, 197, 94, 0.15)' :
    p.$status === 'paused' ? 'rgba(234, 179, 8, 0.15)' : 'rgba(107, 114, 128, 0.15)'};
  color: ${p => p.$status === 'active' ? '#22c55e' :
    p.$status === 'paused' ? '#eab308' : '#6b7280'};
  border: 1px solid ${p => p.$status === 'active' ? 'rgba(34, 197, 94, 0.3)' :
    p.$status === 'paused' ? 'rgba(234, 179, 8, 0.3)' : 'rgba(107, 114, 128, 0.3)'};
`;

const Modal = styled(motion.div)`
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
`;

const ModalContent = styled(motion.div)`
  background: #1a1f2e;
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 20px;
  padding: 32px;
  width: 100%;
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
`;

const ModalTitle = styled.h3`
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 20px;
`;

const KeyDisplay = styled.div`
  background: rgba(0,0,0,0.3);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 8px;
  padding: 12px;
  font-family: 'Fira Code', monospace;
  font-size: 13px;
  color: #22c55e;
  word-break: break-all;
  margin-bottom: 12px;
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 60px 20px;
  color: rgba(255,255,255,0.4);
  
  .icon {
    font-size: 48px;
    margin-bottom: 16px;
  }
  
  p { margin-bottom: 20px; }
`;

const TableRow = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 12px;
  margin-bottom: 10px;
  transition: all 0.3s;
  &:hover { border-color: rgba(255,255,255,0.12); }
`;

// ── Dashboard Component ──────────────────────────────

export default function DashboardPage({ onNavigate }) {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const [chatbots, setChatbots] = useState([]);
  const [apiKeys, setApiKeys] = useState([]);
  const [usage, setUsage] = useState(null);
  const [models, setModels] = useState([]);
  const [showCreateBot, setShowCreateBot] = useState(false);
  const [showCreateKey, setShowCreateKey] = useState(false);
  const [newKeyResult, setNewKeyResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedChatbot, setSelectedChatbot] = useState(null);

  // Form state
  const [botForm, setBotForm] = useState({
    name: '', system_prompt: '', llm_model: 'gpt-3.5-turbo',
    voice_id: 'en-US-GuyNeural', temperature: 0.7, max_tokens: 1024,
  });
  const [keyName, setKeyName] = useState('Default Key');

  const loadData = useCallback(async () => {
    try {
      console.log('[Dashboard] Loading data...');
      
      // Load chatbots
      const botsRes = await chatbotsAPI.list().catch((err) => {
        console.error('[Dashboard] Failed to load chatbots:', err);
        return { data: [] };
      });
      
      // Load API keys
      const keysRes = await apiKeysAPI.list().catch((err) => {
        console.error('[Dashboard] Failed to load API keys:', err);
        return { data: [] };
      });
      
      // Load usage (non-critical, skip if fails)
      let usageData = null;
      try {
        const usageRes = await usageAPI.summary();
        usageData = usageRes.data;
        console.log('[Dashboard] Usage data loaded');
      } catch (err) {
        console.warn('[Dashboard] Usage API failed (non-critical):', err.response?.status, err.response?.data?.detail);
        // Continue without usage data
        usageData = null;
      }
      
      // Load models
      const modelsRes = await modelsAPI.list().catch((err) => {
        console.error('[Dashboard] Failed to load models:', err);
        return { data: { data: [] } };
      });
      
      setChatbots(botsRes.data || []);
      setApiKeys(keysRes.data || []);
      setUsage(usageData);
      setModels(modelsRes.data?.data || []);
      
      console.log('[Dashboard] Data loaded successfully');
    } catch (err) {
      console.error('[Dashboard] Failed to load dashboard data:', err);
    }
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  // ── Chatbot CRUD ─────────────────────────────────

  const createChatbot = async () => {
    if (!botForm.name.trim()) return;
    setLoading(true);
    try {
      console.log('[Dashboard] Creating chatbot with data:', botForm);
      const token = localStorage.getItem('athena_token');
      console.log('[Dashboard] Token status:', token ? 'Present' : 'Missing');
      
      await chatbotsAPI.create(botForm);
      
      console.log('[Dashboard] Chatbot created successfully');
      setShowCreateBot(false);
      setBotForm({ name: '', system_prompt: '', llm_model: 'gpt-4o-mini', voice_id: 'en-US-GuyNeural', temperature: 0.7, max_tokens: 1024 });
      loadData();
    } catch (err) {
      console.error('[Dashboard] Chatbot creation failed:', err);
      console.error('[Dashboard] Error details:', {
        status: err.response?.status,
        statusText: err.response?.statusText,
        data: err.response?.data,
        headers: err.config?.headers,
      });
      
      const errorMessage = 
        err.response?.status === 401 ? 'Authentication failed. Please check the Debug page (🔍 Debug button) - your token might not be sent correctly.' :
        err.response?.status === 400 ? `Invalid input: ${err.response?.data?.detail || 'Please check your chatbot settings.'}` :
        err.response?.data?.detail || err.message || 'Failed to create chatbot';
      
      alert(errorMessage);
    }
    setLoading(false);
  };

  const deleteChatbot = async (id) => {
    if (!window.confirm('Delete this chatbot?')) return;
    try {
      await chatbotsAPI.delete(id);
      loadData();
    } catch (err) {
      alert('Failed to delete chatbot');
    }
  };

  const toggleChatbotStatus = async (bot) => {
    const newStatus = bot.status === 'active' ? 'paused' : 'active';
    try {
      await chatbotsAPI.update(bot.id, { status: newStatus });
      loadData();
    } catch (err) {
      alert('Failed to update chatbot');
    }
  };

  // ── API Key Management ───────────────────────────

  const createApiKey = async () => {
    setLoading(true);
    try {
      const res = await apiKeysAPI.create(keyName);
      setNewKeyResult(res.data);
      setShowCreateKey(false);
      setKeyName('Default Key');
      loadData();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to create API key');
    }
    setLoading(false);
  };

  const revokeApiKey = async (id) => {
    if (!window.confirm('Revoke this API key? This action cannot be undone.')) return;
    try {
      await apiKeysAPI.revoke(id);
      loadData();
    } catch (err) {
      alert('Failed to revoke key');
    }
  };

  const handleLogout = () => {
    logout();
    onNavigate('home');
  };

  // ── Render ───────────────────────────────────────

  return (
    <DashContainer>
      <TopBar>
        <Logo onClick={() => onNavigate('home')}>ATHENA AI</Logo>
        <UserInfo>
          <UserName>{user?.name || user?.email}</UserName>
          <Badge $status="active">{user?.plan || 'free'}</Badge>
          <LogoutBtn onClick={handleLogout}>Logout</LogoutBtn>
        </UserInfo>
      </TopBar>

      <Content>
        <Tabs>
          <Tab $active={activeTab === 'overview'} onClick={() => setActiveTab('overview')}>Overview</Tab>
          <Tab $active={activeTab === 'chatbots'} onClick={() => setActiveTab('chatbots')}>Chatbots</Tab>
          <Tab $active={activeTab === 'apikeys'} onClick={() => setActiveTab('apikeys')}>API Keys</Tab>
          <Tab $active={activeTab === 'usage'} onClick={() => setActiveTab('usage')}>Usage</Tab>
        </Tabs>

        {/* ── Overview Tab ── */}
        {activeTab === 'overview' && (
          <>
            <SectionTitle>Dashboard</SectionTitle>
            <Grid>
              <StatCard>
                <StatValue>{chatbots.length}</StatValue>
                <StatLabel>Chatbots</StatLabel>
              </StatCard>
              <StatCard>
                <StatValue>{apiKeys.length}</StatValue>
                <StatLabel>API Keys</StatLabel>
              </StatCard>
              <StatCard>
                <StatValue>{usage?.total_messages || 0}</StatValue>
                <StatLabel>Messages (30d)</StatLabel>
              </StatCard>
              <StatCard>
                <StatValue>{usage?.total_tokens || 0}</StatValue>
                <StatLabel>Tokens Used (30d)</StatLabel>
              </StatCard>
            </Grid>

            <SectionTitle>Quick Actions</SectionTitle>
            <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
              <Btn onClick={() => { setActiveTab('chatbots'); setShowCreateBot(true); }}>+ Create Chatbot</Btn>
              <Btn $variant="secondary" onClick={() => setActiveTab('apikeys')}>Manage API Keys</Btn>
              <Btn $variant="secondary" onClick={() => onNavigate('home')}>Back to Home</Btn>
            </div>
          </>
        )}

        {/* ── Chatbots Tab ── */}
        {activeTab === 'chatbots' && (
          <>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
              <SectionTitle style={{ margin: 0 }}>Your Chatbots</SectionTitle>
              <Btn onClick={() => setShowCreateBot(true)}>+ Create Chatbot</Btn>
            </div>

            {chatbots.length === 0 ? (
              <EmptyState>
                <div className="icon">🤖</div>
                <p>No chatbots yet. Create your first one!</p>
                <Btn onClick={() => setShowCreateBot(true)}>+ Create Chatbot</Btn>
              </EmptyState>
            ) : (
              <Grid>
                {chatbots.map(bot => (
                  <Card 
                    key={bot.id}
                    onClick={() => setSelectedChatbot(bot)}
                    style={{ cursor: 'pointer' }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                      <div>
                        <h3 style={{ fontSize: '18px', fontWeight: '700', marginBottom: '4px' }}>{bot.name}</h3>
                        <Badge $status={bot.status}>{bot.status}</Badge>
                      </div>
                      <div style={{ display: 'flex', gap: '8px' }} onClick={(e) => e.stopPropagation()}>
                        <Btn $size="sm" $variant="secondary" onClick={() => toggleChatbotStatus(bot)}>
                          {bot.status === 'active' ? 'Pause' : 'Resume'}
                        </Btn>
                        <Btn $size="sm" $variant="danger" onClick={() => deleteChatbot(bot.id)}>Delete</Btn>
                      </div>
                    </div>
                    <div style={{ fontSize: '13px', color: 'rgba(255,255,255,0.4)', marginBottom: '8px' }}>
                      Model: {bot.llm_model} | Voice: {bot.voice_id}
                    </div>
                    {bot.system_prompt && (
                      <div style={{ fontSize: '13px', color: 'rgba(255,255,255,0.5)', marginTop: '8px', fontStyle: 'italic' }}>
                        "{bot.system_prompt?.substring(0, 100)}{bot.system_prompt?.length > 100 ? '...' : ''}"
                      </div>
                    )}
                    <div style={{ fontSize: '11px', color: 'rgba(255,255,255,0.3)', marginTop: '12px' }}>
                      Created: {new Date(bot.created_at).toLocaleDateString()}
                    </div>
                    <div style={{ marginTop: '12px', paddingTop: '12px', borderTop: '1px solid rgba(255,255,255,0.08)', textAlign: 'center', fontSize: '12px', color: 'rgba(139, 92, 246, 0.8)', fontWeight: '600' }}>
                      💬 Click to Chat
                    </div>
                  </Card>
                ))}
              </Grid>
            )}
          </>
        )}

        {/* ── API Keys Tab ── */}
        {activeTab === 'apikeys' && (
          <>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
              <SectionTitle style={{ margin: 0 }}>API Keys</SectionTitle>
              <Btn onClick={() => setShowCreateKey(true)}>+ Generate Key</Btn>
            </div>

            {apiKeys.length === 0 ? (
              <EmptyState>
                <div className="icon">🔑</div>
                <p>No API keys. Generate one to use the API programmatically.</p>
                <Btn onClick={() => setShowCreateKey(true)}>+ Generate Key</Btn>
              </EmptyState>
            ) : (
              apiKeys.map(key => (
                <TableRow key={key.id}>
                  <div>
                    <div style={{ fontWeight: '600', marginBottom: '4px' }}>{key.name}</div>
                    <div style={{ fontSize: '13px', color: 'rgba(255,255,255,0.4)', fontFamily: 'monospace' }}>
                      {key.key_prefix}...
                    </div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <Badge $status={key.is_active ? 'active' : 'archived'}>
                      {key.is_active ? 'Active' : 'Revoked'}
                    </Badge>
                    <div style={{ fontSize: '12px', color: 'rgba(255,255,255,0.3)' }}>
                      {new Date(key.created_at).toLocaleDateString()}
                    </div>
                    {key.is_active && (
                      <Btn $size="sm" $variant="danger" onClick={() => revokeApiKey(key.id)}>Revoke</Btn>
                    )}
                  </div>
                </TableRow>
              ))
            )}
          </>
        )}

        {/* ── Usage Tab ── */}
        {activeTab === 'usage' && (
          <>
            <SectionTitle>Usage & Analytics</SectionTitle>
            <Grid>
              <StatCard>
                <StatValue>{usage?.total_messages || 0}</StatValue>
                <StatLabel>Total Messages</StatLabel>
              </StatCard>
              <StatCard>
                <StatValue>{usage?.total_tokens || 0}</StatValue>
                <StatLabel>Tokens Used</StatLabel>
              </StatCard>
              <StatCard>
                <StatValue>{(usage?.total_audio_seconds || 0).toFixed(1)}s</StatValue>
                <StatLabel>Audio Processed</StatLabel>
              </StatCard>
              <StatCard>
                <StatValue>${(usage?.total_cost || 0).toFixed(2)}</StatValue>
                <StatLabel>Total Cost</StatLabel>
              </StatCard>
            </Grid>
            <div style={{ color: 'rgba(255,255,255,0.4)', fontSize: '13px', textAlign: 'center', marginTop: '20px' }}>
              Showing data for: {usage?.period || 'last 30 days'}
            </div>
          </>
        )}
      </Content>

      {/* ── Create Chatbot Modal ── */}
      <AnimatePresence>
        {showCreateBot && (
          <Modal 
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            onClick={() => setShowCreateBot(false)}
          >
            <ModalContent
              initial={{ scale: 0.9 }} animate={{ scale: 1 }} exit={{ scale: 0.9 }}
              onClick={e => e.stopPropagation()}
            >
              <ModalTitle>Create New Chatbot</ModalTitle>
              <Input placeholder="Chatbot Name *" value={botForm.name}
                onChange={e => setBotForm({...botForm, name: e.target.value})} />
              <TextArea placeholder="System Prompt (optional)" value={botForm.system_prompt}
                onChange={e => setBotForm({...botForm, system_prompt: e.target.value})} />
              <Select value={botForm.llm_model}
                onChange={e => setBotForm({...botForm, llm_model: e.target.value})}>
                {models.length > 0 ? models.map(m => (
                  <option key={m.id} value={m.id}>{m.name} ({m.provider})</option>
                )) : (
                  <>
                    <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                    <option value="gpt-4">GPT-4</option>
                    <option value="gpt-4o">GPT-4o</option>
                    <option value="gemini-pro">Gemini Pro</option>
                  </>
                )}
              </Select>
              <Input placeholder="Voice ID" value={botForm.voice_id}
                onChange={e => setBotForm({...botForm, voice_id: e.target.value})} />
              <div style={{ display: 'flex', gap: '12px' }}>
                <div style={{ flex: 1 }}>
                  <label style={{ fontSize: '12px', color: 'rgba(255,255,255,0.4)', marginBottom: '4px', display: 'block' }}>
                    Temperature ({botForm.temperature})
                  </label>
                  <input type="range" min="0" max="2" step="0.1" value={botForm.temperature}
                    onChange={e => setBotForm({...botForm, temperature: parseFloat(e.target.value)})}
                    style={{ width: '100%', marginBottom: '12px' }} />
                </div>
                <div style={{ flex: 1 }}>
                  <label style={{ fontSize: '12px', color: 'rgba(255,255,255,0.4)', marginBottom: '4px', display: 'block' }}>
                    Max Tokens
                  </label>
                  <Input type="number" value={botForm.max_tokens}
                    onChange={e => setBotForm({...botForm, max_tokens: parseInt(e.target.value)})} />
                </div>
              </div>
              <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
                <Btn $variant="secondary" onClick={() => setShowCreateBot(false)}>Cancel</Btn>
                <Btn onClick={createChatbot} disabled={loading || !botForm.name.trim()}>
                  {loading ? 'Creating...' : 'Create Chatbot'}
                </Btn>
              </div>
            </ModalContent>
          </Modal>
        )}
      </AnimatePresence>

      {/* ── Create API Key Modal ── */}
      <AnimatePresence>
        {showCreateKey && (
          <Modal
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            onClick={() => setShowCreateKey(false)}
          >
            <ModalContent
              initial={{ scale: 0.9 }} animate={{ scale: 1 }} exit={{ scale: 0.9 }}
              onClick={e => e.stopPropagation()}
            >
              <ModalTitle>Generate API Key</ModalTitle>
              <Input placeholder="Key Name" value={keyName}
                onChange={e => setKeyName(e.target.value)} />
              <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
                <Btn $variant="secondary" onClick={() => setShowCreateKey(false)}>Cancel</Btn>
                <Btn onClick={createApiKey} disabled={loading}>
                  {loading ? 'Generating...' : 'Generate'}
                </Btn>
              </div>
            </ModalContent>
          </Modal>
        )}
      </AnimatePresence>

      {/* ── New Key Display Modal ── */}
      <AnimatePresence>
        {newKeyResult && (
          <Modal
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            onClick={() => setNewKeyResult(null)}
          >
            <ModalContent
              initial={{ scale: 0.9 }} animate={{ scale: 1 }} exit={{ scale: 0.9 }}
              onClick={e => e.stopPropagation()}
            >
              <ModalTitle>API Key Created!</ModalTitle>
              <p style={{ color: 'rgba(255,255,255,0.6)', fontSize: '14px', marginBottom: '16px' }}>
                Copy this key now. It won't be shown again.
              </p>
              <KeyDisplay>{newKeyResult.full_key}</KeyDisplay>
              <Btn onClick={() => {
                navigator.clipboard.writeText(newKeyResult.full_key);
                alert('Copied to clipboard!');
              }} style={{ width: '100%', marginBottom: '8px' }}>
                Copy to Clipboard
              </Btn>
              <Btn $variant="secondary" onClick={() => setNewKeyResult(null)} style={{ width: '100%' }}>
                Done
              </Btn>
            </ModalContent>
          </Modal>
        )}

        {/* Chat Modal - Advanced */}
        <AnimatePresence>
          {selectedChatbot && (
            <ChatModalAdvanced 
              bot={selectedChatbot} 
              onClose={() => setSelectedChatbot(null)} 
            />
          )}
        </AnimatePresence>
      </AnimatePresence>
    </DashContainer>
  );
}
