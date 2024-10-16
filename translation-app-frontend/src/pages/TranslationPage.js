// src/pages/TranslationPage.js

import React, { useState, useContext, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Grid, 
  CircularProgress, 
  Button 
} from '@mui/material';
import DynamicAudioRecorder from '../components/DynamicAudioRecorder';
import { SessionContext } from '../contexts/SessionContext';
import Notification from '../components/Notification';
import PopupDialog from '../components/PopupDialog';
import ConversationHistory from '../components/ConversationHistory';
import ChatInput from '../components/ChatInput';
import { TextToSpeech } from '../components/TextToSpeech';
import { languageCodeMap } from '../utils/languageCodes';
import { sendTextMessage } from '../api';

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
      triggerNotification('error', 'Please set your objective first.');
      window.location.href = '/';
    } else if (!isInitialMessageSent) {
      // Send the initial objective as a message to initialize the chat
      const sendInitialObjective = async () => {
        setIsProcessing(true);
        try {
          // Send an initial empty message or customize as needed
          const response = await sendTextMessage(sessionId, '');
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
      const messageType = match[1].toUpperCase();
      const message = assistantResponse.replace(prefixPattern, '').trim();
      return { messageType, message };
    } else {
      return { messageType: 'ASSISTANT', message: assistantResponse };
    }
  };

  // Handle assistant response
  const handleAssistantResponse = (assistant_response, summary, userText = null) => {
    setIsProcessing(true);
    try {
      if (!assistant_response || !assistant_response.trim()) {
        triggerNotification('warning', 'Received an empty response from the Assistant.');
        return;
      }

      console.log('Handling assistant response:', assistant_response);

      const { messageType, message } = parseAssistantResponse(assistant_response);

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
          setTranslatedText(message);
          break;
        case 'CAUTION':
          setCautionMessage(message);
          setCautionOpen(true);
          newMessages.push({
            type: 'CAUTION',
            recipient: 'Assistant',
            content: message,
          });
          setTranslatedText(message);
          break;
        case 'SUMMARY':
          setSummaryMessage(message);
          setSummaryOpen(true);
          newMessages.push({
            type: 'SUMMARY',
            recipient: 'Assistant',
            content: message,
          });
          setTranslatedText(message);
          break;
        default:
          console.warn('Unknown message type:', messageType);
          newMessages.push({
            type: 'ASSISTANT',
            recipient: 'Assistant',
            content: message,
          });
          setTranslatedText(message);
          break;
      }

      if (summary) {
        console.log('Handling summary:', summary);
        setSummaryMessage(summary);
        setSummaryOpen(true);
        newMessages.push({
          type: 'SUMMARY',
          recipient: 'Assistant',
          content: summary,
        });
        setTranslatedText(summary);
      }

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
        XMTranslation
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
