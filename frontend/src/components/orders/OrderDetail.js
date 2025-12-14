import React, { useState, useEffect, useCallback } from "react";
import PropTypes from "prop-types";
import { useParams, useNavigate } from "react-router-dom";
import {
  Container,
  Typography,
  Box,
  Alert,
  Grid,
  Button,
  Divider,
  Stepper,
  Step,
  StepLabel,
  StepConnector,
  Paper,
  Skeleton,
  stepConnectorClasses,
  styled,
} from "@mui/material";
import {
  ArrowBack,
  ShoppingBag,
  CheckCircle,
  Receipt,
  Person,
  Home,
  Phone,
  Email,
} from "@mui/icons-material";
import { ordersAPI } from "../../services/api";
import { useAuth } from "../../utils/AuthContext";
import { motion } from "framer-motion";

const MotionPaper = motion(Paper);

const QontoConnector = styled(StepConnector)(({ theme }) => ({
  [`&.${stepConnectorClasses.alternativeLabel}`]: {
    top: 10,
    left: "calc(-50% + 16px)",
    right: "calc(50% + 16px)",
  },
  [`&.${stepConnectorClasses.active}`]: {
    [`& .${stepConnectorClasses.line}`]: {
      borderColor: "#22c55e",
    },
  },
  [`&.${stepConnectorClasses.completed}`]: {
    [`& .${stepConnectorClasses.line}`]: {
      borderColor: "#22c55e",
    },
  },
  [`& .${stepConnectorClasses.line}`]: {
    borderColor:
      theme.palette.mode === "dark" ? theme.palette.grey[800] : "#eaeaf0",
    borderTopWidth: 3,
    borderRadius: 1,
  },
}));

const QontoStepIconRoot = styled("div")(({ theme, ownerState }) => ({
  color: theme.palette.mode === "dark" ? theme.palette.grey[700] : "#eaeaf0",
  display: "flex",
  height: 22,
  alignItems: "center",
  ...(ownerState.active && {
    color: "#22c55e",
  }),
  "& .QontoStepIcon-completedIcon": {
    color: "#22c55e",
    zIndex: 1,
    fontSize: 18,
  },
  "& .QontoStepIcon-circle": {
    width: 8,
    height: 8,
    borderRadius: "50%",
    backgroundColor: "currentColor",
  },
}));

function QontoStepIcon(props) {
  const { active, completed, className } = props;

  return (
    <QontoStepIconRoot ownerState={{ active }} className={className}>
      {completed ? (
        <CheckCircle className="QontoStepIcon-completedIcon" />
      ) : (
        <div className="QontoStepIcon-circle" />
      )}
    </QontoStepIconRoot>
  );
}

QontoStepIcon.propTypes = {
  active: PropTypes.bool,
  completed: PropTypes.bool,
  className: PropTypes.string,
};

const OrderDetail = () => {
  const { id } = useParams();
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadOrder = useCallback(async () => {
    try {
      const response = await ordersAPI.getOrder(id);
      setOrder(response.data);
    } catch (error) {
      console.error("Failed to load order:", error);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    if (isAuthenticated) {
      loadOrder();
    } else {
      loading && setLoading(false);
    }
  }, [isAuthenticated, loadOrder, loading]);

  const steps = ["Pending", "Confirmed", "Shipped", "Delivered"];

  const getActiveStep = (status) => {
    switch (status) {
      case "pending":
        return 0;
      case "confirmed":
        return 1;
      case "shipped":
        return 2;
      case "delivered":
        return 4; // All completed
      case "cancelled":
        return -1;
      default:
        return 0;
    }
  };

  if (!isAuthenticated) {
    return (
      <Container maxWidth="md" sx={{ py: 8, textAlign: "center" }}>
        <Typography variant="h6">Please login to view details.</Typography>
        <Button
          variant="contained"
          sx={{ mt: 2 }}
          onClick={() => navigate("/login")}
        >
          Login
        </Button>
      </Container>
    );
  }

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 6 }}>
        <Skeleton variant="text" width={200} height={40} sx={{ mb: 4 }} />
        <Grid container spacing={4}>
          <Grid item xs={12} md={8}>
            <Skeleton
              variant="rectangular"
              height={200}
              sx={{ borderRadius: 4, mb: 3 }}
            />
            <Skeleton
              variant="rectangular"
              height={300}
              sx={{ borderRadius: 4 }}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <Skeleton
              variant="rectangular"
              height={400}
              sx={{ borderRadius: 4 }}
            />
          </Grid>
        </Grid>
      </Container>
    );
  }

  if (!order) {
    return (
      <Container maxWidth="md" sx={{ py: 8, textAlign: "center" }}>
        <Typography variant="h5" color="error">
          Order not found
        </Typography>
        <Button
          startIcon={<ArrowBack />}
          onClick={() => navigate("/orders")}
          sx={{ mt: 2 }}
        >
          Back to Orders
        </Button>
      </Container>
    );
  }

  return (
    <Box
      sx={{
        minHeight: "100vh",
        py: 6,
        background: "linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%)",
      }}
    >
      <Container maxWidth="lg">
        <Button
          startIcon={<ArrowBack />}
          onClick={() => navigate("/orders")}
          sx={{
            mb: 3,
            color: "text.secondary",
            "&:hover": { color: "primary.main" },
          }}
        >
          Back to Orders
        </Button>

        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              mb: 4,
              flexWrap: "wrap",
              gap: 2,
            }}
          >
            <Box>
              <Typography
                variant="h4"
                component="h1"
                fontWeight="800"
                sx={{ color: "#1e293b" }}
              >
                Order #{order.id}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Placed on{" "}
                {new Date(order.created_at).toLocaleDateString(undefined, {
                  weekday: "long",
                  year: "numeric",
                  month: "long",
                  day: "numeric",
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </Typography>
            </Box>
            <Button
              variant="outlined"
              startIcon={<Receipt />}
              sx={{ borderRadius: 2 }}
            >
              Download Invoice
            </Button>
          </Box>
        </motion.div>

        {/* Progress Stepper */}
        {order.status === "cancelled" ? (
          <Alert severity="error" sx={{ mb: 4, borderRadius: 2 }}>
            This order has been cancelled.
          </Alert>
        ) : (
          <MotionPaper
            elevation={0}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            sx={{
              p: 4,
              mb: 4,
              borderRadius: 4,
              border: "1px solid",
              borderColor: "divider",
            }}
          >
            <Stepper
              alternativeLabel
              activeStep={getActiveStep(order.status)}
              connector={<QontoConnector />}
            >
              {steps.map((label) => (
                <Step key={label}>
                  <StepLabel StepIconComponent={QontoStepIcon}>
                    {label}
                  </StepLabel>
                </Step>
              ))}
            </Stepper>
          </MotionPaper>
        )}

        <Grid container spacing={4}>
          <Grid item xs={12} md={8}>
            {/* Order Items */}
            <MotionPaper
              elevation={0}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              sx={{
                p: 3,
                mb: 3,
                borderRadius: 4,
                border: "1px solid",
                borderColor: "divider",
                overflow: "hidden",
              }}
            >
              <Typography
                variant="h6"
                fontWeight="700"
                gutterBottom
                sx={{ mb: 3 }}
              >
                Order Items
              </Typography>
              {order.items.map((item, index) => (
                <Box key={item.id}>
                  <Box sx={{ display: "flex", gap: 3, py: 2 }}>
                    <Box
                      sx={{
                        width: 80,
                        height: 80,
                        borderRadius: 2,
                        bgcolor: "action.hover",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                      }}
                    >
                      <ShoppingBag color="action" />
                    </Box>
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="subtitle1" fontWeight="600">
                        {item.product.name}
                      </Typography>
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        gutterBottom
                      >
                        Vendor: {item.vendor.name}
                      </Typography>
                      <Box
                        sx={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                          mt: 1,
                        }}
                      >
                        <Typography
                          variant="body2"
                          sx={{
                            bgcolor: "action.selected",
                            px: 1,
                            borderRadius: 1,
                          }}
                        >
                          Qty: {item.quantity}
                        </Typography>
                        <Typography
                          variant="subtitle1"
                          fontWeight="700"
                          color="primary"
                        >
                          Ã¢â€šÂ¹{item.price * item.quantity}
                        </Typography>
                      </Box>
                    </Box>
                  </Box>
                  {index < order.items.length - 1 && <Divider />}
                </Box>
              ))}
            </MotionPaper>
          </Grid>

          <Grid item xs={12} md={4}>
            {/* Shipping & Payment Info */}
            <MotionPaper
              elevation={0}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
              sx={{
                p: 3,
                borderRadius: 4,
                border: "1px solid",
                borderColor: "divider",
                height: "100%",
              }}
            >
              <Typography
                variant="h6"
                fontWeight="700"
                gutterBottom
                sx={{ mb: 3 }}
              >
                Delivery Details
              </Typography>

              <Box sx={{ mb: 3 }}>
                <Typography
                  variant="subtitle2"
                  color="text.secondary"
                  gutterBottom
                >
                  Shipping Address
                </Typography>
                <Box sx={{ display: "flex", gap: 1.5, mb: 1 }}>
                  <Person fontSize="small" color="action" />
                  <Typography variant="body2" fontWeight="600">
                    {order.first_name} {order.last_name}
                  </Typography>
                </Box>
                <Box sx={{ display: "flex", gap: 1.5, mb: 1 }}>
                  <Home fontSize="small" color="action" />
                  <Typography variant="body2">
                    {order.address}
                    <br />
                    {order.place}, {order.zipcode}
                  </Typography>
                </Box>
                <Box sx={{ display: "flex", gap: 1.5, mb: 1 }}>
                  <Phone fontSize="small" color="action" />
                  <Typography variant="body2">
                    {order.phone || "N/A"}
                  </Typography>
                </Box>
                <Box sx={{ display: "flex", gap: 1.5 }}>
                  <Email fontSize="small" color="action" />
                  <Typography variant="body2">{order.email}</Typography>
                </Box>
              </Box>

              <Divider sx={{ my: 3 }} />

              <Typography
                variant="subtitle2"
                color="text.secondary"
                gutterBottom
              >
                Payment Summary
              </Typography>
              <Box
                sx={{ display: "flex", justifyContent: "space-between", mb: 1 }}
              >
                <Typography variant="body2">Subtotal</Typography>
                <Typography variant="body2" fontWeight="600">
                  Ã¢â€šÂ¹{order.total_amount || order.paid_amount}
                </Typography>
              </Box>
              <Box
                sx={{ display: "flex", justifyContent: "space-between", mb: 2 }}
              >
                <Typography variant="body2">Shipping</Typography>
                <Typography
                  variant="body2"
                  color="success.main"
                  fontWeight="600"
                >
                  Free
                </Typography>
              </Box>
              <Divider sx={{ my: 2 }} />
              <Box sx={{ display: "flex", justifyContent: "space-between" }}>
                <Typography variant="subtitle1" fontWeight="700">
                  Total
                </Typography>
                <Typography
                  variant="subtitle1"
                  fontWeight="700"
                  color="primary"
                >
                  Ã¢â€šÂ¹{order.total_amount || order.paid_amount}
                </Typography>
              </Box>
            </MotionPaper>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default OrderDetail;
