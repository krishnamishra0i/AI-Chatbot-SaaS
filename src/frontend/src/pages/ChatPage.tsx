// src/pages/ChatPage.tsx
import React from 'react';
import { ModernChatbot } from '../components/ModernChatbot';

export const ChatPage: React.FC = () => {
  return (
    <ModernChatbot
      apiBaseUrl="http://localhost:8001"
      botName="AI Assistant"
      botAvatar="🤖"
    />
  );
};
