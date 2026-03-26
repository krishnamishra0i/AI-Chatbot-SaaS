import React, { useState, useEffect, useRef, useCallback } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageCircle, X, Send, Video, VideoOff, Mic, MicOff, LogIn, LayoutDashboard, Settings } from 'lucide-react';
import axios from 'axios';
import './App.css';
import FeatureCards from './FeatureCards';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { chatAPI, ChatWebSocket, TTSWebSocket, healthAPI } from './services/api';
import AuthPage from './pages/AuthPage';
import DashboardPage from './pages/DashboardPage';
import SettingsPage from './pages/SettingsPage';
import DebugAuthPage from './pages/DebugAuthPage';
import TokenDiagnosisPage from './pages/TokenDiagnosisPage';
import HomePageModern from './pages/HomePageModern';
import TechnologyPage from './pages/TechnologyPage';
import PersonaAIPage from './pages/PersonaAIPage';
import LoginPage from './pages/LoginPage';
import VerificationPage from './pages/VerificationPage';

// Styled Components
const Container = styled.div`
  min-height: 100vh;
  background: #0B0F19;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  position: relative;
  overflow-x: hidden;
  
  &::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: 
      radial-gradient(circle at 20% 50%, rgba(139, 92, 246, 0.1) 0%, transparent 50%),
      radial-gradient(circle at 80% 80%, rgba(59, 130, 246, 0.08) 0%, transparent 50%),
      radial-gradient(circle at 40% 20%, rgba(6, 182, 212, 0.06) 0%, transparent 50%);
    pointer-events: none;
    z-index: 1;
  }
  
  &::after {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: 
      radial-gradient(circle at 25% 25%, rgba(255, 255, 255, 0.02) 1px, transparent 1px),
      radial-gradient(circle at 75% 75%, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
    background-size: 50px 50px;
    animation: particleFloat 20s linear infinite;
    pointer-events: none;
    z-index: 1;
  }
  
  @keyframes particleFloat {
    0% { transform: translateY(0px) rotate(0deg); }
    100% { transform: translateY(-20px) rotate(360deg); }
  }
`;

const Navigation = styled.nav`
  position: fixed;
  top: 0;
  width: 100%;
  background: rgba(11, 15, 25, 0.8);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  padding: 20px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 1000;
`;

const Logo = styled.div`
  font-size: 28px;
  font-weight: 800;
  background: linear-gradient(135deg, #8B5CF6, #3B82F6, #06B6D4);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.5px;
`;

const CTAButton = styled.button`
  padding: 12px 28px;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(59, 130, 246, 0.2));
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: #ffffff;
  font-weight: 600;
  cursor: pointer;
  font-size: 15px;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(139, 92, 246, 0.3);
    border-color: rgba(255, 255, 255, 0.2);
  }
`;

const Main = styled.main`
  margin-top: 70px;
`;

const Hero = styled.section`
  padding: 140px 40px 100px;
  position: relative;
  overflow: visible;
  z-index: 2;
  max-width: 1400px;
  margin: 0 auto;
  
  &::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: linear-gradient(45deg, transparent, rgba(139, 92, 246, 0.03), transparent);
    animation: shimmer 4s infinite;
  }
  
  @keyframes shimmer {
    0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
    100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
  }
`;

const HeroContent = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 80px;
  align-items: center;
  position: relative;
  z-index: 3;
  
  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
    gap: 60px;
    text-align: center;
  }
`;

const HeroLeft = styled.div`
  position: relative;
`;

const HeroRight = styled.div`
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: visible;
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
  font-size: 72px;
  font-weight: 800;
  background: linear-gradient(135deg, #ffffff 0%, #8B5CF6 50%, #3B82F6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 24px;
  line-height: 1.1;
  letter-spacing: -2px;
  
  @media (max-width: 768px) {
    font-size: 48px;
  }
`;

const Subtitle = styled.p`
  font-size: 20px;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 32px;
  line-height: 1.6;
  font-weight: 400;
`;

const SystemIndicators = styled.div`
  display: flex;
  gap: 24px;
  margin-bottom: 48px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  
  @media (max-width: 768px) {
    justify-content: center;
  }
`;

const Indicator = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  
  .status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #10B981;
    animation: pulse 2s infinite;
  }
  
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }
`;

const HeroButtons = styled.div`
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  
  @media (max-width: 768px) {
    justify-content: center;
  }
`;

const Button = styled.button`
  padding: 16px 40px;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  
  &.primary {
    background: linear-gradient(135deg, #8B5CF6, #3B82F6, #06B6D4);
    color: white;
    box-shadow: 0 10px 30px rgba(139, 92, 246, 0.4);
    animation: glowPulse 2s ease-in-out infinite;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 15px 40px rgba(139, 92, 246, 0.6);
    }
  }
  
  &.secondary {
    background: rgba(255, 255, 255, 0.05);
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(10px);
    
    &:hover {
      background: rgba(255, 255, 255, 0.1);
      border-color: rgba(255, 255, 255, 0.3);
      transform: translateY(-2px);
    }
  }
  
  @keyframes glowPulse {
    0%, 100% { box-shadow: 0 10px 30px rgba(139, 92, 246, 0.4); }
    50% { box-shadow: 0 10px 40px rgba(139, 92, 246, 0.6); }
  }
`;

const AvatarContainer = styled.div`
  position: relative;
  width: 400px;
  height: 400px;
  border-radius: 50%;
  overflow: visible;
  
  /* Primary pulsing glow */
  &::before {
    content: '';
    position: absolute;
    top: -30px;
    left: -30px;
    right: -30px;
    bottom: -30px;
    background: radial-gradient(circle, rgba(139, 92, 246, 0.35) 0%, rgba(99, 62, 206, 0.2) 30%, rgba(59, 130, 246, 0.12) 55%, transparent 75%);
    border-radius: 50%;
    animation: avatarGlowPulse 3s ease-in-out infinite;
    z-index: -1;
  }
  
  /* Secondary outer glow ring */
  &::after {
    content: '';
    position: absolute;
    top: -10px;
    left: -10px;
    right: -10px;
    bottom: -10px;
    border-radius: 50%;
    border: 2px solid rgba(139, 92, 246, 0.15);
    animation: avatarRingPulse 4s ease-in-out infinite;
    z-index: -1;
  }
  
  @media (max-width: 768px) {
    width: 300px;
    height: 300px;
  }
  
  @keyframes avatarGlowPulse {
    0%, 100% { 
      opacity: 0.7;
      transform: scale(1);
    }
    50% { 
      opacity: 1;
      transform: scale(1.08);
    }
  }
  
  @keyframes avatarRingPulse {
    0%, 100% {
      opacity: 0.3;
      transform: scale(1);
      border-color: rgba(139, 92, 246, 0.15);
    }
    50% {
      opacity: 0.7;
      transform: scale(1.05);
      border-color: rgba(139, 92, 246, 0.4);
    }
  }
`;

const AvatarVideo = styled.video`
  width: 100%;
  height: 100%;
  border-radius: 20px;
  object-fit: cover;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
`;

const AvatarImage = styled.img`
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  box-shadow: 
    0 0 30px rgba(139, 92, 246, 0.35),
    0 0 60px rgba(139, 92, 246, 0.15),
    0 20px 60px rgba(0, 0, 0, 0.4);
  border: 3px solid rgba(139, 92, 246, 0.3);
  transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  
  &:hover {
    box-shadow: 
      0 0 40px rgba(139, 92, 246, 0.55),
      0 0 80px rgba(139, 92, 246, 0.25),
      0 25px 70px rgba(0, 0, 0, 0.5);
    border-color: rgba(139, 92, 246, 0.6);
    transform: scale(1.05);
  }
`;

const FloatingPanel = styled(motion.div)`
  position: absolute;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 12px 16px;
  color: white;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  
  &.panel-1 {
    top: -30px;
    right: -60px;
    z-index: 10;
  }
  
  &.panel-2 {
    bottom: -10px;
    left: -80px;
    z-index: 10;
  }
  
  &.panel-3 {
    top: 50%;
    right: -100px;
    transform: translateY(-50%);
    z-index: 10;
  }
`;

const FeaturesGrid = styled.section`
  padding: 100px 40px;
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
  z-index: 2;
`;

// New Sections
const LiveDemoSection = styled.section`
  background: #111827;
  padding: 100px 40px;
  position: relative;
  z-index: 2;
`;

const DemoContent = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 80px;
  align-items: center;
  
  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
    gap: 60px;
  }
`;

const DemoVideoContainer = styled.div`
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    top: -10px;
    left: -10px;
    right: -10px;
    bottom: -10px;
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.3), rgba(59, 130, 246, 0.3));
    border-radius: 20px;
    z-index: -1;
    animation: glowPulse 3s ease-in-out infinite;
  }
`;

const DemoVideo = styled.video`
  width: 100%;
  height: auto;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
`;

const DemoFeatures = styled.div`
  h2 {
    font-size: 48px;
    font-weight: 800;
    background: linear-gradient(135deg, #ffffff, #8B5CF6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 32px;
  }
  
  ul {
    list-style: none;
    padding: 0;
    
    li {
      color: rgba(255, 255, 255, 0.8);
      font-size: 18px;
      margin-bottom: 16px;
      padding-left: 24px;
      position: relative;
      
      &::before {
        content: '✓';
        position: absolute;
        left: 0;
        color: #8B5CF6;
        font-weight: bold;
      }
    }
  }
`;

const FounderSection = styled.section`
  padding: 100px 40px;
  max-width: 1400px;
  margin: 0 auto;
  position: relative;
  z-index: 2;
`;

const FounderContent = styled.div`
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 60px;
  align-items: center;
  
  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
    text-align: center;
  }
`;

const FounderImageContainer = styled.div`
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    top: -20px;
    left: -20px;
    right: -20px;
    bottom: -20px;
    background: radial-gradient(circle, rgba(139, 92, 246, 0.2) 0%, transparent 70%);
    border-radius: 50%;
    animation: glowPulse 3s ease-in-out infinite;
    z-index: -1;
  }
`;

const FounderImage = styled.img`
  width: 100%;
  height: auto;
  border-radius: 50%;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
`;

const FounderText = styled.div`
  h2 {
    font-size: 48px;
    font-weight: 800;
    background: linear-gradient(135deg, #ffffff, #8B5CF6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 24px;
  }
  
  p {
    color: rgba(255, 255, 255, 0.8);
    font-size: 18px;
    line-height: 1.6;
    margin-bottom: 24px;
  }
`;

const TechPipelineSection = styled.section`
  background: #111827;
  padding: 100px 40px;
  position: relative;
  z-index: 2;
`;

const PipelineContent = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  text-align: center;
  
  h2 {
    font-size: 48px;
    font-weight: 800;
    background: linear-gradient(135deg, #ffffff, #8B5CF6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 60px;
  }
`;

const PipelineFlow = styled.div`
  display: flex;
  flex-direction: column;
  gap: 32px;
  align-items: center;
  
  @media (max-width: 768px) {
    gap: 24px;
  }
`;

const PipelineNode = styled(motion.div)`
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 16px;
  padding: 20px 32px;
  color: white;
  font-size: 18px;
  font-weight: 600;
  position: relative;
  transition: all 0.3s ease;
  
  &:hover {
    background: rgba(139, 92, 246, 0.1);
    border-color: rgba(139, 92, 246, 0.6);
    transform: scale(1.05);
    box-shadow: 0 10px 30px rgba(139, 92, 246, 0.3);
  }
  
  &::after {
    content: '↓';
    position: absolute;
    bottom: -32px;
    left: 50%;
    transform: translateX(-50%);
    font-size: 24px;
    color: #8B5CF6;
  }
  
  &:last-child::after {
    display: none;
  }
`;

const FeatureCard = styled(motion.div)`
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(20px);
  padding: 48px;
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 
    0 20px 40px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
    transition: left 0.5s;
  }
  
  &:hover {
    transform: translateY(-8px);
    box-shadow: 
      0 30px 60px rgba(0, 0, 0, 0.4),
      inset 0 1px 0 rgba(255, 255, 255, 0.2);
    border-color: rgba(255, 255, 255, 0.2);
    
    &::before {
      left: 100%;
    }
  }
`;

const FeatureImage = styled.div`
  width: 100%;
  height: 200px;
  border-radius: 16px;
  overflow: hidden;
  margin-bottom: 24px;
  position: relative;
  
  &::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 60px;
    background: linear-gradient(to top, rgba(0, 0, 0, 0.4), transparent);
  }
  
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.5s ease;
  }
  
  &:hover img {
    transform: scale(1.08);
  }
`;

const FeatureIcon = styled.div`
  font-size: 56px;
  margin-bottom: 24px;
  background: linear-gradient(135deg, #7878c6, #ff77c6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
`;

const FeatureTitle = styled.h3`
  font-size: 24px;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 16px;
  line-height: 1.3;
`;

const FeatureDescription = styled.p`
  color: rgba(255, 255, 255, 0.6);
  line-height: 1.6;
  font-size: 16px;
`;

// Chatbot Components
const ChatbotContainer = styled(motion.div)`
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 380px;
  height: 600px;
  background: rgba(10, 10, 10, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  box-shadow: 
    0 30px 60px rgba(0, 0, 0, 0.5),
    0 15px 30px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
  z-index: 1000;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  }
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

const ChatAvatarContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 15px;
`;

const ChatAvatarIcon = styled.div`
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
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, rgba(120, 119, 198, 0.9), rgba(255, 119, 198, 0.9));
  border: none;
  border-radius: 50%;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 
    0 20px 40px rgba(120, 119, 198, 0.4),
    0 10px 20px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
  z-index: 999;
  
  &:hover {
    transform: scale(1.1) translateY(-2px);
    box-shadow: 
      0 25px 50px rgba(120, 119, 198, 0.6),
      0 15px 30px rgba(0, 0, 0, 0.4),
      inset 0 1px 0 rgba(255, 255, 255, 0.3);
  }
`;

const Footer = styled.footer`
  background: #080B14;
  color: rgba(255, 255, 255, 0.6);
  padding: 60px 40px;
  text-align: center;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  position: relative;
  z-index: 2;
`;

// Additional Styled Components for Complete Features
const VisualShowcase = styled.section`
  background: #0B0F19;
  padding: 80px 40px;
  position: relative;
  z-index: 2;
`;

const ShowcaseContent = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  text-align: center;
`;

const ShowcaseTitle = styled.h2`
  font-size: 48px;
  margin-bottom: 20px;
  background: linear-gradient(135deg, #ffffff, #8B5CF6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 800;
`;

const ShowcaseDescription = styled.p`
  color: rgba(255, 255, 255, 0.6);
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
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(20px);
  padding: 40px;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  text-align: center;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-10px);
    box-shadow: 0 20px 50px rgba(139, 92, 246, 0.15);
    border-color: rgba(139, 92, 246, 0.3);
  }
  
  p {
    color: rgba(255, 255, 255, 0.6);
  }
`;

const ShowcaseIcon = styled.div`
  font-size: 64px;
  margin-bottom: 20px;
`;

const ShowcaseCardTitle = styled.h3`
  font-size: 24px;
  font-weight: 600;
  color: #ffffff;
  margin-bottom: 15px;
`;

const UsedBySection = styled.section`
  background: #111827;
  padding: 80px 40px;
  position: relative;
  z-index: 2;
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
  background: linear-gradient(135deg, #ffffff, #8B5CF6);
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
  background: #0B0F19;
  padding: 80px 40px;
  position: relative;
  z-index: 2;
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
  background: linear-gradient(135deg, #ffffff, #3B82F6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 800;
`;

const IntegrationGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 20px;
  margin-top: 40px;
`;

const IntegrationCard = styled.div`
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(10px);
  padding: 20px;
  border-radius: 12px;
  text-align: center;
  border: 1px solid rgba(255, 255, 255, 0.08);
  transition: all 0.3s ease;
  color: white;
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 30px rgba(139, 92, 246, 0.2);
    border-color: rgba(139, 92, 246, 0.4);
  }
`;

const EnterpriseSection = styled.section`
  background: #111827;
  padding: 80px 40px;
  position: relative;
  z-index: 2;
`;

const EnterpriseTitle = styled.h2`
  font-size: 48px;
  text-align: center;
  margin-bottom: 20px;
  background: linear-gradient(135deg, #ffffff, #06B6D4);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 800;
`;

const EnterpriseSubtitle = styled.p`
  text-align: center;
  color: rgba(255, 255, 255, 0.6);
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
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(20px);
  padding: 30px;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  text-align: center;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 30px rgba(139, 92, 246, 0.2);
    border-color: rgba(139, 92, 246, 0.3);
  }
`;

const TestimonialsSection = styled.section`
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, #111827 100%);
  color: white;
  padding: 80px 40px;
  position: relative;
  z-index: 2;
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
  background: #0B0F19;
  padding: 80px 40px;
  position: relative;
  z-index: 2;
`;

const FAQTitle = styled.h2`
  font-size: 48px;
  text-align: center;
  margin-bottom: 20px;
  background: linear-gradient(135deg, #8B5CF6, #3B82F6);
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
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
`;

const FAQQuestion = styled.div`
  padding: 20px;
  background: rgba(255, 255, 255, 0.04);
  font-weight: 600;
  font-size: 16px;
  color: #ffffff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.3s ease;
  
  &:hover {
    background: rgba(139, 92, 246, 0.1);
  }
`;

const FAQAnswer = styled.div`
  padding: 20px;
  background: rgba(255, 255, 255, 0.02);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.6;
`;

const CTASection = styled.section`
  background: radial-gradient(ellipse at center, rgba(139, 92, 246, 0.15) 0%, #0B0F19 70%);
  color: white;
  padding: 120px 40px;
  text-align: center;
  position: relative;
  z-index: 2;
`;

const CTATitle = styled.h2`
  font-size: 52px;
  margin-bottom: 20px;
  font-weight: 800;
  background: linear-gradient(135deg, #ffffff, #8B5CF6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
`;

const CTADescription = styled.p`
  font-size: 18px;
  margin-bottom: 40px;
  opacity: 0.95;
`;

const CTASectionButton = styled.button`
  padding: 18px 48px;
  background: linear-gradient(135deg, #8B5CF6, #3B82F6, #06B6D4);
  color: white;
  border: none;
  border-radius: 14px;
  font-weight: 700;
  cursor: pointer;
  font-size: 18px;
  transition: all 0.3s;
  box-shadow: 0 10px 30px rgba(139, 92, 246, 0.4);
  animation: glowPulse 2s ease-in-out infinite;
  
  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 15px 40px rgba(139, 92, 246, 0.6);
  }
  
  @keyframes glowPulse {
    0%, 100% { box-shadow: 0 10px 30px rgba(139, 92, 246, 0.4); }
    50% { box-shadow: 0 10px 40px rgba(139, 92, 246, 0.6); }
  }
`;

// Why We're Different Section
const WhyDifferentSection = styled.section`
  background: #0B0F19;
  padding: 100px 40px;
  position: relative;
  z-index: 2;
`;

const WhyDifferentTitle = styled.h2`
  font-size: 48px;
  text-align: center;
  margin-bottom: 60px;
  font-weight: 800;
  background: linear-gradient(135deg, #ffffff, #06B6D4);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
`;

const WhyDifferentGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 40px;
  max-width: 1200px;
  margin: 0 auto;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const WhyDifferentCard = styled(motion.div)`
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(20px);
  padding: 48px 32px;
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  text-align: center;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, #8B5CF6, #3B82F6, #06B6D4);
    opacity: 0;
    transition: opacity 0.3s ease;
  }
  
  &:hover {
    transform: translateY(-8px);
    box-shadow: 0 20px 50px rgba(139, 92, 246, 0.15);
    border-color: rgba(139, 92, 246, 0.3);
    
    &::before {
      opacity: 1;
    }
  }
  
  .icon {
    font-size: 56px;
    margin-bottom: 24px;
  }
  
  h3 {
    font-size: 22px;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 12px;
  }
  
  p {
    color: rgba(255, 255, 255, 0.6);
    line-height: 1.6;
    font-size: 16px;
  }
`;

const NavStatus = styled.span`
  font-size: 12px;
  color: ${p => p.$online ? '#22c55e' : 'rgba(255,255,255,0.4)'};
  padding: 6px 12px;
  border-radius: 20px;
  background: ${p => p.$online ? 'rgba(34, 197, 94, 0.1)' : 'rgba(255,255,255,0.05)'};
  border: 1px solid ${p => p.$online ? 'rgba(34, 197, 94, 0.2)' : 'rgba(255,255,255,0.1)'};
`;

// Auth-aware nav buttons
function AuthButtons({ onNavigate }) {
  const { isAuthenticated, user } = useAuth();
  
  if (isAuthenticated) {
    return (
      <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
        <CTAButton onClick={() => onNavigate('token-diagnosis')} style={{ display: 'flex', alignItems: 'center', gap: '6px', background: '#8B5A3C', fontSize: '12px' }}>
          🔐 Token
        </CTAButton>
        <CTAButton onClick={() => onNavigate('debug')} style={{ display: 'flex', alignItems: 'center', gap: '6px', background: '#666', fontSize: '12px' }}>
          🔍 Debug
        </CTAButton>
        <CTAButton onClick={() => onNavigate('settings')} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Settings size={16} /> Settings
        </CTAButton>
        <CTAButton onClick={() => onNavigate('dashboard')} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <LayoutDashboard size={16} /> Dashboard
        </CTAButton>
        <span style={{ color: 'rgba(255,255,255,0.5)', fontSize: '13px' }}>{user?.name || user?.email}</span>
      </div>
    );
  }
  
  return (
    <div style={{ display: 'flex', gap: '10px' }}>
      <CTAButton onClick={() => onNavigate('login')} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
        <LogIn size={16} /> Sign In
      </CTAButton>
    </div>
  );
}

function App() {
  const [currentPage, setCurrentPage] = useState('login');
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [messages, setMessages] = useState([
    { type: 'bot', text: 'Hello! I\'m Athena, your AI assistant. How can I help you today?' }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isVideoEnabled, setIsVideoEnabled] = useState(false);
  const [isAudioEnabled, setIsAudioEnabled] = useState(true);
  const [expandedFAQ, setExpandedFAQ] = useState(null);
  const [backendStatus, setBackendStatus] = useState('checking');
  const [wsChat, setWsChat] = useState(null);
  const [useWebSocket, setUseWebSocket] = useState(false);
  const messagesEndRef = useRef(null);

  // Handle OAuth callback from URL
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get('token');
    if (token) {
      localStorage.setItem('athena_token', token);
      const name = params.get('name') || '';
      const email = params.get('email') || '';
      localStorage.setItem('athena_user', JSON.stringify({ name, email }));
      window.history.replaceState({}, document.title, window.location.pathname);
      setCurrentPage('dashboard');
    }
    // Check if path contains auth callback
    if (window.location.pathname.includes('/auth/callback')) {
      setCurrentPage('dashboard');
    }
  }, []);

  // Check backend health
  useEffect(() => {
    healthAPI.check()
      .then(() => setBackendStatus('online'))
      .catch(() => setBackendStatus('offline'));
  }, []);

  // Try to establish WebSocket connection
  useEffect(() => {
    if (!isChatOpen) return;
    
    const ws = new ChatWebSocket((data) => {
      if (data.type === 'chunk') {
        setMessages(prev => {
          const last = prev[prev.length - 1];
          if (last && last.type === 'bot' && last.streaming) {
            return [...prev.slice(0, -1), { ...last, text: last.text + data.content }];
          }
          return [...prev, { type: 'bot', text: data.content, streaming: true }];
        });
      } else if (data.type === 'done') {
        setMessages(prev => {
          const last = prev[prev.length - 1];
          if (last && last.streaming) {
            return [...prev.slice(0, -1), { ...last, streaming: false }];
          }
          return prev;
        });
        setIsTyping(false);
      }
    });

    ws.connect()
      .then(() => { setWsChat(ws); setUseWebSocket(true); })
      .catch(() => { setUseWebSocket(false); });

    return () => ws.close();
  }, [isChatOpen]);

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

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const callPythonBackend = async (message, settings = {}) => {
    try {
      const response = await chatAPI.send(message, {
        model: settings.model,
        temperature: settings.temperature,
        max_tokens: settings.maxTokens,
        prompt_template: settings.promptTemplate,
        emotion: settings.emotion,
      });
      return response.data.message || response.data.response;
    } catch (error) {
      console.log('Backend not available, using fallback responses');
      return null;
    }
  };

  const handleSendMessage = async () => {
    if (inputValue.trim()) {
      const userMessage = { type: 'user', text: inputValue };
      setMessages(prev => [...prev, userMessage]);
      const currentInput = inputValue;
      setInputValue('');
      setIsTyping(true);

      // Try WebSocket first
      if (useWebSocket && wsChat) {
        const settings = JSON.parse(localStorage.getItem('athena_settings') || '{}');
        wsChat.send(currentInput, {
          stream: true,
          model: settings.model,
          temperature: settings.temperature,
          session_id: 'default',
        });
        return;
      }

      // Fallback to REST API
      // Fallback to REST API with settings
      const settings = JSON.parse(localStorage.getItem('athena_settings') || '{}');
      const botResponse = await callPythonBackend(currentInput, settings);
      
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

  const navigate = (page) => {
    setCurrentPage(page);
    window.scrollTo(0, 0);
  };

  // ── Render Dashboard ──
  if (currentPage === 'dashboard') {
    return <DashboardPage onNavigate={navigate} />;
  }

  // ── Render Settings Page ──
  if (currentPage === 'settings') {
    return <SettingsPage onNavigate={navigate} />;
  }

  // ── Render Debug Page ──
  if (currentPage === 'debug') {
    return <DebugAuthPage />;
  }

  // ── Render Token Diagnosis Page ──
  if (currentPage === 'token-diagnosis') {
    return <TokenDiagnosisPage />;
  }

  // ── Render New Home Page ──
  if (currentPage === 'home') {
    return <HomePageModern onNavigate={navigate} onLaunchDemo={() => navigate('login')} />;
  }

  // ── Render Technology Page ──
  if (currentPage === 'technology') {
    return <TechnologyPage onNavigate={navigate} onLaunchDemo={() => navigate('login')} />;
  }

  // ── Render PersonaAI Page ──
  if (currentPage === 'persona-ai') {
    return <PersonaAIPage onNavigate={navigate} onLaunchDemo={() => navigate('login')} />;
  }

  // ── Render Login Page ──
  if (currentPage === 'login') {
    return <LoginPage onNavigate={navigate} />;
  }

  // ── Render Verification Page ──
  if (currentPage === 'verification') {
    return <VerificationPage onNavigate={navigate} />;
  }

  const features = [
    { icon: '🔊', title: 'Real-Time Voice Processing', description: 'Advanced speech-to-text with ultra-low latency and high accuracy for natural conversations', image: '/images/real-time-voice-processing.jpg' },
    { icon: '🤖', title: 'AI Chat Intelligence', description: 'Powered by cutting-edge LLM technology for intelligent, context-aware responses', image: '/images/ai-chat-intelligence.png' },
    { icon: '🎮', title: 'Unreal Engine Integration', description: 'Seamless integration with Unreal Engine for photorealistic 3D avatars', image: '/images/ai-chat-intelligence.jpg' },
    { icon: '👄', title: 'Ultra-Accurate Lip Sync', description: 'Precision lip-sync technology that matches speech patterns perfectly', image: '/images/ultra-accurate-lip-sync.jpg' }
  ];

  return (
    <Container>
      <Navigation>
        <Logo>📚 ATHENA AI</Logo>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <NavStatus $online={backendStatus === 'online'}>
            {backendStatus === 'online' ? '● Online' : backendStatus === 'offline' ? '○ Offline' : '◌ Checking...'}
          </NavStatus>
          <AuthButtons onNavigate={navigate} />
        </div>
      </Navigation>
      
      <Main>
        <Hero>
          <HeroContent>
            <HeroLeft>
              <Title>Real-Time AI Avatar Conversations</Title>
              <Subtitle>Voice-to-text • LLM Intelligence • Text-to-Speech • Real-Time Lip Sync • Unreal Engine Integration</Subtitle>
              <SystemIndicators>
                <Indicator>
                  <span className="status-dot"></span>
                  System Online
                </Indicator>
                <Indicator>
                  <span>⚡</span>
                  Avg Latency: 120ms
                </Indicator>
              </SystemIndicators>
              <HeroButtons>
                <Button className="primary">Try Live Demo</Button>
                <Button className="secondary">View Documentation</Button>
              </HeroButtons>
            </HeroLeft>
            <HeroRight>
              <AvatarContainer>
                <AvatarImage 
                  src="/images/paul-sir-image.png" 
                  alt="Paul Sir - AI Avatar"
                />
                <FloatingPanel 
                  className="panel-1"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.5 }}
                >
                  🎤 Live Transcription
                </FloatingPanel>
                <FloatingPanel 
                  className="panel-2"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.7 }}
                >
                  🤖 AI Response Generating
                </FloatingPanel>
                <FloatingPanel 
                  className="panel-3"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.9 }}
                >
                  👄 Lip-Sync Active
                </FloatingPanel>
              </AvatarContainer>
            </HeroRight>
          </HeroContent>
        </Hero>

        <LiveDemoSection>
          <DemoContent>
            <DemoVideoContainer>
              <DemoVideo autoPlay muted loop playsInline>
                <source src="/video01_converted.mp4" type="video/mp4" />
                <source src="/video01.mp4" type="video/mp4" />
                Your browser does not support the video tag.
              </DemoVideo>
            </DemoVideoContainer>
            <DemoFeatures>
              <h2>See The AI Avatar In Action</h2>
              <ul>
                <li>Real-time voice processing</li>
                <li>AI response generation</li>
                <li>Ultra-accurate lip movement</li>
                <li>Unreal Engine 3D animation sync</li>
              </ul>
            </DemoFeatures>
          </DemoContent>
        </LiveDemoSection>

        <FounderSection>
          <FounderContent>
            <FounderImageContainer>
              <FounderImage src="/images/paul-sir-image.png" alt="AI Innovator" />
            </FounderImageContainer>
            <FounderText>
              <h2>Built by AI Innovators</h2>
              <p>Leading the future of real-time AI avatar technology with cutting-edge research in speech processing, natural language understanding, and 3D animation synchronization.</p>
              <p>Our team combines expertise from AI research labs, gaming industry veterans, and enterprise software engineers to deliver the most advanced avatar conversation platform.</p>
            </FounderText>
          </FounderContent>
        </FounderSection>

        <TechPipelineSection>
          <PipelineContent>
            <h2>Technology Pipeline</h2>
            <PipelineFlow>
              <PipelineNode
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                whileHover={{ scale: 1.05 }}
              >
                User Voice
              </PipelineNode>
              <PipelineNode
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                whileHover={{ scale: 1.05 }}
              >
                Speech-to-Text
              </PipelineNode>
              <PipelineNode
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                whileHover={{ scale: 1.05 }}
              >
                Large Language Model
              </PipelineNode>
              <PipelineNode
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                whileHover={{ scale: 1.05 }}
              >
                Text-to-Speech
              </PipelineNode>
              <PipelineNode
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                whileHover={{ scale: 1.05 }}
              >
                Lip Sync Engine
              </PipelineNode>
              <PipelineNode
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
                whileHover={{ scale: 1.05 }}
              >
                3D Avatar Output
              </PipelineNode>
            </PipelineFlow>
          </PipelineContent>
        </TechPipelineSection>

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
          <div style={{ textAlign: 'center', marginBottom: '60px' }}>
            <h2 style={{ fontSize: '48px', marginBottom: '20px', background: 'linear-gradient(135deg, #ffffff, #8B5CF6)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text', fontWeight: 800 }}>Powerful Features</h2>
            <p style={{ fontSize: '18px', color: 'rgba(255, 255, 255, 0.6)', marginBottom: '40px', lineHeight: '1.8' }}>Everything you need to create amazing AI avatar experiences</p>
          </div>
          <FeatureCards>
            {features.map((feature, index) => (
              <FeatureCard
                key={index}
                initial={{ opacity: 0, y: 50 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                whileHover={{ scale: 1.05 }}
              >
                {feature.image && (
                  <FeatureImage>
                    <img src={feature.image} alt={feature.title} />
                  </FeatureImage>
                )}
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
              <p style={{ fontSize: '18px', color: 'rgba(255, 255, 255, 0.6)', marginBottom: '30px', lineHeight: '1.8' }}>
                From startups to Fortune 500 companies, thousands of teams trust Athena AI for their customer communication and internal collaboration needs.
              </p>
              <ul style={{ listStyle: 'none', padding: 0, color: 'rgba(255, 255, 255, 0.8)' }}>
                <li style={{ marginBottom: '15px', fontSize: '16px' }}>✓ 10M+ conversations processed daily</li>
                <li style={{ marginBottom: '15px', fontSize: '16px' }}>✓ 99.9% uptime guarantee</li>
                <li style={{ marginBottom: '15px', fontSize: '16px' }}>✓ 50+ countries supported</li>
                <li style={{ fontSize: '16px' }}>✓ 45+ languages available</li>
              </ul>
            </UsedByText>
          </UsedByContent>
        </UsedBySection>

        <IntegrationsSection>
          <IntegrationsContent>
            <div>
              <IntegrationsTitle>Seamless Integrations</IntegrationsTitle>
              <p style={{ fontSize: '18px', color: 'rgba(255, 255, 255, 0.6)', marginBottom: '30px', lineHeight: '1.8' }}>
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
                <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#ffffff', marginBottom: '15px' }}>{feature.title}</h3>
                <p style={{ color: 'rgba(255, 255, 255, 0.6)', lineHeight: '1.6' }}>{feature.description}</p>
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
          <CTATitle>Start Building Real-Time AI Avatars Today</CTATitle>
          <CTADescription>Join thousands of enterprise customers using Athena for real-time AI interactions</CTADescription>
          <CTASectionButton onClick={() => navigate('login')}>Launch Demo</CTASectionButton>
          <CTASectionButton onClick={() => navigate('login')} style={{ marginLeft: '16px', background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.2)', boxShadow: 'none', animation: 'none' }}>
            Get Started Free
          </CTASectionButton>
        </CTASection>

        <WhyDifferentSection>
          <WhyDifferentTitle>Why We're Different</WhyDifferentTitle>
          <WhyDifferentGrid>
            <WhyDifferentCard
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              whileHover={{ scale: 1.03 }}
            >
              <div className="icon">⚡</div>
              <h3>Ultra-Low Latency</h3>
              <p>End-to-end response time under 150ms for seamless real-time conversations</p>
            </WhyDifferentCard>
            <WhyDifferentCard
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              whileHover={{ scale: 1.03 }}
            >
              <div className="icon">🧬</div>
              <h3>Modular AI Pipeline</h3>
              <p>Swap STT, LLM, TTS, and avatar engines independently for maximum flexibility</p>
            </WhyDifferentCard>
            <WhyDifferentCard
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              whileHover={{ scale: 1.03 }}
            >
              <div className="icon">🌍</div>
              <h3>Multi-Avatar System</h3>
              <p>Support multiple concurrent avatar instances with global edge deployment</p>
            </WhyDifferentCard>
          </WhyDifferentGrid>
        </WhyDifferentSection>
      </Main>
      
      <Footer>
          <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '40px', marginBottom: '40px', flexWrap: 'wrap' }}>
              <div style={{ textAlign: 'center' }}>
                <h3 style={{ fontSize: '28px', fontWeight: '800', background: 'linear-gradient(135deg, #8B5CF6, #3B82F6, #06B6D4)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text', marginBottom: '10px' }}>📚 ATHENA AI</h3>
                <p style={{ color: 'rgba(255, 255, 255, 0.5)', marginBottom: '24px', fontSize: '15px' }}>Transform your communication with photorealistic AI avatars</p>
              </div>
            </div>
            <div style={{ display: 'flex', justifyContent: 'center', gap: '32px', marginBottom: '30px', flexWrap: 'wrap' }}>
              <a href="#" style={{ color: 'rgba(255, 255, 255, 0.5)', textDecoration: 'none', fontSize: '14px', transition: 'color 0.3s' }}>GitHub</a>
              <a href="#" style={{ color: 'rgba(255, 255, 255, 0.5)', textDecoration: 'none', fontSize: '14px' }}>Documentation</a>
              <a href="#" style={{ color: 'rgba(255, 255, 255, 0.5)', textDecoration: 'none', fontSize: '14px' }}>Twitter</a>
              <a href="#" style={{ color: 'rgba(255, 255, 255, 0.5)', textDecoration: 'none', fontSize: '14px' }}>LinkedIn</a>
              <a href="#" style={{ color: 'rgba(255, 255, 255, 0.5)', textDecoration: 'none', fontSize: '14px' }}>Contact</a>
            </div>
            <div style={{ borderTop: '1px solid rgba(255, 255, 255, 0.05)', paddingTop: '24px', display: 'flex', gap: '15px', justifyContent: 'center', flexWrap: 'wrap' }}>
              <span style={{ fontSize: '13px', color: 'rgba(255, 255, 255, 0.35)' }}>© 2026 Athena AI. All rights reserved.</span>
              <span style={{ fontSize: '13px', color: 'rgba(255, 255, 255, 0.25)' }}>•</span>
              <span style={{ fontSize: '13px', color: 'rgba(255, 255, 255, 0.35)' }}>Enterprise Avatar Platform</span>
            </div>
          </div>
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
              <ChatAvatarContainer>
                <AvatarVideoContainer>
                  {isVideoEnabled ? (
                    <>
                      <VideoAvatar autoPlay muted loop>
                        <source src="/video01.mp4" type="video/mp4" />
                        <source src="/video01.mp4" type="video/mp4" />
                        Your browser does not support the video tag.
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
                      <ChatAvatarIcon>
                        <img src="/images/paul-sir-image.png" alt="Athena AI Assistant" />
                      </ChatAvatarIcon>
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
              </ChatAvatarContainer>
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
                    <ChatAvatarIcon style={{ width: '40px', height: '40px' }}>
                      <img src="/images/paul-sir-image.png" alt="Athena AI Assistant" style={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius: '50%' }} />
                    </ChatAvatarIcon>
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
                  <ChatAvatarIcon style={{ width: '40px', height: '40px' }}>
                    <img src="/images/paul-sir-image.png" alt="Athena AI Assistant" style={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius: '50%' }} />
                  </ChatAvatarIcon>
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
                onKeyDown={handleKeyPress}
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

// Wrap App in AuthProvider
function AppWithAuth() {
  return (
    <AuthProvider>
      <App />
    </AuthProvider>
  );
}

export default AppWithAuth;
