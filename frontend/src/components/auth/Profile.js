import React, { useState, useEffect, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import {
  Container,
  Typography,
  TextField,
  Button,
  Box,
  Alert,
  Grid,
  CircularProgress,
  Skeleton,
  Paper,
  Avatar,
  Divider,
  InputAdornment,
} from "@mui/material";
import {
  Person,
  Email,
  Store,
  Receipt,
  Home,
  LocationCity,
  Public,
  PinDrop,
  Save,
  CameraAlt,
} from "@mui/icons-material";
import { useAuth } from "../../utils/AuthContext";
import { motion } from "framer-motion";

const MotionPaper = motion(Paper);

const Profile = () => {
  const { user, updateProfile, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    email: "",
    shop_name: "",
    gst_number: "",
    address: "",
    city: "",
    state: "",
    pincode: "",
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [initialLoading, setInitialLoading] = useState(true);

  // Redirect if not authenticated
  useEffect(() => {
    if (isAuthenticated) {
      setInitialLoading(false);
    } else {
      navigate("/login", { state: { from: "/profile" } });
    }
  }, [isAuthenticated, navigate]);

  // Populate form data when user is loaded
  useEffect(() => {
    if (user) {
      setFormData({
        first_name: user.first_name || "",
        last_name: user.last_name || "",
        email: user.email || "",
        shop_name: user.profile?.shop_name || "",
        gst_number: user.profile?.gst_number || "",
        address: user.profile?.address || "",
        city: user.profile?.city || "",
        state: user.profile?.state || "",
        pincode: user.profile?.pincode || "",
      });
    }
  }, [user]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage("");

    const result = await updateProfile({
      first_name: formData.first_name,
      last_name: formData.last_name,
      email: formData.email,
      profile: {
        shop_name: formData.shop_name,
        gst_number: formData.gst_number,
        address: formData.address,
        city: formData.city,
        state: formData.state,
        pincode: formData.pincode,
      },
    });

    if (result.success) {
      setMessage("Profile updated successfully!");
    } else {
      setMessage(result.error);
    }

    setLoading(false);
  };

  // Memoize alert severity to avoid recalculation
  const alertSeverity = useMemo(() => {
    return message.includes("success") ? "success" : "error";
  }, [message]);

  // Show loading skeleton while checking authentication
  if (initialLoading || !isAuthenticated) {
    return (
      <Container maxWidth="md" sx={{ py: 6 }}>
        <Skeleton variant="text" width={300} height={60} sx={{ mb: 4 }} />
        <Grid container spacing={4}>
          <Grid item xs={12} md={4}>
            <Skeleton
              variant="rectangular"
              height={300}
              sx={{ borderRadius: 4 }}
            />
          </Grid>
          <Grid item xs={12} md={8}>
            <Skeleton
              variant="rectangular"
              height={500}
              sx={{ borderRadius: 4 }}
            />
          </Grid>
        </Grid>
      </Container>
    );
  }

  return (
    <Box
      sx={{
        minHeight: "100vh",
        py: 6,
        background: "linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%)",
      }}
    >
      <Container maxWidth="lg">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Typography
            variant="h4"
            component="h1"
            gutterBottom
            fontWeight="800"
            sx={{ color: "#1e293b" }}
          >
            My Account
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
            Manage your personal information and address
          </Typography>
        </motion.div>

        <Grid container spacing={4}>
          {/* Sidebar / Profile Summary */}
          <Grid item xs={12} md={4}>
            <MotionPaper
              elevation={0}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              sx={{
                p: 4,
                borderRadius: 4,
                textAlign: "center",
                border: "1px solid",
                borderColor: "divider",
                background: "#fff",
                boxShadow:
                  "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
              }}
            >
              <Box
                sx={{ position: "relative", display: "inline-block", mb: 2 }}
              >
                <Avatar
                  sx={{
                    width: 120,
                    height: 120,
                    fontSize: "3rem",
                    margin: "0 auto",
                    background:
                      "linear-gradient(135deg, #22c55e 0%, #16a34a 100%)",
                    boxShadow: "0 10px 15px -3px rgba(34, 197, 94, 0.5)",
                  }}
                >
                  {formData.first_name ? (
                    formData.first_name.charAt(0)
                  ) : (
                    <Person sx={{ fontSize: 60 }} />
                  )}
                </Avatar>
                <Box
                  sx={{
                    position: "absolute",
                    bottom: 0,
                    right: 0,
                    bgcolor: "background.paper",
                    borderRadius: "50%",
                    p: 0.5,
                    boxShadow: 1,
                    cursor: "pointer",
                  }}
                >
                  <CameraAlt color="action" fontSize="small" />
                </Box>
              </Box>

              <Typography variant="h5" fontWeight="700" gutterBottom>
                {formData.first_name} {formData.last_name}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                {formData.email}
              </Typography>
              {formData.shop_name && (
                <Box
                  sx={{
                    display: "inline-flex",
                    alignItems: "center",
                    bgcolor: "primary.light",
                    color: "primary.contrastText",
                    px: 1.5,
                    py: 0.5,
                    borderRadius: 2,
                    mt: 1,
                  }}
                >
                  <Store fontSize="small" sx={{ mr: 0.5 }} />
                  <Typography variant="caption" fontWeight="600">
                    {formData.shop_name}
                  </Typography>
                </Box>
              )}
            </MotionPaper>
          </Grid>

          {/* Main Settings Form */}
          <Grid item xs={12} md={8}>
            <MotionPaper
              elevation={0}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              sx={{
                p: { xs: 3, md: 4 },
                borderRadius: 4,
                border: "1px solid",
                borderColor: "divider",
                background: "#fff",
                boxShadow:
                  "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
              }}
            >
              {message && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                >
                  <Alert
                    severity={alertSeverity}
                    sx={{ mb: 3, borderRadius: 2 }}
                  >
                    {message}
                  </Alert>
                </motion.div>
              )}

              <Box component="form" onSubmit={handleSubmit}>
                <Box sx={{ mb: 4 }}>
                  <Typography
                    variant="h6"
                    gutterBottom
                    fontWeight="700"
                    color="primary"
                    sx={{ display: "flex", alignItems: "center" }}
                  >
                    <Person sx={{ mr: 1 }} /> Personal Information
                  </Typography>
                  <Divider sx={{ mb: 3 }} />
                  <Grid container spacing={3}>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="First Name"
                        name="first_name"
                        value={formData.first_name}
                        onChange={handleChange}
                        InputProps={{
                          startAdornment: (
                            <InputAdornment position="start">
                              <Person color="action" />
                            </InputAdornment>
                          ),
                        }}
                      />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Last Name"
                        name="last_name"
                        value={formData.last_name}
                        onChange={handleChange}
                        InputProps={{
                          startAdornment: (
                            <InputAdornment position="start">
                              <Person color="action" />
                            </InputAdornment>
                          ),
                        }}
                      />
                    </Grid>
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="Email Address"
                        name="email"
                        type="email"
                        value={formData.email}
                        onChange={handleChange}
                        InputProps={{
                          startAdornment: (
                            <InputAdornment position="start">
                              <Email color="action" />
                            </InputAdornment>
                          ),
                        }}
                      />
                    </Grid>
                  </Grid>
                </Box>

                <Box sx={{ mb: 4 }}>
                  <Typography
                    variant="h6"
                    gutterBottom
                    fontWeight="700"
                    color="primary"
                    sx={{ display: "flex", alignItems: "center" }}
                  >
                    <Store sx={{ mr: 1 }} /> Business & Address
                  </Typography>
                  <Divider sx={{ mb: 3 }} />
                  <Grid container spacing={3}>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Shop/Business Name"
                        name="shop_name"
                        value={formData.shop_name}
                        onChange={handleChange}
                        InputProps={{
                          startAdornment: (
                            <InputAdornment position="start">
                              <Store color="action" />
                            </InputAdornment>
                          ),
                        }}
                      />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="GST Number"
                        name="gst_number"
                        value={formData.gst_number}
                        onChange={handleChange}
                        InputProps={{
                          startAdornment: (
                            <InputAdornment position="start">
                              <Receipt color="action" />
                            </InputAdornment>
                          ),
                        }}
                      />
                    </Grid>
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="Street Address"
                        name="address"
                        multiline
                        rows={2}
                        value={formData.address}
                        onChange={handleChange}
                        InputProps={{
                          startAdornment: (
                            <InputAdornment position="start">
                              <Home color="action" />
                            </InputAdornment>
                          ),
                        }}
                      />
                    </Grid>
                    <Grid item xs={12} sm={4}>
                      <TextField
                        fullWidth
                        label="City"
                        name="city"
                        value={formData.city}
                        onChange={handleChange}
                        InputProps={{
                          startAdornment: (
                            <InputAdornment position="start">
                              <LocationCity color="action" />
                            </InputAdornment>
                          ),
                        }}
                      />
                    </Grid>
                    <Grid item xs={12} sm={4}>
                      <TextField
                        fullWidth
                        label="State"
                        name="state"
                        value={formData.state}
                        onChange={handleChange}
                        InputProps={{
                          startAdornment: (
                            <InputAdornment position="start">
                              <Public color="action" />
                            </InputAdornment>
                          ),
                        }}
                      />
                    </Grid>
                    <Grid item xs={12} sm={4}>
                      <TextField
                        fullWidth
                        label="PIN Code"
                        name="pincode"
                        value={formData.pincode}
                        onChange={handleChange}
                        InputProps={{
                          startAdornment: (
                            <InputAdornment position="start">
                              <PinDrop color="action" />
                            </InputAdornment>
                          ),
                        }}
                      />
                    </Grid>
                  </Grid>
                </Box>

                <Box
                  sx={{ display: "flex", justifyContent: "flex-end", mt: 4 }}
                >
                  <Button
                    type="submit"
                    variant="contained"
                    size="large"
                    disabled={loading}
                    startIcon={
                      loading ? (
                        <CircularProgress size={20} color="inherit" />
                      ) : (
                        <Save />
                      )
                    }
                    sx={{
                      px: 4,
                      py: 1.5,
                      borderRadius: 2,
                      fontWeight: 700,
                      boxShadow: "0 4px 6px -1px rgba(34, 197, 94, 0.4)",
                      background:
                        "linear-gradient(135deg, #22c55e 0%, #16a34a 100%)",
                      "&:hover": {
                        background:
                          "linear-gradient(135deg, #16a34a 0%, #15803d 100%)",
                        boxShadow: "0 10px 15px -3px rgba(34, 197, 94, 0.5)",
                      },
                    }}
                  >
                    {loading ? "Saving Changes..." : "Save Changes"}
                  </Button>
                </Box>
              </Box>
            </MotionPaper>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default Profile;
