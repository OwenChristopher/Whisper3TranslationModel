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
