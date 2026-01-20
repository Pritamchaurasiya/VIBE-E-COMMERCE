import React, { useState } from 'react';
import {
    Container, Typography, Box, Grid, TextField, Button,
    Card, CardContent, Paper, List, ListItem, ListItemText,
    Alert, CircularProgress, ListItemIcon
} from '@mui/material';
import { Science, Grass, WaterDrop, CheckCircle, Warning } from '@mui/icons-material';
import axios from 'axios';
import TopNav from '../components/layout/TopNav';
import BottomNav from '../components/layout/BottomNav';
import AgriProductCard from '../components/products/AgriProductCard';

const SoilHealth = () => {
    const [formData, setFormData] = useState({
        n: '',
        p: '',
        k: '',
        ph: ''
    });
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setResult(null);

        try {
            const response = await axios.post('/api/v1/soil-health/', formData);
            setResult(response.data);
        } catch (err) {
            console.error(err);
            setError('Failed to analyze data. Please check your inputs.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ backgroundColor: '#f5f5f5', minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
            <TopNav />
            <Container maxWidth="lg" sx={{ mt: 4, mb: 8, flexGrow: 1 }}>
                <Typography variant="h4" component="h1" gutterBottom fontWeight="bold" color="primary">
                    <Science sx={{ mr: 1, verticalAlign: 'bottom' }} />
                    Soil Health Analysis
                </Typography>
                <Typography variant="body1" paragraph color="textSecondary">
                    Enter your soil test results (N, P, K, pH) to get personalized fertilizer recommendations and crop advice.
                </Typography>

                <Grid container spacing={4}>
                    <Grid item xs={12} md={5}>
                        <Paper elevation={3} sx={{ p: 3, borderRadius: 2 }}>
                            <form onSubmit={handleSubmit}>
                                <Typography variant="h6" gutterBottom>
                                    Enter Soil Parameters
                                </Typography>
                                <Grid container spacing={2}>
                                    <Grid item xs={12}>
                                        <TextField
                                            fullWidth
                                            label="Nitrogen (N)"
                                            name="n"
                                            type="number"
                                            value={formData.n}
                                            onChange={handleChange}
                                            required
                                            helperText="mg/kg (ppm)"
                                            InputProps={{
                                                endAdornment: <Grass color="action" />
                                            }}
                                        />
                                    </Grid>
                                    <Grid item xs={12}>
                                        <TextField
                                            fullWidth
                                            label="Phosphorus (P)"
                                            name="p"
                                            type="number"
                                            value={formData.p}
                                            onChange={handleChange}
                                            required
                                            helperText="mg/kg (ppm)"
                                            InputProps={{
                                                endAdornment: <Science color="action" />
                                            }}
                                        />
                                    </Grid>
                                    <Grid item xs={12}>
                                        <TextField
                                            fullWidth
                                            label="Potassium (K)"
                                            name="k"
                                            type="number"
                                            value={formData.k}
                                            onChange={handleChange}
                                            required
                                            helperText="mg/kg (ppm)"
                                            InputProps={{
                                                endAdornment: <WaterDrop color="action" />
                                            }}
                                        />
                                    </Grid>
                                    <Grid item xs={12}>
                                        <TextField
                                            fullWidth
                                            label="Soil pH"
                                            name="ph"
                                            type="number"
                                            inputProps={{ step: "0.1", min: "0", max: "14" }}
                                            value={formData.ph}
                                            onChange={handleChange}
                                            required
                                            helperText="0-14 scale"
                                        />
                                    </Grid>
                                    <Grid item xs={12}>
                                        <Button
                                            type="submit"
                                            variant="contained"
                                            color="primary"
                                            fullWidth
                                            size="large"
                                            disabled={loading}
                                        >
                                            {loading ? <CircularProgress size={24} /> : 'Analyze Soil'}
                                        </Button>
                                    </Grid>
                                </Grid>
                            </form>
                        </Paper>
                    </Grid>

                    <Grid item xs={12} md={7}>
                        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

                        {result && (
                            <Box>
                                <Paper elevation={3} sx={{ p: 3, borderRadius: 2, mb: 4, bgcolor: '#e8f5e9' }}>
                                    <Typography variant="h5" gutterBottom fontWeight="bold" color="success.main">
                                        Analysis Results
                                    </Typography>
                                    <List>
                                        {result.analysis.map((item, index) => (
                                            <ListItem key={index}>
                                                <ListItemIcon>
                                                    <Warning color="warning" />
                                                </ListItemIcon>
                                                <ListItemText primary={item} />
                                            </ListItem>
                                        ))}
                                    </List>

                                    <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                                        Recommendations:
                                    </Typography>
                                    <List dense>
                                        {result.recommendations.map((item, index) => (
                                            <ListItem key={index}>
                                                <ListItemIcon>
                                                    <CheckCircle color="success" />
                                                </ListItemIcon>
                                                <ListItemText primary={item} />
                                            </ListItem>
                                        ))}
                                    </List>
                                </Paper>

                                {result.products && result.products.length > 0 && (
                                    <Box>
                                        <Typography variant="h6" gutterBottom fontWeight="bold">
                                            Recommended Products
                                        </Typography>
                                        <Grid container spacing={2}>
                                            {result.products.map(product => (
                                                <Grid item xs={12} sm={6} key={product.id}>
                                                    <AgriProductCard product={product} />
                                                </Grid>
                                            ))}
                                        </Grid>
                                    </Box>
                                )}
                            </Box>
                        )}

                        {!result && !loading && !error && (
                            <Box display="flex" justifyContent="center" alignItems="center" height="100%" flexDirection="column" opacity={0.6}>
                                <Science sx={{ fontSize: 80, color: 'text.disabled', mb: 2 }} />
                                <Typography variant="h6" color="textSecondary">
                                    Results will appear here
                                </Typography>
                            </Box>
                        )}
                    </Grid>
                </Grid>
            </Container>
            <BottomNav />
        </div>
    );
};

export default SoilHealth;
