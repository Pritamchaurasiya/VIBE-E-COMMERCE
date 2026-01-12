import React, { useState, useEffect } from 'react';
import { Box, Card, CardContent, Typography, Stepper, Step, StepLabel, Chip, Button, Divider, Skeleton } from '@mui/material';
import { LocalShipping, Inventory, AssignmentTurnedIn, VerifiedUser, Flag } from '@mui/icons-material';
import { motion } from 'framer-motion';

const steps = [
  { label: 'Harvested', icon: <Inventory />, description: 'Crop harvested at farm' },
  { label: 'Processing', icon: <AssignmentTurnedIn />, description: 'Quality check and processing' },
  { label: 'In Transit', icon: <LocalShipping />, description: 'Shipped to distribution center' },
  { label: 'Quality Verified', icon: <VerifiedUser />, description: 'Final quality verification' },
  { label: 'Delivered', icon: <Flag />, description: 'Available at vendor' },
];

const SupplyChainTracker = ({ batchId }) => {
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(true);
  const [batchData, setBatchData] = useState(null);

  useEffect(() => {
    // Simulate API call
    const fetchBatchData = async () => {
      setLoading(true);
      setTimeout(() => {
        setBatchData({
          id: batchId || 'BATCH-2024-001',
          farm: 'Green Valley Farms',
          harvestDate: '2024-05-15',
          currentStatus: 2, // 0-based index
          temperature: '24°C',
          humidity: '65%',
          location: 'Pune Distribution Center'
        });
        setActiveStep(2);
        setLoading(false);
      }, 1500);
    };

    fetchBatchData();
  }, [batchId]);

  if (loading) {
    return <Skeleton variant="rectangular" height={300} sx={{ borderRadius: 2 }} />;
  }

  return (
    <Card sx={{ borderRadius: 3, boxShadow: '0 4px 20px rgba(0,0,0,0.05)', mb: 4 }}>
      <CardContent sx={{ p: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
          <Box>
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              Supply Chain Traceability
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Batch ID: <Chip label={batchData.id} size="small" sx={{ ml: 1, fontWeight: 'bold' }} />
            </Typography>
          </Box>
          <Button variant="outlined" startIcon={<VerifiedUser color="success" />}>
            Blockchain Verified
          </Button>
        </Box>

        <Stepper activeStep={activeStep} alternativeLabel>
          {steps.map((step, index) => (
            <Step key={step.label}>
              <StepLabel
                StepIconComponent={(props) => {
                  const { active, completed } = props;
                  return (
                    <motion.div
                      initial={{ scale: 0.8 }}
                      animate={{ scale: active ? 1.2 : 1 }}
                      transition={{ type: "spring", stiffness: 300 }}
                    >
                      <Box
                        sx={{
                          bgcolor: active || completed ? 'primary.main' : 'grey.300',
                          color: 'white',
                          width: 40,
                          height: 40,
                          borderRadius: '50%',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          boxShadow: active ? '0 0 0 4px rgba(34, 197, 94, 0.2)' : 'none',
                        }}
                      >
                        {step.icon}
                      </Box>
                    </motion.div>
                  );
                }}
              >
                <Typography fontWeight={index === activeStep ? 'bold' : 'normal'}>{step.label}</Typography>
                <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 0.5, maxWidth: 120, mx: 'auto' }}>
                  {step.description}
                </Typography>
              </StepLabel>
            </Step>
          ))}
        </Stepper>

        <Divider sx={{ my: 4 }} />

        <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: 2 }}>
          <Box>
            <Typography variant="caption" color="text.secondary">Origin Farm</Typography>
            <Typography variant="subtitle1" fontWeight="600">{batchData.farm}</Typography>
          </Box>
          <Box>
            <Typography variant="caption" color="text.secondary">Harvest Date</Typography>
            <Typography variant="subtitle1" fontWeight="600">{batchData.harvestDate}</Typography>
          </Box>
          <Box>
            <Typography variant="caption" color="text.secondary">Current Location</Typography>
            <Typography variant="subtitle1" fontWeight="600">{batchData.location}</Typography>
          </Box>
          <Box>
            <Typography variant="caption" color="text.secondary">Storage Conditions</Typography>
            <Typography variant="subtitle1" fontWeight="600" color="primary">
              {batchData.temperature} • {batchData.humidity}
            </Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default SupplyChainTracker;
