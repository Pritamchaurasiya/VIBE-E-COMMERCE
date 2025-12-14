import React, { useState, useEffect, useCallback } from "react";
import { useSearchParams, Link, useNavigate, useParams, useLocation } from "react-router-dom";
import PropTypes from "prop-types";
import {
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Box,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  IconButton,
  Alert,
  Drawer,
  Divider,
  Slider,
  FormControlLabel,
  Checkbox,
  ToggleButton,
  ToggleButtonGroup,
  Badge,
  Rating,
  Tooltip,
  Fab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Paper,
  Skeleton,
  CircularProgress,
  Snackbar,
  Popover,
} from "@mui/material";
import {
  Favorite,
  FavoriteBorder,
  FilterList,
  ViewList,
  ViewModule,
  Compare,
  Search,
  ExpandMore,
  ShoppingCart,
  Visibility,
  Clear,
  Verified,
  ExpandLess,
  FlashOn,
  Star,
  Warning,
} from "@mui/icons-material";
import { productsAPI, wishlistAPI } from "../../services/api";
import { useAuth } from "../../utils/AuthContext";
import { useCart } from "../../utils/CartContext";
import { motion, AnimatePresence } from "framer-motion";
import LazyImage from "../common/LazyImage";

const ProductCard = React.memo(
  ({
    product,
    index,
    selectedProducts,
    onSelect,
    isAuthenticated,
    onToggleWishlist,
    onAddToCart,
    onQuickView,
    onHoverPreview,
    onBuyNow,
    navigate,
  }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: index * 0.05 }}
    >
      <Card
        sx={{
          height: "100%",
          display: "flex",
          flexDirection: "column",
          position: "relative",
          transition: "all 0.4s cubic-bezier(0.4, 0, 0.2, 1)",
          borderRadius: 4,
          overflow: "hidden",
          border: "1px solid",
          borderColor: "divider",
          backgroundColor: "background.paper",
          cursor: "pointer",
          "&:hover": {
            transform: "translateY(-8px)",
            boxShadow:
              "0 20px 40px -4px rgba(0,0,0,0.1), 0 8px 16px -4px rgba(0,0,0,0.06)",
            borderColor: "primary.main",
            "& .product-image": {
              transform: "scale(1.08)",
            },
            "& .product-actions": {
              opacity: 1,
              transform: "translateY(0)",
            },
            "& .product-overlay": {
              opacity: 1,
            },
          },
        }}
        onMouseEnter={(e) => onHoverPreview?.(product, e.currentTarget)}
        onMouseLeave={() => onHoverPreview?.(null, null)}
        tabIndex={0}
        role="button"
        onClick={() => navigate(`/products/${product.slug}`)}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            navigate(`/products/${product.slug}`);
          }
        }}
      >
        {/* Compare Checkbox */}
        <Box sx={{ position: "absolute", top: 12, left: 12, zIndex: 3 }}>
          <Checkbox
            checked={selectedProducts.includes(product.id)}
            onChange={() => onSelect(product.id)}
            size="small"
            onClick={(e) => e.stopPropagation()}
            sx={{
              backgroundColor: "rgba(255,255,255,0.8)",
              backdropFilter: "blur(8px)",
              borderRadius: 2,
              transition: "all 0.2s",
              "&:hover": {
                backgroundColor: "white",
                transform: "scale(1.1)",
              },
            }}
          />
        </Box>

        {/* Wishlist Button */}
        {isAuthenticated && (
          <Tooltip
            title={
              product.is_in_wishlist
                ? "Remove from Wishlist"
                : "Add to Wishlist"
            }
          >
            <IconButton
              sx={{
                position: "absolute",
                top: 12,
                right: 12,
                zIndex: 3,
                backgroundColor: "rgba(255,255,255,0.8)",
                backdropFilter: "blur(8px)",
                boxShadow: "0 2px 8px rgba(0,0,0,0.05)",
                "&:hover": {
                  backgroundColor: "white",
                  transform: "scale(1.1)",
                  color: "error.main",
                  boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
                },
                transition: "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
              }}
              onClick={(e) => {
                e.stopPropagation();
                onToggleWishlist(product.id, product.is_in_wishlist);
              }}
            >
              {product.is_in_wishlist ? (
                <Favorite color="error" fontSize="small" />
              ) : (
                <FavoriteBorder fontSize="small" />
              )}
            </IconButton>
          </Tooltip>
        )}

        {/* Image Container */}
        <Box
          sx={{
            position: "relative",
            overflow: "hidden",
            pt: "100%",
            backgroundColor: "action.hover",
          }}
        >
          <Box
            component={Link}
            to={`/products/${product.slug}`}
            sx={{
              position: "absolute",
              top: 0,
              left: 0,
              width: "100%",
              height: "100%",
            }}
          >
            <LazyImage
              src={product.image || "/placeholder.png"}
              alt={product.name}
              height="100%"
              width="100%"
              objectFit="contain"
              className="product-image"
              sx={{
                padding: 3,
                transition: "transform 0.6s cubic-bezier(0.4, 0, 0.2, 1)",
              }}
            />
          </Box>

          {/* Badges */}
          <Box
            sx={{
              position: "absolute",
              bottom: 12,
              left: 12,
              display: "flex",
              gap: 1,
              zIndex: 2,
            }}
          >
            {product.discount_percentage > 0 && (
              <Chip
                label={`${product.discount_percentage}% OFF`}
                color="error"
                size="small"
                sx={{
                  fontWeight: 700,
                  fontSize: "0.75rem",
                  height: 24,
                  boxShadow: 2,
                }}
              />
            )}
            {product.is_featured && (
              <Chip
                label="Featured"
                color="secondary"
                size="small"
                sx={{
                  fontWeight: 700,
                  fontSize: "0.75rem",
                  height: 24,
                  boxShadow: 2,
                }}
              />
            )}
          </Box>
        </Box>

        <CardContent
          sx={{ flexGrow: 1, display: "flex", flexDirection: "column", p: 2.5 }}
        >
          <Box
            sx={{
              mb: 1,
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <Typography
              variant="caption"
              sx={{
                color: "text.secondary",
                fontWeight: 600,
                textTransform: "uppercase",
                letterSpacing: 0.5,
                fontSize: "0.7rem",
              }}
            >
              {product.category?.name}
            </Typography>
            <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
              <Star sx={{ color: "warning.main", fontSize: 16 }} />
              <Typography
                variant="caption"
                fontWeight="600"
                color="text.primary"
              >
                {product.average_rating?.toFixed(1) || "0.0"}
              </Typography>
            </Box>
          </Box>

          <Typography
            variant="subtitle1"
            component={Link}
            to={`/products/${product.slug}`}
            sx={{
              textDecoration: "none",
              color: "text.primary",
              mb: 1,
              fontWeight: 700,
              lineHeight: 1.4,
              overflow: "hidden",
              textOverflow: "ellipsis",
              display: "-webkit-box",
              WebkitLineClamp: 2,
              WebkitBoxOrient: "vertical",
              fontSize: "1rem",
              transition: "color 0.2s",
              "&:hover": {
                color: "primary.main",
              },
            }}
          >
            {product.name}
          </Typography>

          <Typography
            variant="caption"
            color="text.secondary"
            sx={{ mb: 2, display: "block" }}
          >
            By{" "}
            <Box
              component="span"
              sx={{ color: "primary.main", fontWeight: 500 }}
            >
              {product.vendor?.name}
            </Box>
          </Typography>

          <Box sx={{ mt: "auto" }}>
            <Box
              sx={{ display: "flex", alignItems: "flex-end", gap: 1, mb: 2 }}
            >
              <Typography
                variant="h6"
                color="primary.main"
                fontWeight="800"
                sx={{ lineHeight: 1 }}
              >
                {new Intl.NumberFormat("en-IN", {
                  style: "currency",
                  currency: "INR",
                  maximumFractionDigits: 0,
                }).format(product.price)}
              </Typography>
              {product.mrp && product.mrp > product.price && (
                <Typography
                  variant="caption"
                  sx={{ textDecoration: "line-through", mb: 0.2 }}
                  color="text.secondary"
                >
                  {new Intl.NumberFormat("en-IN", {
                    style: "currency",
                    currency: "INR",
                    maximumFractionDigits: 0,
                  }).format(product.mrp)}
                </Typography>
              )}
            </Box>

            <Box
              sx={{
                display: "flex",
                alignItems: "center",
                gap: 1,
                mb: 2,
                minHeight: 24,
              }}
            >
              {product.in_stock ? (
                <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
                  <Verified sx={{ color: "success.main", fontSize: 16 }} />
                  <Typography
                    variant="caption"
                    color="success.main"
                    fontWeight="600"
                  >
                    In Stock
                  </Typography>
                </Box>
              ) : (
                <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
                  <Warning sx={{ color: "error.main", fontSize: 16 }} />
                  <Typography
                    variant="caption"
                    color="error.main"
                    fontWeight="600"
                  >
                    Out of Stock
                  </Typography>
                </Box>
              )}
            </Box>

            <Box
              className="product-actions"
              sx={{
                display: "flex",
                gap: 1,
                opacity: { xs: 1, md: 0 },
                transform: { xs: "none", md: "translateY(10px)" },
                transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
              }}
            >
              <Button
                variant="contained"
                fullWidth
                onClick={(e) => {
                  e.stopPropagation();
                  onAddToCart(product.id);
                }}
                disabled={!product.in_stock}
                startIcon={<ShoppingCart sx={{ fontSize: 20 }} />}
                size="small"
                sx={{
                  borderRadius: 2,
                  fontWeight: 600,
                  textTransform: "none",
                  boxShadow: "none",
                  py: 1,
                  flex: 1,
                }}
              >
                Add
              </Button>
              <Button
                variant="contained"
                color="secondary"
                onClick={(e) => {
                  e.stopPropagation();
                  onBuyNow(product.id);
                }}
                disabled={!product.in_stock}
                startIcon={<FlashOn sx={{ fontSize: 20 }} />}
                size="small"
                sx={{
                  borderRadius: 2,
                  fontWeight: 600,
                  textTransform: "none",
                  boxShadow: "none",
                  py: 1,
                  flex: 1,
                }}
              >
                Buy
              </Button>
              <Tooltip title="Quick View">
                <IconButton
                  onClick={(e) => {
                    e.stopPropagation();
                    onQuickView(product);
                  }}
                  color="default"
                  size="small"
                  sx={{
                    border: "1px solid",
                    borderColor: "divider",
                    borderRadius: 2,
                    "&:hover": {
                      backgroundColor: "action.hover",
                      borderColor: "primary.main",
                      color: "primary.main",
                    },
                  }}
                >
                  <Visibility fontSize="small" />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>
        </CardContent>
      </Card>
    </motion.div>
  ),
);

ProductCard.propTypes = {
  product: PropTypes.shape({
    id: PropTypes.number.isRequired,
    name: PropTypes.string.isRequired,
    slug: PropTypes.string.isRequired,
    price: PropTypes.number.isRequired,
    mrp: PropTypes.number,
    discount_percentage: PropTypes.number,
    image: PropTypes.string,
    category: PropTypes.shape({ name: PropTypes.string }),
    vendor: PropTypes.shape({ name: PropTypes.string }),
    average_rating: PropTypes.number,
    review_count: PropTypes.number,
    in_stock: PropTypes.bool,
    is_featured: PropTypes.bool,
    is_in_wishlist: PropTypes.bool,
    description: PropTypes.string,
  }).isRequired,
  index: PropTypes.number,
  selectedProducts: PropTypes.arrayOf(PropTypes.number).isRequired,
  onSelect: PropTypes.func.isRequired,
  isAuthenticated: PropTypes.bool.isRequired,
  onToggleWishlist: PropTypes.func.isRequired,
  onAddToCart: PropTypes.func.isRequired,
  onQuickView: PropTypes.func.isRequired,
  onHoverPreview: PropTypes.func,
  onBuyNow: PropTypes.func.isRequired,
};

const ProductListItem = React.memo(
  ({ product, selectedProducts, onSelect, onAddToCart, onQuickView }) => (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      whileHover={{ scale: 1.01 }}
      transition={{ duration: 0.3 }}
    >
      <Card
        sx={{
          mb: 2,
          borderRadius: 2,
          overflow: "hidden",
          boxShadow: 1,
          "&:hover": { boxShadow: 4 },
        }}
      >
        <CardContent sx={{ p: 0 }}>
          <Grid container spacing={0} alignItems="center">
            <Grid item xs={12} sm={4} md={3}>
              <Box sx={{ position: "relative", height: 150 }}>
                <Checkbox
                  checked={selectedProducts.includes(product.id)}
                  onChange={() => onSelect(product.id)}
                  size="small"
                  sx={{
                    position: "absolute",
                    top: 8,
                    left: 8,
                    zIndex: 2,
                    backgroundColor: "rgba(255,255,255,0.8)",
                    borderRadius: 1,
                  }}
                />
                <Box
                  component={Link}
                  to={`/products/${product.slug}`}
                  sx={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    height: "100%",
                    width: "100%",
                    backgroundColor: "grey.50",
                    textDecoration: "none",
                  }}
                >
                  <LazyImage
                    src={product.image || "/placeholder.png"}
                    alt={product.name}
                    width="100%"
                    height="100%"
                    objectFit="contain"
                    sx={{ padding: 1 }}
                  />
                </Box>
              </Box>
            </Grid>
            <Grid item xs={12} sm={8} md={9}>
              <Box sx={{ p: 2 }}>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <Typography
                      variant="h6"
                      component={Link}
                      to={`/products/${product.slug}`}
                      sx={{
                        textDecoration: "none",
                        color: "text.primary",
                        fontWeight: 600,
                        "&:hover": {
                          color: "primary.main",
                        },
                      }}
                    >
                      {product.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {product.category?.name} Ã¢â‚¬Â¢ {product.vendor?.name}
                    </Typography>
                    <Box
                      sx={{
                        display: "flex",
                        alignItems: "center",
                        gap: 1,
                        mt: 1,
                      }}
                    >
                      <Rating
                        value={product.average_rating || 0}
                        readOnly
                        size="small"
                      />
                      <Typography variant="body2">
                        ({product.review_count || 0} reviews)
                      </Typography>
                    </Box>
                    <Box
                      sx={{
                        display: "flex",
                        alignItems: "center",
                        gap: 1,
                        mt: 1,
                      }}
                    >
                      {product.in_stock ? (
                        <Chip
                          label="In Stock"
                          size="small"
                          color="success"
                          variant="outlined"
                        />
                      ) : (
                        <Chip
                          label="Out of Stock"
                          size="small"
                          color="error"
                          variant="outlined"
                        />
                      )}
                    </Box>
                  </Grid>
                  <Grid
                    item
                    xs={12}
                    md={6}
                    sx={{ textAlign: { xs: "left", md: "right" } }}
                  >
                    <Box sx={{ mb: 2 }}>
                      <Typography
                        variant="h6"
                        color="primary"
                        fontWeight="bold"
                      >
                        {new Intl.NumberFormat("en-IN", {
                          style: "currency",
                          currency: "INR",
                          maximumFractionDigits: 0,
                        }).format(product.price)}
                      </Typography>
                      {product.mrp && product.mrp > product.price && (
                        <Typography
                          variant="body2"
                          sx={{ textDecoration: "line-through" }}
                          color="text.secondary"
                        >
                          {new Intl.NumberFormat("en-IN", {
                            style: "currency",
                            currency: "INR",
                            maximumFractionDigits: 0,
                          }).format(product.mrp)}
                        </Typography>
                      )}
                    </Box>
                    <Box
                      sx={{
                        display: "flex",
                        alignItems: "center",
                        gap: 1,
                        justifyContent: { xs: "flex-start", md: "flex-end" },
                      }}
                    >
                      <Button
                        variant="contained"
                        onClick={() => onAddToCart(product.id)}
                        disabled={!product.in_stock}
                        size="small"
                        startIcon={<ShoppingCart />}
                      >
                        Add
                      </Button>
                      <IconButton
                        onClick={() => onQuickView(product)}
                        size="small"
                        sx={{ border: "1px solid", borderColor: "divider" }}
                      >
                        <Visibility />
                      </IconButton>
                    </Box>
                  </Grid>
                </Grid>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </motion.div>
  ),
);

ProductListItem.propTypes = {
  product: PropTypes.shape({
    id: PropTypes.number.isRequired,
    name: PropTypes.string.isRequired,
    slug: PropTypes.string.isRequired,
    price: PropTypes.number.isRequired,
    mrp: PropTypes.number,
    image: PropTypes.string,
    category: PropTypes.shape({ name: PropTypes.string }),
    vendor: PropTypes.shape({ name: PropTypes.string }),
    average_rating: PropTypes.number,
    review_count: PropTypes.number,
    in_stock: PropTypes.bool,
  }).isRequired,
  selectedProducts: PropTypes.arrayOf(PropTypes.number).isRequired,
  onSelect: PropTypes.func.isRequired,
  onAddToCart: PropTypes.func.isRequired,
  onQuickView: PropTypes.func.isRequired,
};
const ProductList = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const { slug } = useParams();
  const location = useLocation();
  const { isAuthenticated } = useAuth();
  const { addToCart, cart } = useCart();
  const navigate = useNavigate();

  const [products, setProducts] = useState([]);
  const [brands, setBrands] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [hasNextPage, setHasNextPage] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [viewMode, setViewMode] = useState("grid");
  const [selectedProducts, setSelectedProducts] = useState([]);
  const [quickViewProduct, setQuickViewProduct] = useState(null);
  const [filtersOpen, setFiltersOpen] = useState(false);
  const [hoverPreview, setHoverPreview] = useState({
    product: null,
    anchorEl: null,
  });
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: "",
    severity: "success",
  });

  // Filters
  const [filters, setFilters] = useState({
    q: searchParams.get("q") || "",
    category: searchParams.get("category") || "",
    vendor: searchParams.get("vendor") || "",
    brands: searchParams.get("brands")
      ? searchParams.get("brands").split(",")
      : [],
    min_price: searchParams.get("min_price") || "",
    max_price: searchParams.get("max_price") || "",
    min_rating: searchParams.get("min_rating") || "",
    sort: searchParams.get("sort") || "relevance",
    in_stock: searchParams.get("in_stock") || "",
    crop: searchParams.get("crop") || "",
    disease: searchParams.get("disease") || "",
    has_discount: searchParams.get("has_discount") || "",
  });

  const [priceRange, setPriceRange] = useState([
    filters.min_price ? Number.parseInt(filters.min_price, 10) : 0,
    filters.max_price ? Number.parseInt(filters.max_price, 10) : 10000,
  ]);

  useEffect(() => {
    loadFiltersData();
  }, []);

  useEffect(() => {
    // Determine filter based on URL path
    let newFilters = {
      q: searchParams.get("q") || "",
      category: searchParams.get("category") || "",
      vendor: searchParams.get("vendor") || "",
      crop: searchParams.get("crop") || "",
      disease: searchParams.get("disease") || "",
      brands: searchParams.get("brands")
        ? searchParams.get("brands").split(",")
        : [],
      min_price: searchParams.get("min_price") || "",
      max_price: searchParams.get("max_price") || "",
      min_rating: searchParams.get("min_rating") || "",
      sort: searchParams.get("sort") || "relevance",
      in_stock: searchParams.get("in_stock") || "",
      has_discount: searchParams.get("has_discount") || "",
    };

    if (slug) {
      if (location.pathname.includes("/category/")) {
        newFilters.category = slug;
      } else if (location.pathname.includes("/crop/")) {
        newFilters.crop = slug;
      } else if (location.pathname.includes("/disease/")) {
        newFilters.disease = slug;
      }
    }

    if (location.pathname === "/offers") {
      newFilters.has_discount = "true";
    }

    setFilters(prev => ({ ...prev, ...newFilters }));
  }, [searchParams, slug, location.pathname]);

  const loadProducts = useCallback(
    async (append = false) => {
      if (append) {
        setLoadingMore(true);
      } else {
        setLoading(true);
        setProducts([]);
      }
      setError(null);
      try {
        const params = {
          ...filters,
          brands: filters.brands.join(","),
          page: append ? currentPage + 1 : 1,
        };

        // Remove empty filters
        Object.keys(params).forEach((key) => {
          if (
            params[key] === "" ||
            params[key] === null ||
            params[key] === undefined
          )
            delete params[key];
        });

        const response = await productsAPI.getProducts(params);
        const newProducts = response.data.results || response.data;
        const totalCount = response.data.count || newProducts.length;

        if (append) {
          setProducts((prev) => [...prev, ...newProducts]);
          setCurrentPage((prev) => prev + 1);
        } else {
          setProducts(newProducts);
          setCurrentPage(1);
        }

        setHasNextPage(
          newProducts.length === 20 &&
            (append ? currentPage + 1 : 1) * 20 < totalCount,
        );
      } catch (err) {
        setError("Failed to load products");
        console.error("Failed to load products:", err);
      } finally {
        setLoading(false);
        setLoadingMore(false);
      }
    },
    [filters, currentPage],
  );

  useEffect(() => {
    loadProducts();
  }, [loadProducts]);

  // Real-time wishlist updates
  useEffect(() => {
    if (!isAuthenticated) return;

    const pollInterval = setInterval(() => {
      loadProducts();
    }, 60000); // Poll every minute for wishlist updates

    return () => clearInterval(pollInterval);
  }, [isAuthenticated, loadProducts]);

  const loadFiltersData = async () => {
    try {
      const [categoriesRes, , productsRes] = await Promise.all([
        productsAPI.getCategories(),
        productsAPI.getVendors(),
        productsAPI.getProducts({ limit: 100 }),
      ]);

      setCategories(categoriesRes.data);
      const allProducts = productsRes.data.results || productsRes.data;
      const uniqueBrands = [
        ...new Set(allProducts.map((p) => p.brand).filter(Boolean)),
      ];
      setBrands(uniqueBrands);
    } catch (err) {
      console.error("Failed to load filter data:", err);
    }
  };

  const handleFilterChange = (name, value) => {
    const newFilters = { ...filters, [name]: value };
    setFilters(newFilters);
    setCurrentPage(1);

    const params = new URLSearchParams();
    Object.entries(newFilters).forEach(([key, val]) => {
      if (Array.isArray(val)) {
        if (val.length > 0) params.set(key, val.join(","));
      } else if (val) {
        params.set(key, val);
      }
    });
    setSearchParams(params);
  };

  const loadMore = () => {
    loadProducts(true);
  };

  const handleBrandChange = (brand, checked) => {
    const newBrands = checked
      ? [...filters.brands, brand]
      : filters.brands.filter((b) => b !== brand);
    handleFilterChange("brands", newBrands);
  };

  const handlePriceRangeChange = (event, newValue) => {
    setPriceRange(newValue);
    handleFilterChange("min_price", newValue[0].toString());
    handleFilterChange("max_price", newValue[1].toString());
  };

  const handleViewModeChange = (event, newViewMode) => {
    if (newViewMode !== null) {
      setViewMode(newViewMode);
    }
  };

  const handleProductSelect = (productId) => {
    setSelectedProducts((prev) =>
      prev.includes(productId)
        ? prev.filter((id) => id !== productId)
        : [...prev, productId],
    );
  };

  const handleAddToCart = useCallback(
    async (productId) => {
      if (!isAuthenticated) {
        navigate("/login");
        return;
      }
      const result = await addToCart(productId);
      if (result.success) {
        setSnackbar({
          open: true,
          message: "Added to cart successfully",
          severity: "success",
        });
      } else {
        setSnackbar({ open: true, message: result.error, severity: "error" });
      }
    },
    [addToCart, isAuthenticated, navigate],
  );

  const handleBuyNow = useCallback(
    async (productId) => {
      await handleAddToCart(productId);
      navigate("/checkout");
    },
    [handleAddToCart, navigate],
  );

  const handleToggleWishlist = async (productId, isInWishlist) => {
    if (!isAuthenticated) {
      navigate("/login");
      return;
    }
    try {
      if (isInWishlist) {
        await wishlistAPI.removeFromWishlist(productId);
      } else {
        await wishlistAPI.addToWishlist(productId);
      }
      loadProducts();
    } catch (error) {
      console.error("Failed to update wishlist:", error);
    }
  };

  const handleHoverPreview = (product, anchorEl) => {
    setHoverPreview({ product, anchorEl });
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const clearFilters = () => {
    const clearedFilters = {
      q: "",
      category: "",
      vendor: "",
      brands: [],
      min_price: "",
      max_price: "",
      min_rating: "",
      sort: "relevance",
      in_stock: "",
    };
    setFilters(clearedFilters);
    setPriceRange([0, 10000]);
    setCurrentPage(1);
    setSearchParams({});
  };

  return (
    <Container maxWidth="xl">
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography
          variant="h4"
          component="h1"
          gutterBottom
          sx={{ fontWeight: 700, color: "text.primary" }}
        >
          Agricultural Products
        </Typography>
        <Typography
          variant="body1"
          color="text.secondary"
          sx={{ mb: 3, fontSize: "1.1rem" }}
        >
          Discover quality farming equipment, seeds, fertilizers, and supplies
          from trusted vendors
        </Typography>
      </Box>

      {/* Search and Controls */}
      <Paper
        elevation={1}
        sx={{
          p: 3,
          mb: 3,
          borderRadius: 3,
          background: (theme) =>
            `linear-gradient(135deg, ${theme.palette.background.paper} 0%, ${theme.palette.background.default} 100%)`,
        }}
      >
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              placeholder="Search products by name, category, or vendor..."
              value={filters.q}
              onChange={(e) => handleFilterChange("q", e.target.value)}
              InputProps={{
                startAdornment: (
                  <Search sx={{ mr: 1, color: "text.secondary" }} />
                ),
              }}
              sx={{
                "& .MuiOutlinedInput-root": {
                  borderRadius: 2,
                  backgroundColor: "white",
                },
              }}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap" }}>
              <Button
                variant="outlined"
                startIcon={<FilterList />}
                onClick={() => setFiltersOpen(true)}
                sx={{
                  borderRadius: 2,
                  px: 3,
                  "&:hover": {
                    backgroundColor: "primary.main",
                    color: "white",
                  },
                }}
              >
                Filters
              </Button>

              <FormControl size="small" sx={{ minWidth: 150 }}>
                <InputLabel>Sort By</InputLabel>
                <Select
                  value={filters.sort}
                  onChange={(e) => handleFilterChange("sort", e.target.value)}
                  sx={{ borderRadius: 2 }}
                >
                  <MenuItem value="relevance">Relevance</MenuItem>
                  <MenuItem value="name">Name A-Z</MenuItem>
                  <MenuItem value="price_low">Price: Low to High</MenuItem>
                  <MenuItem value="price_high">Price: High to Low</MenuItem>
                  <MenuItem value="newest">Newest First</MenuItem>
                  <MenuItem value="rating">Highest Rated</MenuItem>
                  <MenuItem value="popular">Most Popular</MenuItem>
                </Select>
              </FormControl>

              <ToggleButtonGroup
                value={viewMode}
                exclusive
                onChange={handleViewModeChange}
                size="small"
                sx={{
                  "& .MuiToggleButton-root": {
                    borderRadius: 2,
                    px: 2,
                  },
                }}
              >
                <ToggleButton value="grid" aria-label="grid view">
                  <ViewModule />
                </ToggleButton>
                <ToggleButton value="list" aria-label="list view">
                  <ViewList />
                </ToggleButton>
              </ToggleButtonGroup>
            </Box>
          </Grid>
        </Grid>

        {/* Active Filters */}
        {(filters.brands.length > 0 ||
          filters.category ||
          filters.min_rating ||
          filters.in_stock) && (
          <Box
            sx={{
              mt: 2,
              display: "flex",
              gap: 1,
              flexWrap: "wrap",
              alignItems: "center",
            }}
          >
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{ fontWeight: 600 }}
            >
              Active filters:
            </Typography>
            {filters.category && (
              <Chip
                label={`Category: ${categories.find((c) => c.slug === filters.category)?.name || filters.category}`}
                onDelete={() => handleFilterChange("category", "")}
                size="small"
                color="primary"
                variant="outlined"
              />
            )}
            {filters.brands.map((brand) => (
              <Chip
                key={brand}
                label={`Brand: ${brand}`}
                onDelete={() => handleBrandChange(brand, false)}
                size="small"
                sx={{ fontWeight: 600 }}
              />
            ))}
            {filters.min_rating && (
              <Chip
                label={`Rating: ${filters.min_rating}+ stars`}
                onDelete={() => handleFilterChange("min_rating", "")}
                size="small"
                color="warning"
                variant="outlined"
              />
            )}
            {filters.in_stock && (
              <Chip
                label="In Stock Only"
                onDelete={() => handleFilterChange("in_stock", "")}
                size="small"
                color="success"
                variant="outlined"
              />
            )}
            <Button
              size="small"
              onClick={clearFilters}
              sx={{ textTransform: "none" }}
            >
              Clear all
            </Button>
          </Box>
        )}
      </Paper>

      <Grid container spacing={4}>
        {/* Desktop Filters Sidebar */}
        <Grid item xs={12} md={3} sx={{ display: { xs: "none", md: "block" } }}>
          <Card sx={{ borderRadius: 3, position: "sticky", top: 20 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom fontWeight="bold">
                Filters
              </Typography>
              <Divider sx={{ mb: 3 }} />

              <Box sx={{ mb: 3 }}>
                <Typography gutterBottom fontWeight="600">
                  Price Range
                </Typography>
                <Slider
                  value={priceRange}
                  onChange={handlePriceRangeChange}
                  valueLabelDisplay="auto"
                  min={0}
                  max={10000}
                  step={100}
                  sx={{ color: "primary.main" }}
                />
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ mt: 1 }}
                >
                  Ã¢â€šÂ¹{priceRange[0]} - Ã¢â€šÂ¹{priceRange[1]}
                </Typography>
              </Box>

              <Box sx={{ mb: 3 }}>
                <Typography gutterBottom fontWeight="600">
                  Category
                </Typography>
                <FormControl fullWidth size="small">
                  <InputLabel>Category</InputLabel>
                  <Select
                    value={filters.category}
                    onChange={(e) =>
                      handleFilterChange("category", e.target.value)
                    }
                    sx={{ borderRadius: 2 }}
                  >
                    <MenuItem value="">All Categories</MenuItem>
                    {categories.map((category) => (
                      <MenuItem key={category.id} value={category.slug}>
                        {category.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Box>

              <Box sx={{ mb: 3 }}>
                <Typography gutterBottom fontWeight="600">
                  Brands
                </Typography>
                <Box sx={{ maxHeight: 200, overflowY: "auto" }}>
                  {brands.slice(0, 15).map((brand) => (
                    <FormControlLabel
                      key={brand}
                      control={
                        <Checkbox
                          checked={filters.brands.includes(brand)}
                          onChange={(e) =>
                            handleBrandChange(brand, e.target.checked)
                          }
                          size="small"
                        />
                      }
                      label={brand}
                      sx={{ width: "100%", mb: 0.5 }}
                    />
                  ))}
                </Box>
              </Box>

              <Box sx={{ mb: 3 }}>
                <Typography gutterBottom fontWeight="600">
                  Minimum Rating
                </Typography>
                {[4, 3, 2, 1].map((rating) => (
                  <FormControlLabel
                    key={rating}
                    control={
                      <Checkbox
                        checked={filters.min_rating === rating.toString()}
                        onChange={(e) =>
                          handleFilterChange(
                            "min_rating",
                            e.target.checked ? rating.toString() : "",
                          )
                        }
                        size="small"
                      />
                    }
                    label={`${rating}+ Stars`}
                  />
                ))}
              </Box>

              <Box sx={{ mb: 3 }}>
                <Typography gutterBottom fontWeight="600">
                  Availability
                </Typography>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={filters.in_stock === "true"}
                      onChange={(e) =>
                        handleFilterChange(
                          "in_stock",
                          e.target.checked ? "true" : "",
                        )
                      }
                      size="small"
                    />
                  }
                  label="In Stock Only"
                />
              </Box>

              <Button
                variant="outlined"
                fullWidth
                onClick={clearFilters}
                startIcon={<Clear />}
                sx={{ borderRadius: 2 }}
              >
                Clear All Filters
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Products */}
        <Grid item xs={12} md={9}>
          {error && (
            <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }}>
              {error}
            </Alert>
          )}

          {loading && !loadingMore && products.length === 0 ? (
            <Box>
              <Grid container spacing={3}>
                {[
                  "prod-1",
                  "prod-2",
                  "prod-3",
                  "prod-4",
                  "prod-5",
                  "prod-6",
                  "prod-7",
                  "prod-8",
                ].map((id) => (
                  <Grid
                    item
                    xs={12}
                    sm={6}
                    md={6}
                    lg={4}
                    xl={3}
                    key={`loading-skeleton-${id}`}
                  >
                    <Skeleton
                      variant="rectangular"
                      height={350}
                      sx={{ borderRadius: 3 }}
                    />
                  </Grid>
                ))}
              </Grid>
            </Box>
          ) : (
            <>
              <Box
                sx={{
                  mb: 3,
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <Typography variant="body1" color="text.secondary">
                  Showing {products.length} products
                  {selectedProducts.length > 0 &&
                    ` Ã¢â‚¬Â¢ ${selectedProducts.length} selected`}
                </Typography>
                {selectedProducts.length > 0 && (
                  <Button
                    variant="contained"
                    startIcon={<Compare />}
                    component={Link}
                    to={`/compare?products=${selectedProducts.join(",")}`}
                    sx={{ borderRadius: 2 }}
                  >
                    Compare Selected ({selectedProducts.length})
                  </Button>
                )}
              </Box>

              <AnimatePresence mode="wait">
                {viewMode === "grid" ? (
                  <Grid container spacing={3} component={motion.div} layout>
                    {products.map((product, index) => (
                      <Grid
                        item
                        xs={12}
                        sm={6}
                        md={6}
                        lg={4}
                        xl={3}
                        key={product.id}
                      >
                        <ProductCard
                          product={product}
                          index={index}
                          selectedProducts={selectedProducts}
                          onSelect={handleProductSelect}
                          isAuthenticated={isAuthenticated}
                          onToggleWishlist={handleToggleWishlist}
                          onAddToCart={handleAddToCart}
                          onQuickView={setQuickViewProduct}
                          onHoverPreview={handleHoverPreview}
                          onBuyNow={handleBuyNow}
                          navigate={navigate}
                        />
                      </Grid>
                    ))}
                  </Grid>
                ) : (
                  <Box component={motion.div} layout>
                    {products.map((product, index) => (
                      <ProductListItem
                        key={product.id}
                        product={product}
                        selectedProducts={selectedProducts}
                        onSelect={handleProductSelect}
                        onAddToCart={handleAddToCart}
                        onQuickView={setQuickViewProduct}
                      />
                    ))}
                  </Box>
                )}
              </AnimatePresence>

              {/* Load More Button */}
              {hasNextPage && (
                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "center",
                    mt: 6,
                    mb: 4,
                  }}
                >
                  <Button
                    variant="outlined"
                    size="large"
                    onClick={loadMore}
                    disabled={loadingMore}
                    startIcon={
                      loadingMore ? (
                        <CircularProgress size={20} />
                      ) : (
                        <ExpandMore />
                      )
                    }
                    sx={{
                      borderRadius: 3,
                      px: 4,
                      py: 1.5,
                      fontWeight: 600,
                      borderWidth: 2,
                      "&:hover": {
                        borderWidth: 2,
                        transform: "translateY(-2px)",
                        boxShadow: 3,
                      },
                      transition: "all 0.3s ease",
                    }}
                  >
                    {loadingMore ? "Loading..." : "Load More Products"}
                  </Button>
                </Box>
              )}
            </>
          )}
        </Grid>
      </Grid>

      {/* Floating Action Buttons */}
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
        {/* Compare Button */}
        {selectedProducts.length > 1 && (
          <Fab
            color="primary"
            size="medium"
            sx={{
              borderRadius: 3,
              boxShadow: 4,
              "&:hover": {
                transform: "scale(1.1)",
              },
            }}
            component={Link}
            to={`/compare?products=${selectedProducts.join(",")}`}
          >
            <Badge badgeContent={selectedProducts.length} color="secondary">
              <Compare />
            </Badge>
          </Fab>
        )}

        {/* Quick Cart Access */}
        {cart?.item_count > 0 && (
          <Fab
            color="secondary"
            size="medium"
            sx={{
              borderRadius: 3,
              boxShadow: 4,
              "&:hover": {
                transform: "scale(1.1)",
              },
            }}
            component={Link}
            to="/cart"
          >
            <Badge badgeContent={cart.item_count} color="primary">
              <ShoppingCart />
            </Badge>
          </Fab>
        )}

        {/* Scroll to Top */}
        <Fab
          color="default"
          size="small"
          sx={{
            borderRadius: 3,
            boxShadow: 4,
            backgroundColor: "background.paper",
            "&:hover": {
              transform: "scale(1.1)",
              backgroundColor: "grey.100",
            },
          }}
          onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
        >
          <ExpandLess />
        </Fab>
      </Box>

      <FiltersDrawer
        filtersOpen={filtersOpen}
        setFiltersOpen={setFiltersOpen}
        priceRange={priceRange}
        handlePriceRangeChange={handlePriceRangeChange}
        filters={filters}
        handleFilterChange={handleFilterChange}
        categories={categories}
        brands={brands}
        handleBrandChange={handleBrandChange}
        clearFilters={clearFilters}
      />
      <QuickViewDialog
        quickViewProduct={quickViewProduct}
        setQuickViewProduct={setQuickViewProduct}
        handleAddToCart={handleAddToCart}
        handleBuyNow={handleBuyNow}
      />

      {/* Hover Preview Popover */}
      <Popover
        open={!!hoverPreview.product}
        anchorEl={hoverPreview.anchorEl}
        onClose={() => setHoverPreview({ product: null, anchorEl: null })}
        anchorOrigin={{
          vertical: "center",
          horizontal: "right",
        }}
        transformOrigin={{
          vertical: "center",
          horizontal: "left",
        }}
        disableRestoreFocus
        sx={{
          pointerEvents: "none",
          "& .MuiPopover-paper": {
            pointerEvents: "auto",
            borderRadius: 3,
            boxShadow: "0 25px 50px rgba(0,0,0,0.15)",
            border: "1px solid",
            borderColor: "divider",
            maxWidth: 350,
            overflow: "visible",
          },
        }}
      >
        {hoverPreview.product && (
          <Box sx={{ p: 0, position: "relative" }}>
            {/* Close button */}
            <IconButton
              onClick={() => setHoverPreview({ product: null, anchorEl: null })}
              sx={{
                position: "absolute",
                top: 8,
                right: 8,
                zIndex: 1,
                backgroundColor: "rgba(255,255,255,0.9)",
                backdropFilter: "blur(4px)",
                "&:hover": {
                  backgroundColor: "white",
                },
              }}
              size="small"
            >
              <Clear fontSize="small" />
            </IconButton>

            <Box sx={{ p: 2 }}>
              <Box
                component="img"
                src={hoverPreview.product.image || "/placeholder.png"}
                alt={hoverPreview.product.name}
                sx={{
                  width: "100%",
                  height: 180,
                  objectFit: "contain",
                  borderRadius: 2,
                  mb: 2,
                  transition: "transform 0.3s ease",
                  "&:hover": {
                    transform: "scale(1.05)",
                  },
                }}
              />
              <Typography
                variant="h6"
                fontWeight="bold"
                gutterBottom
                sx={{ pr: 3 }}
              >
                {hoverPreview.product.name}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                {hoverPreview.product.category?.name} Ã¢â‚¬Â¢{" "}
                {hoverPreview.product.vendor?.name}
              </Typography>
              <Box
                sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}
              >
                <Typography variant="h6" color="primary" fontWeight="bold">
                  Ã¢â€šÂ¹{hoverPreview.product.price}
                </Typography>
                {hoverPreview.product.mrp &&
                  hoverPreview.product.mrp > hoverPreview.product.price && (
                    <Typography
                      variant="body2"
                      sx={{ textDecoration: "line-through" }}
                      color="text.secondary"
                    >
                      Ã¢â€šÂ¹{hoverPreview.product.mrp}
                    </Typography>
                  )}
                {hoverPreview.product.discount_percentage > 0 && (
                  <Chip
                    label={`${hoverPreview.product.discount_percentage}% OFF`}
                    color="error"
                    size="small"
                    sx={{ fontSize: "0.7rem", height: 20 }}
                  />
                )}
              </Box>
              <Box
                sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}
              >
                <Rating
                  value={hoverPreview.product.average_rating || 0}
                  readOnly
                  size="small"
                  precision={0.1}
                />
                <Typography variant="body2" color="text.secondary">
                  ({hoverPreview.product.review_count || 0})
                </Typography>
              </Box>
              <Typography
                variant="body2"
                color="text.secondary"
                sx={{ mb: 2, lineHeight: 1.4 }}
              >
                {hoverPreview.product.description?.substring(0, 120) ||
                  "No description available."}
                {hoverPreview.product.description?.length > 120 && "..."}
              </Typography>
              <Box
                sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2 }}
              >
                {hoverPreview.product.in_stock ? (
                  <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
                    <Verified sx={{ color: "success.main", fontSize: 16 }} />
                    <Typography
                      variant="caption"
                      color="success.main"
                      fontWeight="600"
                    >
                      In Stock
                    </Typography>
                  </Box>
                ) : (
                  <Typography
                    variant="caption"
                    color="error.main"
                    fontWeight="600"
                  >
                    Out of Stock
                  </Typography>
                )}
              </Box>

              {/* Quick Actions */}
              <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
                <Button
                  variant="contained"
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleAddToCart(hoverPreview.product.id);
                    setHoverPreview({ product: null, anchorEl: null });
                  }}
                  disabled={!hoverPreview.product.in_stock}
                  startIcon={<ShoppingCart />}
                  sx={{ flex: 1, minWidth: 0 }}
                >
                  Add to Cart
                </Button>
                <Tooltip title="Quick View">
                  <IconButton
                    onClick={(e) => {
                      e.stopPropagation();
                      setQuickViewProduct(hoverPreview.product);
                      setHoverPreview({ product: null, anchorEl: null });
                    }}
                    color="primary"
                    size="small"
                    sx={{
                      border: 1,
                      borderColor: "primary.main",
                      borderRadius: 1,
                      "&:hover": {
                        backgroundColor: "primary.main",
                        color: "white",
                      },
                    }}
                  >
                    <Visibility />
                  </IconButton>
                </Tooltip>
                {isAuthenticated && (
                  <Tooltip
                    title={
                      hoverPreview.product.is_in_wishlist
                        ? "Remove from Wishlist"
                        : "Add to Wishlist"
                    }
                  >
                    <IconButton
                      onClick={(e) => {
                        e.stopPropagation();
                        handleToggleWishlist(
                          hoverPreview.product.id,
                          hoverPreview.product.is_in_wishlist,
                        );
                      }}
                      size="small"
                      sx={{
                        border: 1,
                        borderColor: "divider",
                        borderRadius: 1,
                        "&:hover": {
                          backgroundColor: hoverPreview.product.is_in_wishlist
                            ? "error.main"
                            : "primary.main",
                          color: "white",
                        },
                      }}
                    >
                      {hoverPreview.product.is_in_wishlist ? (
                        <Favorite />
                      ) : (
                        <FavoriteBorder />
                      )}
                    </IconButton>
                  </Tooltip>
                )}
                <Tooltip title="View Details">
                  <IconButton
                    component={Link}
                    to={`/products/${hoverPreview.product.slug}`}
                    onClick={() =>
                      setHoverPreview({ product: null, anchorEl: null })
                    }
                    size="small"
                    sx={{
                      border: 1,
                      borderColor: "divider",
                      borderRadius: 1,
                      "&:hover": {
                        backgroundColor: "secondary.main",
                        color: "white",
                      },
                    }}
                  >
                    <Visibility />
                  </IconButton>
                </Tooltip>
              </Box>
            </Box>
          </Box>
        )}
      </Popover>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      >
        <Alert
          onClose={handleCloseSnackbar}
          severity={snackbar.severity}
          sx={{ width: "100%", borderRadius: 2 }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

const FiltersDrawer = React.memo(
  ({
    filtersOpen,
    setFiltersOpen,
    priceRange,
    handlePriceRangeChange,
    filters,
    handleFilterChange,
    categories,
    brands,
    handleBrandChange,
    clearFilters,
  }) => (
    <Drawer
      anchor="left"
      open={filtersOpen}
      onClose={() => setFiltersOpen(false)}
      sx={{
        "& .MuiDrawer-paper": {
          width: { xs: "100%", sm: 350 },
          p: 2,
        },
      }}
    >
      <Box
        sx={{
          mb: 2,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <Typography
          variant="h6"
          fontWeight="bold"
          sx={{ display: { xs: "flex", sm: "none" } }}
        >
          Filters
        </Typography>
        <Button
          startIcon={<Clear />}
          onClick={() => setFiltersOpen(false)}
          sx={{ display: { xs: "flex", sm: "none" } }}
        >
          Close
        </Button>
      </Box>
      <Divider sx={{ mb: 2 }} />

      <Box sx={{ overflowY: "auto", flexGrow: 1 }}>
        <Accordion defaultExpanded sx={{ mb: 2 }}>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Typography fontWeight="600">Price Range</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Slider
              value={priceRange}
              onChange={handlePriceRangeChange}
              valueLabelDisplay="auto"
              min={0}
              max={10000}
              step={100}
              sx={{ color: "primary.main" }}
            />
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Ã¢â€šÂ¹{priceRange[0]} - Ã¢â€šÂ¹{priceRange[1]}
            </Typography>
          </AccordionDetails>
        </Accordion>

        <Accordion sx={{ mb: 2 }}>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Typography fontWeight="600">Category</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <FormControl fullWidth size="small">
              <InputLabel>Category</InputLabel>
              <Select
                value={filters.category}
                onChange={(e) => handleFilterChange("category", e.target.value)}
                sx={{ borderRadius: 2 }}
              >
                <MenuItem value="">All Categories</MenuItem>
                {categories.map((category) => (
                  <MenuItem key={category.id} value={category.slug}>
                    {category.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </AccordionDetails>
        </Accordion>

        <Accordion sx={{ mb: 2 }}>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Typography fontWeight="600">Brands</Typography>
          </AccordionSummary>
          <AccordionDetails>
            {brands.slice(0, 15).map((brand) => (
              <FormControlLabel
                key={brand}
                control={
                  <Checkbox
                    checked={filters.brands.includes(brand)}
                    onChange={(e) => handleBrandChange(brand, e.target.checked)}
                    size="small"
                  />
                }
                label={brand}
                sx={{ width: "100%", mb: 0.5 }}
              />
            ))}
          </AccordionDetails>
        </Accordion>

        <Accordion sx={{ mb: 2 }}>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Typography fontWeight="600">Rating</Typography>
          </AccordionSummary>
          <AccordionDetails>
            {[4, 3, 2, 1].map((rating) => (
              <FormControlLabel
                key={rating}
                control={
                  <Checkbox
                    checked={filters.min_rating === rating.toString()}
                    onChange={(e) =>
                      handleFilterChange(
                        "min_rating",
                        e.target.checked ? rating.toString() : "",
                      )
                    }
                    size="small"
                  />
                }
                label={`${rating}+ Stars`}
              />
            ))}
          </AccordionDetails>
        </Accordion>

        <Accordion>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Typography fontWeight="600">Availability</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <FormControlLabel
              control={
                <Checkbox
                  checked={filters.in_stock === "true"}
                  onChange={(e) =>
                    handleFilterChange(
                      "in_stock",
                      e.target.checked ? "true" : "",
                    )
                  }
                  size="small"
                />
              }
              label="In Stock Only"
            />
          </AccordionDetails>
        </Accordion>
      </Box>

      <Box sx={{ mt: 2, pt: 2, borderTop: 1, borderColor: "divider" }}>
        <Button
          variant="outlined"
          fullWidth
          onClick={clearFilters}
          startIcon={<Clear />}
          sx={{ borderRadius: 2 }}
        >
          Clear All Filters
        </Button>
      </Box>
    </Drawer>
  ),
);

FiltersDrawer.propTypes = {
  filtersOpen: PropTypes.bool.isRequired,
  setFiltersOpen: PropTypes.func.isRequired,
  priceRange: PropTypes.array.isRequired,
  handlePriceRangeChange: PropTypes.func.isRequired,
  filters: PropTypes.object.isRequired,
  handleFilterChange: PropTypes.func.isRequired,
  categories: PropTypes.array.isRequired,
  brands: PropTypes.array.isRequired,
  handleBrandChange: PropTypes.func.isRequired,
  clearFilters: PropTypes.func.isRequired,
};

const QuickViewDialog = React.memo(
  ({
    quickViewProduct,
    setQuickViewProduct,
    handleAddToCart,
    handleBuyNow,
  }) => (
    <Dialog
      open={!!quickViewProduct}
      onClose={() => setQuickViewProduct(null)}
      maxWidth="md"
      fullWidth
      sx={{
        "& .MuiDialog-paper": {
          borderRadius: 3,
        },
      }}
    >
      {quickViewProduct && (
        <>
          <DialogTitle sx={{ pb: 1 }}>
            <Typography variant="h5" fontWeight="bold">
              {quickViewProduct.name}
            </Typography>
          </DialogTitle>
          <DialogContent>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Box
                  component="img"
                  src={quickViewProduct.image || "/placeholder.png"}
                  alt={quickViewProduct.name}
                  sx={{
                    width: "100%",
                    height: "auto",
                    borderRadius: 2,
                    boxShadow: 2,
                  }}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="body1" color="text.secondary" gutterBottom>
                  {quickViewProduct.category?.name} Ã¢â‚¬Â¢{" "}
                  {quickViewProduct.vendor?.name}
                </Typography>
                <Box
                  sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2 }}
                >
                  <Typography variant="h4" color="primary" fontWeight="bold">
                    Ã¢â€šÂ¹{quickViewProduct.price}
                  </Typography>
                  {quickViewProduct.mrp &&
                    quickViewProduct.mrp > quickViewProduct.price && (
                      <Typography
                        variant="h6"
                        sx={{ textDecoration: "line-through" }}
                        color="text.secondary"
                      >
                        Ã¢â€šÂ¹{quickViewProduct.mrp}
                      </Typography>
                    )}
                </Box>
                <Box
                  sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2 }}
                >
                  <Rating
                    value={quickViewProduct.average_rating || 0}
                    readOnly
                    precision={0.1}
                  />
                  <Typography variant="body2">
                    ({quickViewProduct.review_count || 0} reviews)
                  </Typography>
                </Box>
                <Typography variant="body1" paragraph>
                  {quickViewProduct.description || "No description available."}
                </Typography>
                <Box
                  sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2 }}
                >
                  {quickViewProduct.in_stock ? (
                    <>
                      <Verified sx={{ color: "success.main" }} />
                      <Typography variant="body2" color="success.main">
                        In Stock
                      </Typography>
                    </>
                  ) : (
                    <Typography variant="body2" color="error.main">
                      Out of Stock
                    </Typography>
                  )}
                </Box>
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions sx={{ p: 3 }}>
            <Button onClick={() => setQuickViewProduct(null)}>Close</Button>
            <Button
              variant="contained"
              color="secondary"
              onClick={() => {
                handleBuyNow(quickViewProduct.id);
                setQuickViewProduct(null);
              }}
              disabled={!quickViewProduct.in_stock}
              startIcon={<FlashOn />}
            >
              Buy Now
            </Button>
            <Button
              variant="contained"
              onClick={() => {
                handleAddToCart(quickViewProduct.id);
                setQuickViewProduct(null);
              }}
              disabled={!quickViewProduct.in_stock}
              startIcon={<ShoppingCart />}
            >
              Add to Cart
            </Button>
          </DialogActions>
        </>
      )}
    </Dialog>
  ),
);

QuickViewDialog.propTypes = {
  quickViewProduct: PropTypes.object,
  setQuickViewProduct: PropTypes.func.isRequired,
  handleAddToCart: PropTypes.func.isRequired,
  handleBuyNow: PropTypes.func.isRequired,
};

export default ProductList;
