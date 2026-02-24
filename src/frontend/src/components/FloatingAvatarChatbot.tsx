import React, { useEffect, useRef, useState } from 'react';
import { Volume2, VolumeX, Maximize2, X, Mic, MicOff, Send, Loader } from 'lucide-react';

interface FloatingAvatarChatbotProps {
  apiBaseUrl: string;
  botName?: string;
}

interface ChatMessage {
  id: number;
  content: string;
  isUser: boolean;
  source?: string;
  usedKnowledgeBase?: boolean;
}

const FloatingAvatarChatbot: React.FC<FloatingAvatarChatbotProps> = ({
  apiBaseUrl,
  botName = 'Ambassador Paul',
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    { 
      id: 1, 
      content: `Hi, I'm ${botName}. How can I help you?`, 
      isUser: false 
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isSpeakerOn, setIsSpeakerOn] = useState(true);
  const [recordingDuration, setRecordingDuration] = useState(0);
  const [isGeneratingVoice, setIsGeneratingVoice] = useState(false);
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [autoPlayAudio] = useState(true);

  const audioRef = useRef<HTMLAudioElement>(null);
  const recognitionRef = useRef<any>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const recordingTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize Web Speech API
  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      console.warn('Speech Recognition not supported');
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onresult = (event: any) => {
      let finalTranscript = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalTranscript += transcript + ' ';
        }
      }
      if (finalTranscript) {
        setInputValue(finalTranscript.trim());
      }
    };

    recognitionRef.current = recognition;
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
    };
  }, []);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  // Send message to backend
  const handleSendMessage = async () => {
    if (inputValue.trim() === '') return;

    const userMessage: ChatMessage = {
      id: Date.now(),
      content: inputValue,
      isUser: true,
    };

    setMessages(prev => [...prev, userMessage]);
    const query = inputValue;
    setInputValue('');
    setIsTyping(true);

    try {
      // Use direct RAG endpoint (works without LLM!)
      const response = await fetch(`${apiBaseUrl}/api/chat/direct`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: query,
        }),
      });

      const data = await response.json();
      const botMessage: ChatMessage = {
        id: Date.now() + 1,
        content: data.response || "I couldn't understand that question.",
        isUser: false,
        usedKnowledgeBase: data.used_knowledge_base,
        source: data.used_knowledge_base ? 'knowledge_base' : 'general',
      };

      setMessages(prev => [...prev, botMessage]);
      setIsTyping(false);

      // Auto-play if enabled
      if ((isSpeakerOn || autoPlayAudio)) {
        generateVoiceFromText(data.response);
      }
    } catch (error) {
      console.error('Chat error:', error);
      setIsTyping(false);
      const errorMessage: ChatMessage = {
        id: Date.now() + 2,
        content: 'Sorry, something went wrong. Please try again.',
        isUser: false,
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  // Generate voice
  const generateVoiceFromText = async (text: string) => {
    if (!isSpeakerOn && !autoPlayAudio) return;

    try {
      setIsGeneratingVoice(true);
      setIsPlayingAudio(true);

      const response = await fetch(`${apiBaseUrl}/api/tts/synthesize-audio`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: text,
          voice: 'en-US-GuyNeural',
        }),
      });

      if (!response.ok) throw new Error('TTS failed');

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);

      if (audioRef.current) {
        audioRef.current.src = url;
        audioRef.current.onended = () => {
          setIsPlayingAudio(false);
          URL.revokeObjectURL(url);
        };
        audioRef.current.onerror = () => {
          setIsPlayingAudio(false);
        };
        audioRef.current.play().catch(err => {
          console.error('Audio play error:', err);
          setIsPlayingAudio(false);
        });
      }
    } catch (error) {
      console.error('TTS error:', error);
      setIsPlayingAudio(false);
    } finally {
      setIsGeneratingVoice(false);
    }
  };

  // Recording functions
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const chunks: Blob[] = [];

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) chunks.push(event.data);
      };

      recorder.onstart = () => {
        setIsRecording(true);
      };

      mediaRecorderRef.current = recorder;
      (recorder as any).audioChunks = chunks;
      recorder.start();

      setRecordingDuration(0);
      const timer = setInterval(() => {
        setRecordingDuration(prev => prev + 1);
      }, 1000);
      recordingTimerRef.current = timer;
    } catch (error) {
      console.error('Recording error:', error);
    }
  };

  const stopRecording = async () => {
    return new Promise<Blob>((resolve, reject) => {
      if (mediaRecorderRef.current && isRecording) {
        mediaRecorderRef.current.onstop = () => {
          setIsRecording(false);

          if (recordingTimerRef.current) {
            clearInterval(recordingTimerRef.current);
          }

          const chunks = (mediaRecorderRef.current as any)?.audioChunks || [];
          if (chunks.length > 0) {
            const audioBlob = new Blob(chunks, { type: 'audio/wav' });
            resolve(audioBlob);
          } else {
            reject(new Error('No audio recorded'));
          }
        };

        mediaRecorderRef.current.stop();
        mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      } else {
        reject(new Error('No active recording'));
      }
    });
  };

  const processAudioInput = async () => {
    try {
      const audioBlob = await stopRecording();

      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.wav');

      const response = await fetch(`${apiBaseUrl}/api/stt/transcribe`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      if (data.text) {
        setInputValue(data.text);
        setTimeout(() => {
          handleSendMessage();
        }, 100);
      }
    } catch (error) {
      console.error('STT error:', error);
    }
  };

  const toggleMic = async () => {
    if (isRecording) {
      await processAudioInput();
    } else {
      await startRecording();
    }
  };

  return (
    <div className="w-screen h-screen bg-white flex">
      <audio ref={audioRef} style={{ display: 'none' }} />

      {/* Left Side - Avatar */}
      <div className="w-1/2 bg-gradient-to-br from-rose-400 via-rose-300 to-pink-300 relative flex flex-col justify-between p-6">
        {/* Top Controls */}
        <div className="flex justify-end gap-3">
          <button 
            className="w-12 h-12 rounded-full bg-gray-700/80 hover:bg-gray-600 text-white flex items-center justify-center transition"
            title="Settings"
          >
            S
          </button>
          <button 
            onClick={() => setIsSpeakerOn(!isSpeakerOn)}
            className={`w-12 h-12 rounded-full flex items-center justify-center transition ${
              isSpeakerOn 
                ? 'bg-teal-500 hover:bg-teal-600' 
                : 'bg-gray-500 hover:bg-gray-600'
            } text-white`}
            title={isSpeakerOn ? 'Speaker on' : 'Speaker off'}
          >
            {isSpeakerOn ? <Volume2 size={24} /> : <VolumeX size={24} />}
          </button>
          <button 
            className="w-12 h-12 rounded-full bg-gray-700/80 hover:bg-gray-600 text-white flex items-center justify-center transition"
            title="Fullscreen"
          >
            <Maximize2 size={22} />
          </button>
          <button 
            className="w-12 h-12 rounded-full bg-red-500 hover:bg-red-600 text-white flex items-center justify-center transition"
            title="Close"
          >
            <X size={22} />
          </button>
        </div>

        {/* Avatar Image */}
        <div className="flex-1 flex items-center justify-center">
          <img 
            src="/images/paulmichael.png" 
            alt="Avatar" 
            className="w-80 h-96 object-cover rounded-2xl shadow-lg"
          />
        </div>

        {/* Bottom Section */}
        <div className="flex flex-col items-start gap-4">
          <h2 className="text-white text-3xl font-bold">{botName}</h2>
          
          {/* Microphone Controls */}
          <div className="flex gap-3">
            <button
              onClick={toggleMic}
              className={`w-14 h-14 rounded-full flex items-center justify-center transition text-white ${
                isRecording
                  ? 'bg-red-500 hover:bg-red-600 animate-pulse'
                  : 'bg-teal-500 hover:bg-teal-600'
              }`}
              title={isRecording ? 'Stop recording' : 'Start recording'}
            >
              {isRecording ? <MicOff size={24} /> : <Mic size={24} />}
            </button>
            <button
              className="w-14 h-14 rounded-full bg-green-500 hover:bg-green-600 text-white flex items-center justify-center transition"
              title="Record video"
            >
              <div className="w-5 h-5 border-2 border-white rounded"></div>
            </button>
          </div>

          {/* Recording Status */}
          {isRecording && (
            <div className="text-white text-sm">
              🎙️ Recording: {recordingDuration}s
            </div>
          )}
        </div>
      </div>

      {/* Right Side - Chat */}
      <div className="w-1/2 bg-white flex flex-col">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center">
          <h2 className="text-xl font-semibold text-gray-800">Chat</h2>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsSpeakerOn(!isSpeakerOn)}
              className={`w-10 h-10 rounded-full flex items-center justify-center transition ${
                isSpeakerOn
                  ? 'bg-red-500 hover:bg-red-600 text-white'
                  : 'bg-gray-300 hover:bg-gray-400'
              }`}
              title={isSpeakerOn ? 'Speaker on' : 'Speaker off'}
            >
              <Volume2 size={18} />
            </button>
            <div className="bg-gray-200 px-4 py-1 rounded-full text-sm font-medium text-gray-700 flex items-center gap-2">
              <span className="w-1.5 h-1.5 bg-gray-400 rounded-full"></span>
              {autoPlayAudio ? '🔊 Auto' : '⏸ Manual'}
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-gray-50">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-md px-6 py-3 rounded-3xl ${
                  message.isUser
                    ? 'bg-red-500 text-white rounded-3xl'
                    : 'bg-gray-200 text-gray-800'
                }`}
              >
                <p className="text-sm">{message.content}</p>
                {!message.isUser && message.usedKnowledgeBase && (
                  <div className="text-xs mt-2 pt-2 border-t border-gray-300 opacity-70">
                    📚 Knowledge Base
                  </div>
                )}
              </div>
              {!message.isUser && (
                <button
                  onClick={() => generateVoiceFromText(message.content)}
                  className="ml-3 w-10 h-10 rounded-full bg-blue-500 hover:bg-blue-600 text-white flex items-center justify-center transition"
                  title="Play audio"
                >
                  {isGeneratingVoice || isPlayingAudio ? (
                    <Loader size={18} className="animate-spin" />
                  ) : (
                    <Volume2 size={18} />
                  )}
                </button>
              )}
            </div>
          ))}

          {isTyping && (
            <div className="flex justify-start">
              <div className="bg-gray-200 px-6 py-3 rounded-3xl">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-100"></div>
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-200"></div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-200 p-4 bg-white">
          <div className="flex gap-2">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  handleSendMessage();
                }
              }}
              placeholder="Type a message..."
              className="flex-1 px-4 py-3 rounded-full border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={toggleMic}
              className={`w-12 h-12 rounded-full flex items-center justify-center transition text-white ${
                isRecording
                  ? 'bg-red-500 hover:bg-red-600'
                  : 'bg-red-500 hover:bg-red-600'
              }`}
              title={isRecording ? 'Stop recording' : 'Mic input'}
            >
              <Mic size={20} />
            </button>
            <button
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isTyping}
              className="w-12 h-12 rounded-full bg-blue-500 hover:bg-blue-600 disabled:bg-blue-300 text-white flex items-center justify-center transition"
              title="Send message"
            >
              <Send size={20} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FloatingAvatarChatbot;
