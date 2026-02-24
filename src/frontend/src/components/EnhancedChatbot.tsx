// src/components/EnhancedChatbot.tsx
import React, { useState, useRef, useEffect } from 'react';
import { useChatbot } from '../hooks/useChatbot';
import { Message, AudioMode } from '../types/chatbot';
import styles from './EnhancedChatbot.module.css';

interface EnhancedChatbotProps {
  apiBaseUrl: string;
  botName?: string;
  botAvatar?: string;
}

const QUICK_REPLIES = [
  "Help me understand",
  "Tell me more",
  "Great! What's next?",
  "How does this work?",
  "Can you explain?",
  "I'd like to know more",
];

type Theme = 'light' | 'dark' | 'ocean' | 'sunset';

export const EnhancedChatbot: React.FC<EnhancedChatbotProps> = ({
  apiBaseUrl,
  botName = 'Ambassador Paul',
  botAvatar = '👨‍💼',
}) => {
  const [inputValue, setInputValue] = useState('');
  const [showSettings, setShowSettings] = useState(false);
  const [theme, setTheme] = useState<Theme>('light');
  const [fontSize, setFontSize] = useState<'small' | 'medium' | 'large'>('medium');
  const [isTyping, setIsTyping] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [reactions, setReactions] = useState<{ [key: string]: string }>({});
  
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
  }, [messages, isLoading]);

  // Simulate typing indicator
  useEffect(() => {
    if (isLoading) {
      setIsTyping(true);
    } else {
      setIsTyping(false);
    }
  }, [isLoading]);

  // Handle sending message
  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return;
    await sendMessage(inputValue);
    setInputValue('');
    inputRef.current?.focus();
  };

  const handleQuickReply = async (reply: string) => {
    setInputValue(reply);
    setTimeout(() => {
      setInputValue('');
      sendMessage(reply).then(() => {
        inputRef.current?.focus();
      });
    }, 100);
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !isLoading && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleMicClick = async () => {
    if (isRecording) {
      await stopRecording();
    } else {
      await startRecording();
    }
  };

  const copyToClipboard = (text: string, messageId: string) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopiedId(messageId);
      setTimeout(() => setCopiedId(null), 2000);
    });
  };

  const addReaction = (messageId: string, emoji: string) => {
    setReactions(prev => ({
      ...prev,
      [messageId]: prev[messageId] === emoji ? '' : emoji
    }));
  };

  const clearChat = () => {
    if (window.confirm('Are you sure you want to clear the conversation?')) {
      // Reset messages if your hook supports it
      window.location.reload();
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
    <div className={`${styles.container} ${styles[`theme-${theme}`]} ${styles[`font-${fontSize}`]}`}>
      {/* Header */}
      <div className={styles.header}>
        <div className={styles.headerContent}>
          <div className={styles.botInfo}>
            <div className={styles.botAvatar}>{botAvatar}</div>
            <div className={styles.botDetails}>
              <h1 className={styles.botName}>{botName}</h1>
              <p className={styles.botStatus}>
                {isLoading ? '⌛ Thinking...' : isRecording ? '🎙️ Recording...' : '✓ Ready to help'}
              </p>
            </div>
          </div>
          <div className={styles.headerActions}>
            <button
              className={`${styles.headerBtn} ${isSpeakerOn ? styles.active : ''}`}
              onClick={() => setIsSpeakerOn(!isSpeakerOn)}
              title={isSpeakerOn ? 'Mute audio responses' : 'Enable audio responses'}
            >
              {isSpeakerOn ? '🔊' : '🔇'}
            </button>
            <button
              className={`${styles.headerBtn} ${showSettings ? styles.active : ''}`}
              onClick={() => setShowSettings(!showSettings)}
              title="Settings"
            >
              ⚙️
            </button>
          </div>
        </div>
      </div>

      {/* Settings Panel */}
      {showSettings && (
        <div className={styles.settingsPanel}>
          <div className={styles.settingsHeader}>
            <h3>Settings</h3>
            <button className={styles.closeBtn} onClick={() => setShowSettings(false)}>×</button>
          </div>
          
          <div className={styles.settingSection}>
            <label className={styles.settingLabel}>Theme</label>
            <div className={styles.themeButtons}>
              {(['light', 'dark', 'ocean', 'sunset'] as Theme[]).map(t => (
                <button
                  key={t}
                  className={`${styles.themeBtn} ${theme === t ? styles.active : ''}`}
                  onClick={() => setTheme(t)}
                  title={`Switch to ${t} theme`}
                >
                  {t === 'light' && '☀️'}
                  {t === 'dark' && '🌙'}
                  {t === 'ocean' && '🌊'}
                  {t === 'sunset' && '🌅'}
                </button>
              ))}
            </div>
          </div>

          <div className={styles.settingSection}>
            <label className={styles.settingLabel}>Font Size</label>
            <div className={styles.sizeButtons}>
              {(['small', 'medium', 'large'] as const).map(size => (
                <button
                  key={size}
                  className={`${styles.sizeBtn} ${fontSize === size ? styles.active : ''}`}
                  onClick={() => setFontSize(size)}
                >
                  {size.charAt(0).toUpperCase()}
                </button>
              ))}
            </div>
          </div>

          <div className={styles.settingSection}>
            <label>
              <input
                type="checkbox"
                checked={isSpeakerOn}
                onChange={(e) => setIsSpeakerOn(e.target.checked)}
              />
              <span className={styles.checkLabel}>Auto-play voice responses</span>
            </label>
          </div>

          <button className={styles.clearBtn} onClick={clearChat}>
            🗑️ Clear Conversation
          </button>
        </div>
      )}

      {/* Messages Area */}
      <div className={styles.messagesContainer}>
        {messages.length === 0 ? (
          <div className={styles.emptyState}>
            <div className={styles.emptyIcon}>🎯</div>
            <h2>Welcome to {botName}</h2>
            <p>Start a conversation or try a quick reply below</p>
            <div className={styles.quickRepliesEmpty}>
              {QUICK_REPLIES.slice(0, 3).map(reply => (
                <button
                  key={reply}
                  className={styles.quickReplyBtn}
                  onClick={() => handleQuickReply(reply)}
                >
                  {reply}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className={styles.messagesList}>
            {messages.map((msg: Message) => (
              <React.Fragment key={msg.id}>
                <div className={`${styles.messageRow} ${msg.isUser ? styles.userRow : styles.botRow}`}>
                  <div className={styles.messageGroup}>
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
                    
                    {/* Message actions */}
                    {!msg.isUser && (
                      <div className={styles.messageActions}>
                        <button
                          className={styles.actionBtn}
                          onClick={() => copyToClipboard(msg.content, msg.id)}
                          title="Copy message"
                        >
                          {copiedId === msg.id ? '✓' : '📋'}
                        </button>
                        <div className={styles.reactionMenu}>
                          {['👍', '❤️', '😂', '🤔', '🚀'].map(emoji => (
                            <button
                              key={emoji}
                              className={`${styles.reactionBtn} ${reactions[msg.id] === emoji ? styles.active : ''}`}
                              onClick={() => addReaction(msg.id, emoji)}
                              title={`React with ${emoji}`}
                            >
                              {emoji}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
                
                {/* Reaction display */}
                {reactions[msg.id] && (
                  <div className={styles.reactionDisplay}>
                    {reactions[msg.id]}
                  </div>
                )}
              </React.Fragment>
            ))}

            {isTyping && (
              <div className={`${styles.messageRow} ${styles.botRow}`}>
                <div className={styles.messageBubble} data-role="bot">
                  <div className={styles.typingIndicator}>
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

      {/* Quick Replies */}
      {messages.length > 0 && !isLoading && (
        <div className={styles.quickReplies}>
          <div className={styles.quickRepliesLabel}>Quick replies:</div>
          <div className={styles.quickRepliesContainer}>
            {QUICK_REPLIES.map(reply => (
              <button
                key={reply}
                className={styles.quickReplyBtn}
                onClick={() => handleQuickReply(reply)}
              >
                {reply}
              </button>
            ))}
          </div>
        </div>
      )}

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

        {isRecording && (
          <div className={styles.recordingHint}>
            🎙️ Recording in progress... Speak now or click button to stop
          </div>
        )}
      </div>
    </div>
  );
};
