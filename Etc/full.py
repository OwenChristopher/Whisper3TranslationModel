// src/components/AudioRecorder.js

import React, { useState, useRef } from 'react';
import { Button, Typography, Box, CircularProgress } from '@mui/material';
import { Mic, Stop } from '@mui/icons-material';
import { processAudio } from '../api'; 


const AudioRecorder = ({ sessionId, onResponse }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const startRecording = async () => {
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
        <CircularProgress />
      )}
    </Box>
  );
};

export default AudioRecorder;

// src/components/ChatInput.js

import React, { useState } from 'react';
import { Box, TextField, Button, CircularProgress } from '@mui/material';
import PropTypes from 'prop-types';
import { sendTextMessage } from '../api'; // Ensure correct import

const ChatInput = ({ sessionId, onResponse, isProcessing, onClose }) => {
  const [manualText, setManualText] = useState('');

  const handleManualTextSubmit = async (e) => {
    e.preventDefault();
    if (!manualText.trim()) return;

    try {
      // Send manual text to backend using sendTextMessage
      const response = await sendTextMessage(sessionId, manualText);
      const { assistant_response, history: updatedHistory, summary } = response;

      // Handle assistant response
      onResponse(assistant_response, summary, manualText);

      setManualText('');
    } catch (error) {
      console.error('Error submitting manual text:', error.response ? error.response.data : error.message);
      // Optionally, trigger a notification here
    }
  };

  return (
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
      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Button 
          type="submit" 
          variant="contained" 
          color="primary" 
          disabled={isProcessing}
          sx={{
            borderRadius: '50px', // Rounded button
            height: '56px', // Match TextField height
            minWidth: '100px',
          }}
        >
          {isProcessing ? <CircularProgress size={24} /> : 'Submit'}
        </Button>
        <Button 
          variant="text" 
          color="secondary" 
          onClick={onClose}
          sx={{
            borderRadius: '50px',
            minWidth: '100px',
          }}
        >
          Cancel
        </Button>
      </Box>
    </Box>
  );
};

ChatInput.propTypes = {
  sessionId: PropTypes.string.isRequired,
  onResponse: PropTypes.func.isRequired,
  isProcessing: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
};

export default ChatInput;

// src/components/ConversationHistory.js

import React, { useEffect, useRef, useState } from 'react';
import { Box, Typography, Paper, List, ListItem, ListItemText, Divider, Button, Collapse, IconButton } from '@mui/material';
import { ExpandLess, ExpandMore, Close } from '@mui/icons-material';

/**
 * ConversationHistory component displays the list of messages exchanged between the user and the assistant.
 * @param {Array} history - An array of message objects containing type, recipient, and content.
 * @param {Function} onClose - Function to handle closing the chat box.
 */
const ConversationHistory = React.memo(({ history, onClose }) => {
  const listEndRef = useRef(null);
  const [isVisible, setIsVisible] = useState(true); // State to manage visibility

  useEffect(() => {
    // Scroll to the bottom when a new message is added
    if (listEndRef.current && isVisible) {
      listEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [history, isVisible]);

  /**
   * Parses each message to ensure it has type, recipient, and content.
   * Provides default values if necessary to prevent runtime errors.
   * @param {Object} item - A message object from the history.
   * @param {number} index - The index of the message in the history array.
   * @returns {Object|null} - Parsed message with type, recipient, and content or null to skip rendering.
   */
  const parseMessage = (item, index) => {
    // **Skip rendering the first message regardless of its type**
    if (index === 0) {
      return null;
    }

    // Ensure that 'type' and 'recipient' exist; provide defaults if not
    const messageType = item.type ? item.type.toUpperCase() : 'ASSISTANT';
    const recipient = item.recipient ? item.recipient : (messageType === 'USER' ? 'User' : 'Assistant');
    const content = item.content ? item.content : '';

    return {
      type: messageType, // 'USER', 'TARGET', 'CAUTION', 'SUMMARY', 'SYSTEM', etc.
      recipient: recipient, // 'User', 'Target', 'Caution', 'Summary', 'Assistant', 'System'
      content: content,
    };
  };

  const toggleVisibility = () => {
    setIsVisible((prev) => !prev);
  };

  return (
    <Box sx={{ mt: 4 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h5" gutterBottom>
          Conversation Logs
        </Typography>
        <Box>
          <Button onClick={toggleVisibility} startIcon={isVisible ? <ExpandLess /> : <ExpandMore />} sx={{ mr: 1 }}>
            {isVisible ? 'Collapse' : 'Expand'}
          </Button>
          <IconButton onClick={onClose} color="secondary" aria-label="Close Chat Box">
            <Close />
          </IconButton>
        </Box>
      </Box>
      <Collapse in={isVisible}>
        <Paper elevation={3} sx={{ maxHeight: 400, overflowY: 'auto', padding: 2 }}>
          <List>
            {history.map((item, index) => {
              const parsedMessage = parseMessage(item, index);
              if (!parsedMessage) return null; // Skip rendering

              const { type, recipient, content } = parsedMessage;

              // Determine the color based on message type
              let color;
              switch (type) {
                case 'USER':
                  color = 'primary';
                  break;
                case 'TARGET':
                  color = 'secondary';
                  break;
                case 'CAUTION':
                case 'SUMMARY':
                  color = 'error';
                  break;
                case 'SYSTEM':
                  color = 'textSecondary';
                  break;
                default:
                  color = 'textPrimary';
                  break;
              }

              // Determine the display name based on recipient
              let displayName;
              switch (type) {
                case 'USER':
                  displayName = 'You';
                  break;
                case 'TARGET':
                  displayName = 'Target';
                  break;
                case 'CAUTION':
                  displayName = 'Caution';
                  break;
                case 'SUMMARY':
                  displayName = 'Summary';
                  break;
                case 'SYSTEM':
                  displayName = 'System';
                  break;
                default:
                  displayName = 'Assistant';
                  break;
              }

              return (
                <React.Fragment key={index}>
                  <ListItem alignItems="flex-start">
                    <ListItemText
                      primary={
                        <Typography
                          variant="subtitle2"
                          color={color}
                        >
                          {displayName}
                        </Typography>
                      }
                      secondary={
                        <Typography variant="body1" color="textPrimary">
                          {content}
                        </Typography>
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
      </Collapse>
    </Box>
  );
});

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
  width: isRecording ? 150 : 120, // Increased size for better visibility
  height: isRecording ? 150 : 120,
  borderRadius: '50%',
  backgroundColor: isRecording ? theme.palette.error.main : theme.palette.primary.main,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  cursor: 'pointer',
  transition: 'all 0.3s ease-in-out',
  animation: isRecording ? 'pulse 1s infinite' : 'none',
  boxShadow: isRecording
    ? `0 0 0 20px rgba(255, 0, 0, 0.2)`
    : `0 0 0 15px rgba(25, 118, 210, 0.2)`,

  '@keyframes pulse': {
    '0%': {
      transform: 'scale(1)',
      opacity: 1,
    },
    '50%': {
      transform: 'scale(1.2)',
      opacity: 0.7,
    },
    '100%': {
      transform: 'scale(1)',
      opacity: 1,
    },
  },

  // Responsive adjustments
  [theme.breakpoints.down('sm')]: {
    width: isRecording ? 100 : 80,
    height: isRecording ? 100 : 80,
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
          sx={{
            borderRadius: '50px',
            transition: 'background-color 0.3s, transform 0.3s',
            '&:hover': {
              backgroundColor: 'primary.dark',
              transform: 'scale(1.05)',
            },
          }}
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
              sx={{
                borderRadius: '50px',
                transition: 'background-color 0.3s, transform 0.3s',
                '&:hover': {
                  backgroundColor: 'primary.dark',
                  transform: 'scale(1.05)',
                },
                ml: 2,
              }}
            >
              Translate
            </Button>
            <Button
              color="inherit"
              startIcon={<HistoryIcon />}
              component={RouterLink}
              to="/history"
              sx={{
                borderRadius: '50px',
                transition: 'background-color 0.3s, transform 0.3s',
                '&:hover': {
                  backgroundColor: 'primary.dark',
                  transform: 'scale(1.05)',
                },
                ml: 2,
              }}
            >
              History
            </Button>
            <Button
              color="inherit"
              onClick={handleResetSession}
              sx={{ 
                ml: 2,
                borderRadius: '50px',
                transition: 'background-color 0.3s, transform 0.3s',
                '&:hover': {
                  backgroundColor: 'secondary.dark',
                  transform: 'scale(1.05)',
                },
              }}
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

// src/components/Notification.js

import React from 'react';
import { Snackbar, Alert } from '@mui/material';

const Notification = ({ open, onClose, severity, message }) => {
  return (
    <Snackbar
      open={open}
      autoHideDuration={6000}
      onClose={onClose}
      anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
    >
      <Alert onClose={onClose} severity={severity} sx={{ width: '100%' }}>
        {message}
      </Alert>
    </Snackbar>
  );
};

export default Notification;

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
      console.error('Error setting objective:', error.response ? error.response.data : error.message);
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
  Slide,
} from '@mui/material';

const Transition = React.forwardRef(function Transition(props, ref) {
  return <Slide direction="up" ref={ref} {...props} />;
});

const PopupDialog = ({ open, onClose, title, message }) => {
  return (
    <Dialog
      open={open}
      onClose={onClose}
      TransitionComponent={Transition}
      keepMounted
      // Reduce transition duration for faster appearance
      transitionDuration={{ enter: 300, exit: 200 }}
      aria-describedby="alert-dialog-description"
    >
      <DialogTitle>{title}</DialogTitle>
      <DialogContent>
        <Typography>{message}</Typography>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} color="primary" autoFocus>
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

import React, { useEffect, useState } from 'react';

export const TextToSpeech = ({ text, language }) => {
  const [voices, setVoices] = useState([]);

  useEffect(() => {
    // Function to load voices
    const loadVoices = () => {
      const availableVoices = speechSynthesis.getVoices();
      setVoices(availableVoices);
    };

    // Load voices when they are loaded
    if (speechSynthesis.onvoiceschanged !== undefined) {
      speechSynthesis.onvoiceschanged = loadVoices;
    }

    // Initial load
    loadVoices();
  }, []);

  useEffect(() => {
    if (text) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'zh-CN';
    
      // Manually select the Chinese voice by name
      const selectedVoice = voices.find(voice => voice.name === 'Google 普通话（中国大陆）');
    
      if (selectedVoice) {
        console.log(`Manually selected Voice: ${selectedVoice.name}, Lang: ${selectedVoice.lang}`);
        utterance.voice = selectedVoice;
      } else {
        console.warn(`Chinese voice not found. Using default voice.`);
      }
    
      window.speechSynthesis.speak(utterance);
    }
  }, [text, language, voices]);

  return null; // This component does not render anything
};

// src/utils/languageCodes.js

export const languageCodeMap = {
  'English': 'en-US',
  'Spanish': 'es-ES',
  'French': 'fr-FR',
  'Chinese': 'zh-CN',
  // Add more languages as needed
};

// src/contexts/SessionContext.js

import React, { createContext, useState } from 'react';

export const SessionContext = createContext();

// export const SessionProvider = ({ children }) => {
//   const [sessionId, setSessionId] = useState(null);
//   const [userLanguage, setUserLanguage] = useState('en'); // Initialized with language code
//   const [targetLanguage, setTargetLanguage] = useState('en'); // Initialized with language code
//   const [country, setCountry] = useState('US'); // Country code as per your implementation

export const SessionProvider = ({ children }) => {
  const [sessionId, setSessionId] = useState(null);
  const [userLanguage, setUserLanguage] = useState('zh'); // Initialized with language code
  const [targetLanguage, setTargetLanguage] = useState('zh'); // Initialized with language code
  const [country, setCountry] = useState('CN'); // Country code as per your implementation

  return (
    <SessionContext.Provider
      value={{
        sessionId,
        setSessionId,
        userLanguage,
        setUserLanguage,
        targetLanguage,
        setTargetLanguage,
        country,
        setCountry,
      }}
    >
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
    <Box 
      textAlign="center"
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        borderRadius: '16px', // Changed from '50%' to '16px' for rounded corners
        backgroundColor: '#e0f7fa',
        padding: 4,
        boxShadow: 3,
        transition: 'transform 0.3s',
        '&:hover': {
          transform: 'scale(1.05)',
        },
        maxWidth: '800px', // Optional: Set a max width for better layout
        margin: '0 auto', // Center the box horizontally
      }}
    >
      <Typography variant="h3" gutterBottom>
        Welcome to XMTranslator!
      </Typography>
      <Typography variant="h6" gutterBottom>
        Seamlessly translate text and speech between multiple languages using our AI-powered tool.
      </Typography>
      <ObjectiveForm onObjectiveSet={handleObjectiveSet} />
    </Box>
  );
};

export default HomePage;

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
    <Box 
      textAlign="center"
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        borderRadius: '16px', // Changed from '50%' to '16px' for rounded corners
        backgroundColor: '#e0f7fa',
        padding: 4,
        boxShadow: 3,
        transition: 'transform 0.3s',
        '&:hover': {
          transform: 'scale(1.05)',
        },
        maxWidth: '800px', // Optional: Set a max width for better layout
        margin: '0 auto', // Center the box horizontally
      }}
    >
      <Typography variant="h3" gutterBottom>
        Welcome to XMTranslator!
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
  Button 
} from '@mui/material';
import { sendAudioMessage, sendTextMessage } from '../api'; // Ensure correct imports
import DynamicAudioRecorder from '../components/DynamicAudioRecorder';
import { SessionContext } from '../contexts/SessionContext';
import Notification from '../components/Notification'; // Correct import
import PopupDialog from '../components/PopupDialog'; // Correct import
import ConversationHistory from '../components/ConversationHistory';
import ChatInput from '../components/ChatInput'; // Separate ChatInput component
import { TextToSpeech } from '../components/TextToSpeech';
import { languageCodeMap } from '../utils/languageCodes'; // Ensure correct import

const TranslationPage = () => {
  const { 
    sessionId, 
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
  const [isInitialMessageSent, setIsInitialMessageSent] = useState(false); // Flag to prevent multiple initial sends

  // State for notifications
  const [notification, setNotification] = useState({
    open: false,
    severity: 'info', // 'error', 'warning', 'info', 'success'
    message: '',
  });

  // State to control chat input visibility
  const [showChatInput, setShowChatInput] = useState(false);

  // Function to trigger notification
  const triggerNotification = (severity, message) => {
    setNotification({ open: true, severity, message });
  };

  // Handle notification close
  const handleNotificationClose = () => {
    setNotification({ ...notification, open: false });
  };

  useEffect(() => {
    if (!sessionId) {
      alert('Please set your objective first.');
      window.location.href = '/';
    } else if (!isInitialMessageSent) {
      // Send the initial objective as a message to initialize the chat
      const sendInitialObjective = async () => {
        setIsProcessing(true);
        try {
          // Assuming the initial objective is already set in the backend session
          // If not, you might need to send it here
          const response = await sendTextMessage(sessionId, ''); // Sending an empty message or adjust as needed
          const { assistant_response, history: updatedHistory, summary } = response;

          // Map backend history to frontend structure
          const mappedHistory = updatedHistory.map(item => mapBackendMessageToFrontend(item));

          setHistory(mappedHistory);

          // Handle assistant response
          handleAssistantResponse(assistant_response, summary);
          
          // Set the flag to true to prevent re-sending
          setIsInitialMessageSent(true);
        } catch (error) {
          console.error('Error sending initial objective:', error.response ? error.response.data : error.message);
          triggerNotification('error', 'Failed to initialize chat with objective.');
        } finally {
          setIsProcessing(false);
        }
      };

      sendInitialObjective();
    }
  }, [sessionId, isInitialMessageSent]);

  // Function to map backend message to frontend structure
  const mapBackendMessageToFrontend = (item) => {
    if (item.role === 'assistant') {
      // Parse content to extract messageType and message
      const { messageType, message } = parseAssistantResponse(item.content);
      let recipient;
      switch (messageType) {
        case 'USER':
          recipient = 'User';
          break;
        case 'TARGET':
          recipient = 'Target';
          break;
        case 'CAUTION':
          recipient = 'Caution';
          break;
        case 'SUMMARY':
          recipient = 'Summary';
          break;
        default:
          recipient = 'Assistant';
          break;
      }
      return {
        type: messageType,
        recipient: recipient,
        content: message
      };
    } else if (item.role === 'user') {
      return {
        type: 'USER',
        recipient: 'Assistant',
        content: item.content
      };
    } else if (item.role === 'system') {
      return {
        type: 'SYSTEM',
        recipient: 'System',
        content: item.content
      };
    } else {
      // Default mapping for any other roles
      return {
        type: 'ASSISTANT',
        recipient: 'Assistant',
        content: item.content
      };
    }
  };

  // Function to parse the assistant's response
  const parseAssistantResponse = (assistantResponse) => {
    const prefixPattern = /^\[(USER|TARGET|CAUTION|SUMMARY)\]\s+/;
    const match = assistantResponse.match(prefixPattern);
    if (match) {
      const messageType = match[1].toUpperCase(); // USER, TARGET, CAUTION, SUMMARY
      const message = assistantResponse.replace(prefixPattern, '').trim();
      return { messageType, message };
    } else {
      // If no prefix found, treat it as a regular assistant message
      return { messageType: 'ASSISTANT', message: assistantResponse };
    }
  };

  // Handle assistant response
  const handleAssistantResponse = (assistant_response, summary, userText = null) => {
    setIsProcessing(true);
    try {
      console.log('Handling assistant response:', assistant_response);

      const { messageType, message } = parseAssistantResponse(assistant_response);

      // Prepare new messages
      const newMessages = [];

      if (userText) {
        newMessages.push({
          type: 'USER',
          recipient: 'Assistant',
          content: userText,
        });
      }

      switch (messageType) {
        case 'USER':
        case 'TARGET':
          newMessages.push({
            type: messageType,
            recipient: 'Assistant',
            content: message,
          });
          setTranslatedText(message); // This will trigger the TextToSpeech component
          break;
        case 'CAUTION':
          setCautionMessage(message);
          setCautionOpen(true);
          newMessages.push({
            type: 'CAUTION',
            recipient: 'Assistant',
            content: message,
          });
          setTranslatedText(message); // TTS for caution messages
          break;
        case 'SUMMARY':
          setSummaryMessage(message);
          setSummaryOpen(true);
          newMessages.push({
            type: 'SUMMARY',
            recipient: 'Assistant',
            content: message,
          });
          setTranslatedText(message); // TTS for summary messages
          break;
        default:
          console.warn('Unknown message type:', messageType);
          newMessages.push({
            type: 'ASSISTANT',
            recipient: 'Assistant',
            content: message,
          });
          setTranslatedText(message); // Default TTS
          break;
      }

      // Handle summary if present
      if (summary) {
        console.log('Handling summary:', summary);
        setSummaryMessage(summary);
        setSummaryOpen(true);
        newMessages.push({
          type: 'SUMMARY',
          recipient: 'Assistant',
          content: summary,
        });
        setTranslatedText(summary); // TTS for summary
      }

      // Update conversation history
      setHistory((prevHistory) => [...prevHistory, ...newMessages]);
    } catch (error) {
      console.error('Error handling assistant response:', error);
      triggerNotification('error', 'Failed to process assistant response.');
    } finally {
      setIsProcessing(false);
    }
  };

  // Handle responses from audio recordings
  const handleAudioResponse = (response) => {
    console.log('Handling audio response:', response);
    const { user_text, assistant_response, summary } = response;
    handleAssistantResponse(assistant_response, summary, user_text);
  };

  // Function to handle "I cannot speak right now" button click
  const handleShowChatInput = () => {
    setShowChatInput(true);
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

        {/* Conversation History - Always Visible */}
        <Grid item xs={12} md={10}>
          <ConversationHistory history={history} />
        </Grid>

        {/* Button to Show Chat Input */}
        {!showChatInput && (
          <Grid item xs={12} textAlign="center">
            <Button
              variant="contained"
              color="secondary"
              onClick={handleShowChatInput}
              sx={{
                borderRadius: '50px',
                padding: '12px 24px',
                transition: 'background-color 0.3s, transform 0.3s',
                '&:hover': {
                  backgroundColor: 'secondary.dark',
                  transform: 'scale(1.05)',
                },
              }}
            >
              I cannot speak right now
            </Button>
          </Grid>
        )}

        {/* Conditionally Render Chat Input */}
        {showChatInput && (
          <Grid item xs={12} md={6} sx={{ margin: '0 auto' }}>
            <ChatInput 
              sessionId={sessionId}
              onResponse={handleAssistantResponse}
              isProcessing={isProcessing}
              onClose={() => setShowChatInput(false)} // Function to hide chat input
            />
          </Grid>
        )}

        {/* Removed Informational Text for Non-Verbal Users */}
        {/* <Grid item xs={12} textAlign="center">
          <Typography variant="body1" color="textSecondary">
            If you're unable to speak, please use the text input below to submit your message.
          </Typography>
        </Grid> */}
      </Grid>

      {/* Notification Component */}
      <Notification
        open={notification.open}
        onClose={handleNotificationClose}
        severity={notification.severity}
        message={notification.message}
      />

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

      {/* Text-to-Speech Component */}
      <TextToSpeech text={translatedText} language={languageCodeMap[targetLanguage] || 'en-US'} />
    </Box>
  );
};

export default TranslationPage;

// src/api.js

import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000'; // Ensure this matches your backend's URL

/**
 * Sets the objective and initializes a session.
 * @param {string} objective - The user's objective.
 * @param {string} targetLanguage - The target language (e.g., 'en', 'es').
 * @param {string} userLanguage - The user's language (e.g., 'en', 'es').
 * @param {string} country - The user's country/region (e.g., 'US', 'ES').
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
    console.error('Error in setObjective:', error.response ? error.response.data : error.message);
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
    console.log(`Sending message to session ${sessionId}:`, message);
    const response = await axios.post(
      `${API_BASE_URL}/send_message/${sessionId}`,
      { message }, // Correct structure
      {
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );
    console.log('sendTextMessage response:', response.data);
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
  formData.append('file', audioFile); // Ensure the key is 'file'

  try {
    const response = await axios.post(`${API_BASE_URL}/process_audio/${sessionId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data', // Correct header
      },
    });
    console.log('sendAudioMessage response:', response.data);
    return response.data; // Expected response: { user_text, assistant_response, summary (optional) }
  } catch (error) {
    console.error('Error in sendAudioMessage:', error.response ? error.response.data : error.message);
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
    console.error('Error in getSummary:', error.response ? error.response.data : error.message);
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
    console.error('Error in synthesizeText:', error.response ? error.response.data : error.message);
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

/* src/App.css */

.App {
  text-align: center;
}

.App-logo {
  height: 40vmin;
  pointer-events: none;
}

@media (prefers-reduced-motion: no-preference) {
  .App-logo {
    animation: App-logo-spin infinite 20s linear;
  }
}

.App-header {
  background-color: #282c34;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-size: calc(10px + 2vmin);
  color: white;
}

.App-link {
  color: #61dafb;
}

@keyframes App-logo-spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

// src/App.js

import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import NavigationBar from './components/NavigationBar';
import { Container } from '@mui/material';
import { SessionProvider, SessionContext } from './contexts/SessionContext';

// Lazy load pages
const HomePage = lazy(() => import('./pages/HomePage'));
const TranslationPage = lazy(() => import('./pages/TranslationPage'));
const HistoryPage = lazy(() => import('./pages/HistoryPage'));

const ProtectedRoute = ({ children }) => {
  const { sessionId } = React.useContext(SessionContext);
  return sessionId ? children : <Navigate to="/" />;
};

const App = () => {
  return (
    <SessionProvider>
      <Router>
        <NavigationBar />
        <Container sx={{ mt: 4 }}>
          <Suspense fallback={<div>Loading...</div>}>
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
          </Suspense>
        </Container>
      </Router>
    </SessionProvider>
  );
};

export default App;

/* src/index.css */
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}

.recording {
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.7;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

// src/index.js

import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

// Create a custom theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2', // Customize primary color
    },
    secondary: {
      main: '#dc004e', // Customize secondary color
    },
    error: {
      main: '#f44336', // Customize error color
    },
    success: {
      main: '#4caf50', // Customize success color
    },
  },
  shape: {
    borderRadius: 50, // Increase global border radius for more rounded elements
  },
  typography: {
    fontFamily: 'Roboto, Arial, sans-serif', // Customize font
  },
});

ReactDOM.render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline /> {/* Normalize CSS across browsers */}
      <App />
    </ThemeProvider>
  </React.StrictMode>,
  document.getElementById('root')
);
