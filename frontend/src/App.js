import React, { useState, useEffect, useRef } from 'react';
import { Container, TextField, Button, Paper, Typography, Box } from '@mui/material';
import { AccountCircle, SmartToy } from '@mui/icons-material';
import './App.css';

function App() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [listening, setListening] = useState(false);
  const recognitionRef = useRef(null);

  // Set up speech recognition on mount if supported
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-US';
      recognition.onresult = (event) => {
        if (event.results.length > 0) {
          const transcript = event.results[0][0].transcript;
          setQuery(transcript);
        }
      };
      recognition.onerror = (event) => {
        console.error("Speech recognition error:", event.error);
        setListening(false);
      };
      recognition.onend = () => {
        setListening(false);
      };
      recognitionRef.current = recognition;
    } else {
      console.warn("Speech Recognition API not supported in this browser.");
    }
  }, []);

  // Save chat history to local storage whenever messages update
  useEffect(() => {
    localStorage.setItem('chatHistory', JSON.stringify(messages));
  }, [messages]);

  const startListening = () => {
    if (recognitionRef.current) {
      setListening(true);
      recognitionRef.current.start();
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    // Add user message to state
    const newMessages = [...messages, { text: query, sender: 'user' }];
    setMessages(newMessages);
    setLoading(true);
    setQuery("");

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, chatHistory: newMessages })
      });
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      const data = await res.json();
      console.log("Bot response:", data);

      // Add bot response to state
      setMessages([...newMessages, { text: data.answer, sender: 'bot', research: data.research }]);
    } catch (error) {
      console.error("Error fetching data:", error);
      setMessages([...newMessages, { text: "An error occurred. Please try again.", sender: 'bot' }]);
    }
    setLoading(false);
  };

  return (
    <Container maxWidth="md" className="App">
      <Box className="signature-container" textAlign="right" mb={2}>
        developed with ❤️ & ☕️ by<br />
        ~ Codes N' Roses
      </Box>

      <Paper elevation={3} style={{ padding: '20px', marginBottom: '20px' }}>
        <Typography variant="h4" gutterBottom>
          WildWise - AI: Wildlife Research Chat
        </Typography>
        <Typography variant="body1" gutterBottom>
          An AI-powered tool that scrapes research data and delivers comprehensive insights on wildlife, biodiversity, and conservation topics.
        </Typography>
      </Paper>

      <div className="chat-container">
        {messages.map((message, index) => (
          <Paper
            key={index}
            className={`message ${message.sender === 'user' ? 'user-message' : 'bot-message'}`}
            style={{ padding: '10px', marginBottom: '10px', alignSelf: message.sender === 'user' ? 'flex-end' : 'flex-start' }}
          >
            <div style={{ display: 'flex', alignItems: 'center' }}>
              {message.sender === 'user' ? (
                <AccountCircle className="message-icon" />
              ) : (
                <SmartToy className="message-icon" />
              )}
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                <Typography variant="body1">{message.text}</Typography>
                {message.research && message.research.length > 0 && (
                  <div className="research-container" style={{ marginTop: '10px' }}>
                    <Typography variant="h6">Research Papers:</Typography>
                    <ul>
                      {message.research.map((paper, idx) => (
                        <li key={idx}>
                          <a href={paper.url} target="_blank" rel="noopener noreferrer">
                            {paper.title}
                          </a>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          </Paper>
        ))}
      </div>

      <div className="form-container">
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column' }}>
          <TextField sx={{ mb: 2 }}
            fullWidth
            variant="outlined"
            placeholder="Ask me about wildlife, biodiversity, or conservation..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="chat-input"
          />
          <div className="button-container">
            <Button sx={{ mr: 2 }} variant="contained" color="primary" onClick={startListening} className="voice-button">
              {listening ? "Listening..." : "Voice Input"}
            </Button>
            <Button variant="contained" color="primary" type="submit" className="submit-button">
              Send
            </Button>
          </div>
        </form>
      </div>

      {loading && (
        <div className="loading-overlay">
        <img src="/running_tiger.gif" alt="Loading..." style={{ width: '100px', height: '100px' }} />
      </div>
      )}
    </Container>
  );
}

export default App;