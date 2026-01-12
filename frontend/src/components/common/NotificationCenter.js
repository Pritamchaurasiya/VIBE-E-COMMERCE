import React, { useState, useEffect } from 'react';
import {
  Badge, IconButton, Menu, MenuItem, ListItemText, ListItemAvatar,
  Avatar, Typography, Box, Divider, Button
} from '@mui/material';
import { Notifications, ShoppingBag, LocalOffer, Info } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { formatDistanceToNow } from 'date-fns';
import { notificationsAPI } from '../../services/api';

const NotificationCenter = () => {
  const [anchorEl, setAnchorEl] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    // Poll for notifications every 60 seconds
    // In a real app, use WebSockets for real-time updates
    const fetchNotifications = async () => {
      try {
        const response = await notificationsAPI.getNotifications();
        if (response.data && response.data.results) {
          setNotifications(response.data.results.slice(0, 5)); // Show top 5
          setUnreadCount(response.data.unread_count || 0);
        }
      } catch (error) {
        console.error("Failed to fetch notifications");
      }
    };

    fetchNotifications();
    const interval = setInterval(fetchNotifications, 60000);
    return () => clearInterval(interval);
  }, []);

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleNotificationClick = (notification) => {
    handleClose();
    if (notification.link) {
      navigate(notification.link);
    }
    // Mark as read API call would go here
  };

  const getIcon = (type) => {
    switch (type) {
      case 'order': return <ShoppingBag color="primary" />;
      case 'deal': return <LocalOffer color="secondary" />;
      default: return <Info color="info" />;
    }
  };

  return (
    <>
      <IconButton color="inherit" onClick={handleClick}>
        <Badge badgeContent={unreadCount} color="error">
          <Notifications />
        </Badge>
      </IconButton>
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleClose}
        PaperProps={{
          sx: { width: 320, maxHeight: 400 }
        }}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        <Box sx={{ p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6" fontSize="1rem" fontWeight="bold">Notifications</Typography>
          <Button size="small" onClick={() => navigate('/notifications')}>View All</Button>
        </Box>
        <Divider />
        {notifications.length === 0 ? (
          <Box sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary">No new notifications</Typography>
          </Box>
        ) : (
          notifications.map((notification) => (
            <MenuItem
              key={notification.id}
              onClick={() => handleNotificationClick(notification)}
              sx={{
                py: 1.5,
                px: 2,
                bgcolor: notification.is_read ? 'transparent' : 'action.hover'
              }}
            >
              <ListItemAvatar>
                <Avatar sx={{ bgcolor: 'background.paper' }}>
                  {getIcon(notification.type)}
                </Avatar>
              </ListItemAvatar>
              <ListItemText
                primary={
                  <Typography variant="subtitle2" noWrap>
                    {notification.title}
                  </Typography>
                }
                secondary={
                  <React.Fragment>
                    <Typography component="span" variant="body2" color="text.primary" display="block" noWrap>
                      {notification.message}
                    </Typography>
                    <Typography component="span" variant="caption" color="text.secondary">
                      {formatDistanceToNow(new Date(notification.created_at), { addSuffix: true })}
                    </Typography>
                  </React.Fragment>
                }
              />
            </MenuItem>
          ))
        )}
      </Menu>
    </>
  );
};

export default NotificationCenter;
