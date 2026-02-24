// src/components/ModernChatbot.tsx
import React, { useState, useRef, useEffect } from 'react';
import { useChatbot } from '../hooks/useChatbot';
import { Message, AudioMode } from '../types/chatbot';
import styles from './ModernChatbot.module.css';

interface ModernChatbotProps {
  apiBaseUrl: string;
  botName?: string;
  botAvatar?: string;
}

export const ModernChatbot: React.FC<ModernChatbotProps> = ({
  apiBaseUrl,
  botName = 'Ambassador Paul',
  botAvatar = '👨‍💼',
}) => {
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const {
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
    setIsSpeakerOn,
  } = useChatbot(apiBaseUrl);

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Handle sending message
  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return;
    await sendMessage(inputValue);
    setInputValue('');
    inputRef.current?.focus();
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !isLoading && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Handle microphone button
  const handleMicClick = async () => {
    if (isRecording) {
      await stopRecording();
    } else {
      await startRecording();
    }
  };

  // Auto-play response if speaker is on
  useEffect(() => {
    if (messages.length > 0 && !isLoading) {
      const lastMessage = messages[messages.length - 1];
      if (!lastMessage.isUser && audioMode === AudioMode.AUTO && isSpeakerOn && !isPlayingAudio) {
        playTTS(lastMessage.content);
      }
    }
  }, [messages, isLoading, audioMode, isSpeakerOn, isPlayingAudio, playTTS]);

  return (
    <div className={styles.container}>
      {/* Header */}
      <div className={styles.header}>
        <div className={styles.headerContent}>
          <div className={styles.botInfo}>
            <div className={styles.botAvatar}>{botAvatar}</div>
            <div className={styles.botDetails}>
              <h1 className={styles.botName}>{botName}</h1>
              <p className={styles.botStatus}>
                {isLoading ? '⌛ Thinking...' : '✓ Online'}
              </p>
            </div>
          </div>
          <div className={styles.headerActions}>
            <button
              className={`${styles.headerBtn} ${isSpeakerOn ? styles.active : ''}`}
              onClick={() => setIsSpeakerOn(!isSpeakerOn)}
              title={isSpeakerOn ? 'Mute speaker' : 'Unmute speaker'}
            >
              {isSpeakerOn ? '🔊' : '🔇'}
            </button>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className={styles.messagesContainer}>
        {messages.length === 0 ? (
          <div className={styles.emptyState}>
            <div className={styles.emptyIcon}>💬</div>
            <h2>Start a conversation</h2>
            <p>Type a message or use the microphone to speak with {botName}</p>
          </div>
        ) : (
          <div className={styles.messagesList}>
            {messages.map((msg: Message) => (
              <React.Fragment key={msg.id}>
                <div
                  className={`${styles.messageRow} ${msg.isUser ? styles.userRow : styles.botRow}`}
                >
                  <div className={styles.messageBubble} data-role={msg.isUser ? 'user' : 'bot'}>
                    {msg.isUser ? (
                      <div className={styles.userMessage}>{msg.content}</div>
                    ) : (
                      <div className={styles.botMessage}>
                        <div className={styles.botMessageText}>{msg.content}</div>
                        {isSpeakerOn && (
                          <button
                            className={styles.playBtn}
                            onClick={() => playTTS(msg.content)}
                            disabled={isPlayingAudio}
                            title="Play audio response"
                          >
                            {isPlayingAudio ? '♫' : '▶'}
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                </div>
                {!msg.isUser && msg.usedKnowledgeBase && (
                  <div className={styles.sourceBadge} title={`Knowledge Base: ${msg.sources?.join(', ') || 'Custom Documents'}`}>
                    📚 Knowledge
                  </div>
                )}
              </React.Fragment>
            ))}
            {isLoading && (
              <div className={`${styles.messageRow} ${styles.botRow}`}>
                <div className={styles.messageBubble} data-role="bot">
                  <div className={styles.loadingDots}>
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className={styles.inputArea}>
        <div className={styles.inputWrapper}>
          {/* Microphone Button */}
          <button
            className={`${styles.micBtn} ${isRecording ? styles.recording : ''}`}
            onClick={handleMicClick}
            title={isRecording ? `Recording... ${recordingDuration}s` : 'Click to record voice'}
            disabled={isLoading}
          >
            {isRecording ? (
              <>
                <span className={styles.recordingPulse}></span>
                <span className={styles.recordingTime}>{recordingDuration}s</span>
              </>
            ) : (
              '🎤'
            )}
          </button>

          {/* Text Input */}
          <input
            ref={inputRef}
            type="text"
            className={styles.textInput}
            placeholder="Type a message or speak..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isLoading || isRecording}
          />

          {/* Send Button */}
          <button
            className={styles.sendBtn}
            onClick={handleSend}
            disabled={!inputValue.trim() || isLoading}
            title="Send message"
          >
            {isLoading ? '⏳' : '→'}
          </button>
        </div>
        <div className={styles.inputHint}>
          {isRecording && (
            <div className={styles.recordingHint}>
              🎙️ Recording in progress... Speak now or click button to stop
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
