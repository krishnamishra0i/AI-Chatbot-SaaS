import React, { useState } from 'react';
import { useUsageAnalytics, useDailyUsage, formatNumber, formatCurrency, formatDateTime } from '../services/backendAPI';

export default function UsageAnalyticsPageNew() {
  const { data: usageData, loading: usageLoading } = useUsageAnalytics(30, true);
  const { data: dailyData, loading: dailyLoading } = useDailyUsage(30);
  const [selectedPeriod, setSelectedPeriod] = useState('30');
  const [expandedBot, setExpandedBot] = useState(null);

  // Calculate stats
  const stats = {
    totalTokens: usageData?.total_tokens || 0,
    totalCost: usageData?.total_cost || 0,
    thisMonthMessages: usageData?.message_count || 0,
    avgTokensPerDay: usageData?.avg_tokens_per_day || 0,
    dailyLimit: 10000,
  };

  // Mock monthly breakdown by service (replace with real data from backend)
  const serviceBreakdown = [
    { service: 'Chat (GPT-4o)', tokens: 45000, cost: 125.50, percentage: 62 },
    { service: 'Chat (Llama 3)', tokens: 22000, cost: 48.30, percentage: 30 },
    { service: 'TTS (Text-to-Speech)', tokens: 5000, cost: 15.20, percentage: 7 },
    { service: 'STT (Speech-to-Text)', tokens: 1000, cost: 3.00, percentage: 1 },
  ];

  // Mock recent activity (replace with real data)
  const recentActivity = [
    {
      method: 'POST',
      endpoint: '/api/chat/completions',
      status: '200 OK',
      tokens: '1,242',
      latency: '320ms',
      time: '2 mins ago',
      service: 'Chat',
    },
    {
      method: 'POST',
      endpoint: '/api/tts',
      status: '200 OK',
      tokens: '0',
      latency: '1200ms',
      time: '5 mins ago',
      service: 'TTS',
    },
    {
      method: 'POST',
      endpoint: '/api/stt',
      status: '200 OK',
      tokens: '0',
      latency: '850ms',
      time: '12 mins ago',
      service: 'STT',
    },
  ];

  const renderChart = (data, max, label) => {
    return (
      <div className="flex items-end gap-2 h-32 bg-slate-50 p-4 rounded-lg">
        {data.map((value, idx) => (
          <div
            key={idx}
            className="flex-1 bg-gradient-to-t from-[#006c50] to-[#00a858] rounded-t opacity-80 hover:opacity-100 transition-opacity group"
            style={{ height: `${(value / max) * 100}%` }}
          >
            <div className="hidden group-hover:block absolute bg-slate-900 text-white text-xs px-2 py-1 rounded whitespace-nowrap pointer-events-none">
              {value}
            </div>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="space-y-6 pb-20">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Usage Analytics</h1>
          <p className="text-slate-600 mt-1">Track your API usage and costs</p>
        </div>
        <div className="flex gap-2">
          {['7', '30', '90'].map((period) => (
            <button
              key={period}
              onClick={() => setSelectedPeriod(period)}
              className={`px-4 py-2 rounded-lg font-semibold transition-colors ${
                selectedPeriod === period
                  ? 'bg-[#006c50] text-white'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              {period}d
            </button>
          ))}
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white border border-slate-200 rounded-lg p-4">
          <p className="text-slate-600 text-sm font-medium mb-1">Total Tokens</p>
          <p className="text-3xl font-bold text-slate-900">{formatNumber(stats.totalTokens)}</p>
          <p className="text-xs text-slate-500 mt-2">This period</p>
        </div>

        <div className="bg-white border border-slate-200 rounded-lg p-4">
          <p className="text-slate-600 text-sm font-medium mb-1">Total Cost</p>
          <p className="text-3xl font-bold text-slate-900">{formatCurrency(stats.totalCost)}</p>
          <p className="text-xs text-slate-500 mt-2">Estimated</p>
        </div>

        <div className="bg-white border border-slate-200 rounded-lg p-4">
          <p className="text-slate-600 text-sm font-medium mb-1">Messages</p>
          <p className="text-3xl font-bold text-slate-900">{formatNumber(stats.thisMonthMessages)}</p>
          <p className="text-xs text-slate-500 mt-2">Total conversations</p>
        </div>

        <div className="bg-white border border-slate-200 rounded-lg p-4">
          <p className="text-slate-600 text-sm font-medium mb-1">Avg Daily</p>
          <p className="text-3xl font-bold text-slate-900">{formatNumber(stats.avgTokensPerDay)}</p>
          <p className="text-xs text-slate-500 mt-2">Tokens per day</p>
        </div>
      </div>

      {/* Daily Usage Trend */}
      <div className="bg-white border border-slate-200 rounded-xl p-6">
        <h2 className="text-xl font-bold text-slate-900 mb-4">Daily Token Usage</h2>
        {dailyLoading ? (
          <div className="h-40 bg-slate-200 rounded animate-pulse" />
        ) : (
          <div className="space-y-4">
            {renderChart(
              [40, 60, 55, 80, 45, 70, 90, 85, 75, 65, 88, 92, 78, 65, 71, 82, 69, 74, 85, 91, 76, 68, 72, 80, 86, 75, 68, 73, 79, 85],
              100,
              'Tokens'
            )}
            <div className="flex justify-between text-xs text-slate-500">
              <span>30 days ago</span>
              <span>Today</span>
            </div>
          </div>
        )}
      </div>

      {/* Service Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* By Service */}
        <div className="bg-white border border-slate-200 rounded-xl p-6">
          <h2 className="text-xl font-bold text-slate-900 mb-4">Usage by Service</h2>
          <div className="space-y-4">
            {serviceBreakdown.map((service, idx) => (
              <div key={idx}>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-slate-900 truncate">{service.service}</p>
                    <p className="text-xs text-slate-500">{formatNumber(service.tokens)} tokens</p>
                  </div>
                  <div className="text-right flex-shrink-0 ml-4">
                    <p className="font-semibold text-slate-900">{service.percentage}%</p>
                    <p className="text-xs text-slate-500">{formatCurrency(service.cost)}</p>
                  </div>
                </div>
                <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-[#006c50] to-[#00a858] h-full"
                    style={{ width: `${service.percentage}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Cost Breakdown */}
        <div className="bg-white border border-slate-200 rounded-xl p-6">
          <h2 className="text-xl font-bold text-slate-900 mb-4">Cost Breakdown</h2>
          <div className="space-y-4">
            {serviceBreakdown.map((service, idx) => (
              <div key={idx} className="flex items-center justify-between py-2 border-b border-slate-100 last:border-0">
                <div className="flex items-center gap-3">
                  <div className={`w-4 h-4 rounded-full ${['bg-[#006c50]', 'bg-[#00a858]', 'bg-[#45d4a6]', 'bg-[#99f3bd]'][idx]}`} />
                  <span className="text-sm font-medium text-slate-700">{service.service}</span>
                </div>
                <div className="text-right">
                  <p className="font-bold text-slate-900">{formatCurrency(service.cost)}</p>
                  <p className="text-xs text-slate-500">{service.percentage}% of total</p>
                </div>
              </div>
            ))}

            {/* Total */}
            <div className="pt-4 mt-4 border-t-2 border-slate-300 flex items-center justify-between">
              <span className="font-bold text-slate-900">Total Cost</span>
              <span className="text-2xl font-bold text-[#006c50]">{formatCurrency(stats.totalCost)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white border border-slate-200 rounded-xl p-6">
        <h2 className="text-xl font-bold text-slate-900 mb-4">Recent API Activity</h2>
        <div className="hidden md:block overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200">
                <th className="text-left py-3 px-4 font-semibold text-slate-700">Service</th>
                <th className="text-left py-3 px-4 font-semibold text-slate-700">Endpoint</th>
                <th className="text-left py-3 px-4 font-semibold text-slate-700">Status</th>
                <th className="text-right py-3 px-4 font-semibold text-slate-700">Latency</th>
                <th className="text-right py-3 px-4 font-semibold text-slate-700">Time</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {recentActivity.map((activity, idx) => (
                <tr key={idx} className="hover:bg-slate-50 transition-colors">
                  <td className="py-3 px-4">
                    <span className="inline-block px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-semibold">
                      {activity.service}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-mono text-xs text-slate-600">{activity.endpoint}</td>
                  <td className="py-3 px-4">
                    <span className="inline-block px-2 py-1 bg-green-100 text-green-800 rounded text-xs font-semibold">
                      {activity.status}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right text-slate-900 font-semibold">{activity.latency}</td>
                  <td className="py-3 px-4 text-right text-slate-500 text-xs">{activity.time}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Mobile View */}
        <div className="md:hidden space-y-3">
          {recentActivity.map((activity, idx) => (
            <div key={idx} className="p-4 bg-slate-50 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="inline-block px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-semibold">
                  {activity.service}
                </span>
                <span className="text-xs text-slate-500">{activity.time}</span>
              </div>
              <p className="font-mono text-xs text-slate-600 mb-2">{activity.endpoint}</p>
              <div className="flex items-center justify-between">
                <span className="inline-block px-2 py-1 bg-green-100 text-green-800 rounded text-xs font-semibold">
                  {activity.status}
                </span>
                <span className="text-xs font-semibold text-slate-900">{activity.latency}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Usage Limits */}
      <div className="bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200 rounded-xl p-6">
        <h2 className="text-lg font-bold text-amber-900 mb-4">Daily Limits</h2>
        <div className="space-y-4">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium text-amber-900">Token Usage</span>
              <span className="text-sm font-semibold text-amber-900">{formatNumber(stats.avgTokensPerDay)} / {formatNumber(stats.dailyLimit)} daily</span>
            </div>
            <div className="w-full bg-amber-200 rounded-full h-3 overflow-hidden">
              <div
                className="bg-gradient-to-r from-amber-500 to-orange-500 h-full transition-all duration-300"
                style={{ width: `${Math.min((stats.avgTokensPerDay / stats.dailyLimit) * 100, 100)}%` }}
              />
            </div>
            <p className="text-xs text-amber-700 mt-2">
              {Math.round((stats.avgTokensPerDay / stats.dailyLimit) * 100)}% of daily limit used
            </p>
          </div>
        </div>
      </div>

      {/* Monthly Report */}
      <div className="bg-white border border-slate-200 rounded-xl p-6">
        <h2 className="text-xl font-bold text-slate-900 mb-4">Monthly Report</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div className="p-4 bg-slate-50 rounded-lg">
            <p className="text-slate-600 font-medium mb-1">Report Period</p>
            <p className="text-lg font-bold text-slate-900">Last 30 Days</p>
          </div>
          <div className="p-4 bg-slate-50 rounded-lg">
            <p className="text-slate-600 font-medium mb-1">Generated on</p>
            <p className="text-lg font-bold text-slate-900">{new Date().toLocaleDateString()}</p>
          </div>
          <div className="p-4 bg-slate-50 rounded-lg">
            <p className="text-slate-600 font-medium mb-1">Export</p>
            <button className="text-lg font-bold text-[#006c50] hover:text-[#004d38] flex items-center gap-1">
              <span className="material-symbols-outlined">download</span>
              PDF
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
