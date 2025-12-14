import React, { useState, useEffect, useCallback } from "react";
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
  Avatar,
  Divider,
  Paper,
  Tab,
  Tabs,
  Skeleton,
  Alert,
  IconButton,
  Tooltip,
} from "@mui/material";
import {
  LocationOn,
  Phone,
  Email,
  Verified,
  ShoppingBag,
  AccessTime,
  Language,
  ContactMail,
} from "@mui/icons-material";
import { productsAPI } from "../../services/api";

const VendorDetail = () => {
  const { slug } = useParams();
  const [vendor, setVendor] = useState(null);
  const [products, setProducts] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState(0);

  const loadVendorData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [vendorRes, productsRes, reviewsRes] = await Promise.all([
        productsAPI.getVendor(slug),
        productsAPI.getProducts({ vendor: slug, limit: 12 }),
        productsAPI.getVendorReviews(slug),
      ]);

      setVendor(vendorRes.data);
      setProducts(productsRes.data.results || productsRes.data);
      setReviews(reviewsRes.data || []);
    } catch (err) {
      setError("Failed to load vendor details");
      console.error("Failed to load vendor data:", err);
    } finally {
      setLoading(false);
    }
  }, [slug]);

  useEffect(() => {
    loadVendorData();
  }, [loadVendorData]);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  if (loading) {
    return (
      <Container maxWidth="xl">
        <Box sx={{ mb: 4 }}>
          <Skeleton
            variant="rectangular"
            height={300}
            sx={{ borderRadius: 2 }}
          />
        </Box>
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Skeleton variant="text" height={60} />
            <Skeleton variant="text" height={40} width="60%" />
            <Skeleton variant="rectangular" height={200} sx={{ mt: 2 }} />
          </Grid>
          <Grid item xs={12} md={4}>
            <Skeleton variant="rectangular" height={400} />
          </Grid>
        </Grid>
      </Container>
    );
  }

  if (error || !vendor) {
    return (
      <Container>
        <Alert severity="error">{error || "Vendor not found"}</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl">
      {/* Vendor Header */}
      <Paper
        elevation={2}
        sx={{
          mb: 4,
          background: "linear-gradient(135deg, #22c55e 0%, #16a34a 100%)",
          color: "white",
          borderRadius: 3,
          overflow: "hidden",
        }}
      >
        <Box sx={{ p: 4 }}>
          <Grid container spacing={4} alignItems="center">
            <Grid item xs={12} md={3}>
              <Box sx={{ textAlign: "center" }}>
                <Avatar
                  src={vendor.logo || "/placeholder-vendor.png"}
                  alt={vendor.name}
                  sx={{
                    width: 120,
                    height: 120,
                    mx: "auto",
                    mb: 2,
                    border: "4px solid white",
                    boxShadow: 3,
                  }}
                />
                {vendor.is_verified && (
                  <Box
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      gap: 1,
                    }}
                  >
                    <Verified sx={{ fontSize: 20 }} />
                    <Typography variant="body2" fontWeight="bold">
                      Verified Vendor
                    </Typography>
                  </Box>
                )}
              </Box>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography
                variant="h3"
                component="h1"
                fontWeight="bold"
                gutterBottom
              >
                {vendor.name}
              </Typography>
              <Typography variant="h6" sx={{ mb: 2, opacity: 0.9 }}>
                {vendor.tagline || "Quality Agricultural Solutions"}
              </Typography>

              {/* Rating and Stats */}
              <Box
                sx={{ display: "flex", alignItems: "center", gap: 2, mb: 2 }}
              >
                <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                  <Rating
                    value={vendor.average_rating || 0}
                    readOnly
                    precision={0.1}
                  />
                  <Typography variant="body1" fontWeight="bold">
                    {vendor.average_rating?.toFixed(1) || "N/A"}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.8 }}>
                    ({vendor.review_count || 0} reviews)
                  </Typography>
                </Box>
              </Box>

              {/* Location and Contact */}
              <Box sx={{ display: "flex", flexWrap: "wrap", gap: 2, mb: 2 }}>
                {vendor.location && (
                  <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                    <LocationOn sx={{ fontSize: 18 }} />
                    <Typography variant="body1">{vendor.location}</Typography>
                  </Box>
                )}
                {vendor.years_experience && (
                  <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                    <AccessTime sx={{ fontSize: 18 }} />
                    <Typography variant="body1">
                      {vendor.years_experience} years experience
                    </Typography>
                  </Box>
                )}
              </Box>

              {/* Specialties */}
              {vendor.specialties && vendor.specialties.length > 0 && (
                <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
                  {vendor.specialties.map((specialty) => (
                    <Chip
                      key={specialty}
                      label={specialty}
                      sx={{
                        backgroundColor: "rgba(255,255,255,0.2)",
                        color: "white",
                        border: "1px solid rgba(255,255,255,0.3)",
                      }}
                    />
                  ))}
                </Box>
              )}
            </Grid>
            <Grid item xs={12} md={3}>
              <Box sx={{ textAlign: { xs: "center", md: "right" } }}>
                <Button
                  variant="contained"
                  size="large"
                  component={Link}
                  to={`/products?vendor=${vendor.slug}`}
                  startIcon={<ShoppingBag />}
                  sx={{
                    backgroundColor: "white",
                    color: "primary.main",
                    mb: 2,
                    width: { xs: "100%", md: "auto" },
                    "&:hover": {
                      backgroundColor: "#f8fafc",
                    },
                  }}
                >
                  View Products ({vendor.product_count || 0})
                </Button>
                <Box
                  sx={{
                    display: "flex",
                    gap: 1,
                    justifyContent: { xs: "center", md: "flex-end" },
                  }}
                >
                  {vendor.phone && (
                    <Tooltip title="Call Vendor">
                      <IconButton
                        sx={{
                          backgroundColor: "rgba(255,255,255,0.2)",
                          color: "white",
                          "&:hover": {
                            backgroundColor: "rgba(255,255,255,0.3)",
                          },
                        }}
                      >
                        <Phone />
                      </IconButton>
                    </Tooltip>
                  )}
                  {vendor.email && (
                    <Tooltip title="Email Vendor">
                      <IconButton
                        sx={{
                          backgroundColor: "rgba(255,255,255,0.2)",
                          color: "white",
                          "&:hover": {
                            backgroundColor: "rgba(255,255,255,0.3)",
                          },
                        }}
                      >
                        <Email />
                      </IconButton>
                    </Tooltip>
                  )}
                  {vendor.website && (
                    <Tooltip title="Visit Website">
                      <IconButton
                        sx={{
                          backgroundColor: "rgba(255,255,255,0.2)",
                          color: "white",
                          "&:hover": {
                            backgroundColor: "rgba(255,255,255,0.3)",
                          },
                        }}
                      >
                        <Language />
                      </IconButton>
                    </Tooltip>
                  )}
                </Box>
              </Box>
            </Grid>
          </Grid>
        </Box>
      </Paper>

      {/* Content Tabs */}
      <Box sx={{ mb: 4 }}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          sx={{
            borderBottom: 1,
            borderColor: "divider",
            "& .MuiTab-root": {
              fontWeight: 600,
              fontSize: "1rem",
            },
          }}
        >
          <Tab label="About" />
          <Tab label={`Products (${products.length})`} />
          <Tab label={`Reviews (${reviews.length})`} />
        </Tabs>
      </Box>

      {/* Tab Content */}
      {activeTab === 0 && (
        <Grid container spacing={4}>
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h5" gutterBottom fontWeight="600">
                  About {vendor.name}
                </Typography>
                <Divider sx={{ mb: 3 }} />

                <Typography variant="body1" paragraph>
                  {vendor.description ||
                    "This vendor specializes in providing quality agricultural products and equipment to farmers and businesses across the region."}
                </Typography>

                {vendor.business_details && (
                  <Box sx={{ mb: 3 }}>
                    <Typography variant="h6" gutterBottom>
                      Business Details
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {vendor.business_details}
                    </Typography>
                  </Box>
                )}

                {/* Key Stats */}
                <Grid container spacing={3} sx={{ mt: 2 }}>
                  <Grid item xs={6} sm={3}>
                    <Box
                      sx={{
                        textAlign: "center",
                        p: 2,
                        backgroundColor: "grey.50",
                        borderRadius: 2,
                      }}
                    >
                      <Typography
                        variant="h4"
                        color="primary"
                        fontWeight="bold"
                      >
                        {vendor.product_count || 0}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Products
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Box
                      sx={{
                        textAlign: "center",
                        p: 2,
                        backgroundColor: "grey.50",
                        borderRadius: 2,
                      }}
                    >
                      <Typography
                        variant="h4"
                        color="success.main"
                        fontWeight="bold"
                      >
                        {vendor.customer_count || 0}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Customers
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Box
                      sx={{
                        textAlign: "center",
                        p: 2,
                        backgroundColor: "grey.50",
                        borderRadius: 2,
                      }}
                    >
                      <Typography
                        variant="h4"
                        color="warning.main"
                        fontWeight="bold"
                      >
                        {vendor.years_experience || 0}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Years Exp.
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Box
                      sx={{
                        textAlign: "center",
                        p: 2,
                        backgroundColor: "grey.50",
                        borderRadius: 2,
                      }}
                    >
                      <Typography
                        variant="h4"
                        color="info.main"
                        fontWeight="bold"
                      >
                        {vendor.average_rating?.toFixed(1) || "N/A"}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Rating
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Contact Information
                </Typography>
                <Divider sx={{ mb: 2 }} />

                {vendor.phone && (
                  <Box
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      gap: 2,
                      mb: 2,
                    }}
                  >
                    <Phone color="action" />
                    <Typography variant="body1">{vendor.phone}</Typography>
                  </Box>
                )}

                {vendor.email && (
                  <Box
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      gap: 2,
                      mb: 2,
                    }}
                  >
                    <Email color="action" />
                    <Typography variant="body1">{vendor.email}</Typography>
                  </Box>
                )}

                {vendor.website && (
                  <Box
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      gap: 2,
                      mb: 2,
                    }}
                  >
                    <Language color="action" />
                    <Typography variant="body1">
                      <Link
                        to={vendor.website}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        {vendor.website}
                      </Link>
                    </Typography>
                  </Box>
                )}

                {vendor.address && (
                  <Box
                    sx={{
                      display: "flex",
                      alignItems: "flex-start",
                      gap: 2,
                      mb: 2,
                    }}
                  >
                    <LocationOn color="action" sx={{ mt: 0.5 }} />
                    <Typography variant="body1">{vendor.address}</Typography>
                  </Box>
                )}

                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<ContactMail />}
                  sx={{ mt: 2 }}
                >
                  Request Quote
                </Button>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {activeTab === 1 && (
        <Box>
          <Typography variant="h5" gutterBottom>
            Products by {vendor.name}
          </Typography>
          {products.length === 0 ? (
            <Alert severity="info">
              No products available from this vendor yet.
            </Alert>
          ) : (
            <Grid container spacing={3}>
              {products.map((product) => (
                <Grid item xs={12} sm={6} md={4} lg={3} key={product.id}>
                  <Card
                    component={Link}
                    to={`/products/${product.slug}`}
                    sx={{
                      height: "100%",
                      textDecoration: "none",
                      transition: "all 0.3s ease",
                      "&:hover": {
                        transform: "translateY(-4px)",
                        boxShadow: 4,
                      },
                    }}
                  >
                    <CardMedia
                      component="img"
                      height="200"
                      image={product.image || "/placeholder.png"}
                      alt={product.name}
                      sx={{ objectFit: "cover" }}
                    />
                    <CardContent>
                      <Typography variant="h6" component="h3" gutterBottom>
                        {product.name}
                      </Typography>
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        gutterBottom
                      >
                        {product.category?.name}
                      </Typography>
                      <Typography variant="h6" color="primary">
                        Ã¢â€šÂ¹{product.price}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
        </Box>
      )}

      {activeTab === 2 && (
        <Box>
          <Typography variant="h5" gutterBottom>
            Customer Reviews
          </Typography>
          {reviews.length === 0 ? (
            <Alert severity="info">
              No reviews available for this vendor yet.
            </Alert>
          ) : (
            <Grid container spacing={3}>
              {reviews.map((review) => (
                <Grid item xs={12} md={6} key={review.id}>
                  <Card>
                    <CardContent>
                      <Box
                        sx={{
                          display: "flex",
                          alignItems: "center",
                          gap: 2,
                          mb: 2,
                        }}
                      >
                        <Avatar>{review.user?.charAt(0).toUpperCase()}</Avatar>
                        <Box>
                          <Typography variant="subtitle1" fontWeight="bold">
                            {review.user}
                          </Typography>
                          <Rating value={review.rating} readOnly size="small" />
                        </Box>
                      </Box>
                      <Typography variant="body1" paragraph>
                        {review.comment}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {new Date(review.created_at).toLocaleDateString()}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
        </Box>
      )}
    </Container>
  );
};

export default VendorDetail;
