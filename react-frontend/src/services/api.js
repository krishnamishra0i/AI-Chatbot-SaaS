// API service layer for Athena AI backend
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
const WS_BASE_URL = API_BASE_URL.replace('http', 'ws');

// Create axios instance with auth interceptor
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('athena_token');
  
  // DEBUG: Log token attachment
  console.log('[API] Token from localStorage:', token ? `${token.substring(0, 20)}...` : 'NOT FOUND');
  console.log('[API] Request config:', {
    url: config.url,
    method: config.method,
    hasToken: !!token,
    hasAuthHeader: !!config.headers.Authorization
  });
  
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
    console.log('[API] Authorization header set:', `Bearer ${token.substring(0, 20)}...`);
  } else {
    console.warn('[API] ⚠️ NO TOKEN FOUND - Request will be sent without Authorization header');
  }
  
  return config;
}, (error) => {
  console.error('[API] Request interceptor error:', error);
  return Promise.reject(error);
});

// Handle responses and auto-store tokens from OTP endpoints
api.interceptors.response.use(
  (response) => {
    // Auto-store token if present in response (from OTP endpoints)
    if (response.data && response.data.access_token) {
      console.log('[API] Token found in response - storing in localStorage');
      localStorage.setItem('athena_token', response.data.access_token);
      if (response.data.user) {
        localStorage.setItem('athena_user', JSON.stringify(response.data.user));
        console.log('[API] ✓ Token and user stored from OTP response');
      }
    }
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      console.error('[API] 401 Unauthorized - Clearing auth and logging out');
      console.error('[API] Response:', error.response?.data);
      localStorage.removeItem('athena_token');
      localStorage.removeItem('athena_user');
      window.dispatchEvent(new Event('auth:logout'));
    }
    return Promise.reject(error);
  }
);

// ── Auth ───────────────────────────────────────────────
// Passwordless OTP-only authentication (no passwords needed)

export const authAPI = {
  // Step 1: Send OTP to email
  sendOtp: (email) =>
    api.post('/api/auth/otp/send', { email }),

  // Step 2: Verify OTP and login
  verifyOtp: (email, otp_code) =>
    api.post('/api/auth/otp/verify', { email, otp_code }),

  // Aliases for compatibility
  sendLoginOTP: (email) =>
    api.post('/api/auth/otp/send', { email }),

  verifyLoginOTP: (email, otp) =>
    api.post('/api/auth/otp/verify', { email, otp_code: otp }),

  resendOTP: (email) =>
    api.post('/api/auth/otp/send', { email }),

  getMe: () => api.get('/api/auth/otp/me'),

  updateMe: (data) => api.patch('/api/auth/me', data),
};

// ── Chat ───────────────────────────────────────────────

export const chatAPI = {
  send: (message, options = {}) =>
    api.post('/api/chat', { message, ...options }),

  sendStream: (message, options = {}) =>
    api.post('/api/chat', { message, stream: true, ...options }, {
      responseType: 'text',
      headers: { Accept: 'text/event-stream' },
    }),

  // Dedicated streaming endpoint (sentence-level chunks for TTS)
  streamSentences: (message, options = {}) =>
    api.post('/api/chat/stream', { message, ...options }, {
      responseType: 'text',
      headers: { Accept: 'text/event-stream' },
    }),

  completions: (messages, model = 'groq/llama-3.3-70b-versatile') =>
    api.post('/v1/chat/completions', { messages, model }),
};

// ── Chatbots ───────────────────────────────────────────

export const chatbotsAPI = {
  list: () => api.get('/api/chatbots/'),
  create: (data) => api.post('/api/chatbots/', data),
  get: (id) => api.get(`/api/chatbots/${id}`),
  update: (id, data) => api.patch(`/api/chatbots/${id}`, data),
  delete: (id) => api.delete(`/api/chatbots/${id}`),
};

// ── API Keys ───────────────────────────────────────────

export const apiKeysAPI = {
  list: () => api.get('/api/keys/'),
  create: (name = 'Default Key') => api.post('/api/keys/', { name }),
  revoke: (id) => api.delete(`/api/keys/${id}`),
};

// ── TTS ────────────────────────────────────────────────

export const ttsAPI = {
  // Real-time streaming TTS (preferred)
  synthesize: (text, voice = 'nova', speed = 1.0, pitch = 0) =>
    api.post('/api/tts/realtime/stream', { text, voice, speed }, { responseType: 'blob' }),

  // Base64 variant for pre-buffering
  synthesizeBase64: (text, voice = 'nova', speed = 1.0, pitch = 0) =>
    api.post('/api/tts/realtime/base64', { text, voice, speed }),

  voices: (locale = 'en') => api.get(`/api/tts/voices?locale=${locale}`),

  voiceCategories: () => api.get('/api/tts/voices/categories'),

  // Deprecated: use synthesize() instead
  stream: (text, voice, speed, pitch) =>
    api.post('/api/tts/realtime/stream', { text, voice, speed, pitch }, { responseType: 'blob' }),
};

// ── STT ────────────────────────────────────────────────

export const sttAPI = {
  transcribe: (audioBlob) => {
    const formData = new FormData();
    const isWebm = audioBlob?.type?.includes('webm');
    formData.append('file', audioBlob, isWebm ? 'recording.webm' : 'recording.wav');
    return api.post('/api/stt', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  transcribeBase64: (audioBase64) =>
    api.post('/api/stt/base64', { audio: audioBase64 }),
};

// ── Avatar ─────────────────────────────────────────────

export const avatarAPI = {
  list: () => api.get('/api/avatars'),
  get: (id) => api.get(`/api/avatars/${id}`),
  visemes: (text, avatarId = 'default') =>
    api.post('/api/avatar/visemes', { text, avatar_id: avatarId }),
};

// ── Usage ──────────────────────────────────────────────

export const usageAPI = {
  summary: (days = 30) => api.get(`/api/usage/summary?days=${days}`),
  breakdown: (days = 30) => api.get(`/api/usage/breakdown?days=${days}`),
};

// ── Models ─────────────────────────────────────────────

export const modelsAPI = {
  list: () => api.get('/v1/models'),
  providers: () => api.get('/api/providers'),
  prompts: () => api.get('/api/prompts'),
};

// -- Memory --

export const memoryAPI = {
  getSession: (sessionId) => api.get(`/api/memory/${sessionId}`),
  clearSession: (sessionId) => api.delete(`/api/memory/${sessionId}`),
  listSessions: () => api.get('/api/memory'),
};

// ── Health ─────────────────────────────────────────────

export const healthAPI = {
  check: () => api.get('/api/health'),
};

// ── WebSocket helpers ──────────────────────────────────

export class ChatWebSocket {
  constructor(onMessage, onError) {
    this.onMessage = onMessage;
    this.onError = onError || console.error;
    this.ws = null;
  }

  connect() {
    this.ws = new WebSocket(`${WS_BASE_URL}/ws/chat`);
    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.onMessage(data);
      } catch {
        this.onMessage({ type: 'raw', content: event.data });
      }
    };
    this.ws.onerror = (e) => this.onError(e);
    this.ws.onclose = () => console.log('Chat WebSocket closed');
    return new Promise((resolve, reject) => {
      this.ws.onopen = resolve;
      this.ws.onerror = reject;
    });
  }

  send(message, options = {}) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ message, stream: true, ...options }));
    }
  }

  close() {
    this.ws?.close();
  }
}

export class TTSWebSocket {
  constructor(onAudioChunk, onDone, onError) {
    this.onAudioChunk = onAudioChunk;
    this.onDone = onDone;
    this.onError = onError || console.error;
    this.ws = null;
  }

  connect() {
    this.ws = new WebSocket(`${WS_BASE_URL}/ws/tts`);
    this.ws.binaryType = 'arraybuffer';
    this.ws.onmessage = (event) => {
      if (event.data instanceof ArrayBuffer) {
        this.onAudioChunk(event.data);
      } else {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'done') this.onDone?.();
          if (data.type === 'error') this.onError?.(data.message);
        } catch { /* ignore */ }
      }
    };
    this.ws.onerror = (e) => this.onError(e);
    return new Promise((resolve, reject) => {
      this.ws.onopen = resolve;
      this.ws.onerror = reject;
    });
  }

  synthesize(text, voice = 'en-US-GuyNeural') {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ text, voice }));
    }
  }

  close() {
    this.ws?.close();
  }
}

export default api;
