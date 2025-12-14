import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Dialog,
  DialogContent,
  IconButton,
  Box,
  Typography,
  Button,
  Rating,
  Chip,
  Divider,
  Grid,
  TextField,
  Alert,
} from "@mui/material";
import {
  Close,
  Add,
  Remove,
  ShoppingCart,
  Favorite,
  FavoriteBorder,
  Visibility,
  LocalShipping,
  Verified,
} from "@mui/icons-material";
import { motion, AnimatePresence } from "framer-motion";
import { useCart } from "../../utils/CartContext";
import { useAuth } from "../../utils/AuthContext";
import PropTypes from "prop-types";

/**
 * Quick View Modal for product preview without navigating to product page
 */
const ProductQuickView = ({ open, onClose, product }) => {
  const navigate = useNavigate();
  const { addToCart } = useCart();
  const { isAuthenticated } = useAuth();

  const [quantity, setQuantity] = useState(1);
  const [isWishlisted, setIsWishlisted] = useState(false);
  const [addedToCart, setAddedToCart] = useState(false);

  if (!product) return null;

  const handleAddToCart = async () => {
    try {
      await addToCart(product.id, quantity);
      setAddedToCart(true);
      setTimeout(() => setAddedToCart(false), 2000);
    } catch (error) {
      console.error("Failed to add to cart:", error);
    }
  };

  const handleToggleWishlist = async () => {
    if (!isAuthenticated) {
      console.warn("User must be authenticated to add to wishlist");
      return;
    }
    setIsWishlisted(!isWishlisted);
    // Wishlist API is called through context/service layer
  };

  const handleViewDetails = () => {
    onClose();
    navigate(`/products/${product.slug}`);
  };

  const decrementQuantity = () => {
    if (quantity > 1) setQuantity(quantity - 1);
  };

  const incrementQuantity = () => {
    if (quantity < (product.stock_quantity || 99)) {
      setQuantity(quantity + 1);
    }
  };

  const discount =
    product.mrp && product.mrp > product.price
      ? Math.round((1 - product.price / product.mrp) * 100)
      : 0;

  return (
    <AnimatePresence>
      {open && (
        <Dialog
          open={open}
          onClose={onClose}
          maxWidth="md"
          fullWidth
          PaperProps={{
            sx: {
              borderRadius: 3,
              overflow: "hidden",
            },
          }}
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            transition={{ duration: 0.2 }}
          >
            {/* Close Button */}
            <IconButton
              onClick={onClose}
              sx={{
                position: "absolute",
                top: 8,
                right: 8,
                zIndex: 1,
                bgcolor: "background.paper",
                "&:hover": { bgcolor: "grey.200" },
              }}
            >
              <Close />
            </IconButton>

            <DialogContent sx={{ p: 0 }}>
              <Grid container>
                {/* Product Image */}
                <Grid item xs={12} md={6}>
                  <Box
                    sx={{
                      position: "relative",
                      height: { xs: 300, md: 400 },
                      bgcolor: "grey.100",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      overflow: "hidden",
                    }}
                  >
                    {discount > 0 && (
                      <Chip
                        label={`-${discount}%`}
                        color="error"
                        size="small"
                        sx={{
                          position: "absolute",
                          top: 16,
                          left: 16,
                          fontWeight: "bold",
                        }}
                      />
                    )}
                    <motion.img
                      src={product.image || "/placeholder-product.jpg"}
                      alt={product.name}
                      style={{
                        maxWidth: "100%",
                        maxHeight: "100%",
                        objectFit: "contain",
                      }}
                      initial={{ scale: 1 }}
                      whileHover={{ scale: 1.05 }}
                      transition={{ duration: 0.3 }}
                    />
                  </Box>
                </Grid>

                {/* Product Details */}
                <Grid item xs={12} md={6}>
                  <Box sx={{ p: 3 }}>
                    {/* Category & Vendor */}
                    <Box sx={{ display: "flex", gap: 1, mb: 1 }}>
                      {product.category_name && (
                        <Chip
                          label={product.category_name}
                          size="small"
                          variant="outlined"
                          color="primary"
                        />
                      )}
                      {product.vendor_name && (
                        <Chip
                          icon={<Verified fontSize="small" />}
                          label={product.vendor_name}
                          size="small"
                          variant="outlined"
                        />
                      )}
                    </Box>

                    {/* Product Name */}
                    <Typography variant="h5" fontWeight="bold" gutterBottom>
                      {product.name}
                    </Typography>

                    {/* Rating */}
                    <Box
                      sx={{
                        display: "flex",
                        alignItems: "center",
                        gap: 1,
                        mb: 2,
                      }}
                    >
                      <Rating
                        value={product.average_rating || 4}
                        precision={0.5}
                        readOnly
                        size="small"
                      />
                      <Typography variant="body2" color="text.secondary">
                        ({product.review_count || 0} reviews)
                      </Typography>
                    </Box>

                    {/* Price */}
                    <Box
                      sx={{
                        display: "flex",
                        alignItems: "baseline",
                        gap: 1,
                        mb: 2,
                      }}
                    >
                      <Typography
                        variant="h4"
                        color="primary"
                        fontWeight="bold"
                      >
                        Ã¢â€šÂ¹{product.price}
                      </Typography>
                      {product.mrp && product.mrp > product.price && (
                        <Typography
                          variant="body1"
                          color="text.secondary"
                          sx={{ textDecoration: "line-through" }}
                        >
                          Ã¢â€šÂ¹{product.mrp}
                        </Typography>
                      )}
                    </Box>

                    {/* Stock Status */}
                    {product.stock_quantity !== undefined && (
                      <Box sx={{ mb: 2 }}>
                        {product.stock_quantity > 0 ? (
                          <Chip
                            icon={<LocalShipping fontSize="small" />}
                            label={`In Stock (${product.stock_quantity} available)`}
                            color="success"
                            size="small"
                          />
                        ) : (
                          <Chip
                            label="Out of Stock"
                            color="error"
                            size="small"
                          />
                        )}
                      </Box>
                    )}

                    <Divider sx={{ my: 2 }} />

                    {/* Short Description */}
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{
                        mb: 2,
                        display: "-webkit-box",
                        WebkitLineClamp: 3,
                        WebkitBoxOrient: "vertical",
                        overflow: "hidden",
                      }}
                    >
                      {product.short_description ||
                        product.description?.substring(0, 150)}
                    </Typography>

                    {/* Quantity Selector */}
                    <Box
                      sx={{
                        display: "flex",
                        alignItems: "center",
                        gap: 2,
                        mb: 3,
                      }}
                    >
                      <Typography variant="body2" fontWeight="medium">
                        Quantity:
                      </Typography>
                      <Box sx={{ display: "flex", alignItems: "center" }}>
                        <IconButton
                          size="small"
                          onClick={decrementQuantity}
                          disabled={quantity <= 1}
                        >
                          <Remove fontSize="small" />
                        </IconButton>
                        <TextField
                          value={quantity}
                          size="small"
                          inputProps={{
                            style: { textAlign: "center", width: 50 },
                            readOnly: true,
                          }}
                        />
                        <IconButton
                          size="small"
                          onClick={incrementQuantity}
                          disabled={quantity >= (product.stock_quantity || 99)}
                        >
                          <Add fontSize="small" />
                        </IconButton>
                      </Box>
                    </Box>

                    {/* Success Alert */}
                    {addedToCart && (
                      <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                      >
                        <Alert severity="success" sx={{ mb: 2 }}>
                          Added to cart successfully!
                        </Alert>
                      </motion.div>
                    )}

                    {/* Action Buttons */}
                    <Box sx={{ display: "flex", gap: 2 }}>
                      <Button
                        variant="contained"
                        size="large"
                        startIcon={<ShoppingCart />}
                        onClick={handleAddToCart}
                        disabled={product.stock_quantity === 0}
                        sx={{
                          flex: 1,
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
                        Add to Cart
                      </Button>
                      <IconButton
                        onClick={handleToggleWishlist}
                        sx={{
                          border: "1px solid",
                          borderColor: "divider",
                          borderRadius: 2,
                        }}
                      >
                        {isWishlisted ? (
                          <Favorite color="error" />
                        ) : (
                          <FavoriteBorder />
                        )}
                      </IconButton>
                    </Box>

                    {/* View Full Details */}
                    <Button
                      variant="text"
                      fullWidth
                      startIcon={<Visibility />}
                      onClick={handleViewDetails}
                      sx={{ mt: 2 }}
                    >
                      View Full Details
                    </Button>
                  </Box>
                </Grid>
              </Grid>
            </DialogContent>
          </motion.div>
        </Dialog>
      )}
    </AnimatePresence>
  );
};

ProductQuickView.propTypes = {
  open: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  product: PropTypes.shape({
    id: PropTypes.number,
    slug: PropTypes.string,
    name: PropTypes.string,
    image: PropTypes.string,
    price: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
    mrp: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
    category_name: PropTypes.string,
    vendor_name: PropTypes.string,
    average_rating: PropTypes.number,
    review_count: PropTypes.number,
    stock_quantity: PropTypes.number,
    short_description: PropTypes.string,
    description: PropTypes.string,
  }),
};

export default ProductQuickView;
