import React, { useState } from 'react';
import PropTypes from 'prop-types';
import {
  BarChart3,
  LineChart,
  PieChart,
  TrendingUp,
  Calendar,
  Filter,
  Download,
  Maximize2,
  RefreshCw
} from 'lucide-react';
import './AnalyticsCharts.css';

const AnalyticsCharts = ({ data, loading }) => {
  const [selectedChart, setSelectedChart] = useState('overview');
  const [timeRange, setTimeRange] = useState('7d');
  const [chartType, setChartType] = useState('line');

  // Use data prop for dynamic content
  const chartData = data || {};

  const chartOptions = [
    { id: 'overview', label: 'Overview', icon: <BarChart3 size={18} /> },
    { id: 'traffic', label: 'Traffic', icon: <TrendingUp size={18} /> },
    { id: 'performance', label: 'Performance', icon: <LineChart size={18} /> },
    { id: 'conversion', label: 'Conversion', icon: <PieChart size={18} /> }
  ];

  const renderChartPlaceholder = (title, description) => (
    <div className="chart-placeholder">
      <div className="chart-icon">
        <BarChart3 size={48} />
      </div>
      <div className="chart-info">
        <h4>{title}</h4>
        <p>{description}</p>
      </div>
      <div className="chart-actions">
        <button className="chart-action-btn" aria-label="Maximize chart">
          <Maximize2 size={16} />
        </button>
        <button className="chart-action-btn" aria-label="Download chart">
          <Download size={16} />
        </button>
      </div>
    </div>
  );

  const renderOverviewCharts = () => (
    <div className="charts-grid overview-grid">
      <div className="chart-container">
        <div className="chart-header">
          <h4>User Sessions</h4>
          <div className="chart-controls">
            <button className="control-btn active">7D</button>
            <button className="control-btn">30D</button>
            <button className="control-btn">90D</button>
          </div>
        </div>
        {renderChartPlaceholder(
          'User Sessions Over Time',
          `Track daily active users: ${chartData.sessions || 'N/A'}`
        )}
      </div>

      <div className="chart-container">
        <div className="chart-header">
          <h4>Revenue Trend</h4>
          <div className="chart-controls">
            <button className="control-btn active">Daily</button>
            <button className="control-btn">Weekly</button>
            <button className="control-btn">Monthly</button>
          </div>
        </div>
        {renderChartPlaceholder('Revenue Analytics', 'Monitor revenue growth and trends')}
      </div>

      <div className="chart-container">
        <div className="chart-header">
          <h4>Conversion Funnel</h4>
          <div className="chart-controls">
            <button className="control-btn active">This Week</button>
            <button className="control-btn">This Month</button>
          </div>
        </div>
        {renderChartPlaceholder('Conversion Analysis', 'Analyze user journey and conversion rates')}
      </div>

      <div className="chart-container">
        <div className="chart-header">
          <h4>Geographic Distribution</h4>
          <div className="chart-controls">
            <button className="control-btn active">World</button>
            <button className="control-btn">Region</button>
          </div>
        </div>
        {renderChartPlaceholder('User Geography', 'Visualize user distribution across regions')}
      </div>
    </div>
  );

  const renderTrafficCharts = () => (
    <div className="charts-grid traffic-grid">
      <div className="chart-container full-width">
        <div className="chart-header">
          <h4>Website Traffic</h4>
          <div className="chart-controls">
            <label htmlFor="time-range-select" className="visually-hidden">
              Select time range
            </label>
            <select
              id="time-range-select"
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="time-select"
            >
              <option value="24h">Last 24 Hours</option>
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
              <option value="90d">Last 90 Days</option>
            </select>
            <button className="control-btn active">Page Views</button>
            <button className="control-btn">Unique Visitors</button>
            <button className="control-btn">Bounce Rate</button>
          </div>
        </div>
        {renderChartPlaceholder('Traffic Analytics', 'Comprehensive traffic analysis with visitor insights')}
      </div>

      <div className="chart-container">
        <div className="chart-header">
          <h4>Traffic Sources</h4>
          <div className="chart-controls">
            <button className="control-btn active">Pie</button>
            <button className="control-btn">Bar</button>
          </div>
        </div>
        {renderChartPlaceholder('Traffic Sources', 'Breakdown of traffic by source')}
      </div>

      <div className="chart-container">
        <div className="chart-header">
          <h4>Device Breakdown</h4>
          <div className="chart-controls">
            <button className="control-btn active">Mobile</button>
            <button className="control-btn">Desktop</button>
            <button className="control-btn">Tablet</button>
          </div>
        </div>
        {renderChartPlaceholder('Device Analytics', 'Device and browser usage statistics')}
      </div>
    </div>
  );

  const renderPerformanceCharts = () => (
    <div className="charts-grid performance-grid">
      <div className="chart-container">
        <div className="chart-header">
          <h4>Page Load Times</h4>
          <div className="chart-controls">
            <button className="control-btn active">Real-time</button>
            <button className="control-btn">Historical</button>
          </div>
        </div>
        {renderChartPlaceholder('Performance Metrics', 'Monitor page load times and performance')}
      </div>

      <div className="chart-container">
        <div className="chart-header">
          <h4>API Response Times</h4>
          <div className="chart-controls">
            <button className="control-btn active">Last Hour</button>
            <button className="control-btn">Today</button>
          </div>
        </div>
        {renderChartPlaceholder('API Performance', 'API endpoint response time analysis')}
      </div>

      <div className="chart-container">
        <div className="chart-header">
          <h4>Error Rates</h4>
          <div className="chart-controls">
            <button className="control-btn active">All Errors</button>
            <button className="control-btn">Critical</button>
          </div>
        </div>
        {renderChartPlaceholder('Error Tracking', 'Error frequency and type distribution')}
      </div>

      <div className="chart-container">
        <div className="chart-header">
          <h4>Database Performance</h4>
          <div className="chart-controls">
            <button className="control-btn active">Queries</button>
            <button className="control-btn">Connections</button>
          </div>
        </div>
        {renderChartPlaceholder('Database Metrics', 'Database performance and query analysis')}
      </div>
    </div>
  );

  const renderConversionCharts = () => (
    <div className="charts-grid conversion-grid">
      <div className="chart-container">
        <div className="chart-header">
          <h4>Conversion Funnel</h4>
          <div className="chart-controls">
            <button className="control-btn active">Sales</button>
            <button className="control-btn">Signups</button>
          </div>
        </div>
        {renderChartPlaceholder('Conversion Funnel', 'Track user journey through conversion steps')}
      </div>

      <div className="chart-container">
        <div className="chart-header">
          <h4>Revenue by Channel</h4>
          <div className="chart-controls">
            <button className="control-btn active">Monthly</button>
            <button className="control-btn">Weekly</button>
          </div>
        </div>
        {renderChartPlaceholder('Channel Performance', 'Revenue breakdown by marketing channel')}
      </div>

      <div className="chart-container">
        <div className="chart-header">
          <h4>Customer Lifetime Value</h4>
          <div className="chart-controls">
            <button className="control-btn active">CLV</button>
            <button className="control-btn">Cohort</button>
          </div>
        </div>
        {renderChartPlaceholder('CLV Analysis', 'Customer lifetime value trends and cohorts')}
      </div>

      <div className="chart-container">
        <div className="chart-header">
          <h4>Retention Rate</h4>
          <div className="chart-controls">
            <button className="control-btn active">30 Days</button>
            <button className="control-btn">90 Days</button>
          </div>
        </div>
        {renderChartPlaceholder('Retention Analytics', 'User retention and churn analysis')}
      </div>
    </div>
  );

  const renderChartContent = () => {
    switch (selectedChart) {
      case 'traffic':
        return renderTrafficCharts();
      case 'performance':
        return renderPerformanceCharts();
      case 'conversion':
        return renderConversionCharts();
      default:
        return renderOverviewCharts();
    }
  };

  if (loading) {
    return (
      <div className="analytics-charts">
        <div className="charts-loading">
          <div className="loading-shimmer chart-skeleton"></div>
          <div className="loading-shimmer chart-skeleton"></div>
          <div className="loading-shimmer chart-skeleton"></div>
          <div className="loading-shimmer chart-skeleton"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="analytics-charts">
      {/* Chart Navigation */}
      <div className="chart-navigation">
        <div className="nav-tabs">
          {chartOptions.map(option => (
            <button
              key={option.id}
              className={`nav-tab ${selectedChart === option.id ? 'active' : ''}`}
              onClick={() => setSelectedChart(option.id)}
            >
              {option.icon}
              <span>{option.label}</span>
            </button>
          ))}
        </div>

        <div className="nav-controls">
          <button className="nav-btn">
            <Filter size={16} />
            Filters
          </button>
          <button className="nav-btn">
            <RefreshCw size={16} />
            Refresh
          </button>
          <button className="nav-btn">
            <Download size={16} />
            Export
          </button>
        </div>
      </div>

      {/* Chart Type Selector */}
      <div className="chart-type-selector">
        <span className="chart-type-label">Chart Type:</span>
        <div className="type-buttons">
          <button
            className={`type-btn ${chartType === 'line' ? 'active' : ''}`}
            onClick={() => setChartType('line')}
          >
            <LineChart size={16} />
            Line
          </button>
          <button
            className={`type-btn ${chartType === 'bar' ? 'active' : ''}`}
            onClick={() => setChartType('bar')}
          >
            <BarChart3 size={16} />
            Bar
          </button>
          <button
            className={`type-btn ${chartType === 'pie' ? 'active' : ''}`}
            onClick={() => setChartType('pie')}
          >
            <PieChart size={16} />
            Pie
          </button>
        </div>
      </div>

      {/* Chart Content */}
      <div className="chart-content">
        {renderChartContent()}
      </div>

      {/* Chart Insights */}
      <div className="chart-insights">
        <h4>Key Insights</h4>
        <div className="insights-grid">
          <div className="insight-card">
            <div className="insight-icon positive">
              <TrendingUp size={20} />
            </div>
            <div className="insight-content">
              <div className="insight-title">Traffic Growth</div>
              <div className="insight-value">+23.5% this week</div>
              <div className="insight-description">Compared to previous period</div>
            </div>
          </div>

          <div className="insight-card">
            <div className="insight-icon neutral">
              <BarChart3 size={20} />
            </div>
            <div className="insight-content">
              <div className="insight-title">Peak Hours</div>
              <div className="insight-value">2-4 PM</div>
              <div className="insight-description">Highest traffic period</div>
            </div>
          </div>

          <div className="insight-card">
            <div className="insight-icon positive">
              <PieChart size={20} />
            </div>
            <div className="insight-content">
              <div className="insight-title">Mobile Traffic</div>
              <div className="insight-value">68% of total</div>
              <div className="insight-description">Increasing mobile usage</div>
            </div>
          </div>

          <div className="insight-card">
            <div className="insight-icon warning">
              <Calendar size={20} />
            </div>
            <div className="insight-content">
              <div className="insight-title">Best Performing Day</div>
              <div className="insight-value">Thursday</div>
              <div className="insight-description">Highest conversion rates</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

AnalyticsCharts.propTypes = {
  data: PropTypes.shape({
    sessions: PropTypes.number,
    revenue: PropTypes.number,
    conversions: PropTypes.number,
    traffic: PropTypes.object,
    performance: PropTypes.object
  }),
  loading: PropTypes.bool
};

AnalyticsCharts.defaultProps = {
  data: null,
  loading: false
};

export default AnalyticsCharts;