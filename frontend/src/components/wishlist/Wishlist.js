import React, { useState, useEffect, useCallback } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardMedia,
  Button,
  Box,
  Chip,
  IconButton,
  Alert,
  Skeleton,
  Snackbar,
  Paper,
} from "@mui/material";
import {
  Favorite,
  ShoppingCart,
  DeleteOutline,
  ArrowForward,
} from "@mui/icons-material";
import { wishlistAPI } from "../../services/api";
import { useAuth } from "../../utils/AuthContext";
import { useCart } from "../../utils/CartContext";
import { formatCurrency } from "../../utils/formatCurrency";
import { motion, AnimatePresence } from "framer-motion";

const Wishlist = () => {
  const { isAuthenticated } = useAuth();
  const { addToCart } = useCart();
  const navigate = useNavigate();
  const [wishlist, setWishlist] = useState([]);
  const [loading, setLoading] = useState(true);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: "",
    severity: "success",
  });

  const loadWishlist = useCallback(async () => {
    try {
      const response = await wishlistAPI.getWishlist();
      setWishlist(response.data);
    } catch (error) {
      console.error("Failed to load wishlist:", error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (isAuthenticated) {
      loadWishlist();
    } else {
      setLoading(false);
    }
  }, [isAuthenticated, loadWishlist]);

  // Real-time updates with polling
  useEffect(() => {
    if (!isAuthenticated) return;

    const pollInterval = setInterval(() => {
      loadWishlist();
    }, 30000); // Poll every 30 seconds

    return () => clearInterval(pollInterval);
  }, [isAuthenticated, loadWishlist]);

  const handleRemoveFromWishlist = async (productId) => {
    try {
      await wishlistAPI.removeFromWishlist(productId);
      setWishlist((prev) =>
        prev.filter((item) => item.product.id !== productId),
      );
      setSnackbar({
        open: true,
        message: "Removed from wishlist",
        severity: "success",
      });
    } catch (error) {
      console.error("Failed to remove from wishlist:", error);
      setSnackbar({
        open: true,
        message: "Failed to remove from wishlist",
        severity: "error",
      });
    }
  };

  const handleAddToCart = async (product) => {
    const result = await addToCart(product.id);
    if (result.success) {
      setSnackbar({
        open: true,
        message: "Added to cart!",
        severity: "success",
      });
    } else {
      setSnackbar({ open: true, message: result.error, severity: "error" });
    }
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  if (!isAuthenticated) {
    return (
      <Container maxWidth="md" sx={{ py: 8, textAlign: "center" }}>
        <Typography variant="h5" gutterBottom>
          Please login to view your wishlist
        </Typography>
        <Button variant="contained" onClick={() => navigate("/login")}>
          Login Now
        </Button>
      </Container>
    );
  }

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 6 }}>
        <Box sx={{ mb: 4 }}>
          <Skeleton variant="text" width={300} height={60} />
          <Skeleton variant="text" width={400} height={20} />
        </Box>
        <Grid container spacing={3}>
          {["item-1", "item-2", "item-3", "item-4"].map((id) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={`skeleton-${id}`}>
              <Skeleton
                variant="rectangular"
                height={380}
                sx={{ borderRadius: 4 }}
              />
            </Grid>
          ))}
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
            fontWeight="800"
            sx={{ color: "#1e293b" }}
          >
            My Wishlist
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
            {wishlist.length} {wishlist.length === 1 ? "item" : "items"} saved
            for later
          </Typography>
        </motion.div>

        {wishlist.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
          >
            <Paper
              elevation={0}
              sx={{
                p: 6,
                textAlign: "center",
                borderRadius: 4,
                border: "1px dashed",
                borderColor: "divider",
                bgcolor: "transparent",
              }}
            >
              <Favorite sx={{ fontSize: 60, color: "text.disabled", mb: 2 }} />
              <Typography variant="h6" color="text.secondary" gutterBottom>
                Your wishlist is empty
              </Typography>
              <Button
                component={Link}
                to="/products"
                variant="contained"
                startIcon={<ArrowForward />}
                sx={{
                  mt: 2,
                  borderRadius: 2,
                  textTransform: "none",
                  background:
                    "linear-gradient(135deg, #22c55e 0%, #16a34a 100%)",
                }}
              >
                Browse Products
              </Button>
            </Paper>
          </motion.div>
        ) : (
          <Grid container spacing={3}>
            <AnimatePresence>
              {wishlist.map((item) => {
                const product = item.product;
                return (
                  <Grid item xs={12} sm={6} md={4} lg={3} key={item.id}>
                    <motion.div
                      layout
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.9 }}
                      transition={{ duration: 0.3 }}
                    >
                      <Card
                        elevation={0}
                        sx={{
                          height: "100%",
                          display: "flex",
                          flexDirection: "column",
                          position: "relative",
                          borderRadius: 4,
                          border: "1px solid",
                          borderColor: "divider",
                          transition: "all 0.3s ease",
                          "&:hover": {
                            transform: "translateY(-4px)",
                            boxShadow: "0 12px 24px -4px rgba(0, 0, 0, 0.1)",
                            borderColor: "primary.light",
                          },
                        }}
                      >
                        <IconButton
                          sx={{
                            position: "absolute",
                            top: 12,
                            right: 12,
                            zIndex: 1,
                            backgroundColor: "rgba(255,255,255,0.9)",
                            backdropFilter: "blur(4px)",
                            boxShadow: 1,
                            "&:hover": {
                              backgroundColor: "#fff",
                              color: "error.main",
                            },
                          }}
                          size="small"
                          onClick={() => handleRemoveFromWishlist(product.id)}
                        >
                          <DeleteOutline fontSize="small" />
                        </IconButton>

                        <CardMedia
                          component={Link}
                          to={`/products/${product.slug}`}
                          sx={{
                            height: 220,
                            textDecoration: "none",
                            bgcolor: "action.hover",
                            position: "relative",
                          }}
                        >
                          <Box
                            component="img"
                            src={product.image || "/placeholder.png"}
                            alt={product.name}
                            sx={{
                              width: "100%",
                              height: "100%",
                              objectFit: "cover",
                            }}
                          />
                          {product.discount_percentage > 0 && (
                            <Chip
                              label={`${product.discount_percentage}% OFF`}
                              color="error"
                              size="small"
                              sx={{
                                position: "absolute",
                                top: 12,
                                left: 12,
                                fontWeight: 700,
                                fontSize: "0.7rem",
                              }}
                            />
                          )}
                        </CardMedia>

                        <CardContent sx={{ flexGrow: 1, p: 2.5 }}>
                          <Typography
                            variant="subtitle2"
                            color="text.secondary"
                            gutterBottom
                            sx={{
                              fontSize: "0.75rem",
                              textTransform: "uppercase",
                              letterSpacing: 0.5,
                            }}
                          >
                            {product.category?.name}
                          </Typography>

                          <Typography
                            variant="h6"
                            component={Link}
                            to={`/products/${product.slug}`}
                            sx={{
                              textDecoration: "none",
                              color: "text.primary",
                              display: "-webkit-box",
                              overflow: "hidden",
                              WebkitBoxOrient: "vertical",
                              WebkitLineClamp: 2,
                              mb: 1.5,
                              lineHeight: 1.3,
                              height: 42,
                              fontWeight: 600,
                              "&:hover": {
                                color: "primary.main",
                              },
                            }}
                          >
                            {product.name}
                          </Typography>

                          <Box
                            sx={{
                              display: "flex",
                              alignItems: "center",
                              gap: 1,
                              mb: 2,
                            }}
                          >
                            <Typography
                              variant="h6"
                              color="primary.main"
                              fontWeight="700"
                            >
                              {formatCurrency(product.price)}
                            </Typography>
                            {product.mrp && product.mrp > product.price && (
                              <Typography
                                variant="body2"
                                sx={{
                                  textDecoration: "line-through",
                                  color: "text.disabled",
                                }}
                              >
                                {formatCurrency(product.mrp)}
                              </Typography>
                            )}
                          </Box>

                          <Button
                            variant="contained"
                            fullWidth
                            startIcon={<ShoppingCart />}
                            onClick={() => handleAddToCart(product)}
                            disabled={!product.in_stock}
                            sx={{
                              borderRadius: 2,
                              background:
                                "linear-gradient(135deg, #1e293b 0%, #0f172a 100%)",
                              textTransform: "none",
                              fontWeight: 600,
                              boxShadow: "none",
                              "&:hover": {
                                boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                                background:
                                  "linear-gradient(135deg, #0f172a 0%, #020617 100%)",
                              },
                            }}
                          >
                            {product.in_stock ? "Add to Cart" : "Out of Stock"}
                          </Button>
                        </CardContent>
                      </Card>
                    </motion.div>
                  </Grid>
                );
              })}
            </AnimatePresence>
          </Grid>
        )}

        <Snackbar
          open={snackbar.open}
          autoHideDuration={4000}
          onClose={handleCloseSnackbar}
          anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
        >
          <Alert
            onClose={handleCloseSnackbar}
            severity={snackbar.severity}
            variant="filled"
            sx={{ width: "100%" }}
          >
            {snackbar.message}
          </Alert>
        </Snackbar>
      </Container>
    </Box>
  );
};

export default Wishlist;
