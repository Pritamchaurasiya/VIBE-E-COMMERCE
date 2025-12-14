import React from "react";
import { Link } from "react-router-dom";
import { Container, Typography, Button, Box, Paper } from "@mui/material";
import { Home, Search, ShoppingBag } from "@mui/icons-material";
import { motion } from "framer-motion";

const NotFound = () => {
  return (
    <Container maxWidth="md" sx={{ py: 8, textAlign: "center" }}>
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <Paper
          elevation={0}
          sx={{
            p: 6,
            borderRadius: 4,
            background:
              "linear-gradient(145deg, rgba(74,222,128,0.05) 0%, rgba(34,197,94,0.1) 100%)",
            border: "1px solid",
            borderColor: "divider",
          }}
        >
          {/* 404 Animation */}
          <motion.div
            animate={{
              y: [0, -10, 0],
              rotateZ: [0, 2, -2, 0],
            }}
            transition={{
              duration: 3,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          >
            <Typography
              variant="h1"
              component="h1"
              sx={{
                fontSize: { xs: "6rem", md: "10rem" },
                fontWeight: 900,
                background:
                  "linear-gradient(135deg, #22c55e 0%, #16a34a 50%, #4ade80 100%)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
                lineHeight: 1,
                mb: 2,
              }}
            >
              404
            </Typography>
          </motion.div>

          <Typography
            variant="h4"
            component="h2"
            fontWeight="bold"
            gutterBottom
          >
            Page Not Found
          </Typography>

          <Typography
            variant="body1"
            color="text.secondary"
            sx={{ mb: 4, maxWidth: 400, mx: "auto" }}
          >
            Oops! The page you're looking for doesn't exist or has been moved.
            Let's get you back on track.
          </Typography>

          {/* Quick Links */}
          <Box
            sx={{
              display: "flex",
              flexDirection: { xs: "column", sm: "row" },
              gap: 2,
              justifyContent: "center",
              mb: 4,
            }}
          >
            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              <Button
                component={Link}
                to="/"
                variant="contained"
                size="large"
                startIcon={<Home />}
                sx={{
                  px: 4,
                  py: 1.5,
                  borderRadius: 2,
                  background:
                    "linear-gradient(135deg, #22c55e 0%, #16a34a 100%)",
                  "&:hover": {
                    background:
                      "linear-gradient(135deg, #16a34a 0%, #15803d 100%)",
                  },
                }}
              >
                Go to Home
              </Button>
            </motion.div>

            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              <Button
                component={Link}
                to="/products"
                variant="outlined"
                size="large"
                startIcon={<ShoppingBag />}
                sx={{
                  px: 4,
                  py: 1.5,
                  borderRadius: 2,
                }}
              >
                Browse Products
              </Button>
            </motion.div>
          </Box>

          {/* Search Suggestion */}
          <Paper
            variant="outlined"
            sx={{
              p: 3,
              borderRadius: 3,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: 2,
              maxWidth: 400,
              mx: "auto",
            }}
          >
            <Search color="action" />
            <Typography variant="body2" color="text.secondary">
              Try searching for what you need or contact our support team
            </Typography>
          </Paper>

          {/* Helpful Links */}
          <Box sx={{ mt: 4 }}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Popular Pages
            </Typography>
            <Box
              sx={{
                display: "flex",
                flexWrap: "wrap",
                gap: 1,
                justifyContent: "center",
              }}
            >
              {[
                { label: "Products", to: "/products" },
                { label: "About Us", to: "/about" },
                { label: "Contact", to: "/contact" },
                { label: "My Orders", to: "/orders" },
                { label: "Wishlist", to: "/wishlist" },
              ].map((link) => (
                <Button
                  key={link.to}
                  component={Link}
                  to={link.to}
                  size="small"
                  sx={{
                    textTransform: "none",
                    color: "text.primary",
                    "&:hover": {
                      color: "primary.main",
                    },
                  }}
                >
                  {link.label}
                </Button>
              ))}
            </Box>
          </Box>
        </Paper>
      </motion.div>
    </Container>
  );
};

export default NotFound;
