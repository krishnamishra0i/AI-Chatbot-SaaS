// src/components/MessageBubble.tsx
import React from 'react';
import styles from './MessageBubble.module.css';

interface MessageBubbleProps {
  content: string;
  isUser: boolean;
  onPlayAudio?: () => void;
  isPlayingAudio?: boolean;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({
  content,
  isUser,
  onPlayAudio,
  isPlayingAudio,
}) => {
  return (
    <div className={`${styles.message} ${styles[isUser ? 'user' : 'bot']}`}>
      <div className={styles.bubble}>
        {content}
      </div>
      {!isUser && onPlayAudio && (
        <button
          className={styles.playButton}
          onClick={onPlayAudio}
          title="Play message"
          disabled={isPlayingAudio}
        >
          {isPlayingAudio ? (
            <span className={styles.spinner}>🔊</span>
          ) : (
            '🔊'
          )}
        </button>
      )}
    </div>
  );
};
