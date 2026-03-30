/**
 * Backend API Integration Service
 * Connects React dashboard to FastAPI backend
 * All endpoints require authentication token from localStorage
 */

import React, { useState, useEffect, useCallback } from 'react';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001/api';

/**
 * Get authorization token from localStorage
 */
const getAuthToken = () => {
  return localStorage.getItem('athena_token') || localStorage.getItem('accessToken') || localStorage.getItem('token');
};

/**
 * Make authenticated API requests
 */
const fetchAPI = async (endpoint, options = {}) => {
  const token = getAuthToken();
  const url = `${API_BASE_URL}${endpoint}`;

  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let error = `API Error: ${response.status}`;
    try {
      const errorData = await response.json();
      error = errorData.detail || errorData.message || error;
    } catch (e) {
      // Response wasn't JSON
    }
    throw new Error(error);
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return { success: true };
  }

  return await response.json();
};

// ═══════════════════════════════════════════════════════════
// CHATBOT OPERATIONS
// ═══════════════════════════════════════════════════════════

export const chatbotAPI = {
  /**
   * Get all chatbots for current user
   */
  async list() {
    return fetchAPI('/chatbots');
  },

  /**
   * Get single chatbot by ID
   */
  async get(id) {
    return fetchAPI(`/chatbots/${id}`);
  },

  /**
   * Create new chatbot
   */
  async create(data) {
    return fetchAPI('/chatbots', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Update chatbot
   */
  async update(id, data) {
    return fetchAPI(`/chatbots/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },

  /**
   * Delete chatbot
   */
  async delete(id) {
    return fetchAPI(`/chatbots/${id}`, {
      method: 'DELETE',
    });
  },

  /**
   * Get chatbot sessions (usage statistics)
   */
  async getSessions(id) {
    return fetchAPI(`/chatbots/${id}/sessions`);
  },

  /**
   * Get chatbot chat history
   */
  async getChatHistory(id, limit = 50) {
    return fetchAPI(`/chatbots/${id}/messages?limit=${limit}`);
  },
};

// ═══════════════════════════════════════════════════════════
// API KEY OPERATIONS
// ═══════════════════════════════════════════════════════════

export const apiKeyAPI = {
  /**
   * Get all API keys
   */
  async list() {
    return fetchAPI('/keys');
  },

  /**
   * Create new API key
   */
  async create(name) {
    return fetchAPI('/keys', {
      method: 'POST',
      body: JSON.stringify({ name }),
    });
  },

  /**
   * Revoke/Delete API key
   */
  async delete(id) {
    return fetchAPI(`/keys/${id}`, {
      method: 'DELETE',
    });
  },
};

// ═══════════════════════════════════════════════════════════
// USAGE & ANALYTICS OPERATIONS
// ═══════════════════════════════════════════════════════════

export const usageAPI = {
  /**
   * Get usage summary for specified days
   */
  async getSummary(days = 30) {
    return fetchAPI(`/usage/summary?days=${days}`);
  },

  /**
   * Get usage breakdown by service type
   */
  async getBreakdown(days = 30) {
    return fetchAPI(`/usage/breakdown?days=${days}`);
  },

  /**
   * Get usage report with detailed statistics
   */
  async getReport(startDate, endDate) {
    const params = new URLSearchParams({
      start_date: startDate,
      end_date: endDate,
    });
    return fetchAPI(`/usage/report?${params}`);
  },

  /**
   * Get daily usage statistics
   */
  async getDailyUsage(days = 30) {
    return fetchAPI(`/usage/daily?days=${days}`);
  },

  /**
   * Get usage by chatbot
   */
  async getByService(service, days = 30) {
    return fetchAPI(`/usage/service/${service}?days=${days}`);
  },
};

// ═══════════════════════════════════════════════════════════
// USER PROFILE & ACCOUNT
// ═══════════════════════════════════════════════════════════

export const userAPI = {
  /**
   * Get current user profile
   */
  async getProfile() {
    return fetchAPI('/user/profile');
  },

  /**
   * Get current user info
   */
  async getMe() {
    return fetchAPI('/auth/me');
  },

  /**
   * Update user profile
   */
  async updateProfile(data) {
    return fetchAPI('/user/profile', {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },
};

// ═══════════════════════════════════════════════════════════
// SUBSCRIPTION & BILLING
// ═══════════════════════════════════════════════════════════

export const subscriptionAPI = {
  /**
   * Get current subscription
   */
  async getCurrent() {
    return fetchAPI('/subscriptions/current');
  },

  /**
   * Get pricing plans
   */
  async getPlans() {
    return fetchAPI('/subscriptions/plans');
  },

  /**
   * Get billing history
   */
  async getBillingHistory(limit = 12) {
    return fetchAPI(`/subscriptions/billing?limit=${limit}`);
  },
};

// ═══════════════════════════════════════════════════════════
// CUSTOM REACT HOOKS
// ═══════════════════════════════════════════════════════════

/**
 * Hook for fetching chatbots with real-time updates
 * Usage: const { data, loading, error, refetch } = useChatbots()
 */
export const useChatbots = (autoRefresh = true) => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchChatbots = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await chatbotAPI.list();
      setData(Array.isArray(result) ? result : []);
    } catch (err) {
      setError(err.message);
      setData([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchChatbots();

    if (autoRefresh) {
      // Auto-refresh every 30 seconds
      const interval = setInterval(fetchChatbots, 30000);
      return () => clearInterval(interval);
    }
  }, [fetchChatbots, autoRefresh]);

  return { data, loading, error, refetch: fetchChatbots };
};

/**
 * Hook for fetching API keys
 * Usage: const { data, loading, error, refetch } = useAPIKeys()
 */
export const useAPIKeys = (autoRefresh = true) => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchAPIKeys = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await apiKeyAPI.list();
      setData(Array.isArray(result) ? result : []);
    } catch (err) {
      setError(err.message);
      setData([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAPIKeys();

    if (autoRefresh) {
      const interval = setInterval(fetchAPIKeys, 30000);
      return () => clearInterval(interval);
    }
  }, [fetchAPIKeys, autoRefresh]);

  return { data, loading, error, refetch: fetchAPIKeys };
};

/**
 * Hook for fetching usage analytics
 * Usage: const { data, loading, error } = useUsageAnalytics(30)
 */
export const useUsageAnalytics = (days = 30, autoRefresh = true) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchUsage = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await usageAPI.getSummary(days);
      setData(result);
    } catch (err) {
      setError(err.message);
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [days]);

  useEffect(() => {
    fetchUsage();

    if (autoRefresh) {
      const interval = setInterval(fetchUsage, 60000); // Refresh every minute
      return () => clearInterval(interval);
    }
  }, [fetchUsage, autoRefresh]);

  return { data, loading, error, refetch: fetchUsage };
};

/**
 * Hook for fetching daily usage breakdown
 * Usage: const { data, loading, error } = useDailyUsage(30)
 */
export const useDailyUsage = (days = 30) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const result = await usageAPI.getDailyUsage(days);
        setData(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [days]);

  return { data, loading, error };
};

/**
 * Hook for fetching current user
 * Usage: const { user, loading, error } = useCurrentUser()
 */
export const useCurrentUser = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        setLoading(true);
        const result = await userAPI.getMe();
        setUser(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, []);

  return { user, loading, error };
};

/**
 * Hook for subscription/billing info
 * Usage: const { subscription, loading } = useSubscription()
 */
export const useSubscription = () => {
  const [subscription, setSubscription] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSubscription = async () => {
      try {
        setLoading(true);
        const result = await subscriptionAPI.getCurrent();
        setSubscription(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchSubscription();
  }, []);

  return { subscription, loading, error };
};

// ═══════════════════════════════════════════════════════════
// HELPER FUNCTIONS
// ═══════════════════════════════════════════════════════════

/**
 * Format date to readable format
 */
export const formatDate = (date) => {
  if (!date) return 'Unknown';
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

/**
 * Format time to readable format
 */
export const formatTime = (date) => {
  if (!date) return 'Unknown';
  return new Date(date).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  });
};

/**
 * Format datetime to short format
 */
export const formatDateTime = (date) => {
  if (!date) return 'Unknown';
  return new Date(date).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

/**
 * Format large numbers (1000 -> 1K, 1000000 -> 1M)
 */
export const formatNumber = (num) => {
  if (!num) return '0';
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
  return num.toString();
};

/**
 * Format currency
 */
export const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
};

/**
 * Get status color for UI
 */
export const getStatusColor = (status) => {
  switch (status?.toLowerCase()) {
    case 'active':
    case 'online':
    case 'success':
      return 'bg-green-100 text-green-800';
    case 'paused':
    case 'offline':
    case 'pending':
      return 'bg-yellow-100 text-yellow-800';
    case 'archived':
    case 'error':
    case 'inactive':
      return 'bg-red-100 text-red-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

/**
 * Calculate percentage
 */
export const calculatePercentage = (value, total) => {
  if (total === 0) return 0;
  return Math.round((value / total) * 100);
};

/**
 * Truncate text
 */
export const truncateText = (text, length = 50) => {
  if (!text || text.length <= length) return text;
  return text.substring(0, length) + '...';
};
