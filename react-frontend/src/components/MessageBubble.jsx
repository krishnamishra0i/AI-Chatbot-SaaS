// Message Bubble Component - Display individual messages
import React, { useState } from 'react';
import { ttsService } from '../utils/ttsService';

const MessageBubble = ({ message, isUser, onPlayAudio }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [error, setError] = useState(null);

  const handlePlayAudio = async () => {
    if (isUser) return; // Only AI messages have audio
    
    setIsPlaying(true);
    setError(null);
    
    try {
      await ttsService.speak(message.content);
      if (onPlayAudio) onPlayAudio(message.id);
    } catch (err) {
      setError('Failed to play audio');
      console.error('TTS Error:', err);
    } finally {
      setIsPlaying(false);
    }
  };

  return (
    <div className={`flex gap-4 mb-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[70%] rounded-lg p-4 ${
          isUser
            ? 'bg-secondary text-white rounded-br-none'
            : 'bg-surface-container text-on-surface rounded-bl-none shadow-md'
        }`}
      >
        <p className="text-sm leading-relaxed whitespace-pre-wrap break-words">
          {message.content}
        </p>
        
        {/* Message metadata */}
        <div className={`text-xs mt-2 flex items-center gap-2 ${
          isUser ? 'text-white/70' : 'text-on-surface-variant'
        }`}>
          {message.created_at && (
            <span>{new Date(message.created_at).toLocaleTimeString([], { 
              hour: '2-digit', 
              minute: '2-digit' 
            })}</span>
          )}
          {message.tokens && (
            <span>•</span>
          )}
          {message.tokens && (
            <span>{message.tokens} tokens</span>
          )}
        </div>

        {/* TTS Button for AI messages */}
        {!isUser && (
          <button
            onClick={handlePlayAudio}
            disabled={isPlaying}
            className={`mt-3 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold transition-all ${
              isPlaying
                ? 'bg-white/20 text-white cursor-wait'
                : 'bg-white/10 hover:bg-white/20 text-white active:scale-95'
            }`}
            title="Play audio response (TTS)"
          >
            <span className="material-symbols-outlined text-sm">
              {isPlaying ? 'volume_2' : 'volume_up'}
            </span>
            {isPlaying ? 'Playing...' : 'Listen'}
          </button>
        )}

        {error && (
          <p className="text-xs text-red-300 mt-2">{error}</p>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;
