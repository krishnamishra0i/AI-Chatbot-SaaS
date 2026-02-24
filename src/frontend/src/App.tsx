// src/App.tsx
import { useState } from 'react';
import FloatingAvatarChatbot from './components/FloatingAvatarChatbot';
import RealTimeAvatar from './components/RealTimeAvatar';
import AvatarChatPage from './pages/AvatarChatPage';
import './App.css';

function App() {
  const [mode, setMode] = useState<'select' | 'split-screen' | 'd-id' | 'video-avatar'>('video-avatar');
  
  const config = {
    apiBaseUrl: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8001',
    botName: 'Ambassador Paul',
  };

  if (mode === 'video-avatar') {
    return <AvatarChatPage />;
  }

  if (mode === 'split-screen') {
    return (
      <div className="App">
        <FloatingAvatarChatbot
          apiBaseUrl={config.apiBaseUrl}
          botName={config.botName}
        />
        <button
          onClick={() => setMode('select')}
          className="fixed top-4 left-4 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg z-50"
        >
          ← Back
        </button>
      </div>
    );
  }

  if (mode === 'd-id') {
    return (
      <div className="App">
        <RealTimeAvatar
          apiBaseUrl={config.apiBaseUrl}
        />
      </div>
    );
  }

  // Selection screen
  return (
    <div className="w-screen h-screen bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center">
      <div className="max-w-2xl">
        <h1 className="text-5xl font-bold text-white mb-4 text-center">AI Avatar Chatbot</h1>
        <p className="text-xl text-blue-100 text-center mb-12">Choose your chatbot experience</p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Split Screen Mode */}
          <div
            onClick={() => setMode('split-screen')}
            className="bg-white rounded-2xl shadow-2xl p-8 cursor-pointer hover:shadow-3xl hover:scale-105 transition transform"
          >
            <div className="mb-6">
              <div className="w-16 h-16 bg-gradient-to-br from-rose-400 to-pink-300 rounded-full flex items-center justify-center text-3xl mx-auto">
                👤
              </div>
            </div>
            <h2 className="text-2xl font-bold text-gray-800 mb-3 text-center">Split Screen Chat</h2>
            <p className="text-gray-600 text-center mb-4">
              Avatar on left, chat panel on right. Clean and professional interface.
            </p>
            <ul className="text-sm text-gray-600 space-y-2 mb-6">
              <li>✓ Text & Voice chat</li>
              <li>✓ Real-time responses</li>
              <li>✓ Knowledge base integration</li>
              <li>✓ Simple, clean design</li>
            </ul>
            <button className="w-full bg-rose-500 hover:bg-rose-600 text-white font-bold py-3 rounded-lg transition">
              Start Chat →
            </button>
          </div>

          {/* D-ID Real-time Avatar Mode */}
          <div
            onClick={() => setMode('d-id')}
            className="bg-white rounded-2xl shadow-2xl p-8 cursor-pointer hover:shadow-3xl hover:scale-105 transition transform"
          >
            <div className="mb-6">
              <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center text-3xl mx-auto">
                🎬
              </div>
            </div>
            <h2 className="text-2xl font-bold text-gray-800 mb-3 text-center">D-ID Real-time Avatar</h2>
            <p className="text-gray-600 text-center mb-4">
              Animated avatar video responses. Professional AI avatar that speaks to you.
            </p>
            <ul className="text-sm text-gray-600 space-y-2 mb-6">
              <li>✓ Animated avatar video</li>
              <li>✓ Real-time speech synthesis</li>
              <li>✓ Professional appearance</li>
              <li>✓ Requires D-ID API key</li>
            </ul>
            <button className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 rounded-lg transition">
              Start D-ID Chat →
            </button>
          </div>
        </div>

        <p className="text-center text-blue-100 text-sm mt-12">
          💡 Tip: Get your D-ID API key at <a href="https://www.d-id.com" target="_blank" rel="noopener noreferrer" className="underline hover:text-white">d-id.com</a>
        </p>
      </div>
    </div>
  );
}

export default App;
