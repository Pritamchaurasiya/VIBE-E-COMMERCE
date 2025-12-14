import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import {
  AlertTriangle,
  Info,
  CheckCircle,
  XCircle,
  X,
  Clock,
  Activity,
  Server,
  Database,
  Wifi
} from 'lucide-react';
import './MonitoringAlerts.css';

const MonitoringAlerts = ({ data }) => {
  const [alerts, setAlerts] = useState([]);
  const [dismissedAlerts, setDismissedAlerts] = useState(new Set());
  const [showAll, setShowAll] = useState(false);

  // Initialize alerts from data
  useEffect(() => {
    if (data?.alerts) {
      setAlerts(data.alerts);
    } else {
      // Default demo alerts if no data provided
      setAlerts([
        {
          id: 1,
          type: 'warning',
          title: 'High CPU Usage',
          message: 'CPU usage has exceeded 80% for the last 5 minutes',
          timestamp: new Date(Date.now() - 2 * 60 * 1000).toISOString(),
          source: 'System Health',
          severity: 'medium',
          actionable: true
        },
        {
          id: 2,
          type: 'info',
          title: 'Database Backup Completed',
          message: 'Scheduled database backup completed successfully',
          timestamp: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
          source: 'Database',
          severity: 'low',
          actionable: false
        },
        {
          id: 3,
          type: 'success',
          title: 'System Performance Improved',
          message: 'Page load times have decreased by 15%',
          timestamp: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
          source: 'Performance',
          severity: 'low',
          actionable: false
        }
      ]);
    }
  }, [data]);

  const getAlertIcon = (type) => {
    switch (type) {
      case 'critical': return <XCircle size={18} />;
      case 'warning': return <AlertTriangle size={18} />;
      case 'info': return <Info size={18} />;
      case 'success': return <CheckCircle size={18} />;
      default: return <AlertTriangle size={18} />;
    }
  };

  const getAlertColor = (type) => {
    switch (type) {
      case 'critical': return '#dc2626';
      case 'warning': return '#d97706';
      case 'info': return '#2563eb';
      case 'success': return '#059669';
      default: return '#4b5563';
    }
  };

  const getAlertBgColor = (type) => {
    switch (type) {
      case 'critical': return '#fef2f2';
      case 'warning': return '#fffbeb';
      case 'info': return '#eff6ff';
      case 'success': return '#f0fdf4';
      default: return '#f8fafc';
    }
  };

  const getAlertBorderColor = (type) => {
    switch (type) {
      case 'critical': return '#fecaca';
      case 'warning': return '#fed7aa';
      case 'info': return '#bfdbfe';
      case 'success': return '#bbf7d0';
      default: return '#e2e8f0';
    }
  };

  const getSourceIcon = (source) => {
    const sourceLower = source.toLowerCase();
    switch (sourceLower) {
      case 'system health': return <Server size={16} />;
      case 'database': return <Database size={16} />;
      case 'performance': return <Activity size={16} />;
      case 'network': return <Wifi size={16} />;
      default: return <AlertTriangle size={16} />;
    }
  };

  const handleDismiss = (alertId) => {
    setDismissedAlerts(prev => new Set([...prev, alertId]));
  };

  const handleAction = (alertId, action) => {
    // Handle alert actions here
    console.log(`Alert ${alertId} action:`, action);
    handleDismiss(alertId);
  };

  const getTimeAgo = (timestamp) => {
    const now = new Date();
    const alertTime = new Date(timestamp);
    const diffInMinutes = Math.floor((now - alertTime) / (1000 * 60));

    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;

    const diffInHours = Math.floor(diffInMinutes / 60);
    if (diffInHours < 24) return `${diffInHours}h ago`;

    const diffInDays = Math.floor(diffInHours / 24);
    return `${diffInDays}d ago`;
  };

  const visibleAlerts = showAll ? alerts : alerts.slice(0, 3);
  const filteredAlerts = visibleAlerts.filter(alert => !dismissedAlerts.has(alert.id));

  const activeAlertsCount = alerts.filter(alert =>
    !dismissedAlerts.has(alert.id) &&
    (alert.type === 'critical' || alert.type === 'warning')
  ).length;

  if (filteredAlerts.length === 0) {
    return (
      <div className="monitoring-alerts empty">
        <div className="no-alerts">
          <CheckCircle size={32} />
          <p>All systems operational</p>
        </div>
      </div>
    );
  }

  return (
    <div className="monitoring-alerts">
      <div className="alerts-header">
        <div className="alerts-title">
          <h4>System Alerts</h4>
          {activeAlertsCount > 0 && (
            <span className="active-count">{activeAlertsCount} active</span>
          )}
        </div>
        <div className="alerts-controls">
          {alerts.length > 3 && (
            <button
              className="show-all-btn"
              onClick={() => setShowAll(!showAll)}
            >
              {showAll ? 'Show Less' : `Show All (${alerts.length})`}
            </button>
          )}
        </div>
      </div>

      <div className="alerts-list">
        {filteredAlerts.map((alert) => (
          <div
            key={alert.id}
            className={`alert-item ${alert.type} ${alert.actionable ? 'actionable' : ''}`}
            style={{
              backgroundColor: getAlertBgColor(alert.type),
              borderColor: getAlertBorderColor(alert.type)
            }}
          >
            <div className="alert-icon" style={{ color: getAlertColor(alert.type) }}>
              {getAlertIcon(alert.type)}
            </div>

            <div className="alert-content">
              <div className="alert-header">
                <div className="alert-title">{alert.title}</div>
                <div className="alert-meta">
                  <div className="alert-source">
                    {getSourceIcon(alert.source)}
                    <span>{alert.source}</span>
                  </div>
                  <div className="alert-time">
                    <Clock size={14} />
                    <span>{getTimeAgo(alert.timestamp)}</span>
                  </div>
                </div>
              </div>

              <div className="alert-message">{alert.message}</div>

              {alert.actionable && (
                <div className="alert-actions">
                  <button
                    className="alert-action-btn primary"
                    onClick={() => handleAction(alert.id, 'resolve')}
                  >
                    Resolve
                  </button>
                  <button
                    className="alert-action-btn secondary"
                    onClick={() => handleAction(alert.id, 'investigate')}
                  >
                    Investigate
                  </button>
                </div>
              )}
            </div>

            <button
              className="alert-dismiss"
              onClick={() => handleDismiss(alert.id)}
              title="Dismiss alert"
              aria-label="Dismiss alert"
            >
              <X size={16} />
            </button>
          </div>
        ))}
      </div>

      {/* Alert Summary */}
      <div className="alert-summary">
        <div className="summary-grid">
          <div className="summary-item critical">
            <div className="summary-icon">
              <XCircle size={16} />
            </div>
            <div className="summary-content">
              <div className="summary-count">
                {alerts.filter(a => a.type === 'critical' && !dismissedAlerts.has(a.id)).length}
              </div>
              <div className="summary-label">Critical</div>
            </div>
          </div>

          <div className="summary-item warning">
            <div className="summary-icon">
              <AlertTriangle size={16} />
            </div>
            <div className="summary-content">
              <div className="summary-count">
                {alerts.filter(a => a.type === 'warning' && !dismissedAlerts.has(a.id)).length}
              </div>
              <div className="summary-label">Warning</div>
            </div>
          </div>

          <div className="summary-item info">
            <div className="summary-icon">
              <Info size={16} />
            </div>
            <div className="summary-content">
              <div className="summary-count">
                {alerts.filter(a => a.type === 'info' && !dismissedAlerts.has(a.id)).length}
              </div>
              <div className="summary-label">Info</div>
            </div>
          </div>

          <div className="summary-item success">
            <div className="summary-icon">
              <CheckCircle size={16} />
            </div>
            <div className="summary-content">
              <div className="summary-count">
                {alerts.filter(a => a.type === 'success' && !dismissedAlerts.has(a.id)).length}
              </div>
              <div className="summary-label">Success</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

MonitoringAlerts.propTypes = {
  data: PropTypes.shape({
    alerts: PropTypes.arrayOf(PropTypes.shape({
      id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
      type: PropTypes.oneOf(['critical', 'warning', 'info', 'success']),
      title: PropTypes.string.isRequired,
      message: PropTypes.string,
      timestamp: PropTypes.string,
      source: PropTypes.string,
      severity: PropTypes.string,
      actionable: PropTypes.bool
    }))
  })
};

MonitoringAlerts.defaultProps = {
  data: null
};

export default MonitoringAlerts;