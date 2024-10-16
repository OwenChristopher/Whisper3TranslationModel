// src/components/AudioRecorder.js
import React, { useState, useRef, useContext } from 'react';
import { processAudio } from '../api';
import { Button, Typography, Box, CircularProgress } from '@mui/material';
import { Mic, Stop } from '@mui/icons-material';
import { SessionContext } from '../contexts/SessionContext';

const AudioRecorder = ({ onResponse }) => {
  const { sessionId } = useContext(SessionContext);
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const startRecording = async () => {
    if (!sessionId) {
      alert('Please set your objective first.');
      return;
    }

    if (navigator.mediaDevices) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorderRef.current = new MediaRecorder(stream);
        mediaRecorderRef.current.start();
        setIsRecording(true);

        mediaRecorderRef.current.ondataavailable = (event) => {
          audioChunksRef.current.push(event.data);
        };

        mediaRecorderRef.current.onstop = async () => {
          setIsProcessing(true);
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
          audioChunksRef.current = [];
          const audioFile = new File([audioBlob], 'recording.wav', { type: 'audio/wav' });

          try {
            const response = await processAudio(sessionId, audioFile);
            onResponse(response);
          } catch (error) {
            console.error('Error processing audio:', error);
            alert('Failed to process audio.');
          } finally {
            setIsProcessing(false);
          }
        };
      } catch (error) {
        console.error('Error accessing microphone:', error);
        alert('Microphone access denied.');
      }
    } else {
      alert('Media Devices API not supported.');
    }
  };

  const stopRecording = () => {
    mediaRecorderRef.current.stop();
    setIsRecording(false);
  };

  return (
    <Box sx={{ p: 2, border: '1px solid #ccc', borderRadius: 2, mb: 2, textAlign: 'center' }}>
      <Typography variant="h5">Record Your Audio</Typography>
      {!isProcessing ? (
        <Button
          variant="contained"
          color={isRecording ? "secondary" : "primary"}
          onClick={isRecording ? stopRecording : startRecording}
          startIcon={isRecording ? <Stop /> : <Mic />}
          sx={{ mt: 2 }}
        >
          {isRecording ? 'Stop Recording' : 'Start Recording'}
        </Button>
      ) : (
        <CircularProgress sx={{ mt: 2 }} />
      )}
    </Box>
  );
};

export default AudioRecorder;

// src/components/ConversationHistory.js

import React, { useEffect, useRef } from 'react';
import { Box, Typography, Paper, List, ListItem, ListItemText, Divider } from '@mui/material';

const ConversationHistory = ({ history }) => {
  const listEndRef = useRef(null);

  useEffect(() => {
    // Scroll to the bottom when a new message is added
    if (listEndRef.current) {
      listEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [history]);

  const parseMessage = (item) => {
    // Check for prefixes
    const prefixes = ["[USER]", "[TARGET]", "[CAUTION]", "[SUMMARY]"];
    for (let prefix of prefixes) {
      if (item.content.startsWith(prefix)) {
        return {
          type: prefix.replace('[', '').replace(']', ''),
          content: item.content.replace(prefix, '').trim(),
        };
      }
    }
    // Default to ASSISTANT if no prefix found
    return { type: 'ASSISTANT', content: item.content };
  };

  return (
    <Box sx={{ mt: 4 }}>
      <Typography variant="h5" gutterBottom>
        Conversation Logs
      </Typography>
      <Paper elevation={3} sx={{ maxHeight: 400, overflowY: 'auto', padding: 2 }}>
        <List>
          {history.map((item, index) => {
            const { type, content } = parseMessage(item);
            return (
              <React.Fragment key={index}>
                <ListItem alignItems="flex-start">
                  <ListItemText
                    primary={
                      <Typography
                        variant="subtitle2"
                        color={
                          type === 'USER'
                            ? 'primary'
                            : type === 'TARGET'
                            ? 'secondary'
                            : type === 'CAUTION' || type === 'SUMMARY'
                            ? 'error'
                            : 'textPrimary'
                        }
                      >
                        {type === 'USER'
                          ? 'You'
                          : type === 'TARGET'
                          ? 'Target'
                          : type === 'CAUTION'
                          ? 'Caution'
                          : type === 'SUMMARY'
                          ? 'Summary'
                          : 'Assistant'}
                      </Typography>
                    }
                    secondary={
                      <>
                        <Typography variant="body1" color="textPrimary">
                          {content}
                        </Typography>
                        {item.timestamp && (
                          <Typography variant="caption" color="textSecondary">
                            {new Date(item.timestamp).toLocaleTimeString()}
                          </Typography>
                        )}
                      </>
                    }
                  />
                </ListItem>
                <Divider component="li" />
              </React.Fragment>
            );
          })}
          <div ref={listEndRef} />
        </List>
      </Paper>
    </Box>
  );
};

export default ConversationHistory;

// src/components/DynamicAudioRecorder.js

import React, { useState, useRef, useContext } from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';
import { Mic, Stop } from '@mui/icons-material';
import { styled } from '@mui/system';
import { sendAudioMessage } from '../api'; // Ensure correct import
import { SessionContext } from '../contexts/SessionContext';
import PopupDialog from './PopupDialog';

const PulsatingCircle = styled('div')(({ theme, isRecording }) => ({
  width: isRecording ? 120 : 100, // Increased size for better visibility
  height: isRecording ? 120 : 100,
  borderRadius: '50%',
  backgroundColor: isRecording ? theme.palette.error.main : theme.palette.primary.main,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  cursor: 'pointer',
  transition: 'all 0.3s ease-in-out',
  animation: isRecording ? 'pulse 1s infinite' : 'none',
  boxShadow: isRecording
    ? `0 0 0 15px rgba(255, 0, 0, 0.2)`
    : `0 0 0 10px rgba(25, 118, 210, 0.2)`,

  '@keyframes pulse': {
    '0%': {
      transform: 'scale(1)',
      opacity: 1,
    },
    '50%': {
      transform: 'scale(1.1)',
      opacity: 0.7,
    },
    '100%': {
      transform: 'scale(1)',
      opacity: 1,
    },
  },
}));

const DynamicAudioRecorder = ({ onResponse }) => {
  const { sessionId } = useContext(SessionContext);
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const [popupOpen, setPopupOpen] = useState(false);
  const [popupTitle, setPopupTitle] = useState('');
  const [popupMessage, setPopupMessage] = useState('');

  // Start Recording Function
  const startRecording = async () => {
    if (!sessionId) {
      triggerPopup('Error', 'Please set your objective first.');
      return;
    }

    if (navigator.mediaDevices) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorderRef.current = new MediaRecorder(stream);
        mediaRecorderRef.current.start();
        setIsRecording(true);

        mediaRecorderRef.current.ondataavailable = (event) => {
          audioChunksRef.current.push(event.data);
        };

        mediaRecorderRef.current.onstop = async () => {
          setIsProcessing(true);
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
          audioChunksRef.current = [];
          const audioFile = new File([audioBlob], 'recording.wav', { type: 'audio/wav' });

          console.log('Captured Audio File:', audioFile); // Log the audio file

          try {
            const response = await sendAudioMessage(sessionId, audioFile);
            onResponse(response); // Pass JSON response
          } catch (error) {
            console.error('Error processing audio:', error);
            triggerPopup('Processing Error', 'Failed to process audio. Please try again.');
          } finally {
            setIsProcessing(false);
          }
        };
      } catch (error) {
        console.error('Error accessing microphone:', error);
        triggerPopup('Microphone Access Denied', 'Please allow microphone access to record audio.');
      }
    } else {
      triggerPopup('Unsupported Feature', 'Media Devices API not supported in this browser.');
    }
  };

  // Stop Recording Function
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  // Trigger Popup Dialog
  const triggerPopup = (title, message) => {
    setPopupTitle(title);
    setPopupMessage(message);
    setPopupOpen(true);
  };

  // Handle Popup Close
  const handlePopupClose = () => {
    setPopupOpen(false);
  };

  return (
    <Box sx={{ textAlign: 'center', mt: 4 }}>
      <Typography variant="h6" gutterBottom>
        Record Your Audio
      </Typography>

      {/* Pulsating Circle Recorder */}
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <PulsatingCircle isRecording={isRecording} onClick={isRecording ? stopRecording : startRecording}>
          {isProcessing ? (
            <CircularProgress color="inherit" />
          ) : isRecording ? (
            <Stop
              style={{
                color: 'white',
                fontSize: '2rem',
              }}
            />
          ) : (
            <Mic
              style={{
                color: 'white',
                fontSize: '2rem',
              }}
            />
          )}
        </PulsatingCircle>
      </Box>

      {/* Popup Dialog for Errors or Warnings */}
      <PopupDialog
        open={popupOpen}
        onClose={handlePopupClose}
        title={popupTitle}
        message={popupMessage}
      />
    </Box>
  );
};

export default DynamicAudioRecorder;

// src/components/NavigationBar.js

import React, { useContext } from 'react';
import { AppBar, Toolbar, Typography, Button, IconButton } from '@mui/material';
import TranslateIcon from '@mui/icons-material/Translate';
import HistoryIcon from '@mui/icons-material/History';
import HomeIcon from '@mui/icons-material/Home';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { SessionContext } from '../contexts/SessionContext';

const NavigationBar = () => {
  const { sessionId, setSessionId } = useContext(SessionContext);
  const navigate = useNavigate();

  const handleResetSession = () => {
    setSessionId(null);
    navigate('/');
  };

  return (
    <AppBar position="static">
      <Toolbar>
        <HomeIcon sx={{ mr: 2 }} />
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Translation App
        </Typography>
        <Button
          color="inherit"
          startIcon={<HomeIcon />}
          component={RouterLink}
          to="/"
        >
          Home
        </Button>
        {sessionId && (
          <>
            <Button
              color="inherit"
              startIcon={<TranslateIcon />}
              component={RouterLink}
              to="/translate"
            >
              Translate
            </Button>
            <Button
              color="inherit"
              startIcon={<HistoryIcon />}
              component={RouterLink}
              to="/history"
            >
              History
            </Button>
            <Button
              color="inherit"
              onClick={handleResetSession}
              sx={{ ml: 2 }}
            >
              Reset Session
            </Button>
          </>
        )}
      </Toolbar>
    </AppBar>
  );
};

export default NavigationBar;

// src/components/ObjectiveForm.js

import React, { useState, useContext } from 'react';
import { setObjective } from '../api';
import { Button, TextField, Select, MenuItem, Typography, Box, FormControl, InputLabel } from '@mui/material';
import { SessionContext } from '../contexts/SessionContext';

const languages = [
  { code: 'en', name: 'English' },
  { code: 'es', name: 'Spanish' },
  { code: 'fr', name: 'French' },
  { code: 'zh', name: 'Chinese' }, // Updated code for Chinese
  // Add more languages as needed
];

const countries = [
  { code: 'US', name: 'United States' },
  { code: 'CN', name: 'China' },
  { code: 'ES', name: 'Spain' },
  { code: 'FR', name: 'France' },
  // Add more countries as needed
];

const ObjectiveForm = ({ onObjectiveSet }) => {
  const { setSessionId, setUserLanguage, setTargetLanguage, setCountry } = useContext(SessionContext);
  const [objective, setObjectiveText] = useState('');
  const [targetLanguage, setTargetLang] = useState('en'); // Default to English
  const [userLanguage, setUserLang] = useState('en'); // Default to English
  const [country, setCountryState] = useState('US'); // Default to United States

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const data = await setObjective(objective, targetLanguage, userLanguage, country);
      setSessionId(data.session_id);
      setUserLanguage(userLanguage);
      setTargetLanguage(targetLanguage);
      setCountry(country);
      onObjectiveSet(data.session_id);
    } catch (error) {
      console.error('Error setting objective:', error);
      alert('Failed to set objective.');
    }
  };

  return (
    <Box sx={{ p: 4, border: '1px solid #ccc', borderRadius: 2, textAlign: 'center' }}>
      <Typography variant="h5" gutterBottom>
        Set Your Objective
      </Typography>
      <form onSubmit={handleSubmit}>
        <TextField
          label="Objective"
          variant="outlined"
          fullWidth
          value={objective}
          onChange={(e) => setObjectiveText(e.target.value)}
          required
          sx={{ mb: 2 }}
        />

        {/* User Language Selection */}
        <FormControl fullWidth variant="outlined" sx={{ mb: 2 }}>
          <InputLabel id="user-language-label">Your Language</InputLabel>
          <Select
            labelId="user-language-label"
            value={userLanguage}
            onChange={(e) => setUserLang(e.target.value)}
            label="Your Language"
          >
            {languages.map((language) => (
              <MenuItem key={language.code} value={language.code}>
                {language.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        {/* Target Language Selection */}
        <FormControl fullWidth variant="outlined" sx={{ mb: 2 }}>
          <InputLabel id="target-language-label">Target Language</InputLabel>
          <Select
            labelId="target-language-label"
            value={targetLanguage}
            onChange={(e) => setTargetLang(e.target.value)}
            label="Target Language"
          >
            {languages.map((language) => (
              <MenuItem key={language.code} value={language.code}>
                {language.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        {/* Country Selection */}
        <FormControl fullWidth variant="outlined" sx={{ mb: 2 }}>
          <InputLabel id="country-label">Country/Region</InputLabel>
          <Select
            labelId="country-label"
            value={country}
            onChange={(e) => setCountryState(e.target.value)}
            label="Country/Region"
          >
            {countries.map((country) => (
              <MenuItem key={country.code} value={country.code}>
                {country.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <Button type="submit" variant="contained" color="primary" fullWidth>
          Start Session
        </Button>
      </form>
    </Box>
  );
};

export default ObjectiveForm;

// src/components/PopupDialog.js
import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
} from '@mui/material';

const PopupDialog = ({ open, onClose, title, message }) => {
  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>{title}</DialogTitle>
      <DialogContent>
        <Typography>{message}</Typography>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} color="primary">
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default PopupDialog;

import React, { useEffect, useState } from 'react';
import { Box, Typography } from '@mui/material';
import { getSummary } from '../api';

const Summary = ({ sessionId }) => {
  const [summary, setSummary] = useState('');

  useEffect(() => {
    const fetchSummary = async () => {
      // Existing fetch logic
    };

    fetchSummary();
  }, [sessionId]);

  if (!summary) return null;

  return (
    <Box sx={{ p: 2, border: '1px solid #ccc', borderRadius: 2, mb: 2 }}>
      <Typography variant="h5">Conversation Summary</Typography>
      <Typography>{summary}</Typography>
    </Box>
  );
};

export default Summary;

// src/components/TextToSpeech.js

import React, { useEffect } from 'react';

export const TextToSpeech = ({ text, language }) => {
  useEffect(() => {
    if (text) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = language || 'en-US'; // Default to English if no language provided
      window.speechSynthesis.speak(utterance);
    }
  }, [text, language]);

  return null; // This component does not render anything
};

// src/contexts/SessionContext.js

import React, { createContext, useState } from 'react';

export const SessionContext = createContext();

export const SessionProvider = ({ children }) => {
  const [sessionId, setSessionId] = useState(null);
  const [userLanguage, setUserLanguage] = useState('English');
  const [targetLanguage, setTargetLanguage] = useState('English');
  const [country, setCountry] = useState('US');

  return (
    <SessionContext.Provider value={{
      sessionId,
      setSessionId,
      userLanguage,
      setUserLanguage,
      targetLanguage,
      setTargetLanguage,
      country,
      setCountry,
    }}>
      {children}
    </SessionContext.Provider>
  );
};

// src/pages/HistoryPage.js
import React, { useEffect, useState, useContext } from 'react';
import {
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
} from '@mui/material';
import { Delete, Replay } from '@mui/icons-material';
import { SessionContext } from '../contexts/SessionContext';
import axios from 'axios';

const HistoryPage = () => {
  const { sessionId } = useContext(SessionContext);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    if (!sessionId) {
      alert('Please set your objective first.');
      window.location.href = '/';
      return;
    }

    const fetchHistory = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/history/${sessionId}`);
        setHistory(response.data.history);
      } catch (error) {
        console.error('Error fetching history:', error);
        alert('Failed to fetch history.');
      }
    };

    fetchHistory();
  }, [sessionId]);

  const handleDelete = async (id) => {
    try {
      await axios.delete(`http://localhost:8000/history/${sessionId}/${id}`);
      setHistory((prev) => prev.filter((item) => item.id !== id));
    } catch (error) {
      console.error('Error deleting history item:', error);
      alert('Failed to delete history item.');
    }
  };

  const handleReuse = (item) => {
    // Logic to reuse past translation
    // For example, redirect to TranslationPage with pre-filled text
    // This might require using React Router's navigate function
    // or lifting the state up to App.js
    alert('Reuse feature not implemented yet.');
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Translation History
      </Typography>
      {history.length === 0 ? (
        <Typography>No past translations found.</Typography>
      ) : (
        <TableContainer component={Paper}>
          <Table aria-label="translation history">
            <TableHead>
              <TableRow>
                <TableCell>Timestamp</TableCell>
                <TableCell>Source Language</TableCell>
                <TableCell>Target Language</TableCell>
                <TableCell>Original Text</TableCell>
                <TableCell>Translated Text</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {history.map((item) => (
                <TableRow key={item.id}>
                  <TableCell>{item.timestamp}</TableCell>
                  <TableCell>{item.source_language}</TableCell>
                  <TableCell>{item.target_language}</TableCell>
                  <TableCell>{item.original_text}</TableCell>
                  <TableCell>{item.translated_text}</TableCell>
                  <TableCell>
                    <IconButton
                      color="primary"
                      onClick={() => handleReuse(item)}
                    >
                      <Replay />
                    </IconButton>
                    <IconButton
                      color="secondary"
                      onClick={() => handleDelete(item.id)}
                    >
                      <Delete />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
};

export default HistoryPage;

// src/pages/HomePage.js

import React, { useContext } from 'react';
import { Typography, Box } from '@mui/material';
import ObjectiveForm from '../components/ObjectiveForm';
import { SessionContext } from '../contexts/SessionContext';
import { useNavigate } from 'react-router-dom';

const HomePage = () => {
  const { setSessionId } = useContext(SessionContext);
  const navigate = useNavigate(); // Initialize useNavigate

  const handleObjectiveSet = (session_id) => {
    setSessionId(session_id);
    alert('Objective set successfully! Redirecting to Translation Page...');
    navigate('/translate'); // Redirect to TranslationPage
  };

  return (
    <Box textAlign="center">
      <Typography variant="h3" gutterBottom>
        Welcome to the Translation App
      </Typography>
      <Typography variant="h6" gutterBottom>
        Seamlessly translate text and speech between multiple languages using our AI-powered tool.
      </Typography>
      <ObjectiveForm onObjectiveSet={handleObjectiveSet} />
    </Box>
  );
};

export default HomePage;

// src/pages/TranslationPage.js

import React, { useState, useContext, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Grid, 
  CircularProgress, 
  TextField, 
  Button 
} from '@mui/material';
import { sendAudioMessage, sendTextMessage } from '../api'; // Ensure correct imports
import DynamicAudioRecorder from '../components/DynamicAudioRecorder';
import { SessionContext } from '../contexts/SessionContext';
import PopupDialog from '../components/PopupDialog';
import ConversationHistory from '../components/ConversationHistory';
import { TextToSpeech } from '../components/TextToSpeech'; // Ensure this import

// Utility function to map language codes
const languageCodeMap = {
  'en': 'en-US',
  'es': 'es-ES',
  'fr': 'fr-FR',
  'zh': 'zh-CN',
  // Add more mappings as needed
};

const TranslationPage = () => {
  const { 
    sessionId, 
    objective, 
    userLanguage, 
    targetLanguage 
  } = useContext(SessionContext);

  const [translatedText, setTranslatedText] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [history, setHistory] = useState([]);
  const [cautionOpen, setCautionOpen] = useState(false);
  const [summaryOpen, setSummaryOpen] = useState(false);
  const [cautionMessage, setCautionMessage] = useState('');
  const [summaryMessage, setSummaryMessage] = useState('');
  const [assistantSpeaking, setAssistantSpeaking] = useState(false);
  const [manualText, setManualText] = useState(''); // State for manual text input
  const [isInitialMessageSent, setIsInitialMessageSent] = useState(false); // Flag to prevent multiple initial sends

  useEffect(() => {
    if (!sessionId) {
      alert('Please set your objective first.');
      window.location.href = '/';
    } else if (!isInitialMessageSent) {
      // Send the initial objective as a message to initialize the chat
      const sendInitialObjective = async () => {
        setIsProcessing(true);
        try {
          console.log('Sending initial objective as message:', objective);
          const response = await sendTextMessage(sessionId, objective);
          console.log('Received initial sendTextMessage response:', response);
          const { assistant_response, history: updatedHistory } = response;

          // Update conversation history
          setHistory(updatedHistory);

          // Handle assistant response
          handleAssistantResponse(assistant_response, response.summary);
          
          // Set the flag to true to prevent re-sending
          setIsInitialMessageSent(true);
        } catch (error) {
          console.error('Error sending initial objective:', error.response ? error.response.data : error.message);
          alert('Failed to initialize chat with objective.');
        } finally {
          setIsProcessing(false);
        }
      };

      sendInitialObjective();
    }
  }, [sessionId, isInitialMessageSent, objective]);

  // Handle responses from assistant (both from audio and text messages)
  const handleAssistantResponse = (assistant_response, summary) => {
    setIsProcessing(true);
    try {
      // Determine message type and act accordingly
      if (assistant_response.startsWith('[USER]')) {
        const message = assistant_response.replace('[USER]', '').trim();
        setCautionMessage(message);
        setCautionOpen(true);
        setAssistantSpeaking(true);
        TextToSpeech(message, languageCodeMap[userLanguage] || 'en-US'); // Use user language for caution messages
      } else if (assistant_response.startsWith('[CAUTION]')) {
        const message = assistant_response.replace('[CAUTION]', '').trim();
        setCautionMessage(message);
        setCautionOpen(true);
        setAssistantSpeaking(true);
        TextToSpeech(message, languageCodeMap[targetLanguage] || 'en-US'); // Use target language
      } else if (assistant_response.startsWith('[SUMMARY]')) {
        const message = assistant_response.replace('[SUMMARY]', '').trim();
        setSummaryMessage(message);
        setSummaryOpen(true);
        TextToSpeech(message, languageCodeMap[targetLanguage] || 'en-US'); // Use target language
      } else {
        // For any other assistant responses
        TextToSpeech(assistant_response, languageCodeMap[targetLanguage] || 'en-US'); // Use target language for assistant messages
      }

      // Handle summary if present
      if (summary) {
        setSummaryMessage(summary);
        setSummaryOpen(true);
        TextToSpeech(summary, languageCodeMap[targetLanguage] || 'en-US'); // Use target language
      }

      // Optionally, set translated text or handle accordingly
      setTranslatedText(assistant_response);
    } catch (error) {
      console.error('Error handling assistant response:', error);
      alert('Failed to process assistant response.');
    } finally {
      setIsProcessing(false);
    }
  };

  // Handle responses from audio recordings
  const handleAudioResponse = (response) => {
    console.log('Handling audio response:', response);
    const { assistant_response, summary } = response;
    handleAssistantResponse(assistant_response, summary);
  };

  // Handle manual text submissions
  const handleManualTextSubmit = async (e) => {
    e.preventDefault();
    if (!manualText.trim()) return;

    console.log('Submitting manual text:', manualText);
    setIsProcessing(true);
    try {
      // Send manual text to backend using sendTextMessage
      const response = await sendTextMessage(sessionId, manualText);
      console.log('Received sendTextMessage response:', response);
      const { assistant_response, history: updatedHistory } = response;

      // Update conversation history
      setHistory(updatedHistory);

      // Extract assistant response from the latest message
      const latestAssistantMessage = updatedHistory.find(
        (msg) => msg.type === 'ASSISTANT' && msg.content
      );
      if (latestAssistantMessage) {
        const { content } = latestAssistantMessage;
        handleAssistantResponse(content, response.summary);
      }

      setManualText('');
    } catch (error) {
      console.error('Error submitting manual text:', error.response ? error.response.data : error.message);
      alert('Failed to submit text.');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <Box sx={{ p: 4 }}>
      <Typography variant="h4" gutterBottom align="center">
        Translation
      </Typography>
      <Grid container spacing={4} justifyContent="center">
        {/* Dynamic Audio Recorder */}
        <Grid item xs={12} textAlign="center">
          <DynamicAudioRecorder onResponse={handleAudioResponse} />
        </Grid>

        {/* Conversation History */}
        <Grid item xs={12} md={10}>
          <ConversationHistory history={history} />
        </Grid>

        {/* Informational Text for Non-Verbal Users */}
        <Grid item xs={12} textAlign="center">
          <Typography variant="body1" color="textSecondary">
            If you're unable to speak, please use the text input below to submit your message.
          </Typography>
        </Grid>

        {/* Manual Text Input */}
        <Grid item xs={12} md={6} sx={{ margin: '0 auto' }}>
          <Box component="form" onSubmit={handleManualTextSubmit}>
            <TextField
              label="Enter your message"
              variant="outlined"
              fullWidth
              value={manualText}
              onChange={(e) => setManualText(e.target.value)}
              required
              sx={{ mb: 2 }}
              multiline
              rows={3}
              placeholder="Type your message here..."
              InputProps={{
                style: {
                  borderRadius: '50px', // Make it rounder (oval shape)
                },
              }}
            />
            <Button 
              type="submit" 
              variant="contained" 
              color="primary" 
              fullWidth 
              disabled={isProcessing}
            >
              {isProcessing ? <CircularProgress size={24} /> : 'Submit'}
            </Button>
          </Box>
        </Grid>
      </Grid>

      {/* Caution Dialog */}
      <PopupDialog
        open={cautionOpen}
        onClose={() => setCautionOpen(false)}
        title="Assistant Caution Notification"
        message={cautionMessage}
      />

      {/* Summary Dialog */}
      <PopupDialog
        open={summaryOpen}
        onClose={() => setSummaryOpen(false)}
        title="Conversation Summary"
        message={summaryMessage}
      />

      {/* Assistant Speaking Pop-up */}
      <PopupDialog
        open={assistantSpeaking}
        onClose={() => setAssistantSpeaking(false)}
        title="Assistant is Speaking"
        message="The assistant is currently responding to your request."
      />

      {/* Text-to-Speech Component */}
      {/* This component does not render anything visible */}
      {/* It automatically speaks the text when the 'translatedText' state changes */}
      <TextToSpeech text={translatedText} language={languageCodeMap[targetLanguage] || 'en-US'} />
    </Box>
  );
};

export default TranslationPage;

// src/utils/languageCodes.js

export const languageCodeMap = {
    'English': 'en-US',
    'Spanish': 'es-ES',
    'French': 'fr-FR',
    'Chinese': 'zh-CN',
    // Add more languages as needed
  };
  
  // src/api.js

import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000'; // Replace with your actual backend URL

/**
 * Sets the objective and initializes a session.
 * @param {string} objective - The user's objective.
 * @param {string} targetLanguage - The target language.
 * @param {string} userLanguage - The user's language.
 * @param {string} country - The user's country/region.
 * @returns {Promise<Object>} - The response containing session_id and message.
 */
export const setObjective = async (objective, targetLanguage, userLanguage, country) => {
  console.log('Setting objective with:', { objective, targetLanguage, userLanguage, country });
  try {
    const response = await axios.post(`${API_BASE_URL}/set_objective`, {
      objective,
      target_language: targetLanguage,
      user_language: userLanguage,
      country: country,
    });
    console.log('setObjective response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error in setObjective:', error);
    throw error;
  }
};

/**
 * Sends a text message for processing.
 * @param {string} sessionId - The session ID.
 * @param {string} message - The user's message.
 * @returns {Promise<Object>} - The backend JSON response.
 */
export const sendTextMessage = async (sessionId, message) => {
  try {
    console.log(`Sending message to session ${sessionId}:`, message); // Debug log
    const response = await axios.post(
      `${API_BASE_URL}/send_message/${sessionId}`,
      { message }, // Ensure this matches the MessageRequest model
      {
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );
    console.log('sendTextMessage response:', response.data); // Debug log
    return response.data; // Expected response: { assistant_response, history }
  } catch (error) {
    console.error('Error in sendTextMessage:', error.response ? error.response.data : error.message);
    throw error;
  }
};

/**
 * Sends an audio file for processing.
 * @param {string} sessionId - The session ID.
 * @param {File} audioFile - The audio file to process.
 * @returns {Promise<Object>} - The backend JSON response containing user_text and assistant_response.
 */
export const sendAudioMessage = async (sessionId, audioFile) => {
  console.log('Sending audio message:', { sessionId, audioFile });
  const formData = new FormData();
  formData.append('file', audioFile);

  try {
    const response = await axios.post(`${API_BASE_URL}/process_audio/${sessionId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    console.log('sendAudioMessage response:', response.data);
    return response.data; // Expected response: { user_text, assistant_response, summary (optional) }
  } catch (error) {
    console.error('Error in sendAudioMessage:', error);
    throw error;
  }
};

/**
 * Retrieves the summary of the conversation.
 * @param {string} sessionId - The session ID.
 * @returns {Promise<Object>} - The summary response.
 */
export const getSummary = async (sessionId) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/summary/${sessionId}`);
    return response.data; // Expected response: { summary: "..." }
  } catch (error) {
    console.error('Error in getSummary:', error);
    throw error;
  }
};

/**
 * Synthesizes text to speech (if applicable).
 * @param {string} text - The text to synthesize.
 * @returns {Promise<Blob>} - The synthesized audio Blob.
 */
export const synthesizeText = async (text) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/synthesize_text`, { text }, {
      responseType: 'blob', // Assuming backend returns audio Blob
    });
    return response.data; // Binary audio data
  } catch (error) {
    console.error('Error in synthesizeText:', error);
    throw error;
  }
};

// Export all functions as named exports
export default {
  setObjective,
  sendTextMessage,
  sendAudioMessage,
  getSummary,
  synthesizeText,
};

// src/App.js

import React, { useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import NavigationBar from './components/NavigationBar';
import HomePage from './pages/HomePage';
import TranslationPage from './pages/TranslationPage';
import HistoryPage from './pages/HistoryPage';
import { Container } from '@mui/material';
import { SessionProvider, SessionContext } from './contexts/SessionContext';

const ProtectedRoute = ({ children }) => {
  const { sessionId } = useContext(SessionContext);
  return sessionId ? children : <Navigate to="/" />;
};

const App = () => {
  return (
    <SessionProvider>
      <Router>
        <NavigationBar />
        <Container sx={{ mt: 4 }}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route
              path="/translate"
              element={
                <ProtectedRoute>
                  <TranslationPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/history"
              element={
                <ProtectedRoute>
                  <HistoryPage />
                </ProtectedRoute>
              }
            />
            {/* Add more routes as needed */}
          </Routes>
        </Container>
      </Router>
    </SessionProvider>
  );
};

export default App;

// src/utils/languageCodes.js

export const languageCodeMap = {
    'English': 'en-US',
    'Spanish': 'es-ES',
    'French': 'fr-FR',
    'Chinese': 'zh-CN',
    // Add more languages as needed
  };
  
// src/api.js

import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000'; // Replace with your actual backend URL

/**
 * Sets the objective and initializes a session.
 * @param {string} objective - The user's objective.
 * @param {string} targetLanguage - The target language.
 * @param {string} userLanguage - The user's language.
 * @param {string} country - The user's country/region.
 * @returns {Promise<Object>} - The response containing session_id and message.
 */
export const setObjective = async (objective, targetLanguage, userLanguage, country) => {
  console.log('Setting objective with:', { objective, targetLanguage, userLanguage, country });
  try {
    const response = await axios.post(`${API_BASE_URL}/set_objective`, {
      objective,
      target_language: targetLanguage,
      user_language: userLanguage,
      country: country,
    });
    console.log('setObjective response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error in setObjective:', error);
    throw error;
  }
};

/**
 * Sends a text message for processing.
 * @param {string} sessionId - The session ID.
 * @param {string} message - The user's message.
 * @returns {Promise<Object>} - The backend JSON response.
 */
export const sendTextMessage = async (sessionId, message) => {
  try {
    console.log(`Sending message to session ${sessionId}:`, message); // Debug log
    const response = await axios.post(
      `${API_BASE_URL}/send_message/${sessionId}`,
      { message }, // Ensure this matches the MessageRequest model
      {
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );
    console.log('sendTextMessage response:', response.data); // Debug log
    return response.data; // Expected response: { assistant_response, history }
  } catch (error) {
    console.error('Error in sendTextMessage:', error.response ? error.response.data : error.message);
    throw error;
  }
};

/**
 * Sends an audio file for processing.
 * @param {string} sessionId - The session ID.
 * @param {File} audioFile - The audio file to process.
 * @returns {Promise<Object>} - The backend JSON response containing user_text and assistant_response.
 */
export const sendAudioMessage = async (sessionId, audioFile) => {
  console.log('Sending audio message:', { sessionId, audioFile });
  const formData = new FormData();
  formData.append('file', audioFile);

  try {
    const response = await axios.post(`${API_BASE_URL}/process_audio/${sessionId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    console.log('sendAudioMessage response:', response.data);
    return response.data; // Expected response: { user_text, assistant_response, summary (optional) }
  } catch (error) {
    console.error('Error in sendAudioMessage:', error);
    throw error;
  }
};

/**
 * Retrieves the summary of the conversation.
 * @param {string} sessionId - The session ID.
 * @returns {Promise<Object>} - The summary response.
 */
export const getSummary = async (sessionId) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/summary/${sessionId}`);
    return response.data; // Expected response: { summary: "..." }
  } catch (error) {
    console.error('Error in getSummary:', error);
    throw error;
  }
};

/**
 * Synthesizes text to speech (if applicable).
 * @param {string} text - The text to synthesize.
 * @returns {Promise<Blob>} - The synthesized audio Blob.
 */
export const synthesizeText = async (text) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/synthesize_text`, { text }, {
      responseType: 'blob', // Assuming backend returns audio Blob
    });
    return response.data; // Binary audio data
  } catch (error) {
    console.error('Error in synthesizeText:', error);
    throw error;
  }
};

// Export all functions as named exports
export default {
  setObjective,
  sendTextMessage,
  sendAudioMessage,
  getSummary,
  synthesizeText,
};

Here is the full frontend, I didnt include everything by the way, like the styles.css, app.css and etc, now the thing is that theres several problems
for some reason I cant:
1. it says it cant handle audio processes for some reason when I was done interacting after the mic
 
2. its not letting me post request the send message after setting the objective and post requesting the set_objective for some reason, but when I CURL this command it worked in the backend
so its defintely the front end problem

can you investigate and debug these?