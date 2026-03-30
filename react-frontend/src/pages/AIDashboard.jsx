// Main Dashboard Component - AI Solutions Hub
import React, { useState, useRef } from 'react';
import AILayout from './AILayout';
import OverviewPage from './OverviewPage';
import ChatbotsPage from './ChatbotsPage';
import APIKeysPage from './APIKeysPage';
import UsageAnalyticsPage from './UsageAnalyticsPage';
import CreateChatbotModal from './CreateChatbotModal';
import '../styles/AITheme.css';

const API_BASE_URL = (process.env.REACT_APP_API_URL || 'http://localhost:5001').replace(/\/api\/?$/, '');
const FALLBACK_API_BASE_URL = API_BASE_URL.includes(':5000')
  ? API_BASE_URL.replace(':5000', ':5001')
  : API_BASE_URL.includes(':5001')
  ? API_BASE_URL.replace(':5001', ':5000')
  : null;

const getStoredToken = () =>
  localStorage.getItem('athena_token') ||
  localStorage.getItem('token') ||
  localStorage.getItem('accessToken');

const fetchWithPortFallback = async (path, options) => {
  try {
    return await fetch(`${API_BASE_URL}${path}`, options);
  } catch (error) {
    if (!FALLBACK_API_BASE_URL) {
      throw error;
    }
    console.warn('Primary API unreachable, retrying with fallback:', {
      primary: API_BASE_URL,
      fallback: FALLBACK_API_BASE_URL,
      path,
    });
    return await fetch(`${FALLBACK_API_BASE_URL}${path}`, options);
  }
};

const AIDashboard = ({ onNavigate }) => {
  const [currentTab, setCurrentTab] = useState('overview');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [creatingChatbot, setCreatingChatbot] = useState(false);
  const chatbotsPageRef = useRef(null);

  const handleCreateChatbot = async (formData) => {
    setCreatingChatbot(true);
    try {
      const token = getStoredToken();
      if (!token) {
        alert('Error: Not authenticated. Please log in first.');
        return;
      }

      const response = await fetchWithPortFallback('/api/chatbots/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create chatbot');
      }

      const newChatbot = await response.json();
      console.log('✅ Chatbot created successfully:', newChatbot);
      
      // Show success message
      alert(`✅ Chatbot "${formData.name}" created successfully!`);
      
      // Close modal
      setShowCreateModal(false);
      
      // Refresh chatbots list if callback available
      if (chatbotsPageRef.current?.refreshChatbots) {
        chatbotsPageRef.current.refreshChatbots();
      }
      
      // Switch to chatbots tab to show new bot
      setCurrentTab('chatbots');
    } catch (error) {
      console.error('❌ Error creating chatbot:', error);
      const isConnectionError = error?.message === 'Failed to fetch';
      const message = isConnectionError
        ? `Backend not reachable at ${API_BASE_URL}. Start backend server and try again.`
        : error.message;
      alert(`❌ Error: ${message}`);
    } finally {
      setCreatingChatbot(false);
    }
  };

  const renderContent = () => {
    switch (currentTab) {
      case 'overview':
        return <OverviewPage />;
      case 'chatbots':
        return <ChatbotsPage ref={chatbotsPageRef} onCreateNew={() => setShowCreateModal(true)} />;
      case 'api-keys':
        return <APIKeysPage />;
      case 'usage':
        return <UsageAnalyticsPage />;
      default:
        return <OverviewPage />;
    }
  };

  return (
    <AILayout currentTab={currentTab} setCurrentTab={setCurrentTab} onNavigate={onNavigate}>
      {renderContent()}

      {/* Create Chatbot Modal */}
      <CreateChatbotModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onCreate={handleCreateChatbot}
      />
    </AILayout>
  );
};

export default AIDashboard;
