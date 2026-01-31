import React, { useState, useRef, useEffect } from 'react';
import {
  Box, Paper, Typography, IconButton, TextField, Button,
  Avatar, CircularProgress, Fab, Tooltip, Chip, useTheme
} from '@mui/material';
import {
  Send, Close, SmartToy, Agriculture, BugReport, Cloud, Help
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { cropsAPI, diseasesAPI } from '../../services/api';

const AgriBot = () => {
  const theme = useTheme();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Namaste! I am your Kisan Sahayak (Agri-Advisor). How can I help you today?",
      sender: 'bot',
      type: 'text'
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isOpen]);

  const processMessage = async (text) => {
    setIsTyping(true);
    const lowerInput = text.toLowerCase();

    let botResponse = {
      id: Date.now(),
      sender: 'bot',
      type: 'text',
      text: "I didn't understand that. Please try asking about crops, diseases, or weather."
    };

    try {
      if (lowerInput.includes('crop') || lowerInput.includes('seed') || lowerInput.includes('plant')) {
        const response = await cropsAPI.getAll();
        const crops = response.data.crops ? response.data.crops.slice(0, 5) : [];
        if (crops.length > 0) {
          botResponse.text = "Here are some popular crops you can grow:";
          botResponse.type = 'crop_list';
          botResponse.data = crops;
        } else {
            botResponse.text = "I couldn't find any crop information at the moment.";
        }
      } else if (lowerInput.includes('disease') || lowerInput.includes('pest') || lowerInput.includes('bug')) {
        const response = await diseasesAPI.getAll();
        const diseases = response.data.diseases ? response.data.diseases.slice(0, 5) : [];
        if (diseases.length > 0) {
            botResponse.text = "Common crop diseases to watch out for:";
            botResponse.type = 'disease_list';
            botResponse.data = diseases;
        } else {
            botResponse.text = "I couldn't find any disease information at the moment.";
        }
      } else if (lowerInput.includes('weather') || lowerInput.includes('rain')) {
        botResponse.text = "I can't check real-time weather yet, but typically for this season (Kharif), expect heavy rains. Ensure proper drainage!";
      } else if (lowerInput.includes('hello') || lowerInput.includes('hi') || lowerInput.includes('namaste')) {
        botResponse.text = "Namaste! Ask me about 'popular crops', 'common diseases', or 'farming tips'.";
      } else if (lowerInput.includes('help')) {
        botResponse.text = "I can help you with:\n- Finding popular crops\n- Identifying diseases\n- Weather advice\n- General farming tips";
      }
    } catch (error) {
      console.error("Bot Error:", error);
      botResponse.text = "Sorry, I'm having trouble connecting to the server. Please check your internet connection.";
    }

    setIsTyping(false);
    setMessages(prev => [...prev, botResponse]);
  };

  const handleSend = () => {
    if (!inputValue.trim()) return;

    const text = inputValue;
    const userMessage = {
      id: Date.now(),
      text: text,
      sender: 'user',
      type: 'text'
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');

    // Process response
    processMessage(text);
  };

  const handleQuickAction = (query) => {
    const userMessage = {
      id: Date.now(),
      text: query,
      sender: 'user',
      type: 'text'
    };
    setMessages(prev => [...prev, userMessage]);
    processMessage(query);
  };

  const quickActions = [
    { label: 'Popular Crops', icon: <Agriculture fontSize="small" />, query: 'Show me popular crops' },
    { label: 'Crop Diseases', icon: <BugReport fontSize="small" />, query: 'Common crop diseases' },
    { label: 'Help', icon: <Help fontSize="small" />, query: 'Help' },
  ];

  return (
    <>
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 50, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 50, scale: 0.9 }}
            style={{
              position: 'fixed',
              bottom: 90,
              right: 20,
              zIndex: 1200, // Higher than other elements
            }}
          >
            <Paper
              elevation={6}
              sx={{
                width: { xs: 300, sm: 350 },
                height: 500,
                display: 'flex',
                flexDirection: 'column',
                overflow: 'hidden',
                borderRadius: 4,
                border: `1px solid ${theme.palette.divider}`,
                bgcolor: 'background.paper'
              }}
            >
              {/* Header */}
              <Box sx={{
                p: 2,
                bgcolor: 'primary.main',
                color: 'white',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
              }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Avatar sx={{ bgcolor: 'white', color: 'primary.main' }}>
                    <SmartToy />
                  </Avatar>
                  <Typography variant="subtitle1" fontWeight="bold">
                    Kisan Sahayak
                  </Typography>
                </Box>
                <IconButton size="small" onClick={() => setIsOpen(false)} sx={{ color: 'white' }}>
                  <Close />
                </IconButton>
              </Box>

              {/* Messages Area */}
              <Box sx={{
                flex: 1,
                p: 2,
                overflowY: 'auto',
                bgcolor: theme.palette.mode === 'dark' ? 'grey.900' : 'grey.50',
                display: 'flex',
                flexDirection: 'column',
                gap: 2
              }}>
                {messages.map((msg, index) => (
                  <Box
                    key={msg.id || index}
                    sx={{
                      alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                      maxWidth: '85%'
                    }}
                  >
                    <Paper
                      elevation={1}
                      sx={{
                        p: 1.5,
                        bgcolor: msg.sender === 'user' ? 'primary.main' : 'background.paper',
                        color: msg.sender === 'user' ? 'white' : 'text.primary',
                        borderRadius: 2,
                        borderTopRightRadius: msg.sender === 'user' ? 0 : 2,
                        borderTopLeftRadius: msg.sender === 'bot' ? 0 : 2
                      }}
                    >
                      <Typography variant="body2" sx={{ whiteSpace: 'pre-line' }}>{msg.text}</Typography>
                    </Paper>

                    {/* Render rich content if available */}
                    {msg.type === 'crop_list' && msg.data && (
                       <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                         {msg.data.map((crop, idx) => (
                           <Chip
                            key={crop.id || idx}
                            label={crop.name}
                            size="small"
                            icon={<Agriculture fontSize="small"/>}
                            component="a"
                            href={`/crop/${crop.slug}`}
                            clickable
                            sx={{ bgcolor: 'background.paper' }}
                           />
                         ))}
                       </Box>
                    )}
                    {msg.type === 'disease_list' && msg.data && (
                       <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                         {msg.data.map((disease, idx) => (
                           <Chip
                            key={disease.id || idx}
                            label={disease.name}
                            size="small"
                            color="error"
                            variant="outlined"
                            icon={<BugReport fontSize="small"/>}
                            component="a"
                            href={`/disease/${disease.slug}`}
                            clickable
                            sx={{ bgcolor: 'background.paper' }}
                           />
                         ))}
                       </Box>
                    )}
                  </Box>
                ))}

                {isTyping && (
                  <Box sx={{ alignSelf: 'flex-start', display: 'flex', alignItems: 'center', gap: 1, ml: 1 }}>
                     <CircularProgress size={16} />
                     <Typography variant="caption" color="text.secondary">Kisan Sahayak is typing...</Typography>
                  </Box>
                )}
                <div ref={messagesEndRef} />
              </Box>

              {/* Quick Actions (if no input) */}
              {!isTyping && (
                <Box sx={{ px: 2, py: 1, display: 'flex', gap: 1, overflowX: 'auto', bgcolor: 'background.paper' }}>
                  {quickActions.map((action, idx) => (
                    <Chip
                      key={idx}
                      icon={action.icon}
                      label={action.label}
                      onClick={() => handleQuickAction(action.query)}
                      variant="outlined"
                      size="small"
                      clickable
                      sx={{ borderColor: 'primary.light' }}
                    />
                  ))}
                </Box>
              )}

              {/* Input Area */}
              <Box sx={{ p: 2, borderTop: `1px solid ${theme.palette.divider}`, bgcolor: 'background.paper' }}>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <TextField
                    fullWidth
                    size="small"
                    placeholder="Ask about crops, diseases..."
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                    disabled={isTyping}
                    autoComplete="off"
                  />
                  <IconButton
                    color="primary"
                    onClick={handleSend}
                    disabled={!inputValue.trim() || isTyping}
                  >
                    <Send />
                  </IconButton>
                </Box>
              </Box>
            </Paper>
          </motion.div>
        )}
      </AnimatePresence>

      <Tooltip title="Chat with Agri-Advisor" placement="left">
        <Fab
          color="primary"
          aria-label="chat"
          onClick={() => setIsOpen(!isOpen)}
          sx={{
            position: 'fixed',
            bottom: 20,
            right: 20,
            zIndex: 1200,
            boxShadow: '0 4px 12px rgba(0,0,0,0.25)',
            transition: 'transform 0.2s',
            '&:hover': {
              transform: 'scale(1.1)'
            }
          }}
        >
          {isOpen ? <Close /> : <SmartToy />}
        </Fab>
      </Tooltip>
    </>
  );
};

export default AgriBot;
