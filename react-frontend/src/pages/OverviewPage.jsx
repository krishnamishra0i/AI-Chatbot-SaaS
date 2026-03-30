// Overview Dashboard Page
import React, { useState } from 'react';

const OverviewPage = () => {
  const [selectedPeriod, setSelectedPeriod] = useState('30');

  return (
    <div className="pb-24 md:pb-0">
      {/* Hero Section */}
      <div className="mb-10">
        <h2 className="text-3xl font-extrabold font-headline tracking-tight text-on-background mb-2">
          Welcome back, Alex
        </h2>
        <p className="text-neutral-500 max-w-2xl">
          Your AI infrastructure is performing optimally. Here is what happened in the last 24 hours.
        </p>
      </div>

      {/* KPI Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
        {/* KPI 1 - Chatbots */}
        <div className="glass-card p-6 rounded-lg relative overflow-hidden group hover:shadow-lg transition-shadow bg-white/40 backdrop-blur-md">
          <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:scale-110 transition-transform">
            <span className="material-symbols-outlined text-6xl text-primary">forum</span>
          </div>
          <div className="flex flex-col gap-1">
            <span className="text-sm font-label font-medium text-neutral-500 uppercase tracking-wider">
              Total Chatbots
            </span>
            <span className="text-4xl font-headline font-extrabold text-on-background">12</span>
            <div className="flex items-center gap-1 text-primary-container text-sm font-bold mt-2">
              <span className="material-symbols-outlined text-base">trending_up</span>
              <span>+2 this month</span>
            </div>
          </div>
        </div>

        {/* KPI 2 - API Keys */}
        <div className="glass-card p-6 rounded-lg relative overflow-hidden group hover:shadow-lg transition-shadow bg-white/40 backdrop-blur-md">
          <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:scale-110 transition-transform">
            <span className="material-symbols-outlined text-6xl text-secondary">vpn_key</span>
          </div>
          <div className="flex flex-col gap-1">
            <span className="text-sm font-label font-medium text-neutral-500 uppercase tracking-wider">
              API Keys
            </span>
            <span className="text-4xl font-headline font-extrabold text-on-background">24</span>
            <div className="flex items-center gap-1 text-secondary text-sm font-bold mt-2">
              <span className="material-symbols-outlined text-base">check_circle</span>
              <span>All keys active</span>
            </div>
          </div>
        </div>

        {/* KPI 3 - Messages */}
        <div className="glass-card p-6 rounded-lg relative overflow-hidden group hover:shadow-lg transition-shadow bg-white/40 backdrop-blur-md">
          <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:scale-110 transition-transform">
            <span className="material-symbols-outlined text-6xl text-tertiary">bar_chart</span>
          </div>
          <div className="flex flex-col gap-1">
            <span className="text-sm font-label font-medium text-neutral-500 uppercase tracking-wider">
              Monthly Messages
            </span>
            <span className="text-4xl font-headline font-extrabold text-on-background">1.2M</span>
            <div className="flex items-center gap-1 text-tertiary text-sm font-bold mt-2">
              <span className="material-symbols-outlined text-base">bolt</span>
              <span>84% of quota used</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Bento Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Usage Chart */}
        <div className="lg:col-span-8 glass-card p-8 rounded-lg flex flex-col min-h-[400px] bg-white/40 backdrop-blur-md border border-white/30">
          <div className="flex justify-between items-center mb-8">
            <div>
              <h3 className="text-xl font-headline font-bold">API Performance</h3>
              <p className="text-sm text-neutral-500">Latency vs Traffic volume</p>
            </div>
            <div className="flex gap-2">
              <button className="px-4 py-1.5 rounded-full text-xs font-bold bg-white/50 border border-outline-variant hover:bg-white transition-colors">
                7 Days
              </button>
              <button className="px-4 py-1.5 rounded-full text-xs font-bold bg-primary-container text-white">
                30 Days
              </button>
            </div>
          </div>

          {/* Bar Chart Visualization */}
          <div className="flex-grow flex items-end gap-2 px-2">
            {[40, 55, 35, 70, 60, 90, 85, 45, 30, 65].map((height, idx) => (
              <div
                key={idx}
                className="w-full bg-primary-container rounded-t-full hover:opacity-100 opacity-70 transition-opacity"
                style={{ height: `${height}%` }}
                title={`Day ${idx + 1}`}
              />
            ))}
          </div>

          <div className="flex justify-between text-[10px] uppercase font-bold text-neutral-400 mt-4 tracking-tighter">
            <span>Oct 01</span>
            <span>Oct 10</span>
          </div>
        </div>

        {/* Quick Actions Sidebar */}
        <div className="lg:col-span-4 flex flex-col gap-6">
          {/* Quick Actions Card */}
          <div className="glass-card p-8 rounded-lg bg-white/40 backdrop-blur-md border border-white/30">
            <h3 className="text-xl font-headline font-bold mb-6">Quick Actions</h3>
            <div className="flex flex-col gap-3">
              {[
                {
                  icon: 'add_circle',
                  label: 'Create Chatbot',
                  bg: 'bg-primary-container',
                  text: 'text-white',
                },
                {
                  icon: 'key',
                  label: 'Manage API Keys',
                  bg: 'bg-secondary-container',
                  text: 'text-white',
                },
                {
                  icon: 'settings',
                  label: 'System Settings',
                  bg: 'bg-white/50',
                  text: 'text-on-background',
                  border: 'border border-outline-variant',
                },
              ].map((action, idx) => (
                <button
                  key={idx}
                  className={`w-full py-4 px-6 ${action.bg} ${action.text} rounded-full flex items-center justify-between group hover:shadow-lg transition-all active:scale-95 ${action.border || ''}`}
                >
                  <div className="flex items-center gap-3">
                    <span className="material-symbols-outlined">{action.icon}</span>
                    <span className="font-label font-bold">{action.label}</span>
                  </div>
                  <span className="material-symbols-outlined group-hover:translate-x-1 transition-transform">
                    chevron_right
                  </span>
                </button>
              ))}
            </div>
          </div>

          {/* Live Activity Card */}
          <div className="glass-card p-8 rounded-lg flex-grow bg-white/40 backdrop-blur-md border border-white/30">
            <h3 className="text-lg font-headline font-bold mb-4">Live Activity</h3>
            <div className="space-y-4">
              {[
                {
                  title: 'Support Bot v2',
                  desc: 'Processed request #4829 • 2m ago',
                  color: 'bg-primary-container',
                },
                {
                  title: 'New API Key',
                  desc: 'Created for Marketing Dept • 45m ago',
                  color: 'bg-secondary',
                },
                {
                  title: 'Quota Alert',
                  desc: 'Tier 1 reached 80% capacity • 1h ago',
                  color: 'bg-tertiary',
                },
              ].map((activity, idx) => (
                <div key={idx} className="flex gap-4 items-start">
                  <div className={`w-2 h-2 rounded-full ${activity.color} mt-2`} />
                  <div>
                    <p className="text-sm font-bold">{activity.title}</p>
                    <p className="text-xs text-neutral-500">{activity.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* FAB Button */}
      <button className="fixed bottom-24 right-6 md:bottom-12 md:right-12 w-16 h-16 bg-primary-container text-white rounded-full shadow-2xl flex items-center justify-center active:scale-90 transition-transform z-40 hover:scale-110">
        <span className="material-symbols-outlined text-3xl">add</span>
      </button>
    </div>
  );
};

export default OverviewPage;
