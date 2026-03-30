// Chat Window Component - Full chat interface for a specific chatbot
import React, { useState, useEffect, useRef, useCallback } from 'react';
import MessageBubble from '../components/MessageBubble';
import { ttsService } from '../utils/ttsService';
import { sttAPI, ttsAPI } from '../services/api';

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

const ChatWindow = ({ chatbot, onBack }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioStreamRef = useRef(null);
  const audioChunksRef = useRef([]);
  const sessionId = `chatbot_${chatbot?.id || 'default'}`;
  const isMicSupported =
    typeof window !== 'undefined' &&
    !!window.MediaRecorder &&
    !!navigator.mediaDevices?.getUserMedia;

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchChatHistory = useCallback(async () => {
    try {
      setLoading(true);
      const token = getStoredToken();
      
      const response = await fetchWithPortFallback(
        `/api/chat-history/session/${sessionId}`,
        {
          headers: token
            ? {
                Authorization: `Bearer ${token}`,
              }
            : {},
        }
      );

      if (response.ok) {
        const data = await response.json();
        setMessages(data.messages || []);
        setError(null);
      }
    } catch (err) {
      console.error('Error fetching chat history:', err);
      // Don't show error for first-time chat (no history)
      setMessages([]);
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  // Load chat history
  useEffect(() => {
    fetchChatHistory();
  }, [fetchChatHistory]);

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const resolveRealtimeVoice = () => {
    const voiceId = (chatbot.voice_id || '').toLowerCase();
    if (voiceId.includes('guy') || voiceId.includes('male')) {
      return 'onyx';
    }
    return 'nova';
  };

  const playAssistantAudio = async (text) => {
    if (!text?.trim()) return;

    try {
      const ttsResponse = await ttsAPI.synthesize(text, resolveRealtimeVoice(), 1.0);
      const audioBlob = ttsResponse?.data instanceof Blob
        ? ttsResponse.data
        : new Blob([ttsResponse?.data], { type: 'audio/mpeg' });
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      audio.onended = () => URL.revokeObjectURL(audioUrl);
      audio.onerror = () => URL.revokeObjectURL(audioUrl);
      await audio.play();
    } catch (ttsErr) {
      console.error('Backend TTS error, falling back to browser speech:', ttsErr);
      await ttsService.speak(text).catch((fallbackErr) => {
        console.error('Browser TTS fallback failed:', fallbackErr);
      });
    }
  };

  const submitMessage = async (userMessage, fromVoice = false) => {
    if (!userMessage?.trim() || sending) return;

    setSending(true);
    setError(null);

    const newUserMessage = {
      id: `user_${Date.now()}`,
      role: 'user',
      content: userMessage,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, newUserMessage]);

    try {
      const token = getStoredToken();

      if (!token) {
        throw new Error('Not authenticated');
      }

      const response = await fetchWithPortFallback('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          message: userMessage,
          session_id: sessionId,
          model: chatbot.llm_model || 'gpt-4o-mini',
          temperature: chatbot.temperature || 0.7,
          stream: false,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to send message');
      }

      const data = await response.json();
      const assistantText = data.message || data.content || data.response || 'No response received';

      const aiMessage = {
        id: `ai_${Date.now()}`,
        role: 'assistant',
        content: assistantText,
        tokens: data.tokens_used || data.usage?.total_tokens || 0,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, aiMessage]);

      if (fromVoice || chatbot.voice_id) {
        setTimeout(() => {
          playAssistantAudio(aiMessage.content).catch((err) => console.error('TTS Error:', err));
        }, 300);
      }
    } catch (err) {
      console.error('Error sending message:', err);
      const isConnectionError = err?.message === 'Failed to fetch';
      const message = isConnectionError
        ? `Cannot reach backend at ${API_BASE_URL}. Please start backend server.`
        : err.message || 'Failed to send message';
      setError(message);

      setMessages((prev) => prev.filter((m) => m.id !== newUserMessage.id));
    } finally {
      setSending(false);
    }
  };

  const stopMicTracks = () => {
    if (audioStreamRef.current) {
      audioStreamRef.current.getTracks().forEach((track) => track.stop());
      audioStreamRef.current = null;
    }
  };

  const transcribeAndSend = async (audioBlob) => {
    try {
      setIsTranscribing(true);
      setError(null);

      const sttResponse = await sttAPI.transcribe(audioBlob);
      const transcript = sttResponse?.data?.text?.trim();

      if (!transcript) {
        throw new Error('No speech detected. Please speak clearly and try again.');
      }

      await submitMessage(transcript, true);
    } catch (sttErr) {
      console.error('STT error:', sttErr);
      const message = sttErr?.response?.data?.detail || sttErr?.message || 'Speech-to-text failed.';
      setError(message);
    } finally {
      setIsTranscribing(false);
    }
  };

  const startVoiceCapture = async () => {
    if (isRecording || isTranscribing) return;

    try {
      setError(null);
      if (!isMicSupported) {
        throw new Error('Microphone recording is not supported in this browser.');
      }

      audioStreamRef.current = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });

      audioChunksRef.current = [];

      const preferredMimeType =
        window.MediaRecorder?.isTypeSupported?.('audio/webm;codecs=opus')
          ? 'audio/webm;codecs=opus'
          : window.MediaRecorder?.isTypeSupported?.('audio/webm')
          ? 'audio/webm'
          : '';

      mediaRecorderRef.current = preferredMimeType
        ? new MediaRecorder(audioStreamRef.current, { mimeType: preferredMimeType })
        : new MediaRecorder(audioStreamRef.current);
      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: preferredMimeType || 'audio/webm' });
        stopMicTracks();
        if (audioBlob.size > 0) {
          await transcribeAndSend(audioBlob);
        }
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (micErr) {
      console.error('Microphone access error:', micErr);
      stopMicTracks();
      setError('Microphone permission denied or unavailable. Please allow mic access and try again.');
    }
  };

  const stopVoiceCapture = () => {
    if (!isRecording) return;

    try {
      mediaRecorderRef.current?.stop();
    } finally {
      setIsRecording(false);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    const userMessage = input.trim();
    if (!userMessage) return;
    setInput('');
    await submitMessage(userMessage, false);
  };

  useEffect(() => {
    return () => {
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.stop();
      }
      stopMicTracks();
    };
  }, []);

  if (!chatbot) {
    return null;
  }

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div className="bg-white/90 backdrop-blur-md rounded-xl shadow-2xl w-full max-w-2xl h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-white/20">
          <div className="flex items-center gap-4">
            <button
              onClick={onBack}
              className="p-2 hover:bg-slate-200 rounded-full transition-colors"
              title="Go back"
            >
              <span className="material-symbols-outlined">arrow_back</span>
            </button>
            <div>
              <h2 className="text-xl font-bold text-on-background">{chatbot.name}</h2>
              <p className="text-xs text-on-surface-variant">
                Model: {chatbot.llm_model || 'Unknown'}
              </p>
            </div>
          </div>

          {/* Voice indicator */}
          {chatbot.voice_id && (
            <div className="flex items-center gap-2 px-3 py-1.5 bg-secondary/10 rounded-full">
              <span className="material-symbols-outlined text-sm text-secondary">
                record_voice_over
              </span>
              <span className="text-xs font-semibold text-secondary">
                {chatbot.voice_id.includes('Guy') ? 'Male' : 'Female'}
              </span>
            </div>
          )}
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 && !loading && (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <span className="material-symbols-outlined text-6xl text-outline/20 mb-4">
                chat
              </span>
              <p className="text-on-surface-variant">
                Start chatting with {chatbot.name}
              </p>
            </div>
          )}

          {loading && messages.length === 0 && (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <div className="inline-block">
                  <div className="w-8 h-8 border-4 border-secondary border-t-transparent rounded-full animate-spin" />
                </div>
                <p className="text-on-surface-variant mt-4">Loading chat history...</p>
              </div>
            </div>
          )}

          {messages.map((message) => (
            <MessageBubble
              key={message.id}
              message={message}
              isUser={message.role === 'user'}
            />
          ))}

          {sending && (
            <div className="flex gap-4 mb-4 justify-start">
              <div className="max-w-[70%] rounded-lg p-4 bg-surface-container text-on-surface rounded-bl-none shadow-md">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-on-surface rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-on-surface rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                  <div className="w-2 h-2 bg-on-surface rounded-full animate-bounce" style={{ animationDelay: '0.4s' }} />
                </div>
              </div>
            </div>
          )}

          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
              <p className="font-semibold">Error</p>
              <p className="text-sm">{error}</p>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t border-white/20 p-4 bg-white/50">
          <form onSubmit={sendMessage} className="flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={sending || isTranscribing}
              placeholder="Type your message..."
              className="flex-1 px-4 py-3 rounded-full border border-outline-variant focus:ring-2 focus:ring-secondary focus:border-secondary bg-white transition-all disabled:opacity-50"
            />
            <button
              type="button"
              onClick={isRecording ? stopVoiceCapture : startVoiceCapture}
              disabled={isTranscribing || sending || !isMicSupported}
              title={!isMicSupported ? 'Mic not supported in this browser' : isRecording ? 'Stop mic' : 'Start mic'}
              className={`w-12 h-12 rounded-full transition-all flex items-center justify-center ${
                isRecording
                  ? 'bg-red-600 text-white hover:bg-red-700'
                  : 'bg-sky-600 text-white hover:bg-sky-700'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              <span className="material-symbols-outlined text-base">
                {isRecording ? 'stop_circle' : 'mic'}
              </span>
            </button>
            <button
              type="submit"
              disabled={!input.trim() || sending || isTranscribing}
              className="px-6 py-3 bg-secondary text-white rounded-full font-semibold hover:brightness-110 active:scale-95 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <span className="material-symbols-outlined text-sm">
                {sending ? 'schedule' : 'send'}
              </span>
              {sending ? 'Sending' : 'Send'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ChatWindow;
