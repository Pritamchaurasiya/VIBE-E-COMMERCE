import React, { useState, useRef, useEffect, useCallback } from "react";
import { Box, Skeleton } from "@mui/material";
import { motion } from "framer-motion";
import PropTypes from "prop-types";

const LazyImage = ({
  src,
  alt,
  width = "100%",
  height = "auto",
  objectFit = "cover",
  borderRadius = 0,
  placeholder = null,
  blurSrc = null, // Low-quality image placeholder for blur-up effect
  onLoad = null,
  onError = null,
  preloadOnHover = false,
  webpSrc = null, // WebP version for better compression
  progressive = false, // Enable progressive loading
  ...props
}) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [isInView, setIsInView] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [isBlurLoaded, setIsBlurLoaded] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const imgRef = useRef(null);
  const blurImgRef = useRef(null);
  const observerRef = useRef(null);

  // Generate WebP src if not provided
  const getWebpSrc = useCallback(() => {
    if (webpSrc) return webpSrc;
    if (src?.includes(".")) {
      return src.replace(/\.(jpg|jpeg|png)$/i, ".webp");
    }
    return null;
  }, [src, webpSrc]);

  // Check WebP support
  const supportsWebP = useCallback(() => {
    const canvas = document.createElement("canvas");
    canvas.width = 1;
    canvas.height = 1;
    return canvas.toDataURL("image/webp").startsWith("data:image/webp");
  }, []);

  // Get the best image source
  const getImageSrc = useCallback(() => {
    if (supportsWebP() && getWebpSrc()) {
      return getWebpSrc();
    }
    return src;
  }, [src, getWebpSrc, supportsWebP]);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true);
          observer.disconnect();
        }
      },
      {
        threshold: 0.1,
        rootMargin: "100px", // Increased for better UX
      },
    );

    if (imgRef.current) {
      observer.observe(imgRef.current);
      observerRef.current = observer;
    }

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, []);

  // Preload image on hover
  useEffect(() => {
    if (preloadOnHover && isHovered && !isInView) {
      setIsInView(true);
    }
  }, [isHovered, preloadOnHover, isInView]);

  const handleLoad = () => {
    setIsLoaded(true);
    if (onLoad) onLoad();
  };

  const handleError = () => {
    setHasError(true);
    if (onError) onError();
  };

  const handleBlurLoad = () => {
    setIsBlurLoaded(true);
  };

  const handleMouseEnter = () => {
    setIsHovered(true);
  };

  const handleMouseLeave = () => {
    setIsHovered(false);
  };

  return (
    <Box
      ref={imgRef}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      sx={{
        width,
        height,
        position: "relative",
        overflow: "hidden",
        borderRadius,
        backgroundColor: "grey.100",
        cursor: preloadOnHover ? "pointer" : "default",
        ...props.sx,
      }}
      {...props}
    >
      {/* Blur placeholder */}
      {blurSrc && !isLoaded && !hasError && (
        <motion.img
          ref={blurImgRef}
          src={blurSrc}
          alt=""
          onLoad={handleBlurLoad}
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            objectFit,
            filter: "blur(10px)",
            transform: "scale(1.1)",
            opacity: isBlurLoaded ? 0.6 : 0,
            transition: "opacity 0.3s ease",
          }}
        />
      )}

      {/* Placeholder/Skeleton */}
      {!isLoaded && !hasError && (
        <Skeleton
          variant="rectangular"
          width="100%"
          height="100%"
          sx={{
            position: "absolute",
            top: 0,
            left: 0,
            borderRadius,
            backgroundColor: "grey.200",
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
      )}

      {/* Custom placeholder */}
      {placeholder && !isLoaded && !hasError && (
        <Box
          sx={{
            position: "absolute",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            backgroundColor: "grey.100",
            borderRadius,
          }}
        >
          {placeholder}
        </Box>
      )}

      {/* Progressive loading indicator */}
      {progressive && isInView && !isLoaded && !hasError && (
        <Box
          sx={{
            position: "absolute",
            bottom: 8,
            left: "50%",
            transform: "translateX(-50%)",
            display: "flex",
            gap: 0.5,
          }}
        >
          {[0, 1, 2].map((i) => (
            <motion.div
              key={i}
              animate={{
                scale: [1, 1.2, 1],
                opacity: [0.5, 1, 0.5],
              }}
              transition={{
                duration: 1,
                repeat: Infinity,
                delay: i * 0.2,
              }}
              style={{
                width: 4,
                height: 4,
                borderRadius: "50%",
                backgroundColor: "#1976d2",
              }}
            />
          ))}
        </Box>
      )}

      {/* Actual image */}
      {isInView && (
        <motion.img
          src={getImageSrc()}
          alt={alt}
          onLoad={handleLoad}
          onError={handleError}
          initial={{ opacity: 0 }}
          animate={{
            opacity: isLoaded ? 1 : 0,
            filter: isLoaded ? "blur(0px)" : "blur(2px)",
          }}
          transition={{
            opacity: { duration: 0.3 },
            filter: { duration: 0.2 },
          }}
          style={{
            width: "100%",
            height: "100%",
            objectFit,
            display: hasError ? "none" : "block",
          }}
        />
      )}

      {/* Error placeholder */}
      {hasError && (
        <Box
          sx={{
            position: "absolute",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            backgroundColor: "grey.200",
            borderRadius,
            color: "text.secondary",
          }}
        >
          <Box sx={{ textAlign: "center" }}>
            <Box
              component="img"
              src="/placeholder.png"
              alt="Image not available"
              sx={{
                width: "50%",
                height: "auto",
                opacity: 0.5,
                mb: 1,
              }}
            />
            <Box sx={{ fontSize: "0.75rem", mt: 1 }}>Image unavailable</Box>
          </Box>
        </Box>
      )}
    </Box>
  );
};

LazyImage.propTypes = {
  src: PropTypes.string.isRequired,
  alt: PropTypes.string.isRequired,
  width: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  height: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  objectFit: PropTypes.string,
  borderRadius: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  placeholder: PropTypes.node,
  blurSrc: PropTypes.string,
  onLoad: PropTypes.func,
  onError: PropTypes.func,
  preloadOnHover: PropTypes.bool,
  webpSrc: PropTypes.string,
  progressive: PropTypes.bool,
  sx: PropTypes.object,
};

LazyImage.defaultProps = {
  width: "100%",
  height: "auto",
  objectFit: "cover",
  borderRadius: 0,
  preloadOnHover: false,
  progressive: false,
};

export default LazyImage;
