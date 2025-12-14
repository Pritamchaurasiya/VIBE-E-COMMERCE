import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../utils/AuthContext';
import {
  Box, Button, CircularProgress, Dialog, DialogTitle, DialogContent, DialogActions,
  Typography, Divider, List, ListItem, ListItemText, TextField, FormControlLabel,
  Checkbox, Alert, Chip, useTheme
} from '@mui/material';
import { CreditCard, LocalShipping, VerifiedUser, Lock, ShoppingCartCheckout } from '@mui/icons-material';
import { motion } from 'framer-motion';
import { selectCartItems, selectCartTotalAmount, clearCart } from '../../features/cart/cartSlice';
import { selectCurrentUser } from '../../features/auth/authSlice';

const OneClickCheckout = ({ onSuccess, onError }) => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const theme = useTheme();
  const { isAuthenticated } = useAuth();

  const cartItems = useSelector(selectCartItems);
  const totalAmount = useSelector(selectCartTotalAmount);
  const currentUser = useSelector(selectCurrentUser);

  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [paymentMethod, setPaymentMethod] = useState('saved');
  const [shippingAddress, setShippingAddress] = useState(null);
  const [useDefaultAddress, setUseDefaultAddress] = useState(true);
  const [customAddress, setCustomAddress] = useState({
    address: '',
    city: '',
    state: '',
    zip: '',
    country: 'India'
  });

  // Mock saved payment methods and addresses (in a real app, these would come from user profile)
  const [savedPaymentMethods] = useState([
    { id: '1', type: 'credit_card', last4: '4242', brand: 'Visa', isDefault: true },
    { id: '2', type: 'credit_card', last4: '1234', brand: 'Mastercard', isDefault: false }
  ]);

  const [savedAddresses] = useState([
    {
      id: '1',
      name: 'Home',
      address: '123 Main Street',
      city: 'Bangalore',
      state: 'Karnataka',
      zip: '560001',
      country: 'India',
      isDefault: true
    },
    {
      id: '2',
      name: 'Office',
      address: '456 Tech Park',
      city: 'Bangalore',
      state: 'Karnataka',
      zip: '560037',
      country: 'India',
      isDefault: false
    }
  ]);

  useEffect(() => {
    if (useDefaultAddress) {
      const defaultAddress = savedAddresses.find(addr => addr.isDefault) || savedAddresses[0];
      setShippingAddress(defaultAddress);
    } else {
      setShippingAddress(null);
    }
  }, [useDefaultAddress, savedAddresses]);

  const handleOpen = () => {
    if (!isAuthenticated) {
      navigate('/login', { state: { from: window.location.pathname } });
      return;
    }
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    setError(null);
  };

  const handlePaymentMethodChange = (methodId) => {
    setPaymentMethod(methodId);
  };

  const handleAddressChange = (addressId) => {
    const selectedAddress = savedAddresses.find(addr => addr.id === addressId);
    setShippingAddress(selectedAddress);
    setUseDefaultAddress(false);
  };

  const handleCustomAddressChange = (e) => {
    const { name, value } = e.target;
    setCustomAddress(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async () => {
    if (!shippingAddress && !useDefaultAddress) {
      setError('Please select a shipping address or use your default address');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // In a real app, this would call your backend API to process the order
      const orderData = {
        userId: currentUser?.id,
        items: cartItems.map(item => ({
          productId: item.id,
          quantity: item.quantity,
          price: item.price
        })),
        totalAmount: totalAmount,
        paymentMethod: paymentMethod,
        shippingAddress: shippingAddress || customAddress,
        orderType: 'one_click'
      };

      // Simulate API call
      console.log('Processing one-click checkout:', orderData);

      // Mock API delay
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Clear cart after successful checkout
      dispatch(clearCart());

      // Call success callback
      if (onSuccess) onSuccess(orderData);

      // Navigate to order confirmation
      navigate('/orders/confirmation', {
        state: {
          orderId: 'ORD-' + Math.random().toString(36).substr(2, 9).toUpperCase(),
          totalAmount: totalAmount,
          items: cartItems
        }
      });

    } catch (err) {
      console.error('Checkout failed:', err);
      setError(err.message || 'Failed to process your order. Please try again.');
      if (onError) onError(err);
    } finally {
      setLoading(false);
    }
  };

  const getDefaultPaymentMethod = () => {
    return savedPaymentMethods.find(method => method.isDefault) || savedPaymentMethods[0];
  };

  const containerVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        type: 'spring',
        stiffness: 100,
        damping: 12,
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 10 },
    visible: { opacity: 1, y: 0 }
  };

  return (
    <>
      <Button
        variant="contained"
        color="primary"
        onClick={handleOpen}
        startIcon={<ShoppingCartCheckout />}
        sx={{
          borderRadius: 3,
          py: 1.5,
          px: 3,
          fontWeight: 'bold',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
        }}
        disabled={cartItems.length === 0 || !isAuthenticated}
      >
        One-Click Checkout
      </Button>

      <Dialog
        open={open}
        onClose={handleClose}
        fullWidth
        maxWidth="md"
        PaperProps={{
          sx: {
            borderRadius: 4,
            overflow: 'hidden'
          }
        }}
      >
        <DialogTitle sx={{ bgcolor: 'primary.main', color: 'white', p: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <ShoppingCartCheckout fontSize="large" />
            <Typography variant="h5" fontWeight="bold">
              One-Click Checkout
            </Typography>
          </Box>
        </DialogTitle>

        <DialogContent sx={{ p: 0 }}>
          <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="visible"
          >
            {/* Order Summary */}
            <Box sx={{ p: 3, bgcolor: 'background.paper' }}>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Order Summary
              </Typography>

              <List sx={{ mb: 2 }}>
                {cartItems.slice(0, 3).map((item, index) => (
                  <motion.div key={index} variants={itemVariants}>
                    <ListItem sx={{ py: 1 }}>
                      <ListItemText
                        primary={
                          <Typography variant="body1" fontWeight="medium">
                            {item.name}
                          </Typography>
                        }
                        secondary={
                          <Typography variant="body2" color="text.secondary">
                            {item.quantity} x ₹{item.price.toFixed(2)}
                          </Typography>
                        }
                      />
                      <Typography variant="body1" fontWeight="bold">
                        ₹{(item.quantity * item.price).toFixed(2)}
                      </Typography>
                    </ListItem>
                    {index < cartItems.slice(0, 3).length - 1 && <Divider />}
                  </motion.div>
                ))}

                {cartItems.length > 3 && (
                  <ListItem>
                    <ListItemText
                      primary={
                        <Typography variant="body2" color="text.secondary">
                          and {cartItems.length - 3} more items
                        </Typography>
                      }
                    />
                  </ListItem>
                )}
              </List>

              <Divider sx={{ my: 2 }} />

              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body1" fontWeight="medium">
                  Subtotal:
                </Typography>
                <Typography variant="body1" fontWeight="medium">
                  ₹{totalAmount.toFixed(2)}
                </Typography>
              </Box>

              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body1" fontWeight="medium">
                  Shipping:
                </Typography>
                <Typography variant="body1" fontWeight="medium" color="success.main">
                  FREE
                </Typography>
              </Box>

              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body1" fontWeight="medium">
                  Taxes:
                </Typography>
                <Typography variant="body1" fontWeight="medium">
                  Included
                </Typography>
              </Box>

              <Divider sx={{ my: 2 }} />

              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="h6" fontWeight="bold">
                  Total:
                </Typography>
                <Typography variant="h6" fontWeight="bold" color="primary.main">
                  ₹{totalAmount.toFixed(2)}
                </Typography>
              </Box>
            </Box>

            {/* Payment Method */}
            <Box sx={{ p: 3, bgcolor: 'grey.50' }}>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Payment Method
              </Typography>

              <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                {savedPaymentMethods.map((method) => (
                  <motion.div
                    key={method.id}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <Card
                      onClick={() => handlePaymentMethodChange(method.id)}
                      sx={{
                        p: 2,
                        cursor: 'pointer',
                        border: paymentMethod === method.id ? '2px solid' : '1px solid',
                        borderColor: paymentMethod === method.id ? 'primary.main' : 'divider',
                        backgroundColor: paymentMethod === method.id ? 'action.selected' : 'background.paper',
                        width: 180
                      }}
                    >
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <CreditCard color={paymentMethod === method.id ? 'primary' : 'action'} />
                        <Typography variant="body2" fontWeight="medium">
                          {method.brand} ••••{method.last4}
                        </Typography>
                      </Box>
                      {method.isDefault && (
                        <Chip label="Default" size="small" sx={{ mt: 1, fontSize: '0.6rem' }} />
                      )}
                    </Card>
                  </motion.div>
                ))}
              </Box>

              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, color: 'text.secondary' }}>
                <Lock fontSize="small" />
                <Typography variant="body2">
                  All transactions are secure and encrypted
                </Typography>
              </Box>
            </Box>

            {/* Shipping Address */}
            <Box sx={{ p: 3, bgcolor: 'background.paper' }}>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Shipping Address
              </Typography>

              <Box sx={{ mb: 2 }}>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={useDefaultAddress}
                      onChange={(e) => setUseDefaultAddress(e.target.checked)}
                      color="primary"
                    />
                  }
                  label="Use my default shipping address"
                />
              </Box>

              {!useDefaultAddress && (
                <>
                  <Typography variant="subtitle2" fontWeight="medium" gutterBottom>
                    Saved Addresses
                  </Typography>

                  <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                    {savedAddresses.map((address) => (
                      <motion.div
                        key={address.id}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                      >
                        <Card
                          onClick={() => handleAddressChange(address.id)}
                          sx={{
                            p: 2,
                            cursor: 'pointer',
                            border: shippingAddress?.id === address.id ? '2px solid' : '1px solid',
                            borderColor: shippingAddress?.id === address.id ? 'primary.main' : 'divider',
                            backgroundColor: shippingAddress?.id === address.id ? 'action.selected' : 'background.paper',
                            width: 180
                          }}
                        >
                          <Typography variant="body2" fontWeight="medium" gutterBottom>
                            {address.name}
                          </Typography>
                          <Typography variant="caption" display="block" gutterBottom>
                            {address.address}
                          </Typography>
                          <Typography variant="caption" display="block">
                            {address.city}, {address.state} {address.zip}
                          </Typography>
                          {address.isDefault && (
                            <Chip label="Default" size="small" sx={{ mt: 1, fontSize: '0.6rem' }} />
                          )}
                        </Card>
                      </motion.div>
                    ))}
                  </Box>

                  <Divider sx={{ my: 2 }} />

                  <Typography variant="subtitle2" fontWeight="medium" gutterBottom>
                    Or use a different address
                  </Typography>

                  <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
                    <TextField
                      label="Address"
                      name="address"
                      value={customAddress.address}
                      onChange={handleCustomAddressChange}
                      size="small"
                      fullWidth
                    />
                    <TextField
                      label="City"
                      name="city"
                      value={customAddress.city}
                      onChange={handleCustomAddressChange}
                      size="small"
                      fullWidth
                    />
                    <TextField
                      label="State"
                      name="state"
                      value={customAddress.state}
                      onChange={handleCustomAddressChange}
                      size="small"
                      fullWidth
                    />
                    <TextField
                      label="ZIP Code"
                      name="zip"
                      value={customAddress.zip}
                      onChange={handleCustomAddressChange}
                      size="small"
                      fullWidth
                    />
                  </Box>
                </>
              )}

              {shippingAddress && (
                <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 2 }}>
                  <Typography variant="body2" fontWeight="medium" gutterBottom>
                    Selected Address
                  </Typography>
                  <Typography variant="body2">
                    {shippingAddress.name && `${shippingAddress.name}: `}
                    {shippingAddress.address}, {shippingAddress.city}, {shippingAddress.state} {shippingAddress.zip}
                  </Typography>
                </Box>
              )}
            </Box>

            {/* Security and Guarantees */}
            <Box sx={{ p: 3, bgcolor: 'grey.50' }}>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Your Purchase is Protected
              </Typography>

              <Box sx={{ display: 'flex', gap: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <VerifiedUser color="success" />
                  <Typography variant="body2">100% Authentic Products</Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <LocalShipping color="primary" />
                  <Typography variant="body2">Fast & Reliable Delivery</Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Lock color="secondary" />
                  <Typography variant="body2">Secure Payment</Typography>
                </Box>
              </Box>
            </Box>
          </motion.div>
        </DialogContent>

        <DialogActions sx={{ p: 3, bgcolor: 'grey.50' }}>
          {error && (
            <Alert severity="error" sx={{ flex: 1, mr: 2 }}>
              {error}
            </Alert>
          )}

          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              onClick={handleClose}
              variant="outlined"
              disabled={loading}
              sx={{ borderRadius: 2 }}
            >
              Cancel
            </Button>

            <Button
              onClick={handleSubmit}
              variant="contained"
              color="primary"
              disabled={loading || cartItems.length === 0}
              startIcon={loading ? <CircularProgress size={20} /> : <ShoppingCartCheckout />}
              sx={{
                borderRadius: 2,
                px: 3,
                fontWeight: 'bold'
              }}
            >
              {loading ? 'Processing...' : `Complete Purchase - ₹${totalAmount.toFixed(2)}`}
            </Button>
          </Box>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default OneClickCheckout;