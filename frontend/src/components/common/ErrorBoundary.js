/* global globalThis */
import React, { Component } from "react";
import PropTypes from "prop-types";
import { Box, Container, Typography, Button, Paper } from "@mui/material";
import { ErrorOutline, Refresh, Home } from "@mui/icons-material";

/**
 * Error Boundary component that catches JavaScript errors anywhere in their child component tree
 * and displays a fallback UI instead of crashing the whole app.
 */
class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // Log the error to an error reporting service
    console.error("Error caught by ErrorBoundary:", error, errorInfo);
    this.setState({ errorInfo });

    // You can also log to an error reporting service here
    // logErrorToService(error, errorInfo);
  }

  handleReload = () => {
    // Reset state and reload the page
    this.setState({ hasError: false, error: null, errorInfo: null });
    globalThis.location.reload();
  };

  handleGoHome = () => {
    // Reset state and navigate to home
    this.setState({ hasError: false, error: null, errorInfo: null });
    globalThis.location.href = "/";
  };

  render() {
    if (this.state.hasError) {
      const { fallback } = this.props;

      // If a custom fallback is provided, use it
      if (fallback) {
        return fallback;
      }

      // Default error UI
      return (
        <Container maxWidth="md" sx={{ py: 8 }}>
          <Paper
            elevation={3}
            sx={{
              p: 6,
              textAlign: "center",
              borderRadius: 3,
              background: "linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%)",
            }}
          >
            <Box sx={{ mb: 4 }}>
              <ErrorOutline
                sx={{
                  fontSize: 80,
                  color: "error.main",
                  animation: "pulse 2s infinite",
                  "@keyframes pulse": {
                    "0%, 100%": { opacity: 1 },
                    "50%": { opacity: 0.5 },
                  },
                }}
              />
            </Box>

            <Typography
              variant="h4"
              component="h1"
              gutterBottom
              fontWeight="bold"
              color="text.primary"
            >
              Oops! Something went wrong
            </Typography>

            <Typography
              variant="body1"
              color="text.secondary"
              sx={{ mb: 4, maxWidth: 500, mx: "auto" }}
            >
              We apologize for the inconvenience. An unexpected error has
              occurred. Please try refreshing the page or go back to the home
              page.
            </Typography>

            {process.env.NODE_ENV === "development" && this.state.error && (
              <Paper
                variant="outlined"
                sx={{
                  p: 2,
                  mb: 4,
                  textAlign: "left",
                  bgcolor: "grey.50",
                  maxHeight: 200,
                  overflow: "auto",
                }}
              >
                <Typography variant="subtitle2" color="error" gutterBottom>
                  Error Details (Development Only):
                </Typography>
                <Typography
                  variant="body2"
                  component="pre"
                  sx={{
                    fontFamily: "monospace",
                    fontSize: "0.75rem",
                    whiteSpace: "pre-wrap",
                    wordBreak: "break-word",
                  }}
                >
                  {this.state.error.toString()}
                  {this.state.errorInfo && (
                    <>
                      {"\n\nComponent Stack:"}
                      {this.state.errorInfo.componentStack}
                    </>
                  )}
                </Typography>
              </Paper>
            )}

            <Box sx={{ display: "flex", gap: 2, justifyContent: "center" }}>
              <Button
                variant="contained"
                size="large"
                startIcon={<Refresh />}
                onClick={this.handleReload}
                sx={{
                  px: 4,
                  py: 1.5,
                  borderRadius: 2,
                }}
              >
                Refresh Page
              </Button>
              <Button
                variant="outlined"
                size="large"
                startIcon={<Home />}
                onClick={this.handleGoHome}
                sx={{
                  px: 4,
                  py: 1.5,
                  borderRadius: 2,
                }}
              >
                Go to Home
              </Button>
            </Box>
          </Paper>
        </Container>
      );
    }

    return this.props.children;
  }
}

ErrorBoundary.propTypes = {
  children: PropTypes.node.isRequired,
  fallback: PropTypes.node,
};

ErrorBoundary.defaultProps = {
  fallback: null,
};

export default ErrorBoundary;
