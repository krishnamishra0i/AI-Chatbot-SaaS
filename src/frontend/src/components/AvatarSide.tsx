// src/components/AvatarSide.tsx
import React from 'react';
import styles from './AvatarSide.module.css';

interface AvatarSideProps {
  botName: string;
  avatarImage?: string;
  isRecording: boolean;
  recordingDuration: number;
  isSpeakerOn: boolean;
  onToggleSpeaker: () => void;
  onToggleMic: () => void;
  onToggleChat: () => void;
  onClose: () => void;
}

export const AvatarSide: React.FC<AvatarSideProps> = ({
  botName,
  avatarImage,
  isRecording,
  recordingDuration,
  isSpeakerOn,
  onToggleSpeaker,
  onToggleMic,
  onToggleChat,
  onClose,
}) => {
  return (
    <div className={styles.avatar}>
      {/* Top Control Buttons Row */}
      <div className={styles.topControls}>
        <button
          className={`${styles.controlBtn} ${styles.speakBtn}`}
          onClick={onToggleMic}
          title={isRecording ? 'Stop Speaking' : 'Start Speaking'}
        >
          S
        </button>
        
        <button
          className={`${styles.controlBtn} ${styles.speakerBtn} ${isSpeakerOn ? styles.active : ''}`}
          onClick={onToggleSpeaker}
          title="Toggle Speaker"
        >
          🔊
        </button>

        <button className={`${styles.controlBtn} ${styles.expandBtn}`} title="Expand">
          ⤢
        </button>
        
        <button className={`${styles.controlBtn} ${styles.closeBtn}`} onClick={onClose} title="Close">
          ✕
        </button>
      </div>

      {/* Avatar Image */}
      <div className={styles.avatarContainer}>
        {avatarImage ? (
          <img src={avatarImage} alt="Bot Avatar" className={styles.avatarImage} />
        ) : (
          <div className={styles.avatarPlaceholder}>Avatar</div>
        )}
        
        {isRecording && (
          <div className={styles.recordingIndicator}>
            <span className={styles.recordingDot}></span>
            <span className={styles.recordingTime}>{recordingDuration}s</span>
          </div>
        )}
      </div>

      {/* Bot Name */}
      <div className={styles.botName}>{botName}</div>

      {/* Bottom Control Buttons Row */}
      <div className={styles.bottomControls}>
        <button
          className={`${styles.controlBtn} ${styles.micBtn} ${isRecording ? styles.active : ''}`}
          onClick={onToggleMic}
          title="Microphone"
        >
          🎤
        </button>
        
        <button className={`${styles.controlBtn} ${styles.chatBtn}`} onClick={onToggleChat} title="Chat">
          💬
        </button>
      </div>
    </div>
  );
};
