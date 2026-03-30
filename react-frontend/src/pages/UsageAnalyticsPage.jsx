// Usage Analytics Page
import React, { useState } from 'react';

const UsageAnalyticsPage = () => {
  const [timePeriod, setTimePeriod] = useState('30');

  return (
    <div className="pb-24 md:pb-0">
      {/* Header Section */}
      <div className="mb-10 flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h2 className="text-3xl font-extrabold font-headline tracking-tight text-on-background">
            Usage Analytics
          </h2>
          <p className="text-on-surface-variant font-medium mt-1">
            Real-time performance metrics and cost management.
          </p>
        </div>
        <div className="flex items-center gap-3 bg-white px-4 py-2 rounded-full shadow-sm border border-outline-variant">
          <span className="material-symbols-outlined text-slate-400">calendar_today</span>
          <span className="font-label text-sm font-semibold">Last 30 Days</span>
          <span className="material-symbols-outlined text-slate-400">expand_more</span>
        </div>
      </div>

      {/* Bento Grid Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        {[
          {
            icon: 'token',
            label: 'Total Tokens',
            value: '1.42M',
            change: '+12.5%',
            color: 'primary',
            colorLight: 'primary-container',
          },
          {
            icon: 'bolt',
            label: 'Total Requests',
            value: '84,202',
            change: '+8.2%',
            color: 'secondary',
            colorLight: 'secondary-container',
          },
          {
            icon: 'payments',
            label: 'Current Costs',
            value: '$284.12',
            change: '+4.1%',
            color: 'error',
            colorLight: 'error-container',
          },
          {
            icon: 'timer',
            label: 'Avg. Latency',
            value: '412ms',
            change: '-15ms',
            color: 'primary',
            colorLight: 'primary-fixed-dim',
          },
        ].map((stat, idx) => (
          <div
            key={idx}
            className="glass-card p-6 rounded-lg shadow-sm group hover:border-primary-container transition-all bg-white/40 backdrop-blur-md border border-white/30"
          >
            <div className="flex justify-between items-start mb-4">
              <div className={`p-2 bg-${stat.colorLight}/10 rounded-full`}>
                <span className={`material-symbols-outlined text-${stat.color}`}>{stat.icon}</span>
              </div>
              <span
                className={`text-xs font-bold text-${stat.color} px-2 py-1 bg-${stat.color}/10 rounded-full`}
              >
                {stat.change}
              </span>
            </div>
            <h3 className="text-on-surface-variant font-label text-xs uppercase tracking-wider mb-1">
              {stat.label}
            </h3>
            <p className="text-2xl font-bold font-headline">{stat.value}</p>
          </div>
        ))}
      </div>

      {/* Main Analytics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Large Token Usage Chart */}
        <div className="lg:col-span-2 glass-card p-8 rounded-lg shadow-md relative overflow-hidden bg-white/40 backdrop-blur-md border border-white/30">
          <div className="flex justify-between items-center mb-8">
            <div>
              <h3 className="text-xl font-bold font-headline">Token Consumption</h3>
              <p className="text-sm text-on-surface-variant">Daily breakdown across all deployed models</p>
            </div>
            <div className="flex gap-2">
              <span className="w-3 h-3 rounded-full bg-primary" />
              <span className="w-3 h-3 rounded-full bg-secondary" />
            </div>
          </div>

          {/* Mock Chart Area */}
          <div className="h-64 flex items-end justify-between gap-2 relative">
            {/* Background Grid */}
            <div className="absolute inset-0 border-b border-outline-variant flex flex-col justify-between">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="w-full border-t border-slate-100" />
              ))}
            </div>

            {/* Bars */}
            {[40, 60, 55, 80, 45, 70, 90, 65, 40, 85, 50, 75].map((height, idx) => (
              <div
                key={idx}
                className="flex-1 bg-gradient-to-b from-cyan-400 to-primary-container rounded-t-full opacity-30 transition-all hover:opacity-100"
                style={{ height: `${height}%` }}
              />
            ))}
          </div>

          <div className="flex justify-between mt-4 text-[10px] font-bold text-slate-400 font-label">
            <span>01 OCT</span>
            <span>07 OCT</span>
            <span>14 OCT</span>
            <span>21 OCT</span>
            <span>30 OCT</span>
          </div>
        </div>

        {/* Side Card: Cost Distribution */}
        <div className="glass-card p-8 rounded-lg shadow-md flex flex-col bg-white/40 backdrop-blur-md border border-white/30">
          <h3 className="text-xl font-bold font-headline mb-6">Cost by Model</h3>
          <div className="space-y-6 flex-grow">
            {[
              { model: 'GPT-4 Omni', cost: '$182.40', width: '65%' },
              { model: 'Claude 3.5 Sonnet', cost: '$64.12', width: '25%' },
              { model: 'Gemini 1.5 Flash', cost: '$21.10', width: '10%' },
            ].map((item, idx) => (
              <div key={idx} className="space-y-2">
                <div className="flex justify-between text-sm font-semibold">
                  <span>{item.model}</span>
                  <span className="text-primary">{item.cost}</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-cyan-400 to-primary-container h-full rounded-full"
                    style={{ width: item.width, opacity: 0.5 + idx * 0.25 }}
                  />
                </div>
              </div>
            ))}
          </div>

          <div className="mt-8 pt-6 border-t border-slate-100">
            <button className="w-full bg-gradient-to-r from-cyan-400 to-primary-container text-white font-bold py-3 rounded-full shadow-lg shadow-cyan-200 active:scale-95 transition-transform hover:shadow-xl">
              Download Report
            </button>
          </div>
        </div>

        {/* Request Volume */}
        <div className="lg:col-span-3 glass-card p-8 rounded-lg shadow-md bg-white/40 backdrop-blur-md border border-white/30">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
            <div>
              <h3 className="text-xl font-bold font-headline">Request Volume</h3>
              <p className="text-sm text-on-surface-variant">Success rate vs. Error density over the last 24 hours</p>
            </div>
            <div className="flex bg-slate-100 p-1 rounded-full">
              <button className="px-4 py-1 text-xs font-bold rounded-full bg-white shadow-sm">
                Requests
              </button>
              <button className="px-4 py-1 text-xs font-bold text-slate-500">Errors</button>
            </div>
          </div>

          {/* Abstract Line Chart */}
          <div className="h-48 relative w-full">
            <svg className="w-full h-full" viewBox="0 0 1000 200" preserveAspectRatio="none">
              {/* Primary Gradient Curve */}
              <path
                d="M0 150 Q 50 120 100 140 T 200 100 T 300 160 T 400 80 T 500 120 T 600 40 T 700 90 T 800 60 T 900 110 T 1000 70"
                fill="none"
                stroke="url(#gradient-line)"
                strokeLinecap="round"
                strokeWidth="4"
              />

              {/* Secondary Decorative Curve */}
              <path
                d="M0 170 Q 50 150 100 160 T 200 140 T 300 180 T 400 120 T 500 150 T 600 90 T 700 130 T 800 110 T 900 150 T 1000 120"
                fill="none"
                stroke="#0EA5E9"
                strokeDasharray="8 4"
                strokeOpacity="0.3"
                strokeWidth="2"
              />

              <defs>
                <linearGradient id="gradient-line" x1="0%" x2="100%">
                  <stop offset="0%" stopColor="#34B5FA" stopOpacity="1" />
                  <stop offset="100%" stopColor="#60FCC7" stopOpacity="1" />
                </linearGradient>
              </defs>
            </svg>

            {/* Floating Data Node */}
            <div className="absolute top-[30%] left-[60%] -translate-x-1/2 -translate-y-1/2">
              <div className="relative group">
                <div className="w-4 h-4 rounded-full bg-primary border-4 border-white shadow-md animate-pulse" />
                <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 bg-on-background text-white text-[10px] px-2 py-1 rounded whitespace-nowrap">
                  Peak: 4,210 req/m
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity Table */}
      <div className="mt-8 glass-card rounded-lg overflow-hidden shadow-md bg-white/40 backdrop-blur-md border border-white/30">
        <div className="px-8 py-6 border-b border-slate-100 flex justify-between items-center">
          <h3 className="text-xl font-bold font-headline">Recent API Activity</h3>
          <button className="text-primary font-bold text-sm hover:underline">View All</button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left font-label">
            <thead className="bg-slate-50 text-slate-500 text-[11px] uppercase tracking-widest">
              <tr>
                <th className="px-8 py-4">Endpoint</th>
                <th className="px-8 py-4">Status</th>
                <th className="px-8 py-4">Tokens</th>
                <th className="px-8 py-4">Latency</th>
                <th className="px-8 py-4 text-right">Time</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {[
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
                {
                  method: 'POST',
                  endpoint: '/v1/images/generations',
                  status: '429 Rate Limit',
                  statusError: true,
                  tokens: '0',
                  latency: '12ms',
                  time: '12 mins ago',
                },
              ].map((row, idx) => (
                <tr key={idx} className="hover:bg-primary/5 transition-colors">
                  <td className="px-8 py-4">
                    <div className="flex items-center gap-3">
                      <span className="text-xs font-mono bg-slate-100 px-2 py-1 rounded">{row.method}</span>
                      <span className="font-semibold">{row.endpoint}</span>
                    </div>
                  </td>
                  <td className="px-8 py-4">
                    <span
                      className={`inline-flex items-center gap-1 text-xs font-bold ${
                        row.statusError ? 'text-error' : 'text-primary'
                      }`}
                    >
                      <span
                        className={`w-2 h-2 rounded-full ${
                          row.statusError ? 'bg-error' : 'bg-primary'
                        }`}
                      />
                      {row.status}
                    </span>
                  </td>
                  <td className="px-8 py-4 font-semibold">{row.tokens}</td>
                  <td className="px-8 py-4 font-semibold text-on-surface-variant">{row.latency}</td>
                  <td className="px-8 py-4 text-right text-slate-400 text-sm">{row.time}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default UsageAnalyticsPage;
