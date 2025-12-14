import React, {
  createContext,
  useContext,
  useState,
  useCallback,
  useMemo,
} from "react";
import { Snackbar, Alert, Slide } from "@mui/material";
import PropTypes from "prop-types";

/**
 * Toast notification context for global notifications
 */
const ToastContext = createContext();

/**
 * Hook to use toast notifications
 */
export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error("useToast must be used within a ToastProvider");
  }
  return context;
};

/**
 * Slide transition for toast notifications
 */
function SlideTransition(props) {
  return <Slide {...props} direction="up" />;
}

/**
 * Toast Provider component
 */
export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);

  /**
   * Add a new toast notification
   */
  const addToast = useCallback(
    (message, severity = "info", duration = 5000) => {
      const id = Date.now() + Math.random();
      setToasts((prev) => [...prev, { id, message, severity, duration }]);
      return id;
    },
    [],
  );

  /**
   * Remove a toast by ID
   */
  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  /**
   * Show success toast
   */
  const success = useCallback(
    (message, duration) => {
      return addToast(message, "success", duration);
    },
    [addToast],
  );

  /**
   * Show error toast
   */
  const error = useCallback(
    (message, duration) => {
      return addToast(message, "error", duration);
    },
    [addToast],
  );

  /**
   * Show warning toast
   */
  const warning = useCallback(
    (message, duration) => {
      return addToast(message, "warning", duration);
    },
    [addToast],
  );

  /**
   * Show info toast
   */
  const info = useCallback(
    (message, duration) => {
      return addToast(message, "info", duration);
    },
    [addToast],
  );

  // Memoize the context value to prevent unnecessary re-renders
  const value = useMemo(
    () => ({
      addToast,
      removeToast,
      success,
      error,
      warning,
      info,
    }),
    [addToast, removeToast, success, error, warning, info],
  );

  return (
    <ToastContext.Provider value={value}>
      {children}
      {toasts.map((toast, index) => (
        <Snackbar
          key={toast.id}
          open={true}
          autoHideDuration={toast.duration}
          onClose={() => removeToast(toast.id)}
          TransitionComponent={SlideTransition}
          anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
          sx={{
            bottom: `${24 + index * 70}px !important`,
          }}
        >
          <Alert
            onClose={() => removeToast(toast.id)}
            severity={toast.severity}
            variant="filled"
            elevation={6}
            sx={{
              width: "100%",
              minWidth: 300,
              boxShadow: 4,
            }}
          >
            {toast.message}
          </Alert>
        </Snackbar>
      ))}
    </ToastContext.Provider>
  );
};

ToastProvider.propTypes = {
  children: PropTypes.node.isRequired,
};

export default ToastContext;
