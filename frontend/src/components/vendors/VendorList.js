import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Box,
  Chip,
  Rating,
  Avatar,
  TextField,
  InputAdornment,
  Skeleton,
  Paper,
  Divider,
  IconButton,
  Tooltip,
} from "@mui/material";
import {
  Search,
  LocationOn,
  Phone,
  Verified,
  ShoppingBag,
} from "@mui/icons-material";
import { productsAPI } from "../../services/api";

const VendorList = () => {
  const [vendors, setVendors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [filteredVendors, setFilteredVendors] = useState([]);

  useEffect(() => {
    loadVendors();
  }, []);

  useEffect(() => {
    // Filter vendors based on search query
    const filtered = vendors.filter(
      (vendor) =>
        vendor.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        vendor.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        vendor.location?.toLowerCase().includes(searchQuery.toLowerCase()),
    );
    setFilteredVendors(filtered);
  }, [vendors, searchQuery]);

  const loadVendors = async () => {
    try {
      const response = await productsAPI.getVendors();
      setVendors(response.data);
      setFilteredVendors(response.data);
    } catch (error) {
      console.error("Failed to load vendors:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Container maxWidth="xl">
        <Box sx={{ mb: 4 }}>
          <Skeleton variant="text" height={60} width={300} />
          <Skeleton variant="rectangular" height={60} sx={{ mt: 2 }} />
        </Box>
        <Grid container spacing={3}>
          {["sk1", "sk2", "sk3", "sk4", "sk5", "sk6", "sk7", "sk8"].map(
            (skeletonId) => (
              <Grid item xs={12} sm={6} md={4} lg={3} key={skeletonId}>
                <Skeleton variant="rectangular" height={300} />
              </Grid>
            ),
          )}
        </Grid>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl">
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography
          variant="h4"
          component="h1"
          gutterBottom
          sx={{ fontWeight: 600, color: "text.primary" }}
        >
          Our Trusted Vendors
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
          Discover verified vendors offering quality agricultural equipment and
          supplies
        </Typography>

        {/* Search Bar */}
        <Paper
          elevation={1}
          sx={{
            p: 2,
            borderRadius: 2,
            backgroundColor: "background.paper",
          }}
        >
          <TextField
            fullWidth
            placeholder="Search vendors by name, location, or specialty..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search color="action" />
                </InputAdornment>
              ),
            }}
            sx={{ mb: 2 }}
          />

          <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
            <Chip
              label="All Vendors"
              variant="outlined"
              color="primary"
              sx={{ cursor: "pointer" }}
            />
            <Chip
              label="Equipment"
              variant="outlined"
              sx={{ cursor: "pointer" }}
            />
            <Chip label="Seeds" variant="outlined" sx={{ cursor: "pointer" }} />
            <Chip
              label="Fertilizers"
              variant="outlined"
              sx={{ cursor: "pointer" }}
            />
            <Chip label="Tools" variant="outlined" sx={{ cursor: "pointer" }} />
          </Box>
        </Paper>
      </Box>

      {/* Vendors Grid */}
      <Grid container spacing={3}>
        {filteredVendors.map((vendor) => (
          <Grid item xs={12} sm={6} md={4} lg={3} key={vendor.id}>
            <Card
              component={Link}
              to={`/vendors/${vendor.slug}`}
              sx={{
                height: "100%",
                display: "flex",
                flexDirection: "column",
                textDecoration: "none",
                transition: "all 0.3s ease",
                borderRadius: 2,
                overflow: "hidden",
                "&:hover": {
                  transform: "translateY(-4px)",
                  boxShadow: 6,
                },
              }}
            >
              {/* Vendor Header */}
              <Box
                sx={{
                  background:
                    "linear-gradient(135deg, #22c55e 0%, #16a34a 100%)",
                  p: 2,
                  color: "white",
                  textAlign: "center",
                }}
              >
                <Avatar
                  src={vendor.logo || "/placeholder-vendor.png"}
                  alt={vendor.name}
                  sx={{
                    width: 80,
                    height: 80,
                    mx: "auto",
                    mb: 1,
                    border: "3px solid white",
                  }}
                />
                <Typography variant="h6" fontWeight="bold">
                  {vendor.name}
                </Typography>
                {vendor.is_verified && (
                  <Box
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      gap: 0.5,
                      mt: 0.5,
                    }}
                  >
                    <Verified sx={{ fontSize: 16 }} />
                    <Typography variant="body2">Verified Vendor</Typography>
                  </Box>
                )}
              </Box>

              <CardContent sx={{ flexGrow: 1 }}>
                {/* Rating */}
                <Box
                  sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2 }}
                >
                  <Rating
                    value={vendor.average_rating || 0}
                    readOnly
                    size="small"
                    precision={0.1}
                  />
                  <Typography variant="body2" color="text.secondary">
                    ({vendor.review_count || 0} reviews)
                  </Typography>
                </Box>

                {/* Location */}
                {vendor.location && (
                  <Box
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      gap: 1,
                      mb: 1,
                    }}
                  >
                    <LocationOn
                      sx={{ fontSize: 16, color: "text.secondary" }}
                    />
                    <Typography variant="body2" color="text.secondary">
                      {vendor.location}
                    </Typography>
                  </Box>
                )}

                {/* Description */}
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{
                    mb: 2,
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    display: "-webkit-box",
                    WebkitLineClamp: 3,
                    WebkitBoxOrient: "vertical",
                  }}
                >
                  {vendor.description ||
                    "Specialized in quality agricultural products and equipment."}
                </Typography>

                {/* Specialties */}
                {vendor.specialties && vendor.specialties.length > 0 && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" fontWeight="600" gutterBottom>
                      Specialties:
                    </Typography>
                    <Box sx={{ display: "flex", gap: 0.5, flexWrap: "wrap" }}>
                      {vendor.specialties.slice(0, 3).map((specialty) => (
                        <Chip
                          key={`specialty-${specialty}`}
                          label={specialty}
                          size="small"
                          variant="outlined"
                          sx={{ fontSize: "0.7rem" }}
                        />
                      ))}
                      {vendor.specialties.length > 3 && (
                        <Chip
                          label={`+${vendor.specialties.length - 3} more`}
                          size="small"
                          variant="outlined"
                          sx={{ fontSize: "0.7rem" }}
                        />
                      )}
                    </Box>
                  </Box>
                )}

                {/* Stats */}
                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    mb: 2,
                  }}
                >
                  <Box sx={{ textAlign: "center" }}>
                    <Typography variant="h6" color="primary" fontWeight="bold">
                      {vendor.product_count || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Products
                    </Typography>
                  </Box>
                  <Box sx={{ textAlign: "center" }}>
                    <Typography
                      variant="h6"
                      color="success.main"
                      fontWeight="bold"
                    >
                      {vendor.years_experience || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Years Exp.
                    </Typography>
                  </Box>
                  <Box sx={{ textAlign: "center" }}>
                    <Typography
                      variant="h6"
                      color="warning.main"
                      fontWeight="bold"
                    >
                      {vendor.customer_count || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Customers
                    </Typography>
                  </Box>
                </Box>

                <Divider sx={{ mb: 2 }} />

                {/* Contact Actions */}
                <Box sx={{ display: "flex", gap: 1 }}>
                  <Button
                    variant="contained"
                    fullWidth
                    startIcon={<ShoppingBag />}
                    sx={{ borderRadius: 2 }}
                  >
                    View Products
                  </Button>
                  <Tooltip title="Contact Vendor">
                    <IconButton
                      sx={{
                        border: 1,
                        borderColor: "primary.main",
                        borderRadius: 2,
                        color: "primary.main",
                        "&:hover": {
                          backgroundColor: "primary.main",
                          color: "white",
                        },
                      }}
                    >
                      <Phone />
                    </IconButton>
                  </Tooltip>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {filteredVendors.length === 0 && (
        <Box sx={{ textAlign: "center", py: 8 }}>
          <Typography variant="h6" color="text.secondary">
            No vendors found matching your search.
          </Typography>
          <Button
            variant="outlined"
            onClick={() => setSearchQuery("")}
            sx={{ mt: 2 }}
          >
            Clear Search
          </Button>
        </Box>
      )}

      {/* Call to Action */}
      <Paper
        elevation={2}
        sx={{
          mt: 6,
          p: 4,
          background: "linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)",
          borderRadius: 2,
          textAlign: "center",
        }}
      >
        <Typography variant="h5" gutterBottom fontWeight="600">
          Become a Vendor
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
          Join our network of trusted agricultural suppliers and reach more
          customers
        </Typography>
        <Button
          variant="contained"
          size="large"
          component={Link}
          to="/vendor-register"
          sx={{ borderRadius: 2 }}
        >
          Register as Vendor
        </Button>
      </Paper>
    </Container>
  );
};

export default VendorList;
