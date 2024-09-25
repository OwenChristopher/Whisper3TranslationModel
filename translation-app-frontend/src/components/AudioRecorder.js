// src/components/AudioRecorder.js
import React, { useState, useRef } from 'react';
import { processAudio } from '../api';

const AudioRecorder = ({ sessionId, onResponse }) => {
  const [isRecording, setIsRecording] = useState(false);
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
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
          audioChunksRef.current = [];
          const audioFile = new File([audioBlob], 'recording.wav', { type: 'audio/wav' });

          try {
            const response = await processAudio(sessionId, audioFile);
            onResponse(response);
          } catch (error) {
            console.error('Error processing audio:', error);
            alert('Failed to process audio.');
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
    <div>
      <h2>Record Your Audio</h2>
      {!isRecording ? (
        <button onClick={startRecording}>Start Recording</button>
      ) : (
        <button onClick={stopRecording}>Stop Recording</button>
      )}
    </div>
  );
};

export default AudioRecorder;
