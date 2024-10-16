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
