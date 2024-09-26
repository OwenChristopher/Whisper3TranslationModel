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
