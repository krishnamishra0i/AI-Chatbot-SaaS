// Passwordless OTP-Only Authentication Page
// No passwords, simple 2-step OTP flow: email → OTP code
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

const OTPInput = styled(Input)`
  font-size: 32px;
  letter-spacing: 12px;
  text-align: center;
  font-weight: bold;
  font-family: 'Courier New', monospace;
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

  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(139, 92, 246, 0.3);
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
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

const SuccessMsg = styled.div`
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.3);
  border-radius: 8px;
  padding: 12px;
  color: #22c55e;
  font-size: 13px;
  margin-bottom: 16px;
  text-align: center;
`;

const BackButton = styled.button`
  color: #8B5CF6;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 14px;
  text-decoration: underline;
  
  &:hover {
    opacity: 0.8;
  }
`;

const InfoBox = styled.div`
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 8px;
  padding: 12px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
  margin-bottom: 24px;
  text-align: center;
`;

export default function AuthPage({ onNavigate }) {
  const [step, setStep] = useState('email'); // 'email' or 'otp'
  const [email, setEmail] = useState('');
  const [otp, setOtp] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  // Step 1: Send OTP to email
  const handleSendOTP = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      if (!email || !email.includes('@')) {
        throw new Error('Please enter a valid email');
      }

      await authAPI.sendOtp(email);
      setSuccess(`✓ OTP sent to ${email}. Check your email!`);
      setStep('otp');
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Failed to send OTP';
      setError(msg);
    }
    setLoading(false);
  };

  // Step 2: Verify OTP and login
  const handleVerifyOTP = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      if (otp.length !== 6) {
        throw new Error('Please enter a 6-digit code');
      }

      const res = await authAPI.verifyOtp(email, otp);
      const { access_token, user } = res.data;

      // Store authentication
      localStorage.setItem('athena_token', access_token);
      localStorage.setItem('athena_user', JSON.stringify(user));

      setSuccess('✓ Login successful! Redirecting...');
      
      // Redirect to dashboard after short delay
      setTimeout(() => {
        onNavigate('dashboard');
      }, 500);
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Invalid OTP code';
      setError(msg);
    }
    setLoading(false);
  };

  return (
    <AuthContainer>
      <AuthCard
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Logo>ATHENA AI</Logo>
        
        {step === 'email' ? (
          <>
            <Title>Passwordless Login</Title>
            <Subtitle>Enter your email to receive a login code</Subtitle>
            
            <InfoBox>
              🔐 No password needed. We'll send a code to your email.
            </InfoBox>

            {error && <ErrorMsg>{error}</ErrorMsg>}
            {success && <SuccessMsg>{success}</SuccessMsg>}

            <form onSubmit={handleSendOTP}>
              <Input
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={loading}
                autoFocus
              />
              <Button type="submit" disabled={loading || !email}>
                {loading ? '⏳ Sending...' : '📧 Send Login Code'}
              </Button>
            </form>
          </>
        ) : (
          <>
            <Title>Enter OTP Code</Title>
            <Subtitle>Check your email for the 6-digit code</Subtitle>

            {error && <ErrorMsg>{error}</ErrorMsg>}
            {success && <SuccessMsg>{success}</SuccessMsg>}

            <form onSubmit={handleVerifyOTP}>
              <OTPInput
                type="text"
                placeholder="000000"
                value={otp}
                onChange={(e) => {
                  const val = e.target.value.replace(/\D/g, '').slice(0, 6);
                  setOtp(val);
                }}
                maxLength="6"
                disabled={loading}
                autoFocus
              />
              <Button type="submit" disabled={loading || otp.length !== 6}>
                {loading ? '⏳ Verifying...' : '✓ Verify & Login'}
              </Button>
            </form>

            <div style={{ textAlign: 'center' }}>
              <BackButton onClick={() => { setStep('email'); setOtp(''); setError(''); }}>
                ← Back to email
              </BackButton>
            </div>
          </>
        )}
      </AuthCard>
    </AuthContainer>
  );
}
