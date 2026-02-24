import React from 'react';
import './AvatarChatPage.css';
import VideoAvatarChat from '../components/VideoAvatarChat';

const AvatarChatPage: React.FC = () => {
  return (
    <div className="avatar-chat-page">
      <VideoAvatarChat 
        apiUrl="http://localhost:8000"
        avatarName="Ambassador Paul"
        avatarImage="/images/paulmichael.png"
      />
    </div>
  );
};

export default AvatarChatPage;
