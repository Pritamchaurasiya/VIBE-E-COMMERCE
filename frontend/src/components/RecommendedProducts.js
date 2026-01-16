import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardMedia, Typography, Grid, Button, Box } from '@mui/material';
import axios from 'axios';
import { Link } from 'react-router-dom';

const RecommendedProducts = () => {
  const [products, setProducts] = useState([]);

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        const response = await axios.get('/api/v1/personalized/');
        setProducts(response.data.recommendations);
      } catch (error) {
        console.error("Error fetching recommendations:", error);
      }
    };
    fetchRecommendations();
  }, []);

  if (products.length === 0) return null;

  return (
    <Box sx={{ my: 4 }}>
      <Typography variant="h5" gutterBottom component="div" sx={{ fontWeight: 'bold' }}>
        Recommended for You
      </Typography>
      <Grid container spacing={2}>
        {products.map((product) => (
          <Grid item key={product.id} xs={6} sm={4} md={3}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <CardMedia
                component="img"
                height="140"
                image={product.image || 'https://via.placeholder.com/150'}
                alt={product.name}
              />
              <CardContent sx={{ flexGrow: 1 }}>
                <Typography gutterBottom variant="h6" component="div" noWrap>
                  {product.name}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  ₹{product.price}
                </Typography>
                <Button
                    component={Link}
                    to={`/product/${product.slug}`}
                    size="small"
                    variant="contained"
                    sx={{ mt: 1 }}
                >
                    View
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default RecommendedProducts;
