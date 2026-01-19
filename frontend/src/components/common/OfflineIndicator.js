import React, { useState, useEffect } from 'react';
import { Box, Typography, Slide } from '@mui/material';
import { WifiOff } from '@mui/icons-material';

const OfflineIndicator = () => {
  const [isOffline, setIsOffline] = useState(!navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setIsOffline(false);
    const handleOffline = () => setIsOffline(true);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return (
    <Slide direction="down" in={isOffline} mountOnEnter unmountOnExit>
      <Box
        sx={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          zIndex: 9999,
          bgcolor: 'error.main',
          color: 'white',
          textAlign: 'center',
          py: 1,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 1
        }}
      >
        <WifiOff fontSize="small" />
        <Typography variant="body2" fontWeight="bold">
          You are currently offline. Some features may not work.
        </Typography>
      </Box>
    </Slide>
  );
};

export default OfflineIndicator;
