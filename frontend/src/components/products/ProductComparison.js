import React, { useState, useEffect, useCallback } from "react";
import { useSearchParams, Link } from "react-router-dom";
import {
  Container,
  Typography,
  Card,
  CardContent,
  CardMedia,
  Button,
  Box,
  Grid,
  Chip,
  Rating,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Tooltip,
  Alert,
  Breadcrumbs,
  Fab,
} from "@mui/material";
import {
  ShoppingCart,
  Favorite,
  FavoriteBorder,
  Clear,
  Compare,
  CheckCircle,
  Cancel,
} from "@mui/icons-material";
import { productsAPI, wishlistAPI } from "../../services/api";
import { useAuth } from "../../utils/AuthContext";
import { useCart } from "../../utils/CartContext";
import { motion } from "framer-motion";
import ScrollAnimation from "../common/ScrollAnimation";
import LazyImage from "../common/LazyImage";

const ProductComparison = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const { isAuthenticated } = useAuth();
  const { addToCart } = useCart();

  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const productIds = searchParams.get("products")?.split(",") || [];
  const productIdsString = productIds.join(",");

  const loadProducts = useCallback(async () => {
    if (productIds.length === 0) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const productPromises = productIds.map((id) =>
        productsAPI.getProduct(id).catch(() => null),
      );

      const results = await Promise.all(productPromises);
      const validProducts = results
        .filter((product) => product !== null)
        .map((res) => res.data);

      setProducts(validProducts);
    } catch (err) {
      setError("Failed to load products for comparison");
      console.error("Failed to load products:", err);
    } finally {
      setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [productIdsString]);

  useEffect(() => {
    loadProducts();
  }, [loadProducts]);

  const handleRemoveProduct = (productId) => {
    const newIds = productIds.filter((id) => id !== productId.toString());
    if (newIds.length > 0) {
      setSearchParams({ products: newIds.join(",") });
      setProducts(products.filter((p) => p.id !== productId));
    } else {
      // Clear comparison if no products left
      setSearchParams({});
      setProducts([]);
    }
  };

  const handleAddToCart = async (productId) => {
    const result = await addToCart(productId);
    if (result.success) {
      alert("Added to cart successfully!");
    } else {
      alert(result.error);
    }
  };

  const handleToggleWishlist = async (productId, isInWishlist) => {
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

      // Update product in state
      setProducts(
        products.map((p) =>
          p.id === productId ? { ...p, is_in_wishlist: !isInWishlist } : p,
        ),
      );
    } catch (error) {
      console.error("Failed to update wishlist:", error);
    }
  };

  const getBestValue = (products, field) => {
    if (!products.length) return null;

    const values = products
      .map((p) => {
        if (field === "price") return p.price;
        if (field === "rating") return p.average_rating || 0;
        if (field === "reviews") return p.review_count || 0;
        return null;
      })
      .filter((v) => v !== null);

    if (field === "price") {
      return Math.min(...values);
    }
    return Math.max(...values);
  };

  const isBestValue = (product, field) => {
    const best = getBestValue(products, field);
    if (field === "price") return product.price === best;
    if (field === "rating") return (product.average_rating || 0) === best;
    if (field === "reviews") return (product.review_count || 0) === best;
    return false;
  };

  if (loading) {
    return (
      <Container maxWidth="xl">
        <Box sx={{ textAlign: "center", py: 8 }}>
          <Typography variant="h6">
            Loading products for comparison...
          </Typography>
        </Box>
      </Container>
    );
  }

  if (error || products.length === 0) {
    return (
      <Container maxWidth="xl">
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
          <Typography color="text.primary">Compare Products</Typography>
        </Breadcrumbs>

        <Alert severity="info" sx={{ textAlign: "center", py: 8 }}>
          <Typography variant="h6" gutterBottom>
            No products to compare
          </Typography>
          <Typography variant="body1">
            Add products to compare by selecting them from the product list.
          </Typography>
          <Box sx={{ mt: 3 }}>
            <Button component={Link} to="/products" variant="contained">
              Browse Products
            </Button>
          </Box>
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl">
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
        <Typography color="text.primary">
          Compare Products ({products.length})
        </Typography>
      </Breadcrumbs>

      <ScrollAnimation animation="fadeUp">
        <Box sx={{ mb: 4, textAlign: "center" }}>
          <Typography
            variant="h4"
            component="h1"
            gutterBottom
            fontWeight="bold"
          >
            Product Comparison
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Compare features, prices, and ratings side by side
          </Typography>
        </Box>
      </ScrollAnimation>

      {/* Product Overview Cards */}
      <ScrollAnimation animation="fadeUp" delay={0.2}>
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {products.map((product, index) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={product.id}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
              >
                <Card sx={{ position: "relative", height: "100%" }}>
                  <IconButton
                    onClick={() => handleRemoveProduct(product.id)}
                    sx={{
                      position: "absolute",
                      top: 8,
                      right: 8,
                      zIndex: 1,
                      backgroundColor: "rgba(255,255,255,0.9)",
                      "&:hover": {
                        backgroundColor: "white",
                      },
                    }}
                  >
                    <Clear />
                  </IconButton>

                  <CardMedia sx={{ height: 200, position: "relative" }}>
                    <LazyImage
                      src={product.image || "/placeholder.png"}
                      alt={product.name}
                      height="100%"
                      width="100%"
                      objectFit="contain"
                      sx={{ p: 2 }}
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
                        }}
                      />
                    )}
                  </CardMedia>

                  <CardContent>
                    <Typography
                      variant="h6"
                      component={Link}
                      to={`/products/${product.slug}`}
                      sx={{
                        textDecoration: "none",
                        color: "inherit",
                        display: "block",
                        mb: 1,
                        "&:hover": {
                          color: "primary.main",
                        },
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
                        mb: 1,
                      }}
                    >
                      <Rating
                        value={product.average_rating || 0}
                        readOnly
                        size="small"
                        precision={0.1}
                      />
                      <Typography variant="body2">
                        ({product.review_count || 0})
                      </Typography>
                    </Box>

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
                    </Box>

                    <Box sx={{ display: "flex", gap: 1 }}>
                      <Button
                        variant="contained"
                        fullWidth
                        onClick={() => handleAddToCart(product.id)}
                        disabled={!product.in_stock}
                        startIcon={<ShoppingCart />}
                        size="small"
                      >
                        Add to Cart
                      </Button>
                      {isAuthenticated && (
                        <Tooltip
                          title={
                            product.is_in_wishlist
                              ? "Remove from Wishlist"
                              : "Add to Wishlist"
                          }
                        >
                          <IconButton
                            onClick={() =>
                              handleToggleWishlist(
                                product.id,
                                product.is_in_wishlist,
                              )
                            }
                            size="small"
                            sx={{
                              border: 1,
                              borderColor: "divider",
                              "&:hover": {
                                backgroundColor: product.is_in_wishlist
                                  ? "error.main"
                                  : "primary.main",
                                color: "white",
                              },
                            }}
                          >
                            {product.is_in_wishlist ? (
                              <Favorite />
                            ) : (
                              <FavoriteBorder />
                            )}
                          </IconButton>
                        </Tooltip>
                      )}
                    </Box>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>
          ))}
        </Grid>
      </ScrollAnimation>

      {/* Detailed Comparison Table */}
      <ScrollAnimation animation="fadeUp" delay={0.4}>
        <Card sx={{ borderRadius: 3, overflow: "hidden" }}>
          <CardContent sx={{ p: 0 }}>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow sx={{ backgroundColor: "grey.50" }}>
                    <TableCell
                      sx={{ fontWeight: "bold", fontSize: "1.1rem", py: 2 }}
                    >
                      Feature
                    </TableCell>
                    {products.map((product) => (
                      <TableCell
                        key={product.id}
                        align="center"
                        sx={{ fontWeight: "bold", py: 2 }}
                      >
                        <Box
                          sx={{
                            display: "flex",
                            flexDirection: "column",
                            alignItems: "center",
                          }}
                        >
                          <Typography variant="subtitle1" fontWeight="bold">
                            {product.name}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {product.vendor?.name}
                          </Typography>
                        </Box>
                      </TableCell>
                    ))}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {/* Price */}
                  <TableRow>
                    <TableCell
                      component="th"
                      scope="row"
                      sx={{ fontWeight: 600 }}
                    >
                      Price
                    </TableCell>
                    {products.map((product) => (
                      <TableCell key={product.id} align="center">
                        <Box
                          sx={{
                            display: "flex",
                            flexDirection: "column",
                            alignItems: "center",
                          }}
                        >
                          <Typography
                            variant="h6"
                            color="primary"
                            fontWeight="bold"
                          >
                            Ã¢â€šÂ¹{product.price}
                          </Typography>
                          {isBestValue(product, "price") && (
                            <Chip
                              label="Best Value"
                              color="success"
                              size="small"
                            />
                          )}
                        </Box>
                      </TableCell>
                    ))}
                  </TableRow>

                  {/* MRP */}
                  <TableRow sx={{ backgroundColor: "grey.25" }}>
                    <TableCell
                      component="th"
                      scope="row"
                      sx={{ fontWeight: 600 }}
                    >
                      MRP
                    </TableCell>
                    {products.map((product) => (
                      <TableCell key={product.id} align="center">
                        <Typography
                          variant="body2"
                          sx={{ textDecoration: "line-through" }}
                          color="text.secondary"
                        >
                          {product.mrp ? `Ã¢â€šÂ¹${product.mrp}` : "N/A"}
                        </Typography>
                      </TableCell>
                    ))}
                  </TableRow>

                  {/* Discount */}
                  <TableRow>
                    <TableCell
                      component="th"
                      scope="row"
                      sx={{ fontWeight: 600 }}
                    >
                      Discount
                    </TableCell>
                    {products.map((product) => (
                      <TableCell key={product.id} align="center">
                        {product.discount_percentage > 0 ? (
                          <Chip
                            label={`${product.discount_percentage}%`}
                            color="error"
                            size="small"
                          />
                        ) : (
                          <Typography variant="body2" color="text.secondary">
                            No discount
                          </Typography>
                        )}
                      </TableCell>
                    ))}
                  </TableRow>

                  {/* Rating */}
                  <TableRow sx={{ backgroundColor: "grey.25" }}>
                    <TableCell
                      component="th"
                      scope="row"
                      sx={{ fontWeight: 600 }}
                    >
                      Rating
                    </TableCell>
                    {products.map((product) => (
                      <TableCell key={product.id} align="center">
                        <Box
                          sx={{
                            display: "flex",
                            flexDirection: "column",
                            alignItems: "center",
                          }}
                        >
                          <Rating
                            value={product.average_rating || 0}
                            readOnly
                            size="small"
                            precision={0.1}
                          />
                          <Typography variant="body2" color="text.secondary">
                            ({product.review_count || 0} reviews)
                          </Typography>
                          {isBestValue(product, "rating") && (
                            <Chip
                              label="Highest Rated"
                              color="warning"
                              size="small"
                              sx={{ mt: 0.5 }}
                            />
                          )}
                        </Box>
                      </TableCell>
                    ))}
                  </TableRow>

                  {/* Stock Status */}
                  <TableRow>
                    <TableCell
                      component="th"
                      scope="row"
                      sx={{ fontWeight: 600 }}
                    >
                      Availability
                    </TableCell>
                    {products.map((product) => (
                      <TableCell key={product.id} align="center">
                        {product.in_stock ? (
                          <Box
                            sx={{
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "center",
                              gap: 0.5,
                            }}
                          >
                            <CheckCircle color="success" />
                            <Typography
                              variant="body2"
                              color="success.main"
                              fontWeight="500"
                            >
                              In Stock
                            </Typography>
                          </Box>
                        ) : (
                          <Box
                            sx={{
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "center",
                              gap: 0.5,
                            }}
                          >
                            <Cancel color="error" />
                            <Typography
                              variant="body2"
                              color="error.main"
                              fontWeight="500"
                            >
                              Out of Stock
                            </Typography>
                          </Box>
                        )}
                      </TableCell>
                    ))}
                  </TableRow>

                  {/* Category */}
                  <TableRow sx={{ backgroundColor: "grey.25" }}>
                    <TableCell
                      component="th"
                      scope="row"
                      sx={{ fontWeight: 600 }}
                    >
                      Category
                    </TableCell>
                    {products.map((product) => (
                      <TableCell key={product.id} align="center">
                        <Typography variant="body2">
                          {product.category?.name || "N/A"}
                        </Typography>
                      </TableCell>
                    ))}
                  </TableRow>

                  {/* Vendor */}
                  <TableRow>
                    <TableCell
                      component="th"
                      scope="row"
                      sx={{ fontWeight: 600 }}
                    >
                      Vendor
                    </TableCell>
                    {products.map((product) => (
                      <TableCell key={product.id} align="center">
                        <Typography variant="body2">
                          {product.vendor?.name || "N/A"}
                        </Typography>
                      </TableCell>
                    ))}
                  </TableRow>

                  {/* Actions */}
                  <TableRow sx={{ backgroundColor: "grey.25" }}>
                    <TableCell
                      component="th"
                      scope="row"
                      sx={{ fontWeight: 600 }}
                    >
                      Actions
                    </TableCell>
                    {products.map((product) => (
                      <TableCell key={product.id} align="center">
                        <Box
                          sx={{
                            display: "flex",
                            gap: 1,
                            justifyContent: "center",
                          }}
                        >
                          <Button
                            variant="contained"
                            size="small"
                            onClick={() => handleAddToCart(product.id)}
                            disabled={!product.in_stock}
                            startIcon={<ShoppingCart />}
                          >
                            Add to Cart
                          </Button>
                          <Button
                            component={Link}
                            to={`/products/${product.slug}`}
                            variant="outlined"
                            size="small"
                          >
                            View Details
                          </Button>
                        </Box>
                      </TableCell>
                    ))}
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      </ScrollAnimation>

      {/* Floating Action Button for Comparison Actions */}
      <Box
        sx={{
          position: "fixed",
          bottom: 24,
          right: 24,
          display: "flex",
          flexDirection: "column",
          gap: 2,
          zIndex: 1000,
        }}
      >
        <Fab
          color="primary"
          size="medium"
          component={Link}
          to="/products"
          sx={{
            borderRadius: 3,
            boxShadow: 4,
            "&:hover": {
              transform: "scale(1.1)",
            },
          }}
        >
          <Compare />
        </Fab>
      </Box>
    </Container>
  );
};

export default ProductComparison;
