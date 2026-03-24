import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import axios from 'axios';

const Container = styled.div`
  max-width: 900px;
  margin: 40px auto;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
`;

const Section = styled.div`
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  background: #f9f9f9;
`;

const Title = styled.h2`
  color: #333;
  margin-top: 0;
`;

const Code = styled.pre`
  background: #262626;
  color: #00ff00;
  padding: 15px;
  border-radius: 6px;
  overflow-x: auto;
  font-size: 12px;
`;

const Button = styled.button`
  background: #0066cc;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  margin-right: 10px;
  
  &:hover {
    background: #0052a3;
  }
`;

const Status = styled.div`
  padding: 15px;
  border-radius: 4px;
  margin-top: 15px;
  font-weight: 500;
  
  &.success {
    background: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
  }
  
  &.error {
    background: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
  }
  
  &.warning {
    background: #fff3cd;
    color: #856404;
    border: 1px solid #ffeaa7;
  }
  
  &.info {
    background: #d1ecf1;
    color: #0c5460;
    border: 1px solid #bee5eb;
  }
`;

export default function DebugAuthPage() {
  const [token, setToken] = useState('');
  const [message, setMessage] = useState('');
  const [outputLog, setOutputLog] = useState('');
  const API_BASE_URL = 'http://localhost:5000';

  const log = (msg, type = 'info') => {
    console.log(`[${type.toUpperCase()}]`, msg);
    setOutputLog(prev => `${prev}\n[${type}] ${msg}`);
  };

  useEffect(() => {
    const storedToken = localStorage.getItem('athena_token');
    setToken(storedToken || '');
    if (storedToken) {
      log(`✓ Token found in localStorage (${storedToken.substring(0, 20)}...)`, 'success');
    } else {
      log('✗ No token found in localStorage', 'warning');
    }
  }, []);

  const testGetMe = async () => {
    setOutputLog('');
    log('Testing GET /api/auth/me...', 'info');
    
    const currentToken = localStorage.getItem('athena_token');
    if (!currentToken) {
      log('✗ No token found', 'error');
      return;
    }

    try {
      const response = await axios.get(`${API_BASE_URL}/api/auth/me`, {
        headers: {
          'Authorization': `Bearer ${currentToken}`,
          'Content-Type': 'application/json',
        },
      });
      log('✓ GET /api/auth/me succeeded', 'success');
      log(`Response: ${JSON.stringify(response.data, null, 2)}`, 'info');
    } catch (error) {
      log(`✗ GET /api/auth/me failed: ${error.response?.status || error.message}`, 'error');
      log(`Error: ${JSON.stringify(error.response?.data, null, 2)}`, 'error');
      log(`Headers sent: ${JSON.stringify(error.config?.headers, null, 2)}`, 'warning');
    }
  };

  const testCreateChatbot = async () => {
    setOutputLog('');
    log('Testing POST /api/chatbots/...', 'info');
    
    const currentToken = localStorage.getItem('athena_token');
    if (!currentToken) {
      log('✗ No token found', 'error');
      return;
    }

    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/chatbots/`,
        {
          name: 'Debug Test Bot',
          system_prompt: 'You are a helpful assistant.',
          llm_model: 'gpt-4o-mini',
          voice_id: 'default',
          avatar_id: 'default',
          temperature: 0.7,
          max_tokens: 1000,
        },
        {
          headers: {
            'Authorization': `Bearer ${currentToken}`,
            'Content-Type': 'application/json',
          },
        }
      );
      log('✓ POST /api/chatbots/ succeeded', 'success');
      log(`Response: ${JSON.stringify(response.data, null, 2)}`, 'info');
    } catch (error) {
      log(`✗ POST /api/chatbots/ failed: ${error.response?.status || error.message}`, 'error');
      log(`Error: ${JSON.stringify(error.response?.data, null, 2)}`, 'error');
      log(`Request headers: ${JSON.stringify(error.config?.headers, null, 2)}`, 'warning');
    }
  };

  const testListChatbots = async () => {
    setOutputLog('');
    log('Testing GET /api/chatbots/...', 'info');
    
    const currentToken = localStorage.getItem('athena_token');
    if (!currentToken) {
      log('✗ No token found', 'error');
      return;
    }

    try {
      const response = await axios.get(`${API_BASE_URL}/api/chatbots/`, {
        headers: {
          'Authorization': `Bearer ${currentToken}`,
          'Content-Type': 'application/json',
        },
      });
      log('✓ GET /api/chatbots/ succeeded', 'success');
      log(`Count: ${response.data.length} chatbots`, 'info');
      log(`Response: ${JSON.stringify(response.data, null, 2)}`, 'info');
    } catch (error) {
      log(`✗ GET /api/chatbots/ failed: ${error.response?.status || error.message}`, 'error');
      log(`Error: ${JSON.stringify(error.response?.data, null, 2)}`, 'error');
    }
  };

  const clearToken = () => {
    localStorage.removeItem('athena_token');
    localStorage.removeItem('athena_user');
    setToken('');
    setOutputLog('');
    log('✓ Token cleared from localStorage', 'success');
  };

  const checkInterceptor = () => {
    setOutputLog('');
    log('Checking axios interceptors...', 'info');
    log('Note: Open browser DevTools > Console to see interceptor logs', 'info');
    
    // Make a test request
    const api = axios.create({
      baseURL: API_BASE_URL,
      headers: { 'Content-Type': 'application/json' },
    });

    // Add interceptor like in api.js
    api.interceptors.request.use((config) => {
      const token = localStorage.getItem('athena_token');
      console.log('[API] Token from localStorage:', token ? `${token.substring(0, 20)}...` : 'NOT FOUND');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
        console.log('[API] Authorization header set');
      } else {
        console.warn('[API] NO TOKEN - Request will be sent without Authorization header');
      }
      return config;
    });

    api.get('/api/auth/me')
      .then(res => log(`✓ Interceptor test successful: ${JSON.stringify(res.data)}`, 'success'))
      .catch(err => log(`✗ Interceptor test failed: ${err.response?.status} - ${JSON.stringify(err.response?.data)}`, 'error'));
  };

  return (
    <Container>
      <h1>🔍 Debug Authentication Flow</h1>

      <Section>
        <Title>📍 Current Token Status</Title>
        <Status className={token ? 'success' : 'warning'}>
          {token ? `Token exists: ${token.substring(0, 30)}...` : 'No token in localStorage'}
        </Status>
        <Button onClick={() => {
          const t = localStorage.getItem('athena_token');
          setMessage(t ? `Token: ${t}` : 'No token');
        }}>
          Copy Token to Console
        </Button>
        <Button onClick={clearToken}>Clear Token</Button>
      </Section>

      <Section>
        <Title>🧪 API Tests</Title>
        <div>
          <Button onClick={testGetMe}>Test GET /api/auth/me</Button>
          <Button onClick={testListChatbots}>Test GET /api/chatbots/</Button>
          <Button onClick={testCreateChatbot}>Test POST /api/chatbots/</Button>
          <Button onClick={checkInterceptor}>Check Interceptor</Button>
        </div>
      </Section>

      <Section>
        <Title>📋 Output Log</Title>
        <Code>{outputLog || 'Run a test above to see output...'}</Code>
      </Section>

      <Section>
        <Title>💡 Instructions</Title>
        <ol>
          <li>Make sure token is shown above (log in if empty)</li>
          <li>Open DevTools (F12) and go to Console tab</li>
          <li>Click "Test GET /api/auth/me" button</li>
          <li>Check console for [API] logs and Network tab for request headers</li>
          <li>Verify Authorization header is present: <code>Authorization: Bearer ...</code></li>
        </ol>
      </Section>
    </Container>
  );
}
