import React, { useState } from 'react';
import PropTypes from 'prop-types';
import {
  Users,
  Target,
  TrendingUp,
  Plus,
  Edit,
  Trash2,
  Eye,
  BarChart3,
  PieChart,
  UserCheck,
  UserX,
  Clock,
  Star
} from 'lucide-react';
import './UserSegmentationWidget.css';

const UserSegmentationWidget = ({ data, loading, expanded }) => {
  const [selectedSegment, setSelectedSegment] = useState(null);
  const [viewMode, setViewMode] = useState('segments'); // 'segments' or 'members'
  const [showCreateModal, setShowCreateModal] = useState(false);

  const formatNumber = (num) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  const getSegmentColor = (segmentType) => {
    const colors = {
      'high-value': '#10b981',
      'frequent-buyer': '#3b82f6',
      'at-risk': '#ef4444',
      'new-customer': '#f59e0b',
      'loyal': '#8b5cf6',
      'inactive': '#6b7280'
    };
    return colors[segmentType] || '#64748b';
  };

  const getSegmentIcon = (segmentType) => {
    switch (segmentType) {
      case 'high-value': return <Star size={20} />;
      case 'frequent-buyer': return <TrendingUp size={20} />;
      case 'at-risk': return <UserX size={20} />;
      case 'new-customer': return <UserCheck size={20} />;
      case 'loyal': return <Users size={20} />;
      case 'inactive': return <Clock size={20} />;
      default: return <Target size={20} />;
    }
  };

  const getSegmentDescription = (segmentType) => {
    const descriptions = {
      'high-value': 'Users with high lifetime value and frequent purchases',
      'frequent-buyer': 'Regular customers with consistent buying patterns',
      'at-risk': 'Users showing signs of reduced engagement',
      'new-customer': 'Recently registered users in onboarding phase',
      'loyal': 'Long-term customers with high satisfaction scores',
      'inactive': 'Users with no recent activity or purchases'
    };
    return descriptions[segmentType] || 'Custom user segment';
  };

  if (loading) {
    return (
      <div className={`user-segmentation-widget ${expanded ? 'expanded' : ''}`}>
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
    <div className={`user-segmentation-widget ${expanded ? 'expanded' : ''}`}>
      {/* Header */}
      <div className="widget-header">
        <div className="header-info">
          <h3>User Segmentation</h3>
          <div className="segmentation-stats">
            <div className="stat-item">
              <span className="stat-value">{data?.total_segments || 0}</span>
              <span className="stat-label">Segments</span>
            </div>
            <div className="stat-item">
              <span className="stat-value">{formatNumber(data?.total_users_segmented || 0)}</span>
              <span className="stat-label">Users Segmented</span>
            </div>
          </div>
        </div>
        <div className="header-actions">
          <div className="view-mode-toggle">
            <button
              className={`view-btn ${viewMode === 'segments' ? 'active' : ''}`}
              onClick={() => setViewMode('segments')}
            >
              <PieChart size={16} />
              Segments
            </button>
            <button
              className={`view-btn ${viewMode === 'members' ? 'active' : ''}`}
              onClick={() => setViewMode('members')}
            >
              <Users size={16} />
              Members
            </button>
          </div>
          <button
            className="create-segment-btn"
            onClick={() => setShowCreateModal(true)}
          >
            <Plus size={16} />
            New Segment
          </button>
        </div>
      </div>

      {/* Segmentation Overview */}
      <div className="segmentation-overview">
        <h4>Segment Distribution</h4>
        <div className="overview-grid">
          {data?.segment_distribution && Object.entries(data.segment_distribution).map(([segmentType, count]) => {
            const percentage = ((count / (data.total_users_segmented || 1)) * 100).toFixed(1);
            return (
              <div key={segmentType} className="overview-card">
                <div className="card-icon" style={{ color: getSegmentColor(segmentType) }}>
                  {getSegmentIcon(segmentType)}
                </div>
                <div className="card-content">
                  <div className="card-title">
                    {segmentType.split('-').map(word =>
                      word.charAt(0).toUpperCase() + word.slice(1)
                    ).join(' ')}
                  </div>
                  <div className="card-stats">
                    <span className="user-count">{formatNumber(count)} users</span>
                    <span className="percentage">{percentage}%</span>
                  </div>
                  <div className="progress-bar">
                    <div
                      className="progress-fill"
                      style={{
                        width: `${percentage}%`,
                        backgroundColor: getSegmentColor(segmentType)
                      }}
                    ></div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Segments List */}
      {viewMode === 'segments' && (
        <div className="segments-list">
          <h4>Active Segments</h4>
          <div className="segments-grid">
            {data?.segments && data.segments.map((segment, index) => (
              <div
                key={index}
                className={`segment-card ${selectedSegment === index ? 'selected' : ''}`}
                onClick={() => setSelectedSegment(selectedSegment === index ? null : index)}
              >
                <div className="segment-header">
                  <div className="segment-info">
                    <div className="segment-icon" style={{ color: getSegmentColor(segment.type) }}>
                      {getSegmentIcon(segment.type)}
                    </div>
                    <div className="segment-details">
                      <div className="segment-name">{segment.name}</div>
                      <div className="segment-description">{segment.description}</div>
                    </div>
                  </div>
                  <div className="segment-actions">
                    <button className="action-btn">
                      <Eye size={14} />
                    </button>
                    <button className="action-btn">
                      <Edit size={14} />
                    </button>
                    <button className="action-btn delete">
                      <Trash2 size={14} />
                    </button>
                  </div>
                </div>

                <div className="segment-metrics">
                  <div className="metric">
                    <span className="metric-label">Members</span>
                    <span className="metric-value">{formatNumber(segment.member_count)}</span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Growth</span>
                    <span className={`metric-value ${segment.growth >= 0 ? 'positive' : 'negative'}`}>
                      {segment.growth >= 0 ? '+' : ''}{segment.growth.toFixed(1)}%
                    </span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Avg Value</span>
                    <span className="metric-value">${segment.avg_value}</span>
                  </div>
                </div>

                {selectedSegment === index && (
                  <div className="segment-expanded">
                    <div className="criteria-section">
                      <h5>Segmentation Criteria</h5>
                      <div className="criteria-list">
                        {segment.criteria && Object.entries(segment.criteria).map(([key, value]) => (
                          <div key={key} className="criteria-item">
                            <span className="criteria-key">{key.replace(/_/g, ' ')}</span>
                            <span className="criteria-value">{value}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="performance-section">
                      <h5>Performance Metrics</h5>
                      <div className="performance-grid">
                        <div className="performance-item">
                          <span className="performance-label">Conversion Rate</span>
                          <span className="performance-value">{segment.conversion_rate}%</span>
                        </div>
                        <div className="performance-item">
                          <span className="performance-label">Retention Rate</span>
                          <span className="performance-value">{segment.retention_rate}%</span>
                        </div>
                        <div className="performance-item">
                          <span className="performance-label">Engagement Score</span>
                          <span className="performance-value">{segment.engagement_score}/10</span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Members View */}
      {viewMode === 'members' && (
        <div className="members-view">
          <h4>Segment Members</h4>
          {selectedSegment !== null && data?.segments[selectedSegment] ? (
            <div className="selected-segment-members">
              <div className="segment-header-info">
                <h5>{data.segments[selectedSegment].name}</h5>
                <p>{getSegmentDescription(data.segments[selectedSegment].type)}</p>
              </div>

              <div className="members-stats">
                <div className="member-stat">
                  <span className="stat-value">{formatNumber(data.segments[selectedSegment].member_count)}</span>
                  <span className="stat-label">Total Members</span>
                </div>
                <div className="member-stat">
                  <span className="stat-value">{data.segments[selectedSegment].active_members}</span>
                  <span className="stat-label">Active (30d)</span>
                </div>
                <div className="member-stat">
                  <span className="stat-value">${data.segments[selectedSegment].total_value}</span>
                  <span className="stat-label">Total Value</span>
                </div>
              </div>

              <div className="member-filters">
                <div className="filter-group">
                  <label>Status:</label>
                  <select className="filter-select">
                    <option value="all">All Members</option>
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                    <option value="new">New</option>
                  </select>
                </div>
                <div className="filter-group">
                  <label>Sort by:</label>
                  <select className="filter-select">
                    <option value="recent">Most Recent</option>
                    <option value="value">Highest Value</option>
                    <option value="activity">Most Active</option>
                  </select>
                </div>
              </div>

              <div className="members-table">
                <div className="table-header">
                  <div className="table-cell">User</div>
                  <div className="table-cell">Segment</div>
                  <div className="table-cell">Joined</div>
                  <div className="table-cell">Value</div>
                  <div className="table-cell">Activity</div>
                  <div className="table-cell">Actions</div>
                </div>
                {data.segments[selectedSegment].sample_members &&
                 data.segments[selectedSegment].sample_members.map((member, index) => (
                  <div key={index} className="table-row">
                    <div className="table-cell">
                      <div className="user-info">
                        <div className="user-avatar">
                          {member.name.charAt(0).toUpperCase()}
                        </div>
                        <div className="user-details">
                          <div className="user-name">{member.name}</div>
                          <div className="user-email">{member.email}</div>
                        </div>
                      </div>
                    </div>
                    <div className="table-cell">
                      <span className="segment-badge" style={{
                        backgroundColor: getSegmentColor(data.segments[selectedSegment].type) + '20',
                        color: getSegmentColor(data.segments[selectedSegment].type)
                      }}>
                        {data.segments[selectedSegment].type}
                      </span>
                    </div>
                    <div className="table-cell">
                      {new Date(member.joined_date).toLocaleDateString()}
                    </div>
                    <div className="table-cell">
                      ${member.lifetime_value}
                    </div>
                    <div className="table-cell">
                      <span className={`activity-status ${member.status}`}>
                        {member.status}
                      </span>
                    </div>
                    <div className="table-cell">
                      <button className="action-btn small">
                        <Eye size={14} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="no-segment-selected">
              <Target size={48} />
              <h5>Select a Segment</h5>
              <p>Choose a segment from the list above to view its members</p>
            </div>
          )}
        </div>
      )}

      {/* Segmentation Insights */}
      <div className="segmentation-insights">
        <h4>Segmentation Insights</h4>
        <div className="insights-grid">
          <div className="insight-card">
            <div className="insight-icon">
              <TrendingUp size={20} />
            </div>
            <div className="insight-content">
              <div className="insight-title">Growth Opportunity</div>
              <div className="insight-description">
                High-value segment growing at {data?.growth_opportunity || 0}% monthly
              </div>
            </div>
          </div>

          <div className="insight-card">
            <div className="insight-icon">
              <Target size={20} />
            </div>
            <div className="insight-content">
              <div className="insight-title">Retention Focus</div>
              <div className="insight-description">
                {data?.at_risk_users || 0} users need retention strategies
              </div>
            </div>
          </div>

          <div className="insight-card">
            <div className="insight-icon">
              <BarChart3 size={20} />
            </div>
            <div className="insight-content">
              <div className="insight-title">Segmentation ROI</div>
              <div className="insight-description">
                Segmented campaigns show {data?.segmentation_roi || 0}% higher conversion
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Create Segment Modal */}
      {showCreateModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>Create New Segment</h3>
              <button
                className="close-btn"
                onClick={() => setShowCreateModal(false)}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <p>This feature would open a comprehensive segment creation interface.</p>
              <p>It would include:</p>
              <ul>
                <li>Drag-and-drop criteria builder</li>
                <li>Real-time member count preview</li>
                <li>Segment performance simulation</li>
                <li>Automated segment recommendations</li>
              </ul>
            </div>
            <div className="modal-footer">
              <button
                className="btn-secondary"
                onClick={() => setShowCreateModal(false)}
              >
                Cancel
              </button>
              <button className="btn-primary">
                Create Segment
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

UserSegmentationWidget.propTypes = {
  data: PropTypes.shape({
    total_segments: PropTypes.number,
    total_users_segmented: PropTypes.number,
    segment_distribution: PropTypes.object,
    segments: PropTypes.arrayOf(PropTypes.shape({
      name: PropTypes.string,
      type: PropTypes.string,
      description: PropTypes.string,
      member_count: PropTypes.number,
      growth: PropTypes.number,
      avg_value: PropTypes.number,
      criteria: PropTypes.object,
      conversion_rate: PropTypes.number,
      retention_rate: PropTypes.number,
      engagement_score: PropTypes.number,
      active_members: PropTypes.number,
      total_value: PropTypes.number,
      sample_members: PropTypes.array
    })),
    growth_opportunity: PropTypes.number,
    at_risk_users: PropTypes.number,
    segmentation_roi: PropTypes.number
  }),
  loading: PropTypes.bool,
  expanded: PropTypes.bool
};

UserSegmentationWidget.defaultProps = {
  data: null,
  loading: false,
  expanded: false
};

export default UserSegmentationWidget;
