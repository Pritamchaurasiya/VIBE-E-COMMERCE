import React, { useState, useEffect } from 'react';
import { Box, Typography, Paper } from '@mui/material';
import { AccessTime } from '@mui/icons-material';

const FlashSaleWidget = ({ endTime }) => {
  const [timeLeft, setTimeLeft] = useState(calculateTimeLeft());

  function calculateTimeLeft() {
    const difference = +new Date(endTime) - +new Date();
    let timeLeft = {};

    if (difference > 0) {
      timeLeft = {
        days: Math.floor(difference / (1000 * 60 * 60 * 24)),
        hours: Math.floor((difference / (1000 * 60 * 60)) % 24),
        minutes: Math.floor((difference / 1000 / 60) % 60),
        seconds: Math.floor((difference / 1000) % 60),
      };
    }
    return timeLeft;
  }

  useEffect(() => {
    const timer = setTimeout(() => {
      setTimeLeft(calculateTimeLeft());
    }, 1000);

    return () => clearTimeout(timer);
  });

  const TimeUnit = ({ value, label }) => (
    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mx: 0.5 }}>
      <Paper
        elevation={0}
        sx={{
          bgcolor: 'error.main',
          color: 'white',
          p: 1,
          borderRadius: 1,
          minWidth: 32,
          textAlign: 'center',
          fontWeight: 'bold',
          fontSize: '1rem'
        }}
      >
        {String(value).padStart(2, '0')}
      </Paper>
      <Typography variant="caption" sx={{ mt: 0.5, fontSize: '0.65rem', fontWeight: 600, color: 'text.secondary' }}>
        {label}
      </Typography>
    </Box>
  );

  if (Object.keys(timeLeft).length === 0) {
    return <Typography color="error" fontWeight="bold">Sale Ended!</Typography>;
  }

  return (
    <Box sx={{ display: 'flex', alignItems: 'center' }}>
      <AccessTime sx={{ color: 'error.main', mr: 1 }} fontSize="small" />
      <Typography variant="body2" fontWeight="bold" color="error.main" sx={{ mr: 2, display: { xs: 'none', sm: 'block' } }}>
        Ends In:
      </Typography>
      <Box sx={{ display: 'flex' }}>
        {timeLeft.days > 0 && <TimeUnit value={timeLeft.days} label="DAYS" />}
        <TimeUnit value={timeLeft.hours} label="HRS" />
        <Typography sx={{ alignSelf: 'flex-start', mt: 1, fontWeight: 'bold' }}>:</Typography>
        <TimeUnit value={timeLeft.minutes} label="MIN" />
        <Typography sx={{ alignSelf: 'flex-start', mt: 1, fontWeight: 'bold' }}>:</Typography>
        <TimeUnit value={timeLeft.seconds} label="SEC" />
      </Box>
    </Box>
  );
};

export default FlashSaleWidget;
