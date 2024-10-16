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
