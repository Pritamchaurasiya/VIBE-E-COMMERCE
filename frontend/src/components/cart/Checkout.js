import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import {
  Container,
  Typography,
  Card,
  CardContent,
  Box,
  Button,
  Grid,
  TextField,
  FormControl,
  Alert,
  Divider,
  Stepper,
  Step,
  StepLabel,
  Paper,
  RadioGroup,
  FormControlLabel,
  Radio,
  Checkbox,
  Breadcrumbs,
} from "@mui/material";
import {
  Person,
  Payment,
  CheckCircle,
  CreditCard,
  AccountBalance,
} from "@mui/icons-material";
import { loadStripe } from "@stripe/stripe-js";
import { useCart } from "../../utils/CartContext";
import { useAuth } from "../../utils/AuthContext";
import { ordersAPI } from "../../services/api";

const steps = ["Shipping", "Payment", "Review"];

// Helper function to validate shipping fields
const validateShipping = (formData) => {
  const errors = {};
  if (!formData.first_name.trim()) errors.first_name = "First name is required";
  if (!formData.last_name.trim()) errors.last_name = "Last name is required";
  if (!formData.email.trim()) {
    errors.email = "Email is required";
  } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
    errors.email = "Email is invalid";
  }
  if (!formData.phone.trim()) errors.phone = "Phone number is required";
  if (!formData.address.trim()) errors.address = "Address is required";
  if (!formData.city.trim()) errors.city = "City is required";
  if (!formData.zipcode.trim()) errors.zipcode = "ZIP code is required";
  return errors;
};

// Helper function to validate payment fields
const validatePayment = (formData) => {
  const errors = {};
  if (formData.payment_method === "card") {
    if (!formData.card_number.trim())
      errors.card_number = "Card number is required";
    if (!formData.expiry_date.trim())
      errors.expiry_date = "Expiry date is required";
    if (!formData.cvv.trim()) errors.cvv = "CVV is required";
    if (!formData.cardholder_name.trim())
      errors.cardholder_name = "Cardholder name is required";
  }
  if (!formData.agree_terms)
    errors.agree_terms = "You must agree to the terms and conditions";
  return errors;
};

// Helper function to get button text
const getButtonText = (isLastStep, loading) => {
  if (!isLastStep) return "Next";
  return loading ? "Placing Order..." : "Place Order";
};

const Checkout = () => {
  const { cart, clearCart } = useCart();
  const { user } = useAuth();
  const navigate = useNavigate();

  const [activeStep, setActiveStep] = useState(0);
  const [completed, setCompleted] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [formData, setFormData] = useState({
    // Shipping Information
    first_name: user?.first_name || "",
    last_name: user?.last_name || "",
    email: user?.email || "",
    phone: "",
    company: "",
    address: "",
    address2: "",
    city: "",
    state: "",
    zipcode: "",

    // Payment Information
    payment_method: "cod",
    card_number: "",
    expiry_date: "",
    cvv: "",
    cardholder_name: "",

    // Additional
    delivery_instructions: "",
    create_account: false,
    subscribe_newsletter: true,
    agree_terms: false,
  });

  const [formErrors, setFormErrors] = useState({});

  const handleChange = (e) => {
    const { name, value, checked, type } = e.target;
    setFormData({
      ...formData,
      [name]: type === "checkbox" ? checked : value,
    });

    // Clear error when user starts typing
    if (formErrors[name]) {
      setFormErrors({
        ...formErrors,
        [name]: "",
      });
    }
  };

  const validateStep = (step) => {
    let errors = {};

    if (step === 0) {
      errors = validateShipping(formData);
    } else if (step === 1) {
      errors = validatePayment(formData);
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(activeStep)) {
      setActiveStep((prevActiveStep) => prevActiveStep + 1);
      setCompleted({
        ...completed,
        [activeStep]: true,
      });
    }
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateStep(activeStep)) return;

    setLoading(true);
    setError("");

    try {
      // Create order
      const orderData = {
        ...formData,
        place: formData.city, // Django expects 'place' field
      };

      const response = await ordersAPI.createOrder(orderData);

      // Handle the response
      if (response.data.session) {
        // Stripe Payment
        const stripePromise = loadStripe(
          process.env.REACT_APP_STRIPE_PUBLIC_KEY,
        );
        const stripe = await stripePromise;
        const result = await stripe.redirectToCheckout({
          sessionId: response.data.session.id,
        });

        if (result.error) {
          setError(result.error.message);
        }
      } else if (response.data.success) {
        // COD or other success (no redirect needed)
        await clearCart();
        navigate("/orders");
      } else {
        throw new Error(response.data.error || "Failed to place order");
      }
    } catch (error) {
      setError(error.message || "Failed to place order. Please try again.");
      console.error("Checkout error:", error);
    } finally {
      setLoading(false);
    }
  };

  const getStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <Box>
            <Typography variant="h6" gutterBottom fontWeight="600">
              Shipping Information
            </Typography>
            <Divider sx={{ mb: 3 }} />

            <Grid container spacing={3}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="First Name"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleChange}
                  required
                  error={!!formErrors.first_name}
                  helperText={formErrors.first_name}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Last Name"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleChange}
                  required
                  error={!!formErrors.last_name}
                  helperText={formErrors.last_name}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Email"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  error={!!formErrors.email}
                  helperText={formErrors.email}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Phone"
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                  required
                  error={!!formErrors.phone}
                  helperText={formErrors.phone}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Company (Optional)"
                  name="company"
                  value={formData.company}
                  onChange={handleChange}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Address"
                  name="address"
                  multiline
                  rows={2}
                  value={formData.address}
                  onChange={handleChange}
                  required
                  error={!!formErrors.address}
                  helperText={formErrors.address}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Address Line 2 (Optional)"
                  name="address2"
                  value={formData.address2}
                  onChange={handleChange}
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="City"
                  name="city"
                  value={formData.city}
                  onChange={handleChange}
                  required
                  error={!!formErrors.city}
                  helperText={formErrors.city}
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="State"
                  name="state"
                  value={formData.state}
                  onChange={handleChange}
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="ZIP Code"
                  name="zipcode"
                  value={formData.zipcode}
                  onChange={handleChange}
                  required
                  error={!!formErrors.zipcode}
                  helperText={formErrors.zipcode}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Delivery Instructions (Optional)"
                  name="delivery_instructions"
                  multiline
                  rows={2}
                  value={formData.delivery_instructions}
                  onChange={handleChange}
                  placeholder="Any special delivery instructions..."
                />
              </Grid>
            </Grid>
          </Box>
        );
      case 1:
        return (
          <Box>
            <Typography variant="h6" gutterBottom fontWeight="600">
              Payment Information
            </Typography>
            <Divider sx={{ mb: 3 }} />

            <FormControl component="fieldset" sx={{ mb: 3 }}>
              <Typography variant="subtitle1" gutterBottom fontWeight="600">
                Payment Method
              </Typography>
              <RadioGroup
                name="payment_method"
                value={formData.payment_method}
                onChange={handleChange}
              >
                <Paper sx={{ p: 2, mb: 2, border: 1, borderColor: "grey.300" }}>
                  <FormControlLabel
                    value="cod"
                    control={<Radio />}
                    label={
                      <Box
                        sx={{ display: "flex", alignItems: "center", gap: 2 }}
                      >
                        <AccountBalance color="primary" />
                        <Box>
                          <Typography fontWeight="600">
                            Cash on Delivery
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Pay when your order is delivered
                          </Typography>
                        </Box>
                      </Box>
                    }
                  />
                </Paper>
                <Paper sx={{ p: 2, border: 1, borderColor: "grey.300" }}>
                  <FormControlLabel
                    value="card"
                    control={<Radio />}
                    label={
                      <Box
                        sx={{ display: "flex", alignItems: "center", gap: 2 }}
                      >
                        <CreditCard color="primary" />
                        <Box>
                          <Typography fontWeight="600">
                            Credit/Debit Card
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Secure online payment
                          </Typography>
                        </Box>
                      </Box>
                    }
                  />
                </Paper>
              </RadioGroup>
            </FormControl>

            {formData.payment_method === "card" && (
              <Box sx={{ mt: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Card Details
                </Typography>
                <Grid container spacing={3}>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Card Number"
                      name="card_number"
                      value={formData.card_number}
                      onChange={handleChange}
                      placeholder="1234 5678 9012 3456"
                      error={!!formErrors.card_number}
                      helperText={formErrors.card_number}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Expiry Date"
                      name="expiry_date"
                      value={formData.expiry_date}
                      onChange={handleChange}
                      placeholder="MM/YY"
                      error={!!formErrors.expiry_date}
                      helperText={formErrors.expiry_date}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="CVV"
                      name="cvv"
                      value={formData.cvv}
                      onChange={handleChange}
                      placeholder="123"
                      error={!!formErrors.cvv}
                      helperText={formErrors.cvv}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Cardholder Name"
                      name="cardholder_name"
                      value={formData.cardholder_name}
                      onChange={handleChange}
                      error={!!formErrors.cardholder_name}
                      helperText={formErrors.cardholder_name}
                    />
                  </Grid>
                </Grid>
              </Box>
            )}

            <Box sx={{ mt: 3 }}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={formData.agree_terms}
                    onChange={handleChange}
                    name="agree_terms"
                  />
                }
                label={
                  <Typography variant="body2">
                    I agree to the{" "}
                    <a href="/terms" target="_blank" rel="noopener noreferrer">
                      Terms and Conditions
                    </a>{" "}
                    and{" "}
                    <a
                      href="/privacy"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      Privacy Policy
                    </a>
                  </Typography>
                }
              />
              {formErrors.agree_terms && (
                <Typography variant="body2" color="error" sx={{ mt: 1 }}>
                  {formErrors.agree_terms}
                </Typography>
              )}
            </Box>

            <Box sx={{ mt: 2 }}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={formData.subscribe_newsletter}
                    onChange={handleChange}
                    name="subscribe_newsletter"
                  />
                }
                label="Subscribe to newsletter for updates and offers"
              />
            </Box>
          </Box>
        );
      case 2:
        return (
          <Box>
            <Typography variant="h6" gutterBottom fontWeight="600">
              Order Review
            </Typography>
            <Divider sx={{ mb: 3 }} />

            {/* Order Items */}
            <Typography variant="h6" gutterBottom>
              Order Items
            </Typography>
            {cart.items.map((item) => (
              <Paper
                key={item.id}
                sx={{ p: 2, mb: 2, backgroundColor: "action.hover" }}
              >
                <Grid container spacing={2} alignItems="center">
                  <Grid item xs={3}>
                    <Box
                      component="img"
                      src={item.image || "/placeholder.png"}
                      alt={item.name}
                      sx={{
                        width: "100%",
                        height: 60,
                        objectFit: "cover",
                        borderRadius: 1,
                      }}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="subtitle1" fontWeight="600">
                      {item.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Quantity: {item.quantity}
                    </Typography>
                  </Grid>
                  <Grid item xs={3} sx={{ textAlign: "right" }}>
                    <Typography variant="h6" color="primary">
                      Ã¢â€šÂ¹{item.total_price.toFixed(2)}
                    </Typography>
                  </Grid>
                </Grid>
              </Paper>
            ))}

            {/* Shipping Address */}
            <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
              Shipping Address
            </Typography>
            <Paper sx={{ p: 2, backgroundColor: "action.hover" }}>
              <Typography>
                {formData.first_name} {formData.last_name}
              </Typography>
              {formData.company && <Typography>{formData.company}</Typography>}
              <Typography>{formData.address}</Typography>
              {formData.address2 && (
                <Typography>{formData.address2}</Typography>
              )}
              <Typography>
                {formData.city}, {formData.state} {formData.zipcode}
              </Typography>
              <Typography>{formData.phone}</Typography>
              <Typography>{formData.email}</Typography>
            </Paper>

            {/* Payment Method */}
            <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
              Payment Method
            </Typography>
            <Paper sx={{ p: 2, backgroundColor: "action.hover" }}>
              <Typography>
                {formData.payment_method === "cod"
                  ? "Cash on Delivery"
                  : "Credit/Debit Card"}
              </Typography>
            </Paper>
          </Box>
        );
      default:
        return "Unknown step";
    }
  };

  if (cart.items.length === 0) {
    return (
      <Container maxWidth="lg">
        <Breadcrumbs sx={{ mb: 3 }}>
          <Link to="/" style={{ textDecoration: "none", color: "inherit" }}>
            Home
          </Link>
          <Typography color="text.primary">Checkout</Typography>
        </Breadcrumbs>

        <Alert severity="info" sx={{ borderRadius: 2 }}>
          Your cart is empty. <a href="/products">Continue shopping</a>
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Breadcrumbs sx={{ mb: 3 }}>
        <Link to="/" style={{ textDecoration: "none", color: "inherit" }}>
          Home
        </Link>
        <Link to="/cart" style={{ textDecoration: "none", color: "inherit" }}>
          Cart
        </Link>
        <Typography color="text.primary">Checkout</Typography>
      </Breadcrumbs>

      <Typography
        variant="h4"
        component="h1"
        gutterBottom
        sx={{ fontWeight: 700, mb: 4 }}
      >
        Checkout
      </Typography>

      {/* Progress Indicator */}
      <Paper sx={{ p: 3, mb: 4, borderRadius: 3 }}>
        <Stepper activeStep={activeStep} alternativeLabel>
          {steps.map((label, index) => {
            const stepIcons = {
              0: <Person key="person-icon" />,
              1: <Payment key="payment-icon" />,
              2: <CheckCircle key="check-icon" />,
            };
            return (
              <Step key={label} completed={completed[index]}>
                <StepLabel StepIconComponent={() => stepIcons[index]}>
                  {label}
                </StepLabel>
              </Step>
            );
          })}
        </Stepper>
      </Paper>

      <Grid container spacing={4}>
        {/* Checkout Form */}
        <Grid item xs={12} md={8}>
          <Card sx={{ borderRadius: 3 }}>
            <CardContent sx={{ p: 4 }}>
              {error && (
                <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }}>
                  {error}
                </Alert>
              )}

              <Box component="form" onSubmit={handleSubmit}>
                {getStepContent(activeStep)}

                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    mt: 4,
                  }}
                >
                  <Button
                    disabled={activeStep === 0}
                    onClick={handleBack}
                    variant="outlined"
                    sx={{ borderRadius: 2 }}
                  >
                    Back
                  </Button>
                  <Button
                    variant="contained"
                    onClick={
                      activeStep === steps.length - 1
                        ? handleSubmit
                        : handleNext
                    }
                    disabled={loading}
                    sx={{ borderRadius: 2, px: 4 }}
                  >
                    {getButtonText(activeStep === steps.length - 1, loading)}
                  </Button>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Order Summary */}
        <Grid item xs={12} md={4}>
          <Card sx={{ borderRadius: 3, position: "sticky", top: 20 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom fontWeight="bold">
                Order Summary
              </Typography>
              <Divider sx={{ mb: 2 }} />

              {cart.items.map((item) => (
                <Box
                  key={item.id}
                  sx={{ mb: 2, pb: 2, borderBottom: 1, borderColor: "divider" }}
                >
                  <Grid container spacing={1}>
                    <Grid item xs={3}>
                      <Box
                        component="img"
                        src={item.image || "/placeholder.png"}
                        alt={item.name}
                        sx={{
                          width: "100%",
                          height: 50,
                          objectFit: "cover",
                          borderRadius: 1,
                        }}
                      />
                    </Grid>
                    <Grid item xs={6}>
                      <Typography
                        variant="body2"
                        fontWeight="600"
                        sx={{ fontSize: "0.875rem" }}
                      >
                        {item.name}
                      </Typography>
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{ fontSize: "0.75rem" }}
                      >
                        Qty: {item.quantity}
                      </Typography>
                    </Grid>
                    <Grid item xs={3} sx={{ textAlign: "right" }}>
                      <Typography variant="body2" fontWeight="600">
                        Ã¢â€šÂ¹{item.total_price.toFixed(2)}
                      </Typography>
                    </Grid>
                  </Grid>
                </Box>
              ))}

              <Divider sx={{ my: 2 }} />

              <Box
                sx={{ display: "flex", justifyContent: "space-between", mb: 1 }}
              >
                <Typography>Items ({cart.item_count}):</Typography>
                <Typography>Ã¢â€šÂ¹{cart.total_cost.toFixed(2)}</Typography>
              </Box>

              <Box
                sx={{ display: "flex", justifyContent: "space-between", mb: 1 }}
              >
                <Typography>Shipping:</Typography>
                <Typography color="success.main">Free</Typography>
              </Box>

              <Box
                sx={{ display: "flex", justifyContent: "space-between", mb: 1 }}
              >
                <Typography>Tax:</Typography>
                <Typography>Ã¢â€šÂ¹{(cart.total_cost * 0.18).toFixed(2)}</Typography>
              </Box>

              <Divider sx={{ my: 2 }} />

              <Box
                sx={{ display: "flex", justifyContent: "space-between", mb: 2 }}
              >
                <Typography variant="h6">Total:</Typography>
                <Typography variant="h6" color="primary" fontWeight="bold">
                  Ã¢â€šÂ¹{(cart.total_cost * 1.18).toFixed(2)}
                </Typography>
              </Box>

              <Alert severity="info" sx={{ borderRadius: 2 }}>
                <Typography variant="body2" fontWeight="600" gutterBottom>
                  Estimated Delivery
                </Typography>
                <Typography variant="body2">
                  3-5 business days for standard delivery
                </Typography>
              </Alert>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Checkout;
