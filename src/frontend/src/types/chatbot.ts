// src/types/chatbot.ts
export interface Message {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
  audioUrl?: string;
  sources?: string[];  // Where the answer came from
  usedKnowledgeBase?: boolean;  // Whether knowledge base was used
}

export interface ChatbotConfig {
  apiBaseUrl: string;
  botName: string;
  avatarImage?: string;
  position?: {
    bottom: string;
    right: string;
  };
}

export interface TTSRequest {
  text: string;
  language?: string;
  voice?: string;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
  use_knowledge_base?: boolean;
}

export interface ChatResponse {
  response: string;
  success?: boolean;
  used_knowledge_base?: boolean;
  sources?: string[];
}

export interface RecordingState {
  isRecording: boolean;
  duration: number;
  audioBlob?: Blob;
}

export enum AudioMode {
  AUTO = 'auto',
  MANUAL = 'manual',
}
