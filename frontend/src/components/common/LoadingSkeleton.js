import React from "react";
import PropTypes from "prop-types";
import {
  Skeleton,
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemText,
} from "@mui/material";
import { motion } from "framer-motion";

const AnimatedSkeleton = ({ children, delay = 0, ...props }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.5, delay }}
  >
    {children}
  </motion.div>
);

export const ProductCardSkeleton = ({ variant = "default" }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.5 }}
  >
    <Card
      sx={{
        height: "100%",
        display: "flex",
        flexDirection: "column",
        borderRadius: 3,
        overflow: "hidden",
        position: "relative",
        ...(variant === "pulse" && {
          "&::before": {
            content: '""',
            position: "absolute",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            background:
              "linear-gradient(45deg, rgba(255,255,255,0.1), rgba(255,255,255,0.3), rgba(255,255,255,0.1))",
            animation: "pulse 2s ease-in-out infinite",
          },
          "@keyframes pulse": {
            "0%, 100%": { opacity: 0.5 },
            "50%": { opacity: 1 },
          },
        }),
        ...(variant === "wave" && {
          "&::before": {
            content: '""',
            position: "absolute",
            top: 0,
            left: "-100%",
            width: "100%",
            height: "100%",
            background:
              "linear-gradient(90deg, transparent, rgba(255,255,255,0.6), transparent)",
            animation: "wave 1.8s infinite",
          },
          "@keyframes wave": {
            "0%": { left: "-100%" },
            "100%": { left: "100%" },
          },
        }),
        ...(variant === "shimmer" && {
          "&::before": {
            content: '""',
            position: "absolute",
            top: 0,
            left: "-100%",
            width: "100%",
            height: "100%",
            background:
              "linear-gradient(90deg, transparent, rgba(255,255,255,0.4), rgba(255,255,255,0.8), rgba(255,255,255,0.4), transparent)",
            animation: "shimmer 2.5s infinite",
          },
          "@keyframes shimmer": {
            "0%": { left: "-100%" },
            "100%": { left: "100%" },
          },
        }),
        ...(variant === "default" && {
          "&::before": {
            content: '""',
            position: "absolute",
            top: 0,
            left: "-100%",
            width: "100%",
            height: "100%",
            background:
              "linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent)",
            animation: "shimmer 2s infinite",
          },
          "@keyframes shimmer": {
            "0%": { left: "-100%" },
            "100%": { left: "100%" },
          },
        }),
      }}
    >
      <Box sx={{ position: "relative", overflow: "hidden" }}>
        <Skeleton
          variant="rectangular"
          height={220}
          sx={{
            borderRadius: 0,
            backgroundColor: "grey.100",
            "&::after": {
              background:
                "linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)",
              backgroundSize: "200% 100%",
              animation: "loading 1.5s infinite",
            },
            "@keyframes loading": {
              "0%": { backgroundPosition: "200% 0" },
              "100%": { backgroundPosition: "-200% 0" },
            },
          }}
        />
        {/* Discount badge skeleton */}
        <Skeleton
          variant="rectangular"
          width={60}
          height={24}
          sx={{
            position: "absolute",
            top: 12,
            left: 12,
            borderRadius: 1,
            backgroundColor: "error.main",
            opacity: 0.8,
          }}
        />
        {/* Featured badge skeleton */}
        <Skeleton
          variant="rectangular"
          width={70}
          height={24}
          sx={{
            position: "absolute",
            top: 12,
            right: 12,
            borderRadius: 1,
            backgroundColor: "secondary.main",
            opacity: 0.8,
          }}
        />
      </Box>

      <CardContent sx={{ flexGrow: 1, p: 2 }}>
        {/* Category and vendor */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1, duration: 0.3 }}
        >
          <Skeleton
            variant="text"
            width="60%"
            height={16}
            sx={{ mb: 1, backgroundColor: "grey.200" }}
          />
        </motion.div>

        {/* Product name */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2, duration: 0.3 }}
        >
          <Skeleton
            variant="text"
            width="90%"
            height={24}
            sx={{ mb: 1, backgroundColor: "grey.300" }}
          />
          <Skeleton
            variant="text"
            width="70%"
            height={24}
            sx={{ mb: 1, backgroundColor: "grey.300" }}
          />
        </motion.div>

        {/* Rating */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3, duration: 0.3 }}
        >
          <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}>
            <Skeleton
              variant="rectangular"
              width={80}
              height={16}
              sx={{ borderRadius: 1 }}
            />
            <Skeleton variant="text" width={40} height={14} />
          </Box>
        </motion.div>

        {/* Price */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4, duration: 0.3 }}
        >
          <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2 }}>
            <Skeleton
              variant="text"
              width={60}
              height={24}
              sx={{ backgroundColor: "primary.main", opacity: 0.6 }}
            />
            <Skeleton variant="text" width={50} height={18} />
          </Box>
        </motion.div>

        {/* Stock status */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5, duration: 0.3 }}
        >
          <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2 }}>
            <Skeleton variant="circular" width={16} height={16} />
            <Skeleton variant="text" width={60} height={16} />
          </Box>
        </motion.div>

        {/* Action buttons */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6, duration: 0.3 }}
        >
          <Skeleton
            variant="rectangular"
            height={36}
            sx={{
              borderRadius: 2,
              width: "100%",
              backgroundColor: "primary.main",
              opacity: 0.8,
            }}
          />
        </motion.div>
      </CardContent>
    </Card>
  </motion.div>
);

export const OrderCardSkeleton = () => (
  <Card>
    <CardContent>
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          mb: 2,
        }}
      >
        <Typography variant="h6">
          <Skeleton width={120} />
        </Typography>
        <Skeleton variant="circular" width={32} height={32} />
      </Box>
      <Typography variant="body2" color="text.secondary" gutterBottom>
        <Skeleton width={140} />
      </Typography>
      <Typography variant="body1" gutterBottom>
        <Skeleton width={200} />
      </Typography>
      <Typography variant="body2" gutterBottom>
        <Skeleton width={160} />
      </Typography>
      <Box sx={{ mt: 2 }}>
        <Typography variant="h6" color="primary">
          <Skeleton width={100} />
        </Typography>
      </Box>
      <Box sx={{ mt: 2 }}>
        <Skeleton variant="rectangular" height={36} width={120} />
      </Box>
    </CardContent>
  </Card>
);

export const ProfileFormSkeleton = () => (
  <Box>
    <Typography variant="h6" gutterBottom>
      <Skeleton width={150} />
    </Typography>
    <Grid container spacing={2} sx={{ mb: 3 }}>
      <Grid item xs={12} sm={6}>
        <Skeleton variant="rectangular" height={56} />
      </Grid>
      <Grid item xs={12} sm={6}>
        <Skeleton variant="rectangular" height={56} />
      </Grid>
      <Grid item xs={12}>
        <Skeleton variant="rectangular" height={56} />
      </Grid>
    </Grid>

    <Typography variant="h6" gutterBottom>
      <Skeleton width={160} />
    </Typography>
    <Grid container spacing={2} sx={{ mb: 3 }}>
      <Grid item xs={12} sm={6}>
        <Skeleton variant="rectangular" height={56} />
      </Grid>
      <Grid item xs={12} sm={6}>
        <Skeleton variant="rectangular" height={56} />
      </Grid>
      <Grid item xs={12}>
        <Skeleton variant="rectangular" height={96} />
      </Grid>
      <Grid item xs={12} sm={4}>
        <Skeleton variant="rectangular" height={56} />
      </Grid>
      <Grid item xs={12} sm={4}>
        <Skeleton variant="rectangular" height={56} />
      </Grid>
      <Grid item xs={12} sm={4}>
        <Skeleton variant="rectangular" height={56} />
      </Grid>
    </Grid>

    <Skeleton variant="rectangular" height={48} width={150} />
  </Box>
);

export const WishlistItemSkeleton = () => (
  <Grid item xs={12} sm={6} md={4} lg={3}>
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4 }}
    >
      <Card
        sx={{
          height: "100%",
          display: "flex",
          flexDirection: "column",
          borderRadius: 3,
          overflow: "hidden",
          position: "relative",
          "&::before": {
            content: '""',
            position: "absolute",
            top: 0,
            left: "-100%",
            width: "100%",
            height: "100%",
            background:
              "linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent)",
            animation: "shimmer 2.5s infinite",
          },
          "@keyframes shimmer": {
            "0%": { left: "-100%" },
            "100%": { left: "100%" },
          },
        }}
      >
        <Box sx={{ position: "relative", overflow: "hidden" }}>
          <Skeleton
            variant="rectangular"
            height={200}
            sx={{
              backgroundColor: "grey.100",
              "&::after": {
                background:
                  "linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)",
                backgroundSize: "200% 100%",
                animation: "loading 2s infinite",
              },
              "@keyframes loading": {
                "0%": { backgroundPosition: "200% 0" },
                "100%": { backgroundPosition: "-200% 0" },
              },
            }}
          />
          {/* Heart icon skeleton */}
          <Skeleton
            variant="circular"
            width={32}
            height={32}
            sx={{
              position: "absolute",
              top: 12,
              right: 12,
              zIndex: 1,
              backgroundColor: "rgba(255,255,255,0.9)",
              border: "2px solid rgba(0,0,0,0.1)",
            }}
          />
        </Box>

        <CardContent sx={{ flexGrow: 1, p: 2 }}>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.1, duration: 0.3 }}
          >
            <Skeleton
              variant="text"
              width="85%"
              height={24}
              sx={{ mb: 1, backgroundColor: "grey.300" }}
            />
            <Skeleton
              variant="text"
              width="60%"
              height={24}
              sx={{ mb: 1, backgroundColor: "grey.300" }}
            />
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2, duration: 0.3 }}
          >
            <Skeleton
              variant="text"
              width="70%"
              height={16}
              sx={{ mb: 1, backgroundColor: "grey.200" }}
            />
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3, duration: 0.3 }}
          >
            <Skeleton
              variant="text"
              width="50%"
              height={20}
              sx={{ mb: 2, backgroundColor: "primary.main", opacity: 0.6 }}
            />
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4, duration: 0.3 }}
          >
            <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2 }}>
              <Skeleton variant="circular" width={16} height={16} />
              <Skeleton variant="text" width={60} height={16} />
            </Box>
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5, duration: 0.3 }}
          >
            <Skeleton
              variant="rectangular"
              height={36}
              sx={{
                borderRadius: 2,
                width: "100%",
                backgroundColor: "primary.main",
                opacity: 0.8,
              }}
            />
          </motion.div>
        </CardContent>
      </Card>
    </motion.div>
  </Grid>
);

export const OrderDetailSkeleton = () => (
  <Box>
    <Typography variant="h4" gutterBottom>
      <Skeleton width={200} />
    </Typography>

    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            mb: 2,
          }}
        >
          <Typography variant="h6">
            <Skeleton width={100} />
          </Typography>
          <Skeleton variant="circular" width={32} height={32} />
        </Box>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          <Skeleton width={140} />
        </Typography>
        <Box sx={{ mt: 2 }}>
          <Typography variant="h6" color="primary">
            <Skeleton width={100} />
          </Typography>
        </Box>
      </CardContent>
    </Card>

    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          <Skeleton width={120} />
        </Typography>
        <List>
          {[1, 2, 3].map((item) => (
            <ListItem key={item} sx={{ px: 0 }}>
              <ListItemText
                primary={<Skeleton width={200} />}
                secondary={<Skeleton width={300} />}
              />
            </ListItem>
          ))}
        </List>
      </CardContent>
    </Card>
  </Box>
);

export const ProductComparisonSkeleton = () => (
  <Box>
    <Typography variant="h4" gutterBottom>
      <Skeleton width={250} />
    </Typography>
    <Typography variant="body1" color="text.secondary" gutterBottom>
      <Skeleton width={400} />
    </Typography>

    <Grid container spacing={3} sx={{ mt: 2 }}>
      {[1, 2, 3].map((product) => (
        <Grid item xs={12} md={4} key={product}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <Skeleton />
              </Typography>
              <List>
                {["Price", "Rating", "In Stock", "Vendor", "Category"].map(
                  (feature) => (
                    <ListItem key={feature} sx={{ px: 0 }}>
                      <ListItemText
                        primary={feature}
                        secondary={<Skeleton width={80} />}
                      />
                    </ListItem>
                  ),
                )}
              </List>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  </Box>
);

export const LoadingSpinner = ({ size = 40, message = "Loading..." }) => (
  <Box
    sx={{
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      minHeight: "200px",
      gap: 2,
      position: "relative",
    }}
  >
    {/* Outer rotating ring */}
    <motion.div
      animate={{ rotate: 360 }}
      transition={{
        duration: 2,
        repeat: Infinity,
        ease: "linear",
      }}
    >
      <Box
        sx={{
          width: size + 20,
          height: size + 20,
          border: "3px solid rgba(34, 197, 94, 0.1)",
          borderTop: "3px solid rgba(34, 197, 94, 0.6)",
          borderRadius: "50%",
          position: "relative",
        }}
      />
    </motion.div>

    {/* Inner spinning dots */}
    <Box sx={{ position: "absolute" }}>
      {[0, 1, 2].map((index) => (
        <motion.div
          key={index}
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.7, 1, 0.7],
          }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            delay: index * 0.2,
            ease: "easeInOut",
          }}
          style={{
            position: "absolute",
            width: 8,
            height: 8,
            backgroundColor: "#22c55e",
            borderRadius: "50%",
            left: size / 2 - 4,
            top: size / 2 - 4,
            transformOrigin: `${size / 2 + 4}px ${size / 2 + 4}px`,
          }}
        />
      ))}
    </Box>

    {/* Main spinner */}
    <motion.div
      animate={{ rotate: 360 }}
      transition={{
        duration: 1,
        repeat: Infinity,
        ease: "linear",
      }}
    >
      <Box
        sx={{
          width: size,
          height: size,
          border: "3px solid #f3f3f3",
          borderTop: "3px solid #22c55e",
          borderRadius: "50%",
          position: "relative",
          boxShadow: "0 0 20px rgba(34, 197, 94, 0.2)",
          "&::before": {
            content: '""',
            position: "absolute",
            top: -6,
            left: -6,
            right: -6,
            bottom: -6,
            border: "2px solid rgba(34, 197, 94, 0.1)",
            borderRadius: "50%",
            animation: "ripple 2s infinite",
          },
          "@keyframes ripple": {
            "0%": {
              transform: "scale(1)",
              opacity: 1,
            },
            "100%": {
              transform: "scale(1.3)",
              opacity: 0,
            },
          },
        }}
      />
    </motion.div>

    {message && (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2, duration: 0.3 }}
      >
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{
            fontWeight: 500,
            textAlign: "center",
            maxWidth: 200,
          }}
        >
          {message}
        </Typography>
      </motion.div>
    )}

    {/* Progress dots */}
    <Box sx={{ display: "flex", gap: 0.5, mt: 1 }}>
      {[0, 1, 2].map((index) => (
        <motion.div
          key={index}
          animate={{
            scale: [1, 1.5, 1],
            opacity: [0.3, 1, 0.3],
          }}
          transition={{
            duration: 1.2,
            repeat: Infinity,
            delay: index * 0.15,
          }}
        >
          <Box
            sx={{
              width: 6,
              height: 6,
              borderRadius: "50%",
              backgroundColor: "primary.main",
            }}
          />
        </motion.div>
      ))}
    </Box>
  </Box>
);

// Advanced skeleton with multiple animation types
export const AdvancedSkeleton = ({
  variant = "shimmer",
  height = 200,
  width = "100%",
  borderRadius = 2,
  animationDuration = 2,
  colors = ["#f0f0f0", "#e0e0e0", "#f0f0f0"],
}) => {
  const getAnimationStyles = () => {
    switch (variant) {
      case "shimmer":
        return {
          "&::after": {
            background: `linear-gradient(90deg, ${colors.join(", ")})`,
            backgroundSize: "200% 100%",
            animation: `shimmer ${animationDuration}s infinite`,
          },
          "@keyframes shimmer": {
            "0%": { backgroundPosition: "200% 0" },
            "100%": { backgroundPosition: "-200% 0" },
          },
        };
      case "pulse":
        return {
          animation: `pulse ${animationDuration}s ease-in-out infinite`,
          "@keyframes pulse": {
            "0%, 100%": { opacity: 0.6 },
            "50%": { opacity: 1 },
          },
        };
      case "wave":
        return {
          "&::after": {
            background: `linear-gradient(90deg, transparent, ${colors[1]}, transparent)`,
            backgroundSize: "200% 100%",
            animation: `wave ${animationDuration}s infinite`,
          },
          "@keyframes wave": {
            "0%": { backgroundPosition: "200% 0" },
            "100%": { backgroundPosition: "-200% 0" },
          },
        };
      case "bounce":
        return {
          animation: `bounce ${animationDuration}s ease-in-out infinite`,
          "@keyframes bounce": {
            "0%, 100%": { transform: "scale(1)" },
            "50%": { transform: "scale(1.05)" },
          },
        };
      default:
        return {};
    }
  };

  return (
    <Skeleton
      variant="rectangular"
      width={width}
      height={height}
      sx={{
        borderRadius,
        backgroundColor: colors[0],
        ...getAnimationStyles(),
      }}
    />
  );
};

// Skeleton group with staggered animations
export const SkeletonGroup = ({ children, staggerDelay = 0.1 }) => (
  <Box>
    {React.Children.map(children, (child, index) => (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{
          duration: 0.5,
          delay: index * staggerDelay,
        }}
      >
        {child}
      </motion.div>
    ))}
  </Box>
);

// PropTypes definitions
AnimatedSkeleton.propTypes = {
  children: PropTypes.node.isRequired,
  delay: PropTypes.number,
};

AnimatedSkeleton.defaultProps = {
  delay: 0,
};

ProductCardSkeleton.propTypes = {
  variant: PropTypes.oneOf(["default", "pulse", "wave", "shimmer"]),
};

ProductCardSkeleton.defaultProps = {
  variant: "default",
};

LoadingSpinner.propTypes = {
  size: PropTypes.number,
  message: PropTypes.string,
};

LoadingSpinner.defaultProps = {
  size: 40,
  message: "Loading...",
};

AdvancedSkeleton.propTypes = {
  variant: PropTypes.oneOf(["shimmer", "pulse", "wave", "bounce"]),
  height: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  width: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  borderRadius: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  animationDuration: PropTypes.number,
  colors: PropTypes.arrayOf(PropTypes.string),
};

AdvancedSkeleton.defaultProps = {
  variant: "shimmer",
  height: 200,
  width: "100%",
  borderRadius: 2,
  animationDuration: 2,
  colors: ["#f0f0f0", "#e0e0e0", "#f0f0f0"],
};

SkeletonGroup.propTypes = {
  children: PropTypes.node.isRequired,
  staggerDelay: PropTypes.number,
};

SkeletonGroup.defaultProps = {
  staggerDelay: 0.1,
};
