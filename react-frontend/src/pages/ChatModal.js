// ChatModal — Chat with TTS/STT integration
import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { chatAPI, ttsAPI, sttAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

// ── Styled Components ────────────────────────────────

const ModalOverlay = styled(motion.div)`
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 20px;
`;

const ModalContainer = styled(motion.div)`
  background: linear-gradient(135deg, #1a1f2e 0%, #0f1419 100%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 800px;
  height: 80vh;
  max-height: 800px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
`;

const Header = styled.div`
  padding: 20px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.02);
`;

const Title = styled.h2`
  font-size: 18px;
  font-weight: 700;
  margin: 0;
  background: linear-gradient(135deg, #8B5CF6, #3B82F6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
`;

const CloseBtn = styled.button`
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.6);
  font-size: 28px;
  cursor: pointer;
  padding: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  &:hover {
    color: #fff;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 50%;
  }
`;

const ChatArea = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const Message = styled.div`
  display: flex;
  justify-content: ${p => p.$role === 'user' ? 'flex-end' : 'flex-start'};
  gap: 12px;
  animation: slideIn 0.3s ease;
  
  @keyframes slideIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }
`;

const MessageBubble = styled.div`
  background: ${p => p.$role === 'user' 
    ? 'linear-gradient(135deg, #8B5CF6, #3B82F6)' 
    : 'rgba(255, 255, 255, 0.06)'};
  border: 1px solid ${p => p.$role === 'user' 
    ? 'transparent' 
    : 'rgba(255, 255, 255, 0.1)'};
  border-radius: 16px;
  padding: 12px 16px;
  max-width: 70%;
  word-wrap: break-word;
  font-size: 14px;
  line-height: 1.5;
  color: #fff;
`;

const MessageActions = styled.div`
  display: flex;
  gap: 8px;
  margin-top: 4px;
`;

const IconBtn = styled.button`
  background: none;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  padding: 6px 8px;
  font-size: 12px;
  transition: all 0.3s;
  
  &:hover {
    background: rgba(255, 255, 255, 0.1);
    color: #fff;
    border-color: rgba(255, 255, 255, 0.4);
  }
  
  &:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }
`;

const InputArea = styled.div`
  padding: 20px 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.02);
  display: flex;
  gap: 12px;
  align-items: flex-end;
`;

const InputField = styled.input`
  flex: 1;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 12px 16px;
  color: #fff;
  font-size: 14px;
  outline: none;
  
  &:focus {
    border-color: rgba(139, 92, 246, 0.5);
    background: rgba(255, 255, 255, 0.08);
  }
  
  &::placeholder {
    color: rgba(255, 255, 255, 0.3);
  }
`;

const ControlBtn = styled.button`
  padding: 10px 14px;
  background: ${p => p.$variant === 'primary' 
    ? 'linear-gradient(135deg, #8B5CF6, #3B82F6)' 
    : 'rgba(255, 255, 255, 0.1)'};
  border: none;
  border-radius: 10px;
  color: #fff;
  cursor: pointer;
  font-weight: 600;
  font-size: 13px;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 6px;
  
  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 10px 20px rgba(139, 92, 246, 0.3);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const StatusBar = styled.div`
  padding: 12px 24px;
  background: rgba(255, 255, 255, 0.02);
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const RecordingIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  
  .pulse {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #ef4444;
    animation: pulse 1s infinite;
  }
  
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }
`;

// ── ChatModal Component ──────────────────────────────

export default function ChatModal({ bot, onClose }) {
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const chatEndRef = useRef(null);

  // Auto-scroll to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // ── Send Message ─────────────────────────────────

  const sendMessage = async (text) => {
    if (!text.trim()) return;

    // Add user message
    setMessages(prev => [...prev, { role: 'user', content: text, timestamp: new Date() }]);
    setInput('');
    setLoading(true);

    try {
      // Send to backend
      const response = await chatAPI.send(text, {
        session_id: bot.id,
        model: bot.llm_model,
        stream: false,
      });

      const botMessage = response.data.message;

      // Add bot message
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: botMessage,
        timestamp: new Date(),
      }]);

      // Auto-play TTS if voice is configured
      if (bot.voice_id) {
        playTTS(botMessage, bot.voice_id);
      }
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Failed to send message';
      setMessages(prev => [...prev, { 
        role: 'system', 
        content: `Error: ${errorMsg}`,
        timestamp: new Date(),
        isError: true,
      }]);
    }

    setLoading(false);
  };

  // ── TTS (Text-to-Speech) ─────────────────────────

  const playTTS = async (text, voice) => {
    try {
      const response = await ttsAPI.synthesize(text, voice);
      
      // Play audio
      const audioData = response.data.audio || response.data;
      const audioBlob = typeof audioData === 'string' 
        ? await fetch(`data:audio/mp3;base64,${audioData}`).then(r => r.blob())
        : audioData;

      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      audio.play().catch(err => console.error('Failed to play audio:', err));
    } catch (err) {
      console.error('TTS Error:', err);
      alert('Failed to generate speech');
    }
  };

  const handlePlayMessage = async (content, voice) => {
    await playTTS(content, voice || bot.voice_id);
  };

  // ── STT (Speech-to-Text) ─────────────────────────

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        await transcribeAudio(audioBlob);
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (err) {
      console.error('Recording Error:', err);
      alert('Microphone access denied');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      setIsRecording(false);
    }
  };

  const transcribeAudio = async (audioBlob) => {
    setLoading(true);
    try {
      const response = await sttAPI.transcribe(audioBlob);
      const transcribedText = response.data.text;
      
      if (transcribedText) {
        setInput(transcribedText);
        // Auto-send after transcription
        setTimeout(() => sendMessage(transcribedText), 500);
      }
    } catch (err) {
      console.error('STT Error:', err);
      alert('Failed to transcribe audio');
    }
    setLoading(false);
  };

  // ── Render ───────────────────────────────────────

  return (
    <AnimatePresence>
      <ModalOverlay
        as={motion.div}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
      >
        <ModalContainer
          as={motion.div}
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <Header>
            <div>
              <Title>💬 {bot.name}</Title>
              <div style={{ fontSize: '12px', color: 'rgba(255,255,255,0.4)', marginTop: '4px' }}>
                {bot.llm_model} • Voice: {bot.voice_id}
              </div>
            </div>
            <CloseBtn onClick={onClose}>×</CloseBtn>
          </Header>

          {/* Chat Messages */}
          <ChatArea>
            {messages.length === 0 && (
              <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center', 
                height: '100%',
                color: 'rgba(255,255,255,0.3)',
                textAlign: 'center',
              }}>
                <div>
                  <div style={{ fontSize: '48px', marginBottom: '12px' }}>👋</div>
                  <div>Start a conversation with {bot.name}</div>
                </div>
              </div>
            )}

            {messages.map((msg, idx) => (
              <Message key={idx} $role={msg.role}>
                <div style={{ maxWidth: '85%' }}>
                  <MessageBubble $role={msg.role} style={{
                    background: msg.isError ? 'rgba(239, 68, 68, 0.15)' : undefined,
                    borderColor: msg.isError ? 'rgba(239, 68, 68, 0.3)' : undefined,
                    color: msg.isError ? '#fca5a5' : '#fff',
                  }}>
                    {msg.content}
                  </MessageBubble>

                  {msg.role === 'assistant' && !msg.isError && (
                    <MessageActions>
                      <IconBtn onClick={() => handlePlayMessage(msg.content, bot.voice_id)}>
                        🔊 Speak
                      </IconBtn>
                      <IconBtn onClick={() => navigator.clipboard.writeText(msg.content)}>
                        📋 Copy
                      </IconBtn>
                    </MessageActions>
                  )}
                </div>
              </Message>
            ))}

            {loading && (
              <Message $role="assistant">
                <MessageBubble $role="assistant">
                  <div style={{ display: 'flex', gap: '4px' }}>
                    <span style={{ animation: 'bounce 1s infinite' }}>●</span>
                    <span style={{ animation: 'bounce 1s infinite 0.1s' }}>●</span>
                    <span style={{ animation: 'bounce 1s infinite 0.2s' }}>●</span>
                  </div>
                  <style>{`
                    @keyframes bounce {
                      0%, 100% { opacity: 0.4; }
                      50% { opacity: 1; }
                    }
                  `}</style>
                </MessageBubble>
              </Message>
            )}

            <div ref={chatEndRef} />
          </ChatArea>

          {/* Status Bar */}
          <StatusBar>
            <div>
              {messages.length} messages • Model: {bot.llm_model}
            </div>
            {isRecording && (
              <RecordingIndicator>
                <div className="pulse"></div>
                Recording...
              </RecordingIndicator>
            )}
          </StatusBar>

          {/* Input Area */}
          <InputArea>
            <InputField
              type="text"
              placeholder="Type a message or use voice..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  sendMessage(input);
                }
              }}
              disabled={loading}
            />

            <ControlBtn
              $variant={isRecording ? 'danger' : 'default'}
              onClick={isRecording ? stopRecording : startRecording}
              disabled={loading}
              title={isRecording ? 'Stop Recording' : 'Start Recording'}
            >
              {isRecording ? '⏹️ Stop' : '🎤 Voice'}
            </ControlBtn>

            <ControlBtn
              $variant="primary"
              onClick={() => sendMessage(input)}
              disabled={!input.trim() || loading}
              title="Send Message"
            >
              📤 Send
            </ControlBtn>
          </InputArea>
        </ModalContainer>
      </ModalOverlay>
    </AnimatePresence>
  );
}
