import React, { useState, useEffect } from 'react';
import { Typography, Box, Card, CardContent, Grid, Button } from '@mui/material';
import axios from 'axios';

const InventoryPrediction = () => {
    const [predictions, setPredictions] = useState([]);

    // Mock getting a list of products to predict for demo
    useEffect(() => {
        // In real app, fetch list of low stock products first
        // Here we just mock checking product ID 1
        const checkPrediction = async () => {
            try {
                const res = await axios.get('/api/v1/inventory-prediction/1/');
                setPredictions([res.data]);
            } catch (err) {
                console.error(err);
            }
        };
        checkPrediction();
    }, []);

    return (
        <Box sx={{ p: 3 }}>
            <Typography variant="h4">Inventory AI Prediction</Typography>
            <Grid container spacing={2} sx={{ mt: 2 }}>
                {predictions.map((p, i) => (
                    <Grid item xs={12} md={4} key={i}>
                        <Card>
                            <CardContent>
                                <Typography variant="h6">Product #{p.product_id}</Typography>
                                <Typography variant="h3" color="error">{p.days_until_stockout} Days</Typography>
                                <Typography variant="caption">Until Stockout</Typography>
                            </CardContent>
                        </Card>
                    </Grid>
                ))}
            </Grid>
        </Box>
    );
};

export default InventoryPrediction;
