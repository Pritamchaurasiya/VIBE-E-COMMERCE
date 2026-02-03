import React, { useState, useEffect, useCallback } from 'react';
import {
  Activity,
  Users,
  Server,
  Database,
  AlertTriangle,
  RefreshCw,
  Download,
  Settings,
  BarChart3,
  PieChart
} from 'lucide-react';
import RealTimeWidget from '../components/monitoring/RealTimeWidget';
import SystemHealthWidget from '../components/monitoring/SystemHealthWidget';
import UserAnalyticsWidget from '../components/monitoring/UserAnalyticsWidget';
import ErrorTrackingWidget from '../components/monitoring/ErrorTrackingWidget';
import DatabaseMetricsWidget from '../components/monitoring/DatabaseMetricsWidget';
import UserSegmentationWidget from '../components/monitoring/UserSegmentationWidget';
import AnalyticsCharts from '../components/monitoring/AnalyticsCharts';
import MonitoringAlerts from '../components/monitoring/MonitoringAlerts';
import useWebSocket from '../hooks/useWebSocket';
import { analyticsAPI } from '../services/api';
import './MonitoringDashboard.css';

const MonitoringDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [dashboardData, setDashboardData] = useState(null);
  const [realTimeData, setRealTimeData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const refreshInterval = 30; // seconds

  // WebSocket connection for real-time updates
  const {
    isConnected,
    data: wsData,
    error: wsError
  } = useWebSocket('ws://localhost:8000/ws/monitoring/', {
    autoConnect: true,
    reconnectAttempts: 5,
    reconnectInterval: 3000
  });

  // Load dashboard data
  const loadDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      const [dashboardResponse, realTimeResponse] = await Promise.all([
        analyticsAPI.getDashboard(),
        analyticsAPI.getRealTimeAnalytics()
      ]);

      setDashboardData(dashboardResponse.data);
      setRealTimeData(realTimeResponse.data);
      setLastUpdated(new Date());
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  // Auto-refresh data
  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(loadDashboardData, refreshInterval * 1000);
      return () => clearInterval(interval);
    }
    return undefined;
  }, [autoRefresh, refreshInterval, loadDashboardData]);

  // Handle WebSocket data updates
  useEffect(() => {
    if (wsData) {
      setRealTimeData(prevData => ({
        ...prevData,
        ...wsData
      }));
    }
  }, [wsData]);

  // Initial load
  useEffect(() => {
    loadDashboardData();
  }, [loadDashboardData]);

  const handleRefresh = () => {
    loadDashboardData();
  };

  const exportData = () => {
    const exportPayload = {
      dashboard: dashboardData,
      realTime: realTimeData,
      exportedAt: new Date().toISOString()
    };

    const blob = new Blob([JSON.stringify(exportPayload, null, 2)], {
      type: 'application/json'
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `monitoring-dashboard-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'realtime', label: 'Real-Time', icon: Activity },
    { id: 'users', label: 'User Analytics', icon: Users },
    { id: 'system', label: 'System Health', icon: Server },
    { id: 'database', label: 'Database', icon: Database },
    { id: 'segments', label: 'User Segments', icon: PieChart },
    { id: 'errors', label: 'Error Tracking', icon: AlertTriangle }
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return (
          <div className="monitoring-overview">
            <div className="overview-grid">
              <div className="overview-section">
                <h3>Real-Time Overview</h3>
                <RealTimeWidget data={realTimeData} loading={loading} />
              </div>

              <div className="overview-section">
                <h3>System Health</h3>
                <SystemHealthWidget data={dashboardData?.systemHealth} loading={loading} />
              </div>

              <div className="overview-section">
                <h3>User Analytics</h3>
                <UserAnalyticsWidget data={dashboardData?.userAnalytics} loading={loading} />
              </div>

              <div className="overview-section">
                <h3>Database Performance</h3>
                <DatabaseMetricsWidget data={dashboardData?.databaseMetrics} loading={loading} />
              </div>
            </div>

            <div className="overview-charts">
              <h3>Analytics Charts</h3>
              <AnalyticsCharts data={dashboardData?.charts} loading={loading} />
            </div>
          </div>
        );

      case 'realtime':
        return <RealTimeWidget data={realTimeData} loading={loading} expanded />;

      case 'users':
        return (
          <div className="user-analytics-page">
            <UserAnalyticsWidget data={dashboardData?.userAnalytics} loading={loading} expanded />
            <UserSegmentationWidget data={dashboardData?.userSegments} loading={loading} />
          </div>
        );

      case 'system':
        return <SystemHealthWidget data={dashboardData?.systemHealth} loading={loading} expanded />;

      case 'database':
        return <DatabaseMetricsWidget data={dashboardData?.databaseMetrics} loading={loading} expanded />;

      case 'segments':
        return <UserSegmentationWidget data={dashboardData?.userSegments} loading={loading} expanded />;

      case 'errors':
        return <ErrorTrackingWidget data={dashboardData?.errorTracking} loading={loading} expanded />;

      default:
        return null;
    }
  };

  return (
    <div className="monitoring-dashboard">
      {/* Header */}
      <div className="dashboard-header">
        <div className="header-content">
          <div className="dashboard-title">
            <Activity className="title-icon" />
            <h1>Monitoring Dashboard</h1>
            <div className="connection-status">
              <div className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}>
                <div className="status-dot"></div>
                <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
              </div>
            </div>
          </div>

          <div className="header-controls">
            <div className="refresh-info">
              <span className="last-updated">
                Last updated: {lastUpdated ? lastUpdated.toLocaleTimeString() : 'Never'}
              </span>
              <button
                className="refresh-btn"
                onClick={handleRefresh}
                disabled={loading}
              >
                <RefreshCw className={`refresh-icon ${loading ? 'spinning' : ''}`} />
                Refresh
              </button>
            </div>

            <div className="auto-refresh">
              <label className="toggle-switch" htmlFor="auto-refresh-toggle">
                <input
                  id="auto-refresh-toggle"
                  type="checkbox"
                  checked={autoRefresh}
                  onChange={(e) => setAutoRefresh(e.target.checked)}
                />
                <span className="slider"></span>
              </label>
              <span>Auto-refresh ({refreshInterval}s)</span>
            </div>

            <div className="header-actions">
              <button className="export-btn" onClick={exportData}>
                <Download size={16} />
                Export
              </button>
              <button className="settings-btn" aria-label="Settings">
                <Settings size={16} />
                Settings
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Alerts */}
      <MonitoringAlerts data={dashboardData?.alerts} />

      {/* Navigation Tabs */}
      <div className="dashboard-tabs">
        {tabs.map(tab => {
          const IconComponent = tab.icon;
          return (
            <button
              key={tab.id}
              className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <IconComponent size={18} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      <div className="dashboard-content">
        {loading && !dashboardData ? (
          <div className="loading-spinner">
            <RefreshCw className="spinning" size={32} />
            <p>Loading monitoring data...</p>
          </div>
        ) : (
          renderTabContent()
        )}
      </div>

      {/* WebSocket Error Alert */}
      {wsError && (
        <div className="websocket-error">
          <AlertTriangle size={16} />
          <span>WebSocket connection error: {wsError}</span>
        </div>
      )}
    </div>
  );
};

export default MonitoringDashboard;