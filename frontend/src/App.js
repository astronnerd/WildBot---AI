import React, { useState, useEffect, useRef } from 'react';
import './App.css';

function App() {
  const [query, setQuery] = useState("");
  const [responseData, setResponseData] = useState(null);
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

  const startListening = () => {
    if (recognitionRef.current) {
      setListening(true);
      recognitionRef.current.start();
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setResponseData(null);
    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });
      const data = await res.json();
      setResponseData(data);
    } catch (error) {
      console.error("Error fetching data:", error);
      setResponseData({ error: "An error occurred. Please try again." });
    }
    setLoading(false);
  };

  return (
    <div className="App">
      {/* Fixed signature container at top right */}
      <div className="signature-container">
        developed with ❤️ & ☕️ by<br />
        ~ Codes N' Roses
      </div>

      {/* Main Chat Window */}
      <header>
        <h1>WildWise - AI: Wildlife Research Chat</h1>
        <p className="description">
          <br />
          An AI-powered tool that scrapes research data and delivers comprehensive insights on wildlife, biodiversity, and conservation topics.
          <br />
          <br />
        </p>
      </header>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Ask me about wildlife, biodiversity, or conservation..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="chat-input"
        />
        <button type="button" onClick={startListening} className="voice-button">
          {listening ? "Listening..." : "Voice Input"}
        </button>
        <button type="submit" className="submit-button">Send</button>
      </form>
      {loading && <p>Loading...</p>}
      {responseData && (
        <div className="response-container">
          {responseData.error ? (
            <p>{responseData.error}</p>
          ) : (
            <>
              <div className="chat-response">
                <h2>Answer:</h2>
                <p>{responseData.answer}</p>
              </div>
              {responseData.research && (
                <div className="research-section">
                  <h3>Research Papers:</h3>
                  {responseData.research.length > 0 ? (
                    <ul>
                      {responseData.research.map((paper, index) => (
                        <li key={index}>
                          <a href={paper.url} target="_blank" rel="noopener noreferrer">
                            {paper.title}
                          </a>
                          <p>{paper.abstract}</p>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p>No research papers found.</p>
                  )}
                </div>
              )}
              {responseData.image_url && (
                <div className="image-section">
                  <h3>Related Image:</h3>
                  <img src={responseData.image_url} alt="Wildlife related" />
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
