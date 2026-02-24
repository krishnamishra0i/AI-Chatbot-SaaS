// src/hooks/useChatbot.ts
import { useState, useCallback, useRef } from 'react';
import { Message, ChatRequest, ChatResponse, AudioMode } from '../types/chatbot';

export const useChatbot = (apiBaseUrl: string) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSpeakerOn, setIsSpeakerOn] = useState(true);
  const [audioMode, setAudioMode] = useState<AudioMode>(AudioMode.AUTO);
  const [isRecording, setIsRecording] = useState(false);
  const [recordingDuration, setRecordingDuration] = useState(0);
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const recordingIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const audioRef = useRef<HTMLAudioElement>(new Audio());

  // Send message and get response
  const sendMessage = useCallback(
    async (text: string) => {
      if (!text.trim()) return;

      const userMessage: Message = {
        id: Date.now().toString(),
        content: text,
        isUser: true,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, userMessage]);
      setIsLoading(true);

      try {
        // Use direct RAG endpoint (works without LLM!)
        const response = await fetch(`${apiBaseUrl}/api/chat/direct`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: text,
            session_id: getSessionId(),
          } as ChatRequest),
        });

        if (!response.ok) throw new Error('Failed to send message');

        const data: ChatResponse = await response.json();
        const botMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: data.response || "I didn't understand that.",
          isUser: false,
          timestamp: new Date(),
          usedKnowledgeBase: data.used_knowledge_base,
          sources: data.sources || [],
        };

        setMessages(prev => [...prev, botMessage]);

        // Auto-play TTS if enabled
        if (audioMode === AudioMode.AUTO && isSpeakerOn) {
          playTTS(data.response);
        }
      } catch (error) {
        console.error('Chat error:', error);
        const errorMessage: Message = {
          id: (Date.now() + 2).toString(),
          content: 'Sorry, something went wrong. Please try again.',
          isUser: false,
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, errorMessage]);
      } finally {
        setIsLoading(false);
      }
    },
    [apiBaseUrl, audioMode, isSpeakerOn]
  );

  // Play TTS for text with male voice
  const playTTS = useCallback(
    async (text: string) => {
      if (!isSpeakerOn) return;

      try {
        setIsPlayingAudio(true);
        const response = await fetch(`${apiBaseUrl}/api/tts/synthesize-audio`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            text,
            voice: 'en-US-GuyNeural'  // Use male voice by default
          }),
        });

        if (!response.ok) throw new Error('TTS failed');

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        audioRef.current.src = url;

        audioRef.current.onended = () => {
          setIsPlayingAudio(false);
          URL.revokeObjectURL(url);
        };

        await audioRef.current.play();
      } catch (error) {
        console.error('TTS error:', error);
        setIsPlayingAudio(false);
      }
    },
    [apiBaseUrl, isSpeakerOn]
  );

  // Start recording audio
  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = event => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.start();
      mediaRecorderRef.current = mediaRecorder;
      setIsRecording(true);
      setRecordingDuration(0);

      recordingIntervalRef.current = setInterval(() => {
        setRecordingDuration(prev => prev + 1);
      }, 1000);
    } catch (error) {
      console.error('Recording error:', error);
    }
  }, []);

  // Stop recording and process
  const stopRecording = useCallback(async () => {
    return new Promise<void>((resolve, reject) => {
      if (!mediaRecorderRef.current) {
        reject(new Error('No active recording'));
        return;
      }

      mediaRecorderRef.current.onstop = async () => {
        setIsRecording(false);

        if (recordingIntervalRef.current) {
          clearInterval(recordingIntervalRef.current);
        }

        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        
        try {
          // Send to STT endpoint
          const formData = new FormData();
          formData.append('audio', audioBlob, 'recording.wav');

          const response = await fetch(`${apiBaseUrl}/api/stt/transcribe`, {
            method: 'POST',
            body: formData,
          });

          if (!response.ok) throw new Error('STT failed');

          const data = await response.json();
          if (data.text) {
            await sendMessage(data.text);
          }
          resolve();
        } catch (error) {
          console.error('STT error:', error);
          reject(error);
        }
      };

      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
    });
  }, [sendMessage, apiBaseUrl]);

  // Add message manually
  const addMessage = useCallback((text: string, isUser: boolean) => {
    const message: Message = {
      id: Date.now().toString(),
      content: text,
      isUser,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, message]);
  }, []);

  // Clear messages
  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  // Get or create session ID
  function getSessionId(): string {
    let sessionId = localStorage.getItem('chatbot-session-id');
    if (!sessionId) {
      sessionId = `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('chatbot-session-id', sessionId);
    }
    return sessionId;
  }

  return {
    messages,
    isLoading,
    isRecording,
    recordingDuration,
    isPlayingAudio,
    isSpeakerOn,
    audioMode,
    sendMessage,
    playTTS,
    startRecording,
    stopRecording,
    addMessage,
    clearMessages,
    setIsSpeakerOn,
    setAudioMode,
  };
};
