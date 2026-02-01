import React, { useState, useEffect } from "react";
import { Fab, Zoom } from "@mui/material";
import { KeyboardArrowUp } from "@mui/icons-material";
import { motion } from "framer-motion";
import PropTypes from "prop-types";

/**
 * Back to Top button that appears when user scrolls down
 */
const BackToTop = ({ threshold = 300 }) => {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setVisible(window.scrollY > threshold);
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, [threshold]);

  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  return (
    <Zoom in={visible}>
      <motion.div
        initial={{ scale: 0 }}
        animate={{ scale: visible ? 1 : 0 }}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        style={{
          position: "fixed",
          bottom: 24,
          right: 24,
          zIndex: 1000,
        }}
      >
        <Fab
          color="primary"
          size="medium"
          onClick={scrollToTop}
          aria-label="scroll back to top"
          sx={{
            background: "linear-gradient(135deg, #22c55e 0%, #16a34a 100%)",
            boxShadow: "0 4px 20px rgba(34, 197, 94, 0.3)",
            "&:hover": {
              background: "linear-gradient(135deg, #16a34a 0%, #15803d 100%)",
              boxShadow: "0 6px 25px rgba(34, 197, 94, 0.4)",
            },
          }}
        >
          <KeyboardArrowUp />
        </Fab>
      </motion.div>
    </Zoom>
  );
};

BackToTop.propTypes = {
  threshold: PropTypes.number,
};

export default BackToTop;
