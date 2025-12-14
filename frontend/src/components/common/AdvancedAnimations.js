import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence, useScroll, useTransform } from 'framer-motion';
import { Box, Typography, useTheme } from '@mui/material';

// Parallax Scrolling Section
export const ParallaxSection = ({ children, speed = 0.5, backgroundImage, height = '500px', overlayColor = 'rgba(0, 0, 0, 0.5)' }) => {
  const [offsetY, setOffsetY] = useState(0);

  const handleScroll = () => {
    setOffsetY(window.scrollY);
  };

  useEffect(() => {
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <Box
      sx={{
        position: 'relative',
        height: height,
        overflow: 'hidden',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      {/* Background Image with Parallax Effect */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          backgroundImage: `url(${backgroundImage})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundAttachment: 'fixed',
          transform: `translateY(${offsetY * speed}px)`,
          zIndex: 1,
        }}
      />

      {/* Overlay */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          backgroundColor: overlayColor,
          zIndex: 2,
        }}
      />

      {/* Content */}
      <Box sx={{ position: 'relative', zIndex: 3 }}>
        {children}
      </Box>
    </Box>
  );
};

// Animated Gradient Background
export const GradientBackground = ({ children, colors = ['#667eea', '#764ba2'], angle = 45 }) => {
  return (
    <Box
      sx={{
        position: 'relative',
        background: `linear-gradient(${angle}deg, ${colors.join(', ')})`,
        minHeight: '100vh',
        overflow: 'hidden',
      }}
    >
      {/* Animated floating elements */}
      <motion.div
        animate={{
          scale: [1, 1.2, 1],
          rotate: [0, 180, 360],
          opacity: [0.1, 0.3, 0.1]
        }}
        transition={{
          duration: 20,
          ease: "easeInOut",
          times: [0, 0.5, 1],
          repeat: Infinity,
          repeatDelay: 1
        }}
        style={{
          position: 'absolute',
          top: '10%',
          left: '10%',
          width: 100,
          height: 100,
          backgroundColor: 'rgba(255, 255, 255, 0.1)',
          borderRadius: '50%',
          zIndex: 0,
        }}
      />

      <motion.div
        animate={{
          x: [0, 100, 0],
          y: [0, -50, 0],
          opacity: [0.2, 0.4, 0.2]
        }}
        transition={{
          duration: 15,
          ease: "easeInOut",
          times: [0, 0.5, 1],
          repeat: Infinity,
          repeatDelay: 2
        }}
        style={{
          position: 'absolute',
          bottom: '20%',
          right: '15%',
          width: 150,
          height: 150,
          backgroundColor: 'rgba(255, 255, 255, 0.1)',
          borderRadius: '30%',
          zIndex: 0,
        }}
      />

      {/* Content */}
      <Box sx={{ position: 'relative', zIndex: 1 }}>
        {children}
      </Box>
    </Box>
  );
};

// Scroll-Triggered Animation
export const ScrollTriggeredAnimation = ({ children, threshold = 0.1 }) => {
  const [isVisible, setIsVisible] = useState(false);
  const [hasAnimated, setHasAnimated] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      if (!hasAnimated) {
        const element = document.getElementById('scroll-trigger-element');
        if (element) {
          const rect = element.getBoundingClientRect();
          const isVisible = rect.top < window.innerHeight * threshold && rect.bottom > 0;
          setIsVisible(isVisible);
          if (isVisible) {
            setHasAnimated(true);
          }
        }
      }
    };

    window.addEventListener('scroll', handleScroll);
    handleScroll(); // Check on initial render

    return () => window.removeEventListener('scroll', handleScroll);
  }, [hasAnimated, threshold]);

  return (
    <motion.div
      id="scroll-trigger-element"
      initial={{ opacity: 0, y: 50 }}
      animate={isVisible ? { opacity: 1, y: 0 } : { opacity: 0, y: 50 }}
      transition={{ duration: 0.8, ease: "easeOut" }}
    >
      {children}
    </motion.div>
  );
};

// Staggered List Animation
export const StaggeredList = ({ items, renderItem, itemsPerRow = 4 }) => {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        type: 'spring',
        stiffness: 100,
        damping: 12
      }
    }
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      style={{ display: 'grid', gridTemplateColumns: `repeat(auto-fill, minmax(250px, 1fr))`, gap: '1rem' }}
    >
      {items.map((item, index) => (
        <motion.div key={index} variants={itemVariants}>
          {renderItem(item, index)}
        </motion.div>
      ))}
    </motion.div>
  );
};

// Hover Effect Card
export const HoverEffectCard = ({ children, hoverScale = 1.05, hoverRotate = 2 }) => {
  return (
    <motion.div
      whileHover={{
        scale: hoverScale,
        rotate: hoverRotate,
        transition: { duration: 0.3 }
      }}
      whileTap={{ scale: 0.95 }}
      style={{ display: 'inline-block' }}
    >
      {children}
    </motion.div>
  );
};

// Loading Skeleton with Animation
export const AnimatedSkeleton = ({ width = '100%', height = '20px', borderRadius = '4px' }) => {
  return (
    <motion.div
      initial={{ opacity: 0.3 }}
      animate={{ opacity: 0.8 }}
      transition={{ duration: 1.5, repeat: Infinity, repeatType: 'reverse' }}
      style={{
        width: width,
        height: height,
        backgroundColor: '#e0e0e0',
        borderRadius: borderRadius,
        marginBottom: '0.5rem'
      }}
    />
  );
};

// Typewriter Effect
export const TypewriterEffect = ({ text, speed = 50, delay = 0 }) => {
  const [displayedText, setDisplayedText] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (currentIndex < text.length) {
      const timeout = setTimeout(() => {
        setDisplayedText(prev => prev + text[currentIndex]);
        setCurrentIndex(prev => prev + 1);
      }, speed);

      return () => clearTimeout(timeout);
    }
  }, [currentIndex, text, speed]);

  return <Typography variant="body1">{displayedText}</Typography>;
};

// Particle Background (simplified version)
export const ParticleBackground = ({ children, particleCount = 50, particleSize = 5 }) => {
  const particles = Array.from({ length: particleCount }, (_, i) => ({
    id: i,
    size: Math.random() * particleSize + 2,
    x: Math.random() * 100,
    y: Math.random() * 100,
    delay: Math.random() * 5,
    duration: Math.random() * 10 + 5,
    color: `hsl(${Math.random() * 60 + 180}, 70%, 50%)`
  }));

  return (
    <Box sx={{
      position: 'relative',
      width: '100%',
      height: '100%',
      overflow: 'hidden'
    }}>
      {/* Particles */}
      {particles.map((particle) => (
        <motion.div
          key={particle.id}
          animate={{
            x: ['0%', '100%', '0%'],
            y: ['0%', '50%', '100%'],
            opacity: [0, 1, 0]
          }}
          transition={{
            duration: particle.duration,
            ease: "linear",
            delay: particle.delay,
            repeat: Infinity
          }}
          style={{
            position: 'absolute',
            width: particle.size,
            height: particle.size,
            backgroundColor: particle.color,
            borderRadius: '50%',
            zIndex: 0
          }}
        />
      ))}

      {/* Content */}
      <Box sx={{ position: 'relative', zIndex: 1 }}>
        {children}
      </Box>
    </Box>
  );
};

// Animated Counter
export const AnimatedCounter = ({ from = 0, to, duration = 2, suffix = '' }) => {
  const [count, setCount] = useState(from);

  useEffect(() => {
    let start = from;
    const end = to;
    const range = end - start;
    const increment = range / (duration * 60); // 60fps
    let current = start;

    const timer = setInterval(() => {
      current += increment;
      if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
        current = end;
        clearInterval(timer);
      }
      setCount(Math.floor(current));
    }, 16); // ~60fps

    return () => clearInterval(timer);
  }, [from, to, duration]);

  return <Typography variant="h3" fontWeight="bold">{count}{suffix}</Typography>;
};