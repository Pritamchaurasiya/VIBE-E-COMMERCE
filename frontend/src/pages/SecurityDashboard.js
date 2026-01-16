import React, { useState, useEffect } from 'react';
import {
    Box, Typography, Card, CardContent, Button, TextField, Alert,
    List, ListItem, ListItemText, Divider
} from '@mui/material';
import axios from 'axios';

const SecurityDashboard = () => {
    const [dashboardData, setDashboardData] = useState(null);
    const [phone, setPhone] = useState('');
    const [otp, setOtp] = useState('');
    const [otpSent, setOtpSent] = useState(false);
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

    useEffect(() => {
        fetchDashboard();
    }, []);

    const fetchDashboard = async () => {
        try {
            const res = await axios.get('/api/v1/security/dashboard/');
            setDashboardData(res.data);
        } catch (err) {
            console.error(err);
        }
    };

    const handleSendOTP = async () => {
        try {
            const res = await axios.post('/api/v1/auth/send-otp/', { phone, purpose: 'verify' });
            setOtpSent(true);
            setMessage(`OTP sent! (Debug: ${res.data.debug_otp})`);
            setError('');
        } catch (err) {
            setError('Failed to send OTP');
        }
    };

    const handleVerifyOTP = async () => {
        try {
            await axios.post('/api/v1/auth/verify-otp/', { phone, otp, purpose: 'verify' });
            setMessage('Phone verified successfully!');
            setOtpSent(false);
            setPhone('');
            setOtp('');
        } catch (err) {
            setError('Invalid OTP');
        }
    };

    return (
        <Box sx={{ p: 3 }}>
            <Typography variant="h4" gutterBottom>Security Settings</Typography>

            <Card sx={{ mb: 3 }}>
                <CardContent>
                    <Typography variant="h6">Two-Factor Authentication</Typography>
                    <Typography color="textSecondary" paragraph>
                        Secure your account with phone verification.
                    </Typography>

                    {message && <Alert severity="success" sx={{ mb: 2 }}>{message}</Alert>}
                    {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

                    <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                        <TextField
                            label="Phone Number"
                            value={phone}
                            onChange={(e) => setPhone(e.target.value)}
                            disabled={otpSent}
                        />
                        {!otpSent ? (
                            <Button variant="contained" onClick={handleSendOTP}>
                                Send OTP
                            </Button>
                        ) : (
                            <>
                                <TextField
                                    label="Enter OTP"
                                    value={otp}
                                    onChange={(e) => setOtp(e.target.value)}
                                />
                                <Button variant="contained" color="success" onClick={handleVerifyOTP}>
                                    Verify
                                </Button>
                            </>
                        )}
                    </Box>
                </CardContent>
            </Card>

            <Card>
                <CardContent>
                    <Typography variant="h6">Recent Login Activity</Typography>
                    <List>
                        {dashboardData?.recent_sessions?.map((session, index) => (
                            <React.Fragment key={index}>
                                <ListItem>
                                    <ListItemText
                                        primary={`Session started: ${new Date(session.started_at).toLocaleString()}`}
                                        secondary={`IP: ${session.ip_address || 'Unknown'} | Device: ${session.device_type || 'Unknown'}`}
                                    />
                                </ListItem>
                                <Divider />
                            </React.Fragment>
                        ))}
                        {(!dashboardData?.recent_sessions || dashboardData.recent_sessions.length === 0) && (
                            <Typography sx={{ p: 2 }}>No recent activity found.</Typography>
                        )}
                    </List>
                </CardContent>
            </Card>
        </Box>
    );
};

export default SecurityDashboard;
