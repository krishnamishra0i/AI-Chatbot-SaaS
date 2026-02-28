import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageCircle, X, Send, Video, VideoOff, Mic, MicOff } from 'lucide-react';
import axios from 'axios';
import './App.css';

// Styled Components
const Container = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #e0f2fe 100%);
  font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
`;

const Navigation = styled.nav`
  position: fixed;
  top: 0;
  width: 100%;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 15px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.08);
  z-index: 1000;
`;

const Logo = styled.div`
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
`;

const CTAButton = styled.button`
  padding: 10px 25px;
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  color: white;
  border: none;
  border-radius: 25px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(37, 99, 235, 0.3);
  }
`;

const Main = styled.main`
  margin-top: 70px;
`;

const Hero = styled.section`
  background: linear-gradient(135deg, #f8fafc 0%, #e0f2fe 100%);
  padding: 120px 40px 80px;
  text-align: center;
  position: relative;
  overflow: hidden;
`;

const HeroContent = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 60px;
`;

const HeroText = styled.div`
  flex: 1;
  text-align: left;
`;

const HeroVideo = styled.div`
  flex: 1;
  max-width: 500px;
`;

const HeroVideoContainer = styled.div`
  position: relative;
  width: 100%;
  padding-bottom: 56.25%;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.1);
`;

const HeroVideoElement = styled.video`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
`;

const Title = styled.h1`
  font-size: 48px;
  font-weight: 800;
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 20px;
  line-height: 1.2;
`;

const Subtitle = styled.p`
  font-size: 20px;
  color: #64748b;
  margin-bottom: 40px;
  max-width: 600px;
`;

const HeroButtons = styled.div`
  display: flex;
  gap: 20px;
  justify-content: flex-start;
`;

const Button = styled.button`
  padding: 15px 40px;
  border: none;
  border-radius: 30px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &.primary {
    background: white;
    color: #2563eb;
  }
  
  &.secondary {
    background: linear-gradient(135deg, #2563eb, #3b82f6);
    color: white;
  }
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(37, 99, 235, 0.3);
  }
`;

const FeaturesGrid = styled.section`
  padding: 80px 40px;
  max-width: 1200px;
  margin: 0 auto;
`;

const FeatureCards = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
`;

const FeatureCard = styled(motion.div)`
  background: white;
  padding: 40px;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  text-align: center;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-10px);
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.15);
  }
`;

const FeatureIcon = styled.div`
  font-size: 48px;
  margin-bottom: 20px;
`;

const FeatureTitle = styled.h3`
  font-size: 24px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 15px;
`;

const FeatureDescription = styled.p`
  color: #64748b;
  line-height: 1.6;
`;

// Chatbot Components
const ChatbotContainer = styled(motion.div)`
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 380px;
  height: 600px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  z-index: 1000;
`;

const ChatbotHeader = styled.div`
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  color: white;
  padding: 20px;
  border-radius: 20px 20px 0 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const AvatarContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 15px;
`;

const AvatarImage = styled.div`
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
  animation: pulse 2s infinite;
  position: relative;
  overflow: hidden;
  
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 50%;
  }
`;

const AvatarVideoContainer = styled.div`
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(37, 99, 235, 0.3);
`;

const VideoAvatar = styled.video`
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
`;

const VideoControls = styled.div`
  position: absolute;
  bottom: 5px;
  right: 5px;
  display: flex;
  gap: 5px;
  background: rgba(0, 0, 0, 0.5);
  padding: 4px;
  border-radius: 15px;
`;

const ControlButton = styled.button`
  width: 25px;
  height: 25px;
  border: none;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  
  &:hover {
    background: white;
    transform: scale(1.1);
  }
`;

const ChatbotBody = styled.div`
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 15px;
`;

const MessageContainer = styled.div`
  display: flex;
  gap: 10px;
  align-items: flex-start;
  max-width: 85%;
`;

const UserMessage = styled.div`
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  color: white;
  padding: 12px 16px;
  border-radius: 18px 18px 4px 18px;
  margin-left: auto;
`;

const BotMessage = styled.div`
  background: #f1f5f9;
  color: #333;
  padding: 12px 16px;
  border-radius: 18px 18px 18px 4px;
`;

const ChatInput = styled.div`
  padding: 20px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  gap: 10px;
`;

const InputField = styled.input`
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #e5e7eb;
  border-radius: 25px;
  outline: none;
  font-size: 14px;
  
  &:focus {
    border-color: #2563eb;
  }
`;

const SendButton = styled.button`
  width: 45px;
  height: 45px;
  border-radius: 50%;
  border: none;
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  
  &:hover {
    transform: scale(1.1);
  }
`;

const FloatingButton = styled(motion.button)`
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  border: none;
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 30px rgba(37, 99, 235, 0.3);
  z-index: 999;
`;

const Footer = styled.footer`
  background: #f8f9fa;
  color: #333333;
  padding: 60px 40px;
  text-align: center;
`;

// Additional Styled Components for Complete Features
const VisualShowcase = styled.section`
  background: white;
  padding: 80px 40px;
`;

const ShowcaseContent = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  text-align: center;
`;

const ShowcaseTitle = styled.h2`
  font-size: 48px;
  margin-bottom: 20px;
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 800;
`;

const ShowcaseDescription = styled.p`
  color: #666;
  font-size: 18px;
  margin-bottom: 60px;
  line-height: 1.8;
`;

const ShowcaseGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 40px;
  margin-top: 60px;
`;

const ShowcaseCard = styled(motion.div)`
  background: #f8f9fa;
  padding: 40px;
  border-radius: 20px;
  text-align: center;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-10px);
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.1);
  }
`;

const ShowcaseIcon = styled.div`
  font-size: 64px;
  margin-bottom: 20px;
`;

const ShowcaseCardTitle = styled.h3`
  font-size: 24px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 15px;
`;

const UsedBySection = styled.section`
  background: white;
  padding: 80px 40px;
`;

const UsedByContent = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 60px;
  align-items: center;
`;

const UsedByText = styled.div``;

const UsedByTitle = styled.h2`
  font-size: 48px;
  margin-bottom: 30px;
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 800;
`;

const UsedByImage = styled.div`
  position: relative;
  max-width: 500px;
`;

const UsedByImageContainer = styled.div`
  width: 100%;
  height: 400px;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.1);
`;

const IntegrationsSection = styled.section`
  background: linear-gradient(135deg, #f5f7fa, #e8ecff);
  padding: 80px 40px;
`;

const IntegrationsContent = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 60px;
  align-items: center;
`;

const IntegrationsTitle = styled.h2`
  font-size: 48px;
  margin-bottom: 30px;
  color: #333;
  font-weight: 800;
`;

const IntegrationGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 20px;
  margin-top: 40px;
`;

const IntegrationCard = styled.div`
  background: white;
  padding: 20px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
  }
`;

const EnterpriseSection = styled.section`
  background: white;
  padding: 80px 40px;
`;

const EnterpriseTitle = styled.h2`
  font-size: 48px;
  text-align: center;
  margin-bottom: 20px;
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 800;
`;

const EnterpriseSubtitle = styled.p`
  text-align: center;
  color: #666;
  font-size: 16px;
  margin-bottom: 60px;
`;

const EnterpriseGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
  max-width: 1200px;
  margin: 0 auto;
`;

const EnterpriseCard = styled(motion.div)`
  background: #f8f9fa;
  padding: 30px;
  border-radius: 16px;
  text-align: center;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  }
`;

const TestimonialsSection = styled.section`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 80px 40px;
`;

const TestimonialsTitle = styled.h2`
  font-size: 48px;
  text-align: center;
  margin-bottom: 20px;
  color: white;
  font-weight: 800;
`;

const TestimonialsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 30px;
  max-width: 1200px;
  margin: 60px auto 0;
`;

const TestimonialCard = styled(motion.div)`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  padding: 30px;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
`;

const TestimonialText = styled.p`
  font-size: 16px;
  line-height: 1.6;
  margin-bottom: 20px;
  font-style: italic;
`;

const TestimonialAuthor = styled.div`
  display: flex;
  align-items: center;
  gap: 15px;
`;

const AuthorAvatar = styled.div`
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: white;
`;

const AuthorInfo = styled.div``;

const AuthorName = styled.div`
  font-weight: 600;
  margin-bottom: 5px;
`;

const AuthorRole = styled.div`
  opacity: 0.8;
  font-size: 14px;
`;

const FAQSection = styled.section`
  background: white;
  padding: 80px 40px;
`;

const FAQTitle = styled.h2`
  font-size: 48px;
  text-align: center;
  margin-bottom: 20px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 800;
`;

const FAQContainer = styled.div`
  max-width: 1000px;
  margin: 60px auto 0;
`;

const FAQItem = styled(motion.div)`
  margin-bottom: 20px;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
`;

const FAQQuestion = styled.div`
  padding: 20px;
  background: #f8f9fa;
  font-weight: 600;
  font-size: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.3s ease;
  
  &:hover {
    background: #e5e7eb;
  }
`;

const FAQAnswer = styled.div`
  padding: 20px;
  background: white;
  border-top: 1px solid #e5e7eb;
  color: #666;
  line-height: 1.6;
`;

const CTASection = styled.section`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 80px 40px;
  text-align: center;
`;

const CTATitle = styled.h2`
  font-size: 48px;
  margin-bottom: 20px;
  font-weight: 800;
`;

const CTADescription = styled.p`
  font-size: 18px;
  margin-bottom: 40px;
  opacity: 0.95;
`;

const CTASectionButton = styled.button`
  padding: 15px 40px;
  background: white;
  color: #667eea;
  border: none;
  border-radius: 30px;
  font-weight: 700;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.3s;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(255, 255, 255, 0.3);
  }
`;

function App() {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [messages, setMessages] = useState([
    { type: 'bot', text: 'Hello! I\'m Athena, your AI assistant. How can I help you today?' }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isVideoEnabled, setIsVideoEnabled] = useState(false);
  const [isAudioEnabled, setIsAudioEnabled] = useState(true);
  const [expandedFAQ, setExpandedFAQ] = useState(null);
  const messagesEndRef = useRef(null);

  const API_BASE_URL = 'http://localhost:5000/api';

  // Data for all sections
  const showcaseItems = [
    { icon: '🎭', title: 'Photorealistic Avatars', description: 'Lifelike digital humans that express emotions naturally' },
    { icon: '🧠', title: 'AI Intelligence', description: 'Advanced neural networks for natural conversations' },
    { icon: '🌐', title: 'Global Scale', description: 'Serve millions of users simultaneously with low latency' },
    { icon: '🔒', title: 'Privacy First', description: 'Enterprise-grade security with end-to-end encryption' },
    { icon: '⚡', title: 'Real-Time Processing', description: 'Sub-second response times for seamless interactions' },
    { icon: '🎨', title: 'Customizable', description: 'Tailor avatars to match your brand and personality' }
  ];

  const integrations = [
    { name: 'Slack', icon: '💬' },
    { name: 'Microsoft Teams', icon: '🏢' },
    { name: 'Zoom', icon: '📹' },
    { name: 'Webex', icon: '📞' },
    { name: 'Discord', icon: '🎮' },
    { name: 'WhatsApp', icon: '📱' }
  ];

  const enterpriseFeatures = [
    { icon: '🔐', title: 'Enterprise Security', description: 'SOC 2 Type II certified with 256-bit encryption' },
    { icon: '🌍', title: 'Global CDN', description: '99.9% uptime with edge locations worldwide' },
    { icon: '📊', title: 'Analytics Dashboard', description: 'Real-time insights and performance metrics' },
    { icon: '👥', title: 'Team Management', description: 'Role-based access and administrative controls' },
    { icon: '🔧', title: 'API Access', description: 'RESTful APIs and SDKs for custom integrations' },
    { icon: '📞', title: '24/7 Support', description: 'Dedicated support team with SLA guarantees' }
  ];

  const testimonials = [
    {
      text: 'Athena AI has transformed our customer service. Response times are down 80% while satisfaction scores are up 45%.',
      author: 'Sarah Chen',
      role: 'VP of Customer Experience',
      company: 'TechCorp'
    },
    {
      text: 'The photorealistic avatars are incredible. Our users forget they\'re talking to AI half the time.',
      author: 'Michael Rodriguez',
      role: 'Head of Digital Innovation',
      company: 'GlobalBank'
    },
    {
      text: 'Implementation was seamless and the ROI was immediate. Best investment we\'ve made this year.',
      author: 'Emily Watson',
      role: 'CTO',
      company: 'StartupHub'
    }
  ];

  const faqs = [
    {
      question: 'How accurate are the AI avatars?',
      answer: 'Our avatars achieve 98.7% accuracy in speech recognition and 95% accuracy in contextual understanding, making them among the most advanced in the industry.'
    },
    {
      question: 'Can I customize the avatar appearance?',
      answer: 'Yes! You can fully customize avatar appearance, voice, personality, and even create custom avatars based on real people with proper consent.'
    },
    {
      question: 'What languages do you support?',
      answer: 'We support over 50 languages with real-time translation and native accent support for major global markets.'
    },
    {
      question: 'How secure is the platform?',
      answer: 'We use enterprise-grade encryption, are SOC 2 Type II certified, and comply with GDPR, CCPA, and other major data protection regulations.'
    },
    {
      question: 'What is the pricing model?',
      answer: 'We offer flexible pricing based on usage, starting at $99/month for small teams up to enterprise custom pricing for large organizations.'
    }
  ];

  const API_BASE_URL = 'http://localhost:5000/api';

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const callPythonBackend = async (message) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/chat`, {
        message: message,
        video_enabled: isVideoEnabled,
        audio_enabled: isAudioEnabled
      });
      
      return response.data.message || response.data.response;
    } catch (error) {
      console.log('Python backend not available, using fallback responses');
      return null;
    }
  };

  const handleSendMessage = async () => {
    if (inputValue.trim()) {
      const userMessage = { type: 'user', text: inputValue };
      setMessages([...messages, userMessage]);
      setInputValue('');
      setIsTyping(true);

      const botResponse = await callPythonBackend(inputValue);
      
      setTimeout(() => {
        let responseText;
        
        if (botResponse) {
          responseText = botResponse;
        } else {
          const fallbackResponses = [
            'That\'s interesting! Tell me more about that.',
            'I understand your concern. Let me help you with that.',
            'Great question! Here\'s what I think...',
            'I\'m here to assist you. Could you provide more details?',
            'Thanks for sharing! How can I help you further?',
            'I can help you with information about our AI avatar platform.',
            'Would you like to know more about our features?',
            'How can I assist you with Athena AI today?'
          ];
          responseText = fallbackResponses[Math.floor(Math.random() * fallbackResponses.length)];
        }
        
        setMessages(prev => [...prev, { type: 'bot', text: responseText }]);
        setIsTyping(false);
      }, botResponse ? 500 : 1500);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };

  const toggleVideo = () => {
    setIsVideoEnabled(!isVideoEnabled);
  };

  const toggleAudio = () => {
    setIsAudioEnabled(!isAudioEnabled);
  };

  const toggleFAQ = (index) => {
    setExpandedFAQ(expandedFAQ === index ? null : index);
  };

  const openChatbot = () => {
    setIsChatOpen(true);
  };

  const features = [
    { icon: '🎤', title: 'Real-Time Voice Input', description: 'Speak naturally and let our speech-to-text technology understand you instantly' },
    { icon: '🔊', title: 'Natural Voice Output', description: 'Experience human-like responses with advanced text-to-speech synthesis' },
    { icon: '🎭', title: 'Photorealistic Avatars', description: 'Interact with lifelike AI avatars that express emotions naturally' },
    { icon: '🌍', title: 'Multi-Language Support', description: 'Communicate in over 50 languages with real-time translation' },
    { icon: '🔐', title: 'Enterprise Security', description: 'Bank-grade encryption and compliance with global data protection standards' },
    { icon: '⚡', title: 'Sub-second Latency', description: 'Experience near-instantaneous responses for seamless conversations' }
  ];

  return (
    <Container>
      <Navigation>
        <Logo>📚 ATHENA AI</Logo>
        <CTAButton>Get Started</CTAButton>
      </Navigation>
      
      <Main>
        <Hero>
          <HeroContent>
            <HeroText>
              <Title>Athena AI Platform</Title>
              <Subtitle>Transform your communication with photorealistic AI avatars that understand, respond, and engage naturally</Subtitle>
              <HeroButtons>
                <Button className="primary">Start Free Trial</Button>
                <Button className="secondary">Watch Demo</Button>
              </HeroButtons>
            </HeroText>
            <HeroVideo>
              <HeroVideoContainer>
                <HeroVideoElement autoPlay muted loop>
                  <source src="/video01.mp4" type="video/mp4" />
                  Your browser does not support the video tag.
                </HeroVideoElement>
              </HeroVideoContainer>
            </HeroVideo>
          </HeroContent>
        </Hero>

        <VisualShowcase>
          <ShowcaseContent>
            <ShowcaseTitle>Experience the Future</ShowcaseTitle>
            <ShowcaseDescription>See how our AI avatars are revolutionizing digital communication across industries</ShowcaseDescription>
            <ShowcaseGrid>
              {showcaseItems.map((item, index) => (
                <ShowcaseCard
                  key={index}
                  initial={{ opacity: 0, y: 50 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  whileHover={{ scale: 1.05 }}
                >
                  <ShowcaseIcon>{item.icon}</ShowcaseIcon>
                  <ShowcaseCardTitle>{item.title}</ShowcaseCardTitle>
                  <p>{item.description}</p>
                </ShowcaseCard>
              ))}
            </ShowcaseGrid>
          </ShowcaseContent>
        </VisualShowcase>

        <FeaturesGrid>
          <FeatureCards>
            {features.map((feature, index) => (
              <FeatureCard
                key={index}
                initial={{ opacity: 0, y: 50 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                whileHover={{ scale: 1.05 }}
              >
                <FeatureIcon>{feature.icon}</FeatureIcon>
                <FeatureTitle>{feature.title}</FeatureTitle>
                <FeatureDescription>{feature.description}</FeatureDescription>
              </FeatureCard>
            ))}
          </FeatureCards>
        </FeaturesGrid>

        <UsedBySection>
          <UsedByContent>
            <UsedByText>
              <UsedByTitle>Used by Leading Teams</UsedByTitle>
              <p style={{ fontSize: '18px', color: '#666', marginBottom: '30px', lineHeight: '1.8' }}>
                From startups to Fortune 500 companies, thousands of teams trust Athena AI for their customer communication and internal collaboration needs.
              </p>
              <ul style={{ listStyle: 'none', padding: 0 }}>
                <li style={{ marginBottom: '15px', fontSize: '16px' }}>✓ 10M+ conversations processed daily</li>
                <li style={{ marginBottom: '15px', fontSize: '16px' }}>✓ 99.9% uptime guarantee</li>
                <li style={{ marginBottom: '15px', fontSize: '16px' }}>✓ 50+ countries supported</li>
                <li style={{ fontSize: '16px' }}>✓ 45+ languages available</li>
              </ul>
            </UsedByText>
            <UsedByImage>
              <UsedByImageContainer>
                <img src="/images/paul-sir-image.png" alt="Leading Teams" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
              </UsedByImageContainer>
            </UsedByImage>
          </UsedByContent>
        </UsedBySection>

        <IntegrationsSection>
          <IntegrationsContent>
            <div>
              <IntegrationsTitle>Seamless Integrations</IntegrationsTitle>
              <p style={{ fontSize: '18px', color: '#666', marginBottom: '30px', lineHeight: '1.8' }}>
                Connect Athena AI with your favorite tools and platforms. Our extensive API ecosystem ensures you can deploy avatars wherever your customers are.
              </p>
              <IntegrationGrid>
                {integrations.map((integration, index) => (
                  <IntegrationCard key={index}>
                    <div style={{ fontSize: '32px', marginBottom: '10px' }}>{integration.icon}</div>
                    <div style={{ fontWeight: '600', fontSize: '14px' }}>{integration.name}</div>
                  </IntegrationCard>
                ))}
              </IntegrationGrid>
            </div>
            <div>
              <UsedByImageContainer>
                <HeroVideoElement autoPlay muted loop>
                  <source src="/video01.mp4" type="video/mp4" />
                </HeroVideoElement>
              </UsedByImageContainer>
            </div>
          </IntegrationsContent>
        </IntegrationsSection>

        <EnterpriseSection>
          <EnterpriseTitle>Enterprise-Ready</EnterpriseTitle>
          <EnterpriseSubtitle>Built for the highest standards of reliability, security, and support</EnterpriseSubtitle>
          <EnterpriseGrid>
            {enterpriseFeatures.map((feature, index) => (
              <EnterpriseCard
                key={index}
                initial={{ opacity: 0, y: 50 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                whileHover={{ scale: 1.05 }}
              >
                <div style={{ fontSize: '48px', marginBottom: '20px' }}>{feature.icon}</div>
                <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#1e293b', marginBottom: '15px' }}>{feature.title}</h3>
                <p style={{ color: '#666', lineHeight: '1.6' }}>{feature.description}</p>
              </EnterpriseCard>
            ))}
          </EnterpriseGrid>
        </EnterpriseSection>

        <TestimonialsSection>
          <TestimonialsTitle>What Our Customers Say</TestimonialsTitle>
          <TestimonialsGrid>
            {testimonials.map((testimonial, index) => (
              <TestimonialCard
                key={index}
                initial={{ opacity: 0, y: 50 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
              >
                <TestimonialText>"{testimonial.text}"</TestimonialText>
                <TestimonialAuthor>
                  <AuthorAvatar>{testimonial.author.split(' ').map(n => n[0]).join('')}</AuthorAvatar>
                  <AuthorInfo>
                    <AuthorName>{testimonial.author}</AuthorName>
                    <AuthorRole>{testimonial.role} at {testimonial.company}</AuthorRole>
                  </AuthorInfo>
                </TestimonialAuthor>
              </TestimonialCard>
            ))}
          </TestimonialsGrid>
        </TestimonialsSection>

        <FAQSection>
          <FAQTitle>Frequently Asked Questions</FAQTitle>
          <FAQContainer>
            {faqs.map((faq, index) => (
              <FAQItem key={index}>
                <FAQQuestion onClick={() => toggleFAQ(index)}>
                  <span>{faq.question}</span>
                  <span>{expandedFAQ === index ? '−' : '+'}</span>
                </FAQQuestion>
                {expandedFAQ === index && (
                  <FAQAnswer>
                    {faq.answer}
                  </FAQAnswer>
                )}
              </FAQItem>
            ))}
          </FAQContainer>
        </FAQSection>

        <CTASection>
          <CTATitle>Ready to Transform Your Communication?</CTATitle>
          <CTADescription>Join thousands of enterprise customers using Athena for real-time AI interactions</CTADescription>
          <CTASectionButton onClick={openChatbot}>Start Free Trial Today</CTASectionButton>
        </CTASection>
      </Main>
      
      <Footer>
        <p>&copy; 2026 Athena AI - Enterprise AI Avatar Platform</p>
      </Footer>
      
      <AnimatePresence>
        {isChatOpen && (
          <ChatbotContainer
            initial={{ opacity: 0, scale: 0.8, y: 50 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.8, y: 50 }}
            transition={{ duration: 0.3 }}
          >
            <ChatbotHeader>
              <AvatarContainer>
                <AvatarVideoContainer>
                  {isVideoEnabled ? (
                    <>
                      <VideoAvatar autoPlay muted loop>
                        <source src="/video01.mp4" type="video/mp4" />
                      </VideoAvatar>
                      <VideoControls>
                        <ControlButton onClick={toggleVideo}>
                          {isVideoEnabled ? <VideoOff size={12} /> : <Video size={12} />}
                        </ControlButton>
                        <ControlButton onClick={toggleAudio}>
                          {isAudioEnabled ? <Mic size={12} /> : <MicOff size={12} />}
                        </ControlButton>
                      </VideoControls>
                    </>
                  ) : (
                    <>
                      <AvatarImage>
                        <img src="/images/paul-sir-image.png" alt="Athena AI Assistant" />
                      </AvatarImage>
                      <VideoControls>
                        <ControlButton onClick={toggleVideo}>
                          <Video size={12} />
                        </ControlButton>
                        <ControlButton onClick={toggleAudio}>
                          {isAudioEnabled ? <Mic size={12} /> : <MicOff size={12} />}
                        </ControlButton>
                      </VideoControls>
                    </>
                  )}
                </AvatarVideoContainer>
                <div>
                  <div style={{ fontWeight: '600', fontSize: '16px' }}>Athena AI Assistant</div>
                  <div style={{ fontSize: '12px', opacity: 0.8 }}>
                    {isVideoEnabled ? 'Video Mode' : 'Text Mode'} • {isAudioEnabled ? 'Audio On' : 'Audio Off'}
                  </div>
                </div>
              </AvatarContainer>
              <button 
                style={{ background: 'none', border: 'none', color: 'white', cursor: 'pointer', fontSize: '20px' }}
                onClick={() => setIsChatOpen(false)}
              >
                <X size={20} />
              </button>
            </ChatbotHeader>
            
            <ChatbotBody>
              {messages.map((message, index) => (
                <MessageContainer key={index} style={message.type === 'user' ? { marginLeft: 'auto' } : {}}>
                  {message.type === 'bot' && (
                    <AvatarImage style={{ width: '40px', height: '40px' }}>
                      <img src="/images/paul-sir-image.png" alt="Athena AI Assistant" style={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius: '50%' }} />
                    </AvatarImage>
                  )}
                  {message.type === 'user' ? (
                    <UserMessage>{message.text}</UserMessage>
                  ) : (
                    <BotMessage>{message.text}</BotMessage>
                  )}
                </MessageContainer>
              ))}
              
              {isTyping && (
                <MessageContainer>
                  <AvatarImage style={{ width: '40px', height: '40px' }}>
                    <img src="/images/paul-sir-image.png" alt="Athena AI Assistant" style={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius: '50%' }} />
                  </AvatarImage>
                  <BotMessage>
                    <div style={{ display: 'flex', gap: '4px' }}>
                      <div style={{ width: '8px', height: '8px', background: '#666', borderRadius: '50%', animation: 'typing 1.4s infinite' }}></div>
                      <div style={{ width: '8px', height: '8px', background: '#666', borderRadius: '50%', animation: 'typing 1.4s infinite', animationDelay: '0.2s' }}></div>
                      <div style={{ width: '8px', height: '8px', background: '#666', borderRadius: '50%', animation: 'typing 1.4s infinite', animationDelay: '0.4s' }}></div>
                    </div>
                  </BotMessage>
                </MessageContainer>
              )}
              <div ref={messagesEndRef} />
            </ChatbotBody>
            
            <ChatInput>
              <InputField
                type="text"
                placeholder="Type your message..."
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
              />
              <SendButton onClick={handleSendMessage}>
                <Send size={20} />
              </SendButton>
            </ChatInput>
          </ChatbotContainer>
        )}
      </AnimatePresence>
      
      {!isChatOpen && (
        <FloatingButton
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={() => setIsChatOpen(true)}
        >
          <MessageCircle size={24} />
        </FloatingButton>
      )}
    </Container>
  );
}

export default App;
