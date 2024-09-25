// src/components/ObjectiveForm.js
import React, { useState } from 'react';
import { setObjective } from '../api';

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
    <form onSubmit={handleSubmit}>
      <h2>Set Your Objective</h2>
      <div>
        <label>Objective:</label>
        <input
          type="text"
          value={objective}
          onChange={(e) => setObjectiveText(e.target.value)}
          required
        />
      </div>
      <div>
        <label>Target Language:</label>
        <select
          value={targetLanguage}
          onChange={(e) => setTargetLanguage(e.target.value)}
        >
          <option value="en">English</option>
          <option value="es">Spanish</option>
          <option value="fr">French</option>
          {/* Add more languages as needed */}
        </select>
      </div>
      <button type="submit">Start Session</button>
    </form>
  );
};

export default ObjectiveForm;
