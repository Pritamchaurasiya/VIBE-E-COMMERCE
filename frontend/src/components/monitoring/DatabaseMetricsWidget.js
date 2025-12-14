import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import {
  Database,
  Activity,
  Clock,
  HardDrive,
  TrendingUp,
  TrendingDown,
  Search,
  Zap,
  Users,
  RefreshCw,
  AlertTriangle,
  CheckCircle
} from 'lucide-react';
import './DatabaseMetricsWidget.css';

const DatabaseMetricsWidget = ({ data, loading, expanded }) => {
  const [selectedTab, setSelectedTab] = useState('performance');
  const [animatedValues, setAnimatedValues] = useState({
    connections: 0,
    queriesPerSecond: 0,
    avgQueryTime: 0,
    cacheHitRate: 0,
    diskUsage: 0,
    memoryUsage: 0
  });

  // Animate values when data changes
  useEffect(() => {
    if (data && !loading) {
      const targets = {
        connections: data.active_connections || 0,
        queriesPerSecond: data.queries_per_second || 0,
        avgQueryTime: data.avg_query_time || 0,
        cacheHitRate: data.cache_hit_rate || 0,
        diskUsage: data.disk_usage || 0,
        memoryUsage: data.memory_usage || 0
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

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Number.parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const formatDuration = (ms) => {
    if (ms < 1000) return `${ms.toFixed(0)}ms`;
    return `${(ms / 1000).toFixed(2)}s`;
  };

  const getHealthStatus = (metric, value) => {
    const thresholds = {
      connections: { warning: 80, critical: 95 },
      queriesPerSecond: { warning: 1000, critical: 2000 },
      avgQueryTime: { warning: 100, critical: 500 },
      cacheHitRate: { warning: 85, critical: 70 },
      diskUsage: { warning: 80, critical: 95 },
      memoryUsage: { warning: 80, critical: 95 }
    };

    const threshold = thresholds[metric];
    if (!threshold) return 'unknown';

    if (value >= threshold.critical) return 'critical';
    if (value >= threshold.warning) return 'warning';
    return 'healthy';
  };

  const getHealthColor = (status) => {
    switch (status) {
      case 'healthy': return '#10b981';
      case 'warning': return '#f59e0b';
      case 'critical': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const getHealthIcon = (status) => {
    switch (status) {
      case 'healthy': return <CheckCircle size={16} />;
      case 'warning': return <AlertTriangle size={16} />;
      case 'critical': return <AlertTriangle size={16} />;
      default: return <Clock size={16} />;
    }
  };

  const performanceMetrics = [
    {
      title: 'Active Connections',
      value: formatNumber(animatedValues.connections),
      change: data?.connections_change || 0,
      icon: <Users size={24} />,
      health: getHealthStatus('connections', animatedValues.connections),
      max: data?.max_connections || 100
    },
    {
      title: 'Queries/Second',
      value: formatNumber(animatedValues.queriesPerSecond),
      change: data?.qps_change || 0,
      icon: <Zap size={24} />,
      health: getHealthStatus('queriesPerSecond', animatedValues.queriesPerSecond),
      max: null
    },
    {
      title: 'Avg Query Time',
      value: formatDuration(animatedValues.avgQueryTime),
      change: data?.query_time_change || 0,
      icon: <Clock size={24} />,
      health: getHealthStatus('avgQueryTime', animatedValues.avgQueryTime),
      max: null
    },
    {
      title: 'Cache Hit Rate',
      value: `${animatedValues.cacheHitRate.toFixed(1)}%`,
      change: data?.cache_hit_change || 0,
      icon: <Activity size={24} />,
      health: getHealthStatus('cacheHitRate', animatedValues.cacheHitRate),
      max: 100
    }
  ];

  const resourceMetrics = [
    {
      title: 'Disk Usage',
      value: `${animatedValues.diskUsage.toFixed(1)}%`,
      icon: <HardDrive size={24} />,
      health: getHealthStatus('diskUsage', animatedValues.diskUsage),
      details: {
        used: formatBytes(data?.disk_used || 0),
        total: formatBytes(data?.disk_total || 0),
        available: formatBytes(data?.disk_available || 0)
      }
    },
    {
      title: 'Memory Usage',
      value: `${animatedValues.memoryUsage.toFixed(1)}%`,
      icon: <Database size={24} />,
      health: getHealthStatus('memoryUsage', animatedValues.memoryUsage),
      details: {
        used: formatBytes(data?.memory_used || 0),
        total: formatBytes(data?.memory_total || 0),
        cache: formatBytes(data?.memory_cache || 0)
      }
    }
  ];

  if (loading) {
    return (
      <div className={`database-metrics-widget ${expanded ? 'expanded' : ''}`}>
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
    <div className={`database-metrics-widget ${expanded ? 'expanded' : ''}`}>
      {/* Header */}
      <div className="widget-header">
        <div className="header-info">
          <h3>Database Performance</h3>
          <div className="db-status">
            <div
              className="status-indicator"
              style={{ color: getHealthColor(data?.overall_health || 'unknown') }}
            >
              {getHealthIcon(data?.overall_health || 'unknown')}
              <span className="status-text">
                {data?.overall_health ? data.overall_health.charAt(0).toUpperCase() + data.overall_health.slice(1) : 'Unknown'}
              </span>
            </div>
          </div>
        </div>
        <div className="header-controls">
          <div className="tab-selector">
            <button
              className={`tab-btn ${selectedTab === 'performance' ? 'active' : ''}`}
              onClick={() => setSelectedTab('performance')}
            >
              <Activity size={16} />
              Performance
            </button>
            <button
              className={`tab-btn ${selectedTab === 'resources' ? 'active' : ''}`}
              onClick={() => setSelectedTab('resources')}
            >
              <HardDrive size={16} />
              Resources
            </button>
            <button
              className={`tab-btn ${selectedTab === 'queries' ? 'active' : ''}`}
              onClick={() => setSelectedTab('queries')}
            >
              <Search size={16} />
              Queries
            </button>
          </div>
          <button className="refresh-btn">
            <RefreshCw size={16} />
          </button>
        </div>
      </div>

      {/* Performance Tab */}
      {selectedTab === 'performance' && (
        <div className="tab-content">
          <div className={`performance-metrics ${expanded ? 'expanded' : ''}`}>
            {performanceMetrics.map((metric, index) => (
              <div key={index} className="metric-card">
                <div className="metric-header">
                  <div className="metric-icon" style={{ color: getHealthColor(metric.health) }}>
                    {metric.icon}
                  </div>
                  <div className="metric-title">{metric.title}</div>
                  <div
                    className="health-indicator"
                    style={{ color: getHealthColor(metric.health) }}
                  >
                    {getHealthIcon(metric.health)}
                  </div>
                </div>

                <div className="metric-value" style={{ color: getHealthColor(metric.health) }}>
                  {metric.value}
                </div>

                <div className="metric-change">
                  {metric.change >= 0 ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                  <span className={metric.change >= 0 ? 'positive' : 'negative'}>
                    {Math.abs(metric.change).toFixed(1)}%
                  </span>
                </div>

                {metric.max && (
                  <div className="usage-bar">
                    <div className="usage-fill" style={{
                      width: `${(parseFloat(metric.value) / metric.max) * 100}%`,
                      backgroundColor: getHealthColor(metric.health)
                    }}></div>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Performance Charts */}
          <div className="performance-charts">
            <h4>Performance Trends</h4>
            <div className="charts-grid">
              <div className="chart-card">
                <div className="chart-title">Query Performance</div>
                <div className="chart-placeholder">
                  <Activity size={48} />
                  <p>Query performance chart would be rendered here</p>
                </div>
              </div>
              <div className="chart-card">
                <div className="chart-title">Connection Pool</div>
                <div className="chart-placeholder">
                  <Users size={48} />
                  <p>Connection pool usage chart would be rendered here</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Resources Tab */}
      {selectedTab === 'resources' && (
        <div className="tab-content">
          <div className="resource-metrics">
            {resourceMetrics.map((metric, index) => (
              <div key={index} className="resource-card">
                <div className="resource-header">
                  <div className="resource-icon" style={{ color: getHealthColor(metric.health) }}>
                    {metric.icon}
                  </div>
                  <div className="resource-title">{metric.title}</div>
                  <div
                    className="health-indicator"
                    style={{ color: getHealthColor(metric.health) }}
                  >
                    {getHealthIcon(metric.health)}
                  </div>
                </div>

                <div className="resource-value" style={{ color: getHealthColor(metric.health) }}>
                  {metric.value}
                </div>

                <div className="usage-bar">
                  <div className="usage-fill" style={{
                    width: metric.value,
                    backgroundColor: getHealthColor(metric.health)
                  }}></div>
                </div>

                <div className="resource-details">
                  {metric.details && Object.entries(metric.details).map(([key, value]) => (
                    <div key={key} className="detail-item">
                      <span className="detail-label">{key.charAt(0).toUpperCase() + key.slice(1)}:</span>
                      <span className="detail-value">{value}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* Database Size Breakdown */}
          <div className="size-breakdown">
            <h4>Database Size Breakdown</h4>
            <div className="breakdown-grid">
              {data?.size_breakdown && Object.entries(data.size_breakdown).map(([table, size]) => (
                <div key={table} className="breakdown-item">
                  <div className="table-name">{table}</div>
                  <div className="table-size">{formatBytes(size)}</div>
                  <div className="table-bar">
                    <div
                      className="table-fill"
                      style={{
                        width: `${(size / Math.max(...Object.values(data.size_breakdown))) * 100}%`
                      }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Queries Tab */}
      {selectedTab === 'queries' && (
        <div className="tab-content">
          <div className="query-analytics">
            <div className="query-stats">
              <div className="stat-item">
                <div className="stat-value">{formatNumber(data?.total_queries || 0)}</div>
                <div className="stat-label">Total Queries</div>
              </div>
              <div className="stat-item">
                <div className="stat-value">{formatNumber(data?.slow_queries || 0)}</div>
                <div className="stat-label">Slow Queries</div>
              </div>
              <div className="stat-item">
                <div className="stat-value">{formatNumber(data?.failed_queries || 0)}</div>
                <div className="stat-label">Failed Queries</div>
              </div>
            </div>

            {/* Slow Queries */}
            <div className="slow-queries">
              <h4>Slowest Queries</h4>
              <div className="queries-list">
                {data?.slow_queries_list && data.slow_queries_list.map((query, index) => (
                  <div key={index} className="query-item">
                    <div className="query-time">{formatDuration(query.duration)}</div>
                    <div className="query-content">
                      <div className="query-sql">{query.sql}</div>
                      <div className="query-meta">
                        <span className="query-table">{query.table}</span>
                        <span className="query-execution-time">{formatDuration(query.execution_time)}</span>
                        <span className="query-rows">{query.rows_examined} rows</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Query Performance */}
            <div className="query-performance">
              <h4>Query Performance Distribution</h4>
              <div className="performance-buckets">
                {data?.performance_buckets && Object.entries(data.performance_buckets).map(([bucket, count]) => (
                  <div key={bucket} className="bucket-item">
                    <div className="bucket-label">{bucket}</div>
                    <div className="bucket-bar">
                      <div
                        className="bucket-fill"
                        style={{
                          width: `${(count / Math.max(...Object.values(data.performance_buckets))) * 100}%`
                        }}
                      ></div>
                    </div>
                    <div className="bucket-count">{formatNumber(count)}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Database Health Summary */}
      <div className="health-summary">
        <h4>Database Health Summary</h4>
        <div className="summary-grid">
          <div className="summary-item">
            <div className="summary-icon">
              <CheckCircle size={20} />
            </div>
            <div className="summary-content">
              <div className="summary-title">Uptime</div>
              <div className="summary-value">{data?.uptime || '99.9%'}</div>
            </div>
          </div>
          <div className="summary-item">
            <div className="summary-icon">
              <Activity size={20} />
            </div>
            <div className="summary-content">
              <div className="summary-title">Replication Lag</div>
              <div className="summary-value">{data?.replication_lag || '< 1s'}</div>
            </div>
          </div>
          <div className="summary-item">
            <div className="summary-icon">
              <Database size={20} />
            </div>
            <div className="summary-content">
              <div className="summary-title">Backup Status</div>
              <div className="summary-value">{data?.backup_status || 'Up to date'}</div>
            </div>
          </div>
          <div className="summary-item">
            <div className="summary-icon">
              <Zap size={20} />
            </div>
            <div className="summary-content">
              <div className="summary-title">Index Usage</div>
              <div className="summary-value">{data?.index_usage || '95%'}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

DatabaseMetricsWidget.propTypes = {
  data: PropTypes.shape({
    active_connections: PropTypes.number,
    queries_per_second: PropTypes.number,
    avg_query_time: PropTypes.number,
    cache_hit_rate: PropTypes.number,
    disk_usage: PropTypes.number,
    memory_usage: PropTypes.number,
    max_connections: PropTypes.number,
    connections_change: PropTypes.number,
    qps_change: PropTypes.number,
    query_time_change: PropTypes.number,
    cache_hit_change: PropTypes.number,
    disk_used: PropTypes.number,
    disk_total: PropTypes.number,
    disk_available: PropTypes.number,
    memory_used: PropTypes.number,
    memory_total: PropTypes.number,
    memory_cache: PropTypes.number,
    overall_health: PropTypes.string,
    size_breakdown: PropTypes.object,
    total_queries: PropTypes.number,
    slow_queries: PropTypes.number,
    failed_queries: PropTypes.number,
    slow_queries_list: PropTypes.array,
    performance_buckets: PropTypes.object,
    uptime: PropTypes.string,
    replication_lag: PropTypes.string,
    backup_status: PropTypes.string,
    index_usage: PropTypes.string
  }),
  loading: PropTypes.bool,
  expanded: PropTypes.bool
};

DatabaseMetricsWidget.defaultProps = {
  data: null,
  loading: false,
  expanded: false
};

export default DatabaseMetricsWidget;
