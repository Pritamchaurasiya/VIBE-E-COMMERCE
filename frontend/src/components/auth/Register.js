import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
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
  LinearProgress,
  Chip,
} from "@mui/material";
import {
  Visibility,
  VisibilityOff,
  Google,
  Facebook,
  Email,
  Lock,
  Person,
  Business,
  CheckCircle,
  Agriculture,
} from "@mui/icons-material";
import { useAuth } from "../../utils/AuthContext";
import { motion } from "framer-motion";

const Register = () => {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    username: "",
    email: "",
    first_name: "",
    last_name: "",
    company: "",
    password: "",
    confirm_password: "",
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [acceptTerms, setAcceptTerms] = useState(false);
  const [subscribeNewsletter, setSubscribeNewsletter] = useState(true);
  const [loading, setLoading] = useState(false);
  const [socialLoading, setSocialLoading] = useState(null);
  const [error, setError] = useState("");
  const [formErrors, setFormErrors] = useState({});

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });

    // Clear field-specific error
    if (formErrors[name]) {
      setFormErrors({
        ...formErrors,
        [name]: "",
      });
    }
  };

  const getPasswordStrength = (password) => {
    let strength = 0;
    if (password.length >= 8) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/\d/.test(password)) strength++;
    if (/[^A-Za-z0-9]/.test(password)) strength++;
    return strength;
  };

  const getPasswordStrengthLabel = (strength) => {
    switch (strength) {
      case 0:
      case 1:
        return { label: "Very Weak", color: "error" };
      case 2:
        return { label: "Weak", color: "warning" };
      case 3:
        return { label: "Fair", color: "info" };
      case 4:
        return { label: "Good", color: "success" };
      case 5:
        return { label: "Strong", color: "success" };
      default:
        return { label: "Very Weak", color: "error" };
    }
  };

  const validateForm = () => {
    const errors = {};

    if (!formData.username.trim()) {
      errors.username = "Username is required";
    } else if (formData.username.length < 3) {
      errors.username = "Username must be at least 3 characters";
    }

    if (!formData.email.trim()) {
      errors.email = "Email is required";
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      errors.email = "Email is invalid";
    }

    if (!formData.first_name.trim()) {
      errors.first_name = "First name is required";
    }

    if (!formData.password.trim()) {
      errors.password = "Password is required";
    } else if (formData.password.length < 8) {
      errors.password = "Password must be at least 8 characters";
    } else if (getPasswordStrength(formData.password) < 3) {
      errors.password = "Password is too weak";
    }

    if (!formData.confirm_password.trim()) {
      errors.confirm_password = "Please confirm your password";
    } else if (formData.password !== formData.confirm_password) {
      errors.confirm_password = "Passwords do not match";
    }

    if (!acceptTerms) {
      errors.acceptTerms = "You must accept the terms and conditions";
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!validateForm()) return;

    setLoading(true);

    const result = await register({
      ...formData,
      subscribe_newsletter: subscribeNewsletter,
    });

    if (result.success) {
      navigate("/");
    } else {
      setError(result.error);
    }

    setLoading(false);
  };

  const handleSocialRegister = async (provider) => {
    setSocialLoading(provider);
    setError("");

    try {
      // Simulate social registration - replace with actual implementation
      await new Promise((resolve) => setTimeout(resolve, 2000));

      // For demo purposes, simulate successful registration
      alert(`${provider} registration successful!`);
      navigate("/");
    } catch (err) {
      console.error(`${provider} registration error:`, err);
      setError(`${provider} registration failed. Please try again.`);
    } finally {
      setSocialLoading(null);
    }
  };

  const passwordStrength = getPasswordStrength(formData.password);
  const strengthInfo = getPasswordStrengthLabel(passwordStrength);

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        py: { xs: 4, md: 6 },
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
              p: { xs: 3, md: 5 },
              borderRadius: 4,
              background: "rgba(255, 255, 255, 0.95)",
              backdropFilter: "blur(10px)",
              border: "1px solid",
              borderColor: "divider",
              boxShadow: "0 20px 60px rgba(0,0,0,0.08)",
            }}
          >
            {/* Header */}
            <Box sx={{ textAlign: "center", mb: 4 }}>
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{
                  type: "spring",
                  stiffness: 200,
                  damping: 20,
                  delay: 0.2,
                }}
              >
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
              </motion.div>
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
                Join VIBE E-Commerce
              </Typography>
              <Typography
                variant="body1"
                color="text.secondary"
                sx={{ fontSize: "1.1rem" }}
              >
                Create your account to access premium agricultural products
              </Typography>
            </Box>

            {error && (
              <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }}>
                {error}
              </Alert>
            )}

            {/* Social Registration Buttons */}
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
                onClick={() => handleSocialRegister("google")}
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
                onClick={() => handleSocialRegister("facebook")}
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
                or create account with email
              </Typography>
            </Divider>

            <Box component="form" onSubmit={handleSubmit}>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="First Name"
                    name="first_name"
                    value={formData.first_name}
                    onChange={handleChange}
                    required
                    error={!!formErrors.first_name}
                    helperText={formErrors.first_name}
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <Person color="action" />
                        </InputAdornment>
                      ),
                      sx: { borderRadius: 3 },
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
                      sx: { borderRadius: 3 },
                    }}
                  />
                </Grid>
              </Grid>

              <TextField
                fullWidth
                label="Username"
                name="username"
                value={formData.username}
                onChange={handleChange}
                required
                error={!!formErrors.username}
                helperText={formErrors.username}
                sx={{ mt: 2.5 }}
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
                label="Email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                required
                error={!!formErrors.email}
                helperText={formErrors.email}
                sx={{ mt: 2.5 }}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Email color="action" />
                    </InputAdornment>
                  ),
                  sx: { borderRadius: 3 },
                }}
              />

              <TextField
                fullWidth
                label="Company (Optional)"
                name="company"
                value={formData.company}
                onChange={handleChange}
                sx={{ mt: 2.5 }}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Business color="action" />
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
                sx={{ mt: 2.5 }}
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
                        onClick={() => setShowPassword(!showPassword)}
                        edge="end"
                      >
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                  sx: { borderRadius: 3 },
                }}
              />

              {formData.password && (
                <Box sx={{ mt: 1, mb: 2 }}>
                  <Box
                    sx={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      mb: 1,
                    }}
                  >
                    <Typography variant="body2" color="text.secondary">
                      Password Strength:
                    </Typography>
                    <Chip
                      label={strengthInfo.label}
                      color={strengthInfo.color}
                      size="small"
                      variant="outlined"
                      sx={{ height: 20 }}
                    />
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={(passwordStrength / 5) * 100}
                    color={strengthInfo.color}
                    sx={{ height: 6, borderRadius: 3, bgcolor: "action.hover" }}
                  />
                </Box>
              )}

              <TextField
                fullWidth
                label="Confirm Password"
                name="confirm_password"
                type={showConfirmPassword ? "text" : "password"}
                value={formData.confirm_password}
                onChange={handleChange}
                required
                error={!!formErrors.confirm_password}
                helperText={formErrors.confirm_password}
                sx={{ mt: 2.5 }}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Lock color="action" />
                    </InputAdornment>
                  ),
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        aria-label="toggle confirm password visibility"
                        onClick={() =>
                          setShowConfirmPassword(!showConfirmPassword)
                        }
                        edge="end"
                      >
                        {showConfirmPassword ? (
                          <VisibilityOff />
                        ) : (
                          <Visibility />
                        )}
                      </IconButton>
                    </InputAdornment>
                  ),
                  sx: { borderRadius: 3 },
                }}
              />

              <Box sx={{ mt: 3 }}>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={acceptTerms}
                      onChange={(e) => setAcceptTerms(e.target.checked)}
                      color="primary"
                    />
                  }
                  label={
                    <Typography variant="body2" color="text.secondary">
                      I agree to the{" "}
                      <a
                        href="/terms"
                        style={{
                          color: "#22c55e",
                          textDecoration: "none",
                          fontWeight: 600,
                        }}
                      >
                        Terms and Conditions
                      </a>{" "}
                      and{" "}
                      <a
                        href="/privacy"
                        style={{
                          color: "#22c55e",
                          textDecoration: "none",
                          fontWeight: 600,
                        }}
                      >
                        Privacy Policy
                      </a>
                    </Typography>
                  }
                />
                {formErrors.acceptTerms && (
                  <Typography
                    variant="caption"
                    color="error"
                    sx={{ mt: 0.5, display: "block" }}
                  >
                    {formErrors.acceptTerms}
                  </Typography>
                )}

                <FormControlLabel
                  control={
                    <Checkbox
                      checked={subscribeNewsletter}
                      onChange={(e) => setSubscribeNewsletter(e.target.checked)}
                      color="primary"
                    />
                  }
                  label={
                    <Typography variant="body2" color="text.secondary">
                      Subscribe to newsletter for farming tips and offers
                    </Typography>
                  }
                  sx={{ mt: 1 }}
                />
              </Box>

              <Button
                type="submit"
                fullWidth
                variant="contained"
                size="large"
                disabled={loading || !acceptTerms}
                sx={{
                  mt: 3,
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
                  "Create Account"
                )}
              </Button>
            </Box>

            <Box sx={{ textAlign: "center", mt: 3 }}>
              <Typography variant="body2" color="text.secondary">
                Already have an account?{" "}
                <MuiLink
                  component={Link}
                  to="/login"
                  sx={{
                    color: "primary.main",
                    textDecoration: "none",
                    fontWeight: 700,
                    "&:hover": {
                      textDecoration: "underline",
                    },
                  }}
                >
                  Sign in here
                </MuiLink>
              </Typography>
            </Box>

            {/* Benefits */}
            <Box sx={{ mt: 4, pt: 3, borderTop: 1, borderColor: "divider" }}>
              <Typography
                variant="h6"
                gutterBottom
                fontWeight="700"
                textAlign="center"
                fontSize="1rem"
              >
                Why Join VIBE E-Commerce?
              </Typography>
              <Grid container spacing={2} sx={{ mt: 1 }}>
                <Grid item xs={4} sx={{ textAlign: "center" }}>
                  <motion.div
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                  >
                    <CheckCircle color="success" sx={{ fontSize: 28 }} />
                    <Typography
                      variant="caption"
                      sx={{ mt: 0.5, display: "block", fontWeight: 600 }}
                    >
                      Free Shipping
                    </Typography>
                  </motion.div>
                </Grid>
                <Grid item xs={4} sx={{ textAlign: "center" }}>
                  <motion.div
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                  >
                    <CheckCircle color="success" sx={{ fontSize: 28 }} />
                    <Typography
                      variant="caption"
                      sx={{ mt: 0.5, display: "block", fontWeight: 600 }}
                    >
                      Quality Products
                    </Typography>
                  </motion.div>
                </Grid>
                <Grid item xs={4} sx={{ textAlign: "center" }}>
                  <motion.div
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                  >
                    <CheckCircle color="success" sx={{ fontSize: 28 }} />
                    <Typography
                      variant="caption"
                      sx={{ mt: 0.5, display: "block", fontWeight: 600 }}
                    >
                      Expert Support
                    </Typography>
                  </motion.div>
                </Grid>
              </Grid>
            </Box>
          </Paper>
        </motion.div>
      </Container>
    </Box>
  );
};

export default Register;
