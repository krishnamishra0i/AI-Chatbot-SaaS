// src/components/ChatPanel.tsx
import React, { useRef, useEffect } from 'react';
import { MessageBubble } from './MessageBubble';
import { Message, AudioMode } from '../types/chatbot';
import styles from './ChatPanel.module.css';

interface ChatPanelProps {
  messages: Message[];
  isLoading: boolean;
  isSpeakerOn: boolean;
  audioMode: AudioMode;
  isRecording: boolean;
  isPlayingAudio: boolean;
  onSendMessage: (text: string) => void;
  onPlayAudio: (text: string) => void;
  onToggleSpeaker: () => void;
  onStartRecording: () => void;
  onStopRecording: () => void;
}

export const ChatPanel: React.FC<ChatPanelProps> = ({
  messages,
  isLoading,
  isSpeakerOn,
  audioMode,
  isRecording,
  isPlayingAudio,
  onSendMessage,
  onPlayAudio,
  onToggleSpeaker,
  onStartRecording,
  onStopRecording,
}) => {
  const inputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [inputValue, setInputValue] = React.useState('');

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = () => {
    if (!inputValue.trim() || isLoading) return;
    onSendMessage(inputValue);
    setInputValue('');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !isLoading) {
      handleSend();
    }
  };

  return (
    <div className={styles.container}>
      {/* Header */}
      <div className={styles.header}>
        <h3 className={styles.title}>Chat</h3>
        <div className={styles.tools}>
          <button
            className={`${styles.speakerBtn} ${isSpeakerOn ? styles.active : ''}`}
            onClick={onToggleSpeaker}
            title="Speaker"
          >
            🔊
          </button>
          <div className={styles.modeToggle}>
            <span className={styles.pauseIcon}>⏸</span>
            <span className={styles.modeLabel}>{audioMode === AudioMode.MANUAL ? 'Manual' : 'Auto'}</span>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className={styles.messages}>
        {messages.length === 0 && (
          <div className={styles.emptyState}>
            <div className={styles.emptyIcon}>👋</div>
            <div className={styles.emptyText}>Start a conversation!</div>
          </div>
        )}

        {messages.map(message => (
          <MessageBubble
            key={message.id}
            content={message.content}
            isUser={message.isUser}
            onPlayAudio={!message.isUser ? () => onPlayAudio(message.content) : undefined}
            isPlayingAudio={isPlayingAudio && !message.isUser}
          />
        ))}

        {isLoading && (
          <div className={styles.typing}>
            <span className={styles.dot} />
            <span className={styles.dot} />
            <span className={styles.dot} />
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className={styles.inputArea}>
        <input
          ref={inputRef}
          type="text"
          value={inputValue}
          onChange={e => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type a message..."
          className={styles.input}
          disabled={isLoading}
        />

        <button
          className={`${styles.micBtn} ${isRecording ? styles.recording : ''}`}
          onClick={isRecording ? onStopRecording : onStartRecording}
          title={isRecording ? 'Stop recording' : 'Start recording'}
          disabled={isLoading}
        >
          🎤
        </button>

        <button
          className={styles.sendBtn}
          onClick={handleSend}
          disabled={!inputValue.trim() || isLoading}
          title="Send message"
        >
          Send
        </button>
      </div>
    </div>
  );
};
