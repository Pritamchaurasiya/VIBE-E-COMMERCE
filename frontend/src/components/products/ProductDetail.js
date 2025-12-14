import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
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
  Rating,
  Divider,
  TextField,
  Alert,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tab,
  Tabs,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableRow,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Breadcrumbs,
  Skeleton,
  Avatar,
} from "@mui/material";
import {
  Favorite,
  FavoriteBorder,
  Add,
  Remove,
  Share,
  LocalShipping,
  Verified,
  Agriculture,
  Warning,
  Info,
  ExpandMore,
  ShoppingCart,
  Star,
  ThumbUp,
} from "@mui/icons-material";
import { productsAPI, reviewsAPI, wishlistAPI, recentlyViewedAPI } from "../../services/api";
import { useAuth } from "../../utils/AuthContext";
import { useCart } from "../../utils/CartContext";
import { motion } from "framer-motion";
import ScrollAnimation from "../common/ScrollAnimation";

const ProductDetail = () => {
  const { slug } = useParams();
  const { isAuthenticated, user } = useAuth();
  const { addToCart } = useCart();

  const [product, setProduct] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [reviewDialogOpen, setReviewDialogOpen] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const [selectedImage, setSelectedImage] = useState(0);
  const [reviewForm, setReviewForm] = useState({
    rating: 5,
    title: "",
    comment: "",
  });
  const [submittingReview, setSubmittingReview] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [productRes, reviewsRes] = await Promise.all([
          productsAPI.getProduct(slug),
          reviewsAPI.getReviews(slug),
        ]);

        setProduct(productRes.data);
        setReviews(reviewsRes.data);

        // Add to Recently Viewed
        if (productRes.data.id) {
           recentlyViewedAPI.addToRecentlyViewed(productRes.data.id).catch(err => console.warn("Logged recently viewed failed", err));
        }

        // Load recommendations for the actual product
        if (productRes.data.id) {
          const recRes = await productsAPI.getRecommendations(
            productRes.data.id,
          );
          setRecommendations(recRes.data.recommendations || []);
        }
      } catch (err) {
        setError("Failed to load product details");
        console.error("Failed to load product data:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [slug]);

  const handleQuantityChange = (change) => {
    setQuantity(Math.max(1, quantity + change));
  };

  const handleAddToCart = async () => {
    const result = await addToCart(product.id, quantity);
    if (result.success) {
      alert("Added to cart successfully!");
    } else {
      alert(result.error);
    }
  };

  const handleToggleWishlist = async () => {
    if (!isAuthenticated) {
      alert("Please login to add to wishlist");
      return;
    }

    try {
      if (product.is_in_wishlist) {
        await wishlistAPI.removeFromWishlist(product.id);
        setProduct({ ...product, is_in_wishlist: false });
      } else {
        await wishlistAPI.addToWishlist(product.id);
        setProduct({ ...product, is_in_wishlist: true });
      }
    } catch (error) {
      console.error("Failed to update wishlist:", error);
    }
  };

  const handleReviewSubmit = async () => {
    if (!reviewForm.title.trim() || !reviewForm.comment.trim()) {
      alert("Please fill in all review fields");
      return;
    }

    setSubmittingReview(true);
    try {
      await reviewsAPI.createReview(slug, reviewForm);
      setReviewDialogOpen(false);
      setReviewForm({ rating: 5, title: "", comment: "" });
      // Reload reviews
      const reviewsRes = await reviewsAPI.getReviews(slug);
      setReviews(reviewsRes.data);
    } catch (error) {
      alert("Failed to submit review");
      console.error("Failed to submit review:", error);
    } finally {
      setSubmittingReview(false);
    }
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleImageSelect = (index) => {
    setSelectedImage(index);
  };

  if (loading) {
    return (
      <Container maxWidth="xl">
        <Box sx={{ mb: 4 }}>
          <Skeleton variant="text" height={60} width={400} />
          <Skeleton variant="text" height={40} width={300} />
        </Box>
        <Grid container spacing={4}>
          <Grid item xs={12} md={6}>
            <Skeleton variant="rectangular" height={400} />
            <Box sx={{ display: "flex", gap: 1, mt: 2 }}>
              {Array.from({ length: 4 }, (_, i) => (
                <Skeleton
                  key={`loading-skeleton-thumb-${i}`}
                  variant="rectangular"
                  width={80}
                  height={80}
                />
              ))}
            </Box>
          </Grid>
          <Grid item xs={12} md={6}>
            <Skeleton variant="text" height={40} />
            <Skeleton variant="text" height={30} width="60%" />
            <Skeleton variant="rectangular" height={100} sx={{ mt: 2 }} />
          </Grid>
        </Grid>
      </Container>
    );
  }

  if (error || !product) {
    return (
      <Container>
        <Alert severity="error">{error || "Product not found"}</Alert>
      </Container>
    );
  }

  const userReview = reviews.find((review) => review.user === user?.username);
  const productImages = product.images || [product.image];

  return (
    <Container maxWidth="xl">
      {/* Breadcrumbs */}
      <Breadcrumbs sx={{ mb: 3 }}>
        <Link to="/" style={{ textDecoration: "none", color: "inherit" }}>
          Home
        </Link>
        <Link
          to="/products"
          style={{ textDecoration: "none", color: "inherit" }}
        >
          Products
        </Link>
        <Typography color="text.primary">{product.name}</Typography>
      </Breadcrumbs>

      <Grid container spacing={6}>
        {/* Product Images and Gallery */}
        <Grid item xs={12} md={7}>
          <ScrollAnimation animation="fadeRight">
            <Box sx={{ position: "sticky", top: 100 }}>
              <Card
                sx={{
                  borderRadius: 4,
                  overflow: "hidden",
                  mb: 2,
                  boxShadow: "none",
                  border: "1px solid",
                  borderColor: "divider",
                  backgroundColor: "background.default",
                }}
              >
                <Box
                  sx={{
                    position: "relative",
                    pt: "75%",
                    backgroundColor: "white",
                  }}
                >
                  <motion.div
                    key={selectedImage}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.4 }}
                    style={{
                      position: "absolute",
                      top: 0,
                      left: 0,
                      width: "100%",
                      height: "100%",
                    }}
                  >
                    <Box
                      component="img"
                      src={productImages[selectedImage] || "/placeholder.png"}
                      alt={product.name}
                      sx={{
                        width: "100%",
                        height: "100%",
                        objectFit: "contain",
                        p: 4,
                      }}
                    />
                  </motion.div>
                  {product.discount_percentage > 0 && (
                    <Chip
                      label={`${product.discount_percentage}% OFF`}
                      color="error"
                      sx={{
                        position: "absolute",
                        top: 24,
                        left: 24,
                        fontWeight: 800,
                        height: 32,
                        borderRadius: 2,
                      }}
                    />
                  )}
                  {product.is_featured && (
                    <Chip
                      label="Featured"
                      color="secondary"
                      sx={{
                        position: "absolute",
                        top: 24,
                        right: 24,
                        fontWeight: 800,
                        height: 32,
                        borderRadius: 2,
                      }}
                    />
                  )}
                </Box>
              </Card>

              {/* Image Gallery */}
              {productImages.length > 1 && (
                <Box
                  sx={{
                    display: "flex",
                    gap: 2,
                    overflowX: "auto",
                    pb: 1,
                    "&::-webkit-scrollbar": { height: 6 },
                  }}
                >
                  {productImages.map((image, index) => (
                    <motion.div
                      key={`product-image-${index}-${image || "placeholder"}`}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      <Box
                        component="img"
                        src={image || "/placeholder.png"}
                        alt={`${product.name} ${index + 1}`}
                        sx={{
                          width: 100,
                          height: 100,
                          objectFit: "cover",
                          borderRadius: 3,
                          cursor: "pointer",
                          border: "2px solid",
                          borderColor:
                            selectedImage === index
                              ? "primary.main"
                              : "divider",
                          backgroundColor: "white",
                          p: 1,
                          opacity: selectedImage === index ? 1 : 0.7,
                          transition: "all 0.2s",
                          "&:hover": {
                            opacity: 1,
                            borderColor: "primary.light",
                          },
                        }}
                        onClick={() => handleImageSelect(index)}
                      />
                    </motion.div>
                  ))}
                </Box>
              )}
            </Box>
          </ScrollAnimation>
        </Grid>

        {/* Product Info */}
        <Grid item xs={12} md={5}>
          <ScrollAnimation animation="fadeLeft" delay={0.2}>
            <Box sx={{ position: "sticky", top: 100 }}>
              <Typography
                variant="h3"
                component="h1"
                gutterBottom
                sx={{
                  fontWeight: 800,
                  color: "text.primary",
                  fontSize: { xs: "2rem", md: "2.5rem" },
                  lineHeight: 1.2,
                }}
              >
                {product.name}
              </Typography>

              <Box
                sx={{ display: "flex", alignItems: "center", gap: 2, mb: 3 }}
              >
                <Box
                  sx={{
                    display: "flex",
                    alignItems: "center",
                    bgcolor: "warning.light",
                    px: 1,
                    py: 0.5,
                    borderRadius: 1,
                  }}
                >
                  <Star sx={{ color: "warning.main", fontSize: 20, mr: 0.5 }} />
                  <Typography fontWeight="700" color="warning.dark">
                    {product.average_rating?.toFixed(1) || 0}
                  </Typography>
                </Box>
                <Link to="#" style={{ textDecoration: "none" }}>
                  <Typography
                    variant="body1"
                    color="primary"
                    fontWeight="500"
                    sx={{ "&:hover": { textDecoration: "underline" } }}
                  >
                    {product.review_count} Reviews
                  </Typography>
                </Link>
                <Divider orientation="vertical" flexItem height={20} />
                <Typography variant="body1" color="text.secondary">
                  {product.category?.name}
                </Typography>
              </Box>

              <Box
                sx={{
                  display: "flex",
                  alignItems: "center",
                  flexWrap: "wrap",
                  gap: 1,
                  mb: 2,
                }}
              >
                  {product.is_instant_pack && (
                    <Chip
                      icon={<LocalShipping style={{ color: "#fff" }} />}
                      label="Instant Pack"
                      style={{
                        backgroundColor: "#9c27b0",
                        color: "#fff",
                        fontWeight: "bold",
                      }}
                    />
                  )}
                  {product.stock_quantity > 0 && product.stock_quantity <= 10 && (
                     <Chip
                        icon={<Warning style={{ color: "#fff" }} />}
                        label="Low Stock"
                        color="warning"
                        style={{ fontWeight: "bold" }}
                      />
                  )}
              </Box>

              <Box
                sx={{
                  mb: 4,
                  p: 3,
                  bgcolor: "background.paper",
                  borderRadius: 4,
                  border: "1px solid",
                  borderColor: "divider",
                }}
              >
                <Box
                  sx={{
                    display: "flex",
                    alignItems: "flex-end",
                    gap: 2,
                    mb: 1,
                  }}
                >
                  <Typography
                    variant="h3"
                    color="primary.main"
                    fontWeight="800"
                  >
                    ₹{product.price.toLocaleString()}
                  </Typography>
                  {product.mrp && product.mrp > product.price && (
                    <Typography
                      variant="h5"
                      sx={{
                        textDecoration: "line-through",
                        mb: 0.5,
                        opacity: 0.6,
                      }}
                      color="text.secondary"
                    >
                      ₹{product.mrp.toLocaleString()}
                    </Typography>
                  )}
                </Box>
                <Typography
                  variant="body2"
                  color="success.main"
                  fontWeight="600"
                >
                  Inclusive of all taxes
                </Typography>

                {product.bulk_price && product.bulk_min_quantity && (
                  <Box sx={{ mt: 2, p: 1.5, bgcolor: '#f0f9f0', borderRadius: 2, border: '1px dashed #2e7d32' }}>
                     <Typography variant="subtitle2" color="primary" fontWeight="bold">
                        Bulk Offer:
                     </Typography>
                     <Typography variant="body2" color="text.primary">
                        Buy {product.bulk_min_quantity}+ for <strong>₹{product.bulk_price}</strong> / unit
                     </Typography>
                  </Box>
                )}
              </Box>

              {/* Stock and Delivery Info */}
              <Grid container spacing={2} sx={{ mb: 4 }}>
                <Grid item xs={6}>
                  <Box
                    sx={{
                      p: 2,
                      bgcolor: "success.50",
                      borderRadius: 2,
                      height: "100%",
                    }}
                  >
                    <Box
                      sx={{
                        display: "flex",
                        alignItems: "center",
                        gap: 1,
                        mb: 1,
                      }}
                    >
                      <Verified color="success" />
                      <Typography
                        variant="subtitle2"
                        fontWeight="700"
                        color="success.dark"
                      >
                        Availability
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="success.dark">
                      {product.stock_quantity > 0
                        ? "In Stock & Ready to Ship"
                        : "Currently Out of Stock"}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box
                    sx={{
                      p: 2,
                      bgcolor: "info.50",
                      borderRadius: 2,
                      height: "100%",
                    }}
                  >
                    <Box
                      sx={{
                        display: "flex",
                        alignItems: "center",
                        gap: 1,
                        mb: 1,
                      }}
                    >
                      <LocalShipping color="info" />
                      <Typography
                        variant="subtitle2"
                        fontWeight="700"
                        color="info.dark"
                      >
                        Delivery
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="info.dark">
                      {product.is_instant_pack ? "Same Day Dispatch" : (product.delivery_time || "3-5 Business Days")}
                    </Typography>
                  </Box>
                </Grid>
              </Grid>

              {/* Quantity Selector */}
              <Box sx={{ mb: 4 }}>
                <Typography variant="subtitle2" fontWeight="700" gutterBottom>
                  Quantity
                </Typography>
                <Box sx={{ display: "flex", alignItems: "center", gap: 3 }}>
                  <Box
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      border: "1px solid",
                      borderColor: "divider",
                      borderRadius: 3,
                      bgcolor: "background.paper",
                    }}
                  >
                    <IconButton
                      onClick={() => handleQuantityChange(-1)}
                      disabled={quantity <= 1}
                      sx={{ p: 1.5 }}
                    >
                      <Remove fontSize="small" />
                    </IconButton>
                    <Typography
                      sx={{
                        px: 3,
                        fontWeight: "600",
                        minWidth: 40,
                        textAlign: "center",
                      }}
                    >
                      {quantity}
                    </Typography>
                    <IconButton
                      onClick={() => handleQuantityChange(1)}
                      sx={{ p: 1.5 }}
                    >
                      <Add fontSize="small" />
                    </IconButton>
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    {product.stock_quantity} units available
                  </Typography>
                </Box>
              </Box>

              {/* Action Buttons */}
              <Box
                sx={{ display: "flex", flexDirection: "column", gap: 2, mb: 4 }}
              >
                <Button
                  variant="contained"
                  size="large"
                  onClick={handleAddToCart}
                  disabled={!product.in_stock}
                  startIcon={<ShoppingCart />}
                  sx={{
                    borderRadius: 3,
                    py: 2,
                    fontSize: "1.1rem",
                    fontWeight: 700,
                    boxShadow: "0 8px 25px rgba(34, 197, 94, 0.25)",
                  }}
                >
                  Add to Cart
                </Button>
                <Box sx={{ display: "flex", gap: 2 }}>
                  <Button
                    variant="outlined"
                    size="large"
                    fullWidth
                    startIcon={
                      product.is_in_wishlist ? <Favorite /> : <FavoriteBorder />
                    }
                    onClick={handleToggleWishlist}
                    sx={{
                      borderRadius: 3,
                      py: 1.5,
                      borderWidth: 2,
                      "&:hover": { borderWidth: 2 },
                      color: product.is_in_wishlist ? "error.main" : "inherit",
                      borderColor: product.is_in_wishlist
                        ? "error.main"
                        : "inherit",
                    }}
                  >
                    Wishlist
                  </Button>
                  <Button
                    variant="outlined"
                    size="large"
                    fullWidth
                    startIcon={<Share />}
                    sx={{
                      borderRadius: 3,
                      py: 1.5,
                      borderWidth: 2,
                      "&:hover": { borderWidth: 2 },
                    }}
                  >
                    Share
                  </Button>
                </Box>
              </Box>

              {!product.in_stock && (
                <Alert severity="warning" sx={{ mb: 3, borderRadius: 2 }}>
                  This product is currently out of stock. Please check back
                  later or contact the vendor.
                </Alert>
              )}

              {/* Vendor Info */}
              <Paper
                sx={{
                  p: 3,
                  bgcolor: "background.paper",
                  borderRadius: 3,
                  border: "1px solid",
                  borderColor: "divider",
                }}
              >
                <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                  <Avatar
                    sx={{ bgcolor: "secondary.main", width: 48, height: 48 }}
                  >
                    {product.vendor?.name?.charAt(0) || "V"}
                  </Avatar>
                  <Box>
                    <Typography variant="subtitle1" fontWeight="700">
                      Sold by {product.vendor?.name}
                    </Typography>
                    <Box
                      sx={{ display: "flex", alignItems: "center", gap: 0.5 }}
                    >
                      <Verified fontSize="small" color="primary" />
                      <Typography
                        variant="caption"
                        color="text.secondary"
                        fontWeight="500"
                      >
                        Verified Vendor
                      </Typography>
                    </Box>
                  </Box>
                  <Button size="small" sx={{ ml: "auto" }}>
                    View Profile
                  </Button>
                </Box>
              </Paper>
            </Box>
          </ScrollAnimation>
        </Grid>
      </Grid>

      {/* Product Details Tabs */}
      <ScrollAnimation animation="fadeUp" delay={0.4}>
        <Box sx={{ mt: 6 }}>
          <Paper sx={{ borderRadius: 3 }}>
            <Tabs
              value={activeTab}
              onChange={handleTabChange}
              sx={{
                borderBottom: 1,
                borderColor: "divider",
                "& .MuiTab-root": {
                  fontWeight: 600,
                  fontSize: "1rem",
                  minHeight: 64,
                },
              }}
            >
              <Tab label="Description" />
              <Tab label="Specifications" />
              <Tab label="Usage & Safety" />
              <Tab label={`Reviews (${reviews.length})`} />
            </Tabs>

            {/* Tab Content */}
            {activeTab === 0 && (
              <Box sx={{ p: 4 }}>
                <Typography variant="h5" gutterBottom fontWeight="600">
                  Product Description
                </Typography>
                <Divider sx={{ mb: 3 }} />
                <Typography variant="body1" paragraph sx={{ lineHeight: 1.7 }}>
                  {product.description ||
                    "No detailed description available for this product."}
                </Typography>

                {product.features && product.features.length > 0 && (
                  <Box sx={{ mt: 4 }}>
                    <Typography variant="h6" gutterBottom fontWeight="600">
                      Key Features
                    </Typography>
                    <Box component="ul" sx={{ pl: 3 }}>
                      {product.features.map((feature, index) => (
                        <Typography
                          component="li"
                          key={`feature-${index}-${feature.substring(0, 10)}`}
                          variant="body1"
                          paragraph
                        >
                          {feature}
                        </Typography>
                      ))}
                    </Box>
                  </Box>
                )}
              </Box>
            )}

            {activeTab === 1 && (
              <Box sx={{ p: 4 }}>
                <Typography variant="h5" gutterBottom fontWeight="600">
                  Technical Specifications
                </Typography>
                <Divider sx={{ mb: 3 }} />

                {product.specifications &&
                Object.keys(product.specifications).length > 0 ? (
                  <TableContainer component={Paper} sx={{ borderRadius: 2 }}>
                    <Table>
                      <TableBody>
                        {Object.entries(product.specifications).map(
                          ([key, value]) => (
                            <TableRow key={key}>
                              <TableCell
                                component="th"
                                scope="row"
                                sx={{ fontWeight: 600, width: "30%" }}
                              >
                                {key}
                              </TableCell>
                              <TableCell>{value}</TableCell>
                            </TableRow>
                          ),
                        )}
                      </TableBody>
                    </Table>
                  </TableContainer>
                ) : (
                  <Typography variant="body1" color="text.secondary">
                    No specifications available for this product.
                  </Typography>
                )}
              </Box>
            )}

            {activeTab === 2 && (
              <Box sx={{ p: 4 }}>
                <Typography variant="h5" gutterBottom fontWeight="600">
                  Usage Instructions & Safety Guidelines
                </Typography>
                <Divider sx={{ mb: 3 }} />

                <Grid container spacing={4}>
                  {product.usage_instructions && (
                    <Grid item xs={12} md={6}>
                      <Accordion defaultExpanded>
                        <AccordionSummary expandIcon={<ExpandMore />}>
                          <Box
                            sx={{
                              display: "flex",
                              alignItems: "center",
                              gap: 1,
                            }}
                          >
                            <Agriculture color="primary" />
                            <Typography variant="h6">
                              Usage Instructions
                            </Typography>
                          </Box>
                        </AccordionSummary>
                        <AccordionDetails>
                          <Typography
                            variant="body1"
                            sx={{ whiteSpace: "pre-line" }}
                          >
                            {product.usage_instructions}
                          </Typography>
                        </AccordionDetails>
                      </Accordion>
                    </Grid>
                  )}

                  {product.safety_guidelines && (
                    <Grid item xs={12} md={6}>
                      <Accordion defaultExpanded>
                        <AccordionSummary expandIcon={<ExpandMore />}>
                          <Box
                            sx={{
                              display: "flex",
                              alignItems: "center",
                              gap: 1,
                            }}
                          >
                            <Warning color="error" />
                            <Typography variant="h6">
                              Safety Guidelines
                            </Typography>
                          </Box>
                        </AccordionSummary>
                        <AccordionDetails>
                          <Typography
                            variant="body1"
                            sx={{ whiteSpace: "pre-line" }}
                          >
                            {product.safety_guidelines}
                          </Typography>
                        </AccordionDetails>
                      </Accordion>
                    </Grid>
                  )}

                  {product.storage_instructions && (
                    <Grid item xs={12} md={6}>
                      <Accordion>
                        <AccordionSummary expandIcon={<ExpandMore />}>
                          <Box
                            sx={{
                              display: "flex",
                              alignItems: "center",
                              gap: 1,
                            }}
                          >
                            <Info color="info" />
                            <Typography variant="h6">
                              Storage Instructions
                            </Typography>
                          </Box>
                        </AccordionSummary>
                        <AccordionDetails>
                          <Typography
                            variant="body1"
                            sx={{ whiteSpace: "pre-line" }}
                          >
                            {product.storage_instructions}
                          </Typography>
                        </AccordionDetails>
                      </Accordion>
                    </Grid>
                  )}

                  {product.warranty_info && (
                    <Grid item xs={12} md={6}>
                      <Accordion>
                        <AccordionSummary expandIcon={<ExpandMore />}>
                          <Box
                            sx={{
                              display: "flex",
                              alignItems: "center",
                              gap: 1,
                            }}
                          >
                            <Verified color="success" />
                            <Typography variant="h6">
                              Warranty Information
                            </Typography>
                          </Box>
                        </AccordionSummary>
                        <AccordionDetails>
                          <Typography
                            variant="body1"
                            sx={{ whiteSpace: "pre-line" }}
                          >
                            {product.warranty_info}
                          </Typography>
                        </AccordionDetails>
                      </Accordion>
                    </Grid>
                  )}
                </Grid>
              </Box>
            )}

            {activeTab === 3 && (
              <Box sx={{ p: 4 }}>
                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    mb: 3,
                  }}
                >
                  <Typography variant="h5" fontWeight="600">
                    Customer Reviews ({reviews.length})
                  </Typography>
                  {isAuthenticated && !userReview && (
                    <Button
                      variant="contained"
                      onClick={() => setReviewDialogOpen(true)}
                      startIcon={<Star />}
                    >
                      Write a Review
                    </Button>
                  )}
                </Box>
                <Divider sx={{ mb: 3 }} />

                {reviews.length === 0 ? (
                  <Box sx={{ textAlign: "center", py: 4 }}>
                    <Typography
                      variant="h6"
                      color="text.secondary"
                      gutterBottom
                    >
                      No reviews yet
                    </Typography>
                    <Typography variant="body1" color="text.secondary">
                      Be the first to review this product!
                    </Typography>
                  </Box>
                ) : (
                  <Box>
                    {reviews.map((review) => (
                      <Card key={review.id} sx={{ mb: 2, borderRadius: 2 }}>
                        <CardContent>
                          <Box
                            sx={{
                              display: "flex",
                              alignItems: "flex-start",
                              gap: 2,
                            }}
                          >
                            <Avatar sx={{ width: 40, height: 40 }}>
                              {review.user?.charAt(0).toUpperCase()}
                            </Avatar>
                            <Box sx={{ flex: 1 }}>
                              <Box
                                sx={{
                                  display: "flex",
                                  alignItems: "center",
                                  gap: 1,
                                  mb: 1,
                                }}
                              >
                                <Typography
                                  variant="subtitle1"
                                  fontWeight="bold"
                                >
                                  {review.user}
                                </Typography>
                                <Rating
                                  value={review.rating}
                                  readOnly
                                  size="small"
                                />
                                {review.is_verified_purchase && (
                                  <Chip
                                    label="Verified Purchase"
                                    size="small"
                                    color="success"
                                  />
                                )}
                              </Box>
                              <Typography variant="h6" gutterBottom>
                                {review.title}
                              </Typography>
                              <Typography variant="body1" paragraph>
                                {review.comment}
                              </Typography>
                              <Typography
                                variant="body2"
                                color="text.secondary"
                              >
                                {new Date(
                                  review.created_at,
                                ).toLocaleDateString()}
                              </Typography>
                            </Box>
                          </Box>
                        </CardContent>
                      </Card>
                    ))}
                  </Box>
                )}
              </Box>
            )}
          </Paper>
        </Box>
      </ScrollAnimation>

      {/* Recommendations */}
      {recommendations.length > 0 && (
        <ScrollAnimation animation="fadeUp" delay={0.6}>
          <Box sx={{ mt: 6 }}>
            <Typography variant="h5" gutterBottom fontWeight="600">
              You might also like
            </Typography>
            <Grid container spacing={3}>
              {recommendations.slice(0, 4).map((rec, index) => (
                <Grid item xs={6} sm={3} key={rec.id}>
                  <ScrollAnimation animation="scale" delay={index * 0.1}>
                    <Card
                      component={Link}
                      to={`/products/${rec.slug}`}
                      sx={{
                        textDecoration: "none",
                        borderRadius: 2,
                        transition: "all 0.3s ease",
                        "&:hover": {
                          transform: "translateY(-4px)",
                          boxShadow: 4,
                        },
                      }}
                    >
                      <CardMedia
                        component="img"
                        height="150"
                        image={rec.image || "/placeholder.png"}
                        alt={rec.name}
                        sx={{ objectFit: "cover" }}
                      />
                      <CardContent>
                        <Typography variant="body2" noWrap fontWeight="500">
                          {rec.name}
                        </Typography>
                        <Typography
                          variant="body2"
                          color="primary"
                          fontWeight="bold"
                        >
                          Ã¢â€šÂ¹{rec.price}
                        </Typography>
                      </CardContent>
                    </Card>
                  </ScrollAnimation>
                </Grid>
              ))}
            </Grid>
          </Box>
        </ScrollAnimation>
      )}

      {/* Review Dialog */}
      <Dialog
        open={reviewDialogOpen}
        onClose={() => setReviewDialogOpen(false)}
        maxWidth="sm"
        fullWidth
        sx={{
          "& .MuiDialog-paper": {
            borderRadius: 3,
          },
        }}
      >
        <DialogTitle>Write a Review</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <Typography gutterBottom fontWeight="600">
              Rating
            </Typography>
            <Rating
              value={reviewForm.rating}
              onChange={(event, newValue) => {
                setReviewForm({ ...reviewForm, rating: newValue });
              }}
              size="large"
              sx={{ mb: 2 }}
            />

            <TextField
              fullWidth
              label="Review Title"
              value={reviewForm.title}
              onChange={(e) =>
                setReviewForm({ ...reviewForm, title: e.target.value })
              }
              sx={{ mb: 2 }}
            />

            <TextField
              fullWidth
              label="Your Review"
              multiline
              rows={4}
              value={reviewForm.comment}
              onChange={(e) =>
                setReviewForm({ ...reviewForm, comment: e.target.value })
              }
            />
          </Box>
        </DialogContent>
        <DialogActions sx={{ p: 3 }}>
          <Button onClick={() => setReviewDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleReviewSubmit}
            variant="contained"
            disabled={submittingReview}
            startIcon={<ThumbUp />}
          >
            {submittingReview ? "Submitting..." : "Submit Review"}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default ProductDetail;
