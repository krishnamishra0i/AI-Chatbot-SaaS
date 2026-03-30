import React, { useState, useEffect } from 'react';
import {
  useChatbots,
  useAPIKeys,
  useUsageAnalytics,
  useCurrentUser,
  formatNumber,
  formatCurrency,
  formatDateTime,
} from '../services/backendAPI';

export default function OverviewPage() {
  const { data: chatbots, loading: chatsLoading, error: chatsError } = useChatbots(true);
  const { data: apiKeys, loading: keysLoading } = useAPIKeys(true);
  const { data: usageData, loading: usageLoading } = useUsageAnalytics(30, true);
  const { user } = useCurrentUser();
  const [activityData, setActivityData] = useState([]);

  // Calculate totals and statistics
  const stats = {
    totalChatbots: chatbots?.length || 0,
    totalAPIKeys: apiKeys?.length || 0,
    activeChatbots: chatbots?.filter(c => c.status === 'active' || c.status === 'ACTIVE')?.length || 0,
    totalTokens: usageData?.total_tokens || 0,
    totalCost: usageData?.total_cost || 0,
    monthlyMessages: usageData?.message_count || 0,
  };

  // Simulate activity feed from recent usage
  useEffect(() => {
    if (usageData) {
      const activity = [
        {
          type: 'usage',
          message: `${formatNumber(stats.totalTokens)} tokens used this month`,
          time: 'Today',
          icon: 'trending_up',
        },
        {
          type: 'chatbot',
          message: `${stats.activeChatbots} active chatbots online`,
          time: '2 hours ago',
          icon: 'smart_toy',
        },
        {
          type: 'api',
          message: `${stats.totalAPIKeys} API keys configured`,
          time: '5 hours ago',
          icon: 'vpn_key',
        },
        {
          type: 'cost',
          message: `Monthly cost: ${formatCurrency(stats.totalCost)}`,
          time: 'This month',
          icon: 'attach_money',
        },
      ];
      setActivityData(activity);
    }
  }, [stats]);

  const renderLoadingState = () => (
    <div className="space-y-4">
      {[1, 2, 3, 4].map((i) => (
        <div key={i} className="h-24 bg-gradient-to-r from-slate-200 via-slate-100 to-slate-200 rounded-lg animate-pulse" />
      ))}
    </div>
  );

  const renderKPICard = (icon, title, value, subtitle, color = 'primary') => {
    const colorClasses = {
      primary: 'from-[#006c50] to-[#004d38]',
      secondary: 'from-[#006591] to-[#003a52]',
      tertiary: 'from-[#8b5cf6] to-[#6d28d9]',
      accent: 'from-[#f59e0b] to-[#d97706]',
    };

    return (
      <div className={`bg-gradient-to-br ${colorClasses[color] || colorClasses.primary} text-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow duration-300`}>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <p className="text-white/75 text-sm font-medium mb-2">{title}</p>
            <h3 className="text-3xl font-bold mb-2">{value}</h3>
            {subtitle && <p className="text-white/60 text-xs">{subtitle}</p>}
          </div>
          <div className="material-symbols-outlined text-5xl text-white/20">{icon}</div>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6 pb-20">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold text-slate-900">Welcome back{user?.name ? `, ${user.name.split(' ')[0]}` : ''}! 👋</h1>
        <p className="text-slate-600">Here's your AI platform overview</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {chatsLoading || usageLoading ? (
          renderLoadingState()
        ) : (
          <>
            {renderKPICard('smart_toy', 'Total Chatbots', stats.totalChatbots, `${stats.activeChatbots} active`, 'primary')}
            {renderKPICard('vpn_key', 'API Keys', stats.totalAPIKeys, 'configured', 'secondary')}
            {renderKPICard('storage', 'Tokens Used', formatNumber(stats.totalTokens), 'This month', 'tertiary')}
            {renderKPICard('trending_down', 'Total Cost', formatCurrency(stats.totalCost), 'This month', 'accent')}
          </>
        )}
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Chatbots List */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-slate-900">Active Chatbots</h2>
            <a href="#chatbots" className="text-sm font-semibold text-[#006c50] hover:text-[#004d38]">
              View All →
            </a>
          </div>

          {chatsLoading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-20 bg-slate-200 rounded-lg animate-pulse" />
              ))}
            </div>
          ) : chatsError ? (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-800 text-sm font-medium">Error loading chatbots</p>
              <p className="text-red-600 text-xs mt-1">{chatsError}</p>
            </div>
          ) : chatbots?.length === 0 ? (
            <div className="p-8 text-center bg-slate-50 rounded-xl border border-slate-200">
              <div className="material-symbols-outlined text-5xl text-slate-300 mx-auto mb-3">smart_toy</div>
              <p className="text-slate-600 font-medium">No chatbots yet</p>
              <p className="text-slate-500 text-sm">Create your first AI chatbot to get started</p>
            </div>
          ) : (
            <div className="space-y-3">
              {chatbots.slice(0, 5).map((bot, idx) => (
                <div
                  key={bot.id || idx}
                  className="bg-white border border-slate-200 rounded-lg p-4 hover:border-slate-300 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3 flex-1">
                      <div className="material-symbols-outlined text-2xl text-[#006c50]">smart_toy</div>
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold text-slate-900 truncate">{bot.name}</h3>
                        <p className="text-xs text-slate-500">Model: {bot.llm_model || 'gpt-4o-mini'}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span
                        className={`px-2 py-1 rounded text-xs font-semibold ${
                          bot.status?.toLowerCase() === 'active' || bot.status === 'ACTIVE'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}
                      >
                        {bot.status || 'Active'}
                      </span>
                      <button className="material-symbols-outlined text-slate-400 hover:text-slate-600 text-xl">
                        arrow_forward
                      </button>
                    </div>
                  </div>
                  {bot.created_at && (
                    <p className="text-xs text-slate-400 mt-2">Created: {formatDateTime(bot.created_at)}</p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Activity Feed & Stats */}
        <div className="space-y-4">
          {/* Activity Feed */}
          <div className="bg-white border border-slate-200 rounded-xl p-4">
            <h3 className="font-bold text-slate-900 mb-4">Activity Feed</h3>
            <div className="space-y-4">
              {activityData.map((item, idx) => (
                <div key={idx} className="flex gap-3 pb-4 border-b border-slate-100 last:border-0 last:pb-0">
                  <div className="material-symbols-outlined text-lg text-slate-400 flex-shrink-0">{item.icon}</div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-slate-700">{item.message}</p>
                    <p className="text-xs text-slate-400 mt-1">{item.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Quick Stats */}
          <div className="bg-gradient-to-br from-slate-900 to-slate-800 text-white rounded-xl p-4">
            <h3 className="font-bold mb-3">Platform Stats</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-400">Active Users</span>
                <span className="font-semibold">1</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Total Messages</span>
                <span className="font-semibold">{formatNumber(stats.monthlyMessages)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Plan</span>
                <span className="font-semibold capitalize">{user?.plan || 'Free'}</span>
              </div>
            </div>
          </div>

          {/* Help Card */}
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
            <div className="flex gap-2">
              <div className="material-symbols-outlined text-blue-600 flex-shrink-0">help</div>
              <div>
                <p className="text-xs font-semibold text-blue-900">Need Help?</p>
                <p className="text-xs text-blue-700 mt-1">Check our documentation or contact support</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* API Performance Chart Section */}
      <div className="bg-white border border-slate-200 rounded-xl p-6">
        <h2 className="text-xl font-bold text-slate-900 mb-4">Usage Trends</h2>
        <div className="h-64 bg-gradient-to-b from-slate-50 to-slate-100 rounded-lg flex items-center justify-center">
          <div className="text-center">
            <div className="material-symbols-outlined text-slate-400 text-5xl mx-auto mb-2">show_chart</div>
            <p className="text-slate-600 font-medium">Usage visualization</p>
            <p className="text-slate-500 text-sm">Charts will display here once you have usage data</p>
          </div>
        </div>
      </div>
    </div>
  );
}
