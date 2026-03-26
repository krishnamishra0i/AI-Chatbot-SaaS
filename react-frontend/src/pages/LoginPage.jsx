import React, { useState } from 'react';
import styled from 'styled-components';

const Page = styled.div`
  min-height: 100vh;
  background: #f8f9ff;
  color: #0b1c30;
  font-family: 'Manrope', -apple-system, BlinkMacSystemFont, sans-serif;
  overflow: hidden;
  position: relative;
`;

const BackNav = styled.nav`
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 20;
  padding: 24px;
`;

const HomeButton = styled.button`
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  border-radius: 9999px;
  border: 1px solid rgba(255, 255, 255, 0.4);
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(16px);
  color: #0b1c30;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
`;

const Main = styled.main`
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 110px 16px 36px;
  position: relative;
  background:
    radial-gradient(at 0% 0%, #60fcc7 0%, transparent 50%),
    radial-gradient(at 100% 0%, #39b8fd 0%, transparent 50%),
    radial-gradient(at 100% 100%, #ff972f 0%, transparent 50%),
    radial-gradient(at 0% 100%, #3adfac 0%, transparent 50%);
`;

const TopDeco = styled.div`
  position: fixed;
  top: 48px;
  right: 48px;
  width: 128px;
  height: 128px;
  opacity: 0.2;
  border-radius: 50%;
  border: 20px solid #ffdcc2;
  pointer-events: none;
`;

const BottomDeco = styled.div`
  position: fixed;
  bottom: 52px;
  left: 52px;
  width: 96px;
  height: 96px;
  opacity: 0.2;
  border-radius: 16px;
  background: #39b8fd;
  transform: rotate(45deg);
  pointer-events: none;
`;

const Content = styled.div`
  width: 100%;
  max-width: 640px;
  z-index: 2;
`;

const Card = styled.div`
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.4);
  border-radius: 24px;
  box-shadow: 0 24px 48px rgba(11, 28, 48, 0.16);
  padding: 28px;
  display: flex;
  flex-direction: column;
  gap: 24px;

  @media (min-width: 768px) {
    padding: 36px 42px;
  }
`;

const BrandBlock = styled.div`
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: center;

  .icon {
    width: 64px;
    height: 64px;
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #00c897, #39b8fd);
    color: #fff;
    font-size: 30px;
    box-shadow: 0 10px 20px rgba(0, 108, 80, 0.2);
  }

  h1 {
    margin: 0;
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 38px;
    line-height: 1.1;
    font-weight: 800;
    color: #0b1c30;
  }

  p {
    margin: 0;
    max-width: 320px;
    color: #3c4a43;
    font-size: 16px;
  }
`;

const FormSection = styled.form`
  display: flex;
  flex-direction: column;
  gap: 18px;
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;

  label {
    margin-left: 8px;
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    font-weight: 700;
    color: #0b1c30;
  }

  .input-wrap {
    position: relative;
  }

  .prefix {
    position: absolute;
    left: 16px;
    top: 50%;
    transform: translateY(-50%);
    color: #6c7a73;
    font-size: 24px;
  }

  input {
    width: 100%;
    height: 56px;
    border: none;
    border-radius: 9999px;
    background: rgba(255, 255, 255, 0.5);
    box-shadow: inset 0 0 0 1px rgba(108, 122, 115, 0.2);
    padding: 0 16px 0 50px;
    font-size: 16px;
    color: #0b1c30;

    &::placeholder {
      color: #6c7a73;
    }

    &:focus {
      outline: none;
      box-shadow: inset 0 0 0 2px rgba(0, 200, 151, 0.45);
      background: rgba(255, 255, 255, 0.75);
    }
  }
`;

const ContinueButton = styled.button`
  width: 100%;
  height: 56px;
  border: none;
  border-radius: 9999px;
  background: #00c897;
  color: #004d38;
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: 22px;
  font-weight: 800;
  cursor: pointer;
  box-shadow: 0 10px 24px rgba(0, 108, 80, 0.2);

  &:hover:not(:disabled) {
    opacity: 0.92;
  }

  &:active:not(:disabled) {
    transform: scale(0.98);
  }

  &:disabled {
    opacity: 0.65;
    cursor: not-allowed;
  }
`;

const Divider = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;

  &::before,
  &::after {
    content: '';
    flex: 1;
    height: 1px;
    background: rgba(108, 122, 115, 0.22);
  }

  span {
    font-family: 'Inter', sans-serif;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #6c7a73;
  }
`;

const SocialGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
`;

const SocialButton = styled.button`
  height: 56px;
  border-radius: 9999px;
  border: 1px solid rgba(108, 122, 115, 0.2);
  background: rgba(255, 255, 255, 0.6);
  color: #0b1c30;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
`;

const SignupText = styled.p`
  margin: 0;
  text-align: center;
  color: #3c4a43;
  font-size: 15px;

  span {
    color: #006591;
    font-weight: 700;
    cursor: pointer;
  }
`;

const FooterRow = styled.div`
  margin-top: 18px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: rgba(60, 74, 67, 0.75);
  font-size: 13px;

  button {
    border: none;
    background: transparent;
    color: rgba(60, 74, 67, 0.75);
    font-size: 13px;
    cursor: pointer;
    padding: 0;
  }
`;

const LoginPage = ({ onNavigate = () => {} }) => {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleContinue = (e) => {
    e.preventDefault();
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      onNavigate('verification');
    }, 800);
  };

  return (
    <Page>
      <BackNav>
        <HomeButton type="button" onClick={() => onNavigate('home')}>
          <span>←</span>
          <span>Home</span>
        </HomeButton>
      </BackNav>

      <Main>
        <TopDeco />
        <BottomDeco />

        <Content>
          <Card>
            <BrandBlock>
              <div className="icon">◍</div>
              <h1>PersonaAI</h1>
              <p>Secure authentication for your digital identity.</p>
            </BrandBlock>

            <FormSection onSubmit={handleContinue}>
              <FormGroup>
                <label>Email or ID</label>
                <div className="input-wrap">
                  <span className="prefix">@</span>
                  <input
                    type="email"
                    placeholder="name@company.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                  />
                </div>
              </FormGroup>

              <ContinueButton type="submit" disabled={isLoading}>
                {isLoading ? 'Continue...' : 'Continue →'}
              </ContinueButton>
            </FormSection>

            <Divider>
              <span>or continue with</span>
            </Divider>

            <SocialGrid>
              <SocialButton type="button">
                <span>G</span>
                <span>Google</span>
              </SocialButton>
              <SocialButton type="button">
                <span></span>
                <span>Apple</span>
              </SocialButton>
            </SocialGrid>

            <SignupText>
              Don't have an account? <span onClick={() => onNavigate('signup')}>Sign up</span>
            </SignupText>
          </Card>

          <FooterRow>
            <div>
              <button type="button" onClick={() => onNavigate('home')}>Privacy Policy</button>
              <span style={{ margin: '0 8px' }} />
              <button type="button" onClick={() => onNavigate('home')}>Terms of Service</button>
            </div>
            <span>© 2024 PersonaAI</span>
          </FooterRow>
        </Content>
      </Main>
    </Page>
  );
};

export default LoginPage;
