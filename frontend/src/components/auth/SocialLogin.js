import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../utils/AuthContext';
import { useDispatch } from 'react-redux';
import { setCredentials } from '../../features/auth/authSlice';
import {
  Box, Button, Divider, Typography, CircularProgress, Alert, useTheme
} from '@mui/material';
import { Google, Facebook, Apple } from '@mui/icons-material';
import { motion } from 'framer-motion';
import { secureApiRequest } from '../../utils/securityUtils';

const SocialLogin = ({ onSuccess, onError, redirectTo = '/' }) => {
  const theme = useTheme();
  const navigate = useNavigate();
  const { login } = useAuth();
  const dispatch = useDispatch();

  const [loading, setLoading] = useState(null); // null, 'google', 'facebook', 'apple'
  const [error, setError] = useState(null);

  const handleSocialLogin = async (provider) => {
    try {
      setLoading(provider);
      setError(null);

      // In a real app, this would initiate the OAuth flow
      // For this example, we'll simulate the process

      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1500));

      // Mock response - in a real app, this would come from your backend
      const mockResponse = {
        user: {
          id: 'user_' + Math.random().toString(36).substr(2, 9),
          name: `${provider.charAt(0).toUpperCase() + provider.slice(1)} User`,
          email: `${provider.toLowerCase()}_user@example.com`,
          role: 'customer',
          avatar: `https://i.pravatar.cc/150?u=${provider}_user`
        },
        token: 'mock_jwt_token_' + Math.random().toString(36).substr(2, 15),
        refreshToken: 'mock_refresh_token_' + Math.random().toString(36).substr(2, 15)
      };

      // Dispatch auth action
      dispatch(setCredentials({
        user: mockResponse.user,
        token: mockResponse.token
      }));

      // Call auth context login
      await login(mockResponse.token, mockResponse.user);

      // Call success callback
      if (onSuccess) {
        onSuccess(mockResponse);
      }

      // Redirect
      navigate(redirectTo);

    } catch (err) {
      console.error(`${provider} login failed:`, err);
      setError(err.message || `Failed to login with ${provider}`);
      if (onError) {
        onError(err);
      }
    } finally {
      setLoading(false);
    }
  };

  const getButtonStyle = (provider) => {
    const baseStyle = {
      borderRadius: 2,
      py: 1.5,
      px: 3,
      textTransform: 'none',
      fontWeight: 'medium',
      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
      transition: 'all 0.3s ease',
      '&:hover': {
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)'
      }
    };

    switch (provider) {
      case 'google':
        return {
          ...baseStyle,
          bgcolor: '#ffffff',
          color: '#757575',
          border: '1px solid #dadce0',
          '&:hover': {
            ...baseStyle['&:hover'],
            bgcolor: '#f8f9fa'
          }
        };
      case 'facebook':
        return {
          ...baseStyle,
          bgcolor: '#1877f2',
          color: '#ffffff',
          '&:hover': {
            ...baseStyle['&:hover'],
            bgcolor: '#166fe5'
          }
        };
      case 'apple':
        return {
          ...baseStyle,
          bgcolor: '#000000',
          color: '#ffffff',
          '&:hover': {
            ...baseStyle['&:hover'],
            bgcolor: '#1a1a1a'
          }
        };
      default:
        return baseStyle;
    }
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
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
        stiffness: 100
      }
    }
  };

  return (
    <Box sx={{ width: '100%', maxWidth: 400, mx: 'auto' }}>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {/* Google Login */}
          <motion.div variants={itemVariants}>
            <Button
              fullWidth
              startIcon={loading === 'google' ? <CircularProgress size={20} /> : <Google />}
              onClick={() => handleSocialLogin('google')}
              disabled={!!loading}
              sx={getButtonStyle('google')}
            >
              {loading === 'google' ? 'Signing in with Google...' : 'Continue with Google'}
            </Button>
          </motion.div>

          {/* Facebook Login */}
          <motion.div variants={itemVariants}>
            <Button
              fullWidth
              startIcon={loading === 'facebook' ? <CircularProgress size={20} /> : <Facebook />}
              onClick={() => handleSocialLogin('facebook')}
              disabled={!!loading}
              sx={getButtonStyle('facebook')}
            >
              {loading === 'facebook' ? 'Signing in with Facebook...' : 'Continue with Facebook'}
            </Button>
          </motion.div>

          {/* Apple Login */}
          <motion.div variants={itemVariants}>
            <Button
              fullWidth
              startIcon={loading === 'apple' ? <CircularProgress size={20} /> : <Apple />}
              onClick={() => handleSocialLogin('apple')}
              disabled={!!loading}
              sx={getButtonStyle('apple')}
            >
              {loading === 'apple' ? 'Signing in with Apple...' : 'Continue with Apple'}
            </Button>
          </motion.div>
        </Box>
      </motion.div>

      <Divider sx={{ my: 3 }}>
        <Typography variant="body2" color="text.secondary">
          or continue with email
        </Typography>
      </Divider>
    </Box>
  );
};

export default SocialLogin;