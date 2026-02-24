import React, { useEffect, useRef, useState } from 'react';
import { Volume2, VolumeX, Send, Mic, MicOff, AlertCircle, Loader } from 'lucide-react';

interface Message {
  id: number;
  text: string;
  isUser: boolean;
  timestamp: Date;
}

interface VideoStatus {
  status: string;
  talk_id?: string;
  video_url?: string;
  message?: string;
  progress?: string;
  error?: string;
}

interface RealTimeAvatarProps {
  apiBaseUrl: string;
  avatarImageUrl?: string;
}

const RealTimeAvatar: React.FC<RealTimeAvatarProps> = ({
  apiBaseUrl,
  avatarImageUrl = 'https://api.d-id.com/example-image.jpg',
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [speakerOn, setSpeakerOn] = useState(true);
  const [currentVideoUrl, setCurrentVideoUrl] = useState<string | null>(null);
  const [videoStatus, setVideoStatus] = useState<VideoStatus | null>(null);
  const [apiKey, setApiKey] = useState('');
  const [showApiKeyInput, setShowApiKeyInput] = useState(true);
  const [recordingTime, setRecordingTime] = useState(0);

  const videoRef = useRef<HTMLVideoElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const recordingIntervalRef = useRef<number | null>(null);
  const audioRef = useRef<HTMLAudioElement>(null);

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Initialize Web Speech API
  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onresult = (event: any) => {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          if (event.results[i].isFinal) {
            transcript += event.results[i][0].transcript + ' ';
          }
        }
        if (transcript) {
          setInputValue(transcript.trim());
        }
      };

      (window as any).speechRecognition = recognition;
    }
  }, []);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const chunks: Blob[] = [];

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) chunks.push(event.data);
      };

      recorder.onstop = async () => {
        const audioBlob = new Blob(chunks, { type: 'audio/wav' });
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.wav');

        try {
          const response = await fetch(`${apiBaseUrl}/api/stt/transcribe`, {
            method: 'POST',
            body: formData,
          });
          const data = await response.json();
          if (data.text) {
            setInputValue(data.text);
            setTimeout(() => sendMessage(data.text), 100);
          }
        } catch (error) {
          console.error('STT error:', error);
        }
      };

      mediaRecorderRef.current = recorder;
      recorder.start();
      setIsRecording(true);
      setRecordingTime(0);

      const timer = setInterval(() => {
        setRecordingTime((prev) => prev + 1);
      }, 1000);
      recordingIntervalRef.current = timer;
    } catch (error) {
      console.error('Recording error:', error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach((track) => track.stop());
      setIsRecording(false);

      if (recordingIntervalRef.current) {
        clearInterval(recordingIntervalRef.current);
      }
    }
  };

  const sendMessage = async (text: string = inputValue) => {
    if (!text.trim()) return;
    if (!apiKey) {
      alert('Please enter your D-ID API key first');
      return;
    }

    setInputValue('');
    const userMessage: Message = {
      id: Date.now(),
      text,
      isUser: true,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setVideoStatus(null);

    try {
      // Set D-ID API key in environment (in real scenario, this would be server-side)
      // process.env.REACT_APP_D_ID_API_KEY = apiKey;

      const response = await fetch(`${apiBaseUrl}/api/avatar/chat-with-avatar`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-D-ID-API-Key': apiKey,
        },
        body: JSON.stringify({
          message: text,
          avatar_image_url: avatarImageUrl,
          stream: true,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error('No response body');

      let botResponse = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = new TextDecoder().decode(value);
        const lines = chunk.split('\n').filter((line) => line.trim());

        for (const line of lines) {
          try {
            const data = JSON.parse(line);

            if (data.type === 'text_response') {
              botResponse = data.text;
            } else if (data.type === 'video_status') {
              setVideoStatus(data);

              if (data.status === 'done' && data.video_url) {
                setCurrentVideoUrl(data.video_url);
                const botMessage: Message = {
                  id: Date.now() + 1,
                  text: botResponse,
                  isUser: false,
                  timestamp: new Date(),
                };
                setMessages((prev) => [...prev, botMessage]);

                // Auto-play video if speaker is on
                if (speakerOn && videoRef.current) {
                  setTimeout(() => {
                    videoRef.current?.play().catch((e) => console.log('Autoplay blocked:', e));
                  }, 500);
                }
              } else if (data.status === 'failed' || data.status === 'error') {
                const errorMessage: Message = {
                  id: Date.now() + 2,
                  text: `Error: ${data.message || 'Failed to generate avatar response'}`,
                  isUser: false,
                  timestamp: new Date(),
                };
                setMessages((prev) => [...prev, errorMessage]);
              }
            }
          } catch (e) {
            // Ignore JSON parsing errors
          }
        }
      }
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: Message = {
        id: Date.now() + 3,
        text: `Error: ${error instanceof Error ? error.message : 'Unknown error'}. Make sure D-ID API key is configured.`,
        isUser: false,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  if (showApiKeyInput) {
    return (
      <div className="w-screen h-screen bg-gradient-to-br from-purple-600 to-blue-600 flex items-center justify-center">
        <div className="bg-white p-8 rounded-2xl shadow-2xl max-w-md w-full">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">D-ID Avatar Chatbot</h1>
          <p className="text-gray-600 mb-6">Enter your D-ID API Key to get started</p>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                D-ID API Key
              </label>
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="Enter your D-ID API key"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && apiKey) {
                    setShowApiKeyInput(false);
                  }
                }}
              />
              <p className="text-xs text-gray-500 mt-2">
                Get your API key from <a href="https://www.d-id.com" target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">d-id.com</a>
              </p>
            </div>

            <button
              onClick={() => apiKey && setShowApiKeyInput(false)}
              disabled={!apiKey}
              className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white font-bold py-3 rounded-lg transition"
            >
              Connect to D-ID
            </button>
          </div>

          <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
            <p className="text-xs text-blue-700">
              <strong>Note:</strong> Your API key is stored locally in your browser. Never share it with anyone.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-screen h-screen bg-gray-900 flex">
      <audio ref={audioRef} style={{ display: 'none' }} />

      {/* Avatar Video Section */}
      <div className="w-1/2 bg-black flex flex-col items-center justify-center relative overflow-hidden">
        {currentVideoUrl ? (
          <>
            <video
              ref={videoRef}
              src={currentVideoUrl}
              controls
              className="w-full h-full object-contain"
            />
            <div className="absolute top-4 right-4 bg-green-500 text-white px-3 py-1 rounded-full text-sm font-semibold">
              ✓ D-ID Avatar
            </div>
          </>
        ) : (
          <div className="text-center">
            <div className="inline-block p-8 bg-purple-500 rounded-full mb-4">
              <div className="w-32 h-32 bg-gray-600 rounded-full flex items-center justify-center">
                <svg className="w-16 h-16 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm3.5-9c.83 0 1.5-.67 1.5-1.5S16.33 8 15.5 8 14 8.67 14 9.5s.67 1.5 1.5 1.5zm-7 0c.83 0 1.5-.67 1.5-1.5S9.33 8 8.5 8 7 8.67 7 9.5 7.67 11 8.5 11zm3.5 6.5c2.33 0 4.31-1.46 5.11-3.5H6.89c.8 2.04 2.78 3.5 5.11 3.5z" />
                </svg>
              </div>
            </div>
            <h2 className="text-gray-400 text-xl font-semibold mb-2">Ready for Avatar Response</h2>
            <p className="text-gray-500">Send a message and the avatar will respond</p>

            {videoStatus && (
              <div className="mt-6 text-sm text-gray-400">
                <p>{videoStatus.message}</p>
              </div>
            )}

            {isLoading && <Loader className="w-8 h-8 text-purple-500 animate-spin mt-4 mx-auto" />}
          </div>
        )}
      </div>

      {/* Chat Section */}
      <div className="w-1/2 bg-gray-800 flex flex-col">
        {/* Header */}
        <div className="border-b border-gray-700 px-6 py-4 flex justify-between items-center bg-gray-750">
          <div>
            <h1 className="text-xl font-bold text-white">D-ID Avatar Chat</h1>
            <p className="text-xs text-gray-400">Real-time AI Avatar Responses</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => setSpeakerOn(!speakerOn)}
              className={`p-2 rounded-lg transition ${
                speakerOn ? 'bg-purple-600 text-white' : 'bg-gray-700 text-gray-400'
              }`}
            >
              {speakerOn ? <Volume2 size={20} /> : <VolumeX size={20} />}
            </button>
            <button
              onClick={() => {
                setShowApiKeyInput(true);
                setApiKey('');
              }}
              className="text-xs bg-red-600 hover:bg-red-700 text-white px-3 py-2 rounded-lg"
            >
              Change API Key
            </button>
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 && (
            <div className="flex items-center justify-center h-full text-gray-500">
              <div className="text-center">
                <h3 className="text-lg font-semibold mb-2">Start a conversation</h3>
                <p className="text-sm">Type a message or use speech-to-text</p>
              </div>
            </div>
          )}

          {messages.map((msg) => (
            <div key={msg.id} className={`flex ${msg.isUser ? 'justify-end' : 'justify-start'}`}>
              <div
                className={`max-w-xs px-4 py-3 rounded-lg ${
                  msg.isUser
                    ? 'bg-purple-600 text-white rounded-br-none'
                    : 'bg-gray-700 text-gray-100 rounded-bl-none'
                }`}
              >
                <p className="text-sm break-words">{msg.text}</p>
                <p className="text-xs opacity-70 mt-1">
                  {msg.timestamp.toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))}

          {videoStatus && videoStatus.status === 'processing' && (
            <div className="flex justify-center">
              <div className="bg-gray-700 px-4 py-2 rounded-lg text-gray-300 text-sm flex items-center gap-2">
                <Loader size={16} className="animate-spin" />
                Generating avatar video...
              </div>
            </div>
          )}

          {videoStatus && (videoStatus.status === 'error' || videoStatus.status === 'failed') && (
            <div className="flex justify-center">
              <div className="bg-red-900 px-4 py-2 rounded-lg text-red-200 text-sm flex items-center gap-2">
                <AlertCircle size={16} />
                {videoStatus.message}
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-700 p-4 bg-gray-750">
          {recordingTime > 0 && isRecording && (
            <div className="text-center text-sm text-orange-500 mb-2 font-semibold">
              🎙️ Recording: {recordingTime}s
            </div>
          )}
          <div className="flex gap-2">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter') sendMessage();
              }}
              placeholder="Type a message..."
              disabled={isLoading}
              className="flex-1 px-4 py-3 rounded-lg bg-gray-700 border border-gray-600 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
            />

            <button
              onClick={() => (isRecording ? stopRecording() : startRecording())}
              className={`p-3 rounded-lg transition ${
                isRecording
                  ? 'bg-red-600 hover:bg-red-700 text-white'
                  : 'bg-gray-700 hover:bg-gray-600 text-gray-300'
              }`}
            >
              {isRecording ? <MicOff size={20} /> : <Mic size={20} />}
            </button>

            <button
              onClick={() => sendMessage()}
              disabled={isLoading || !inputValue.trim()}
              className="px-6 py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-700 text-white rounded-lg transition font-semibold"
            >
              <Send size={20} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RealTimeAvatar;
