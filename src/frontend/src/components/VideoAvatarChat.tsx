import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Volume2, VolumeX, Send, Phone, MessageCircle, Bot, User, Minimize2, Maximize2 } from 'lucide-react';
import './VideoAvatarChat.css';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  hasAudio?: boolean;
  isStreaming?: boolean;
}

interface VideoAvatarChatProps {
  apiUrl?: string;
  avatarName?: string;
  avatarVideoUrl?: string;
  avatarImage?: string;
}

const VideoAvatarChat: React.FC<VideoAvatarChatProps> = ({
  apiUrl = 'http://localhost:8000',
  avatarName = 'Ambassador Paul',
  avatarVideoUrl,
  avatarImage = '/images/paulmichael.png'
}) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      text: `Hello! I'm ${avatarName}. I'm here to help you with any questions you have. You can type your message or use voice input. Let's start chatting!`,
      sender: 'bot',
      timestamp: new Date(),
      hasAudio: false
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [isVoiceMode, setIsVoiceMode] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const recognitionRef = useRef<any>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  useEffect(() => {
    // Initialize speech recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;

      recognitionRef.current.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setInputValue(transcript);
        handleSendMessage(transcript);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
    }

    // Add initial greeting
    setTimeout(() => {
      addBotMessage("Hi, I'm Paul. How can I help you today?");
    }, 500);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const addBotMessage = (text: string, hasAudio: boolean = false) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      text,
      sender: 'bot',
      timestamp: new Date(),
      hasAudio
    };
    setMessages(prev => [...prev, newMessage]);
    return newMessage.id;
  };

  const updateBotMessage = (id: string, text: string) => {
    setMessages(prev => prev.map(msg =>
      msg.id === id ? { ...msg, text } : msg
    ));
  };

  const handleSendMessage = async (messageText?: string) => {
    const text = messageText || inputValue.trim();
    if (!text || isStreaming) return;

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      text,
      sender: 'user',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setIsStreaming(true);

    try {
      // Create abort controller for this request
      abortControllerRef.current = new AbortController();

      // Create placeholder bot message
      const botMessageId = addBotMessage('');

      // Call streaming endpoint
      const response = await fetch(`${apiUrl}/api/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: text,
          use_knowledge_base: true,
          use_groq_enhancement: true
        }),
        signal: abortControllerRef.current.signal
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let fullResponse = '';

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));

                if (data.type === 'chunk' && data.content) {
                  fullResponse += data.content;
                  updateBotMessage(botMessageId, fullResponse);
                  scrollToBottom();
                } else if (data.type === 'done') {
                  fullResponse = data.full_response || fullResponse;
                  updateBotMessage(botMessageId, fullResponse);

                  // Play TTS audio
                  if (!isMuted && fullResponse) {
                    await playTTSAudio(fullResponse);
                  }
                } else if (data.type === 'error') {
                  throw new Error(data.message);
                }
              } catch (e) {
                // Ignore parse errors for incomplete chunks
              }
            }
          }
        }
      }

    } catch (error: any) {
      if (error.name === 'AbortError') {
        console.log('Request aborted');
      } else {
        console.error('Streaming error:', error);
        addBotMessage('Sorry, I encountered an error. Please try again.');
      }
    } finally {
      setIsLoading(false);
      setIsStreaming(false);
      abortControllerRef.current = null;
    }
  };

  const playTTSAudio = async (text: string) => {
    try {

      // Request TTS from backend
      const response = await fetch(`${apiUrl}/api/tts/synthesize-audio`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: text,
          language: 'en'
        })
      });

      if (response.ok) {
        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);

        const audio = new Audio(audioUrl);
        audio.onended = () => {
          URL.revokeObjectURL(audioUrl);
        };
        await audio.play();
      }
    } catch (error) {
      console.error('TTS error:', error);
    }
  };

  const handleVoiceInput = () => {
    if (recognitionRef.current) {
      if (isListening) {
        recognitionRef.current.stop();
      } else {
        recognitionRef.current.start();
        setIsListening(true);
      }
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const playAudio = (text: string) => {
    // Text-to-speech for bot messages
    if ('speechSynthesis' in window && !isMuted) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.9;
      utterance.pitch = 1;
      window.speechSynthesis.speak(utterance);
    }
  };

  return (
    <div className={`video-avatar-container ${isFullscreen ? 'fullscreen' : ''}`}>
      {/* Avatar Section */}
      <div className="avatar-section">
        <div className="avatar-placeholder">
          <div className="avatar-image-container">
            {avatarVideoUrl ? (
              <video
                ref={videoRef}
                className="avatar-video"
                src={avatarVideoUrl}
                autoPlay
                loop
                muted={isMuted}
              />
            ) : (
              <img src={avatarImage} alt={avatarName} className="avatar-image" />
            )}
          </div>
          {isListening && (
            <div className="avatar-pulse">
              🎙️
            </div>
          )}
        </div>
        <div className="avatar-controls">
          <button className="control-btn" onClick={() => setIsVoiceMode(!isVoiceMode)} title={isVoiceMode ? 'Text mode' : 'Voice mode'}>
            {isVoiceMode ? <MessageCircle size={20} /> : <Phone size={20} />}
          </button>
        </div>
      </div>

      {/* Chat Section */}
      <div className="chat-section">
        {/* Header */}
        <div className="chat-header">
          <div className="avatar-info">
            <img src={avatarImage} alt={avatarName} className="avatar-image-small" />
            <div>
              <h3 className="avatar-name">{avatarName}</h3>
              <p className="avatar-status">
                <span className="status-dot"></span>
                {isStreaming ? 'Streaming...' : 'Online • Ready to chat'}
              </p>
            </div>
          </div>
          <div className="chat-controls">
            <button className="control-btn" onClick={() => setIsMuted(!isMuted)} title={isMuted ? 'Unmute' : 'Mute'}>
              {isMuted ? <VolumeX size={20} /> : <Volume2 size={20} />}
            </button>
            <button className="control-btn" onClick={() => setIsFullscreen(!isFullscreen)} title={isFullscreen ? 'Exit fullscreen' : 'Fullscreen'}>
              {isFullscreen ? <Minimize2 size={20} /> : <Maximize2 size={20} />}
            </button>
          </div>
        </div>

        {/* Messages */}
        <div className="messages-container">
          {messages.map((message) => (
            <div key={message.id} className={`message ${message.sender}`}>
              <div className="message-avatar">
                {message.sender === 'bot' ? <Bot size={16} /> : <User size={16} />}
              </div>
              <div className="message-content">
                <p className="message-text">{message.text}</p>
                <span className="message-time">
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
              {message.hasAudio && !isMuted && (
                <button
                  className="audio-btn"
                  onClick={() => playAudio(message.text)}
                  title="Play audio"
                >
                  <Volume2 size={16} />
                </button>
              )}
            </div>
          ))}

          {isLoading && !isStreaming && (
            <div className="typing-indicator">
              <div className="typing-dot"></div>
              <div className="typing-dot"></div>
              <div className="typing-dot"></div>
            </div>
          )}

          {isStreaming && (
            <div className="streaming-indicator">
              🌊 Streaming response in real-time...
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="input-area">
          <div className="input-container">
            <textarea
              className="message-input"
              placeholder={isListening ? "🎤 Listening..." : "Type your message..."}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isLoading || isStreaming}
              rows={1}
            />
          </div>
          <button
            className={`voice-btn ${isListening ? 'listening' : ''}`}
            onClick={handleVoiceInput}
            title={isListening ? "Stop listening" : "Click and speak"}
            disabled={isStreaming}
          >
            {isListening ? <MicOff size={20} /> : <Mic size={20} />}
          </button>
          <button
            className="send-btn"
            onClick={() => handleSendMessage()}
            disabled={!inputValue.trim() || isLoading || isStreaming}
          >
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default VideoAvatarChat;
