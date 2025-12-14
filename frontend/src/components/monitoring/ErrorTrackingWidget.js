import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import {
  AlertTriangle,
  XCircle,
  Info,
  CheckCircle,
  Clock,
  User,
  Globe,
  Bug,
  Search,
  Download,
  RefreshCw,
  TrendingDown,
  TrendingUp
} from 'lucide-react';
import './ErrorTrackingWidget.css';

const ErrorTrackingWidget = ({ data, loading, expanded }) => {
  const [selectedSeverity, setSelectedSeverity] = useState('all');
  const [selectedTimeRange, setSelectedTimeRange] = useState('24h');
  const [searchTerm, setSearchTerm] = useState('');
  const [animatedValues, setAnimatedValues] = useState({
    totalErrors: 0,
    resolvedErrors: 0,
    activeErrors: 0,
    errorRate: 0
  });

  // Animate values when data changes
  useEffect(() => {
    if (data && !loading) {
      const targets = {
        totalErrors: data.total_errors || 0,
        resolvedErrors: data.resolved_errors || 0,
        activeErrors: data.active_errors || 0,
        errorRate: data.error_rate || 0
      };

      Object.keys(targets).forEach(key => {
        const targetValue = targets[key];
        const increment = targetValue / 30;

        const animate = () => {
          setAnimatedValues(prev => {
            const current = prev[key];
            const newValue = Math.abs(targetValue - current) < 0.5 ?
              targetValue : current + increment;
            return { ...prev, [key]: newValue };
          });
        };

        const interval = setInterval(animate, 50);
        setTimeout(() => clearInterval(interval), 1500);
      });
    }
  }, [data, loading]);

  const formatNumber = (num) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return Math.floor(num).toString();
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'critical': return <XCircle size={20} />;
      case 'error': return <AlertTriangle size={20} />;
      case 'warning': return <AlertTriangle size={20} />;
      case 'info': return <Info size={20} />;
      default: return <Bug size={20} />;
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return '#dc2626';
      case 'error': return '#ef4444';
      case 'warning': return '#f59e0b';
      case 'info': return '#3b82f6';
      default: return '#6b7280';
    }
  };

  const getSeverityBgColor = (severity) => {
    switch (severity) {
      case 'critical': return '#fef2f2';
      case 'error': return '#fef2f2';
      case 'warning': return '#fffbeb';
      case 'info': return '#eff6ff';
      default: return '#f8fafc';
    }
  };

  const getErrorStatusColor = (status) => {
    switch (status) {
      case 'resolved': return '#10b981';
      case 'investigating': return '#f59e0b';
      case 'new': return '#3b82f6';
      default: return '#6b7280';
    }
  };

  const metrics = [
    {
      title: 'Total Errors',
      value: formatNumber(animatedValues.totalErrors),
      change: data?.errors_change || 0,
      icon: <Bug size={24} />,
      color: '#ef4444'
    },
    {
      title: 'Resolved',
      value: formatNumber(animatedValues.resolvedErrors),
      change: data?.resolved_change || 0,
      icon: <CheckCircle size={24} />,
      color: '#10b981'
    },
    {
      title: 'Active',
      value: formatNumber(animatedValues.activeErrors),
      change: data?.active_change || 0,
      icon: <AlertTriangle size={24} />,
      color: '#f59e0b'
    },
    {
      title: 'Error Rate',
      value: `${animatedValues.errorRate.toFixed(2)}%`,
      change: data?.rate_change || 0,
      icon: <TrendingUp size={24} />,
      color: '#8b5cf6'
    }
  ];

  const filteredErrors = data?.errors ? data.errors.filter(error => {
    const matchesSeverity = selectedSeverity === 'all' || error.severity === selectedSeverity;
    const matchesSearch = searchTerm === '' ||
      error.message.toLowerCase().includes(searchTerm.toLowerCase()) ||
      error.url.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSeverity && matchesSearch;
  }) : [];

  if (loading) {
    return (
      <div className={`error-tracking-widget ${expanded ? 'expanded' : ''}`}>
        <div className="widget-loading">
          <div className="loading-shimmer"></div>
          <div className="loading-shimmer"></div>
          <div className="loading-shimmer"></div>
          <div className="loading-shimmer"></div>
        </div>
      </div>
    );
  }

  return (
    <div className={`error-tracking-widget ${expanded ? 'expanded' : ''}`}>
      {/* Header */}
      <div className="widget-header">
        <div className="header-info">
          <h3>Error Tracking</h3>
          <div className="error-summary">
            <span className="summary-text">
              {data?.summary || 'Monitoring application errors and exceptions'}
            </span>
          </div>
        </div>
        <div className="header-controls">
          <div className="time-range-selector">
            <select
              value={selectedTimeRange}
              onChange={(e) => setSelectedTimeRange(e.target.value)}
              className="time-range-select"
            >
              <option value="1h">Last Hour</option>
              <option value="24h">Last 24 Hours</option>
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
            </select>
          </div>
          <button className="refresh-btn">
            <RefreshCw size={16} />
          </button>
          <button className="export-btn">
            <Download size={16} />
            Export
          </button>
        </div>
      </div>

      {/* Metrics Overview */}
      <div className={`metrics-overview ${expanded ? 'expanded' : ''}`}>
        {metrics.map((metric, index) => (
          <div key={index} className="metric-card">
            <div className="metric-icon" style={{ color: metric.color }}>
              {metric.icon}
            </div>
            <div className="metric-content">
              <div className="metric-value">{metric.value}</div>
              <div className="metric-title">{metric.title}</div>
              <div
                className={`metric-change ${metric.change >= 0 ? 'negative' : 'positive'}`}
              >
                {metric.change >= 0 ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                <span>{Math.abs(metric.change).toFixed(1)}%</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Error Distribution */}
      <div className="error-distribution">
        <h4>Error Distribution by Severity</h4>
        <div className="distribution-grid">
          {data?.error_distribution && Object.entries(data.error_distribution).map(([severity, count]) => {
            const percentage = ((count / (data.total_errors || 1)) * 100).toFixed(1);
            return (
              <div key={severity} className="distribution-card">
                <div
                  className="severity-indicator"
                  style={{ backgroundColor: getSeverityColor(severity) }}
                >
                  {getSeverityIcon(severity)}
                </div>
                <div className="distribution-content">
                  <div className="severity-name">{severity.charAt(0).toUpperCase() + severity.slice(1)}</div>
                  <div className="severity-stats">
                    <span className="error-count">{formatNumber(count)}</span>
                    <span className="percentage">{percentage}%</span>
                  </div>
                  <div className="severity-bar">
                    <div
                      className="severity-fill"
                      style={{
                        width: `${percentage}%`,
                        backgroundColor: getSeverityColor(severity)
                      }}
                    ></div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Filters and Search */}
      <div className="error-filters">
        <div className="search-container">
          <Search size={16} className="search-icon" />
          <input
            type="text"
            placeholder="Search errors..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>
        <div className="severity-filter">
          <label>Severity:</label>
          <select
            value={selectedSeverity}
            onChange={(e) => setSelectedSeverity(e.target.value)}
            className="severity-select"
          >
            <option value="all">All Severities</option>
            <option value="critical">Critical</option>
            <option value="error">Error</option>
            <option value="warning">Warning</option>
            <option value="info">Info</option>
          </select>
        </div>
      </div>

      {/* Error List */}
      <div className="error-list">
        <h4>Recent Errors</h4>
        <div className="errors-container">
          {filteredErrors.length > 0 ? (
            filteredErrors.slice(0, expanded ? 20 : 10).map((error, index) => (
              <div key={index} className="error-item">
                <div className="error-severity" style={{ color: getSeverityColor(error.severity) }}>
                  {getSeverityIcon(error.severity)}
                </div>
                <div className="error-content">
                  <div className="error-header">
                    <div className="error-message">{error.message}</div>
                    <div className="error-status" style={{ color: getErrorStatusColor(error.status) }}>
                      {error.status}
                    </div>
                  </div>
                  <div className="error-details">
                    <div className="error-url">
                      <Globe size={14} />
                      <span>{error.url}</span>
                    </div>
                    <div className="error-timestamp">
                      <Clock size={14} />
                      <span>{new Date(error.timestamp).toLocaleString()}</span>
                    </div>
                    {error.user_id && (
                      <div className="error-user">
                        <User size={14} />
                        <span>User: {error.user_id}</span>
                      </div>
                    )}
                  </div>
                  {error.stack_trace && (
                    <div className="error-stack">
                      <details>
                        <summary>Stack Trace</summary>
                        <pre>{error.stack_trace}</pre>
                      </details>
                    </div>
                  )}
                </div>
                <div className="error-actions">
                  <button className="action-btn">Resolve</button>
                  <button className="action-btn secondary">Ignore</button>
                </div>
              </div>
            ))
          ) : (
            <div className="no-errors">
              <CheckCircle size={48} />
              <h5>No Errors Found</h5>
              <p>Great! No errors match your current filters.</p>
            </div>
          )}
        </div>
      </div>

      {/* Error Analytics */}
      <div className="error-analytics">
        <h4>Error Analytics</h4>
        <div className="analytics-grid">
          <div className="analytics-card">
            <div className="analytics-title">Most Frequent Errors</div>
            <div className="frequency-list">
              {data?.most_frequent_errors && data.most_frequent_errors.map((error, index) => (
                <div key={index} className="frequency-item">
                  <span className="error-name">{error.message.substring(0, 50)}...</span>
                  <span className="frequency-count">{formatNumber(error.count)} times</span>
                </div>
              ))}
            </div>
          </div>

          <div className="analytics-card">
            <div className="analytics-title">Error Sources</div>
            <div className="sources-list">
              {data?.error_sources && Object.entries(data.error_sources).map(([source, count]) => (
                <div key={source} className="source-item">
                  <span className="source-name">{source}</span>
                  <div className="source-bar">
                    <div
                      className="source-fill"
                      style={{
                        width: `${(count / Math.max(...Object.values(data.error_sources))) * 100}%`
                      }}
                    ></div>
                  </div>
                  <span className="source-count">{formatNumber(count)}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Performance Impact */}
      <div className="performance-impact">
        <h4>Performance Impact</h4>
        <div className="impact-grid">
          <div className="impact-item">
            <div className="impact-metric">
              <span className="metric-value">{data?.affected_users || 0}</span>
              <span className="metric-label">Affected Users</span>
            </div>
          </div>
          <div className="impact-item">
            <div className="impact-metric">
              <span className="metric-value">{data?.avg_resolution_time || '0m'}</span>
              <span className="metric-label">Avg Resolution Time</span>
            </div>
          </div>
          <div className="impact-item">
            <div className="impact-metric">
              <span className="metric-value">{data?.uptime_impact || '99.9%'}</span>
              <span className="metric-label">Uptime Impact</span>
            </div>
          </div>
        </div>
      </div>

      {/* Alert Rules */}
      <div className="alert-rules">
        <h4>Alert Rules</h4>
        <div className="rules-list">
          {data?.alert_rules && data.alert_rules.map((rule, index) => (
            <div key={index} className="rule-item">
              <div className="rule-info">
                <div className="rule-name">{rule.name}</div>
                <div className="rule-description">{rule.description}</div>
              </div>
              <div className="rule-status">
                <span className={`rule-indicator ${rule.is_active ? 'active' : 'inactive'}`}>
                  {rule.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

ErrorTrackingWidget.propTypes = {
  data: PropTypes.shape({
    total_errors: PropTypes.number,
    resolved_errors: PropTypes.number,
    active_errors: PropTypes.number,
    error_rate: PropTypes.number,
    errors_change: PropTypes.number,
    resolved_change: PropTypes.number,
    active_change: PropTypes.number,
    rate_change: PropTypes.number,
    summary: PropTypes.string,
    error_distribution: PropTypes.object,
    errors: PropTypes.arrayOf(PropTypes.shape({
      severity: PropTypes.string,
      message: PropTypes.string,
      url: PropTypes.string,
      status: PropTypes.string,
      timestamp: PropTypes.string,
      user_id: PropTypes.string,
      stack_trace: PropTypes.string
    })),
    most_frequent_errors: PropTypes.array,
    error_sources: PropTypes.object,
    affected_users: PropTypes.number,
    avg_resolution_time: PropTypes.string,
    uptime_impact: PropTypes.string,
    alert_rules: PropTypes.array
  }),
  loading: PropTypes.bool,
  expanded: PropTypes.bool
};

ErrorTrackingWidget.defaultProps = {
  data: null,
  loading: false,
  expanded: false
};

export default ErrorTrackingWidget;
