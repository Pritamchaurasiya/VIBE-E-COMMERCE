import React, { useState, useEffect } from 'react';
import { Snackbar, Alert } from '@mui/material';
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
    <Snackbar
      open={isOffline}
      anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
    >
      <Alert
        severity="warning"
        variant="filled"
        icon={<WifiOff fontSize="inherit" />}
        sx={{ width: '100%' }}
      >
        You are currently offline. Some features may be unavailable.
      </Alert>
    </Snackbar>
  );
};

export default OfflineIndicator;
