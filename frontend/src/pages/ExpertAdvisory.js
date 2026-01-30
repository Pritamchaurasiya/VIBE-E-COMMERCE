import React, { useState, useEffect } from "react";
import {
  Container,
  Typography,
  Box,
  Button,
  Card,
  CardContent,
  CardActions,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  Avatar,
  Divider,
  MenuItem,
  Tab,
  Tabs,
} from "@mui/material";
import { QuestionAnswer, Person, VerifiedUser, Add } from "@mui/icons-material";
import agriService from "../services/agriService";

const ExpertAdvisory = () => {
  const [questions, setQuestions] = useState([]);
  const [tab, setTab] = useState(0);
  const [open, setOpen] = useState(false);
  const [newQuestion, setNewQuestion] = useState({
    topic: "general",
    question: "",
  });

  const topics = [
    { value: "crop_disease", label: "Crop Disease" },
    { value: "pest_control", label: "Pest Control" },
    { value: "fertilizer", label: "Fertilizer Use" },
    { value: "seeds", label: "Seeds & Sowing" },
    { value: "weather", label: "Weather Related" },
    { value: "general", label: "General Inquiry" },
  ];

  useEffect(() => {
    fetchQuestions();
  }, [tab]);

  const fetchQuestions = async () => {
    try {
      const response = await agriService.getAdvisory({
        status: tab === 0 ? "" : "answered", // Tab 0: All/My, Tab 1: Answered
      });
      setQuestions(response.data.results || response.data);
    } catch (err) {
      console.error("Failed to fetch advisory", err);
    }
  };

  const handleAsk = async () => {
    try {
      await agriService.askQuestion(newQuestion);
      setOpen(false);
      fetchQuestions();
      setNewQuestion({ topic: "general", question: "" });
    } catch (err) {
      alert("Failed to post question");
    }
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Box textAlign="center" mb={4}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: "bold", color: "#2e7d32" }}>
          Expert Advisory
        </Typography>
        <Typography variant="subtitle1" color="textSecondary">
          Get answers from agricultural experts for your farming queries.
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setOpen(true)}
          sx={{ mt: 2, bgcolor: "#2e7d32" }}
        >
          Ask an Expert
        </Button>
      </Box>

      <Tabs value={tab} onChange={(e, v) => setTab(v)} centered sx={{ mb: 3 }}>
        <Tab label="My Questions" />
        <Tab label="Community Q&A" />
      </Tabs>

      <Box>
        {questions.map((q) => (
          <Card key={q.id} sx={{ mb: 2, borderLeft: q.status === 'answered' ? '4px solid #4caf50' : '4px solid #ff9800' }}>
            <CardContent>
              <Box display="flex" justifyContent="space-between" mb={1}>
                <Chip label={topics.find(t => t.value === q.topic)?.label || q.topic} size="small" color="primary" variant="outlined" />
                <Typography variant="caption" color="textSecondary">
                  {new Date(q.created_at).toLocaleDateString()}
                </Typography>
              </Box>
              <Typography variant="h6" gutterBottom>
                {q.question}
              </Typography>

              {q.status === 'answered' && (
                <Box mt={2} p={2} bgcolor="#f1f8e9" borderRadius={2} border="1px solid #c8e6c9">
                  <Box display="flex" alignItems="center" gap={1} mb={1}>
                    <VerifiedUser color="success" fontSize="small" />
                    <Typography variant="subtitle2" color="success.main">
                      Expert Answer:
                    </Typography>
                  </Box>
                  <Typography variant="body1">
                    {q.answer}
                  </Typography>
                  <Box display="flex" alignItems="center" gap={1} mt={1} justifyContent="flex-end">
                    <Avatar sx={{ width: 24, height: 24, bgcolor: "#2e7d32", fontSize: 12 }}>E</Avatar>
                    <Typography variant="caption" fontWeight="bold">
                      {q.answered_by_name || "Agri Expert"}
                    </Typography>
                  </Box>
                </Box>
              )}

              {q.status === 'open' && (
                <Typography variant="body2" color="textSecondary" sx={{ fontStyle: 'italic', mt: 1 }}>
                  Waiting for expert response...
                </Typography>
              )}
            </CardContent>
          </Card>
        ))}
      </Box>

      {/* Ask Question Dialog */}
      <Dialog open={open} onClose={() => setOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>Ask an Expert</DialogTitle>
        <DialogContent>
          <Box component="form" sx={{ mt: 1 }}>
            <TextField
              select
              fullWidth
              label="Topic"
              margin="normal"
              value={newQuestion.topic}
              onChange={(e) => setNewQuestion({ ...newQuestion, topic: e.target.value })}
            >
              {topics.map((t) => (
                <MenuItem key={t.value} value={t.value}>
                  {t.label}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              fullWidth
              multiline
              rows={4}
              label="Your Question"
              placeholder="Describe your problem in detail..."
              margin="normal"
              value={newQuestion.question}
              onChange={(e) => setNewQuestion({ ...newQuestion, question: e.target.value })}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button onClick={handleAsk} variant="contained" color="primary">
            Submit Question
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default ExpertAdvisory;
