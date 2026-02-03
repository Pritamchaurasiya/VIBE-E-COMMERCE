import React, { useState, useRef, useEffect } from 'react';
import { Box, TextField, Paper, Typography, IconButton, Fab } from '@mui/material';
import { Chat, Close, Send, SmartToy } from '@mui/icons-material';
import { chatAPI } from '../services/api';

const AgriBot = () => {
  const [open, setOpen] = useState(false);
  const [message, setMessage] = useState('');
  const [chatHistory, setChatHistory] = useState([
    { sender: 'bot', text: 'Hello! I am your Agri-Assistant. Ask me about rentals, schemes, or crop prices.' }
  ]);
  const chatEndRef = useRef(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatHistory, open]);

  const handleSend = async () => {
    if (!message.trim()) return;

    const userMessage = { sender: 'user', text: message };
    setChatHistory(prev => [...prev, userMessage]);
    setMessage('');

    try {
      const response = await chatAPI.sendMessage(message);
      const botMessage = { sender: 'bot', text: response.data.response };
      setChatHistory(prev => [...prev, botMessage]);
    } catch (error) {
      console.error("Error sending message:", error);
      const errorMessage = { sender: 'bot', text: 'Sorry, I am having trouble connecting. Please try again later.' };
      setChatHistory(prev => [...prev, errorMessage]);
    }
  };

  return (
    <>
      <Fab
        color="primary"
        aria-label="chat"
        sx={{ position: 'fixed', bottom: 20, right: 20, zIndex: 1000 }}
        onClick={() => setOpen(!open)}
      >
        {open ? <Close /> : <Chat />}
      </Fab>

      {open && (
        <Paper
          elevation={4}
          sx={{
            position: 'fixed',
            bottom: 90,
            right: 20,
            width: 320,
            height: 450,
            display: 'flex',
            flexDirection: 'column',
            zIndex: 1000,
            borderRadius: 2,
            overflow: 'hidden'
          }}
        >
          <Box sx={{ bgcolor: 'primary.main', color: 'white', p: 2, display: 'flex', alignItems: 'center' }}>
            <SmartToy sx={{ mr: 1 }} />
            <Typography variant="h6">Agri-Bot</Typography>
          </Box>

          <Box sx={{ flexGrow: 1, p: 2, overflowY: 'auto', bgcolor: '#f5f5f5' }}>
            {chatHistory.map((msg, index) => (
              <Box
                key={index}
                sx={{
                  display: 'flex',
                  justifyContent: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                  mb: 1.5
                }}
              >
                <Paper
                  sx={{
                    p: 1.5,
                    maxWidth: '80%',
                    bgcolor: msg.sender === 'user' ? 'primary.light' : 'white',
                    color: msg.sender === 'user' ? 'white' : 'text.primary',
                    borderRadius: 2
                  }}
                >
                  <Typography variant="body2">{msg.text}</Typography>
                </Paper>
              </Box>
            ))}
            <div ref={chatEndRef} />
          </Box>

          <Box sx={{ p: 1, display: 'flex', borderTop: '1px solid #e0e0e0' }}>
            <TextField
              fullWidth
              size="small"
              placeholder="Type a message..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            />
            <IconButton color="primary" onClick={handleSend} disabled={!message.trim()}>
              <Send />
            </IconButton>
          </Box>
        </Paper>
      )}
    </>
  );
};

export default AgriBot;
