import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  Container,
  Typography,
  Paper,
  Box,
  Chip,
  Button,
  Grid,
  Skeleton,
} from "@mui/material";
import {
  LocalShipping,
  ShoppingBag,
  AccessTime,
  CheckCircle,
  Cancel,
  ArrowForward,
  DateRange,
  Place,
} from "@mui/icons-material";
import { ordersAPI } from "../../services/api";
import { useAuth } from "../../utils/AuthContext";
import { motion, AnimatePresence } from "framer-motion";

const Orders = () => {
  const { isAuthenticated } = useAuth();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated) {
      loadOrders();
    } else {
      setLoading(false);
    }
  }, [isAuthenticated]);

  const loadOrders = async () => {
    try {
      const response = await ordersAPI.getOrders();
      setOrders(response.data);
    } catch (error) {
      console.error("Failed to load orders:", error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "pending":
        return "warning";
      case "confirmed":
        return "info";
      case "shipped":
        return "primary";
      case "delivered":
        return "success";
      case "cancelled":
        return "error";
      default:
        return "default";
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case "pending":
        return <AccessTime fontSize="small" />;
      case "confirmed":
        return <ShoppingBag fontSize="small" />;
      case "shipped":
        return <LocalShipping fontSize="small" />;
      case "delivered":
        return <CheckCircle fontSize="small" />;
      case "cancelled":
        return <Cancel fontSize="small" />;
      default:
        return <AccessTime fontSize="small" />;
    }
  };

  if (!isAuthenticated) {
    return (
      <Container maxWidth="md" sx={{ py: 8, textAlign: "center" }}>
        <Typography variant="h5" gutterBottom>
          Please login to view your orders
        </Typography>
        <Button variant="contained" onClick={() => navigate("/login")}>
          Login Now
        </Button>
      </Container>
    );
  }

  if (loading) {
    return (
      <Container maxWidth="md" sx={{ py: 6 }}>
        <Box sx={{ mb: 4 }}>
          <Skeleton variant="text" width={200} height={40} />
          <Skeleton variant="text" width={300} height={20} />
        </Box>
        {[1, 2, 3].map((i) => (
          <Paper key={i} sx={{ p: 3, mb: 3, borderRadius: 3 }}>
            <Skeleton variant="text" width="40%" height={30} sx={{ mb: 2 }} />
            <Skeleton
              variant="rectangular"
              height={100}
              sx={{ borderRadius: 2 }}
            />
          </Paper>
        ))}
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
      <Container maxWidth="md">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Typography
            variant="h4"
            component="h1"
            fontWeight="800"
            sx={{ color: "#1e293b" }}
          >
            My Orders
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
            Track your order history and status
          </Typography>
        </motion.div>

        {orders.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
          >
            <Paper
              elevation={0}
              sx={{
                p: 6,
                textAlign: "center",
                borderRadius: 4,
                border: "1px dashed",
                borderColor: "divider",
                bgcolor: "transparent",
              }}
            >
              <ShoppingBag
                sx={{ fontSize: 60, color: "text.disabled", mb: 2 }}
              />
              <Typography variant="h6" color="text.secondary" gutterBottom>
                No orders yet
              </Typography>
              <Typography variant="body2" color="text.disabled" sx={{ mb: 3 }}>
                Looks like you haven't made your first purchase.
              </Typography>
              <Button
                component={Link}
                to="/products"
                variant="contained"
                startIcon={<ShoppingBag />}
                sx={{
                  borderRadius: 2,
                  textTransform: "none",
                  background:
                    "linear-gradient(135deg, #22c55e 0%, #16a34a 100%)",
                }}
              >
                Start Shopping
              </Button>
            </Paper>
          </motion.div>
        ) : (
          <AnimatePresence>
            {orders.map((order, index) => (
              <motion.div
                key={order.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: index * 0.1 }}
              >
                <Paper
                  elevation={0}
                  sx={{
                    p: 3,
                    mb: 3,
                    borderRadius: 3,
                    border: "1px solid",
                    borderColor: "divider",
                    background: "#fff",
                    transition: "all 0.2s ease-in-out",
                    "&:hover": {
                      boxShadow: "0 10px 20px rgba(0,0,0,0.05)",
                      transform: "translateY(-2px)",
                      borderColor: "primary.light",
                    },
                  }}
                >
                  <Grid container spacing={2} alignItems="center">
                    <Grid item xs={12} sm={6}>
                      <Box
                        sx={{
                          display: "flex",
                          alignItems: "center",
                          gap: 2,
                          mb: 1,
                        }}
                      >
                        <Typography variant="h6" fontWeight="700">
                          #{order.id}
                        </Typography>
                        <Chip
                          icon={getStatusIcon(order.status)}
                          label={
                            order.status.charAt(0).toUpperCase() +
                            order.status.slice(1)
                          }
                          color={getStatusColor(order.status)}
                          size="small"
                          sx={{ fontWeight: 600 }}
                        />
                      </Box>
                      <Box
                        sx={{
                          display: "flex",
                          alignItems: "center",
                          gap: 1,
                          color: "text.secondary",
                          mb: 0.5,
                        }}
                      >
                        <DateRange fontSize="small" />
                        <Typography variant="body2">
                          {new Date(order.created_at).toLocaleDateString(
                            undefined,
                            {
                              weekday: "short",
                              year: "numeric",
                              month: "short",
                              day: "numeric",
                            },
                          )}
                        </Typography>
                      </Box>
                      <Box
                        sx={{
                          display: "flex",
                          alignItems: "center",
                          gap: 1,
                          color: "text.secondary",
                        }}
                      >
                        <Place fontSize="small" />
                        <Typography variant="body2" noWrap>
                          {order.city || order.place},{" "}
                          {order.pincode || order.zipcode}
                        </Typography>
                      </Box>
                    </Grid>

                    <Grid
                      item
                      xs={12}
                      sm={6}
                      sx={{
                        display: "flex",
                        flexDirection: "column",
                        alignItems: { xs: "flex-start", sm: "flex-end" },
                        gap: 1,
                      }}
                    >
                      <Typography
                        variant="h5"
                        color="primary.main"
                        fontWeight="800"
                      >
                        Ã¢â€šÂ¹{order.total_amount || order.paid_amount || "0"}
                      </Typography>
                      <Button
                        component={Link}
                        to={`/orders/${order.id}`}
                        variant="outlined"
                        endIcon={<ArrowForward />}
                        size="small"
                        sx={{
                          borderRadius: 2,
                          fontWeight: 600,
                          textTransform: "none",
                        }}
                      >
                        View Details
                      </Button>
                    </Grid>
                  </Grid>
                </Paper>
              </motion.div>
            ))}
          </AnimatePresence>
        )}
      </Container>
    </Box>
  );
};

export default Orders;
