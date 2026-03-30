// Chatbot Management Page
import React, { useState, useEffect, useImperativeHandle, forwardRef } from 'react';
import ChatWindow from './ChatWindow';

const API_BASE_URL = (process.env.REACT_APP_API_URL || 'http://localhost:5001').replace(/\/api\/?$/, '');
const FALLBACK_API_BASE_URL = API_BASE_URL.includes(':5000')
  ? API_BASE_URL.replace(':5000', ':5001')
  : API_BASE_URL.includes(':5001')
  ? API_BASE_URL.replace(':5001', ':5000')
  : null;

const getStoredToken = () =>
  localStorage.getItem('athena_token') ||
  localStorage.getItem('token') ||
  localStorage.getItem('accessToken');

const fetchWithPortFallback = async (path, options) => {
  try {
    return await fetch(`${API_BASE_URL}${path}`, options);
  } catch (error) {
    if (!FALLBACK_API_BASE_URL) {
      throw error;
    }
    console.warn('Primary API unreachable, retrying with fallback:', {
      primary: API_BASE_URL,
      fallback: FALLBACK_API_BASE_URL,
      path,
    });
    return await fetch(`${FALLBACK_API_BASE_URL}${path}`, options);
  }
};

const ChatbotsPage = forwardRef(({ onCreateNew }, ref) => {
  const [chatbots, setChatbots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedChatbot, setSelectedChatbot] = useState(null);
  const [deleting, setDeleting] = useState(null);

  // Expose refreshChatbots to parent component
  useImperativeHandle(ref, () => ({
    refreshChatbots: fetchChatbots,
  }));

  const handleDeleteChatbot = async (chatbotId, chatbotName, e) => {
    e.stopPropagation();
    
    const confirmed = window.confirm(
      `Are you sure you want to delete "${chatbotName}"? This action cannot be undone.`
    );
    if (!confirmed) return;

    setDeleting(chatbotId);
    try {
      const token = getStoredToken();
      
      if (!token) {
        alert('Error: Not authenticated');
        return;
      }

      const response = await fetchWithPortFallback(`/api/chatbots/${chatbotId}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok || response.status === 204) {
        console.log('✅ Chatbot deleted successfully');
        alert(`✅ Chatbot "${chatbotName}" deleted successfully!`);
        setChatbots((prev) => prev.filter((bot) => bot.id !== chatbotId));
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to delete chatbot');
      }
    } catch (error) {
      console.error('Error deleting chatbot:', error);
      alert(`❌ Error: ${error.message}`);
    } finally {
      setDeleting(null);
    }
  };

  const handleUpdateChatbot = async (bot, e) => {
    e.stopPropagation();

    const nextName = window.prompt('Enter new chatbot name:', bot.name);
    if (!nextName || nextName.trim() === '' || nextName.trim() === bot.name) {
      return;
    }

    try {
      const token = getStoredToken();
      if (!token) {
        alert('Error: Not authenticated');
        return;
      }

      const response = await fetchWithPortFallback(`/api/chatbots/${bot.id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ name: nextName.trim() }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to update chatbot');
      }

      const updated = await response.json();
      setChatbots((prev) =>
        prev.map((item) =>
          item.id === bot.id
            ? {
                ...item,
                name: updated.name,
                llm_model: updated.llm_model,
                system_prompt: updated.system_prompt,
                voice_id: updated.voice_id,
                temperature: updated.temperature,
                max_tokens: updated.max_tokens,
              }
            : item
        )
      );
      alert('✅ Chatbot updated successfully!');
    } catch (error) {
      console.error('Error updating chatbot:', error);
      alert(`❌ Error: ${error.message}`);
    }
  };

  const fetchChatbots = async () => {
    try {
      setLoading(true);
      const token = getStoredToken();
      
      if (!token) {
        console.log('No token found, showing demo data');
        setLoading(false);
        return;
      }

      const response = await fetchWithPortFallback('/api/chatbots/', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        console.log('✅ Fetched chatbots from backend:', data);
        
        // Transform data if needed
        const transformedData = data.map((bot) => ({
          id: bot.id,
          name: bot.name,
          status: bot.status || 'Online',
          llm_model: bot.llm_model,
          system_prompt: bot.system_prompt,
          voice_id: bot.voice_id,
          temperature: bot.temperature,
          max_tokens: bot.max_tokens,
          created_at: bot.created_at,
          language: 'Multilingual',
          totalChats: '0',
          dailyUsage: 45,
          icon: 'smart_toy',
          color: 'primary',
        }));
        
        setChatbots(transformedData);
      }
    } catch (error) {
      console.error('Error fetching chatbots:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchChatbots();
  }, []);

  return (
    <div className="pb-24 md:pb-0">
      {/* Header Section */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-10">
        <div>
          <h1 className="text-4xl font-extrabold font-headline tracking-tight text-on-background mb-2">
            Chatbot Management
          </h1>
          <p className="text-on-surface-variant font-medium">
            Deploy, monitor, and optimize your intelligent agents.
          </p>
        </div>
        <button
          onClick={onCreateNew}
          className="flex items-center gap-2 bg-primary-container text-on-primary-container px-8 py-4 rounded-full font-label font-bold shadow-lg shadow-primary-container/20 hover:scale-[1.02] active:scale-95 transition-all"
        >
          <span className="material-symbols-outlined">add</span>
          Create New Chatbot
        </button>
      </div>

      {/* Dashboard Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {loading && chatbots.length === 0 && (
          <div className="col-span-full text-center py-12">
            <p className="text-on-surface-variant">Loading chatbots...</p>
          </div>
        )}
        {!loading && chatbots.length === 0 && (
          <div className="col-span-full text-center py-12">
            <p className="text-on-surface-variant mb-4">No chatbots yet. Create your first one!</p>
            <button
              onClick={onCreateNew}
              className="inline-flex items-center gap-2 bg-primary-container text-on-primary-container px-6 py-3 rounded-full font-label font-bold hover:scale-[1.02] transition-all"
            >
              <span className="material-symbols-outlined">add</span>
              Create First Chatbot
            </button>
          </div>
        )}
        {chatbots.map((bot, idx) => {
          const isOffline = bot.status === 'Offline';
          const isCyan = bot.color === 'cyan';

          return (
            <div
              key={bot.id}
              onClick={() => setSelectedChatbot(bot)}
              className={`glass-card p-6 rounded-lg border shadow-xl transition-all group cursor-pointer ${
                isCyan
                  ? 'bg-white/40 border-cyan-100/50 shadow-cyan-100/30 hover:scale-[1.01]'
                  : 'bg-white/40 border-white/40 hover:shadow-2xl'
              }`}
            >
              {/* Card Header */}
              <div className="flex justify-between items-start mb-6">
                <div className="flex items-center gap-4">
                  <div
                    className={`w-14 h-14 rounded-full flex items-center justify-center ${
                      isOffline
                        ? 'bg-slate-100 text-slate-400'
                        : isCyan
                          ? 'bg-cyan-500 text-white shadow-lg shadow-cyan-500/30'
                          : `bg-${bot.color}-container/20 text-${bot.color}`
                    }`}
                  >
                    <span className="material-symbols-outlined text-3xl">{bot.icon}</span>
                  </div>
                  <div>
                    <h3 className="font-headline font-bold text-lg text-on-background">
                      {bot.name}
                    </h3>
                    <div className="flex items-center gap-1.5 mt-0.5">
                      <span
                        className={`w-2 h-2 rounded-full ${
                          isOffline ? 'bg-slate-300' : 'bg-primary animate-pulse'
                        }`}
                      />
                      <span
                        className={`text-xs font-label font-semibold uppercase tracking-wider ${
                          isOffline ? 'text-slate-400' : 'text-primary'
                        }`}
                      >
                        {bot.status}
                      </span>
                    </div>
                  </div>
                </div>
                <button className="material-symbols-outlined text-outline hover:text-primary transition-colors">
                  more_vert
                </button>
              </div>

              {/* Card Content */}
              <div className="space-y-4">
                {/* Model Info */}
                <div className="flex items-center justify-between p-3 bg-surface-container-low rounded-lg">
                  <div className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-secondary text-sm">
                      model_training
                    </span>
                    <span className="text-sm font-label text-on-surface-variant">Model</span>
                  </div>
                  <span className="text-sm font-bold font-headline text-on-surface">{bot.llm_model || bot.model}</span>
                </div>

                {/* Language & Chats */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 bg-surface-container-low rounded-lg">
                    <span className="text-[10px] uppercase tracking-widest text-outline font-bold block mb-1">
                      Language
                    </span>
                    <div className="flex items-center gap-1.5">
                      <span className="material-symbols-outlined text-xs text-tertiary">
                        {bot.language.includes('Multilingual') ? 'language' : 'translate'}
                      </span>
                      <span className="text-sm font-bold">{bot.language}</span>
                    </div>
                  </div>
                  <div className="p-3 bg-surface-container-low rounded-lg">
                    <span className="text-[10px] uppercase tracking-widest text-outline font-bold block mb-1">
                      Total Chats
                    </span>
                    <div className="flex items-center gap-1.5">
                      <span className="material-symbols-outlined text-xs text-secondary">
                        forum
                      </span>
                      <span className="text-sm font-bold">{bot.totalChats}</span>
                    </div>
                  </div>
                </div>

                {/* Usage Bar */}
                <div className={`pt-2 ${isOffline ? 'opacity-50' : ''}`}>
                  <div className="flex justify-between text-xs font-bold mb-1.5">
                    <span className="text-on-surface-variant">Daily Usage</span>
                    <span className={isOffline ? 'text-slate-400' : 'text-primary'}>
                      {bot.dailyUsage}%
                    </span>
                  </div>
                  <div className="w-full h-2 bg-surface-container-highest rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary-container rounded-full transition-all"
                      style={{ width: `${bot.dailyUsage}%` }}
                    />
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="mt-6 pt-4 border-t border-slate-100 flex gap-2">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedChatbot(bot);
                  }}
                  className="flex-1 py-2 rounded-full bg-secondary text-white text-sm font-bold font-label hover:brightness-110 active:scale-95 transition-colors flex items-center justify-center gap-1"
                >
                  <span className="material-symbols-outlined text-sm">chat</span>
                  Chat
                </button>
                <button
                  onClick={(e) => handleUpdateChatbot(bot, e)}
                  className="px-4 py-2 rounded-full border border-blue-300 text-blue-600 hover:bg-blue-50 active:scale-95 text-sm font-bold font-label transition-colors"
                  title="Update chatbot"
                >
                  <span className="material-symbols-outlined text-sm">edit</span>
                </button>
                <button
                  onClick={(e) => handleDeleteChatbot(bot.id, bot.name, e)}
                  disabled={deleting === bot.id}
                  className={`px-4 py-2 rounded-full text-sm font-bold font-label transition-colors ${
                    deleting === bot.id
                      ? 'bg-slate-300 text-slate-500 cursor-wait'
                      : 'border border-red-300 text-red-600 hover:bg-red-50 active:scale-95'
                  }`}
                  title="Delete this chatbot"
                >
                  <span className="material-symbols-outlined text-sm">delete</span>
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Ecosystem Health */}
      <div className="glass-card p-8 rounded-lg border border-white/50 shadow-lg bg-white/40 backdrop-blur-md flex flex-col md:flex-row items-center gap-8 overflow-hidden relative">
        <div className="absolute -right-20 -top-20 w-64 h-64 bg-cyan-100/30 rounded-full blur-3xl" />
        <div className="absolute -left-20 -bottom-20 w-64 h-64 bg-primary-container/20 rounded-full blur-3xl" />

        <div className="flex-1 relative z-10 text-center md:text-left">
          <h2 className="text-2xl font-extrabold font-headline mb-4">Ecosystem Health</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {[
              { label: 'Total Active', value: '12', subValue: '/ 15' },
              { label: 'Avg Response', value: '1.2s', subValue: '' },
              { label: 'Success Rate', value: '98.4%', subValue: '' },
              { label: 'API Tokens', value: '2.4M', subValue: '' },
            ].map((stat, idx) => (
              <div key={idx}>
                <p className="text-[11px] font-bold text-outline uppercase tracking-widest mb-1">
                  {stat.label}
                </p>
                <p className="text-3xl font-headline font-extrabold text-on-background">
                  {stat.value}
                  {stat.subValue && <span className="text-sm font-medium text-primary"> {stat.subValue}</span>}
                </p>
              </div>
            ))}
          </div>
        </div>

        <div className="relative z-10 w-full md:w-auto">
          <button className="w-full md:w-auto px-8 py-4 bg-on-background text-white rounded-full font-label font-bold flex items-center justify-center gap-2 hover:bg-slate-800 transition-all">
            <span className="material-symbols-outlined">analytics</span>
            Detailed Usage Report
          </button>
        </div>
      </div>

      {/* Chat Window Modal */}
      {selectedChatbot && (
        <ChatWindow
          chatbot={selectedChatbot}
          onBack={() => setSelectedChatbot(null)}
        />
      )}
    </div>
  );
});

export default ChatbotsPage;
