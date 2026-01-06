import React, { useState, useCallback } from "react";
import { Link } from "react-router-dom";
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  TextField,
  Button,
  Switch,
  FormControlLabel,
  Divider,
  Alert,
  Snackbar,
  Avatar,
  IconButton,
  Tooltip,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  Paper,
  CircularProgress,
} from "@mui/material";
import {
  Person,
  Notifications,
  Security,
  Palette,
  Language,
  CameraAlt,
  Save,
  Visibility,
  VisibilityOff,
  Email,
  Phone,
  LocationOn,
  Delete,
  Warning,
} from "@mui/icons-material";
import PropTypes from "prop-types";
import { motion, AnimatePresence } from "framer-motion";
import { useAuth } from "../../utils/AuthContext";
import { useTheme } from "../../utils/ThemeContext";

const TabPanel = ({ children, value, index, ...other }) => (
  <div
    role="tabpanel"
    hidden={value !== index}
    id={`settings-tabpanel-${index}`}
    aria-labelledby={`settings-tab-${index}`}
    {...other}
  >
    {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
  </div>
);

TabPanel.propTypes = {
  children: PropTypes.node,
  value: PropTypes.number.isRequired,
  index: PropTypes.number.isRequired,
};

const Settings = () => {
  const { isAuthenticated, user } = useAuth();
  const { isDarkMode, toggleTheme } = useTheme();
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: "",
    severity: "success",
  });

  // Profile Settings State
  const [profile, setProfile] = useState({
    firstName: user?.first_name || "",
    lastName: user?.last_name || "",
    email: user?.email || "",
    phone: "",
    address: "",
    city: "",
    state: "",
    pincode: "",
  });

  // Notification Settings State
  const [notifications, setNotifications] = useState({
    emailNotifications: true,
    smsNotifications: false,
    pushNotifications: true,
    orderUpdates: true,
    promotions: true,
    newsletter: true,
    priceAlerts: false,
    stockAlerts: true,
  });

  // Security Settings State
  const [security, setSecurity] = useState({
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
  });
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false,
  });

  // Appearance Settings State
  const [appearance, setAppearance] = useState({
    language: "en",
    currency: "INR",
    dateFormat: "DD/MM/YYYY",
  });

  const handleTabChange = useCallback((event, newValue) => {
    setActiveTab(newValue);
  }, []);

  const handleProfileChange = useCallback(
    (field) => (event) => {
      setProfile((prev) => ({ ...prev, [field]: event.target.value }));
    },
    [],
  );

  const handleNotificationChange = useCallback(
    (field) => (event) => {
      setNotifications((prev) => ({ ...prev, [field]: event.target.checked }));
    },
    [],
  );

  const handleSecurityChange = useCallback(
    (field) => (event) => {
      setSecurity((prev) => ({ ...prev, [field]: event.target.value }));
    },
    [],
  );

  const handleAppearanceChange = useCallback(
    (field) => (event) => {
      setAppearance((prev) => ({ ...prev, [field]: event.target.value }));
    },
    [],
  );

  const handleSaveProfile = useCallback(async () => {
    setLoading(true);
    await new Promise((resolve) => setTimeout(resolve, 1000));
    setLoading(false);
    setSnackbar({
      open: true,
      message: "Profile updated successfully!",
      severity: "success",
    });
  }, []);

  const handleSaveNotifications = useCallback(async () => {
    setLoading(true);
    await new Promise((resolve) => setTimeout(resolve, 500));
    setLoading(false);
    setSnackbar({
      open: true,
      message: "Notification preferences saved!",
      severity: "success",
    });
  }, []);

  const handleChangePassword = useCallback(async () => {
    if (security.newPassword !== security.confirmPassword) {
      setSnackbar({
        open: true,
        message: "Passwords do not match!",
        severity: "error",
      });
      return;
    }
    if (security.newPassword.length < 8) {
      setSnackbar({
        open: true,
        message: "Password must be at least 8 characters!",
        severity: "error",
      });
      return;
    }
    setLoading(true);
    await new Promise((resolve) => setTimeout(resolve, 1000));
    setLoading(false);
    setSecurity({ currentPassword: "", newPassword: "", confirmPassword: "" });
    setSnackbar({
      open: true,
      message: "Password changed successfully!",
      severity: "success",
    });
  }, [security.newPassword, security.confirmPassword]);

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
          Please login to access your settings.
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Typography variant="h4" component="h1" fontWeight="bold" gutterBottom>
          Settings
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
          Manage your account settings and preferences
        </Typography>

        <Grid container spacing={4}>
          {/* Sidebar Tabs */}
          <Grid item xs={12} md={3}>
            <Paper sx={{ borderRadius: 2 }}>
              <Tabs
                orientation="vertical"
                value={activeTab}
                onChange={handleTabChange}
                aria-label="settings tabs"
                sx={{
                  "& .MuiTab-root": {
                    alignItems: "flex-start",
                    textAlign: "left",
                    py: 2,
                    minHeight: "auto",
                  },
                }}
              >
                <Tab icon={<Person />} iconPosition="start" label="Profile" />
                <Tab
                  icon={<Notifications />}
                  iconPosition="start"
                  label="Notifications"
                />
                <Tab
                  icon={<Security />}
                  iconPosition="start"
                  label="Security"
                />
                <Tab
                  icon={<Palette />}
                  iconPosition="start"
                  label="Appearance"
                />
              </Tabs>
            </Paper>
          </Grid>

          {/* Content */}
          <Grid item xs={12} md={9}>
            <AnimatePresence mode="wait">
              {/* Profile Tab */}
              <TabPanel value={activeTab} index={0}>
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                >
                  <Card sx={{ borderRadius: 2 }}>
                    <CardContent sx={{ p: 4 }}>
                      <Box
                        sx={{ display: "flex", alignItems: "center", mb: 4 }}
                      >
                        <Box sx={{ position: "relative" }}>
                          <Avatar
                            sx={{
                              width: 100,
                              height: 100,
                              fontSize: "2.5rem",
                              bgcolor: "primary.main",
                            }}
                          >
                            {user?.first_name?.charAt(0) ||
                              user?.username?.charAt(0) ||
                              "U"}
                          </Avatar>
                          <Tooltip title="Change Avatar">
                            <IconButton
                              sx={{
                                position: "absolute",
                                bottom: 0,
                                right: 0,
                                bgcolor: "background.paper",
                                boxShadow: 2,
                                "&:hover": { bgcolor: "grey.100" },
                              }}
                              size="small"
                            >
                              <CameraAlt fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </Box>
                        <Box sx={{ ml: 3 }}>
                          <Typography variant="h6">
                            {user?.username || "User"}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {user?.email || "user@example.com"}
                          </Typography>
                        </Box>
                      </Box>

                      <Divider sx={{ mb: 4 }} />

                      <Grid container spacing={3}>
                        <Grid item xs={12} sm={6}>
                          <TextField
                            fullWidth
                            label="First Name"
                            value={profile.firstName}
                            onChange={handleProfileChange("firstName")}
                          />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                          <TextField
                            fullWidth
                            label="Last Name"
                            value={profile.lastName}
                            onChange={handleProfileChange("lastName")}
                          />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                          <TextField
                            fullWidth
                            label="Email"
                            type="email"
                            value={profile.email}
                            onChange={handleProfileChange("email")}
                            InputProps={{
                              startAdornment: (
                                <Email sx={{ mr: 1, color: "action.active" }} />
                              ),
                            }}
                          />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                          <TextField
                            fullWidth
                            label="Phone"
                            value={profile.phone}
                            onChange={handleProfileChange("phone")}
                            InputProps={{
                              startAdornment: (
                                <Phone sx={{ mr: 1, color: "action.active" }} />
                              ),
                            }}
                          />
                        </Grid>
                        <Grid item xs={12}>
                          <TextField
                            fullWidth
                            label="Address"
                            value={profile.address}
                            onChange={handleProfileChange("address")}
                            InputProps={{
                              startAdornment: (
                                <LocationOn
                                  sx={{ mr: 1, color: "action.active" }}
                                />
                              ),
                            }}
                          />
                        </Grid>
                        <Grid item xs={12} sm={4}>
                          <TextField
                            fullWidth
                            label="City"
                            value={profile.city}
                            onChange={handleProfileChange("city")}
                          />
                        </Grid>
                        <Grid item xs={12} sm={4}>
                          <TextField
                            fullWidth
                            label="State"
                            value={profile.state}
                            onChange={handleProfileChange("state")}
                          />
                        </Grid>
                        <Grid item xs={12} sm={4}>
                          <TextField
                            fullWidth
                            label="PIN Code"
                            value={profile.pincode}
                            onChange={handleProfileChange("pincode")}
                          />
                        </Grid>
                      </Grid>

                      <Box
                        sx={{
                          mt: 4,
                          display: "flex",
                          justifyContent: "flex-end",
                        }}
                      >
                        <Button
                          variant="contained"
                          startIcon={
                            loading ? <CircularProgress size={20} /> : <Save />
                          }
                          onClick={handleSaveProfile}
                          disabled={loading}
                        >
                          Save Changes
                        </Button>
                      </Box>
                    </CardContent>
                  </Card>
                </motion.div>
              </TabPanel>

              {/* Notifications Tab */}
              <TabPanel value={activeTab} index={1}>
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                >
                  <Card sx={{ borderRadius: 2 }}>
                    <CardContent sx={{ p: 4 }}>
                      <Typography variant="h6" gutterBottom>
                        Notification Preferences
                      </Typography>
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{ mb: 3 }}
                      >
                        Choose how you want to receive notifications
                      </Typography>

                      <List>
                        <ListItem>
                          <ListItemIcon>
                            <Email />
                          </ListItemIcon>
                          <ListItemText
                            primary="Email Notifications"
                            secondary="Receive updates via email"
                          />
                          <ListItemSecondaryAction>
                            <Switch
                              checked={notifications.emailNotifications}
                              onChange={handleNotificationChange(
                                "emailNotifications",
                              )}
                            />
                          </ListItemSecondaryAction>
                        </ListItem>
                        <Divider />
                        <ListItem>
                          <ListItemIcon>
                            <Phone />
                          </ListItemIcon>
                          <ListItemText
                            primary="SMS Notifications"
                            secondary="Receive updates via SMS"
                          />
                          <ListItemSecondaryAction>
                            <Switch
                              checked={notifications.smsNotifications}
                              onChange={handleNotificationChange(
                                "smsNotifications",
                              )}
                            />
                          </ListItemSecondaryAction>
                        </ListItem>
                        <Divider />
                        <ListItem>
                          <ListItemIcon>
                            <Notifications />
                          </ListItemIcon>
                          <ListItemText
                            primary="Push Notifications"
                            secondary="Browser push notifications"
                          />
                          <ListItemSecondaryAction>
                            <Switch
                              checked={notifications.pushNotifications}
                              onChange={handleNotificationChange(
                                "pushNotifications",
                              )}
                            />
                          </ListItemSecondaryAction>
                        </ListItem>
                      </List>

                      <Divider sx={{ my: 3 }} />

                      <Typography
                        variant="subtitle1"
                        gutterBottom
                        fontWeight="bold"
                      >
                        Notification Types
                      </Typography>

                      <Grid container spacing={2}>
                        <Grid item xs={12} sm={6}>
                          <FormControlLabel
                            control={
                              <Switch
                                checked={notifications.orderUpdates}
                                onChange={handleNotificationChange(
                                  "orderUpdates",
                                )}
                              />
                            }
                            label="Order Updates"
                          />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                          <FormControlLabel
                            control={
                              <Switch
                                checked={notifications.promotions}
                                onChange={handleNotificationChange(
                                  "promotions",
                                )}
                              />
                            }
                            label="Promotions & Offers"
                          />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                          <FormControlLabel
                            control={
                              <Switch
                                checked={notifications.newsletter}
                                onChange={handleNotificationChange(
                                  "newsletter",
                                )}
                              />
                            }
                            label="Newsletter"
                          />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                          <FormControlLabel
                            control={
                              <Switch
                                checked={notifications.priceAlerts}
                                onChange={handleNotificationChange(
                                  "priceAlerts",
                                )}
                              />
                            }
                            label="Price Drop Alerts"
                          />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                          <FormControlLabel
                            control={
                              <Switch
                                checked={notifications.stockAlerts}
                                onChange={handleNotificationChange(
                                  "stockAlerts",
                                )}
                              />
                            }
                            label="Stock Alerts"
                          />
                        </Grid>
                      </Grid>

                      <Box
                        sx={{
                          mt: 4,
                          display: "flex",
                          justifyContent: "flex-end",
                        }}
                      >
                        <Button
                          variant="contained"
                          startIcon={
                            loading ? <CircularProgress size={20} /> : <Save />
                          }
                          onClick={handleSaveNotifications}
                          disabled={loading}
                        >
                          Save Preferences
                        </Button>
                      </Box>
                    </CardContent>
                  </Card>
                </motion.div>
              </TabPanel>

              {/* Security Tab */}
              <TabPanel value={activeTab} index={2}>
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                >
                  <Card sx={{ borderRadius: 2, mb: 3 }}>
                    <CardContent sx={{ p: 4 }}>
                      <Typography variant="h6" gutterBottom>
                        Change Password
                      </Typography>
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{ mb: 3 }}
                      >
                        Keep your account secure by using a strong password
                      </Typography>

                      <Grid container spacing={3}>
                        <Grid item xs={12}>
                          <TextField
                            fullWidth
                            label="Current Password"
                            type={showPasswords.current ? "text" : "password"}
                            value={security.currentPassword}
                            onChange={handleSecurityChange("currentPassword")}
                            InputProps={{
                              endAdornment: (
                                <IconButton
                                  onClick={() =>
                                    setShowPasswords((p) => ({
                                      ...p,
                                      current: !p.current,
                                    }))
                                  }
                                >
                                  {showPasswords.current ? (
                                    <VisibilityOff />
                                  ) : (
                                    <Visibility />
                                  )}
                                </IconButton>
                              ),
                            }}
                          />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                          <TextField
                            fullWidth
                            label="New Password"
                            type={showPasswords.new ? "text" : "password"}
                            value={security.newPassword}
                            onChange={handleSecurityChange("newPassword")}
                            InputProps={{
                              endAdornment: (
                                <IconButton
                                  onClick={() =>
                                    setShowPasswords((p) => ({
                                      ...p,
                                      new: !p.new,
                                    }))
                                  }
                                >
                                  {showPasswords.new ? (
                                    <VisibilityOff />
                                  ) : (
                                    <Visibility />
                                  )}
                                </IconButton>
                              ),
                            }}
                          />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                          <TextField
                            fullWidth
                            label="Confirm New Password"
                            type={showPasswords.confirm ? "text" : "password"}
                            value={security.confirmPassword}
                            onChange={handleSecurityChange("confirmPassword")}
                            InputProps={{
                              endAdornment: (
                                <IconButton
                                  onClick={() =>
                                    setShowPasswords((p) => ({
                                      ...p,
                                      confirm: !p.confirm,
                                    }))
                                  }
                                >
                                  {showPasswords.confirm ? (
                                    <VisibilityOff />
                                  ) : (
                                    <Visibility />
                                  )}
                                </IconButton>
                              ),
                            }}
                          />
                        </Grid>
                      </Grid>

                      <Box
                        sx={{
                          mt: 4,
                          display: "flex",
                          justifyContent: "flex-end",
                        }}
                      >
                        <Button
                          variant="contained"
                          startIcon={
                            loading ? (
                              <CircularProgress size={20} />
                            ) : (
                              <Security />
                            )
                          }
                          onClick={handleChangePassword}
                          disabled={
                            loading ||
                            !security.currentPassword ||
                            !security.newPassword
                          }
                        >
                          Update Password
                        </Button>
                      </Box>
                    </CardContent>
                  </Card>

                  <Card
                    sx={{
                      borderRadius: 2,
                      border: "1px solid",
                      borderColor: "error.light",
                    }}
                  >
                    <CardContent sx={{ p: 4 }}>
                      <Box
                        sx={{
                          display: "flex",
                          alignItems: "center",
                          gap: 2,
                          mb: 2,
                        }}
                      >
                        <Warning color="error" />
                        <Typography variant="h6" color="error">
                          Danger Zone
                        </Typography>
                      </Box>
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{ mb: 3 }}
                      >
                        Permanently delete your account and all associated data.
                      </Typography>
                      <Button
                        variant="outlined"
                        color="error"
                        startIcon={<Delete />}
                      >
                        Delete Account
                      </Button>
                    </CardContent>
                  </Card>
                </motion.div>
              </TabPanel>

              {/* Appearance Tab */}
              <TabPanel value={activeTab} index={3}>
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                >
                  <Card sx={{ borderRadius: 2 }}>
                    <CardContent sx={{ p: 4 }}>
                      <Typography variant="h6" gutterBottom>
                        Appearance & Preferences
                      </Typography>

                      <List>
                        <ListItem>
                          <ListItemIcon>
                            <Palette />
                          </ListItemIcon>
                          <ListItemText
                            primary="Dark Mode"
                            secondary="Switch between light and dark themes"
                          />
                          <ListItemSecondaryAction>
                            <Switch
                              checked={isDarkMode}
                              onChange={toggleTheme}
                            />
                          </ListItemSecondaryAction>
                        </ListItem>
                        <Divider />
                      </List>

                      <Grid container spacing={3} sx={{ mt: 1 }}>
                        <Grid item xs={12} sm={6}>
                          <FormControl fullWidth>
                            <InputLabel>Language</InputLabel>
                            <Select
                              value={appearance.language}
                              label="Language"
                              onChange={handleAppearanceChange("language")}
                              startAdornment={<Language sx={{ mr: 1 }} />}
                            >
                              <MenuItem value="en">English</MenuItem>
                              <MenuItem value="hi">Hindi</MenuItem>
                              <MenuItem value="ta">Tamil</MenuItem>
                              <MenuItem value="te">Telugu</MenuItem>
                            </Select>
                          </FormControl>
                        </Grid>
                        <Grid item xs={12} sm={6}>
                          <FormControl fullWidth>
                            <InputLabel>Currency</InputLabel>
                            <Select
                              value={appearance.currency}
                              label="Currency"
                              onChange={handleAppearanceChange("currency")}
                            >
                              <MenuItem value="INR">Indian Rupee (₹)</MenuItem>
                              <MenuItem value="USD">US Dollar ($)</MenuItem>
                              <MenuItem value="EUR">Euro (€)</MenuItem>
                            </Select>
                          </FormControl>
                        </Grid>
                        <Grid item xs={12} sm={6}>
                          <FormControl fullWidth>
                            <InputLabel>Date Format</InputLabel>
                            <Select
                              value={appearance.dateFormat}
                              label="Date Format"
                              onChange={handleAppearanceChange("dateFormat")}
                            >
                              <MenuItem value="DD/MM/YYYY">DD/MM/YYYY</MenuItem>
                              <MenuItem value="MM/DD/YYYY">MM/DD/YYYY</MenuItem>
                              <MenuItem value="YYYY-MM-DD">YYYY-MM-DD</MenuItem>
                            </Select>
                          </FormControl>
                        </Grid>
                      </Grid>
                    </CardContent>
                  </Card>
                </motion.div>
              </TabPanel>
            </AnimatePresence>
          </Grid>
        </Grid>
      </motion.div>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          sx={{ width: "100%" }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default Settings;
