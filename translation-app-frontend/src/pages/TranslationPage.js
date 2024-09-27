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
          alert('Failed to initialize chat with objective.');
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
  const handleAssistantResponse = (assistant_response, summary) => {
    setIsProcessing(true);
    try {
      console.log('Handling assistant response:', assistant_response);

      const { messageType, message } = parseAssistantResponse(assistant_response);

      switch (messageType) {
        case 'USER':
        case 'TARGET':
          // Regular assistant message intended for the user or target
          setTranslatedText(message); // This will trigger the TextToSpeech component
          break;
        case 'CAUTION':
          setCautionMessage(message);
          setCautionOpen(true);
          setTranslatedText(message); // TTS for caution messages
          break;
        case 'SUMMARY':
          setSummaryMessage(message);
          setSummaryOpen(true);
          setTranslatedText(message); // TTS for summary messages
          break;
        default:
          console.warn('Unknown message type:', messageType);
          setTranslatedText(message); // Default TTS
          break;
      }

      // Handle summary if present
      if (summary) {
        console.log('Handling summary:', summary);
        setSummaryMessage(summary);
        setSummaryOpen(true);
        setTranslatedText(summary); // TTS for summary
      }

      // Optionally, you can update the conversation history here if needed
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
      const { assistant_response, history: updatedHistory, summary } = response;

      // Map backend history to frontend structure
      const mappedHistory = updatedHistory.map(item => mapBackendMessageToFrontend(item));

      // Update conversation history
      setHistory(mappedHistory);

      // Handle assistant response
      handleAssistantResponse(assistant_response, summary);

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

      {/* Text-to-Speech Component */}
      <TextToSpeech text={translatedText} language={languageCodeMap[targetLanguage] || 'en-US'} />
    </Box>
  );
};

export default TranslationPage;
