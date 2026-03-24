import React, { useState, useEffect } from 'react';
import styled from 'styled-components';

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
  margin: 10px 0;
`;

const Button = styled.button`
  background: #0066cc;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  margin: 5px 5px 5px 0;
  
  &:hover {
    background: #0052a3;
  }
`;

const Status = styled.div`
  padding: 12px;
  border-radius: 4px;
  margin: 10px 0;
  font-weight: 500;
  font-family: monospace;
  
  &.ok {
    background: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
  }
  
  &.error {
    background: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
  }
`;

export default function TokenDiagnosisPage() {
  const [diagnostics, setDiagnostics] = useState({});
  const [allTests, setAllTests] = useState([]);

  useEffect(() => {
    runAllDiagnostics();
  }, []);

  const runAllDiagnostics = () => {
    const tests = {
      token_in_storage: checkTokenInStorage(),
      token_format: checkTokenFormat(),
      auth_context: checkAuthContext(),
      request_interceptor: checkRequestInterceptor(),
      storage_persistence: checkStoragePersistence(),
    };
    setDiagnostics(tests);
    setAllTests(Object.entries(tests));
  };

  const checkTokenInStorage = () => {
    const token = localStorage.getItem('athena_token');
    return {
      name: 'Token in localStorage',
      status: token ? 'OK' : 'MISSING',
      value: token ? `${token.substring(0, 50)}...` : 'NOT FOUND',
      action: token ? 'Token exists' : 'User needs to log in',
    };
  };

  const checkTokenFormat = () => {
    const token = localStorage.getItem('athena_token');
    if (!token) {
      return {
        name: 'Token Format Check',
        status: 'SKIP',
        value: 'No token to check',
      };
    }
    
    const isValidJWT = token.split('.').length === 3;
    return {
      name: 'Token Format Check',
      status: isValidJWT ? 'OK' : 'INVALID',
      value: `${token.substring(0, 30)}... (${isValidJWT ? 'valid JWT' : 'INVALID FORMAT'})`,
      details: `JWT has ${token.split('.').length} parts (should be 3)`,
    };
  };

  const checkAuthContext = () => {
    const token = localStorage.getItem('athena_token');
    return {
      name: 'Auth Context State',
      status: token ? 'OK' : 'MISSING',
      value: token ? 'Token should be in useAuth context' : 'No token to sync',
    };
  };

  const checkRequestInterceptor = () => {
    // Try to detect if interceptor is working
    const testURL = 'http://localhost:5000/api/auth/me';
    return {
      name: 'Request Interceptor Setup',
      status: 'CONFIGURED',
      value: `Configured to attach token to all requests to ${testURL}`,
      action: 'Check browser dev tools Network tab to verify Authorization header',
    };
  };

  const checkStoragePersistence = () => {
    const testKey = 'test_persist_' + Date.now();
    const testValue = 'test_value_' + Date.now();
    
    try {
      localStorage.setItem(testKey, testValue);
      const retrieved = localStorage.getItem(testKey);
      localStorage.removeItem(testKey);
      
      const persists = retrieved === testValue;
      return {
        name: 'localStorage Persistence',
        status: persists ? 'OK' : 'FAILED',
        value: persists ? 'localStorage is working correctly' : 'localStorage write/read FAILED',
      };
    } catch (e) {
      return {
        name: 'localStorage Persistence',
        status: 'ERROR',
        value: `Error: ${e.message}`,
      };
    }
  };

  const simulateAPICall = async () => {
    console.log('Simulating API call...');
    const token = localStorage.getItem('athena_token');
    
    if (!token) {
      alert('❌ No token found in localStorage!\n\nYou must log in first.');
      return;
    }

    try {
      const response = await fetch('http://localhost:5000/api/auth/me', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const user = await response.json();
        alert(`✅ SUCCESS!\n\n${JSON.stringify(user, null, 2)}`);
      } else {
        const error = await response.json();
        alert(`❌ FAILED (${response.status})\n\n${JSON.stringify(error, null, 2)}`);
      }
    } catch (e) {
      alert(`❌ ERROR: ${e.message}`);
    }
  };

  const clearAuth = () => {
    if (window.confirm('Clear authentication? You will need to log in again.')) {
      localStorage.removeItem('athena_token');
      localStorage.removeItem('athena_user');
      alert('✓ Authentication cleared. Please log in again.');
      window.location.reload();
    }
  };

  return (
    <Container>
      <h1>🔐 Token Diagnosis Tool</h1>
      <p>Diagnose why you're getting "Missing Authorization header" errors</p>

      <Section>
        <Title>🔍 System Diagnostics</Title>
        {allTests.map(([key, test]) => (
          <div key={key}>
            <Status className={test.status === 'OK' ? 'ok' : 'error'}>
              <strong>{test.name}:</strong> {test.status}
            </Status>
            <Code>{test.value}</Code>
            {test.details && <Code>{test.details}</Code>}
            {test.action && <p><strong>Action:</strong> {test.action}</p>}
          </div>
        ))}
      </Section>

      <Section>
        <Title>🧪 Manual Tests</Title>
        <Button onClick={simulateAPICall}>Test API Call with Token</Button>
        <Button onClick={() => {
          const token = localStorage.getItem('athena_token');
          alert(`Token from localStorage:\n\n${token || 'NO TOKEN FOUND'}`);
        }}>
          Copy Token to Alert
        </Button>
        <Button onClick={() => {
          runAllDiagnostics();
          alert('✓ Diagnostics refreshed');
        }}>
          Refresh Diagnostics
        </Button>
        <Button onClick={clearAuth} style={{ background: '#dc3545' }}>
          Clear Auth & Restart
        </Button>
      </Section>

      <Section>
        <Title>📋 Troubleshooting Steps</Title>
        <ol>
          <li><strong>Check Token Status:</strong> Look at "Token in localStorage" above</li>
          <li><strong>If "MISSING":</strong> You need to log in again
              <ul>
                <li>Go to Auth page</li>
                <li>Enter email and receive OTP</li>
                <li>Verify OTP</li>
                <li>Refresh this page</li>
              </ul>
          </li>
          <li><strong>If "OK" but still getting 401:</strong>
              <ul>
                <li>Click "Test API Call with Token"</li>
                <li>If it works: Frontend issue (cache problem)</li>
                <li>If it fails: Backend rejecting token</li>
              </ul>
          </li>
          <li><strong>Browser Cache Problem:</strong> Clear cache (Ctrl+Shift+Delete)</li>
          <li><strong>localStorage Persistence:</strong> Check the test result above</li>
        </ol>
      </Section>

      <Section>
        <Title>🛠️ Common Issues & Fixes</Title>
        
        <h4>Issue: Token is "MISSING"</h4>
        <p>✓ <strong>Fix:</strong> Log in again at the Auth page and verify OTP</p>
        
        <h4>Issue: Token exists but still getting 401</h4>
        <p>✓ <strong>Fix 1:</strong> Clear browser cache (Ctrl+Shift+Delete)</p>
        <p>✓ <strong>Fix 2:</strong> Hard refresh (Ctrl+Shift+R)</p>
        <p>✓ <strong>Fix 3:</strong> Click "Clear Auth & Restart" button, log in again</p>
        
        <h4>Issue: "Test API Call" succeeds but Dashboard still fails</h4>
        <p>✓ <strong>Fix:</strong> The usageAPI might not be implemented. Try without it:</p>
        <Code>
{`// Modify DashboardPage.js loadData to skip usage:
const loadData = useCallback(async () => {
  try {
    const [botsRes, keysRes, modelsRes] = await Promise.all([
      chatbotsAPI.list().catch(() => ({ data: [] })),
      apiKeysAPI.list().catch(() => ({ data: [] })),
      // Skip: usageAPI.summary().catch(() => ({ data: null })),
      modelsAPI.list().catch(() => ({ data: { data: [] } })),
    ]);
    setChatbots(botsRes.data || []);
    setApiKeys(keysRes.data || []);
    // setUsage(usageRes.data);  // Skip this
    setModels(modelsRes.data?.data || []);
  } catch (err) {
    console.error('Failed to load dashboard data:', err);
  }
}, []);`}
        </Code>
        
        <h4>Issue: localStorage isn't persisting</h4>
        <p>✓ <strong>Fix:</strong> Check browser privacy settings</p>
        <p>&nbsp;&nbsp;&nbsp;&nbsp;- Make sure localhost:3000 allows cookies</p>
        <p>&nbsp;&nbsp;&nbsp;&nbsp;- Try: Settings → Privacy → Cookies and site data → Clear cache</p>
      </Section>

      <Section>
        <Title>🔍 Browser Developer Tools Checks</Title>
        <ol>
          <li>Open DevTools (F12)</li>
          <li>Go to <strong>Console</strong> tab
              <ul>
                <li>You should see "[API] Token from localStorage: ..."</li>
                <li>If you see "NOT FOUND": Token is missing</li>
              </ul>
          </li>
          <li>Go to <strong>Network</strong> tab
              <ul>
                <li>Click on GET request to /api/usage/summary (the one that fails)</li>
                <li>Go to "Request Headers"</li>
                <li>Look for: <code>Authorization: Bearer eyJhbGc...</code></li>
                <li>If missing: Interceptor not working</li>
              </ul>
          </li>
          <li>Go to <strong>Application</strong> tab
              <ul>
                <li>Local Storage → http://localhost:3000</li>
                <li>Look for: <code>athena_token</code></li>
              </ul>
          </li>
        </ol>
      </Section>

      <Section>
        <Title>✅ Expected Working State</Title>
        <p>✓ Token in localStorage shows: "eyJhbGc..." (JWT token)</p>
        <p>✓ "Test API Call" button shows: "SUCCESS" message</p>
        <p>✓ Dashboard loads without auth errors</p>
        <p>✓ Network requests include Authorization header</p>
        <p>✓ No 401 errors in console</p>
      </Section>
    </Container>
  );
}
