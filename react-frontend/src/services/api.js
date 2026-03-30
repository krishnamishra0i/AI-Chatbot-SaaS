// API service layer for Athena AI backend
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';
const WS_BASE_URL = API_BASE_URL.replace('http', 'ws');
const ALTERNATE_API_BASE_URL = API_BASE_URL.includes(':5000')
  ? API_BASE_URL.replace(':5000', ':5001')
  : API_BASE_URL.includes(':5001')
  ? API_BASE_URL.replace(':5001', ':5000')
  : null;

// Create axios instance with auth interceptor
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

const getStoredToken = () =>
  localStorage.getItem('athena_token') ||
  localStorage.getItem('token') ||
  localStorage.getItem('accessToken');

const buildAuthHeaders = () => {
  const token = getStoredToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
};

const requestWithPortFallback = async ({ method, url, data, config = {} }) => {
  try {
    return await api.request({ method, url, data, ...config });
  } catch (error) {
    const isNetworkOrCors = !error.response || error.type === 'CORS_ERROR';
    if (!isNetworkOrCors || !ALTERNATE_API_BASE_URL) {
      throw error;
    }

    console.warn('[API] Retrying request with alternate backend:', {
      primary: API_BASE_URL,
      fallback: ALTERNATE_API_BASE_URL,
      url,
      method,
    });

    return axios.request({
      baseURL: ALTERNATE_API_BASE_URL,
      method,
      url,
      data,
      ...config,
      headers: {
        'Content-Type': 'application/json',
        ...buildAuthHeaders(),
        ...(config.headers || {}),
      },
    });
  }
};

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = getStoredToken();
  const isPublicAuthRoute =
    config.url?.includes('/api/auth/otp/send') ||
    config.url?.includes('/api/auth/otp/verify') ||
    config.url?.includes('/api/auth/send-otp') ||
    config.url?.includes('/api/auth/verify-otp');
  
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
    if (!isPublicAuthRoute) {
      console.warn('[API] ⚠️ NO TOKEN FOUND - Request will be sent without Authorization header');
    }
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
    if (response.data && (response.data.access_token || response.data.token)) {
      const authToken = response.data.access_token || response.data.token;
      console.log('[API] Token found in response - storing in localStorage');
      localStorage.setItem('athena_token', authToken);
      localStorage.setItem('token', authToken);
      localStorage.setItem('accessToken', authToken);
      if (response.data.user) {
        localStorage.setItem('athena_user', JSON.stringify(response.data.user));
        console.log('[API] ✓ Token and user stored from OTP response');
      }
    }
    return response;
  },
  (error) => {
    // Handle CORS errors
    if (!error.response) {
      console.error('[API] ❌ Network/CORS Error:', {
        message: error.message,
        code: error.code,
        url: error.config?.url,
        hint: 'Check backend CORS config allows your frontend origin'
      });
      return Promise.reject({
        type: 'CORS_ERROR',
        message: 'Network error - Backend may have CORS restrictions',
        original: error
      });
    }

    if (error.response?.status === 401) {
      console.error('[API] 401 Unauthorized - Clearing auth and logging out');
      console.error('[API] Response:', error.response?.data);
      localStorage.removeItem('athena_token');
      localStorage.removeItem('athena_user');
      window.dispatchEvent(new Event('auth:logout'));
    }
    
    if (error.response?.status === 400) {
      console.warn('[API] 400 Bad Request:', error.response?.data);
    }

    return Promise.reject(error);
  }
);

// ── Auth ───────────────────────────────────────────────
// Passwordless OTP-only authentication (no passwords needed)

export const authAPI = {
  // Step 1: Send OTP to email
  sendOtp: (email) =>
    requestWithPortFallback({ method: 'post', url: '/api/auth/otp/send', data: { email } }),

  // Step 2: Verify OTP and login
  verifyOtp: (email, otp_code) =>
    requestWithPortFallback({ method: 'post', url: '/api/auth/otp/verify', data: { email, otp_code } }),

  // Aliases for compatibility
  sendLoginOTP: (email) =>
    requestWithPortFallback({ method: 'post', url: '/api/auth/otp/send', data: { email } }),

  verifyLoginOTP: (email, otp) =>
    requestWithPortFallback({ method: 'post', url: '/api/auth/otp/verify', data: { email, otp_code: otp } }),

  resendOTP: (email) =>
    requestWithPortFallback({ method: 'post', url: '/api/auth/otp/send', data: { email } }),

  getMe: () => requestWithPortFallback({ method: 'get', url: '/api/auth/otp/me' }),

  updateMe: (data) => requestWithPortFallback({ method: 'patch', url: '/api/auth/me', data }),
};

// ── Chat ───────────────────────────────────────────────

export const chatAPI = {
  send: (message, options = {}) =>
    requestWithPortFallback({ method: 'post', url: '/api/chat', data: { message, ...options } }),

  sendStream: (message, options = {}) =>
    requestWithPortFallback({
      method: 'post',
      url: '/api/chat',
      data: { message, stream: true, ...options },
      config: {
        responseType: 'text',
        headers: { Accept: 'text/event-stream' },
      },
    }),

  // Dedicated streaming endpoint (sentence-level chunks for TTS)
  streamSentences: (message, options = {}) =>
    requestWithPortFallback({
      method: 'post',
      url: '/api/chat/stream',
      data: { message, ...options },
      config: {
        responseType: 'text',
        headers: { Accept: 'text/event-stream' },
      },
    }),

  completions: (messages, model = 'groq/llama-3.3-70b-versatile') =>
    requestWithPortFallback({ method: 'post', url: '/v1/chat/completions', data: { messages, model } }),
};

// ── Chatbots ───────────────────────────────────────────

export const chatbotsAPI = {
  list: () => requestWithPortFallback({ method: 'get', url: '/api/chatbots/' }),
  create: (data) => requestWithPortFallback({ method: 'post', url: '/api/chatbots/', data }),
  get: (id) => requestWithPortFallback({ method: 'get', url: `/api/chatbots/${id}` }),
  update: (id, data) => requestWithPortFallback({ method: 'patch', url: `/api/chatbots/${id}`, data }),
  delete: (id) => requestWithPortFallback({ method: 'delete', url: `/api/chatbots/${id}` }),
};

// ── API Keys ───────────────────────────────────────────

export const apiKeysAPI = {
  list: () => requestWithPortFallback({ method: 'get', url: '/api/keys/' }),
  create: (name = 'Default Key') => requestWithPortFallback({ method: 'post', url: '/api/keys/', data: { name } }),
  revoke: (id) => requestWithPortFallback({ method: 'delete', url: `/api/keys/${id}` }),
};

// ── TTS ────────────────────────────────────────────────

export const ttsAPI = {
  // Real-time streaming TTS (preferred)
  synthesize: (text, voice = 'nova', speed = 1.0, pitch = 0) =>
    requestWithPortFallback({
      method: 'post',
      url: '/api/tts/realtime/stream',
      data: { text, voice, speed },
      config: { responseType: 'blob' },
    }),

  // Base64 variant for pre-buffering
  synthesizeBase64: (text, voice = 'nova', speed = 1.0, pitch = 0) =>
    requestWithPortFallback({ method: 'post', url: '/api/tts/realtime/base64', data: { text, voice, speed } }),

  voices: (locale = 'en') => requestWithPortFallback({ method: 'get', url: `/api/tts/voices?locale=${locale}` }),

  voiceCategories: () => requestWithPortFallback({ method: 'get', url: '/api/tts/voices/categories' }),

  // Deprecated: use synthesize() instead
  stream: (text, voice, speed, pitch) =>
    requestWithPortFallback({
      method: 'post',
      url: '/api/tts/realtime/stream',
      data: { text, voice, speed, pitch },
      config: { responseType: 'blob' },
    }),
};

// ── STT ────────────────────────────────────────────────

export const sttAPI = {
  transcribe: (audioBlob) => {
    const formData = new FormData();
    const isWebm = audioBlob?.type?.includes('webm');
    formData.append('file', audioBlob, isWebm ? 'recording.webm' : 'recording.wav');
    return requestWithPortFallback({
      method: 'post',
      url: '/api/stt',
      data: formData,
      config: { headers: { 'Content-Type': 'multipart/form-data' } },
    });
  },

  transcribeBase64: (audioBase64) =>
    requestWithPortFallback({ method: 'post', url: '/api/stt/base64', data: { audio: audioBase64 } }),
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
  summary: (days = 30) => requestWithPortFallback({ method: 'get', url: `/api/usage/summary?days=${days}` }),
  breakdown: (days = 30) => requestWithPortFallback({ method: 'get', url: `/api/usage/breakdown?days=${days}` }),
};

// ── Models ─────────────────────────────────────────────

export const modelsAPI = {
  list: () => requestWithPortFallback({ method: 'get', url: '/v1/models' }),
  providers: () => requestWithPortFallback({ method: 'get', url: '/api/providers' }),
  prompts: () => requestWithPortFallback({ method: 'get', url: '/api/prompts' }),
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
