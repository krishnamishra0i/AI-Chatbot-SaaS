// src/components/AdvancedChatbot.tsx
import React, { useState } from 'react';
import { AvatarSide } from './AvatarSide';
import { ChatPanel } from './ChatPanel';
import { useChatbot } from '../hooks/useChatbot';
import { ChatbotConfig } from '../types/chatbot';
import styles from './AdvancedChatbot.module.css';

interface AdvancedChatbotProps extends ChatbotConfig {}

export const AdvancedChatbot: React.FC<AdvancedChatbotProps> = ({
  apiBaseUrl,
  botName,
  avatarImage,
  position = { bottom: '20px', right: '20px' },
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);

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

  // Handle recording timer
  // Timer is managed by the hook, no additional logic needed here

  return (
    <div className={styles.root} style={{ bottom: position.bottom, right: position.right }}>
      {/* Teaser Button */}
      {!isOpen && (
        <button
          className={styles.teaser}
          onClick={() => setIsOpen(true)}
          title="Open chatbot"
        >
          {avatarImage ? (
            <img src={avatarImage} alt={botName} />
          ) : (
            <div className={styles.defaultAvatar}>👤</div>
          )}
        </button>
      )}

      {/* Modal */}
      {isOpen && (
        <div className={styles.modal}>
          <div className={styles.container}>
            {/* Avatar Side */}
            <AvatarSide
              botName={botName}
              avatarImage={avatarImage}
              isRecording={isRecording}
              recordingDuration={recordingDuration}
              isSpeakerOn={isSpeakerOn}
              onToggleSpeaker={() => setIsSpeakerOn(!isSpeakerOn)}
              onToggleMic={isRecording ? stopRecording : startRecording}
              onToggleChat={() => setIsChatOpen(!isChatOpen)}
              onClose={() => setIsOpen(false)}
            />

            {/* Chat Side */}
            {isChatOpen && (
              <ChatPanel
                messages={messages}
                isLoading={isLoading}
                isSpeakerOn={isSpeakerOn}
                audioMode={audioMode}
                isRecording={isRecording}
                isPlayingAudio={isPlayingAudio}
                onSendMessage={sendMessage}
                onPlayAudio={playTTS}
                onToggleSpeaker={() => setIsSpeakerOn(!isSpeakerOn)}
                onStartRecording={startRecording}
                onStopRecording={stopRecording}
              />
            )}
          </div>
        </div>
      )}
    </div>
  );
};
