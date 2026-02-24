// src/hooks/useStreamingChatbot.ts
import { useState, useCallback, useRef, useEffect } from 'react';
import { Message, AudioMode } from '../types/chatbot';

interface StreamingMessage extends Message {
  isStreaming?: boolean;
  streamingContent?: string;
}

export const useStreamingChatbot = (apiBaseUrl: string) => {
  const [messages, setMessages] = useState<StreamingMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [isSpeakerOn, setIsSpeakerOn] = useState(true);
  const [audioMode, setAudioMode] = useState<AudioMode>(AudioMode.AUTO);
  const [isRecording, setIsRecording] = useState(false);
  const [recordingDuration, setRecordingDuration] = useState(0);
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const recordingIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const audioRef = useRef<HTMLAudioElement>(new Audio());
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationFrameRef = useRef<number>();
  const abortControllerRef = useRef<AbortController | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  // Initialize WebSocket connection
  useEffect(() => {
    const connectWebSocket = () => {
      const wsUrl = apiBaseUrl.replace('http', 'ws') + '/ws/chat';
      wsRef.current = new WebSocket(wsUrl);
      
      wsRef.current.onopen = () => {
        console.log('WebSocket connected for real-time chat');
      };

      wsRef.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'stream_start') {
          setIsTyping(true);
          setIsLoading(false);
        } else if (data.type === 'stream_token') {
          handleStreamingToken(data.messageId, data.token);
        } else if (data.type === 'stream_complete') {
          handleStreamingComplete(data.messageId, data.fullResponse, data.metadata);
        } else if (data.type === 'error') {
          handleStreamingError(data.error);
        }
      };

      wsRef.current.onclose = () => {
        console.log('WebSocket disconnected, attempting to reconnect...');
        setTimeout(connectWebSocket, 3000);
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    };

    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [apiBaseUrl]);

  // Handle streaming token
  const handleStreamingToken = useCallback((messageId: string, token: string) => {
    setMessages(prev => prev.map(msg => {
      if (msg.id === messageId) {
        const newContent = (msg.streamingContent || '') + token;
        return {
          ...msg,
          streamingContent: newContent,
          content: newContent,
          isStreaming: true
        };
      }
      return msg;
    }));
  }, []);

  // Handle streaming complete
  const handleStreamingComplete = useCallback((messageId: string, fullResponse: string, metadata?: any) => {
    setMessages(prev => prev.map(msg => {
      if (msg.id === messageId) {
        return {
          ...msg,
          content: fullResponse,
          isStreaming: false,
          streamingContent: undefined,
          usedKnowledgeBase: metadata?.used_knowledge_base,
          sources: metadata?.sources || []
        };
      }
      return msg;
    }));
    
    setIsTyping(false);

    // Auto-play TTS if enabled
    if (audioMode === AudioMode.AUTO && isSpeakerOn) {
      setTimeout(() => playTTS(fullResponse), 500);
    }
  }, [audioMode, isSpeakerOn]);

  // Handle streaming error
  const handleStreamingError = useCallback((_error: string) => {
    setIsTyping(false);
    setIsLoading(false);
    
    const errorMessage: StreamingMessage = {
      id: Date.now().toString(),
      content: 'Sorry, something went wrong. Please try again.',
      isUser: false,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, errorMessage]);
  }, []);

  // Send message with streaming support
  const sendMessage = useCallback(
    async (text: string) => {
      if (!text.trim()) return;

      const userMessage: StreamingMessage = {
        id: Date.now().toString(),
        content: text,
        isUser: true,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, userMessage]);
      setIsLoading(true);

      // Create bot message placeholder for streaming
      const botMessageId = (Date.now() + 1).toString();
      const botMessage: StreamingMessage = {
        id: botMessageId,
        content: '',
        isUser: false,
        timestamp: new Date(),
        isStreaming: true,
        streamingContent: ''
      };
      setMessages(prev => [...prev, botMessage]);

      try {
        // Try WebSocket first, fallback to HTTP streaming
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
          wsRef.current.send(JSON.stringify({
            type: 'chat_message',
            message: text,
            session_id: getSessionId(),
            message_id: botMessageId,
            use_knowledge_base: true
          }));
        } else {
          // Fallback to HTTP streaming
          await sendMessageHTTPStreaming(text, botMessageId);
        }
      } catch (error) {
        console.error('Chat error:', error);
        handleStreamingError('Failed to send message');
      }
    },
    [apiBaseUrl, audioMode, isSpeakerOn]
  );

  // HTTP Streaming fallback
  const sendMessageHTTPStreaming = useCallback(
    async (text: string, messageId: string) => {
      try {
        abortControllerRef.current = new AbortController();
        
        const response = await fetch(`${apiBaseUrl}/api/chat/stream`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: text,
            session_id: getSessionId(),
            use_knowledge_base: true,
          }),
          signal: abortControllerRef.current.signal,
        });

        if (!response.ok) throw new Error('Failed to send message');

        const reader = response.body?.getReader();
        if (!reader) throw new Error('No response body');

        setIsLoading(false);
        setIsTyping(true);

        let fullResponse = '';
        
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = new TextDecoder().decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6);
              if (data.trim() === '[DONE]') {
                handleStreamingComplete(messageId, fullResponse);
                return;
              }
              
              try {
                const parsed = JSON.parse(data);
                if (parsed.token) {
                  fullResponse += parsed.token;
                  handleStreamingToken(messageId, parsed.token);
                }
              } catch (e) {
                // Skip invalid JSON
              }
            }
          }
        }
      } catch (error) {
        if (error instanceof Error && error.name === 'AbortError') {
          return; // Request was cancelled
        }
        console.error('Streaming error:', error);
        handleStreamingError('Streaming failed');
      }
    },
    [apiBaseUrl, handleStreamingToken, handleStreamingComplete, handleStreamingError]
  );

  // Enhanced audio level detection
  const startAudioLevelDetection = useCallback((stream: MediaStream) => {
    try {
      audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
      analyserRef.current = audioContextRef.current.createAnalyser();
      
      const source = audioContextRef.current.createMediaStreamSource(stream);
      source.connect(analyserRef.current);
      
      analyserRef.current.fftSize = 256;
      const bufferLength = analyserRef.current.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);

      const updateAudioLevel = () => {
        if (!analyserRef.current || !isRecording) {
          setAudioLevel(0);
          return;
        }

        analyserRef.current.getByteFrequencyData(dataArray);
        const average = dataArray.reduce((sum, value) => sum + value, 0) / bufferLength;
        setAudioLevel(Math.min(average / 128, 1));
        
        animationFrameRef.current = requestAnimationFrame(updateAudioLevel);
      };

      updateAudioLevel();
    } catch (error) {
      console.error('Audio level detection error:', error);
    }
  }, [isRecording]);

  // Enhanced recording with audio visualization
  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      });
      
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
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

      // Start audio level detection
      startAudioLevelDetection(stream);

      recordingIntervalRef.current = setInterval(() => {
        setRecordingDuration(prev => prev + 1);
      }, 1000);
    } catch (error) {
      console.error('Recording error:', error);
    }
  }, [startAudioLevelDetection]);

  // Stop recording with enhanced processing
  const stopRecording = useCallback(async () => {
    return new Promise<void>((resolve, reject) => {
      if (!mediaRecorderRef.current) {
        reject(new Error('No active recording'));
        return;
      }

      mediaRecorderRef.current.onstop = async () => {
        setIsRecording(false);
        setAudioLevel(0);

        if (recordingIntervalRef.current) {
          clearInterval(recordingIntervalRef.current);
        }

        if (animationFrameRef.current) {
          cancelAnimationFrame(animationFrameRef.current);
        }

        if (audioContextRef.current) {
          audioContextRef.current.close();
        }

        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        
        try {
          const formData = new FormData();
          formData.append('audio', audioBlob, 'recording.webm');

          const response = await fetch(`${apiBaseUrl}/api/stt/transcribe`, {
            method: 'POST',
            body: formData,
          });

          if (!response.ok) throw new Error('STT failed');

          const data = await response.json();
          if (data.text && data.text.trim()) {
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

  // Enhanced TTS with better audio handling
  const playTTS = useCallback(
    async (text: string) => {
      if (!isSpeakerOn || !text.trim()) return;

      try {
        setIsPlayingAudio(true);
        const response = await fetch(`${apiBaseUrl}/api/tts/synthesize-audio`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            text,
            voice: 'en-US-GuyNeural',
            rate: '+0%',
            pitch: '+0Hz'
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

        audioRef.current.onerror = () => {
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

  // Stop current streaming
  const stopStreaming = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    setIsLoading(false);
    setIsTyping(false);
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
    isTyping,
    isRecording,
    recordingDuration,
    isPlayingAudio,
    isSpeakerOn,
    audioMode,
    audioLevel,
    sendMessage,
    playTTS,
    startRecording,
    stopRecording,
    stopStreaming,
    clearMessages,
    setIsSpeakerOn,
    setAudioMode,
  };
};