import React, { useState, useEffect } from 'react';
import TopNav from '../components/layout/TopNav';
import { Typography, Table, TableBody, TableCell, TableHead, TableRow, Button, TextField, Box } from '@mui/material';
import api from '../services/api';

const SecurityDashboard = () => {
  const [data, setData] = useState({ blocked_ips: [], recent_access: [] });
  const [ipToBlock, setIpToBlock] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    const res = await api.get('/api/v1/admin/security/');
    setData(res.data);
  };

  const handleBlock = async () => {
    await api.post('/api/v1/admin/security/', { action: 'block', ip: ipToBlock });
    setIpToBlock('');
    fetchData();
  };

  const handleUnblock = async (ip) => {
    await api.post('/api/v1/admin/security/', { action: 'unblock', ip });
    fetchData();
  };

  return (
    <div className="agri-theme">
      <TopNav />
      <div style={{ padding: 20 }}>
        <Typography variant="h4" gutterBottom>Security Dashboard</Typography>

        <Box mb={4}>
          <Typography variant="h6">Blocked IPs</Typography>
          <Box display="flex" gap={2} mb={2}>
            <TextField
              label="IP Address"
              value={ipToBlock}
              onChange={(e) => setIpToBlock(e.target.value)}
              size="small"
            />
            <Button variant="contained" color="error" onClick={handleBlock}>Block IP</Button>
          </Box>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>IP Address</TableCell>
                <TableCell>Reason</TableCell>
                <TableCell>Action</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {data.blocked_ips.map(item => (
                <TableRow key={item.id}>
                  <TableCell>{item.ip_address}</TableCell>
                  <TableCell>{item.reason}</TableCell>
                  <TableCell>
                    <Button onClick={() => handleUnblock(item.ip_address)}>Unblock</Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Box>

        <Box>
          <Typography variant="h6">Recent System Access</Typography>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Timestamp</TableCell>
                <TableCell>IP</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Risk</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {data.recent_access.map(item => (
                <TableRow key={item.id}>
                  <TableCell>{new Date(item.access_timestamp).toLocaleString()}</TableCell>
                  <TableCell>{item.ip_address}</TableCell>
                  <TableCell>{item.access_type}</TableCell>
                  <TableCell>{item.risk_level}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Box>
      </div>
    </div>
  );
};

export default SecurityDashboard;
