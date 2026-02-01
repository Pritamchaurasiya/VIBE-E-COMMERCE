import React, { useEffect } from "react";
import PropTypes from "prop-types";
import { motion, useAnimation } from "framer-motion";
import { useInView } from "react-intersection-observer";

const ScrollAnimation = ({
  children,
  animation = "fadeUp",
  delay = 0,
  duration = 0.6,
  threshold = 0.1,
  className = "",
  direction = "up",
  distance = 50,
  scale = 0.8,
  easing = "easeOut",
  triggerOnce = true,
  staggerChildren = false,
  staggerDelay = 0.1,
  ...props
}) => {
  const controls = useAnimation();
  const [ref, inView] = useInView({
    threshold,
    triggerOnce,
  });

  const getDirectionalAnimation = (type, dir, dist, scl) => {
    const directions = {
      up: { y: dist },
      down: { y: -dist },
      left: { x: -dist },
      right: { x: dist },
    };

    const transform = directions[dir] || directions.up;

    switch (type) {
      case "fade":
        return {
          initial: { opacity: 0, ...transform },
          animate: { opacity: 1, x: 0, y: 0 },
        };
      case "slide":
        return {
          initial: { ...transform },
          animate: { x: 0, y: 0 },
        };
      case "scale":
        return {
          initial: { opacity: 0, scale: scl, ...transform },
          animate: { opacity: 1, scale: 1, x: 0, y: 0 },
        };
      case "rotate":
        return {
          initial: { opacity: 0, rotate: -180, scale: scl },
          animate: { opacity: 1, rotate: 0, scale: 1 },
        };
      case "flip":
        return {
          initial: { opacity: 0, rotateY: -90 },
          animate: { opacity: 1, rotateY: 0 },
        };
      default:
        // For unknown types, return a simple fade animation
        return {
          initial: { opacity: 0 },
          animate: { opacity: 1 },
        };
    }
  };

  const animations = {
    fadeUp: getDirectionalAnimation("fade", "up", distance, scale),
    fadeDown: getDirectionalAnimation("fade", "down", distance, scale),
    fadeLeft: getDirectionalAnimation("fade", "left", distance, scale),
    fadeRight: getDirectionalAnimation("fade", "right", distance, scale),
    slideUp: getDirectionalAnimation("slide", "up", distance, scale),
    slideDown: getDirectionalAnimation("slide", "down", distance, scale),
    slideLeft: getDirectionalAnimation("slide", "left", distance, scale),
    slideRight: getDirectionalAnimation("slide", "right", distance, scale),
    scale: getDirectionalAnimation("scale", direction, distance, scale),
    rotate: getDirectionalAnimation("rotate", direction, distance, scale),
    flip: getDirectionalAnimation("flip", direction, distance, scale),
    zoomIn: {
      initial: { opacity: 0, scale: 0.5 },
      animate: { opacity: 1, scale: 1 },
      transition: { type: "spring", stiffness: 300, damping: 30 },
    },
    zoomOut: {
      initial: { opacity: 0, scale: 1.5 },
      animate: { opacity: 1, scale: 1 },
      transition: { type: "spring", stiffness: 300, damping: 30 },
    },
    bounce: {
      initial: { opacity: 0, scale: 0.3, y: distance },
      animate: { opacity: 1, scale: 1, y: 0 },
      transition: { type: "spring", stiffness: 400, damping: 10 },
    },
    elastic: {
      initial: { opacity: 0, scale: 0.3, y: distance },
      animate: { opacity: 1, scale: 1, y: 0 },
      transition: { type: "spring", stiffness: 500, damping: 15, mass: 1 },
    },
    slideIn: {
      initial: { opacity: 0, x: -100 },
      animate: { opacity: 1, x: 0 },
    },
  };

  useEffect(() => {
    if (inView) {
      controls.start("animate");
    }
  }, [controls, inView]);

  const selectedAnimation = animations[animation] || animations.fadeUp;

  const containerVariants = staggerChildren
    ? {
        initial: {},
        animate: {
          transition: {
            staggerChildren: staggerDelay,
          },
        },
      }
    : selectedAnimation;

  const itemVariants = staggerChildren ? selectedAnimation : {};

  // Always use motion.div as the wrapper component

  return (
    <motion.div
      ref={ref}
      initial="initial"
      animate={controls}
      variants={containerVariants}
      transition={{
        duration,
        delay,
        ease: easing,
        ...selectedAnimation.transition,
      }}
      className={className}
      {...props}
    >
      {staggerChildren
        ? React.Children.map(children, (child) => (
            <motion.div variants={itemVariants}>{child}</motion.div>
          ))
        : children}
    </motion.div>
  );
};

ScrollAnimation.propTypes = {
  children: PropTypes.node.isRequired,
  animation: PropTypes.oneOf([
    "fadeUp",
    "fadeDown",
    "fadeLeft",
    "fadeRight",
    "slideUp",
    "slideDown",
    "slideLeft",
    "slideRight",
    "scale",
    "rotate",
    "flip",
    "zoomIn",
    "zoomOut",
    "bounce",
    "elastic",
    "slideIn",
  ]),
  delay: PropTypes.number,
  duration: PropTypes.number,
  threshold: PropTypes.number,
  className: PropTypes.string,
  direction: PropTypes.oneOf(["up", "down", "left", "right"]),
  distance: PropTypes.number,
  scale: PropTypes.number,
  easing: PropTypes.string,
  triggerOnce: PropTypes.bool,
  staggerChildren: PropTypes.bool,
  staggerDelay: PropTypes.number,
};

ScrollAnimation.defaultProps = {
  animation: "fadeUp",
  delay: 0,
  duration: 0.6,
  threshold: 0.1,
  className: "",
  direction: "up",
  distance: 50,
  scale: 0.8,
  easing: "easeOut",
  triggerOnce: true,
  staggerChildren: false,
  staggerDelay: 0.1,
};

export default ScrollAnimation;
