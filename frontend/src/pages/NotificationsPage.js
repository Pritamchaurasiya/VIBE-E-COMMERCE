import React, { useEffect, useState } from "react";
import TopNav from "../components/layout/TopNav";
import BottomNav from "../components/layout/BottomNav";
import { useAuth } from "../utils/AuthContext";
import { notificationsAPI } from "../services/api";
import { Notifications, LocalOffer, Info } from "@mui/icons-material";

/**
 * Notifications Page
 * Lists all user notifications (Price drops, Order updates, etc.)
 */
const NotificationsPage = () => {
  const { isAuthenticated } = useAuth();
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    if (!isAuthenticated) return;

    // Fetch notifications from backend
    const fetchNotifications = async () => {
      try {
        const response = await notificationsAPI.getNotifications();
        // Handle various response structures
        const data = response.data?.notifications || response.data || [];

        // Map backend format to frontend UI format
        const mapped = data.map(n => ({
          id: n.id,
          type: mapNotificationType(n.notification_type),
          title: n.title,
          message: n.message || "", // Ensure message exists
          time: new Date(n.created_at).toLocaleDateString(), // Simple date formatting
          read: n.is_read
        }));

        setNotifications(mapped);
      } catch (error) {
        console.error("Failed to fetch notifications:", error);
        // Fallback to mock data or empty state if needed, but let's leave it blank/error
      }
    };

    fetchNotifications();
  }, [isAuthenticated]);

  const mapNotificationType = (type) => {
    switch(type) {
      case 'order': return 'order';
      case 'promotion': return 'promo';
      case 'price_alert': return 'price';
      default: return 'system';
    }
  };

  const getIcon = (type) => {
    switch (type) {
      case 'promo': return <LocalOffer color="error" fontSize="small" />;
      case 'order': return <Info color="primary" fontSize="small" />;
      default: return <Notifications color="action" fontSize="small" />;
    }
  };

  return (
    <div className="agri-theme">
      <TopNav />

      <main className="agri-main">
        <div className="agri-container">
          <div className="agri-page-header">
            <h1 className="agri-page-title">Notifications</h1>
          </div>

          <div className="agri-notification-list">
            {notifications.length === 0 ? (
              <div className="agri-empty-state">
                <Notifications style={{ fontSize: 64, color: '#ccc' }} />
                <p>No notifications yet</p>
              </div>
            ) : (
              notifications.map((notif) => (
                <div
                  key={notif.id}
                  className={`agri-notification-card ${notif.read ? 'read' : 'unread'}`}
                  style={{
                    background: notif.read ? '#fff' : '#f0f9f0',
                    padding: '16px',
                    marginBottom: '12px',
                    borderRadius: '8px',
                    borderLeft: notif.read ? 'none' : '4px solid var(--agri-green-primary)',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
                  }}
                >
                  <div className="agri-notif-header" style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
                    <span className="agri-notif-icon">
                      {getIcon(notif.type)}
                    </span>
                    <span style={{ fontWeight: 600, marginLeft: '8px', flex: 1 }}>{notif.title}</span>
                    <span style={{ fontSize: '0.75rem', color: '#999' }}>{notif.time}</span>
                  </div>
                  <p style={{ margin: 0, color: '#555', fontSize: '0.9rem' }}>{notif.message}</p>
                </div>
              ))
            )}
          </div>
        </div>
      </main>

      <BottomNav />
    </div>
  );
};

export default NotificationsPage;
