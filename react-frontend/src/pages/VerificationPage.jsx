import React, { useState, useEffect } from 'react';
import styled from 'styled-components';

const VerificationContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(
    135deg,
    rgba(96, 252, 199, 0.1) 0%,
    rgba(57, 184, 253, 0.1) 50%,
    rgba(255, 151, 47, 0.1) 100%
  ),
  #f8f9ff;
  font-family: 'Manrope', -apple-system, BlinkMacSystemFont, sans-serif;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 16px;

  &::before {
    content: '';
    position: fixed;
    top: 20%;
    left: -10%;
    width: 400px;
    height: 400px;
    background: rgba(57, 184, 253, 0.15);
    border-radius: 50%;
    filter: blur(100px);
    z-index: 0;
  }

  &::after {
    content: '';
    position: fixed;
    bottom: 20%;
    right: -10%;
    width: 400px;
    height: 400px;
    background: rgba(255, 151, 47, 0.15);
    border-radius: 50%;
    filter: blur(100px);
    z-index: 0;
  }
`;

const TopNav = styled.nav`
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 50;
  padding: 24px;
`;

const BackButton = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 9999px;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: #0b1c30;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);

  &:hover {
    background: rgba(255, 255, 255, 0.8);
  }

  &:active {
    transform: scale(0.95);
  }
`;

const MainContent = styled.main`
  flex-grow: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  max-width: 100%;
  width: 100%;
  z-index: 10;
`;

const VerificationCard = styled.div`
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 16px;
  padding: 32px;
  width: 100%;
  max-width: 500px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: -48px;
    right: -48px;
    width: 128px;
    height: 128px;
    background: rgba(0, 108, 80, 0.1);
    border-radius: 50%;
    filter: blur(100px);
  }

  &::after {
    content: '';
    position: absolute;
    bottom: -48px;
    left: -48px;
    width: 128px;
    height: 128px;
    background: rgba(57, 184, 253, 0.1);
    border-radius: 50%;
    filter: blur(100px);
  }
`;

const CardContent = styled.div`
  position: relative;
  z-index: 1;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 40px;
`;

const IconCircle = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  background: linear-gradient(to bottom right, #00c897, #39b8fd);
  border-radius: 50%;
  margin: 0 auto 24px;
  box-shadow: 0 8px 32px rgba(0, 108, 80, 0.2);
  font-size: 40px;
`;

const Title = styled.h1`
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: 30px;
  font-weight: 800;
  color: #0b1c30;
  letter-spacing: -0.5px;
  margin: 0;
  margin-bottom: 8px;
`;

const Subtitle = styled.p`
  font-size: 14px;
  color: #3c4a43;
  margin: 0;
  padding: 0 16px;
`;

const OTPForm = styled.form`
  display: flex;
  flex-direction: column;
  gap: 32px;
`;

const OTPContainer = styled.div`
  display: flex;
  justify-content: space-between;
  gap: 8px;

  @media (max-width: 640px) {
    gap: 16px;
  }
`;

const OTPInput = styled.input`
  width: 48px;
  height: 80px;
  font-size: 24px;
  font-weight: 700;
  text-align: center;
  border: 2px solid #bacac1;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.5);
  color: #0b1c30;
  transition: all 0.3s ease;

  @media (max-width: 640px) {
    width: 56px;
    height: 80px;
  }

  &::placeholder {
    color: #bacac1;
  }

  &:focus {
    outline: none;
    border-color: #39b8fd;
    box-shadow: 0 0 0 4px rgba(57, 184, 253, 0.2);
    background: rgba(255, 255, 255, 0.8);
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const VerifyButton = styled.button`
  width: 100%;
  padding: 16px 24px;
  background: #00c897;
  color: #ffffff;
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-weight: 700;
  font-size: 16px;
  border: none;
  border-radius: 9999px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 24px rgba(0, 108, 80, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;

  &:hover:not(:disabled) {
    background: #00b386;
    box-shadow: 0 8px 32px rgba(0, 108, 80, 0.3);
  }

  &:active:not(:disabled) {
    transform: scale(0.98);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const ResendContainer = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 8px;
  font-size: 14px;
  font-family: 'Inter', sans-serif;
`;

const ResendButton = styled.button`
  display: flex;
  align-items: center;
  gap: 4px;
  background: none;
  border: none;
  color: #3c4a43;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: color 0.3s ease;

  &:hover:not(:disabled) {
    color: #006c50;
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const ForgotLink = styled.a`
  color: #904d00;
  font-weight: 600;
  text-decoration: none;
  transition: opacity 0.3s ease;

  &:hover {
    opacity: 0.8;
  }
`;

const BannerBox = styled.div`
  margin-top: 32px;
  padding: 16px;
  background: rgba(57, 184, 253, 0.1);
  border-radius: 12px;
  border: 1px solid rgba(57, 184, 253, 0.2);
  display: flex;
  align-items: flex-start;
  gap: 12px;
`;

const BannerText = styled.div`
  text-align: left;
`;

const BannerTitle = styled.p`
  font-weight: 700;
  color: #004666;
  font-size: 12px;
  margin: 0 0 4px 0;
`;

const BannerSubtitle = styled.p`
  color: #004666;
  opacity: 0.7;
  font-size: 12px;
  margin: 0;
`;

const FooterLinks = styled.p`
  margin-top: 32px;
  text-align: center;
  font-size: 12px;
  color: #3c4a43;
  font-family: 'Inter', sans-serif;
`;

const FooterLink = styled.a`
  color: #006591;
  font-weight: 600;
  text-decoration: none;
  margin: 0 8px;
  transition: text-decoration 0.3s ease;

  &:hover {
    text-decoration: underline;
  }
`;

const VerificationPage = ({ onNavigate = () => {} }) => {
  const [otp, setOtp] = useState(['4', '', '', '', '', '']);
  const [timeLeft, setTimeLeft] = useState(120);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (timeLeft > 0) {
      const timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [timeLeft]);

  const handleOTPChange = (index, value) => {
    const newOtp = [...otp];
    newOtp[index] = value.slice(-1);
    setOtp(newOtp);

    if (value && index < 5) {
      document.getElementById(`otp-${index + 1}`)?.focus();
    }
  };

  const handleVerify = (e) => {
    e.preventDefault();
    setIsLoading(true);
    const otpCode = otp.join('');

    if (otpCode.length === 6) {
      setTimeout(() => {
        setIsLoading(false);
        onNavigate('dashboard');
      }, 1500);
    }
  };

  const handleResend = () => {
    setTimeLeft(120);
    setOtp(['4', '', '', '', '', '']);
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
  };

  return (
    <VerificationContainer>
      <TopNav>
        <BackButton onClick={() => onNavigate('login')}>
          ← Back to Login
        </BackButton>
      </TopNav>

      <MainContent>
        <VerificationCard>
          <CardContent>
            <div>
              <IconCircle>🔒</IconCircle>
              <Title>Security Verification</Title>
              <Subtitle>
                Enter the 6-digit code sent to your registered device to continue access.
              </Subtitle>
            </div>

            <OTPForm onSubmit={handleVerify}>
              <OTPContainer>
                {otp.map((digit, index) => (
                  <OTPInput
                    key={index}
                    id={`otp-${index}`}
                    type="text"
                    inputMode="numeric"
                    maxLength="1"
                    value={digit}
                    onChange={(e) => handleOTPChange(index, e.target.value)}
                    placeholder="·"
                  />
                ))}
              </OTPContainer>

              <ButtonGroup>
                <VerifyButton type="submit" disabled={isLoading || otp.join('').length < 6}>
                  {isLoading ? 'Verifying...' : 'Verify Identity'} →
                </VerifyButton>

                <ResendContainer>
                  <ResendButton
                    type="button"
                    onClick={handleResend}
                    disabled={timeLeft > 0}
                  >
                    🔄 {timeLeft > 0 ? `Resend (${formatTime(timeLeft)})` : 'Resend Code'}
                  </ResendButton>
                  <ForgotLink href="#">Forgot Password?</ForgotLink>
                </ResendContainer>
              </ButtonGroup>
            </OTPForm>

            <BannerBox>
              <span style={{ fontSize: '18px' }}>🛡️</span>
              <BannerText>
                <BannerTitle>End-to-End Encrypted</BannerTitle>
                <BannerSubtitle>
                  Your verification is secured with high-grade biometric matching and RSA-4096 encryption.
                </BannerSubtitle>
              </BannerText>
            </BannerBox>
          </CardContent>

          <FooterLinks>
            Need help?{' '}
            <FooterLink href="#">Contact PersonaAI Support</FooterLink>
          </FooterLinks>
        </VerificationCard>
      </MainContent>
    </VerificationContainer>
  );
};

export default VerificationPage;
