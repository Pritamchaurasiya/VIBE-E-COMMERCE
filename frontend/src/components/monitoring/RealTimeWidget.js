import React, { useState, useEffect, useCallback } from 'react';
import PropTypes from 'prop-types';
import {
  Users,
  Eye,
  TrendingUp,
  Activity,
  Clock,
  Smartphone,
  Monitor,
  Tablet
} from 'lucide-react';
import './RealTimeWidget.css';

const RealTimeWidget = ({ data, loading, expanded }) => {
  const [currentTime, setCurrentTime] = useState(new Date());
  const [animatedValues, setAnimatedValues] = useState({
    activeUsers: 0,
    currentSessions: 0,
    pageViewsLastHour: 0,
    conversionsLastHour: 0
  });

  // Update current time every second
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Animate numbers
  useEffect(() => {
    if (data && !loading) {
      const targets = {
        activeUsers: data.active_users || 0,
        currentSessions: data.current_sessions || 0,
        pageViewsLastHour: data.page_views_last_hour || 0,
        conversionsLastHour: data.conversions_last_hour || 0
      };

      Object.keys(targets).forEach(key => {
        const targetValue = targets[key];
        const currentValue = animatedValues[key];
        const increment = (targetValue - currentValue) / 20;

        const animate = () => {
          setAnimatedValues(prev => {
            const newValue = Math.abs(targetValue - prev[key]) < 1
              ? targetValue
              : prev[key] + increment;
            return { ...prev, [key]: newValue };
          });
        };

        const interval = setInterval(() => {
          animate();
          if (Math.abs(targetValue - animatedValues[key]) < 1) {
            clearInterval(interval);
          }
        }, 50);
      });
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data, loading]);

  const formatNumber = useCallback((num) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return Math.floor(num).toString();
  }, []);

  const getDeviceIcon = useCallback((deviceType) => {
    switch (deviceType) {
      case 'mobile': return <Smartphone size={16} />;
      case 'tablet': return <Tablet size={16} />;
      case 'desktop': return <Monitor size={16} />;
      default: return <Monitor size={16} />;
    }
  }, []);

  const getChangeColor = useCallback((change) => {
    if (change > 0) return '#059669';
    if (change < 0) return '#dc2626';
    return '#4b5563';
  }, []);

  const getDeviceColor = useCallback((device) => {
    switch (device) {
      case 'mobile': return '#2563eb';
      case 'tablet': return '#059669';
      default: return '#d97706';
    }
  }, []);

  const metrics = [
    {
      title: 'Active Users',
      value: formatNumber(animatedValues.activeUsers),
      change: data?.active_users_change || 0,
      icon: <Users size={24} />,
      color: '#2563eb'
    },
    {
      title: 'Current Sessions',
      value: formatNumber(animatedValues.currentSessions),
      change: data?.sessions_change || 0,
      icon: <Activity size={24} />,
      color: '#059669'
    },
    {
      title: 'Page Views (1h)',
      value: formatNumber(animatedValues.pageViewsLastHour),
      change: data?.page_views_change || 0,
      icon: <Eye size={24} />,
      color: '#d97706'
    },
    {
      title: 'Conversions (1h)',
      value: formatNumber(animatedValues.conversionsLastHour),
      change: data?.conversions_change || 0,
      icon: <TrendingUp size={24} />,
      color: '#7c3aed'
    }
  ];

  if (loading) {
    return (
      <div className={`real-time-widget ${expanded ? 'expanded' : ''}`}>
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
    <div className={`real-time-widget ${expanded ? 'expanded' : ''}`}>
      {/* Header */}
      <div className="widget-header">
        <div className="header-info">
          <h3>Real-Time Activity</h3>
          <div className="current-time">
            <Clock size={16} />
            <span>{currentTime.toLocaleTimeString()}</span>
          </div>
        </div>
        <div className="live-indicator">
          <div className="live-dot"></div>
          <span>LIVE</span>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className={`metrics-grid ${expanded ? 'expanded' : ''}`}>
        {metrics.map((metric) => (
          <div key={metric.title} className="metric-card">
            <div className="metric-icon" style={{ color: metric.color }}>
              {metric.icon}
            </div>
            <div className="metric-content">
              <div className="metric-value">{metric.value}</div>
              <div className="metric-title">{metric.title}</div>
              <div
                className="metric-change"
                style={{ color: getChangeColor(metric.change) }}
              >
                {metric.change > 0 ? '+' : ''}{metric.change}%
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Top Pages */}
      {data?.top_pages && data.top_pages.length > 0 && (
        <div className="top-pages-section">
          <h4>Top Pages (Live)</h4>
          <div className="top-pages-list">
            {data.top_pages.slice(0, expanded ? 10 : 5).map((page) => (
              <div key={page.path} className="page-item">
                <span className="page-rank">#{data.top_pages.indexOf(page) + 1}</span>
                <span className="page-path">{page.path}</span>
                <span className="page-views">{formatNumber(page.views)} views</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Device Breakdown */}
      {data?.active_devices && (
        <div className="device-breakdown">
          <h4>Active Devices</h4>
          <div className="device-stats">
            {Object.entries(data.active_devices).map(([device, count]) => (
              <div key={device} className="device-stat">
                <div className="device-info">
                  {getDeviceIcon(device)}
                  <span className="device-name">
                    {device.charAt(0).toUpperCase() + device.slice(1)}
                  </span>
                </div>
                <div className="device-count">
                  <span className="count">{formatNumber(count)}</span>
                  <div className="device-bar">
                    <div
                      className="device-fill"
                      style={{
                        width: `${(count / Math.max(...Object.values(data.active_devices))) * 100}%`,
                        backgroundColor: getDeviceColor(device)
                      }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Traffic Sources */}
      {data?.traffic_sources && (
        <div className="traffic-sources">
          <h4>Traffic Sources</h4>
          <div className="sources-list">
            {Object.entries(data.traffic_sources).map(([source, count]) => (
              <div key={source} className="source-item">
                <span className="source-name">{source}</span>
                <div className="source-bar">
                  <div
                    className="source-fill"
                    style={{
                      width: `${(count / Math.max(...Object.values(data.traffic_sources))) * 100}%`
                    }}
                  ></div>
                </div>
                <span className="source-count">{formatNumber(count)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Events */}
      {data?.recent_events && data.recent_events.length > 0 && (
        <div className="recent-events">
          <h4>Recent Events</h4>
          <div className="events-list">
            {data.recent_events.slice(0, expanded ? 15 : 8).map((event) => (
              <div key={`${event.timestamp}-${event.description}`} className="event-item">
                <div className="event-time">
                  {new Date(event.timestamp).toLocaleTimeString()}
                </div>
                <div className="event-description">{event.description}</div>
                <div className="event-user">{event.user || 'Anonymous'}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

RealTimeWidget.propTypes = {
  data: PropTypes.shape({
    active_users: PropTypes.number,
    current_sessions: PropTypes.number,
    page_views_last_hour: PropTypes.number,
    conversions_last_hour: PropTypes.number,
    active_users_change: PropTypes.number,
    sessions_change: PropTypes.number,
    page_views_change: PropTypes.number,
    conversions_change: PropTypes.number,
    top_pages: PropTypes.arrayOf(PropTypes.shape({
      path: PropTypes.string,
      views: PropTypes.number
    })),
    active_devices: PropTypes.object,
    traffic_sources: PropTypes.object,
    recent_events: PropTypes.arrayOf(PropTypes.shape({
      timestamp: PropTypes.string,
      description: PropTypes.string,
      user: PropTypes.string
    }))
  }),
  loading: PropTypes.bool,
  expanded: PropTypes.bool
};

RealTimeWidget.defaultProps = {
  data: null,
  loading: false,
  expanded: false
};

export default RealTimeWidget;