import React, { lazy, Suspense } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  useLocation,
} from "react-router-dom";
import { styled } from "@mui/material/styles";
import { Box, Slide, CircularProgress, Backdrop } from "@mui/material";
import { AnimatePresence } from "framer-motion";

// Context
import { AuthProvider } from "./utils/AuthContext";
import { CartProvider } from "./utils/CartContext";

// Components
import Header from "./components/common/Header";
import Footer from "./components/common/Footer";
import ScrollToTop from "./components/common/ScrollToTop";
import ErrorBoundary from "./components/common/ErrorBoundary";

// Lazy loaded components for code splitting
// const HomePage = lazy(() => import("./components/common/HomePage")); // Switched to AgriHome
const ProductList = lazy(() => import("./components/products/ProductList"));
const ProductDetail = lazy(() => import("./components/products/ProductDetailEnhanced"));
const ProductComparison = lazy(
  () => import("./components/products/ProductComparison"),
);
const VendorList = lazy(() => import("./components/vendors/VendorList"));
const VendorDetail = lazy(() => import("./components/vendors/VendorDetail"));
const Cart = lazy(() => import("./components/cart/Cart"));
const Checkout = lazy(() => import("./components/cart/Checkout"));
const Login = lazy(() => import("./components/auth/Login"));
const Register = lazy(() => import("./components/auth/Register"));
const Profile = lazy(() => import("./components/auth/Profile"));
const Orders = lazy(() => import("./components/orders/Orders"));
const OrderDetail = lazy(() => import("./components/orders/OrderDetail"));
const Wishlist = lazy(() => import("./components/wishlist/Wishlist"));
const Messages = lazy(() => import("./components/messages/Messages"));
const About = lazy(() => import("./components/pages/About"));
const Contact = lazy(() => import("./components/pages/Contact"));
const Settings = lazy(() => import("./components/settings/Settings"));
const NotFound = lazy(() => import("./components/pages/NotFound"));

// AGRIM-Style Pages
const AgriHome = lazy(() => import("./pages/AgriHome"));
const AccountPage = lazy(() => import("./pages/AccountPage"));
const NotificationsPage = lazy(() => import("./pages/NotificationsPage"));
const SoilHealth = lazy(() => import("./pages/SoilHealth"));
const VendorDashboard = lazy(() => import("./pages/VendorDashboard"));

// Monitoring Dashboard
const MonitoringDashboard = lazy(() => import("./pages/MonitoringDashboard"));

const AnimatedBox = styled(Box)(({ theme }) => ({
  minHeight: "100vh",
  display: "flex",
  flexDirection: "column",
  transition: theme.transitions.create(["background-color", "color"], {
    duration: theme.transitions.duration.standard,
  }),
}));

// Loading fallback component
const LoadingFallback = () => (
  <Backdrop
    open
    sx={{ color: "#fff", zIndex: (theme) => theme.zIndex.drawer + 1 }}
  >
    <CircularProgress color="inherit" />
  </Backdrop>
);

const AnimatedRoutes = () => {
  const location = useLocation();

  return (
    <Suspense fallback={<LoadingFallback />}>
      <AnimatePresence mode="wait">
        <Routes location={location} key={location.pathname}>
          <Route
            path="/"
            element={
              <Slide direction="up" in timeout={600} mountOnEnter unmountOnExit>
                <Box>
                  <AgriHome />
                </Box>
              </Slide>
            }
          />
          <Route
            path="/vendor/dashboard"
            element={
              <Slide direction="up" in timeout={500} mountOnEnter unmountOnExit>
                <Box>
                  <VendorDashboard />
                </Box>
              </Slide>
            }
          />
          <Route
            path="/products"
            element={
              <Slide direction="up" in timeout={500} mountOnEnter unmountOnExit>
                <Box>
                  <ProductList />
                </Box>
              </Slide>
            }
          />
          <Route
            path="/products/:slug"
            element={
              <Slide direction="up" in timeout={500} mountOnEnter unmountOnExit>
                <Box>
                  <ProductDetail />
                </Box>
              </Slide>
            }
          />
          <Route
            path="/compare"
            element={
              <Slide direction="up" in timeout={500} mountOnEnter unmountOnExit>
                <Box>
                  <ProductComparison />
                </Box>
              </Slide>
            }
          />
          <Route
            path="/vendors"
            element={
              <Slide
                direction="left"
                in
                timeout={500}
                mountOnEnter
                unmountOnExit
              >
                <Box>
                  <VendorList />
                </Box>
              </Slide>
            }
          />
          <Route
            path="/vendors/:slug"
            element={
              <Slide
                direction="left"
                in
                timeout={500}
                mountOnEnter
                unmountOnExit
              >
                <Box>
                  <VendorDetail />
                </Box>
              </Slide>
            }
          />
          <Route
            path="/cart"
            element={
              <Slide
                direction="right"
                in
                timeout={500}
                mountOnEnter
                unmountOnExit
              >
                <Box>
                  <Cart />
                </Box>
              </Slide>
            }
          />
          <Route
            path="/checkout"
            element={
              <Slide
                direction="right"
                in
                timeout={500}
                mountOnEnter
                unmountOnExit
              >
                <Box>
                  <Checkout />
                </Box>
              </Slide>
            }
          />
          <Route
            path="/login"
            element={
              <Slide
                direction="down"
                in
                timeout={500}
                mountOnEnter
                unmountOnExit
              >
                <Box>
                  <Login />
                </Box>
              </Slide>
            }
          />
          <Route
            path="/register"
            element={
              <Slide
                direction="down"
                in
                timeout={500}
                mountOnEnter
                unmountOnExit
              >
                <Box>
                  <Register />
                </Box>
              </Slide>
            }
          />
          <Route
            path="/profile"
            element={
              <Slide
                direction="left"
                in
                timeout={500}
                mountOnEnter
                unmountOnExit
              >
                <Box>
                  <Profile />
                </Box>
              </Slide>
            }
          />
          <Route
            path="/orders"
            element={
              <Slide
                direction="left"
                in
                timeout={500}
                mountOnEnter
                unmountOnExit
              >
                <Box>
                  <Orders />
                </Box>
              </Slide>
            }
          />
          <Route
            path="/orders/:id"
            element={
              <Slide
                direction="left"
                in
                timeout={500}
                mountOnEnter
                unmountOnExit
              >
                <Box>
                  <OrderDetail />
                </Box>
              </Slide>
            }
          />
          <Route
            path="/wishlist"
            element={
              <Slide
                direction="right"
                in
                timeout={500}
                mountOnEnter
                unmountOnExit
              >
                <Box>
                  <Wishlist />
                </Box>
              </Slide>
            }
          />
          <Route
            path="/messages"
            element={
              <Slide direction="up" in timeout={500} mountOnEnter unmountOnExit>
                <Box>
                  <Messages />
                </Box>
              </Slide>
            }
          />
          <Route
            path="/about"
            element={
              <Slide direction="up" in timeout={500} mountOnEnter unmountOnExit>
                <Box>
                  <About />
                </Box>
              </Slide>
            }
          />
          <Route
            path="/contact"
            element={
              <Slide direction="up" in timeout={500} mountOnEnter unmountOnExit>
                <Box>
                  <Contact />
                </Box>
              </Slide>
            }
          />
          <Route
            path="/settings"
            element={
              <Slide direction="up" in timeout={500} mountOnEnter unmountOnExit>
                <Box>
                  <Settings />
                </Box>
              </Slide>
            }
          />
          {/* AGRIM-Style Routes */}
          <Route
            path="/agri"
            element={
              <Slide direction="up" in timeout={500} mountOnEnter unmountOnExit>
                <Box>
                  <AgriHome />
                </Box>
              </Slide>
            }
          />
          <Route
            path="/store"
            element={
              <Slide direction="up" in timeout={500} mountOnEnter unmountOnExit>
                <Box>
                  <ProductList />
                </Box>
              </Slide>
            }
          />
          <Route
            path="/credit"
            element={
              <Slide direction="up" in timeout={500} mountOnEnter unmountOnExit>
                <Box>
                  <AccountPage />
                </Box>
              </Slide>
            }
          />
          <Route
            path="/offers"
            element={
              <Slide direction="up" in timeout={500} mountOnEnter unmountOnExit>
                <Box>
                  <ProductList />
                </Box>
              </Slide>
            }
          />
          <Route
            path="/account"
            element={
              <Slide direction="up" in timeout={500} mountOnEnter unmountOnExit>
                <Box>
                  <AccountPage />
                </Box>
              </Slide>
            }
          />
          <Route
            path="/notifications"
            element={
              <Slide direction="up" in timeout={500} mountOnEnter unmountOnExit>
                <Box>
                  <NotificationsPage />
                </Box>
              </Slide>
            }
          />
          <Route
            path="/soil-health"
            element={
              <Slide direction="up" in timeout={500} mountOnEnter unmountOnExit>
                <Box>
                  <SoilHealth />
                </Box>
              </Slide>
            }
          />
          <Route
            path="/category/:slug"
            element={
              <Slide direction="up" in timeout={500} mountOnEnter unmountOnExit>
                <Box>
                  <ProductList />
                </Box>
              </Slide>
            }
          />
          <Route
            path="/crop/:slug"
            element={
              <Slide direction="up" in timeout={500} mountOnEnter unmountOnExit>
                <Box>
                  <ProductList />
                </Box>
              </Slide>
            }
          />
          <Route
            path="/disease/:slug"
            element={
              <Slide direction="up" in timeout={500} mountOnEnter unmountOnExit>
                <Box>
                  <ProductList />
                </Box>
              </Slide>
            }
          />
          <Route
            path="/product/:slug"
            element={
              <Slide direction="up" in timeout={500} mountOnEnter unmountOnExit>
                <Box>
                  <ProductDetail />
                </Box>
              </Slide>
            }
          />
          {/* 404 Not Found - Must be last */}
          <Route
            path="/monitoring"
            element={
              <Slide direction="up" in timeout={500} mountOnEnter unmountOnExit>
                <Box>
                  <MonitoringDashboard />
                </Box>
              </Slide>
            }
          />
          <Route
            path="*"
            element={
              <Slide direction="up" in timeout={500} mountOnEnter unmountOnExit>
                <Box>
                  <NotFound />
                </Box>
              </Slide>
            }
          />
        </Routes>
      </AnimatePresence>
    </Suspense>
  );
};

function App() {
  return (
    <AuthProvider>
      <CartProvider>
        <Router>
          <AnimatedBox>
            <Header />
            <Box
              component="main"
              sx={{
                flex: 1,
                padding: { xs: "10px 0", sm: "20px 0" },
                transition: "all 0.3s ease-in-out",
              }}
            >
              <ErrorBoundary>
                <AnimatedRoutes />
              </ErrorBoundary>
            </Box>
            <Footer />
            <ScrollToTop />
          </AnimatedBox>
        </Router>
      </CartProvider>
    </AuthProvider>
  );
}

export default App;
