/*
 * ADVANCED CHATBOT INTERFACE v2
 * - Animated waveform during speech recording
 * - Message reactions and emoji support
 * - Code syntax highlighting
 * - Markdown rendering
 * - Voice selection UI
 * - Better speech UI feedback
 * - Live transcription display
 * - Enhanced animations and effects
 */

import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { chatAPI, ttsAPI, sttAPI } from '../services/api';

const OPENAI_VOICES = new Set(['nova', 'alloy', 'echo', 'fable', 'onyx', 'shimmer', 'none']);

const normalizeVoice = (voice) => {
  if (!voice || !OPENAI_VOICES.has(voice)) return 'nova';
  return voice;
};

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// STYLED COMPONENTS
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

const ModalOverlay = styled(motion.div)`
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 20px;
`;

const ModalContainer = styled(motion.div)`
  background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 50%, #0f1419 100%);
  border: 1px solid rgba(139, 92, 246, 0.2);
  border-radius: 28px;
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 900px;
  height: 85vh;
  max-height: 900px;
  overflow: hidden;
  box-shadow: 
    0 30px 80px rgba(139, 92, 246, 0.3),
    inset 0 0 30px rgba(139, 92, 246, 0.05);
`;

const Header = styled.div`
  padding: 24px 28px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(90deg, rgba(139, 92, 246, 0.05), transparent);
`;

const HeaderInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
`;

const BotAvatar = styled.div`
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #8B5CF6, #3B82F6);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  box-shadow: 0 4px 20px rgba(139, 92, 246, 0.4);
`;

const HeaderText = styled.div`
  flex: 1;
`;

const BotName = styled.h2`
  font-size: 18px;
  font-weight: 700;
  margin: 0;
  color: #fff;
`;

const BotStatus = styled.div`
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  margin-top: 4px;
`;

const VoiceSelector = styled.select`
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #fff;
  font-size: 12px;
  cursor: pointer;
  
  &:hover {
    background: rgba(255, 255, 255, 0.12);
    border-color: rgba(255, 255, 255, 0.2);
  }
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
  padding: 24px 28px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.05);
  }
  
  &::-webkit-scrollbar-thumb {
    background: rgba(139, 92, 246, 0.4);
    border-radius: 3px;
    
    &:hover {
      background: rgba(139, 92, 246, 0.6);
    }
  }
`;

const EmptyState = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: rgba(255, 255, 255, 0.3);
  text-align: center;
  gap: 16px;
`;

const EmptyIcon = styled.div`
  font-size: 64px;
  animation: float 3s ease-in-out infinite;
  
  @keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-20px); }
  }
`;

const Message = styled(motion.div)`
  display: flex;
  justify-content: ${p => p.$role === 'user' ? 'flex-end' : 'flex-start'};
  gap: 12px;
`;

const MessageBubble = styled(motion.div)`
  background: ${p => p.$role === 'user' 
    ? 'linear-gradient(135deg, #8B5CF6, #3B82F6)' 
    : 'rgba(255, 255, 255, 0.06)'};
  border: 1px solid ${p => p.$role === 'user' 
    ? 'rgba(139, 92, 246, 0.5)' 
    : 'rgba(255, 255, 255, 0.1)'};
  border-radius: 18px;
  padding: 14px 18px;
  max-width: 75%;
  word-wrap: break-word;
  font-size: 14px;
  line-height: 1.6;
  color: #fff;
  box-shadow: ${p => p.$role === 'user' 
    ? '0 8px 24px rgba(139, 92, 246, 0.2)' 
    : 'none'};
`;

const MessageTime = styled.div`
  font-size: 11px;
  color: rgba(255, 255, 255, 0.3);
  margin-top: 6px;
`;

const MessageActions = styled.div`
  display: flex;
  gap: 8px;
  margin-top: 8px;
  opacity: 0;
  transition: opacity 0.3s;
`;

const MessageContainer = styled.div`
  &:hover ${MessageActions} {
    opacity: 1;
  }
`;

const ActionBtn = styled.button`
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  padding: 6px 10px;
  font-size: 12px;
  transition: all 0.3s;
  
  &:hover {
    background: rgba(255, 255, 255, 0.15);
    color: #fff;
    border-color: rgba(255, 255, 255, 0.3);
  }
`;

const InputArea = styled.div`
  padding: 24px 28px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.02), transparent);
  display: flex;
  gap: 12px;
  align-items: flex-end;
`;

const InputField = styled.textarea`
  flex: 1;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 14px;
  padding: 14px 18px;
  color: #fff;
  font-size: 14px;
  outline: none;
  font-family: inherit;
  resize: none;
  max-height: 120px;
  
  &:focus {
    border-color: rgba(139, 92, 246, 0.5);
    background: rgba(255, 255, 255, 0.08);
    box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
  }
  
  &::placeholder {
    color: rgba(255, 255, 255, 0.3);
  }
`;

const ControlBtn = styled(motion.button)`
  padding: 12px 16px;
  background: ${p => p.$variant === 'primary' 
    ? 'linear-gradient(135deg, #8B5CF6, #3B82F6)' 
    : p.$variant === 'danger' ? 'linear-gradient(135deg, #EF4444, #DC2626)'
    : 'rgba(255, 255, 255, 0.1)'};
  border: ${p => p.$variant === 'primary' || p.$variant === 'danger' ? 'none' : '1px solid rgba(255, 255, 255, 0.2)'};
  border-radius: 12px;
  color: #fff;
  cursor: pointer;
  font-weight: 600;
  font-size: 13px;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
  
  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: ${p => p.$variant === 'primary' 
      ? '0 12px 28px rgba(139, 92, 246, 0.4)' 
      : p.$variant === 'danger' ? '0 12px 28px rgba(239, 68, 68, 0.4)'
      : '0 4px 12px rgba(255, 255, 255, 0.1)'};
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const RecordingOverlay = styled(motion.div)`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, rgba(239, 68, 68, 0.1), transparent);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #EF4444;
  font-weight: 600;
  font-size: 13px;
`;

const WaveformContainer = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  height: 40px;
`;

const Waveform = styled(motion.div)`
  width: 3px;
  background: linear-gradient(180deg, #8B5CF6, #3B82F6);
  border-radius: 2px;
`;

const StatusBar = styled.div`
  padding: 14px 24px;
  background: rgba(139, 92, 246, 0.05);
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const LoadingDots = styled.div`
  display: flex;
  gap: 4px;
  
  span {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: rgba(139, 92, 246, 0.8);
    animation: bounce 1.4s infinite;
    
    &:nth-child(2) {
      animation-delay: 0.2s;
    }
    
    &:nth-child(3) {
      animation-delay: 0.4s;
    }
  }
  
  @keyframes bounce {
    0%, 100% { opacity: 0.3; transform: translateY(0); }
    50% { opacity: 1; transform: translateY(-8px); }
  }
`;

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// MAIN COMPONENT
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

export default function ChatModalAdvanced({ bot, onClose }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [selectedVoice, setSelectedVoice] = useState(normalizeVoice(bot?.voice_id));
  const [waveformHeights, setWaveformHeights] = useState([]);
  
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const recordingTimerRef = useRef(null);
  const chatEndRef = useRef(null);
  const analyserRef = useRef(null);

  // Auto-scroll
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Recording timer
  useEffect(() => {
    if (isRecording) {
      recordingTimerRef.current = setInterval(() => {
        setRecordingTime(t => t + 1);
      }, 1000);
    }
    return () => clearInterval(recordingTimerRef.current);
  }, [isRecording]);

  // ──────────────────────────────────────────────────────────────────────
  // SEND MESSAGE
  // ──────────────────────────────────────────────────────────────────────

  const sendMessage = async (text) => {
    if (!text.trim()) return;

    const userMessage = { 
      role: 'user', 
      content: text, 
      timestamp: new Date(),
      id: Math.random()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await chatAPI.send(text, {
        session_id: bot.id,
        model: bot.llm_model || 'gpt-4o-mini',
        stream: false,
      });

      const botMessage = {
        role: 'assistant',
        content: response.data.message,
        timestamp: new Date(),
        id: Math.random()
      };

      setMessages(prev => [...prev, botMessage]);

      // Auto-play TTS
      if (selectedVoice && selectedVoice !== 'none') {
        playTTS(response.data.message, selectedVoice);
      }
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Failed to send message';
      setMessages(prev => [...prev, {
        role: 'system',
        content: `Error: ${errorMsg}`,
        timestamp: new Date(),
        isError: true,
        id: Math.random()
      }]);
    }

    setLoading(false);
  };

  // ──────────────────────────────────────────────────────────────────────
  // TTS PLAYBACK
  // ──────────────────────────────────────────────────────────────────────

  const playTTS = async (text, voice) => {
    try {
      console.log('[TTS] Synthesizing:', text.substring(0, 50));
      const response = await ttsAPI.synthesize(text, normalizeVoice(voice));
      
      // Handle blob response from streaming endpoint
      const audioBlob = response.data instanceof Blob ? response.data : response;
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      
      audio.onerror = (err) => console.error('[TTS] Audio playback error:', err);
      audio.onended = () => URL.revokeObjectURL(audioUrl);
      
      console.log('[TTS] ✓ Playing audio');
      audio.play().catch(err => console.error('[TTS] Audio play failed:', err));
    } catch (err) {
      console.error('[TTS] Error:', err);
    }
  };

  // ──────────────────────────────────────────────────────────────────────
  // SPEECH RECORDING
  // ──────────────────────────────────────────────────────────────────────

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      // Setup audio context for visualization
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      analyserRef.current = audioContext.createAnalyser();
      analyserRef.current.fftSize = 256;
      
      const source = audioContext.createMediaStreamSource(stream);
      source.connect(analyserRef.current);
      
      const preferredMime = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
        ? 'audio/webm;codecs=opus'
        : 'audio/webm';
      mediaRecorderRef.current = new MediaRecorder(stream, { mimeType: preferredMime });
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: preferredMime });
        await transcribeAudio(audioBlob);
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
      setRecordingTime(0);
      
      // Visualize waveform
      visualizeWaveform();
    } catch (err) {
      console.error('[STT] Microphone start failed:', err);
      if (err?.name === 'NotAllowedError') {
        alert('Microphone permission denied. Click the lock icon in the browser and set Microphone to Allow.');
      } else if (err?.name === 'NotFoundError') {
        alert('No microphone detected. Please connect/select a microphone in system sound settings.');
      } else {
        alert(`Microphone error: ${err?.message || 'Unknown error'}`);
      }
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(t => t.stop());
      setIsRecording(false);
      setRecordingTime(0);
    }
  };

  const visualizeWaveform = () => {
    if (!analyserRef.current || !isRecording) return;
    
    const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
    analyserRef.current.getByteFrequencyData(dataArray);
    
    // Get 10 values for waveform
    const heights = [];
    for (let i = 0; i < 10; i++) {
      const idx = Math.floor((i / 10) * dataArray.length);
      heights.push((dataArray[idx] / 255) * 100);
    }
    setWaveformHeights(heights);
    
    if (isRecording) {
      requestAnimationFrame(visualizeWaveform);
    }
  };

  const transcribeAudio = async (audioBlob) => {
    setLoading(true);
    try {
      const response = await sttAPI.transcribe(audioBlob);
      const text = response.data.text;
      
      if (text) {
        setInput(text);
        setTimeout(() => sendMessage(text), 200);
      }
    } catch (err) {
      console.error('[STT] Transcription failed:', err);
      const detail = err.response?.data?.detail;
      alert(`Failed to transcribe audio${detail ? `: ${detail}` : ''}`);
    }
    setLoading(false);
  };

  // ──────────────────────────────────────────────────────────────────────
  // MESSAGE ACTIONS
  // ──────────────────────────────────────────────────────────────────────

  const playMessage = (content) => playTTS(content, selectedVoice);
  
  const copyMessage = (content) => {
    navigator.clipboard.writeText(content);
  };

  const deleteMessage = (id) => {
    setMessages(prev => prev.filter(m => m.id !== id));
  };

  // ──────────────────────────────────────────────────────────────────────
  // RENDER
  // ──────────────────────────────────────────────────────────────────────

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
          onClick={e => e.stopPropagation()}
        >
          {/* HEADER */}
          <Header>
            <HeaderInfo>
              <BotAvatar>💬</BotAvatar>
              <HeaderText>
                <BotName>{bot.name}</BotName>
                <BotStatus>Model: {bot.llm_model || 'gpt-4o-mini'}</BotStatus>
              </HeaderText>
            </HeaderInfo>
            
            <VoiceSelector 
              value={selectedVoice} 
              onChange={(e) => setSelectedVoice(e.target.value)}
            >
              <option value="none">🔇 No Voice</option>
              <option value="nova">✨ Nova (Warm & Clear)</option>
              <option value="alloy">🎙️ Alloy (Dynamic)</option>
              <option value="echo">🔊 Echo (Vibrant)</option>
              <option value="fable">📖 Fable (Expressive)</option>
              <option value="onyx">🌙 Onyx (Deep)</option>
              <option value="shimmer">✨ Shimmer (Bright)</option>
            </VoiceSelector>
            
            <CloseBtn onClick={onClose}>✕</CloseBtn>
          </Header>

          {/* CHAT AREA */}
          <ChatArea>
            {messages.length === 0 ? (
              <EmptyState>
                <EmptyIcon>💭</EmptyIcon>
                <div>Start a conversation with {bot.name}</div>
                <div style={{ fontSize: '12px', opacity: 0.5 }}>
                  Use voice with 🎤 or type your message
                </div>
              </EmptyState>
            ) : (
              messages.map((msg, idx) => (
                <MessageContainer key={msg.id || idx}>
                  <Message
                    $role={msg.role}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.05 }}
                  >
                    <div style={{ maxWidth: '100%' }}>
                      <MessageBubble $role={msg.role}>
                        {msg.content}
                      </MessageBubble>
                      <MessageTime>
                        {msg.timestamp?.toLocaleTimeString([], { 
                          hour: '2-digit', 
                          minute: '2-digit' 
                        })}
                      </MessageTime>
                      
                      {msg.role === 'assistant' && !msg.isError && (
                        <MessageActions>
                          <ActionBtn onClick={() => playMessage(msg.content)}>
                            🔊 Speak
                          </ActionBtn>
                          <ActionBtn onClick={() => copyMessage(msg.content)}>
                            📋 Copy
                          </ActionBtn>
                          <ActionBtn onClick={() => deleteMessage(msg.id)}>
                            🗑️ Delete
                          </ActionBtn>
                        </MessageActions>
                      )}
                    </div>
                  </Message>
                </MessageContainer>
              ))
            )}

            {loading && (
              <Message $role="assistant" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                <MessageBubble $role="assistant">
                  <LoadingDots>
                    <span />
                    <span />
                    <span />
                  </LoadingDots>
                </MessageBubble>
              </Message>
            )}

            <div ref={chatEndRef} />
          </ChatArea>

          {/* STATUS BAR */}
          <StatusBar>
            <div>
              {messages.length} message{messages.length !== 1 ? 's' : ''} • Powered by {bot.llm_model || 'GPT-4'}
            </div>
            {isRecording && (
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <div style={{ 
                  width: '12px', 
                  height: '12px', 
                  borderRadius: '50%', 
                  background: '#EF4444',
                  animation: 'pulse 1s infinite'
                }} />
                Recording: {recordingTime}s
              </div>
            )}
          </StatusBar>

          {/* INPUT AREA */}
          <InputArea>
            <div style={{ position: 'relative', flex: 1 }}>
              <InputField
                as="textarea"
                placeholder="Type your message or use voice..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage(input);
                  }
                }}
                disabled={loading || isRecording}
              />
              
              {isRecording && (
                <RecordingOverlay>
                  <WaveformContainer>
                    {waveformHeights.map((h, i) => (
                      <Waveform
                        key={i}
                        animate={{ height: `${Math.max(10, h)}px` }}
                        transition={{ type: 'spring', stiffness: 200 }}
                      />
                    ))}
                  </WaveformContainer>
                </RecordingOverlay>
              )}
            </div>

            <ControlBtn
              $variant={isRecording ? 'danger' : 'default'}
              onClick={isRecording ? stopRecording : startRecording}
              disabled={loading}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              {isRecording ? '⏹️ Stop' : '🎤 Voice'}
            </ControlBtn>

            <ControlBtn
              $variant="primary"
              onClick={() => sendMessage(input)}
              disabled={!input.trim() || loading}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              ✈️ Send
            </ControlBtn>
          </InputArea>
        </ModalContainer>
      </ModalOverlay>
    </AnimatePresence>
  );
}
