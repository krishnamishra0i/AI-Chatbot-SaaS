// Auth context — provides authentication state to the entire app
import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('athena_token'));
  const [loading, setLoading] = useState(true);

  // Load user from token on mount
  useEffect(() => {
    const loadUser = async () => {
      if (!token) {
        setLoading(false);
        return;
      }
      try {
        const res = await authAPI.getMe();
        setUser(res.data);
      } catch {
        localStorage.removeItem('athena_token');
        localStorage.removeItem('athena_user');
        setToken(null);
        setUser(null);
      }
      setLoading(false);
    };
    loadUser();
  }, [token]);

  // Listen for forced logout (from API interceptor)
  useEffect(() => {
    const handleLogout = () => {
      setToken(null);
      setUser(null);
    };
    window.addEventListener('auth:logout', handleLogout);
    return () => window.removeEventListener('auth:logout', handleLogout);
  }, []);

  const login = useCallback(async (email, password) => {
    const res = await authAPI.login(email, password);
    const { access_token: accessToken, user: userData } = res.data;
    localStorage.setItem('athena_token', accessToken);
    localStorage.setItem('athena_user', JSON.stringify(userData));
    setToken(accessToken);
    setUser(userData);
    return userData;
  }, []);

  const register = useCallback(async (email, password, name) => {
    const res = await authAPI.register(email, password, name);
    const { access_token: accessToken, user: userData } = res.data;
    localStorage.setItem('athena_token', accessToken);
    localStorage.setItem('athena_user', JSON.stringify(userData));
    setToken(accessToken);
    setUser(userData);
    return userData;
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('athena_token');
    localStorage.removeItem('athena_user');
    setToken(null);
    setUser(null);
  }, []);

  const handleOAuthCallback = useCallback((urlToken, name, email) => {
    localStorage.setItem('athena_token', urlToken);
    const userData = { name, email };
    localStorage.setItem('athena_user', JSON.stringify(userData));
    setToken(urlToken);
    setUser(userData);
    // Fetch full user profile
    authAPI.getMe().then(res => setUser(res.data)).catch(() => {});
  }, []);

  const handleOTPVerification = useCallback((token, userData) => {
    localStorage.setItem('athena_token', token);
    localStorage.setItem('athena_user', JSON.stringify(userData));
    setToken(token);
    setUser(userData);
  }, []);

  const value = {
    user,
    token,
    loading,
    isAuthenticated: !!token && !!user,
    login,
    register,
    logout,
    handleOAuthCallback,
    handleOTPVerification,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}

export default AuthContext;
