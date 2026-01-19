import React, { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Button,
  TextField,
  Card,
  CardContent,
  Avatar,
  Divider,
  Collapse,
} from "@mui/material";
import { QuestionAnswer, ExpandMore, ExpandLess } from "@mui/icons-material";
import { useAuth } from "../../utils/AuthContext";
import { qnaAPI } from "../../services/api";

const ProductQnA = ({ productId }) => {
  const { isAuthenticated, user } = useAuth();
  const [questions, setQuestions] = useState([]);
  const [newQuestion, setNewQuestion] = useState("");
  const [replyContent, setReplyContent] = useState({});
  const [showReplyBox, setShowReplyBox] = useState({});

  useEffect(() => {
    if (productId) {
      loadQuestions();
    }
  }, [productId]);

  const loadQuestions = async () => {
    try {
      const res = await qnaAPI.getQuestions(productId);
      setQuestions(res.data.results || res.data);
    } catch (err) {
      console.error("Failed to load questions", err);
    }
  };

  const handleAskQuestion = async () => {
    if (!newQuestion.trim()) return;
    try {
      await qnaAPI.askQuestion(productId, newQuestion);
      setNewQuestion("");
      loadQuestions();
    } catch (err) {
      alert("Failed to post question");
    }
  };

  const handleAnswer = async (questionId) => {
    const content = replyContent[questionId];
    if (!content?.trim()) return;
    try {
      await qnaAPI.answerQuestion(questionId, content);
      setReplyContent({ ...replyContent, [questionId]: "" });
      setShowReplyBox({ ...showReplyBox, [questionId]: false });
      loadQuestions();
    } catch (err) {
      alert("Failed to post answer");
    }
  };

  return (
    <Box sx={{ mt: 4 }}>
      <Typography variant="h5" gutterBottom fontWeight="600">
        Questions & Answers
      </Typography>
      <Divider sx={{ mb: 3 }} />

      {/* Ask Question Box */}
      {isAuthenticated ? (
        <Box sx={{ mb: 4, display: "flex", gap: 2 }}>
          <TextField
            fullWidth
            label="Ask a question about this product"
            value={newQuestion}
            onChange={(e) => setNewQuestion(e.target.value)}
            multiline
            rows={2}
          />
          <Button
            variant="contained"
            onClick={handleAskQuestion}
            disabled={!newQuestion.trim()}
            sx={{ height: "fit-content", mt: 1 }}
          >
            Ask
          </Button>
        </Box>
      ) : (
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Please login to ask questions.
        </Typography>
      )}

      {/* Questions List */}
      {questions.length === 0 ? (
        <Typography color="text.secondary">
          No questions yet. Be the first to ask!
        </Typography>
      ) : (
        questions.map((q) => (
          <Card key={q.id} sx={{ mb: 2, borderRadius: 2, bgcolor: "#fafafa" }}>
            <CardContent>
              <Box sx={{ display: "flex", gap: 2, mb: 1 }}>
                <Avatar sx={{ width: 32, height: 32, bgcolor: "primary.main" }}>Q</Avatar>
                <Box>
                  <Typography variant="subtitle2" color="text.secondary">
                    {q.user} asked on {new Date(q.created_at).toLocaleDateString()}
                  </Typography>
                  <Typography variant="body1" fontWeight="500">
                    {q.content}
                  </Typography>
                </Box>
              </Box>

              {/* Answers */}
              <Box sx={{ pl: 6, mt: 2 }}>
                {q.answers.map((a) => (
                  <Box key={a.id} sx={{ mb: 2, display: "flex", gap: 2 }}>
                    <Avatar sx={{ width: 28, height: 28, bgcolor: a.is_vendor_reply ? "secondary.main" : "grey.400" }}>A</Avatar>
                    <Box>
                      <Typography variant="subtitle2" color="text.secondary" sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                        {a.is_vendor_reply ? "Vendor Response" : a.user}
                        {a.is_vendor_reply && <QuestionAnswer fontSize="small" color="secondary" />}
                      </Typography>
                      <Typography variant="body2">{a.content}</Typography>
                    </Box>
                  </Box>
                ))}

                {/* Reply Button */}
                {isAuthenticated && (
                  <Box>
                    <Button
                      size="small"
                      startIcon={showReplyBox[q.id] ? <ExpandLess /> : <ExpandMore />}
                      onClick={() => setShowReplyBox({ ...showReplyBox, [q.id]: !showReplyBox[q.id] })}
                    >
                      Answer this question
                    </Button>
                    <Collapse in={showReplyBox[q.id]}>
                      <Box sx={{ display: "flex", gap: 1, mt: 1 }}>
                        <TextField
                          fullWidth
                          size="small"
                          placeholder="Your answer..."
                          value={replyContent[q.id] || ""}
                          onChange={(e) => setReplyContent({ ...replyContent, [q.id]: e.target.value })}
                        />
                        <Button variant="contained" size="small" onClick={() => handleAnswer(q.id)}>
                          Post
                        </Button>
                      </Box>
                    </Collapse>
                  </Box>
                )}
              </Box>
            </CardContent>
          </Card>
        ))
      )}
    </Box>
  );
};

export default ProductQnA;
