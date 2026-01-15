import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  Container,
  Typography,
  Card,
  CardContent,
  Box,
  Button,
  Grid,
  IconButton,
  TextField,
  Divider,
  Alert,
  Checkbox,
  Chip,
  Paper,
  Breadcrumbs,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from "@mui/material";
import {
  Add,
  Remove,
  Delete,
  ShoppingCart,
  Security,
  ExpandMore,
  Warning,
  Save,
  RestoreFromTrash,
} from "@mui/icons-material";
import { motion, AnimatePresence } from "framer-motion";
import { useCart } from "../../utils/CartContext";
import { useAuth } from "../../utils/AuthContext";

const Cart = () => {
  const { cart, updateCartItem, removeFromCart, clearCart, loading } =
    useCart();
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const [selectedItems, setSelectedItems] = useState([]);
  const [bulkQuantity, setBulkQuantity] = useState(1);
  const [clearDialogOpen, setClearDialogOpen] = useState(false);
  const [couponCode, setCouponCode] = useState("");
  const [appliedCoupon] = useState(null);

  const handleQuantityChange = async (productId, newQuantity) => {
    if (newQuantity < 1) return;

    const result = await updateCartItem(productId, newQuantity);
    if (!result.success) {
      alert(result.error);
    }
  };

  const handleRemoveItem = async (productId) => {
    const result = await removeFromCart(productId);
    if (!result.success) {
      alert(result.error);
    }
  };

  const handleClearCart = async () => {
    const result = await clearCart();
    if (!result.success) {
      alert(result.error);
    }
    setClearDialogOpen(false);
  };

  const handleCheckout = () => {
    if (!isAuthenticated) {
      navigate("/login", { state: { from: "/checkout" } });
      return;
    }
    if (selectedItems.length === 0) {
      alert("Please select items to checkout");
      return;
    }
    navigate("/checkout");
  };

  const handleSelectItem = (itemId) => {
    setSelectedItems((prev) =>
      prev.includes(itemId)
        ? prev.filter((id) => id !== itemId)
        : [...prev, itemId],
    );
  };

  const handleSelectAll = () => {
    if (selectedItems.length === cart.items.length) {
      setSelectedItems([]);
    } else {
      setSelectedItems(cart.items.map((item) => item.id));
    }
  };

  const handleBulkQuantityUpdate = async () => {
    if (selectedItems.length === 0) return;

    for (const itemId of selectedItems) {
      await updateCartItem(itemId, bulkQuantity);
    }
    setSelectedItems([]);
  };

  const handleRemoveSelected = async () => {
    if (selectedItems.length === 0) return;

    for (const itemId of selectedItems) {
      await removeFromCart(itemId);
    }
    setSelectedItems([]);
  };

  const selectedTotal = cart.items
    .filter((item) => selectedItems.includes(item.id))
    .reduce((total, item) => total + item.total_price, 0);

  const selectedCount = selectedItems.length;

  if (cart.items.length === 0) {
    return (
      <Container maxWidth="lg" sx={{ py: 6 }}>
        <Breadcrumbs sx={{ mb: 4 }}>
          <Link to="/" style={{ textDecoration: "none", color: "inherit" }}>
            Home
          </Link>
          <Typography color="text.primary" fontWeight="500">
            Cart
          </Typography>
        </Breadcrumbs>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <Paper
            elevation={0}
            sx={{
              p: { xs: 4, md: 8 },
              textAlign: "center",
              borderRadius: 4,
              background: "linear-gradient(135deg, #f8fafc 0%, #ffffff 100%)",
              border: "1px solid",
              borderColor: "divider",
            }}
          >
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              <Box
                sx={{
                  width: 120,
                  height: 120,
                  mx: "auto",
                  mb: 4,
                  borderRadius: "50%",
                  background:
                    "linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, rgba(16, 185, 129, 0.1) 100%)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <ShoppingCart
                  sx={{ fontSize: 60, color: "primary.main", opacity: 0.7 }}
                />
              </Box>
            </motion.div>

            <Typography
              variant="h4"
              component="h1"
              gutterBottom
              fontWeight="800"
              sx={{ color: "text.primary", mb: 2 }}
            >
              Your Cart is Empty
            </Typography>
            <Typography
              variant="body1"
              color="text.secondary"
              sx={{ mb: 5, maxWidth: 400, mx: "auto", lineHeight: 1.7 }}
            >
              Looks like you haven't added anything to your cart yet. Discover
              quality agricultural products from trusted vendors.
            </Typography>

            <Box
              sx={{
                display: "flex",
                gap: 2,
                justifyContent: "center",
                flexWrap: "wrap",
              }}
            >
              <Button
                variant="contained"
                size="large"
                component={Link}
                to="/products"
                startIcon={<ShoppingCart />}
                sx={{
                  borderRadius: 3,
                  px: 5,
                  py: 1.5,
                  fontWeight: 700,
                  boxShadow: "0 8px 25px rgba(34, 197, 94, 0.25)",
                }}
              >
                Start Shopping
              </Button>
              <Button
                variant="outlined"
                size="large"
                component={Link}
                to="/vendors"
                sx={{
                  borderRadius: 3,
                  px: 5,
                  py: 1.5,
                  fontWeight: 600,
                  borderWidth: 2,
                  "&:hover": { borderWidth: 2 },
                }}
              >
                Find Vendors
              </Button>
            </Box>
          </Paper>
        </motion.div>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl">
      <Breadcrumbs sx={{ mb: 3 }}>
        <Link to="/" style={{ textDecoration: "none", color: "inherit" }}>
          Home
        </Link>
        <Typography color="text.primary">Shopping Cart</Typography>
      </Breadcrumbs>

      <Typography
        variant="h4"
        component="h1"
        gutterBottom
        sx={{ fontWeight: 700, mb: 4 }}
      >
        Shopping Cart ({cart.item_count} items)
      </Typography>

      <Grid container spacing={4}>
        {/* Cart Items */}
        <Grid item xs={12} lg={8}>
          <Card sx={{ borderRadius: 3, overflow: "hidden" }}>
            <CardContent sx={{ p: 0 }}>
              {/* Bulk Actions Header */}
              <Box
                sx={{
                  p: 3,
                  backgroundColor: "grey.50",
                  borderBottom: 1,
                  borderColor: "divider",
                }}
              >
                <Box
                  sx={{
                    display: "flex",
                    alignItems: "center",
                    gap: 2,
                    flexWrap: "wrap",
                  }}
                >
                  <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                    <Checkbox
                      checked={
                        selectedItems.length === cart.items.length &&
                        cart.items.length > 0
                      }
                      indeterminate={
                        selectedItems.length > 0 &&
                        selectedItems.length < cart.items.length
                      }
                      onChange={handleSelectAll}
                      inputProps={{ "aria-label": "Select all items" }}
                    />
                    <Typography variant="body2" fontWeight="600">
                      Select All ({cart.items.length})
                    </Typography>
                  </Box>

                  {selectedItems.length > 0 && (
                    <>
                      <Divider orientation="vertical" flexItem />
                      <Typography
                        variant="body2"
                        color="primary"
                        fontWeight="600"
                      >
                        {selectedCount} item{selectedCount > 1 ? "s" : ""}{" "}
                        selected
                      </Typography>

                      <Box
                        sx={{ display: "flex", gap: 1, alignItems: "center" }}
                      >
                        <TextField
                          size="small"
                          type="number"
                          label="Qty"
                          value={bulkQuantity}
                          onChange={(e) =>
                            setBulkQuantity(
                              Math.max(
                                1,
                                Number.parseInt(e.target.value, 10) || 1,
                              ),
                            )
                          }
                          inputProps={{ min: 1 }}
                          sx={{ width: 80 }}
                        />
                        <Button
                          size="small"
                          variant="outlined"
                          onClick={handleBulkQuantityUpdate}
                          startIcon={<Save />}
                        >
                          Update
                        </Button>
                        <Button
                          size="small"
                          variant="outlined"
                          color="error"
                          onClick={handleRemoveSelected}
                          startIcon={<Delete />}
                        >
                          Remove
                        </Button>
                      </Box>
                    </>
                  )}
                </Box>
              </Box>

              {/* Cart Items List */}
              <AnimatePresence>
                {cart.items.map((item, index) => (
                  <motion.div
                    key={item.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.3, delay: index * 0.05 }}
                  >
                    <Box sx={{ p: 3 }}>
                      <Grid container spacing={2} alignItems="center">
                        <Grid item>
                          <Checkbox
                            checked={selectedItems.includes(item.id)}
                            onChange={() => handleSelectItem(item.id)}
                            inputProps={{ "aria-label": `Select ${item.name}` }}
                          />
                        </Grid>

                        <Grid item xs={12} sm={3}>
                          <Box
                            component={Link}
                            to={`/products/${item.slug}`}
                            sx={{
                              display: "block",
                              textDecoration: "none",
                              "&:hover img": {
                                transform: "scale(1.05)",
                              },
                            }}
                          >
                            <Box
                              component="img"
                              src={item.image || "/placeholder.png"}
                              alt={item.name}
                              sx={{
                                width: "100%",
                                maxWidth: 120,
                                height: 80,
                                objectFit: "cover",
                                borderRadius: 1,
                                transition: "transform 0.3s ease",
                              }}
                            />
                          </Box>
                        </Grid>

                        <Grid item xs={12} sm={4}>
                          <Typography
                            variant="h6"
                            component={Link}
                            to={`/products/${item.slug}`}
                            sx={{
                              textDecoration: "none",
                              color: "inherit",
                              fontWeight: 600,
                              "&:hover": {
                                color: "primary.main",
                              },
                            }}
                          >
                            {item.name}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {item.vendor_name || "Unknown Vendor"}
                          </Typography>
                          <Box
                            sx={{
                              display: "flex",
                              alignItems: "center",
                              gap: 1,
                              mt: 1,
                            }}
                          >
                            <Typography
                              variant="body2"
                              color="primary"
                              fontWeight="600"
                            >
                              Ã¢â€šÂ¹{item.price} each
                            </Typography>
                            {item.discount_percentage > 0 && (
                              <Chip
                                label={`${item.discount_percentage}% off`}
                                size="small"
                                color="success"
                              />
                            )}
                          </Box>
                        </Grid>

                        <Grid item xs={12} sm={2}>
                          <Box
                            sx={{
                              display: "flex",
                              alignItems: "center",
                              border: 1,
                              borderColor: "grey.300",
                              borderRadius: 1,
                              width: "fit-content",
                            }}
                          >
                            <IconButton
                              size="small"
                              onClick={() =>
                                handleQuantityChange(item.id, item.quantity - 1)
                              }
                              disabled={loading}
                              aria-label={`Decrease quantity of ${item.name}`}
                            >
                              <Remove />
                            </IconButton>
                            <TextField
                              size="small"
                              value={item.quantity}
                              onChange={(e) => {
                                const value = Number.parseInt(
                                  e.target.value,
                                  10,
                                );
                                if (!Number.isNaN(value) && value > 0) {
                                  handleQuantityChange(item.id, value);
                                }
                              }}
                              inputProps={{
                                min: 1,
                                style: { textAlign: "center", width: 60 },
                                "aria-label": `Quantity of ${item.name}`,
                              }}
                              disabled={loading}
                              variant="standard"
                              sx={{
                                "& .MuiInput-root": {
                                  "&:before, &:after": { display: "none" },
                                },
                              }}
                            />
                            <IconButton
                              size="small"
                              onClick={() =>
                                handleQuantityChange(item.id, item.quantity + 1)
                              }
                              disabled={loading}
                              aria-label={`Increase quantity of ${item.name}`}
                            >
                              <Add />
                            </IconButton>
                          </Box>
                        </Grid>

                        <Grid item xs={12} sm={2}>
                          <Typography
                            variant="h6"
                            color="primary"
                            fontWeight="bold"
                          >
                            Ã¢â€šÂ¹{item.total_price.toFixed(2)}
                          </Typography>
                        </Grid>

                        <Grid item xs={12} sm={1}>
                          <Tooltip title="Remove from cart">
                            <IconButton
                              color="error"
                              onClick={() => handleRemoveItem(item.id)}
                              disabled={loading}
                              aria-label={`Remove ${item.name} from cart`}
                              sx={{
                                "&:hover": {
                                  backgroundColor: "error.main",
                                  color: "white",
                                },
                              }}
                            >
                              <Delete />
                            </IconButton>
                          </Tooltip>
                        </Grid>
                      </Grid>
                    </Box>
                    <Divider />
                  </motion.div>
                ))}
              </AnimatePresence>

              {/* Cart Actions */}
              <Box sx={{ p: 3, backgroundColor: "grey.50" }}>
                <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap" }}>
                  <Button
                    variant="outlined"
                    color="error"
                    onClick={() => setClearDialogOpen(true)}
                    disabled={loading}
                    startIcon={<RestoreFromTrash />}
                  >
                    Clear Cart
                  </Button>
                  <Button
                    variant="outlined"
                    component={Link}
                    to="/products"
                    startIcon={<ShoppingCart />}
                  >
                    Continue Shopping
                  </Button>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Order Summary */}
        <Grid item xs={12} lg={4}>
          <Card sx={{ borderRadius: 3, position: "sticky", top: 20 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom fontWeight="bold">
                Order Summary
              </Typography>
              <Divider sx={{ mb: 2 }} />

              <Box sx={{ mb: 2 }}>
                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    mb: 1,
                  }}
                >
                  <Typography>Items ({cart.item_count}):</Typography>
                  <Typography>Ã¢â€šÂ¹{cart.total_cost.toFixed(2)}</Typography>
                </Box>

                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    mb: 1,
                  }}
                >
                  <Typography>Shipping:</Typography>
                  <Typography color="success.main" fontWeight="500">
                    Free
                  </Typography>
                </Box>

                {appliedCoupon && (
                  <Box
                    sx={{
                      display: "flex",
                      justifyContent: "space-between",
                      mb: 1,
                    }}
                  >
                    <Typography>Coupon ({appliedCoupon.code}):</Typography>
                    <Typography color="success.main">
                      -Ã¢â€šÂ¹{appliedCoupon.discount.toFixed(2)}
                    </Typography>
                  </Box>
                )}

                <Divider sx={{ my: 2 }} />

                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    mb: 2,
                  }}
                >
                  <Typography variant="h6">Total:</Typography>
                  <Typography variant="h6" color="primary" fontWeight="bold">
                    Ã¢â€šÂ¹
                    {(cart.total_cost - (appliedCoupon?.discount || 0)).toFixed(
                      2,
                    )}
                  </Typography>
                </Box>
              </Box>

              {/* Coupon Code */}
              <Accordion sx={{ mb: 3 }}>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography fontWeight="600">Have a coupon?</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Box sx={{ display: "flex", gap: 1 }}>
                    <TextField
                      fullWidth
                      size="small"
                      placeholder="Enter coupon code"
                      value={couponCode}
                      onChange={(e) => setCouponCode(e.target.value)}
                    />
                    <Button variant="outlined" size="small">
                      Apply
                    </Button>
                  </Box>
                </AccordionDetails>
              </Accordion>

              {/* Delivery Info */}
              <Alert severity="info" sx={{ mb: 3, borderRadius: 2 }}>
                <Typography variant="body2" fontWeight="600" gutterBottom>
                  Free Delivery
                </Typography>
                <Typography variant="body2">
                  Enjoy free shipping on all orders. Delivery within 3-5
                  business days.
                </Typography>
              </Alert>

              <Button
                variant="contained"
                fullWidth
                size="large"
                onClick={handleCheckout}
                disabled={loading || selectedItems.length === 0}
                sx={{
                  borderRadius: 2,
                  py: 1.5,
                  fontWeight: 600,
                  fontSize: "1.1rem",
                }}
              >
                {selectedItems.length > 0
                  ? `Checkout Selected (${selectedCount}) - Ã¢â€šÂ¹${selectedTotal.toFixed(2)}`
                  : "Select Items to Checkout"}
              </Button>

              {!isAuthenticated && (
                <Alert severity="warning" sx={{ mt: 2, borderRadius: 2 }}>
                  <Typography variant="body2" fontWeight="600" gutterBottom>
                    Login Required
                  </Typography>
                  <Typography variant="body2">
                    Please login to proceed with checkout and access your saved
                    cart.
                  </Typography>
                </Alert>
              )}

              {/* Security Info */}
              <Box
                sx={{
                  mt: 3,
                  p: 2,
                  backgroundColor: "success.50",
                  borderRadius: 2,
                }}
              >
                <Box
                  sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}
                >
                  <Security color="success" />
                  <Typography
                    variant="body2"
                    fontWeight="600"
                    color="success.main"
                  >
                    Secure Checkout
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Your payment information is encrypted and secure.
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Clear Cart Dialog */}
      <Dialog
        open={clearDialogOpen}
        onClose={() => setClearDialogOpen(false)}
        sx={{
          "& .MuiDialog-paper": {
            borderRadius: 3,
          },
        }}
      >
        <DialogTitle sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          <Warning color="warning" />
          Clear Shopping Cart
        </DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to remove all items from your cart? This
            action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setClearDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleClearCart}
            color="error"
            variant="contained"
            startIcon={<Delete />}
          >
            Clear Cart
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Cart;
