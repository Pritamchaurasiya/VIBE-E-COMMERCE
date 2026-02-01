import React, { useState, useCallback, useRef, useEffect } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  IconButton,
  Badge,
  Menu,
  MenuItem,
  InputBase,
  Box,
  Container,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Divider,
  Avatar,
  Tooltip,
  Popover,
  Chip,
  useMediaQuery,
  useTheme as useMuiTheme,
} from "@mui/material";
import {
  ShoppingCart,
  Favorite,
  Search as SearchIcon,
  Brightness4,
  Brightness7,
  Menu as MenuIcon,
  Home,
  Store,
  Category,
  Close,
  Notifications,
  Message,
  Settings,
  ExitToApp,
  AccountCircle,
  Receipt,
  Compare,
  ContactSupport,
  Info,
} from "@mui/icons-material";
import { motion, AnimatePresence } from "framer-motion";
import { useAuth } from "../../utils/AuthContext";
import { useCart } from "../../utils/CartContext";
import { useDispatch, useSelector } from "react-redux";
import { toggleTheme, selectIsDarkMode } from "../../features/theme/themeSlice";

const Header = () => {
  const { logout, isAuthenticated, user } = useAuth();
  const { cart } = useCart();
  const dispatch = useDispatch();
  const isDarkMode = useSelector(selectIsDarkMode);
  const navigate = useNavigate();
  const location = useLocation();
  const muiTheme = useMuiTheme();
  useMediaQuery(muiTheme.breakpoints.down("md"));

  const searchInputRef = useRef(null);

  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === "/" && !event.repeat) {
        const activeElement = document.activeElement;
        const isInputActive =
          activeElement.tagName === "INPUT" ||
          activeElement.tagName === "TEXTAREA" ||
          activeElement.isContentEditable;

        if (!isInputActive) {
          event.preventDefault();
          searchInputRef.current?.focus();
        }
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const handleToggleTheme = () => {
    dispatch(toggleTheme());
  };

  const [searchQuery, setSearchQuery] = useState("");
  const [anchorEl, setAnchorEl] = useState(null);
  const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false);
  const [notificationsAnchor, setNotificationsAnchor] = useState(null);

  // Sample notifications - would come from API in production
  const notifications = [
    {
      id: 1,
      title: "Order Shipped",
      message: "Your order #1234 has been shipped",
      time: "2 hours ago",
      read: false,
    },
    {
      id: 2,
      title: "New Offer",
      message: "Get 20% off on all products",
      time: "1 day ago",
      read: true,
    },
    {
      id: 3,
      title: "Wishlist Alert",
      message: "Item in your wishlist is on sale",
      time: "2 days ago",
      read: true,
    },
  ];

  const unreadCount = notifications.filter((n) => !n.read).length;

  const handleProfileMenuOpen = useCallback((event) => {
    setAnchorEl(event.currentTarget);
  }, []);

  const handleProfileMenuClose = useCallback(() => {
    setAnchorEl(null);
  }, []);

  const handleLogout = useCallback(async () => {
    await logout();
    handleProfileMenuClose();
    navigate("/");
  }, [logout, navigate, handleProfileMenuClose]);

  const handleSearch = useCallback(
    (e) => {
      e.preventDefault();
      if (searchQuery.trim()) {
        navigate(`/products?q=${encodeURIComponent(searchQuery)}`);
        setMobileDrawerOpen(false);
      }
    },
    [searchQuery, navigate],
  );

  const toggleMobileDrawer = useCallback(() => {
    setMobileDrawerOpen((prev) => !prev);
  }, []);

  const handleNotificationsOpen = useCallback((event) => {
    setNotificationsAnchor(event.currentTarget);
  }, []);

  const handleNotificationsClose = useCallback(() => {
    setNotificationsAnchor(null);
  }, []);

  const isActiveRoute = useCallback(
    (path) => {
      return (
        location.pathname === path || location.pathname.startsWith(path + "/")
      );
    },
    [location.pathname],
  );

  const navigationItems = [
    { label: "Home", path: "/", icon: <Home /> },
    { label: "Products", path: "/products", icon: <Store /> },
    { label: "Vendors", path: "/vendors", icon: <Category /> },
    { label: "Compare", path: "/compare", icon: <Compare /> },
    { label: "About", path: "/about", icon: <Info /> },
    { label: "Contact", path: "/contact", icon: <ContactSupport /> },
  ];

  const userMenuItems = [
    { label: "Profile", path: "/profile", icon: <AccountCircle /> },
    { label: "Orders", path: "/orders", icon: <Receipt /> },
    { label: "Wishlist", path: "/wishlist", icon: <Favorite /> },
    { label: "Messages", path: "/messages", icon: <Message /> },
    { label: "Settings", path: "/settings", icon: <Settings /> },
  ];

  return (
    <>
      <AppBar
        position="sticky"
        color="primary"
        sx={{
          backdropFilter: "blur(10px)",
          boxShadow: isDarkMode
            ? "0 2px 20px rgba(0,0,0,0.3)"
            : "0 2px 20px rgba(0,0,0,0.1)",
        }}
      >
        <Container maxWidth="xl">
          <Toolbar
            sx={{
              minHeight: { xs: 56, sm: 64 },
              gap: 1,
            }}
          >
            {/* Mobile Menu Button */}
            <IconButton
              color="inherit"
              aria-label="open navigation menu"
              onClick={toggleMobileDrawer}
              sx={{ display: { xs: "flex", md: "none" }, mr: 1 }}
            >
              <MenuIcon />
            </IconButton>

            {/* Logo */}
            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              <Typography
                variant="h6"
                component={Link}
                to="/"
                aria-label="Go to homepage"
                sx={{
                  textDecoration: "none",
                  color: "white",
                  fontWeight: "bold",
                  flexGrow: { xs: 1, md: 0 },
                  mr: { xs: 0, md: 3 },
                  fontSize: { xs: "1rem", sm: "1.25rem" },
                  display: "flex",
                  alignItems: "center",
                  gap: 1,
                }}
              >
                <Box
                  component="span"
                  sx={{
                    background:
                      "linear-gradient(135deg, #ffffff 0%, #e0f2f1 100%)",
                    color: "#22c55e",
                    px: 1,
                    py: 0.5,
                    borderRadius: 1,
                    fontWeight: 800,
                  }}
                >
                  VIBE
                </Box>
                <Box
                  component="span"
                  sx={{ display: { xs: "none", sm: "inline" } }}
                >
                  E-Commerce
                </Box>
              </Typography>
            </motion.div>

            {/* Desktop Navigation Links */}
            <Box
              sx={{ flexGrow: 1, display: { xs: "none", md: "flex" }, gap: 1 }}
            >
              {navigationItems.slice(0, 4).map((item) => (
                <Button
                  key={item.path}
                  color="inherit"
                  component={Link}
                  to={item.path}
                  aria-label={`Navigate to ${item.label}`}
                  sx={{
                    position: "relative",
                    "&::after": isActiveRoute(item.path)
                      ? {
                          content: '""',
                          position: "absolute",
                          bottom: 0,
                          left: "50%",
                          transform: "translateX(-50%)",
                          width: "60%",
                          height: 3,
                          backgroundColor: "white",
                          borderRadius: 2,
                        }
                      : {},
                    fontWeight: isActiveRoute(item.path) ? 700 : 500,
                  }}
                >
                  {item.label}
                </Button>
              ))}
            </Box>

            {/* Search Bar */}
            <Box
              component="form"
              onSubmit={handleSearch}
              sx={{
                display: { xs: "none", sm: "flex" },
                alignItems: "center",
                backgroundColor: "rgba(255, 255, 255, 0.15)",
                borderRadius: 2,
                px: 1.5,
                py: 0.5,
                mr: 2,
                minWidth: { sm: 180, md: 280 },
                transition: "all 0.3s ease",
                "&:hover, &:focus-within": {
                  backgroundColor: "rgba(255, 255, 255, 0.25)",
                  boxShadow: "0 0 0 2px rgba(255,255,255,0.2)",
                },
              }}
            >
              <SearchIcon sx={{ color: "white", mr: 1 }} fontSize="small" />
              <InputBase
                inputRef={searchInputRef}
                placeholder="Search products... (/)"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                inputProps={{
                  "aria-label": "search products",
                  role: "searchbox",
                }}
                sx={{
                  color: "white",
                  flex: 1,
                  "& input::placeholder": { color: "rgba(255,255,255,0.7)" },
                }}
              />
            </Box>

            {/* Theme Toggle */}
            <Tooltip
              title={
                isDarkMode ? "Switch to Light Mode" : "Switch to Dark Mode"
              }
            >
              <IconButton
                color="inherit"
                onClick={handleToggleTheme}
                aria-label={
                  isDarkMode ? "Switch to light mode" : "Switch to dark mode"
                }
              >
                <motion.div
                  initial={false}
                  animate={{ rotate: isDarkMode ? 180 : 0 }}
                  transition={{ duration: 0.3 }}
                >
                  {isDarkMode ? <Brightness7 /> : <Brightness4 />}
                </motion.div>
              </IconButton>
            </Tooltip>

            {/* Notifications */}
            {isAuthenticated && (
              <Tooltip title="Notifications">
                <IconButton
                  color="inherit"
                  onClick={handleNotificationsOpen}
                  aria-label={`${unreadCount} unread notifications`}
                >
                  <Badge badgeContent={unreadCount} color="error">
                    <Notifications />
                  </Badge>
                </IconButton>
              </Tooltip>
            )}

            {/* Cart */}
            <Tooltip title="Shopping Cart">
              <IconButton
                color="inherit"
                component={Link}
                to="/cart"
                aria-label={`Shopping cart with ${cart.item_count} items`}
              >
                <Badge badgeContent={cart.item_count} color="secondary">
                  <ShoppingCart />
                </Badge>
              </IconButton>
            </Tooltip>

            {/* Wishlist - Desktop only */}
            {isAuthenticated && (
              <Tooltip title="Wishlist">
                <IconButton
                  color="inherit"
                  component={Link}
                  to="/wishlist"
                  aria-label="View wishlist"
                  sx={{ display: { xs: "none", sm: "flex" } }}
                >
                  <Favorite />
                </IconButton>
              </Tooltip>
            )}

            {/* User Menu */}
            {isAuthenticated ? (
              <>
                <Tooltip title="Account">
                  <IconButton
                    color="inherit"
                    onClick={handleProfileMenuOpen}
                    aria-label="Open user menu"
                    aria-controls="user-menu"
                    aria-haspopup="true"
                  >
                    <Avatar
                      sx={{
                        width: 32,
                        height: 32,
                        bgcolor: "secondary.main",
                        fontSize: "0.875rem",
                      }}
                    >
                      {user?.first_name?.charAt(0) ||
                        user?.username?.charAt(0) ||
                        "U"}
                    </Avatar>
                  </IconButton>
                </Tooltip>
                <Menu
                  id="user-menu"
                  anchorEl={anchorEl}
                  open={Boolean(anchorEl)}
                  onClose={handleProfileMenuClose}
                  transformOrigin={{ horizontal: "right", vertical: "top" }}
                  anchorOrigin={{ horizontal: "right", vertical: "bottom" }}
                  slotProps={{
                    paper: {
                      sx: {
                        minWidth: 200,
                        mt: 1,
                        borderRadius: 2,
                      },
                    },
                  }}
                >
                  <Box sx={{ px: 2, py: 1.5 }}>
                    <Typography variant="subtitle2" fontWeight="bold">
                      {user?.first_name || user?.username || "User"}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {user?.email || ""}
                    </Typography>
                  </Box>
                  <Divider />
                  {userMenuItems.map((item) => (
                    <MenuItem
                      key={item.path}
                      component={Link}
                      to={item.path}
                      onClick={handleProfileMenuClose}
                    >
                      <ListItemIcon>{item.icon}</ListItemIcon>
                      <ListItemText>{item.label}</ListItemText>
                    </MenuItem>
                  ))}
                  <Divider />
                  <MenuItem onClick={handleLogout}>
                    <ListItemIcon>
                      <ExitToApp />
                    </ListItemIcon>
                    <ListItemText>Logout</ListItemText>
                  </MenuItem>
                </Menu>
              </>
            ) : (
              <Box sx={{ display: { xs: "none", sm: "flex" }, gap: 1 }}>
                <Button
                  color="inherit"
                  component={Link}
                  to="/login"
                  variant="outlined"
                  sx={{
                    borderColor: "rgba(255,255,255,0.5)",
                    "&:hover": {
                      borderColor: "white",
                      bgcolor: "rgba(255,255,255,0.1)",
                    },
                  }}
                >
                  Login
                </Button>
                <Button
                  component={Link}
                  to="/register"
                  variant="contained"
                  sx={{
                    bgcolor: "white",
                    color: "primary.main",
                    "&:hover": { bgcolor: "rgba(255,255,255,0.9)" },
                  }}
                >
                  Register
                </Button>
              </Box>
            )}
          </Toolbar>
        </Container>
      </AppBar>

      {/* Mobile Navigation Drawer */}
      <Drawer
        anchor="left"
        open={mobileDrawerOpen}
        onClose={toggleMobileDrawer}
        slotProps={{
          paper: {
            sx: { width: 280, borderRadius: "0 16px 16px 0" },
          },
        }}
      >
        <Box
          sx={{
            p: 2,
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <Typography variant="h6" fontWeight="bold" color="primary">
            VIBE Menu
          </Typography>
          <IconButton onClick={toggleMobileDrawer} aria-label="close menu">
            <Close />
          </IconButton>
        </Box>
        <Divider />

        {/* Mobile Search */}
        <Box sx={{ p: 2 }}>
          <Box
            component="form"
            onSubmit={handleSearch}
            sx={{
              display: "flex",
              alignItems: "center",
              bgcolor: "action.hover",
              borderRadius: 2,
              px: 2,
              py: 1,
            }}
          >
            <InputBase
              placeholder="Search..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              sx={{ flex: 1 }}
              inputProps={{ "aria-label": "search" }}
            />
            <IconButton type="submit" size="small" aria-label="submit search">
              <SearchIcon />
            </IconButton>
          </Box>
        </Box>

        <List>
          {navigationItems.map((item) => (
            <ListItem key={item.path} disablePadding>
              <ListItemButton
                component={Link}
                to={item.path}
                onClick={toggleMobileDrawer}
                selected={isActiveRoute(item.path)}
                sx={{
                  "&.Mui-selected": {
                    bgcolor: "primary.main",
                    color: "white",
                    "& .MuiListItemIcon-root": { color: "white" },
                    "&:hover": { bgcolor: "primary.dark" },
                  },
                }}
              >
                <ListItemIcon>{item.icon}</ListItemIcon>
                <ListItemText primary={item.label} />
              </ListItemButton>
            </ListItem>
          ))}
        </List>

        <Divider sx={{ my: 1 }} />

        {isAuthenticated ? (
          <List>
            {userMenuItems.map((item) => (
              <ListItem key={item.path} disablePadding>
                <ListItemButton
                  component={Link}
                  to={item.path}
                  onClick={toggleMobileDrawer}
                >
                  <ListItemIcon>{item.icon}</ListItemIcon>
                  <ListItemText primary={item.label} />
                </ListItemButton>
              </ListItem>
            ))}
            <ListItem disablePadding>
              <ListItemButton
                onClick={() => {
                  handleLogout();
                  toggleMobileDrawer();
                }}
              >
                <ListItemIcon>
                  <ExitToApp />
                </ListItemIcon>
                <ListItemText primary="Logout" />
              </ListItemButton>
            </ListItem>
          </List>
        ) : (
          <Box sx={{ p: 2, display: "flex", flexDirection: "column", gap: 1 }}>
            <Button
              variant="contained"
              component={Link}
              to="/login"
              onClick={toggleMobileDrawer}
              fullWidth
            >
              Login
            </Button>
            <Button
              variant="outlined"
              component={Link}
              to="/register"
              onClick={toggleMobileDrawer}
              fullWidth
            >
              Register
            </Button>
          </Box>
        )}
      </Drawer>

      {/* Notifications Popover */}
      <Popover
        open={Boolean(notificationsAnchor)}
        anchorEl={notificationsAnchor}
        onClose={handleNotificationsClose}
        anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
        transformOrigin={{ vertical: "top", horizontal: "right" }}
        slotProps={{
          paper: {
            sx: { width: 320, maxHeight: 400, borderRadius: 2, mt: 1 },
          },
        }}
      >
        <Box sx={{ p: 2, borderBottom: 1, borderColor: "divider" }}>
          <Typography variant="h6" fontWeight="bold">
            Notifications
          </Typography>
        </Box>
        <List sx={{ maxHeight: 300, overflow: "auto" }}>
          <AnimatePresence>
            {notifications.map((notification, index) => (
              <motion.div
                key={notification.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <ListItem
                  sx={{
                    bgcolor: notification.read ? "transparent" : "action.hover",
                    "&:hover": { bgcolor: "action.selected" },
                  }}
                >
                  <ListItemText
                    primary={
                      <Box
                        sx={{ display: "flex", alignItems: "center", gap: 1 }}
                      >
                        <Typography variant="subtitle2" fontWeight="bold">
                          {notification.title}
                        </Typography>
                        {!notification.read && (
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
                        <Typography variant="body2" color="text.secondary">
                          {notification.message}
                        </Typography>
                        <Typography variant="caption" color="text.disabled">
                          {notification.time}
                        </Typography>
                      </>
                    }
                  />
                </ListItem>
                <Divider />
              </motion.div>
            ))}
          </AnimatePresence>
        </List>
        <Box sx={{ p: 1.5, borderTop: 1, borderColor: "divider" }}>
          <Button
            fullWidth
            component={Link}
            to="/messages"
            onClick={handleNotificationsClose}
          >
            View All Notifications
          </Button>
        </Box>
      </Popover>
    </>
  );
};

export default Header;
