import React, { useState, useEffect } from "react";
import {
  Container,
  Typography,
  Box,
  Button,
  Card,
  CardContent,
  Grid,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  MenuItem,
  LinearProgress,
  Chip,
  Alert,
} from "@mui/material";
import { Add, Science, CheckCircle } from "@mui/icons-material";
import agriService from "../services/agriService";

const SoilHealthDashboard = () => {
  const [reports, setReports] = useState([]);
  const [farms, setFarms] = useState([]);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [newReport, setNewReport] = useState({
    farm: "",
    sample_date: new Date().toISOString().split('T')[0],
    ph_level: "",
    nitrogen: "",
    phosphorus: "",
    potassium: "",
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [reportsRes, farmsRes] = await Promise.all([
        agriService.getSoilReports(),
        agriService.getFarms(),
      ]);
      setReports(reportsRes.data.results || reportsRes.data);
      setFarms(farmsRes.data.results || farmsRes.data);
      setLoading(false);
    } catch (err) {
      console.error("Failed to fetch data", err);
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    try {
      await agriService.addSoilReport(newReport);
      setOpen(false);
      fetchData();
      setNewReport({
        farm: "",
        sample_date: new Date().toISOString().split('T')[0],
        ph_level: "",
        nitrogen: "",
        phosphorus: "",
        potassium: "",
      });
    } catch (err) {
      alert("Failed to save report");
    }
  };

  const getNutrientStatus = (val, low, high) => {
    if (val < low) return "Low";
    if (val > high) return "High";
    return "Optimal";
  };

  const getNutrientColor = (status) => {
    if (status === "Optimal") return "success";
    if (status === "Low") return "warning";
    return "error";
  };

  if (loading) return <LinearProgress />;

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Soil Health Dashboard
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setOpen(true)}
          sx={{ bgcolor: "#5d4037", "&:hover": { bgcolor: "#3e2723" } }}
        >
          New Soil Test
        </Button>
      </Box>

      <Grid container spacing={3}>
        {reports.map((report) => (
          <Grid item xs={12} key={report.id}>
            <Card elevation={3}>
              <CardContent>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={4}>
                    <Typography variant="h6" color="primary">
                      {report.farm_name}
                    </Typography>
                    <Typography color="textSecondary" variant="body2">
                      Sample Date: {report.sample_date}
                    </Typography>
                    <Box mt={2} p={2} bgcolor="#f1f8e9" borderRadius={2}>
                      <Typography variant="subtitle2" fontWeight="bold">
                        Recommendations:
                      </Typography>
                      <Typography variant="body2" sx={{ whiteSpace: 'pre-line' }}>
                        {report.recommendations || "No specific issues detected."}
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} md={8}>
                    <Grid container spacing={2}>
                      {[
                        { label: "pH Level", val: report.ph_level, min: 6, max: 7.5 },
                        { label: "Nitrogen (N)", val: report.nitrogen, min: 280, max: 560 },
                        { label: "Phosphorus (P)", val: report.phosphorus, min: 10, max: 25 },
                        { label: "Potassium (K)", val: report.potassium, min: 108, max: 280 },
                      ].map((item) => {
                        const status = getNutrientStatus(item.val, item.min, item.max);
                        return (
                          <Grid item xs={6} sm={3} key={item.label}>
                            <Box textAlign="center" p={2} border={1} borderColor="#eee" borderRadius={2}>
                              <Typography variant="caption" color="textSecondary">
                                {item.label}
                              </Typography>
                              <Typography variant="h6">
                                {item.val}
                              </Typography>
                              <Chip
                                label={status}
                                size="small"
                                color={getNutrientColor(status)}
                                sx={{ mt: 1, height: 20, fontSize: '0.7rem' }}
                              />
                            </Box>
                          </Grid>
                        );
                      })}
                    </Grid>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Add Report Dialog */}
      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Log Soil Test Result</DialogTitle>
        <DialogContent>
          <Box component="form" sx={{ mt: 2 }}>
            <TextField
              select
              fullWidth
              label="Select Farm"
              margin="normal"
              value={newReport.farm}
              onChange={(e) => setNewReport({ ...newReport, farm: e.target.value })}
            >
              {farms.map((farm) => (
                <MenuItem key={farm.id} value={farm.id}>
                  {farm.name}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              fullWidth
              label="Sample Date"
              type="date"
              margin="normal"
              InputLabelProps={{ shrink: true }}
              value={newReport.sample_date}
              onChange={(e) => setNewReport({ ...newReport, sample_date: e.target.value })}
            />
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="pH Level"
                  type="number"
                  margin="normal"
                  value={newReport.ph_level}
                  onChange={(e) => setNewReport({ ...newReport, ph_level: e.target.value })}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Nitrogen (kg/ha)"
                  type="number"
                  margin="normal"
                  value={newReport.nitrogen}
                  onChange={(e) => setNewReport({ ...newReport, nitrogen: e.target.value })}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Phosphorus (kg/ha)"
                  type="number"
                  margin="normal"
                  value={newReport.phosphorus}
                  onChange={(e) => setNewReport({ ...newReport, phosphorus: e.target.value })}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Potassium (kg/ha)"
                  type="number"
                  margin="normal"
                  value={newReport.potassium}
                  onChange={(e) => setNewReport({ ...newReport, potassium: e.target.value })}
                />
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained" color="primary">
            Submit Report
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default SoilHealthDashboard;
