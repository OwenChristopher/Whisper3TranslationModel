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
