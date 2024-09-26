import React, { useState } from 'react';
import { Button, TextField, Select, MenuItem, Typography, Box } from '@mui/material';
import { setObjective } from '../api'; 


const languages = [
  { code: 'en', name: 'English' },
  { code: 'es', name: 'Spanish' },
  { code: 'fr', name: 'French' },
  // Add more languages as needed
];

const ObjectiveForm = ({ onObjectiveSet }) => {
  const [objective, setObjectiveText] = useState('');
  const [targetLanguage, setTargetLanguage] = useState('en'); // Default to English

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const data = await setObjective(objective, targetLanguage);
      onObjectiveSet(data.session_id);
    } catch (error) {
      console.error('Error setting objective:', error);
      alert('Failed to set objective.');
    }
  };

  return (
    <Box sx={{ p: 2, border: '1px solid #ccc', borderRadius: 2 }}>
      <Typography variant="h5">Set Your Objective</Typography>
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
        <Select
          value={targetLanguage}
          onChange={(e) => setTargetLanguage(e.target.value)}
          fullWidth
          sx={{ mb: 2 }}
        >
          {languages.map((language) => (
            <MenuItem key={language.code} value={language.code}>
              {language.name}
            </MenuItem>
          ))}
        </Select>
        <Button type="submit" variant="contained" color="primary" fullWidth>
          Start Session
        </Button>
      </form>
    </Box>
  );
};

export default ObjectiveForm;
