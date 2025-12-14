import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import {
  Cpu,
  HardDrive,
  MemoryStick,
  Activity,
  Thermometer,
  Wifi,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock
} from 'lucide-react';
import './SystemHealthWidget.css';

const SystemHealthWidget = ({ data, loading, expanded }) => {
  const [animatedValues, setAnimatedValues] = useState({
    cpuUsage: 0,
    memoryUsage: 0,
    diskUsage: 0,
    networkIn: 0,
    networkOut: 0
  });

  const [systemStatus, setSystemStatus] = useState('unknown');

  // Animate metrics when data changes
  useEffect(() => {
    if (data && !loading) {
      const targets = {
        cpuUsage: data.cpu_usage || 0,
        memoryUsage: data.memory_usage || 0,
        diskUsage: data.disk_usage || 0,
        networkIn: data.network_in || 0,
        networkOut: data.network_out || 0
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

      // Determine overall system status
      const { cpu_usage, memory_usage, disk_usage } = data;
      if (cpu_usage > 90 || memory_usage > 90 || disk_usage > 95) {
        setSystemStatus('critical');
      } else if (cpu_usage > 70 || memory_usage > 70 || disk_usage > 80) {
        setSystemStatus('warning');
      } else {
        setSystemStatus('healthy');
      }
    }
  }, [data, loading]);

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy': return '#10b981';
      case 'warning': return '#f59e0b';
      case 'critical': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy': return <CheckCircle size={16} />;
      case 'warning': return <AlertTriangle size={16} />;
      case 'critical': return <XCircle size={16} />;
      default: return <Clock size={16} />;
    }
  };

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Number.parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const formatNetworkSpeed = (bytesPerSec) => {
    return `${formatBytes(bytesPerSec)}/s`;
  };

  const getUsageColor = (usage) => {
    if (usage >= 90) return '#ef4444';
    if (usage >= 70) return '#f59e0b';
    return '#10b981';
  };

  const getUsageBarColor = (usage) => {
    if (usage >= 90) return 'linear-gradient(90deg, #ef4444, #dc2626)';
    if (usage >= 70) return 'linear-gradient(90deg, #f59e0b, #d97706)';
    return 'linear-gradient(90deg, #10b981, #059669)';
  };

  const metrics = [
    {
      title: 'CPU Usage',
      value: `${animatedValues.cpuUsage.toFixed(1)}%`,
      icon: <Cpu size={24} />,
      color: getUsageColor(animatedValues.cpuUsage),
      max: 100
    },
    {
      title: 'Memory Usage',
      value: `${animatedValues.memoryUsage.toFixed(1)}%`,
      icon: <MemoryStick size={24} />,
      color: getUsageColor(animatedValues.memoryUsage),
      max: 100
    },
    {
      title: 'Disk Usage',
      value: `${animatedValues.diskUsage.toFixed(1)}%`,
      icon: <HardDrive size={24} />,
      color: getUsageColor(animatedValues.diskUsage),
      max: 100
    },
    {
      title: 'Network In',
      value: formatNetworkSpeed(animatedValues.networkIn),
      icon: <Wifi size={24} />,
      color: '#3b82f6',
      max: null
    },
    {
      title: 'Network Out',
      value: formatNetworkSpeed(animatedValues.networkOut),
      icon: <Wifi size={24} />,
      color: '#8b5cf6',
      max: null
    }
  ];

  if (loading) {
    return (
      <div className={`system-health-widget ${expanded ? 'expanded' : ''}`}>
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
    <div className={`system-health-widget ${expanded ? 'expanded' : ''}`}>
      {/* Header */}
      <div className="widget-header">
        <div className="header-info">
          <h3>System Health</h3>
          <div className="system-status">
            <div
              className="status-indicator"
              style={{ color: getStatusColor(systemStatus) }}
            >
              {getStatusIcon(systemStatus)}
              <span className="status-text">
                {systemStatus.charAt(0).toUpperCase() + systemStatus.slice(1)}
              </span>
            </div>
          </div>
        </div>
        <div className="last-update">
          <Clock size={16} />
          <span>Updated {data?.last_updated ? new Date(data.last_updated).toLocaleTimeString() : 'Never'}</span>
        </div>
      </div>

      {/* System Overview */}
      <div className="system-overview">
        <div className="overview-card">
          <div className="overview-icon" style={{ color: getStatusColor(systemStatus) }}>
            <Activity size={32} />
          </div>
          <div className="overview-content">
            <div className="overview-title">Overall Health</div>
            <div className="overview-status" style={{ color: getStatusColor(systemStatus) }}>
              {systemStatus.charAt(0).toUpperCase() + systemStatus.slice(1)}
            </div>
            <div className="overview-description">
              {systemStatus === 'healthy' && 'All systems operating normally'}
              {systemStatus === 'warning' && 'Some resources running high'}
              {systemStatus === 'critical' && 'Immediate attention required'}
              {systemStatus === 'unknown' && 'System status unknown'}
            </div>
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className={`metrics-grid ${expanded ? 'expanded' : ''}`}>
        {metrics.map((metric, index) => (
          <div key={index} className="metric-card">
            <div className="metric-header">
              <div className="metric-icon" style={{ color: metric.color }}>
                {metric.icon}
              </div>
              <div className="metric-title">{metric.title}</div>
            </div>

            <div className="metric-value" style={{ color: metric.color }}>
              {metric.value}
            </div>

            {metric.max && (
              <div className="usage-bar">
                <div
                  className="usage-fill"
                  style={{
                    width: `${Math.min(animatedValues[Object.keys(animatedValues)[index]] || 0, 100)}%`,
                    background: getUsageBarColor(animatedValues[Object.keys(animatedValues)[index]] || 0)
                  }}
                ></div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Detailed Information */}
      {expanded && (
        <div className="detailed-info">
          <div className="info-section">
            <h4>System Information</h4>
            <div className="info-grid">
              <div className="info-item">
                <span className="info-label">Uptime</span>
                <span className="info-value">{data?.uptime || 'Unknown'}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Load Average</span>
                <span className="info-value">{data?.load_average || 'Unknown'}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Processes</span>
                <span className="info-value">{data?.process_count || 'Unknown'}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Temperature</span>
                <span className="info-value">
                  {data?.temperature ? `${data.temperature}°C` : 'Unknown'}
                </span>
              </div>
            </div>
          </div>

          {/* Storage Details */}
          <div className="info-section">
            <h4>Storage Details</h4>
            <div className="storage-details">
              {data?.disk_details && Object.entries(data.disk_details).map(([mount, details]) => (
                <div key={mount} className="disk-item">
                  <div className="disk-header">
                    <HardDrive size={16} />
                    <span className="disk-mount">{mount}</span>
                  </div>
                  <div className="disk-usage">
                    <div className="disk-usage-bar">
                      <div
                        className="disk-usage-fill"
                        style={{
                          width: `${(details.used / details.total) * 100}%`,
                          background: getUsageBarColor((details.used / details.total) * 100)
                        }}
                      ></div>
                    </div>
                    <div className="disk-info">
                      <span>{formatBytes(details.used)} / {formatBytes(details.total)}</span>
                      <span>{((details.used / details.total) * 100).toFixed(1)}%</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Network Details */}
          <div className="info-section">
            <h4>Network Statistics</h4>
            <div className="network-stats">
              <div className="network-item">
                <Wifi size={16} />
                <span className="network-interface">Total In</span>
                <span className="network-value">{formatBytes(data?.total_network_in || 0)}</span>
              </div>
              <div className="network-item">
                <Wifi size={16} />
                <span className="network-interface">Total Out</span>
                <span className="network-value">{formatBytes(data?.total_network_out || 0)}</span>
              </div>
              <div className="network-item">
                <Activity size={16} />
                <span className="network-interface">Connections</span>
                <span className="network-value">{data?.active_connections || 0}</span>
              </div>
            </div>
          </div>

          {/* Alerts */}
          {data?.alerts && data.alerts.length > 0 && (
            <div className="info-section">
              <h4>System Alerts</h4>
              <div className="alerts-list">
                {data.alerts.map((alert, index) => (
                  <div key={index} className={`alert-item ${alert.severity}`}>
                    <AlertTriangle size={16} />
                    <div className="alert-content">
                      <div className="alert-message">{alert.message}</div>
                      <div className="alert-time">{new Date(alert.timestamp).toLocaleString()}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

SystemHealthWidget.propTypes = {
  data: PropTypes.shape({
    cpu_usage: PropTypes.number,
    memory_usage: PropTypes.number,
    disk_usage: PropTypes.number,
    network_in: PropTypes.number,
    network_out: PropTypes.number,
    last_updated: PropTypes.string,
    uptime: PropTypes.string,
    load_average: PropTypes.string,
    process_count: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    temperature: PropTypes.number,
    disk_details: PropTypes.object,
    total_network_in: PropTypes.number,
    total_network_out: PropTypes.number,
    active_connections: PropTypes.number,
    alerts: PropTypes.arrayOf(PropTypes.shape({
      severity: PropTypes.string,
      message: PropTypes.string,
      timestamp: PropTypes.string
    }))
  }),
  loading: PropTypes.bool,
  expanded: PropTypes.bool
};

SystemHealthWidget.defaultProps = {
  data: null,
  loading: false,
  expanded: false
};

export default SystemHealthWidget;
