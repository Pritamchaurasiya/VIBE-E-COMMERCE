import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchRecommendedProducts, selectRecommendedProducts, selectProductStatus } from '../../features/products/productSlice';
import { Box, Typography, CircularProgress, Grid, Card, CardMedia, CardContent, CardActions, Button, Chip, Rating, Skeleton } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../../utils/AuthContext';

const ProductRecommendations = ({ userId, productId }) => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const recommendedProducts = useSelector(selectRecommendedProducts);
  const status = useSelector(selectProductStatus);
  const [algorithm, setAlgorithm] = useState('collaborative'); // 'collaborative' | 'content-based' | 'hybrid'

  useEffect(() => {
    if (isAuthenticated && userId) {
      dispatch(fetchRecommendedProducts(userId));
    }
  }, [dispatch, userId, isAuthenticated, algorithm]);

  const handleProductClick = (productId) => {
    navigate(`/products/${productId}`);
  };

  const handleAlgorithmChange = (newAlgorithm) => {
    setAlgorithm(newAlgorithm);
    // In a real app, you would call a different API endpoint based on the algorithm
    if (isAuthenticated && userId) {
      dispatch(fetchRecommendedProducts(userId));
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

  if (!isAuthenticated) {
    return (
      <Box sx={{ mt: 4, p: 2, backgroundColor: 'background.paper', borderRadius: 2 }}>
        <Typography variant="h6" gutterBottom>
          Personalized Recommendations
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Please log in to see personalized product recommendations based on your preferences and browsing history.
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h5" fontWeight="bold">
          Recommended for You
        </Typography>

        <Box sx={{ display: 'flex', gap: 1 }}>
          <Chip
            label="Collaborative"
            variant={algorithm === 'collaborative' ? 'filled' : 'outlined'}
            color={algorithm === 'collaborative' ? 'primary' : 'default'}
            onClick={() => handleAlgorithmChange('collaborative')}
            clickable
          />
          <Chip
            label="Content-Based"
            variant={algorithm === 'content-based' ? 'filled' : 'outlined'}
            color={algorithm === 'content-based' ? 'primary' : 'default'}
            onClick={() => handleAlgorithmChange('content-based')}
            clickable
          />
          <Chip
            label="Hybrid"
            variant={algorithm === 'hybrid' ? 'filled' : 'outlined'}
            color={algorithm === 'hybrid' ? 'primary' : 'default'}
            onClick={() => handleAlgorithmChange('hybrid')}
            clickable
          />
        </Box>
      </Box>

      {status === 'loading' ? (
        <Grid container spacing={2}>
          {[...Array(4)].map((_, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Skeleton variant="rectangular" width="100%" height={200} />
              <Skeleton variant="text" width="80%" />
              <Skeleton variant="text" width="60%" />
              <Skeleton variant="rectangular" width="100%" height={40} />
            </Grid>
          ))}
        </Grid>
      ) : status === 'failed' ? (
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', py: 4 }}>
          <Typography variant="body1" color="text.secondary">
            Could not load recommendations. Please try again later.
          </Typography>
        </Box>
      ) : recommendedProducts && recommendedProducts.length > 0 ? (
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          <Grid container spacing={2}>
            {recommendedProducts.map((product) => (
              <Grid item xs={12} sm={6} md={3} key={product.id}>
                <motion.div variants={itemVariants}>
                  <Card
                    sx={{
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                      transition: 'transform 0.3s, box-shadow 0.3s',
                      '&:hover': {
                        transform: 'translateY(-5px)',
                        boxShadow: '0 8px 16px rgba(0,0,0,0.1)'
                      }
                    }}
                  >
                    <CardMedia
                      component="div"
                      sx={{
                        pt: '100%',
                        position: 'relative',
                        cursor: 'pointer',
                        backgroundColor: '#f5f5f5'
                      }}
                      onClick={() => handleProductClick(product.id)}
                    >
                      {product.image ? (
                        <Box
                          component="img"
                          src={product.image}
                          alt={product.name}
                          sx={{
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            width: '100%',
                            height: '100%',
                            objectFit: 'contain',
                            p: 1
                          }}
                        />
                      ) : (
                        <Box
                          sx={{
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            width: '100%',
                            height: '100%',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            backgroundColor: '#f5f5f5'
                          }}
                        >
                          <Typography variant="body2" color="text.secondary">
                            No Image
                          </Typography>
                        </Box>
                      )}
                    </CardMedia>

                    <CardContent sx={{ flexGrow: 1 }}>
                      <Typography gutterBottom variant="subtitle1" component="div" noWrap>
                        {product.name}
                      </Typography>

                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <Rating
                          name="product-rating"
                          value={product.rating || 0}
                          precision={0.5}
                          readOnly
                          size="small"
                        />
                        <Typography variant="body2" color="text.secondary" sx={{ ml: 0.5 }}>
                          ({product.review_count || 0})
                        </Typography>
                      </Box>

                      <Typography variant="h6" color="primary" fontWeight="bold">
                        ${product.price?.toFixed(2)}
                      </Typography>

                      {product.discount && (
                        <Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
                          <Typography variant="body2" color="text.secondary" sx={{ textDecoration: 'line-through', mr: 1 }}>
                            ${(product.price / (1 - product.discount)).toFixed(2)}
                          </Typography>
                          <Chip
                            label={`${Math.round(product.discount * 100)}% OFF`}
                            size="small"
                            color="error"
                          />
                        </Box>
                      )}
                    </CardContent>

                    <CardActions sx={{ justifyContent: 'space-between', p: 1 }}>
                      <Button
                        size="small"
                        variant="outlined"
                        onClick={() => handleProductClick(product.id)}
                      >
                        View Details
                      </Button>
                      <Button
                        size="small"
                        variant="contained"
                        color="primary"
                        disabled={!product.in_stock}
                      >
                        {product.in_stock ? 'Add to Cart' : 'Out of Stock'}
                      </Button>
                    </CardActions>
                  </Card>
                </motion.div>
              </Grid>
            ))}
          </Grid>
        </motion.div>
      ) : (
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', py: 4 }}>
          <Typography variant="body1" color="text.secondary">
            No recommendations available yet. Start browsing products to get personalized suggestions!
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default ProductRecommendations;