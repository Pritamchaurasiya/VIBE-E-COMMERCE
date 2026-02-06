import React, { useState, useEffect } from "react";
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
  Paper,
  Avatar,
  Rating,
  Skeleton,
  InputBase,
  IconButton,
  TextField,
} from "@mui/material";
import {
  Agriculture,
  ShoppingCart,
  LocalShipping,
  VerifiedUser,
  TrendingUp,
  Star,
  Search,
  Favorite,
  FavoriteBorder,
  Email,
  ArrowForward,
} from "@mui/icons-material";
import { productsAPI, wishlistAPI } from "../../services/api";
import { useAuth } from "../../utils/AuthContext";
import { useCart } from "../../utils/CartContext";
import ScrollAnimation from "./ScrollAnimation";
import { motion } from "framer-motion";

const HomePage = () => {
  const [featuredProducts, setFeaturedProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const { addToCart } = useCart();

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchTerm.trim()) {
      navigate(`/products?q=${encodeURIComponent(searchTerm)}`);
    }
  };

  const handleAddToCart = async (productId, event) => {
    event.preventDefault();
    event.stopPropagation();
    const result = await addToCart(productId);
    if (result.success) {
      // Could show a snackbar or toast here
      console.log("Added to cart successfully");
    } else {
      alert(result.error);
    }
  };

  const handleToggleWishlist = async (productId, isInWishlist, event) => {
    event.preventDefault();
    event.stopPropagation();
    if (!isAuthenticated) {
      alert("Please login to add to wishlist");
      return;
    }

    try {
      if (isInWishlist) {
        await wishlistAPI.removeFromWishlist(productId);
      } else {
        await wishlistAPI.addToWishlist(productId);
      }
      // Update the product in state
      setFeaturedProducts((products) =>
        products.map((p) =>
          p.id === productId ? { ...p, is_in_wishlist: !isInWishlist } : p,
        ),
      );
    } catch (error) {
      console.error("Failed to update wishlist:", error);
    }
  };

  useEffect(() => {
    loadHomePageData();
  }, []);

  const loadHomePageData = async () => {
    try {
      const [productsResponse, categoriesResponse] = await Promise.all([
        productsAPI.getProducts({ limit: 8 }),
        productsAPI.getCategories(),
      ]);

      setFeaturedProducts(
        productsResponse.data.results || productsResponse.data,
      );
      setCategories(categoriesResponse.data);
    } catch (error) {
      console.error("Failed to load home page data:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Container>
        <Box sx={{ mb: 4 }}>
          <Skeleton
            variant="rectangular"
            height={400}
            sx={{ borderRadius: 2 }}
          />
        </Box>
        <Grid container spacing={2}>
          {Array.from({ length: 6 }, (_, i) => (
            <Grid item xs={6} sm={4} md={2} key={`skeleton-category-${i}`}>
              <Skeleton variant="rectangular" height={60} />
            </Grid>
          ))}
        </Grid>
        <Box sx={{ mt: 6 }}>
          <Skeleton variant="text" height={40} width={300} />
          <Grid container spacing={3} sx={{ mt: 2 }}>
            {Array.from({ length: 8 }, (_, i) => (
              <Grid
                item
                xs={12}
                sm={6}
                md={4}
                lg={3}
                key={`skeleton-product-${i}`}
              >
                <Skeleton variant="rectangular" height={300} />
              </Grid>
            ))}
          </Grid>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl">
      {/* Hero Section */}
      <ScrollAnimation animation="fadeUp" duration={0.8}>
        <Paper
          elevation={0}
          sx={{
            background: "linear-gradient(120deg, #10b981 0%, #059669 100%)",
            color: "white",
            py: { xs: 8, md: 12 },
            px: { xs: 3, md: 8 },
            mb: 8,
            borderRadius: { xs: 3, md: 5 },
            position: "relative",
            overflow: "hidden",
            boxShadow: "0 20px 40px -10px rgba(16, 185, 129, 0.4)",
            "&::before": {
              content: '""',
              position: "absolute",
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background:
                'url("/static/images/hero-bg.jpg") center/cover no-repeat',
              opacity: 0.15,
              mixBlendMode: "overlay",
            },
            "&::after": {
              content: '""',
              position: "absolute",
              width: "400px",
              height: "400px",
              background:
                "radial-gradient(circle, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0) 70%)",
              top: "-100px",
              right: "-100px",
              borderRadius: "50%",
            },
          }}
        >
          <Box
            sx={{
              position: "relative",
              zIndex: 1,
              textAlign: { xs: "center", md: "left" },
            }}
          >
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
            >
              <Typography
                variant="h1"
                component="h1"
                sx={{
                  fontWeight: 800,
                  mb: 3,
                  fontSize: { xs: "2.5rem", md: "4.5rem" },
                  lineHeight: 1.1,
                  letterSpacing: "-0.02em",
                  background: "linear-gradient(to right, #ffffff, #e0f2f1)",
                  backgroundClip: "text",
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent",
                  textShadow: "0 4px 20px rgba(0,0,0,0.1)",
                }}
              >
                Grow Your Farm with{" "}
                <br sx={{ display: { xs: "none", md: "block" } }} />
                Quality Equipment
              </Typography>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
            >
              <Typography
                variant="h5"
                sx={{
                  mb: 5,
                  opacity: 0.95,
                  fontWeight: 400,
                  maxWidth: 650,
                  mx: { xs: "auto", md: 0 },
                  fontSize: { xs: "1.1rem", md: "1.35rem" },
                  lineHeight: 1.6,
                }}
              >
                Discover premium farming equipment, seeds, and supplies from
                trusted vendors. Boost your agricultural productivity with
                VIBE's B2B marketplace.
              </Typography>

              <Paper
                component="form"
                onSubmit={handleSearch}
                sx={{
                  p: "4px",
                  display: "flex",
                  alignItems: "center",
                  width: "100%",
                  maxWidth: 500,
                  mb: 5,
                  mx: { xs: "auto", md: 0 },
                  borderRadius: 3,
                  boxShadow: "0 8px 30px rgba(0,0,0,0.15)",
                  background: "rgba(255,255,255,0.95)",
                  backdropFilter: "blur(10px)",
                }}
              >
                <InputBase
                  sx={{ ml: 2, flex: 1, fontSize: "1.1rem" }}
                  placeholder="What are you looking for?"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  inputProps={{ "aria-label": "Search products" }}
                />
                <IconButton
                  type="submit"
                  sx={{
                    p: "12px",
                    bgcolor: "primary.main",
                    color: "white",
                    borderRadius: 2,
                    "&:hover": { bgcolor: "primary.dark" },
                  }}
                  aria-label="search"
                >
                  <Search />
                </IconButton>
              </Paper>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.6 }}
            >
              <Box
                sx={{
                  display: "flex",
                  gap: 2,
                  flexWrap: "wrap",
                  justifyContent: { xs: "center", md: "flex-start" },
                }}
              >
                <Button
                  variant="contained"
                  size="large"
                  component={Link}
                  to="/products"
                  startIcon={<ShoppingCart />}
                  sx={{
                    backgroundColor: "white",
                    color: "primary.dark",
                    px: 4,
                    py: 1.8,
                    borderRadius: 3,
                    fontWeight: 700,
                    fontSize: "1.1rem",
                    boxShadow: "0 4px 14px 0 rgba(0,0,0,0.1)",
                    "&:hover": {
                      backgroundColor: "#f8fafc",
                      transform: "translateY(-2px)",
                      boxShadow: "0 6px 20px rgba(0,0,0,0.15)",
                    },
                    transition: "all 0.3s ease",
                  }}
                >
                  Shop Now
                </Button>
                <Button
                  variant="outlined"
                  size="large"
                  component={Link}
                  to="/vendors"
                  startIcon={<VerifiedUser />}
                  sx={{
                    borderColor: "rgba(255,255,255,0.5)",
                    color: "white",
                    px: 4,
                    py: 1.8,
                    borderRadius: 3,
                    fontWeight: 700,
                    fontSize: "1.1rem",
                    borderWidth: 2,
                    "&:hover": {
                      borderColor: "white",
                      backgroundColor: "rgba(255,255,255,0.1)",
                      borderWidth: 2,
                      transform: "translateY(-2px)",
                    },
                    transition: "all 0.3s ease",
                  }}
                >
                  Find Vendors
                </Button>
              </Box>
            </motion.div>
          </Box>

          {/* Floating Stats */}
          <Box
            sx={{
              position: "absolute",
              top: "50%",
              right: 60,
              transform: "translateY(-50%)",
              display: { xs: "none", lg: "flex" },
              flexDirection: "column",
              gap: 3,
            }}
          >
            <motion.div
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.8 }}
            >
              <Paper
                elevation={3}
                sx={{
                  p: 2,
                  backgroundColor: "rgba(255,255,255,0.9)",
                  borderRadius: 2,
                  minWidth: 120,
                }}
              >
                <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                  <TrendingUp color="primary" />
                  <Box>
                    <Typography variant="h6" color="primary" fontWeight="bold">
                      10,000+
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Products
                    </Typography>
                  </Box>
                </Box>
              </Paper>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 1 }}
            >
              <Paper
                elevation={3}
                sx={{
                  p: 2,
                  backgroundColor: "rgba(255,255,255,0.9)",
                  borderRadius: 2,
                  minWidth: 120,
                }}
              >
                <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                  <VerifiedUser color="success" />
                  <Box>
                    <Typography
                      variant="h6"
                      color="success.main"
                      fontWeight="bold"
                    >
                      500+
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Vendors
                    </Typography>
                  </Box>
                </Box>
              </Paper>
            </motion.div>
          </Box>
        </Paper>
      </ScrollAnimation>

      {/* Categories Section */}
      <ScrollAnimation animation="fadeUp" delay={0.2}>
        <Box sx={{ mb: 8 }}>
          <Typography
            variant="h4"
            component="h2"
            gutterBottom
            sx={{
              textAlign: "center",
              mb: 4,
              fontWeight: 600,
              color: "text.primary",
            }}
          >
            Shop by Category
          </Typography>
          <Grid container spacing={3}>
            {categories.slice(0, 6).map((category, index) => (
              <Grid item xs={6} sm={4} md={2} key={category.id}>
                <ScrollAnimation animation="scale" delay={index * 0.1}>
                  <Card
                    component={Link}
                    to={`/products?category=${category.slug}`}
                    sx={{
                      textDecoration: "none",
                      transition: "all 0.3s ease",
                      "&:hover": {
                        transform: "translateY(-4px)",
                        boxShadow: 4,
                      },
                      borderRadius: 2,
                      textAlign: "center",
                      py: 3,
                    }}
                  >
                    <CardContent>
                      <Avatar
                        sx={{
                          width: 60,
                          height: 60,
                          mx: "auto",
                          mb: 2,
                          backgroundColor: "primary.main",
                        }}
                      >
                        <Agriculture />
                      </Avatar>
                      <Typography variant="h6" color="primary" fontWeight="600">
                        {category.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Quality products
                      </Typography>
                    </CardContent>
                  </Card>
                </ScrollAnimation>
              </Grid>
            ))}
          </Grid>
        </Box>
      </ScrollAnimation>

      {/* Featured Products */}
      <ScrollAnimation animation="fadeUp" delay={0.4}>
        <Box>
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              mb: 4,
            }}
          >
            <Typography variant="h4" component="h2" fontWeight="600">
              Featured Products
            </Typography>
            <Button
              component={Link}
              to="/products"
              variant="outlined"
              endIcon={<ShoppingCart />}
            >
              View All
            </Button>
          </Box>
          <Grid container spacing={3}>
            {featuredProducts.map((product, index) => (
              <Grid item xs={12} sm={6} md={4} lg={3} key={product.id}>
                <ScrollAnimation animation="fadeUp" delay={index * 0.1}>
                  <Card
                    component={Link}
                    to={`/products/${product.slug}`}
                    sx={{
                      height: "100%",
                      display: "flex",
                      flexDirection: "column",
                      textDecoration: "none",
                      transition: "all 0.3s ease",
                      borderRadius: 2,
                      overflow: "hidden",
                      "&:hover": {
                        transform: "translateY(-8px)",
                        boxShadow: 6,
                      },
                    }}
                  >
                    <Box sx={{ position: "relative" }}>
                      <CardMedia
                        component="img"
                        height="220"
                        image={product.image || "/placeholder.png"}
                        alt={product.name}
                        sx={{
                          objectFit: "cover",
                          transition: "transform 0.3s ease",
                          "&:hover": {
                            transform: "scale(1.05)",
                          },
                        }}
                      />
                      {product.discount_percentage > 0 && (
                        <Chip
                          label={`${product.discount_percentage}% OFF`}
                          color="error"
                          size="small"
                          sx={{
                            position: "absolute",
                            top: 8,
                            left: 8,
                            fontWeight: "bold",
                          }}
                        />
                      )}
                      {isAuthenticated && (
                        <IconButton
                          onClick={(e) =>
                            handleToggleWishlist(
                              product.id,
                              product.is_in_wishlist,
                              e,
                            )
                          }
                          sx={{
                            position: "absolute",
                            top: 8,
                            right: 8,
                            backgroundColor: "rgba(255,255,255,0.9)",
                            backdropFilter: "blur(4px)",
                            "&:hover": {
                              backgroundColor: "white",
                              transform: "scale(1.1)",
                              color: "error.main",
                            },
                            transition: "all 0.2s ease",
                          }}
                          size="small"
                          aria-label={
                            product.is_in_wishlist
                              ? "Remove from wishlist"
                              : "Add to wishlist"
                          }
                        >
                          {product.is_in_wishlist ? (
                            <Favorite color="error" fontSize="small" />
                          ) : (
                            <FavoriteBorder fontSize="small" />
                          )}
                        </IconButton>
                      )}
                      <Box
                        sx={{
                          position: "absolute",
                          top: 8,
                          right: isAuthenticated ? 50 : 8,
                          display: "flex",
                          alignItems: "center",
                          backgroundColor: "rgba(255,255,255,0.9)",
                          borderRadius: 1,
                          px: 1,
                          py: 0.5,
                        }}
                      >
                        <Star sx={{ color: "#ffc107", fontSize: 16 }} />
                        <Typography
                          variant="body2"
                          sx={{ ml: 0.5, fontWeight: "bold" }}
                        >
                          {product.average_rating?.toFixed(1) || "N/A"}
                        </Typography>
                      </Box>
                    </Box>
                    <CardContent
                      sx={{
                        flexGrow: 1,
                        display: "flex",
                        flexDirection: "column",
                      }}
                    >
                      <Typography
                        variant="h6"
                        component="h3"
                        gutterBottom
                        sx={{
                          fontWeight: 600,
                          overflow: "hidden",
                          textOverflow: "ellipsis",
                          display: "-webkit-box",
                          WebkitLineClamp: 2,
                          WebkitBoxOrient: "vertical",
                        }}
                      >
                        {product.name}
                      </Typography>
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        gutterBottom
                      >
                        {product.category?.name} Ã¢â‚¬Â¢ {product.vendor?.name}
                      </Typography>
                      <Box
                        sx={{
                          display: "flex",
                          alignItems: "center",
                          gap: 1,
                          mb: 2,
                          mt: "auto",
                        }}
                      >
                        <Typography
                          variant="h6"
                          color="primary"
                          fontWeight="bold"
                        >
                          Ã¢â€šÂ¹{product.price}
                        </Typography>
                        {product.mrp && product.mrp > product.price && (
                          <Typography
                            variant="body2"
                            sx={{ textDecoration: "line-through" }}
                            color="text.secondary"
                          >
                            Ã¢â€šÂ¹{product.mrp}
                          </Typography>
                        )}
                        {product.discount_percentage > 0 && (
                          <Chip
                            label={`${product.discount_percentage}% off`}
                            color="success"
                            size="small"
                            variant="outlined"
                          />
                        )}
                      </Box>
                      <Box
                        sx={{
                          display: "flex",
                          alignItems: "center",
                          gap: 1,
                          mb: 2,
                        }}
                      >
                        <Rating
                          value={product.average_rating || 0}
                          readOnly
                          size="small"
                          precision={0.1}
                        />
                        <Typography variant="body2" color="text.secondary">
                          ({product.review_count || 0})
                        </Typography>
                      </Box>
                      <Button
                        variant="contained"
                        fullWidth
                        startIcon={<ShoppingCart />}
                        onClick={(e) => handleAddToCart(product.id, e)}
                        disabled={!product.in_stock}
                        sx={{
                          mt: "auto",
                          borderRadius: 2,
                          "&:hover": {
                            transform: "scale(1.02)",
                          },
                        }}
                      >
                        Add to Cart
                      </Button>
                    </CardContent>
                  </Card>
                </ScrollAnimation>
              </Grid>
            ))}
          </Grid>
        </Box>
      </ScrollAnimation>

      {/* Trust Indicators */}
      <ScrollAnimation animation="fadeUp" delay={0.6}>
        <Box sx={{ mt: 8, py: 4, backgroundColor: "grey.50", borderRadius: 2 }}>
          <Container maxWidth="md">
            <Typography
              variant="h5"
              align="center"
              gutterBottom
              fontWeight="600"
            >
              Why Choose VIBE E-Commerce?
            </Typography>
            <Grid container spacing={4} sx={{ mt: 2 }}>
              <Grid item xs={12} md={4}>
                <ScrollAnimation animation="scale" delay={0.1}>
                  <Box sx={{ textAlign: "center" }}>
                    <VerifiedUser
                      sx={{ fontSize: 48, color: "success.main", mb: 2 }}
                    />
                    <Typography variant="h6" gutterBottom>
                      Verified Vendors
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      All vendors are thoroughly vetted and verified for quality
                      assurance
                    </Typography>
                  </Box>
                </ScrollAnimation>
              </Grid>
              <Grid item xs={12} md={4}>
                <ScrollAnimation animation="scale" delay={0.2}>
                  <Box sx={{ textAlign: "center" }}>
                    <LocalShipping
                      sx={{ fontSize: 48, color: "primary.main", mb: 2 }}
                    />
                    <Typography variant="h6" gutterBottom>
                      Fast Delivery
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Quick and reliable shipping across agricultural regions
                    </Typography>
                  </Box>
                </ScrollAnimation>
              </Grid>
              <Grid item xs={12} md={4}>
                <ScrollAnimation animation="scale" delay={0.3}>
                  <Box sx={{ textAlign: "center" }}>
                    <TrendingUp
                      sx={{ fontSize: 48, color: "warning.main", mb: 2 }}
                    />
                    <Typography variant="h6" gutterBottom>
                      Best Prices
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Competitive pricing with special B2B discounts
                    </Typography>
                  </Box>
                </ScrollAnimation>
              </Grid>
            </Grid>
          </Container>
        </Box>
      </ScrollAnimation>

      {/* Interactive Features Showcase */}
      <ScrollAnimation animation="fadeUp" delay={0.8}>
        <Box sx={{ mt: 8, mb: 6 }}>
          <Typography
            variant="h4"
            component="h2"
            align="center"
            gutterBottom
            sx={{ fontWeight: 600, mb: 4 }}
          >
            Platform Features
          </Typography>
          <Grid container spacing={4}>
            {[
              {
                title: "Smart Search",
                description: "AI-powered search finds exactly what you need",
                icon: <Search sx={{ fontSize: 40, color: "primary.main" }} />,
                animation: "bounce",
              },
              {
                title: "Bulk Ordering",
                description: "Special pricing for large agricultural orders",
                icon: (
                  <ShoppingCart sx={{ fontSize: 40, color: "success.main" }} />
                ),
                animation: "elastic",
              },
              {
                title: "Vendor Verification",
                description: "All vendors are verified for quality assurance",
                icon: (
                  <VerifiedUser sx={{ fontSize: 40, color: "warning.main" }} />
                ),
                animation: "scale",
              },
              {
                title: "Real-time Tracking",
                description: "Track your orders from farm to delivery",
                icon: (
                  <LocalShipping sx={{ fontSize: 40, color: "info.main" }} />
                ),
                animation: "rotate",
              },
            ].map((feature, index) => (
              <Grid item xs={12} sm={6} md={3} key={feature.title}>
                <ScrollAnimation
                  animation={feature.animation}
                  delay={index * 0.2}
                >
                  <Card
                    sx={{
                      height: "100%",
                      textAlign: "center",
                      p: 3,
                      cursor: "pointer",
                      transition: "all 0.3s ease",
                      "&:hover": {
                        transform: "translateY(-8px)",
                        boxShadow: 6,
                        "& .feature-icon": {
                          transform: "scale(1.2) rotate(5deg)",
                        },
                      },
                    }}
                  >
                    <Box
                      className="feature-icon"
                      sx={{
                        mb: 2,
                        transition: "transform 0.3s ease",
                        display: "inline-block",
                      }}
                    >
                      {feature.icon}
                    </Box>
                    <Typography variant="h6" gutterBottom fontWeight="600">
                      {feature.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {feature.description}
                    </Typography>
                  </Card>
                </ScrollAnimation>
              </Grid>
            ))}
          </Grid>
        </Box>
      </ScrollAnimation>

      {/* Newsletter Signup */}
      <ScrollAnimation animation="fadeUp" delay={1}>
        <Paper
          elevation={3}
          sx={{
            mt: 8,
            p: 4,
            background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            color: "white",
            borderRadius: 3,
            textAlign: "center",
          }}
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6 }}
          >
            <Email sx={{ fontSize: 48, mb: 2, opacity: 0.9 }} />
            <Typography variant="h4" gutterBottom fontWeight="bold">
              Stay Updated
            </Typography>
            <Typography variant="body1" sx={{ mb: 3, opacity: 0.9 }}>
              Get the latest agricultural trends, product updates, and exclusive
              offers delivered to your inbox.
            </Typography>
            <Box
              component="form"
              sx={{
                display: "flex",
                gap: 2,
                maxWidth: 500,
                mx: "auto",
                flexDirection: { xs: "column", sm: "row" },
              }}
            >
              <TextField
                fullWidth
                placeholder="Enter your email address"
                variant="outlined"
                inputProps={{ "aria-label": "Email address" }}
                sx={{
                  "& .MuiOutlinedInput-root": {
                    backgroundColor: "rgba(255,255,255,0.1)",
                    backdropFilter: "blur(10px)",
                    borderRadius: 2,
                    "& fieldset": {
                      borderColor: "rgba(255,255,255,0.3)",
                    },
                    "&:hover fieldset": {
                      borderColor: "rgba(255,255,255,0.5)",
                    },
                    "&.Mui-focused fieldset": {
                      borderColor: "white",
                    },
                  },
                  "& .MuiOutlinedInput-input": {
                    color: "white",
                    "&::placeholder": {
                      color: "rgba(255,255,255,0.7)",
                      opacity: 1,
                    },
                  },
                }}
              />
              <Button
                variant="contained"
                size="large"
                sx={{
                  backgroundColor: "white",
                  color: "primary.main",
                  px: 4,
                  borderRadius: 2,
                  fontWeight: 600,
                  "&:hover": {
                    backgroundColor: "#f8fafc",
                    transform: "translateY(-2px)",
                  },
                  transition: "all 0.3s ease",
                  minWidth: { xs: "100%", sm: "auto" },
                }}
                endIcon={<ArrowForward />}
              >
                Subscribe
              </Button>
            </Box>
          </motion.div>
        </Paper>
      </ScrollAnimation>

      {/* Animated Statistics */}
      <ScrollAnimation animation="fadeUp" delay={1.2}>
        <Box
          sx={{
            mt: 8,
            py: 6,
            backgroundColor: "primary.main",
            color: "white",
            borderRadius: 3,
          }}
        >
          <Container maxWidth="md">
            <Typography
              variant="h4"
              align="center"
              gutterBottom
              fontWeight="bold"
            >
              VIBE by Numbers
            </Typography>
            <Typography
              variant="body1"
              align="center"
              sx={{ mb: 4, opacity: 0.9 }}
            >
              Growing the agricultural community together
            </Typography>
            <Grid container spacing={4}>
              {[
                {
                  number: "10,000+",
                  label: "Products Available",
                  icon: <ShoppingCart />,
                },
                {
                  number: "500+",
                  label: "Verified Vendors",
                  icon: <VerifiedUser />,
                },
                {
                  number: "50,000+",
                  label: "Happy Farmers",
                  icon: <Agriculture />,
                },
                { number: "98%", label: "Satisfaction Rate", icon: <Star /> },
              ].map((stat, index) => (
                <Grid item xs={6} md={3} key={stat.label}>
                  <ScrollAnimation animation="scale" delay={index * 0.2}>
                    <Box sx={{ textAlign: "center" }}>
                      <motion.div
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{
                          type: "spring",
                          stiffness: 260,
                          damping: 20,
                          delay: index * 0.2 + 0.5,
                        }}
                      >
                        <Box
                          sx={{ fontSize: 48, mb: 1, color: "secondary.main" }}
                        >
                          {stat.icon}
                        </Box>
                        <Typography
                          variant="h3"
                          fontWeight="bold"
                          sx={{
                            background:
                              "linear-gradient(45deg, #ffffff 0%, #e0f2fe 100%)",
                            backgroundClip: "text",
                            WebkitBackgroundClip: "text",
                            WebkitTextFillColor: "transparent",
                            mb: 1,
                          }}
                        >
                          {stat.number}
                        </Typography>
                      </motion.div>
                      <Typography variant="body1" fontWeight="500">
                        {stat.label}
                      </Typography>
                    </Box>
                  </ScrollAnimation>
                </Grid>
              ))}
            </Grid>
          </Container>
        </Box>
      </ScrollAnimation>
    </Container>
  );
};

export default HomePage;
