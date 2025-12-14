import React, { useState, useEffect, lazy, Suspense } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import {
  Container, Typography, Grid, Card, CardContent, CardMedia, Button, Box, Chip, Rating, Divider,
  IconButton, Dialog, DialogTitle, DialogContent, DialogActions, Tab, Tabs, Paper, Skeleton, Avatar
} from '@mui/material';
import {
  Favorite, FavoriteBorder, Add, Remove, Share, LocalShipping, Verified, Star, ThumbUp, ExpandMore,
  ShoppingCart, ViewInAr, Fullscreen, FullscreenExit, CameraAlt, ZoomIn, ZoomOut
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useAuth } from '../../utils/AuthContext';
import { useCart } from '../../utils/CartContext';
import ScrollAnimation from '../common/ScrollAnimation';
import { fetchProductById, selectCurrentProduct, selectProductStatus } from '../../features/products/productSlice';
import LazyImage from '../common/LazyImage';

// Lazy load heavy components
const Product3DViewer = lazy(() => import('./Product3DViewer'));
const ProductRecommendations = lazy(() => import('./ProductRecommendations'));

const ProductDetailEnhanced = () => {
  const { slug } = useParams();
  const { isAuthenticated, user } = useAuth();
  const { addToCart } = useCart();
  const dispatch = useDispatch();

  const product = useSelector(selectCurrentProduct);
  const status = useSelector(selectProductStatus);
  const [quantity, setQuantity] = useState(1);
  const [reviewDialogOpen, setReviewDialogOpen] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const [selectedImage, setSelectedImage] = useState(0);
  const [is3DView, setIs3DView] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [reviewForm, setReviewForm] = useState({
    rating: 5,
    title: "",
    comment: "",
  });
  const [submittingReview, setSubmittingReview] = useState(false);
  const [reviews, setReviews] = useState([]);

  useEffect(() => {
    dispatch(fetchProductById(slug));
  }, [dispatch, slug]);

  const handleQuantityChange = (change) => {
    setQuantity(Math.max(1, quantity + change));
  };

  const handleAddToCart = async () => {
    const result = await addToCart(product?.id, quantity);
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
    // Implementation would go here
  };

  const handleReviewSubmit = async () => {
    if (!reviewForm.title.trim() || !reviewForm.comment.trim()) {
      alert("Please fill in all review fields");
      return;
    }

    setSubmittingReview(true);
    try {
      // API call would go here
      setReviewDialogOpen(false);
      setReviewForm({ rating: 5, title: "", comment: "" });
    } catch (error) {
      alert("Failed to submit review");
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

  const toggle3DView = () => {
    setIs3DView(!is3DView);
  };

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  if (status === 'loading' || !product) {
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

  if (status === 'failed') {
    return (
      <Container>
        <Typography variant="h6" color="error">Failed to load product details</Typography>
      </Container>
    );
  }

  const productImages = product.images || [product.image];
  const userReview = reviews.find((review) => review.user === user?.username);

  return (
    <Container maxWidth="xl">
      {/* Breadcrumbs */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Link to="/" style={{ textDecoration: "none", color: "inherit" }}>
            Home
          </Link>
          <Typography color="text.secondary">/</Typography>
          <Link to="/products" style={{ textDecoration: "none", color: "inherit" }}>
            Products
          </Link>
          <Typography color="text.secondary">/</Typography>
          <Typography color="text.primary">{product.name}</Typography>
        </Box>

        {/* 3D View Toggle */}
        {product.model_3d_url && (
          <Button
            variant="outlined"
            startIcon={<ViewInAr />}
            onClick={toggle3DView}
            sx={{
              borderRadius: 2,
              textTransform: 'none',
              fontWeight: 'bold'
            }}
          >
            {is3DView ? 'Switch to 2D View' : 'View in 3D'}
          </Button>
        )}
      </Box>

      <Grid container spacing={6}>
        {/* Product Images or 3D Viewer */}
        <Grid item xs={12} md={7}>
          <ScrollAnimation animation="fadeRight">
            <Box sx={{ position: "sticky", top: 100 }}>
              {is3DView && product.model_3d_url ? (
                <Suspense fallback={<Skeleton variant="rectangular" height={400} />}>
                  <Product3DViewer
                    modelUrl={product.model_3d_url}
                    productName={product.name}
                    productImage={product.image}
                    onArClick={() => alert('AR feature coming soon!')}
                    onFullscreenToggle={toggleFullscreen}
                    isFullscreen={isFullscreen}
                  />
                </Suspense>
              ) : (
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
                      <LazyImage
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
              )}

              {/* Image Gallery */}
              {!is3DView && productImages.length > 1 && (
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
                <Typography variant="body1" color="text.secondary">
                  {product.review_count} Reviews
                </Typography>
                <Divider orientation="vertical" flexItem height={20} />
                <Typography variant="body1" color="text.secondary">
                  {product.category?.name}
                </Typography>
              </Box>

              {/* Price and Stock Info */}
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
                    ₹{product.price?.toLocaleString()}
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
                      ₹{product.mrp?.toLocaleString()}
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
            </Box>
          </ScrollAnimation>
        </Grid>
      </Grid>

      {/* AI Recommendations */}
      <Suspense fallback={<Box sx={{ py: 4 }}><Skeleton variant="rectangular" height={300} /></Box>}>
        <ProductRecommendations userId={user?.id} productId={product.id} />
      </Suspense>

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
              <Tab label="Reviews" />
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
                  <Box component="dl" sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 2 }}>
                    {Object.entries(product.specifications).map(
                      ([key, value]) => (
                        <Box key={key} sx={{ mb: 2 }}>
                          <Typography component="dt" fontWeight="600" color="text.primary">
                            {key}:
                          </Typography>
                          <Typography component="dd" color="text.secondary" sx={{ ml: 0 }}>
                            {value}
                          </Typography>
                        </Box>
                      ),
                    )}
                  </Box>
                ) : (
                  <Typography variant="body1" color="text.secondary">
                    No specifications available for this product.
                  </Typography>
                )}
              </Box>
            )}

            {activeTab === 2 && (
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

export default ProductDetailEnhanced;