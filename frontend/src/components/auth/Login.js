import React, { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import {
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Box,
  Alert,
  Link as MuiLink,
  Divider,
  IconButton,
  InputAdornment,
  FormControlLabel,
  Checkbox,
  CircularProgress,
  Grid,
} from "@mui/material";
import {
  Visibility,
  VisibilityOff,
  Google,
  Facebook,
  Lock,
  Person,
  Agriculture,
} from "@mui/icons-material";
import { useAuth } from "../../utils/AuthContext";
import { motion } from "framer-motion";

const Login = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [formData, setFormData] = useState({
    username: "",
    password: "",
  });
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [loading, setLoading] = useState(false);
  const [socialLoading, setSocialLoading] = useState(null);
  const [error, setError] = useState("");
  const [formErrors, setFormErrors] = useState({});

  // Sanitize redirect path to prevent open redirect vulnerability
  const getSafeRedirectPath = (path) => {
    if (
      path &&
      typeof path === "string" &&
      path.startsWith("/") &&
      !path.startsWith("//")
    ) {
      if (!path.includes("://")) {
        return path;
      }
    }
    return "/";
  };

  const from = getSafeRedirectPath(location.state?.from?.pathname);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
    if (formErrors[name]) {
      setFormErrors({ ...formErrors, [name]: "" });
    }
  };

  const validateForm = () => {
    const errors = {};
    if (!formData.username.trim()) {
      errors.username = "Username is required";
    }
    if (!formData.password.trim()) {
      errors.password = "Password is required";
    } else if (formData.password.length < 6) {
      errors.password = "Password must be at least 6 characters";
    }
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    if (!validateForm()) return;
    setLoading(true);
    const result = await login(formData);
    if (result.success) {
      navigate(from, { replace: true });
    } else {
      setError(result.error);
    }
    setLoading(false);
  };

  const handleSocialLogin = async (provider) => {
    setSocialLoading(provider);
    setError("");
    try {
      await new Promise((resolve) => setTimeout(resolve, 2000));
      alert(`${provider} login successful!`);
      navigate(from, { replace: true });
    } catch (err) {
      console.error(`${provider} login error:`, err);
      setError(`${provider} login failed. Please try again.`);
    } finally {
      setSocialLoading(null);
    }
  };

  const handleTogglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  return (
    <Box
      sx={{
        minHeight: "80vh",
        display: "flex",
        alignItems: "center",
        py: 4,
        background:
          "linear-gradient(135deg, rgba(34, 197, 94, 0.03) 0%, rgba(16, 185, 129, 0.05) 100%)",
      }}
    >
      <Container maxWidth="sm">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <Paper
            elevation={0}
            sx={{
              p: { xs: 4, md: 5 },
              borderRadius: 4,
              background: "rgba(255, 255, 255, 0.95)",
              backdropFilter: "blur(10px)",
              border: "1px solid",
              borderColor: "divider",
              boxShadow: "0 20px 60px rgba(0,0,0,0.08)",
            }}
          >
            {/* Header */}
            <Box sx={{ textAlign: "center", mb: 5 }}>
              <Box
                sx={{
                  width: 70,
                  height: 70,
                  mx: "auto",
                  mb: 3,
                  borderRadius: "50%",
                  background:
                    "linear-gradient(135deg, #22c55e 0%, #16a34a 100%)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  boxShadow: "0 10px 30px rgba(34, 197, 94, 0.3)",
                }}
              >
                <Agriculture sx={{ fontSize: 36, color: "white" }} />
              </Box>
              <Typography
                variant="h4"
                component="h1"
                gutterBottom
                sx={{
                  fontWeight: 800,
                  background:
                    "linear-gradient(135deg, #22c55e 0%, #16a34a 100%)",
                  backgroundClip: "text",
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent",
                }}
              >
                Welcome Back
              </Typography>
              <Typography
                variant="body1"
                color="text.secondary"
                sx={{ fontSize: "1.1rem" }}
              >
                Sign in to your VIBE E-Commerce account
              </Typography>
            </Box>

            {error && (
              <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }}>
                {error}
              </Alert>
            )}

            {/* Social Login Buttons */}
            <Box sx={{ mb: 3 }}>
              <Button
                fullWidth
                variant="outlined"
                startIcon={
                  socialLoading === "google" ? (
                    <CircularProgress size={20} />
                  ) : (
                    <Google />
                  )
                }
                onClick={() => handleSocialLogin("google")}
                disabled={socialLoading !== null}
                sx={{
                  mb: 2,
                  py: 1.5,
                  borderRadius: 3,
                  borderColor: "divider",
                  color: "text.primary",
                  fontWeight: 600,
                  "&:hover": {
                    borderColor: "primary.main",
                    backgroundColor: "rgba(34, 197, 94, 0.04)",
                  },
                }}
              >
                {socialLoading === "google"
                  ? "Connecting..."
                  : "Continue with Google"}
              </Button>

              <Button
                fullWidth
                variant="outlined"
                startIcon={
                  socialLoading === "facebook" ? (
                    <CircularProgress size={20} />
                  ) : (
                    <Facebook />
                  )
                }
                onClick={() => handleSocialLogin("facebook")}
                disabled={socialLoading !== null}
                sx={{
                  py: 1.5,
                  borderRadius: 3,
                  borderColor: "divider",
                  color: "#1877f2",
                  fontWeight: 600,
                  "&:hover": {
                    borderColor: "#1877f2",
                    backgroundColor: "rgba(24, 119, 242, 0.04)",
                  },
                }}
              >
                {socialLoading === "facebook"
                  ? "Connecting..."
                  : "Continue with Facebook"}
              </Button>
            </Box>

            <Divider sx={{ mb: 3 }}>
              <Typography variant="body2" color="text.secondary" sx={{ px: 2 }}>
                or continue with email
              </Typography>
            </Divider>

            <Box component="form" onSubmit={handleSubmit}>
              <TextField
                fullWidth
                label="Username or Email"
                name="username"
                value={formData.username}
                onChange={handleChange}
                required
                error={!!formErrors.username}
                helperText={formErrors.username}
                sx={{ mb: 2.5 }}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Person color="action" />
                    </InputAdornment>
                  ),
                  sx: { borderRadius: 3 },
                }}
              />

              <TextField
                fullWidth
                label="Password"
                name="password"
                type={showPassword ? "text" : "password"}
                value={formData.password}
                onChange={handleChange}
                required
                error={!!formErrors.password}
                helperText={formErrors.password}
                sx={{ mb: 2.5 }}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Lock color="action" />
                    </InputAdornment>
                  ),
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        aria-label="toggle password visibility"
                        onClick={handleTogglePasswordVisibility}
                        edge="end"
                      >
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                  sx: { borderRadius: 3 },
                }}
              />

              <Box
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  mb: 3,
                }}
              >
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={rememberMe}
                      onChange={(e) => setRememberMe(e.target.checked)}
                      color="primary"
                    />
                  }
                  label={<Typography variant="body2">Remember me</Typography>}
                />
                <MuiLink
                  component={Link}
                  to="/password-reset"
                  variant="body2"
                  sx={{
                    color: "primary.main",
                    textDecoration: "none",
                    fontWeight: 600,
                    "&:hover": { textDecoration: "underline" },
                  }}
                >
                  Forgot password?
                </MuiLink>
              </Box>

              <Button
                type="submit"
                fullWidth
                variant="contained"
                size="large"
                disabled={loading}
                sx={{
                  mb: 3,
                  py: 1.8,
                  borderRadius: 3,
                  fontWeight: 700,
                  fontSize: "1.1rem",
                  background:
                    "linear-gradient(135deg, #22c55e 0%, #16a34a 100%)",
                  boxShadow: "0 8px 25px rgba(34, 197, 94, 0.25)",
                  "&:hover": {
                    background:
                      "linear-gradient(135deg, #16a34a 0%, #15803d 100%)",
                    boxShadow: "0 10px 30px rgba(34, 197, 94, 0.35)",
                  },
                }}
              >
                {loading ? (
                  <CircularProgress size={24} color="inherit" />
                ) : (
                  "Sign In"
                )}
              </Button>
            </Box>

            <Box sx={{ textAlign: "center" }}>
              <Typography variant="body2" color="text.secondary">
                Don&apos;t have an account?{" "}
                <MuiLink
                  component={Link}
                  to="/register"
                  sx={{
                    color: "primary.main",
                    textDecoration: "none",
                    fontWeight: 700,
                    "&:hover": { textDecoration: "underline" },
                  }}
                >
                  Create one here
                </MuiLink>
              </Typography>
            </Box>

            {/* Additional Links */}
            <Box sx={{ mt: 4, pt: 3, borderTop: 1, borderColor: "divider" }}>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <MuiLink
                    component={Link}
                    to="/help"
                    variant="body2"
                    sx={{
                      color: "text.secondary",
                      textDecoration: "none",
                      "&:hover": { color: "primary.main" },
                    }}
                  >
                    Need Help?
                  </MuiLink>
                </Grid>
                <Grid item xs={6} sx={{ textAlign: "right" }}>
                  <MuiLink
                    component={Link}
                    to="/contact"
                    variant="body2"
                    sx={{
                      color: "text.secondary",
                      textDecoration: "none",
                      "&:hover": { color: "primary.main" },
                    }}
                  >
                    Contact Support
                  </MuiLink>
                </Grid>
              </Grid>
            </Box>
          </Paper>
        </motion.div>

        {/* Demo Credentials */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.3 }}
        >
          <Paper
            sx={{
              p: 3,
              mt: 3,
              borderRadius: 3,
              backgroundColor: "background.paper",
              border: "1px solid",
              borderColor: "divider",
              textAlign: "center",
            }}
          >
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{ fontWeight: 700, mb: 1 }}
            >
              Ã°Å¸â€Â Demo Credentials
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Username: <strong>demo</strong> | Password:{" "}
              <strong>demo123</strong>
            </Typography>
          </Paper>
        </motion.div>
      </Container>
    </Box>
  );
};

export default Login;
