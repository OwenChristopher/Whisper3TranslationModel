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
