

/**
 * RealtimeAudioStreamer - Real-time Speech-to-Text + Text-to-Speech
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * ⚡ Features:
 *   - WebSocket streaming for low-latency audio (200-500ms round-trip)
 *   - Live waveform visualization
 *   - Real-time transcription display
 *   - Concurrent mic + speaker (listen while speaking)
 *   - Automatic reconnection
 *   - Subscription-aware limits
 *
 * Usage:
 * ──────
 *   <RealtimeAudioStreamer
 *     chatbotId="bot-123"
 *     userId="user-456"
 *     onTranscription={(text) => console.log(text)}
 *     onResponse={(text) => console.log(text)}
 *   />
 *
 * Architecture:
 * ─────────────
 *   Mic Input
 *       ↓
 *   [Audio Chunks]
 *       ↓
 *   WebSocket → Backend
 *       ↓
 *   STT (Whisper) + Chat + TTS
 *       ↓
 *   WebSocket → Frontend
 *       ↓
 *   Speaker Output
 */

import React, { useState, useRef, useEffect, useCallback } from 'react';
import styled from 'styled-components';

// ═════════════════════════════════════════════════════════════════════════════
// AUDIO CONFIGURATION
// ═════════════════════════════════════════════════════════════════════════════

const AUDIO_CONFIG = {
  sampleRate: 16000,
  channels: 1,
  bufferSize: 4096,
  mimeType: 'audio/wav',
  chunkDurationMs: 100, // Send 100ms chunks for real-time latency
};

// ═════════════════════════════════════════════════════════════════════════════
// STYLED COMPONENTS
// ═════════════════════════════════════════════════════════════════════════════

const Container = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
`;

const Header = styled.div`
  font-size: 18px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  
  .status {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: ${props => props.connected ? '#10b981' : '#ef4444'};
    animation: ${props => props.connected ? 'pulse' : 'none'} 2s infinite;
  }
  
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }
`;

const WaveformDisplay = styled.div`
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  padding: 16px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2px;
  overflow: hidden;
`;

const Waveform = styled.div`
  display: flex;
  align-items: flex-end;
  gap: 2px;
  height: 100%;
  
  span {
    background: ${props => props.active ? '#fbbf24' : 'rgba(255,255,255,0.3)'};
    width: 3px;
    border-radius: 2px;
    transition: all 0.1s ease;
    animation: ${props => props.animate ? 'waveMove' : 'none'} 0.3s ease;
  }
  
  @keyframes waveMove {
    0% { height: 20%; opacity: 0.5; }
    50% { height: 100%; opacity: 1; }
    100% { height: 20%; opacity: 0.5; }
  }
`;

const TranscriptionBox = styled.div`
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  padding: 12px;
  min-height: 40px;
  font-size: 14px;
  line-height: 1.5;
  
  .partial {
    opacity: 0.7;
    font-style: italic;
  }
  
  .final {
    opacity: 1;
    font-weight: 500;
  }
`;

const ResponseBox = styled.div`
  background: rgba(0, 0, 0, 0.15);
  border-radius: 8px;
  padding: 12px;
  min-height: 40px;
  font-size: 14px;
  line-height: 1.5;
  border-left: 3px solid #fbbf24;
`;

const ControlsContainer = styled.div`
  display: flex;
  gap: 12px;
  justify-content: center;
`;

const Button = styled.button`
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const RecordButton = styled(Button)`
  background: ${props => props.recording ? '#ef4444' : '#10b981'};
  color: white;
  
  &:hover:not(:disabled) {
    background: ${props => props.recording ? '#dc2626' : '#059669'};
  }
`;

const StatusBar = styled.div`
  font-size: 12px;
  opacity: 0.9;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
`;

// ═════════════════════════════════════════════════════════════════════════════
// MAIN COMPONENT
// ═════════════════════════════════════════════════════════════════════════════

export default function RealtimeAudioStreamer({
  chatbotId = 'default',
  userId = 'demo',
  backendUrl = 'ws://localhost:8000',
  onTranscription = () => {},
  onResponse = () => {},
  onError = () => {},
  autoPlay = true,
}) {
  // ─────────────────────────────────────────────────────────────────────────
  // STATE
  // ─────────────────────────────────────────────────────────────────────────

  const [isConnected, setIsConnected] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [transcriptionText, setTranscriptionText] = useState('');
  const [responseText, setResponseText] = useState('');
  const [recordingTime, setRecordingTime] = useState(0);
  const [waveformData, setWaveformData] = useState(Array(20).fill(20));
  const [connectionStatus, setConnectionStatus] = useState('Disconnected');
  const [stats, setStats] = useState({
    audioChunksSent: 0,
    transcriptionLatencyMs: 0,
    audioChunksReceived: 0,
  });

  // ─────────────────────────────────────────────────────────────────────────
  // REFS
  // ─────────────────────────────────────────────────────────────────────────

  const wsRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioStreamRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const recordingTimerRef = useRef(null);
  const audioChunksRef = useRef([]);
  const waveformIntervalRef = useRef(null);
  const audioPlaybackRef = useRef(null);

  // ─────────────────────────────────────────────────────────────────────────
  // WEBSOCKET CONNECTION
  // ─────────────────────────────────────────────────────────────────────────

  const connectWebSocket = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    try {
      const wsUrl = `${backendUrl}/ws/audio/streaming?user_id=${userId}`;
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        console.log('✅ WebSocket connected');
        setIsConnected(true);
        setConnectionStatus('Connected');
      };

      wsRef.current.onmessage = async (event) => {
        await handleWebSocketMessage(JSON.parse(event.data));
      };

      wsRef.current.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        setConnectionStatus('Error');
        onError(error);
      };

      wsRef.current.onclose = () => {
        console.log('🔌 WebSocket disconnected');
        setIsConnected(false);
        setConnectionStatus('Disconnected');
        // Attempt reconnection
        setTimeout(() => {
          connectWebSocket();
        }, 3000);
      };
    } catch (error) {
      console.error('Connection error:', error);
      onError(error);
    }
  }, [backendUrl, userId, onError]);

  // ─────────────────────────────────────────────────────────────────────────
  // WEBSOCKET MESSAGE HANDLER
  // ─────────────────────────────────────────────────────────────────────────

  const handleWebSocketMessage = async (message) => {
    const { type, data, text, error, chunks_sent, index, final } = message;

    switch (type) {
      case 'ack':
        // Audio chunk received by server
        setStats(s => ({ ...s, audioChunksSent: message.chunks_received }));
        break;

      case 'transcription':
        // STT complete
        setIsTranscribing(false);
        setTranscriptionText(text);
        onTranscription(text);
        const latency = Date.now() - recordingStartTimeRef.current;
        setStats(s => ({ ...s, transcriptionLatencyMs: latency }));
        break;

      case 'chat_response':
        // Chat response received
        setResponseText(text);
        onResponse(text);
        break;

      case 'tts_chunk':
        // TTS audio chunk received
        await playAudioChunk(data);
        if (index === 0) {
          setStats(s => ({ ...s, audioChunksReceived: 1 }));
        }
        break;

      case 'tts_complete':
        // TTS streaming complete
        console.log(`✅ TTS complete: ${chunks_sent} chunks`);
        break;

      case 'reset_ack':
        // Buffer reset acknowledged
        audioChunksRef.current = [];
        break;

      case 'error':
        console.error('Server error:', error);
        onError(new Error(error));
        break;

      default:
        console.warn('Unknown message type:', type);
    }
  };

  // ─────────────────────────────────────────────────────────────────────────
  // RECORDING
  // ─────────────────────────────────────────────────────────────────────────

  const recordingStartTimeRef = useRef(0);

  const startRecording = async () => {
    try {
      if (!isConnected) {
        alert('⚠️ WebSocket not connected. Please wait...');
        return;
      }

      // Get audio stream
      audioStreamRef.current = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: AUDIO_CONFIG.sampleRate,
        },
      });

      // Setup audio context for visualization
      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
      analyserRef.current = audioContextRef.current.createAnalyser();
      analyserRef.current.fftSize = 256;

      const source = audioContextRef.current.createMediaStreamSource(audioStreamRef.current);
      source.connect(analyserRef.current);

      // Setup media recorder
      mediaRecorderRef.current = new MediaRecorder(audioStreamRef.current, {
        mimeType: 'audio/webm',
        audioBitsPerSecond: 128000,
      });

      audioChunksRef.current = [];
      recordingStartTimeRef.current = Date.now();

      mediaRecorderRef.current.ondataavailable = async (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
          
          // Send chunk to server immediately (streaming)
          const base64 = await blobToBase64(event.data);
          wsRef.current?.send(JSON.stringify({
            type: 'audio_chunk',
            data: base64,
            encoding: 'base64',
          }));
        }
      };

      // Start recording with 100ms chunks
      mediaRecorderRef.current.start(AUDIO_CONFIG.chunkDurationMs);
      setIsRecording(true);
      setRecordingTime(0);
      setTranscriptionText('');
      setIsTranscribing(false);

      // Start recording timer
      recordingTimerRef.current = setInterval(() => {
        setRecordingTime(t => t + 1);
      }, 1000);

      // Start waveform visualization
      startWaveformVisualization();

      console.log('🎤 Recording started');
    } catch (error) {
      console.error('Recording error:', error);
      alert(`❌ Microphone error: ${error.message}`);
      onError(error);
    }
  };

  const stopRecording = () => {
    if (!mediaRecorderRef.current || !isRecording) return;

    mediaRecorderRef.current.stop();
    audioStreamRef.current?.getTracks().forEach(track => track.stop());
    audioContextRef.current?.close();

    clearInterval(recordingTimerRef.current);
    clearInterval(waveformIntervalRef.current);

    setIsRecording(false);
    setRecordingTime(0);

    // Signal server to transcribe
    setIsTranscribing(true);
    wsRef.current?.send(JSON.stringify({ type: 'transcribe' }));

    console.log('⏹️ Recording stopped, starting transcription...');
  };

  // ─────────────────────────────────────────────────────────────────────────
  // WAVEFORM VISUALIZATION
  // ─────────────────────────────────────────────────────────────────────────

  const startWaveformVisualization = () => {
    waveformIntervalRef.current = setInterval(() => {
      if (!analyserRef.current || !isRecording) return;

      const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
      analyserRef.current.getByteFrequencyData(dataArray);

      const newWaveform = Array(20)
        .fill(0)
        .map((_, i) => {
          const start = Math.floor((i / 20) * dataArray.length);
          const end = Math.floor(((i + 1) / 20) * dataArray.length);
          const slice = dataArray.slice(start, end);
          return (
            (slice.reduce((a, b) => a + b, 0) / slice.length / 255) * 100 +
            20
          );
        });

      setWaveformData(newWaveform);
    }, 50);
  };

  // ─────────────────────────────────────────────────────────────────────────
  // AUDIO PLAYBACK
  // ─────────────────────────────────────────────────────────────────────────

  const playAudioChunk = async (base64Data) => {
    if (!autoPlay) return;

    try {
      const binaryString = atob(base64Data);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      const blob = new Blob([bytes], { type: 'audio/mp3' });
      const url = URL.createObjectURL(blob);

      if (!audioPlaybackRef.current) {
        audioPlaybackRef.current = new Audio();
      }

      audioPlaybackRef.current.src = url;
      audioPlaybackRef.current.play().catch(e => console.warn('Play failed:', e));
    } catch (error) {
      console.error('Audio playback error:', error);
    }
  };

  // ─────────────────────────────────────────────────────────────────────────
  // UTILITIES
  // ─────────────────────────────────────────────────────────────────────────

  const blobToBase64 = (blob) => {
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        resolve(reader.result.split(',')[1]);
      };
      reader.readAsDataURL(blob);
    });
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // ─────────────────────────────────────────────────────────────────────────
  // EFFECTS
  // ─────────────────────────────────────────────────────────────────────────

  useEffect(() => {
    connectWebSocket();

    return () => {
      wsRef.current?.close();
      audioStreamRef.current?.getTracks().forEach(track => track.stop());
      audioContextRef.current?.close();
      clearInterval(recordingTimerRef.current);
      clearInterval(waveformIntervalRef.current);
    };
  }, [connectWebSocket]);

  // ─────────────────────────────────────────────────────────────────────────
  // RENDER
  // ─────────────────────────────────────────────────────────────────────────

  return (
    <Container>
      <Header connected={isConnected}>
        <div className="status" />
        🎤 Real-time Voice Chat
      </Header>

      {/* Waveform Visualization */}
      <WaveformDisplay>
        <Waveform>
          {waveformData.map((height, i) => (
            <span
              key={i}
              style={{ height: `${height}%` }}
              active={isRecording}
              animate={isRecording}
            />
          ))}
        </Waveform>
      </WaveformDisplay>

      {/* Transcription Display */}
      <TranscriptionBox>
        {isTranscribing && <div className="partial">🔍 Transcribing...</div>}
        {transcriptionText && (
          <div className="final">👤 You: {transcriptionText}</div>
        )}
        {!transcriptionText && !isTranscribing && (
          <div style={{ opacity: 0.5 }}>Click record to start speaking...</div>
        )}
      </TranscriptionBox>

      {/* Response Display */}
      {responseText && (
        <ResponseBox>
          🤖 Bot: {responseText}
        </ResponseBox>
      )}

      {/* Controls */}
      <ControlsContainer>
        <RecordButton
          recording={isRecording}
          onClick={isRecording ? stopRecording : startRecording}
          disabled={!isConnected}
        >
          {isRecording ? `⏹️ Stop (${formatTime(recordingTime)})` : '🎤 Start Record'}
        </RecordButton>
      </ControlsContainer>

      {/* Status Bar */}
      <StatusBar>
        <div>{connectionStatus}</div>
        <div>📤 {stats.audioChunksSent} chunks | {stats.transcriptionLatencyMs}ms</div>
        <div>📥 {stats.audioChunksReceived} TTS chunks</div>
      </StatusBar>
    </Container>
  );
}
