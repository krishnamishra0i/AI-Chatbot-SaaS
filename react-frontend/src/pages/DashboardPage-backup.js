// New AI Solutions Dashboard - with all 5 sections
import React from 'react';
import AIDashboard from './AIDashboard';

/**
 * DashboardPage - Wrapper for the new AI Solutions Dashboard
 * Replaces the old styled-components dashboard with the modern Tailwind-based version
 */
export default function DashboardPage({ onNavigate }) {
  return <AIDashboard />;
}
