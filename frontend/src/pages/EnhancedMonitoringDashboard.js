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
  PieChart,
  TrendingUp,
  TrendingDown,
  AlertCircle,
  CheckCircle,
  XCircle,
  Clock,
  Cpu,
  MemoryStick,
  HardDrive,
  Network,
  User,
  ShoppingCart,
  CreditCard,
  Shield,
  Thermometer,
  Gauge,
  Target,
  BrainCircuit,
  Lightbulb,
  Search,
  Filter,
  Sliders,
  LayoutDashboard,
  PieChart as PieChartIcon
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
import { getAnalyticsDashboard, getRealTimeAnalytics } from '../services/api';
import './EnhancedMonitoringDashboard.css';

const EnhancedMonitoringDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [dashboardData, setDashboardData] = useState(null);
  const [realTimeData, setRealTimeData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [anomalies, setAnomalies] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [trends, setTrends] = useState([]);
  const [healthScore, setHealthScore] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [performanceForecast, setPerformanceForecast] = useState(null);
  const [userAnalytics, setUserAnalytics] = useState(null);
  const refreshInterval = 30; // seconds

  // WebSocket connection for enhanced real-time updates
  const {
    isConnected,
    data: wsData,
    error: wsError
  } = useWebSocket('ws://localhost:8000/ws/enhanced-monitoring/', {
    autoConnect: true,
    reconnectAttempts: 5,
    reconnectInterval: 3000
  });

  // Load dashboard data
  const loadDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      const [dashboardResponse, realTimeResponse] = await Promise.all([
        getAnalyticsDashboard(),
        getRealTimeAnalytics()
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

  // Load advanced analytics
  const loadAdvancedAnalytics = useCallback(async () => {
    try {
      // In a real implementation, these would be separate API calls
      // For now, we'll use mock data or derive from existing data

      // Mock anomalies
      const mockAnomalies = [
        {
          type: 'high_error_rate',
          severity: 'high',
          message: 'Error rate increased by 15% in the last hour',
          recommendations: ['Review recent deployments', 'Check application logs']
        },
        {
          type: 'memory_usage',
          severity: 'medium',
          message: 'Memory usage approaching 85% capacity',
          recommendations: ['Monitor memory usage', 'Consider scaling resources']
        }
      ];

      // Mock predictions
      const mockPredictions = [
        {
          metric: 'page_views',
          prediction: 1250,
          timeframe: 'next_hour',
          confidence: 87.5,
          method: 'linear_regression'
        },
        {
          metric: 'conversion_rate',
          prediction: 3.2,
          timeframe: 'next_3_hours',
          confidence: 78.9,
          method: 'historical_average'
        }
      ];

      // Mock trends
      const mockTrends = [
        {
          metric: 'page_views',
          current: 1120,
          previous: 980,
          change_percent: 14.3,
          direction: 'up'
        },
        {
          metric: 'error_rate',
          current: 8,
          previous: 12,
          change_percent: -33.3,
          direction: 'down'
        }
      ];

      // Mock health score
      const mockHealthScore = {
        overall: 87.5,
        components: {
          system_resources: 28.5,
          application: 26.0,
          tracking: 18.0,
          database: 15.0
        },
        status: 'good',
        recommendations: [
          'Monitor memory usage trends',
          'Review database query performance'
        ]
      };

      setAnomalies(mockAnomalies);
      setPredictions(mockPredictions);
      setTrends(mockTrends);
      setHealthScore(mockHealthScore);

    } catch (error) {
      console.error('Error loading advanced analytics:', error);
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
      switch (wsData.type) {
        case 'comprehensive_metrics':
          setRealTimeData(prevData => ({
            ...prevData,
            ...wsData.metrics
          }));
          if (wsData.analysis) {
            setHealthScore(prev => ({
              ...prev,
              ...wsData.analysis
            }));
          }
          break;

        case 'anomaly_detection':
          setAnomalies(wsData.anomalies);
          break;

        case 'predictive_analytics':
          setPredictions(wsData.predictions);
          break;

        case 'trend_analysis':
          setTrends(wsData.trends);
          break;

        case 'intelligent_alerts':
          setAlerts(wsData.alerts);
          break;

        case 'performance_forecast':
          setPerformanceForecast(wsData.forecast);
          break;

        case 'user_behavior_analytics':
          setUserAnalytics(wsData.analytics);
          break;

        case 'system_health_score':
          setHealthScore(wsData.health_score);
          break;

        default:
          console.log('Unhandled WebSocket message type:', wsData.type);
      }
    }
  }, [wsData]);

  // Initial load
  useEffect(() => {
    loadDashboardData();
    loadAdvancedAnalytics();
  }, [loadDashboardData, loadAdvancedAnalytics]);

  const handleRefresh = () => {
    loadDashboardData();
    loadAdvancedAnalytics();
  };

  const exportData = () => {
    const exportPayload = {
      dashboard: dashboardData,
      realTime: realTimeData,
      anomalies,
      predictions,
      trends,
      healthScore,
      exportedAt: new Date().toISOString()
    };

    const blob = new Blob([JSON.stringify(exportPayload, null, 2)], {
      type: 'application/json'
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `enhanced-monitoring-dashboard-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  };

  const toggleAdvancedView = () => {
    setShowAdvanced(!showAdvanced);
  };

  const getHealthStatusColor = (status) => {
    switch (status) {
      case 'excellent': return '#059669';
      case 'good': return '#10b981';
      case 'fair': return '#f59e0b';
      case 'concerning': return '#f97316';
      case 'critical': return '#dc2626';
      default: return '#6b7280';
    }
  };

  const getTrendIcon = (direction) => {
    switch (direction) {
      case 'up': return <TrendingUp className="trend-icon up" size={16} />;
      case 'down': return <TrendingDown className="trend-icon down" size={16} />;
      default: return <TrendingUp className="trend-icon stable" size={16} />;
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'critical': return <AlertCircle className="severity-icon critical" size={16} />;
      case 'high': return <AlertTriangle className="severity-icon high" size={16} />;
      case 'medium': return <AlertCircle className="severity-icon medium" size={16} />;
      default: return <CheckCircle className="severity-icon low" size={16} />;
    }
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'realtime', label: 'Real-Time', icon: Activity },
    { id: 'users', label: 'User Analytics', icon: Users },
    { id: 'system', label: 'System Health', icon: Server },
    { id: 'database', label: 'Database', icon: Database },
    { id: 'segments', label: 'User Segments', icon: PieChartIcon },
    { id: 'errors', label: 'Error Tracking', icon: AlertTriangle },
    { id: 'anomalies', label: 'Anomalies', icon: AlertCircle },
    { id: 'predictions', label: 'Predictions', icon: BrainCircuit },
    { id: 'trends', label: 'Trends', icon: TrendingUp },
    { id: 'health', label: 'Health Score', icon: Thermometer }
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return (
          <div className="enhanced-overview">
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

            {/* Advanced Analytics Section */}
            {showAdvanced && (
              <div className="advanced-analytics">
                <div className="advanced-grid">
                  <div className="advanced-card">
                    <h4>System Health Score</h4>
                    {healthScore && (
                      <div className="health-score-display">
                        <div className="health-score-value" style={{ color: getHealthStatusColor(healthScore.status) }}>
                          {healthScore.overall}
                        </div>
                        <div className="health-status" style={{ color: getHealthStatusColor(healthScore.status) }}>
                          {healthScore.status.charAt(0).toUpperCase() + healthScore.status.slice(1)}
                        </div>
                        <div className="health-components">
                          {Object.entries(healthScore.components).map(([component, score]) => (
                            <div key={component} className="health-component">
                              <span className="component-name">{component.replace('_', ' ')}</span>
                              <span className="component-score">{score}</span>
                            </div>
                          ))}
                        </div>
                        {healthScore.recommendations && healthScore.recommendations.length > 0 && (
                          <div className="health-recommendations">
                            <h5>Recommendations</h5>
                            <ul>
                              {healthScore.recommendations.map((rec, index) => (
                                <li key={index}>{rec}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    )}
                  </div>

                  <div className="advanced-card">
                    <h4>Anomaly Detection</h4>
                    {anomalies.length > 0 ? (
                      <div className="anomalies-list">
                        {anomalies.map((anomaly, index) => (
                          <div key={index} className="anomaly-item">
                            <div className="anomaly-header">
                              {getSeverityIcon(anomaly.severity)}
                              <span className="anomaly-type">{anomaly.type}</span>
                              <span className={`anomaly-severity ${anomaly.severity}`}>
                                {anomaly.severity.toUpperCase()}
                              </span>
                            </div>
                            <div className="anomaly-message">{anomaly.message}</div>
                            {anomaly.recommendations && (
                              <div className="anomaly-recommendations">
                                {anomaly.recommendations.map((rec, recIndex) => (
                                  <div key={recIndex} className="recommendation-item">
                                    <Lightbulb size={14} /> {rec}
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="no-anomalies">
                        <CheckCircle size={24} className="check-icon" />
                        <span>No anomalies detected</span>
                      </div>
                    )}
                  </div>

                  <div className="advanced-card">
                    <h4>Predictive Analytics</h4>
                    {predictions.length > 0 ? (
                      <div className="predictions-list">
                        {predictions.map((prediction, index) => (
                          <div key={index} className="prediction-item">
                            <div className="prediction-header">
                              <span className="prediction-metric">{prediction.metric.replace('_', ' ')}</span>
                              <span className="prediction-timeframe">{prediction.timeframe}</span>
                            </div>
                            <div className="prediction-value">
                              {prediction.metric === 'conversion_rate' ? `${prediction.prediction}%` : prediction.prediction}
                            </div>
                            <div className="prediction-details">
                              <span className="prediction-method">{prediction.method}</span>
                              <span className="prediction-confidence">Confidence: {prediction.confidence}%</span>
                            </div>
                            <div className="confidence-bar">
                              <div
                                className="confidence-fill"
                                style={{ width: `${prediction.confidence}%` }}
                              ></div>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="no-predictions">
                        <BrainCircuit size={24} className="brain-icon" />
                        <span>No predictions available</span>
                      </div>
                    )}
                  </div>

                  <div className="advanced-card">
                    <h4>Trend Analysis</h4>
                    {trends.length > 0 ? (
                      <div className="trends-list">
                        {trends.map((trend, index) => (
                          <div key={index} className="trend-item">
                            <div className="trend-header">
                              <span className="trend-metric">{trend.metric.replace('_', ' ')}</span>
                              {getTrendIcon(trend.direction)}
                            </div>
                            <div className="trend-values">
                              <span className="current-value">Current: {trend.current}</span>
                              <span className="previous-value">Previous: {trend.previous}</span>
                            </div>
                            <div className={`trend-change ${trend.direction}`}>
                              {trend.change_percent > 0 ? '+' : ''}{trend.change_percent}%
                            </div>
                            <div className="trend-direction">
                              {trend.direction.charAt(0).toUpperCase() + trend.direction.slice(1)}
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="no-trends">
                        <TrendingUp size={24} className="trend-icon" />
                        <span>No trend data available</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
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

      case 'anomalies':
        return (
          <div className="anomalies-dashboard">
            <h3>Anomaly Detection Dashboard</h3>
            {anomalies.length > 0 ? (
              <div className="anomalies-grid">
                {anomalies.map((anomaly, index) => (
                  <div key={index} className="anomaly-card">
                    <div className="anomaly-card-header">
                      {getSeverityIcon(anomaly.severity)}
                      <h4>{anomaly.type.replace('_', ' ')}</h4>
                      <span className={`severity-badge ${anomaly.severity}`}>
                        {anomaly.severity.toUpperCase()}
                      </span>
                    </div>
                    <div className="anomaly-card-body">
                      <p className="anomaly-message">{anomaly.message}</p>
                      {anomaly.recommendations && (
                        <div className="anomaly-recommendations">
                          <h5>Recommendations</h5>
                          <ul>
                            {anomaly.recommendations.map((rec, recIndex) => (
                              <li key={recIndex}>{rec}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                    <div className="anomaly-card-footer">
                      <button className="anomaly-action">Investigate</button>
                      <button className="anomaly-action secondary">Dismiss</button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="no-anomalies-large">
                <CheckCircle size={48} className="check-icon" />
                <h4>No Anomalies Detected</h4>
                <p>All systems are operating within normal parameters.</p>
              </div>
            )}
          </div>
        );

      case 'predictions':
        return (
          <div className="predictions-dashboard">
            <h3>Predictive Analytics Dashboard</h3>
            {predictions.length > 0 ? (
              <div className="predictions-grid">
                {predictions.map((prediction, index) => (
                  <div key={index} className="prediction-card">
                    <div className="prediction-card-header">
                      <h4>{prediction.metric.replace('_', ' ')}</h4>
                      <span className="prediction-timeframe">{prediction.timeframe}</span>
                    </div>
                    <div className="prediction-card-body">
                      <div className="prediction-value">
                        {prediction.metric === 'conversion_rate' ? `${prediction.prediction}%` : prediction.prediction}
                      </div>
                      <div className="prediction-method">
                        <BrainCircuit size={16} /> {prediction.method}
                      </div>
                      <div className="confidence-display">
                        <div className="confidence-label">Confidence</div>
                        <div className="confidence-value">{prediction.confidence}%</div>
                        <div className="confidence-bar">
                          <div
                            className="confidence-fill"
                            style={{ width: `${prediction.confidence}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                    <div className="prediction-card-footer">
                      <button className="prediction-action">View Details</button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="no-predictions-large">
                <BrainCircuit size={48} className="brain-icon" />
                <h4>No Predictions Available</h4>
                <p>Insufficient data for predictive analytics.</p>
              </div>
            )}
          </div>
        );

      case 'trends':
        return (
          <div className="trends-dashboard">
            <h3>Trend Analysis Dashboard</h3>
            {trends.length > 0 ? (
              <div className="trends-grid">
                {trends.map((trend, index) => (
                  <div key={index} className="trend-card">
                    <div className="trend-card-header">
                      <h4>{trend.metric.replace('_', ' ')}</h4>
                      {getTrendIcon(trend.direction)}
                    </div>
                    <div className="trend-card-body">
                      <div className="trend-values">
                        <div className="value-item">
                          <span className="value-label">Current</span>
                          <span className="value-number">{trend.current}</span>
                        </div>
                        <div className="value-item">
                          <span className="value-label">Previous</span>
                          <span className="value-number">{trend.previous}</span>
                        </div>
                        <div className={`value-item change ${trend.direction}`}>
                          <span className="value-label">Change</span>
                          <span className="value-number">
                            {trend.change_percent > 0 ? '+' : ''}{trend.change_percent}%
                          </span>
                        </div>
                      </div>
                      <div className="trend-chart">
                        <div className="trend-line">
                          <div className="trend-point start"></div>
                          <div className="trend-point end"></div>
                        </div>
                      </div>
                    </div>
                    <div className="trend-card-footer">
                      <span className={`trend-direction ${trend.direction}`}>
                        {trend.direction.charAt(0).toUpperCase() + trend.direction.slice(1)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="no-trends-large">
                <TrendingUp size={48} className="trend-icon" />
                <h4>No Trend Data Available</h4>
                <p>Insufficient historical data for trend analysis.</p>
              </div>
            )}
          </div>
        );

      case 'health':
        return (
          <div className="health-dashboard">
            <h3>System Health Dashboard</h3>
            {healthScore ? (
              <div className="health-overview">
                <div className="health-score-card">
                  <div className="health-score-header">
                    <h4>Overall System Health</h4>
                    <div className="health-status-indicator" style={{ backgroundColor: getHealthStatusColor(healthScore.status) }}>
                      {healthScore.status.charAt(0).toUpperCase() + healthScore.status.slice(1)}
                    </div>
                  </div>
                  <div className="health-score-display">
                    <div className="health-score-value" style={{ color: getHealthStatusColor(healthScore.status) }}>
                      {healthScore.overall}
                    </div>
                    <div className="health-score-label">Health Score</div>
                  </div>
                  <div className="health-gauge">
                    <div className="gauge-container">
                      <div className="gauge-fill" style={{
                        width: `${healthScore.overall}%`,
                        backgroundColor: getHealthStatusColor(healthScore.status)
                      }}></div>
                    </div>
                  </div>
                </div>

                <div className="health-components-grid">
                  {Object.entries(healthScore.components).map(([component, score]) => (
                    <div key={component} className="health-component-card">
                      <div className="component-header">
                        <h5>{component.replace('_', ' ')}</h5>
                        <div className="component-score">{score}</div>
                      </div>
                      <div className="component-gauge">
                        <div className="component-fill" style={{ width: `${score}%` }}></div>
                      </div>
                    </div>
                  ))}
                </div>

                {healthScore.recommendations && healthScore.recommendations.length > 0 && (
                  <div className="health-recommendations-card">
                    <h4>Recommendations</h4>
                    <ul className="recommendations-list">
                      {healthScore.recommendations.map((rec, index) => (
                        <li key={index} className="recommendation-item">
                          <Lightbulb size={16} className="recommendation-icon" />
                          {rec}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ) : (
              <div className="no-health-data">
                <Thermometer size={48} className="thermometer-icon" />
                <h4>Health Data Loading</h4>
                <p>Gathering system health metrics...</p>
              </div>
            )}
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="enhanced-monitoring-dashboard">
      {/* Header */}
      <div className="dashboard-header">
        <div className="header-content">
          <div className="dashboard-title">
            <Activity className="title-icon" />
            <h1>Enhanced Monitoring Dashboard</h1>
            <div className="connection-status">
              <div className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}>
                <div className="status-dot"></div>
                <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
              </div>
              {isConnected && <span className="live-badge">LIVE</span>}
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
              <button className="advanced-toggle" onClick={toggleAdvancedView}>
                <Sliders size={16} />
                {showAdvanced ? 'Hide Advanced' : 'Show Advanced'}
              </button>
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
            <p>Loading enhanced monitoring data...</p>
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

      {/* Quick Stats Sidebar */}
      <div className="quick-stats-sidebar">
        <div className="quick-stats-header">
          <h4>Quick Stats</h4>
          <Clock size={16} />
        </div>
        <div className="quick-stats-grid">
          <div className="quick-stat">
            <Cpu size={20} className="stat-icon" />
            <div className="stat-value">
              {realTimeData?.system?.cpu?.percent?.toFixed(1) || '0.0'}%
            </div>
            <div className="stat-label">CPU Usage</div>
          </div>
          <div className="quick-stat">
            <MemoryStick size={20} className="stat-icon" />
            <div className="stat-value">
              {realTimeData?.system?.memory?.percent?.toFixed(1) || '0.0'}%
            </div>
            <div className="stat-label">Memory</div>
          </div>
          <div className="quick-stat">
            <HardDrive size={20} className="stat-icon" />
            <div className="stat-value">
              {realTimeData?.system?.disk?.percent?.toFixed(1) || '0.0'}%
            </div>
            <div className="stat-label">Disk</div>
          </div>
          <div className="quick-stat">
            <User size={20} className="stat-icon" />
            <div className="stat-value">
              {realTimeData?.application?.active_users || '0'}
            </div>
            <div className="stat-label">Active Users</div>
          </div>
          <div className="quick-stat">
            <ShoppingCart size={20} className="stat-icon" />
            <div className="stat-value">
              {realTimeData?.application?.current_sessions || '0'}
            </div>
            <div className="stat-label">Sessions</div>
          </div>
          <div className="quick-stat">
            <AlertTriangle size={20} className="stat-icon" />
            <div className="stat-value">
              {dashboardData?.tracking?.active_alerts || '0'}
            </div>
            <div className="stat-label">Alerts</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnhancedMonitoringDashboard;