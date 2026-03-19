// Auth page — Login & Register with Google OAuth
import React, { useState } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import { authAPI } from '../services/api';

const AuthContainer = styled.div`
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #0B0F19;
  padding: 40px 20px;
  position: relative;
  
  &::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: 
      radial-gradient(circle at 30% 40%, rgba(139, 92, 246, 0.1) 0%, transparent 50%),
      radial-gradient(circle at 70% 60%, rgba(59, 130, 246, 0.08) 0%, transparent 50%);
    pointer-events: none;
  }
`;

const AuthCard = styled(motion.div)`
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  padding: 48px 40px;
  width: 100%;
  max-width: 440px;
  position: relative;
  z-index: 2;
`;

const Logo = styled.div`
  font-size: 28px;
  font-weight: 800;
  background: linear-gradient(135deg, #8B5CF6, #3B82F6, #06B6D4);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-align: center;
  margin-bottom: 8px;
`;

const Title = styled.h2`
  color: #fff;
  text-align: center;
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 8px;
`;

const Subtitle = styled.p`
  color: rgba(255,255,255,0.5);
  text-align: center;
  font-size: 14px;
  margin-bottom: 32px;
`;

const Input = styled.input`
  width: 100%;
  padding: 14px 16px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: #fff;
  font-size: 15px;
  margin-bottom: 16px;
  outline: none;
  transition: border-color 0.3s;
  box-sizing: border-box;

  &:focus {
    border-color: rgba(139, 92, 246, 0.5);
  }
  
  &::placeholder {
    color: rgba(255,255,255,0.3);
  }
`;

const Button = styled.button`
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #8B5CF6, #3B82F6);
  border: none;
  border-radius: 12px;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  margin-bottom: 16px;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(139, 92, 246, 0.3);
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
`;

const Divider = styled.div`
  display: flex;
  align-items: center;
  margin: 20px 0;
  gap: 12px;

  &::before, &::after {
    content: '';
    flex: 1;
    height: 1px;
    background: rgba(255,255,255,0.1);
  }
  
  span {
    color: rgba(255,255,255,0.4);
    font-size: 13px;
  }
`;

const OAuthButton = styled.button`
  width: 100%;
  padding: 14px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 12px;
  color: #fff;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;

  &:hover {
    background: rgba(255,255,255,0.1);
    border-color: rgba(255,255,255,0.2);
  }
`;

const Toggle = styled.p`
  text-align: center;
  color: rgba(255,255,255,0.5);
  font-size: 14px;
  margin-top: 24px;

  span {
    color: #8B5CF6;
    cursor: pointer;
    font-weight: 600;
    
    &:hover {
      text-decoration: underline;
    }
  }
`;

const ErrorMsg = styled.div`
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 8px;
  padding: 12px;
  color: #ef4444;
  font-size: 13px;
  margin-bottom: 16px;
  text-align: center;
`;

const BackLink = styled.div`
  text-align: center;
  margin-top: 16px;

  a {
    color: rgba(255,255,255,0.4);
    text-decoration: none;
    font-size: 13px;
    
    &:hover {
      color: rgba(255,255,255,0.7);
    }
  }
`;

export default function AuthPage({ onNavigate }) {
  const { login, register } = useAuth();
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isLogin) {
        await login(email, password);
      } else {
        await register(email, password, name);
      }
      onNavigate('home');
    } catch (err) {
      const msg = err.response?.data?.detail || 'Something went wrong. Please try again.';
      setError(msg);
    }
    setLoading(false);
  };

  const handleGoogleLogin = () => {
    window.location.href = authAPI.googleOAuthUrl();
  };

  return (
    <AuthContainer>
      <AuthCard
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Logo>ATHENA Chatbot AI</Logo>
        <Title>{isLogin ? 'Welcome Back' : 'Create Account'}</Title>
        <Subtitle>{isLogin ? 'Sign in to your account' : 'Start your AI avatar journey'}</Subtitle>

        {error && <ErrorMsg>{error}</ErrorMsg>}

        <form onSubmit={handleSubmit}>
          {!isLogin && (
            <Input
              type="text"
              placeholder="Full Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          )}
          <Input
            type="email"
            placeholder="Email Address"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <Input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={6}
          />
          <Button type="submit" disabled={loading}>
            {loading ? '...' : isLogin ? 'Sign In' : 'Create Account'}
          </Button>
        </form>

        <Divider><span>or continue with</span></Divider>

        <OAuthButton type="button" onClick={handleGoogleLogin}>
          <svg width="18" height="18" viewBox="0 0 24 24">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"/>
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
          </svg>
          Continue with Google
        </OAuthButton>

        <Toggle>
          {isLogin ? "Don't have an account? " : 'Already have an account? '}
          <span onClick={() => { setIsLogin(!isLogin); setError(''); }}>
            {isLogin ? 'Sign Up' : 'Sign In'}
          </span>
        </Toggle>

        <BackLink>
          <a href="/" onClick={(e) => { e.preventDefault(); onNavigate('home'); }}>
            ← Back to Home
          </a>
        </BackLink>
      </AuthCard>
    </AuthContainer>
  );
}
