import React, { useState } from "react";
import {
  Container,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  TextField,
  Button,
  Paper,
  Alert,
  Snackbar,
  CircularProgress,
} from "@mui/material";
import {
  Email,
  Phone,
  LocationOn,
  Send,
  AccessTime,
  Chat,
  HeadsetMic,
} from "@mui/icons-material";
import { motion } from "framer-motion";
import ScrollAnimation from "../common/ScrollAnimation";

const Contact = () => {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
    subject: "",
    message: "",
  });
  const [loading, setLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: "",
    severity: "success",
  });
  const [errors, setErrors] = useState({});

  const contactInfo = [
    {
      icon: <Email sx={{ fontSize: 40 }} />,
      title: "Email Us",
      details: "support@vibe-ecommerce.com",
      subtitle: "We respond within 24 hours",
    },
    {
      icon: <Phone sx={{ fontSize: 40 }} />,
      title: "Call Us",
      details: "+91 1800-XXX-XXXX",
      subtitle: "Toll-free, 24/7 support",
    },
    {
      icon: <LocationOn sx={{ fontSize: 40 }} />,
      title: "Visit Us",
      details: "Chennai, Tamil Nadu, India",
      subtitle: "Mon-Sat: 9AM - 6PM",
    },
    {
      icon: <Chat sx={{ fontSize: 40 }} />,
      title: "Live Chat",
      details: "Available on website",
      subtitle: "Instant support",
    },
  ];

  const faqItems = [
    {
      question: "How do I track my order?",
      answer:
        "You can track your order from the Orders page in your account. We also send tracking updates via email and SMS.",
    },
    {
      question: "What is your return policy?",
      answer:
        "We offer a 7-day return policy for most products. Fresh produce can be returned within 24 hours if quality issues are found.",
    },
    {
      question: "How do I become a vendor?",
      answer:
        "Visit our Vendor Registration page and fill out the application form. Our team will review and get back within 48 hours.",
    },
    {
      question: "What payment methods do you accept?",
      answer:
        "We accept UPI, credit/debit cards, net banking, and cash on delivery for eligible orders.",
    },
  ];

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: "" }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    if (!formData.name.trim()) newErrors.name = "Name is required";
    if (!formData.email.trim()) newErrors.email = "Email is required";
    else if (!/\S+@\S+\.\S+/.test(formData.email))
      newErrors.email = "Invalid email format";
    if (!formData.message.trim()) newErrors.message = "Message is required";
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    setLoading(true);
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1500));
    setLoading(false);
    setSnackbar({
      open: true,
      message: "Message sent successfully! We will get back to you soon.",
      severity: "success",
    });
    setFormData({ name: "", email: "", phone: "", subject: "", message: "" });
  };

  return (
    <Box>
      {/* Hero Section */}
      <Box
        sx={{
          background:
            "linear-gradient(135deg, #22c55e 0%, #16a34a 50%, #15803d 100%)",
          color: "white",
          py: { xs: 6, md: 10 },
          position: "relative",
          overflow: "hidden",
        }}
      >
        <Container maxWidth="lg">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <Typography
              variant="h2"
              component="h1"
              fontWeight="bold"
              gutterBottom
              textAlign="center"
            >
              Contact Us
            </Typography>
            <Typography
              variant="h6"
              textAlign="center"
              sx={{ opacity: 0.9, maxWidth: 600, mx: "auto" }}
            >
              Have questions? We'd love to hear from you. Send us a message and
              we'll respond as soon as possible.
            </Typography>
          </motion.div>
        </Container>
      </Box>

      {/* Contact Info Cards */}
      <Container maxWidth="lg" sx={{ mt: -4, position: "relative", zIndex: 1 }}>
        <Grid container spacing={3}>
          {contactInfo.map((info, index) => (
            <Grid item xs={6} md={3} key={info.title}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <Paper
                  elevation={3}
                  sx={{
                    p: 3,
                    textAlign: "center",
                    borderRadius: 3,
                    height: "100%",
                    transition: "all 0.3s ease",
                    "&:hover": {
                      transform: "translateY(-5px)",
                      boxShadow: 6,
                    },
                  }}
                >
                  <Box sx={{ color: "primary.main", mb: 2 }}>{info.icon}</Box>
                  <Typography variant="h6" fontWeight="bold" gutterBottom>
                    {info.title}
                  </Typography>
                  <Typography variant="body1" color="primary" fontWeight="600">
                    {info.details}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {info.subtitle}
                  </Typography>
                </Paper>
              </motion.div>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* Contact Form and Map */}
      <Container maxWidth="lg" sx={{ py: 10 }}>
        <Grid container spacing={6}>
          {/* Contact Form */}
          <Grid item xs={12} md={6}>
            <ScrollAnimation animation="fadeRight">
              <Typography variant="h4" fontWeight="bold" gutterBottom>
                Send us a Message
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
                Fill out the form below and our team will get back to you within
                24 hours.
              </Typography>

              <Box component="form" onSubmit={handleSubmit}>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Your Name"
                      name="name"
                      value={formData.name}
                      onChange={handleChange}
                      error={!!errors.name}
                      helperText={errors.name}
                      required
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Email Address"
                      name="email"
                      type="email"
                      value={formData.email}
                      onChange={handleChange}
                      error={!!errors.email}
                      helperText={errors.email}
                      required
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Phone Number"
                      name="phone"
                      value={formData.phone}
                      onChange={handleChange}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Subject"
                      name="subject"
                      value={formData.subject}
                      onChange={handleChange}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Your Message"
                      name="message"
                      multiline
                      rows={4}
                      value={formData.message}
                      onChange={handleChange}
                      error={!!errors.message}
                      helperText={errors.message}
                      required
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <Button
                      type="submit"
                      variant="contained"
                      size="large"
                      fullWidth
                      disabled={loading}
                      startIcon={
                        loading ? <CircularProgress size={20} /> : <Send />
                      }
                      sx={{ py: 1.5 }}
                    >
                      {loading ? "Sending..." : "Send Message"}
                    </Button>
                  </Grid>
                </Grid>
              </Box>
            </ScrollAnimation>
          </Grid>

          {/* Map/Info Section */}
          <Grid item xs={12} md={6}>
            <ScrollAnimation animation="fadeLeft">
              <Card sx={{ borderRadius: 3, height: "100%", minHeight: 400 }}>
                <Box
                  sx={{
                    background:
                      "linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)",
                    height: 200,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                  }}
                >
                  <LocationOn
                    sx={{ fontSize: 80, color: "primary.main", opacity: 0.5 }}
                  />
                </Box>
                <CardContent sx={{ p: 3 }}>
                  <Typography variant="h6" fontWeight="bold" gutterBottom>
                    Our Office
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    VIBE E-Commerce Pvt. Ltd.
                    <br />
                    123, Tech Park Road
                    <br />
                    Chennai, Tamil Nadu 600001
                    <br />
                    India
                  </Typography>
                  <Box
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      gap: 1,
                      mt: 2,
                    }}
                  >
                    <AccessTime color="action" />
                    <Typography variant="body2" color="text.secondary">
                      Mon - Sat: 9:00 AM - 6:00 PM IST
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </ScrollAnimation>
          </Grid>
        </Grid>
      </Container>

      {/* FAQ Section */}
      <Box sx={{ bgcolor: "grey.50", py: 10 }}>
        <Container maxWidth="lg">
          <ScrollAnimation animation="fadeUp">
            <Box sx={{ textAlign: "center", mb: 6 }}>
              <HeadsetMic sx={{ fontSize: 48, color: "primary.main", mb: 2 }} />
              <Typography variant="h4" fontWeight="bold" gutterBottom>
                Frequently Asked Questions
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Quick answers to common questions
              </Typography>
            </Box>
          </ScrollAnimation>

          <Grid container spacing={3}>
            {faqItems.map((faq, index) => (
              <Grid item xs={12} md={6} key={faq.question}>
                <ScrollAnimation animation="fadeUp" delay={index * 0.1}>
                  <Card sx={{ height: "100%", borderRadius: 3 }}>
                    <CardContent sx={{ p: 3 }}>
                      <Typography
                        variant="h6"
                        fontWeight="bold"
                        gutterBottom
                        color="primary"
                      >
                        {faq.question}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {faq.answer}
                      </Typography>
                    </CardContent>
                  </Card>
                </ScrollAnimation>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
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
    </Box>
  );
};

export default Contact;
