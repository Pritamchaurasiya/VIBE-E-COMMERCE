import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import {
  Users,
  Eye,
  Clock,
  TrendingUp,
  TrendingDown,
  MapPin,
  ShoppingCart,
  Heart,
  Search
} from 'lucide-react';
import './UserAnalyticsWidget.css';

const UserAnalyticsWidget = ({ data, loading, expanded }) => {
  const [animatedValues, setAnimatedValues] = useState({
    totalSessions: 0,
    totalInteractions: 0,
    averageSessionDuration: 0,
    conversionRate: 0,
    engagementScore: 0,
    loyaltyScore: 0,
    lifetimeValue: 0
  });

  const [selectedTimeframe, setSelectedTimeframe] = useState('7d');
  const [selectedMetric, setSelectedMetric] = useState('overview');

  // Animate values when data changes
  useEffect(() => {
    if (data && !loading) {
      const targets = {
        totalSessions: data.total_sessions || 0,
        totalInteractions: data.total_interactions || 0,
        averageSessionDuration: data.average_session_duration || 0,
        conversionRate: data.conversion_rate || 0,
        engagementScore: data.engagement_score || 0,
        loyaltyScore: data.loyalty_score || 0,
        lifetimeValue: data.lifetime_value || 0
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

  const formatDuration = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const getScoreColor = (score) => {
    if (score >= 80) return '#10b981';
    if (score >= 60) return '#f59e0b';
    return '#ef4444';
  };

  const getScoreGradient = (score) => {
    if (score >= 80) return 'linear-gradient(135deg, #10b981, #059669)';
    if (score >= 60) return 'linear-gradient(135deg, #f59e0b, #d97706)';
    return 'linear-gradient(135deg, #ef4444, #dc2626)';
  };

  const metrics = [
    {
      title: 'Total Sessions',
      value: formatNumber(animatedValues.totalSessions),
      change: data?.sessions_change || 0,
      icon: <Users size={24} />,
      color: '#3b82f6'
    },
    {
      title: 'Interactions',
      value: formatNumber(animatedValues.totalInteractions),
      change: data?.interactions_change || 0,
      icon: <Eye size={24} />,
      color: '#10b981'
    },
    {
      title: 'Avg Session',
      value: formatDuration(animatedValues.averageSessionDuration),
      change: data?.session_duration_change || 0,
      icon: <Clock size={24} />,
      color: '#f59e0b'
    },
    {
      title: 'Conversion Rate',
      value: `${animatedValues.conversionRate.toFixed(1)}%`,
      change: data?.conversion_change || 0,
      icon: <TrendingUp size={24} />,
      color: '#8b5cf6'
    }
  ];

  const scoreMetrics = [
    {
      title: 'Engagement Score',
      value: animatedValues.engagementScore.toFixed(0),
      max: 100,
      color: getScoreColor(animatedValues.engagementScore),
      gradient: getScoreGradient(animatedValues.engagementScore)
    },
    {
      title: 'Loyalty Score',
      value: animatedValues.loyaltyScore.toFixed(0),
      max: 100,
      color: getScoreColor(animatedValues.loyaltyScore),
      gradient: getScoreGradient(animatedValues.loyaltyScore)
    }
  ];

  if (loading) {
    return (
      <div className={`user-analytics-widget ${expanded ? 'expanded' : ''}`}>
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
    <div className={`user-analytics-widget ${expanded ? 'expanded' : ''}`}>
      {/* Header */}
      <div className="widget-header">
        <div className="header-info">
          <h3>User Analytics</h3>
          <div className="timeframe-selector">
            <select
              value={selectedTimeframe}
              onChange={(e) => setSelectedTimeframe(e.target.value)}
              className="timeframe-select"
            >
              <option value="1d">Last 24 Hours</option>
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
              <option value="90d">Last 90 Days</option>
            </select>
          </div>
        </div>
        <div className="user-insight">
          <div className="insight-summary">
            <span className="insight-text">
              {data?.user_insight || 'Analyzing user behavior patterns...'}
            </span>
          </div>
        </div>
      </div>

      {/* Main Metrics */}
      <div className={`main-metrics ${expanded ? 'expanded' : ''}`}>
        {metrics.map((metric, index) => (
          <div key={index} className="metric-card">
            <div className="metric-icon" style={{ color: metric.color }}>
              {metric.icon}
            </div>
            <div className="metric-content">
              <div className="metric-value">{metric.value}</div>
              <div className="metric-title">{metric.title}</div>
              <div
                className={`metric-change ${metric.change >= 0 ? 'positive' : 'negative'}`}
              >
                {metric.change >= 0 ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                <span>{Math.abs(metric.change).toFixed(1)}%</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Score Metrics */}
      <div className="score-metrics">
        <h4>User Scores</h4>
        <div className="scores-grid">
          {scoreMetrics.map((score, index) => (
            <div key={index} className="score-card">
              <div className="score-header">
                <span className="score-title">{score.title}</span>
                <span className="score-value" style={{ color: score.color }}>
                  {score.value}
                </span>
              </div>
              <div className="score-bar">
                <div
                  className="score-fill"
                  style={{
                    width: `${(score.value / score.max) * 100}%`,
                    background: score.gradient
                  }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Top Interactions */}
      {data?.top_interactions && data.top_interactions.length > 0 && (
        <div className="top-interactions">
          <h4>Top User Interactions</h4>
          <div className="interactions-list">
            {data.top_interactions.slice(0, expanded ? 10 : 5).map((interaction, index) => (
              <div key={index} className="interaction-item">
                <div className="interaction-rank">#{index + 1}</div>
                <div className="interaction-details">
                  <div className="interaction-type">{interaction.type}</div>
                  <div className="interaction-description">{interaction.description}</div>
                </div>
                <div className="interaction-count">
                  <span className="count">{formatNumber(interaction.count)}</span>
                  <span className="label">times</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Behavior Patterns */}
      {data?.behavior_patterns && data.behavior_patterns.length > 0 && (
        <div className="behavior-patterns">
          <h4>Behavior Patterns</h4>
          <div className="patterns-grid">
            {data.behavior_patterns.slice(0, expanded ? 6 : 3).map((pattern, index) => (
              <div key={index} className="pattern-card">
                <div className="pattern-icon">
                  {pattern.type === 'purchase' && <ShoppingCart size={20} />}
                  {pattern.type === 'browse' && <Eye size={20} />}
                  {pattern.type === 'search' && <Search size={20} />}
                  {pattern.type === 'wishlist' && <Heart size={20} />}
                </div>
                <div className="pattern-content">
                  <div className="pattern-title">{pattern.pattern}</div>
                  <div className="pattern-confidence">
                    <span className="confidence-label">Confidence:</span>
                    <span className="confidence-value">{(pattern.confidence * 100).toFixed(0)}%</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Preferred Categories */}
      {data?.preferred_categories && data.preferred_categories.length > 0 && (
        <div className="preferred-categories">
          <h4>Preferred Categories</h4>
          <div className="categories-list">
            {data.preferred_categories.slice(0, expanded ? 8 : 4).map((category, index) => (
              <div key={index} className="category-item">
                <div className="category-info">
                  <span className="category-name">{category.name}</span>
                  <span className="category-score">{category.score.toFixed(1)}</span>
                </div>
                <div className="category-bar">
                  <div
                    className="category-fill"
                    style={{ width: `${category.score}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Geographic Data */}
      {data?.geographic_data && (
        <div className="geographic-data">
          <h4>User Locations</h4>
          <div className="locations-list">
            {Object.entries(data.geographic_data).slice(0, expanded ? 8 : 4).map(([location, stats]) => (
              <div key={location} className="location-item">
                <div className="location-info">
                  <MapPin size={16} />
                  <span className="location-name">{location}</span>
                </div>
                <div className="location-stats">
                  <span className="user-count">{formatNumber(stats.users)} users</span>
                  <span className="session-count">{formatNumber(stats.sessions)} sessions</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Purchase History Summary */}
      {data?.purchase_history && data.purchase_history.length > 0 && (
        <div className="purchase-summary">
          <h4>Purchase Summary</h4>
          <div className="purchase-stats">
            <div className="purchase-stat">
              <div className="stat-value">{formatCurrency(animatedValues.lifetimeValue)}</div>
              <div className="stat-label">Lifetime Value</div>
            </div>
            <div className="purchase-stat">
              <div className="stat-value">{formatNumber(data.total_orders || 0)}</div>
              <div className="stat-label">Total Orders</div>
            </div>
            <div className="purchase-stat">
              <div className="stat-value">{formatCurrency(data.average_order_value || 0)}</div>
              <div className="stat-label">Avg Order Value</div>
            </div>
          </div>
        </div>
      )}

      {/* Predictive Analytics */}
      {data?.predicted_churn_risk !== undefined && (
        <div className="predictive-analytics">
          <h4>Predictive Insights</h4>
          <div className="prediction-card">
            <div className="prediction-header">
              <span className="prediction-title">Churn Risk</span>
              <span className={`prediction-value ${data.predicted_churn_risk > 50 ? 'high' : 'low'}`}>
                {data.predicted_churn_risk.toFixed(1)}%
              </span>
            </div>
            <div className="prediction-bar">
              <div
                className="prediction-fill"
                style={{
                  width: `${data.predicted_churn_risk}%`,
                  background: data.predicted_churn_risk > 50 ?
                    'linear-gradient(90deg, #ef4444, #dc2626)' :
                    'linear-gradient(90deg, #10b981, #059669)'
                }}
              ></div>
            </div>
            <div className="prediction-description">
              {data.predicted_churn_risk > 50 ?
                'High risk - Consider retention strategies' :
                'Low risk - User likely to remain active'
              }
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

UserAnalyticsWidget.propTypes = {
  data: PropTypes.shape({
    total_sessions: PropTypes.number,
    total_interactions: PropTypes.number,
    average_session_duration: PropTypes.number,
    conversion_rate: PropTypes.number,
    engagement_score: PropTypes.number,
    loyalty_score: PropTypes.number,
    lifetime_value: PropTypes.number,
    sessions_change: PropTypes.number,
    interactions_change: PropTypes.number,
    session_duration_change: PropTypes.number,
    conversion_change: PropTypes.number,
    user_insight: PropTypes.string,
    top_interactions: PropTypes.array,
    behavior_patterns: PropTypes.array,
    preferred_categories: PropTypes.array,
    geographic_data: PropTypes.object,
    purchase_history: PropTypes.array,
    total_orders: PropTypes.number,
    average_order_value: PropTypes.number,
    predicted_churn_risk: PropTypes.number
  }),
  loading: PropTypes.bool,
  expanded: PropTypes.bool
};

UserAnalyticsWidget.defaultProps = {
  data: null,
  loading: false,
  expanded: false
};

export default UserAnalyticsWidget;
