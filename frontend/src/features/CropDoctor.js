import React, { useState } from 'react';
import { Box, Button, Typography, Card, CardMedia, CardContent, CircularProgress, Alert, Chip } from '@mui/material';
import { CloudUpload } from '@mui/icons-material';
import axios from 'axios';

const CropDoctor = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleImageChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedImage(file);
      setPreview(URL.createObjectURL(file));
      setResult(null);
      setError(null);
    }
  };

  const handleDiagnose = async () => {
    if (!selectedImage) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('image', selectedImage);

    try {
      const response = await axios.post('/api/v1/ai/diagnose/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setResult(response.data);
    } catch (err) {
      setError('Diagnosis failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ maxWidth: 600, mx: 'auto', p: 3 }}>
      <Typography variant="h4" gutterBottom align="center" sx={{ fontWeight: 'bold', color: 'success.main' }}>
        AI Crop Doctor
      </Typography>
      <Typography variant="body1" align="center" sx={{ mb: 3, color: 'text.secondary' }}>
        Upload a photo of your crop to detect diseases instantly.
      </Typography>

      <Card sx={{ mb: 3, boxShadow: 3 }}>
        <Box sx={{ p: 2, textAlign: 'center', border: '2px dashed #ccc', m: 2, borderRadius: 2, bgcolor: '#fafafa' }}>
          <input
            accept="image/*"
            style={{ display: 'none' }}
            id="raised-button-file"
            type="file"
            onChange={handleImageChange}
          />
          <label htmlFor="raised-button-file">
            <Button variant="outlined" component="span" startIcon={<CloudUpload />}>
              Upload Crop Image
            </Button>
          </label>
        </Box>
        {preview && (
          <Box sx={{ p: 2 }}>
            <CardMedia
              component="img"
              height="300"
              image={preview}
              alt="Crop Preview"
              sx={{ objectFit: 'contain', borderRadius: 2 }}
            />
          </Box>
        )}
        <CardContent>
          <Button
            fullWidth
            variant="contained"
            color="success"
            onClick={handleDiagnose}
            disabled={!selectedImage || loading}
            size="large"
          >
            {loading ? <CircularProgress size={24} color="inherit" /> : 'Diagnose Disease'}
          </Button>
        </CardContent>
      </Card>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {result && (
        <Card sx={{ bgcolor: '#f0fdf4', border: '1px solid #bbf7d0', boxShadow: 2 }}>
          <CardContent>
            <Typography variant="h5" color="success.dark" gutterBottom fontWeight="bold">
              Diagnosis: {result.disease.name}
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Typography variant="body2" color="text.secondary" sx={{ mr: 1 }}>
                Confidence Score:
                </Typography>
                <Chip label={`${result.confidence}%`} color={result.confidence > 90 ? "success" : "warning"} size="small" />
            </Box>

            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle1" fontWeight="bold">Symptoms:</Typography>
              <Typography variant="body1">{result.disease.symptoms}</Typography>
            </Box>
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle1" fontWeight="bold">Prevention:</Typography>
              <Typography variant="body1">{result.disease.prevention}</Typography>
            </Box>
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle1" fontWeight="bold" color="primary">Treatment:</Typography>
              <Typography variant="body1">{result.disease.treatment}</Typography>
            </Box>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default CropDoctor;
