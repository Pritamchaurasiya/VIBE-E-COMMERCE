import React, { useState, useEffect, useCallback } from "react";
import { Link } from "react-router-dom";
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Avatar,
  Chip,
  Button,
  IconButton,
  TextField,
  InputAdornment,
  Tabs,
  Tab,
  Badge,
  Divider,
  Alert,
  Skeleton,
  Paper,
  Fab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from "@mui/material";
import {
  Notifications,
  LocalShipping,
  LocalOffer,
  Info,
  Error as ErrorIcon,
  CheckCircle,
  Search,
  Delete,
  MarkEmailRead,
  Refresh,
  Add,
} from "@mui/icons-material";
import { motion, AnimatePresence } from "framer-motion";
import { useAuth } from "../../utils/AuthContext";

// Message type icons
const getMessageIcon = (type) => {
  const icons = {
    order: <LocalShipping />,
    promotion: <LocalOffer />,
    system: <Info />,
    alert: <ErrorIcon color="error" />,
    success: <CheckCircle color="success" />,
  };
  return icons[type] || <Notifications />;
};

// Message type colors
const getMessageColor = (type) => {
  const colors = {
    order: "primary",
    promotion: "secondary",
    system: "info",
    alert: "error",
    success: "success",
  };
  return colors[type] || "default";
};

const Messages = () => {
  const { isAuthenticated } = useAuth();
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTab, setSelectedTab] = useState(0);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedMessages, setSelectedMessages] = useState([]);
  const [composeOpen, setComposeOpen] = useState(false);

  // Helper function to format unread count message
  const getUnreadMessage = (count) => {
    if (count === 0) return "All caught up!";
    const plural = count === 1 ? "" : "s";
    return `You have ${count} unread message${plural}`;
  };

  // Sample messages - would come from API in production
  const sampleMessages = [
    {
      id: 1,
      type: "order",
      title: "Order #1234 Shipped",
      message:
        "Your order has been shipped and will arrive in 3-5 business days.",
      time: "2 hours ago",
      timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
      read: false,
      category: "orders",
    },
    {
      id: 2,
      type: "promotion",
      title: "Flash Sale - 30% Off Everything!",
      message: "Use code FLASH30 at checkout. Valid until midnight.",
      time: "5 hours ago",
      timestamp: new Date(Date.now() - 5 * 60 * 60 * 1000),
      read: false,
      category: "promotions",
    },
    {
      id: 3,
      type: "system",
      title: "Password Changed Successfully",
      message:
        "Your account password was changed. Contact support if this was not you.",
      time: "1 day ago",
      timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000),
      read: true,
      category: "account",
    },
    {
      id: 4,
      type: "success",
      title: "Order #1230 Delivered",
      message:
        "Your order has been successfully delivered. Enjoy your purchase!",
      time: "2 days ago",
      timestamp: new Date(Date.now() - 48 * 60 * 60 * 1000),
      read: true,
      category: "orders",
    },
  ];

  useEffect(() => {
    const loadMessages = async () => {
      setLoading(true);
      await new Promise((resolve) => setTimeout(resolve, 1000));
      setMessages(sampleMessages);
      setLoading(false);
    };
    loadMessages();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleTabChange = useCallback((event, newValue) => {
    setSelectedTab(newValue);
  }, []);

  const handleMarkAsRead = useCallback((messageId) => {
    setMessages((prev) =>
      prev.map((msg) => (msg.id === messageId ? { ...msg, read: true } : msg)),
    );
  }, []);

  const handleMarkAllAsRead = useCallback(() => {
    setMessages((prev) => prev.map((msg) => ({ ...msg, read: true })));
  }, []);

  const handleDeleteMessage = useCallback((messageId) => {
    setMessages((prev) => prev.filter((msg) => msg.id !== messageId));
    setSelectedMessages((prev) => prev.filter((id) => id !== messageId));
  }, []);

  const handleDeleteSelected = useCallback(() => {
    setMessages((prev) =>
      prev.filter((msg) => !selectedMessages.includes(msg.id)),
    );
    setSelectedMessages([]);
  }, [selectedMessages]);

  const handleRefresh = useCallback(async () => {
    setLoading(true);
    await new Promise((resolve) => setTimeout(resolve, 500));
    setLoading(false);
  }, []);

  const filteredMessages = messages.filter((msg) => {
    if (selectedTab === 1 && msg.read) return false;
    if (selectedTab === 2 && msg.category !== "orders") return false;
    if (selectedTab === 3 && msg.category !== "promotions") return false;

    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        msg.title.toLowerCase().includes(query) ||
        msg.message.toLowerCase().includes(query)
      );
    }

    return true;
  });

  const unreadCount = messages.filter((msg) => !msg.read).length;

  // Helper function to render message content - avoids nested ternary
  const renderMessageContent = () => {
    if (loading) {
      return (
        <List>
          {["msg-1", "msg-2", "msg-3"].map((key) => (
            <ListItem key={key} sx={{ py: 2 }}>
              <ListItemAvatar>
                <Skeleton variant="circular" width={40} height={40} />
              </ListItemAvatar>
              <ListItemText
                primary={<Skeleton width="60%" />}
                secondary={
                  <>
                    <Skeleton width="90%" />
                    <Skeleton width="30%" />
                  </>
                }
              />
            </ListItem>
          ))}
        </List>
      );
    }

    if (filteredMessages.length === 0) {
      return (
        <Box sx={{ py: 8, textAlign: "center" }}>
          <Notifications sx={{ fontSize: 64, color: "text.disabled", mb: 2 }} />
          <Typography variant="h6" color="text.secondary">
            No messages found
          </Typography>
        </Box>
      );
    }

    return (
      <List disablePadding>
        <AnimatePresence>
          {filteredMessages.map((message, index) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, x: -100 }}
              transition={{ delay: index * 0.05 }}
            >
              <ListItem
                sx={{
                  py: 2,
                  bgcolor: message.read ? "transparent" : "action.hover",
                  "&:hover": { bgcolor: "action.selected" },
                }}
                secondaryAction={
                  <Box sx={{ display: "flex", gap: 1 }}>
                    {!message.read && (
                      <IconButton
                        size="small"
                        onClick={() => handleMarkAsRead(message.id)}
                        aria-label="mark as read"
                      >
                        <MarkEmailRead fontSize="small" />
                      </IconButton>
                    )}
                    <IconButton
                      size="small"
                      color="error"
                      onClick={() => handleDeleteMessage(message.id)}
                      aria-label="delete"
                    >
                      <Delete fontSize="small" />
                    </IconButton>
                  </Box>
                }
              >
                <ListItemAvatar>
                  <Avatar
                    sx={{ bgcolor: `${getMessageColor(message.type)}.main` }}
                  >
                    {getMessageIcon(message.type)}
                  </Avatar>
                </ListItemAvatar>
                <ListItemText
                  primary={
                    <Box
                      sx={{
                        display: "flex",
                        alignItems: "center",
                        gap: 1,
                        mb: 0.5,
                      }}
                    >
                      <Typography
                        variant="subtitle1"
                        fontWeight={message.read ? "normal" : "bold"}
                        sx={{ flex: 1 }}
                      >
                        {message.title}
                      </Typography>
                      {!message.read && (
                        <Chip
                          label="New"
                          size="small"
                          color="primary"
                          sx={{ height: 20 }}
                        />
                      )}
                    </Box>
                  }
                  secondary={
                    <>
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{ mb: 0.5 }}
                      >
                        {message.message}
                      </Typography>
                      <Typography variant="caption" color="text.disabled">
                        {message.time}
                      </Typography>
                    </>
                  }
                />
              </ListItem>
              {index < filteredMessages.length - 1 && <Divider />}
            </motion.div>
          ))}
        </AnimatePresence>
      </List>
    );
  };

  if (!isAuthenticated) {
    return (
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Alert
          severity="info"
          action={
            <Button component={Link} to="/login" color="inherit" size="small">
              Login
            </Button>
          }
        >
          Please login to view your messages and notifications.
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box
        sx={{
          mb: 4,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: 2,
        }}
      >
        <Box>
          <Typography
            variant="h4"
            component="h1"
            fontWeight="bold"
            gutterBottom
          >
            Messages & Notifications
          </Typography>
          <Typography variant="body1" color="text.secondary">
            {getUnreadMessage(unreadCount)}
          </Typography>
        </Box>
        <Box sx={{ display: "flex", gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<MarkEmailRead />}
            onClick={handleMarkAllAsRead}
            disabled={unreadCount === 0}
          >
            Mark All Read
          </Button>
          <IconButton onClick={handleRefresh} aria-label="refresh messages">
            <Refresh />
          </IconButton>
        </Box>
      </Box>

      {/* Search */}
      <Card sx={{ mb: 3, borderRadius: 2 }}>
        <CardContent
          sx={{
            display: "flex",
            gap: 2,
            alignItems: "center",
            flexWrap: "wrap",
          }}
        >
          <TextField
            placeholder="Search messages..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            size="small"
            sx={{ flexGrow: 1, minWidth: 200 }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search />
                </InputAdornment>
              ),
            }}
          />
          {selectedMessages.length > 0 && (
            <Button
              variant="outlined"
              color="error"
              startIcon={<Delete />}
              onClick={handleDeleteSelected}
            >
              Delete ({selectedMessages.length})
            </Button>
          )}
        </CardContent>
      </Card>

      {/* Tabs */}
      <Paper sx={{ mb: 3, borderRadius: 2 }}>
        <Tabs
          value={selectedTab}
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
          aria-label="message categories"
        >
          <Tab
            label={
              <Badge badgeContent={messages.length} color="default" max={99}>
                All
              </Badge>
            }
          />
          <Tab
            label={
              <Badge badgeContent={unreadCount} color="primary" max={99}>
                Unread
              </Badge>
            }
          />
          <Tab
            label={
              <Badge
                badgeContent={
                  messages.filter((m) => m.category === "orders").length
                }
                color="info"
                max={99}
              >
                Orders
              </Badge>
            }
          />
          <Tab
            label={
              <Badge
                badgeContent={
                  messages.filter((m) => m.category === "promotions").length
                }
                color="secondary"
                max={99}
              >
                Promos
              </Badge>
            }
          />
        </Tabs>
      </Paper>

      {/* Messages List */}
      <Card sx={{ borderRadius: 2 }}>{renderMessageContent()}</Card>

      {/* Compose FAB */}
      <Fab
        color="primary"
        aria-label="compose"
        onClick={() => setComposeOpen(true)}
        sx={{ position: "fixed", bottom: 24, right: 24 }}
      >
        <Add />
      </Fab>

      {/* Compose Dialog */}
      <Dialog
        open={composeOpen}
        onClose={() => setComposeOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Contact Support</DialogTitle>
        <DialogContent>
          <TextField autoFocus label="Subject" fullWidth margin="normal" />
          <TextField
            label="Message"
            fullWidth
            multiline
            rows={4}
            margin="normal"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setComposeOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={() => setComposeOpen(false)}>
            Send
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Messages;
