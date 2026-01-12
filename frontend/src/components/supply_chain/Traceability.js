import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Typography, Box, Stepper, Step, StepLabel, Card, CardContent } from '@mui/material';
import axios from 'axios';

const SupplyChainTraceability = () => {
    const { batchNumber } = useParams();
    const [batchData, setBatchData] = useState(null);

    useEffect(() => {
        const fetchBatch = async () => {
            try {
                const response = await axios.get(\`/api/v1/supply-chain/batch/\${batchNumber}/\`);
                setBatchData(response.data);
            } catch (error) {
                console.error("Error fetching batch data", error);
            }
        };
        fetchBatch();
    }, [batchNumber]);

    if (!batchData) return <Typography>Loading traceability info...</Typography>;

    return (
        <Box sx={{ p: 3 }}>
            <Typography variant="h4" gutterBottom>Traceability: Batch {batchData.batch_number}</Typography>
            <Card sx={{ mb: 3 }}>
                <CardContent>
                    <Typography variant="h6">{batchData.product_name}</Typography>
                    <Typography color="textSecondary">Exp: {batchData.expiration_date}</Typography>
                </CardContent>
            </Card>

            <Stepper orientation="vertical">
                {batchData.journey.map((point, index) => (
                    <Step key={index} active={true}>
                        <StepLabel>
                            <Typography variant="subtitle1">{point.location}</Typography>
                            <Typography variant="caption">{new Date(point.timestamp).toLocaleString()}</Typography>
                            <Typography variant="body2">{point.status}</Typography>
                        </StepLabel>
                    </Step>
                ))}
            </Stepper>
        </Box>
    );
};

export default SupplyChainTraceability;
