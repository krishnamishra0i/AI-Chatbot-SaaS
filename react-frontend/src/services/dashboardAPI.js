// API Integration Guide & Mock Data Service
// This file shows how to integrate the dashboard with real APIs

/**
 * Mock Data Service
 * Use this while developing or if your APIs aren't ready yet
 */
export const mockDataService = {
  // Mock Chatbots Data
  chatbots: [
    {
      id: 1,
      name: 'Customer Support v2',
      status: 'Online',
      model: 'GPT-4 Turbo',
      language: 'Multilingual',
      totalChats: '12.4k',
      dailyUsage: 84,
      icon: 'support_agent',
      color: 'primary',
    },
    {
      id: 2,
      name: 'Internal Wiki Bot',
      status: 'Offline',
      model: 'Claude 3 Opus',
      language: 'English',
      totalChats: '452',
      dailyUsage: 0,
      icon: 'smart_toy',
      color: 'slate',
    },
    {
      id: 3,
      name: 'LeadGen AI',
      status: 'Online',
      model: 'Llama 3 70B',
      language: '12+ Langs',
      totalChats: '3.1k',
      dailyUsage: 65,
      icon: 'auto_awesome',
      color: 'cyan',
    },
  ],

  // Mock API Keys Data
  apiKeys: [
    {
      id: 1,
      name: 'Production_Main_App',
      created: 'Oct 12, 2023',
      key: 'sk-•••••••••••••4k2j',
      icon: 'terminal',
    },
    {
      id: 2,
      name: 'Staging_Testing',
      created: 'Jan 05, 2024',
      key: 'sk-•••••••••••••9m1s',
      icon: 'science',
    },
    {
      id: 3,
      name: 'Data_Warehouse_Sync',
      created: 'Mar 18, 2024',
      key: 'sk-•••••••••••••2z8h',
      icon: 'webhook',
    },
  ],

  // Mock Overview Stats
  overviewStats: {
    totalChatbots: 12,
    totalAPIKeys: 24,
    monthlyMessages: '1.2M',
    currentCosts: '$284.12',
    avgLatency: '412ms',
    totalTokens: '1.42M',
  },

  // Mock Usage Analytics
  usageAnalytics: {
    tokenConsumption: [40, 60, 55, 80, 45, 70, 90, 65, 40, 85, 50, 75],
    costByModel: [
      { model: 'GPT-4 Omni', cost: '$182.40', width: '65%' },
      { model: 'Claude 3.5 Sonnet', cost: '$64.12', width: '25%' },
      { model: 'Gemini 1.5 Flash', cost: '$21.10', width: '10%' },
    ],
    recentActivity: [
      {
        method: 'POST',
        endpoint: '/v1/chat/completions',
        status: '200 OK',
        tokens: '1,242',
        latency: '320ms',
        time: '2 mins ago',
      },
      {
        method: 'GET',
        endpoint: '/v1/models/gpt-4o',
        status: '200 OK',
        tokens: '0',
        latency: '45ms',
        time: '5 mins ago',
      },
    ],
  },
};

/**
 * Real API Service
 * Replace with your actual API endpoints
 */
export const apiService = {
  // Base URL - update this to your API
  BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:5001/api',

  /**
   * Fetch all chatbots
   */
  async getChatbots() {
    try {
      const response = await fetch(`${this.BASE_URL}/chatbots`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch chatbots');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching chatbots:', error);
      // Fallback to mock data in development
      return mockDataService.chatbots;
    }
  },

  /**
   * Create a new chatbot
   */
  async createChatbot(chatbotData) {
    try {
      const response = await fetch(`${this.BASE_URL}/chatbots`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify(chatbotData),
      });

      if (!response.ok) {
        throw new Error('Failed to create chatbot');
      }

      return await response.json();
    } catch (error) {
      console.error('Error creating chatbot:', error);
      throw error;
    }
  },

  /**
   * Update a chatbot
   */
  async updateChatbot(id, chatbotData) {
    try {
      const response = await fetch(`${this.BASE_URL}/chatbots/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify(chatbotData),
      });

      if (!response.ok) {
        throw new Error('Failed to update chatbot');
      }

      return await response.json();
    } catch (error) {
      console.error('Error updating chatbot:', error);
      throw error;
    }
  },

  /**
   * Delete a chatbot
   */
  async deleteChatbot(id) {
    try {
      const response = await fetch(`${this.BASE_URL}/chatbots/${id}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to delete chatbot');
      }

      return true;
    } catch (error) {
      console.error('Error deleting chatbot:', error);
      throw error;
    }
  },

  /**
   * Fetch all API keys
   */
  async getAPIKeys() {
    try {
      const response = await fetch(`${this.BASE_URL}/api-keys`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch API keys');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching API keys:', error);
      return mockDataService.apiKeys;
    }
  },

  /**
   * Generate a new API key
   */
  async generateAPIKey(name) {
    try {
      const response = await fetch(`${this.BASE_URL}/api-keys/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({ name }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate API key');
      }

      return await response.json();
    } catch (error) {
      console.error('Error generating API key:', error);
      throw error;
    }
  },

  /**
   * Fetch usage analytics
   */
  async getUsageAnalytics(period = '30') {
    try {
      const response = await fetch(`${this.BASE_URL}/usage?period=${period}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch usage analytics');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching usage analytics:', error);
      return mockDataService.usageAnalytics;
    }
  },

  /**
   * Fetch overview statistics
   */
  async getOverviewStats() {
    try {
      const response = await fetch(`${this.BASE_URL}/overview/stats`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch overview stats');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching overview stats:', error);
      return mockDataService.overviewStats;
    }
  },
};

/**
 * Example Hook for fetching chatbots
 * Usage in component:
 * const { data: chatbots, loading, error } = useChatbots();
 */
export const useChatbots = () => {
  const [data, setData] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState(null);

  React.useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const result = await apiService.getChatbots();
        setData(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return { data, loading, error };
};

/**
 * Example Hook for fetching API keys
 */
export const useAPIKeys = () => {
  const [data, setData] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState(null);

  React.useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const result = await apiService.getAPIKeys();
        setData(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return { data, loading, error };
};

/**
 * Example Hook for fetching usage analytics
 */
export const useUsageAnalytics = (period = '30') => {
  const [data, setData] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState(null);

  React.useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const result = await apiService.getUsageAnalytics(period);
        setData(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [period]);

  return { data, loading, error };
};

import React from 'react';
