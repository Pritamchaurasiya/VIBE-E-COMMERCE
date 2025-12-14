import React from "react";
import PropTypes from "prop-types";
import { Link as RouterLink } from "react-router-dom";
import {
  Box,
  Container,
  Typography,
  Grid,
  Link,
  IconButton,
  Divider,
  TextField,
  InputAdornment,
} from "@mui/material";
import {
  Facebook,
  Twitter,
  Instagram,
  LinkedIn,
  YouTube,
  Email,
  Phone,
  LocationOn,
  Send,
} from "@mui/icons-material";
import { motion } from "framer-motion";

const FooterLink = ({ to, children }) => (
  <Link
    component={RouterLink}
    to={to}
    color="inherit"
    sx={{
      display: "block",
      mb: 1,
      opacity: 0.8,
      textDecoration: "none",
      transition: "all 0.2s ease",
      "&:hover": {
        opacity: 1,
        transform: "translateX(4px)",
      },
    }}
  >
    {children}
  </Link>
);

FooterLink.propTypes = {
  to: PropTypes.string.isRequired,
  children: PropTypes.node.isRequired,
};

const Footer = () => {
  const currentYear = new Date().getFullYear();

  const socialLinks = [
    { icon: <Facebook />, url: "#", label: "Facebook" },
    { icon: <Twitter />, url: "#", label: "Twitter" },
    { icon: <Instagram />, url: "#", label: "Instagram" },
    { icon: <LinkedIn />, url: "#", label: "LinkedIn" },
    { icon: <YouTube />, url: "#", label: "YouTube" },
  ];

  return (
    <Box
      component="footer"
      sx={{
        background:
          "linear-gradient(135deg, #1f2937 0%, #374151 50%, #1f2937 100%)",
        color: "white",
        pt: 6,
        pb: 3,
        mt: "auto",
      }}
    >
      <Container maxWidth="lg">
        <Grid container spacing={4}>
          {/* Company Info */}
          <Grid item xs={12} md={4}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
            >
              <Typography
                variant="h5"
                fontWeight="bold"
                gutterBottom
                sx={{
                  background:
                    "linear-gradient(135deg, #4ade80 0%, #22c55e 100%)",
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent",
                }}
              >
                VIBE E-Commerce
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.8, mb: 2 }}>
                Your trusted partner for quality products and excellent service.
                Connecting farmers, vendors, and customers through innovation.
              </Typography>

              {/* Contact Info */}
              <Box sx={{ mt: 2 }}>
                <Box
                  sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}
                >
                  <Email fontSize="small" sx={{ color: "primary.light" }} />
                  <Typography variant="body2">
                    support@vibe-ecommerce.com
                  </Typography>
                </Box>
                <Box
                  sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}
                >
                  <Phone fontSize="small" sx={{ color: "primary.light" }} />
                  <Typography variant="body2">+91 1800-XXX-XXXX</Typography>
                </Box>
                <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                  <LocationOn
                    fontSize="small"
                    sx={{ color: "primary.light" }}
                  />
                  <Typography variant="body2">
                    Chennai, Tamil Nadu, India
                  </Typography>
                </Box>
              </Box>

              {/* Social Links */}
              <Box sx={{ mt: 2, display: "flex", gap: 1 }}>
                {socialLinks.map((social) => (
                  <IconButton
                    key={social.label}
                    href={social.url}
                    aria-label={social.label}
                    sx={{
                      color: "white",
                      bgcolor: "rgba(255,255,255,0.1)",
                      transition: "all 0.3s ease",
                      "&:hover": {
                        bgcolor: "primary.main",
                        transform: "translateY(-3px)",
                      },
                    }}
                    size="small"
                  >
                    {social.icon}
                  </IconButton>
                ))}
              </Box>
            </motion.div>
          </Grid>

          {/* Quick Links */}
          <Grid item xs={6} sm={3} md={2}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              viewport={{ once: true }}
            >
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Quick Links
              </Typography>
              <FooterLink to="/">Home</FooterLink>
              <FooterLink to="/products">Products</FooterLink>
              <FooterLink to="/vendors">Vendors</FooterLink>
              <FooterLink to="/compare">Compare</FooterLink>
              <FooterLink to="/about">About Us</FooterLink>
              <FooterLink to="/contact">Contact</FooterLink>
            </motion.div>
          </Grid>

          {/* Account */}
          <Grid item xs={6} sm={3} md={2}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              viewport={{ once: true }}
            >
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                My Account
              </Typography>
              <FooterLink to="/profile">Profile</FooterLink>
              <FooterLink to="/orders">My Orders</FooterLink>
              <FooterLink to="/wishlist">Wishlist</FooterLink>
              <FooterLink to="/cart">Cart</FooterLink>
              <FooterLink to="/messages">Messages</FooterLink>
              <FooterLink to="/login">Login</FooterLink>
            </motion.div>
          </Grid>

          {/* Customer Service */}
          <Grid item xs={6} sm={3} md={2}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              viewport={{ once: true }}
            >
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Help & Support
              </Typography>
              <FooterLink to="/contact">Help Center</FooterLink>
              <FooterLink to="/contact">Shipping Info</FooterLink>
              <FooterLink to="/contact">Returns</FooterLink>
              <FooterLink to="/contact">FAQs</FooterLink>
              <FooterLink to="/contact">Track Order</FooterLink>
            </motion.div>
          </Grid>

          {/* Newsletter */}
          <Grid item xs={12} sm={6} md={2}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              viewport={{ once: true }}
            >
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Newsletter
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.8, mb: 2 }}>
                Subscribe for updates and exclusive offers.
              </Typography>
              <TextField
                placeholder="Your email"
                size="small"
                fullWidth
                sx={{
                  "& .MuiOutlinedInput-root": {
                    bgcolor: "rgba(255,255,255,0.1)",
                    color: "white",
                    "& fieldset": { borderColor: "rgba(255,255,255,0.3)" },
                    "&:hover fieldset": {
                      borderColor: "rgba(255,255,255,0.5)",
                    },
                  },
                  "& input::placeholder": { color: "rgba(255,255,255,0.5)" },
                }}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton size="small" sx={{ color: "primary.light" }}>
                        <Send />
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />
            </motion.div>
          </Grid>
        </Grid>

        <Divider sx={{ my: 4, borderColor: "rgba(255,255,255,0.1)" }} />

        {/* Bottom Bar */}
        <Box
          sx={{
            display: "flex",
            flexDirection: { xs: "column", sm: "row" },
            justifyContent: "space-between",
            alignItems: "center",
            gap: 2,
          }}
        >
          <Typography variant="body2" sx={{ opacity: 0.7 }}>
            Ã‚Â© {currentYear} VIBE E-Commerce. All rights reserved.
          </Typography>
          <Box sx={{ display: "flex", gap: 2 }}>
            <Link
              href="#"
              color="inherit"
              sx={{ opacity: 0.7, "&:hover": { opacity: 1 } }}
            >
              Privacy Policy
            </Link>
            <Link
              href="#"
              color="inherit"
              sx={{ opacity: 0.7, "&:hover": { opacity: 1 } }}
            >
              Terms of Service
            </Link>
            <Link
              href="#"
              color="inherit"
              sx={{ opacity: 0.7, "&:hover": { opacity: 1 } }}
            >
              Cookie Policy
            </Link>
          </Box>
        </Box>
      </Container>
    </Box>
  );
};

export default Footer;
