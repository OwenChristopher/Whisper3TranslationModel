// src/components/Summary.js

import React, { useEffect, useState } from 'react';
import { Box, Typography } from '@mui/material';
import { getSummary } from '../api';

const Summary = ({ sessionId }) => {
  const [summary, setSummary] = useState('');

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const data = await getSummary(sessionId);
        setSummary(data.summary);
      } catch (error) {
        console.error('Error fetching summary:', error);
      }
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
