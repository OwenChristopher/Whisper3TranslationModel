// src/App.js
import React, { useState } from 'react';
import ObjectiveForm from './components/ObjectiveForm';
import AudioRecorder from './components/AudioRecorder';
import ConversationHistory from './components/ConversationHistory';
import Summary from './components/Summary';
import { Container, Box, Typography } from '@mui/material';

const App = () => {
  const [sessionId, setSessionId] = useState(null);
  const [history, setHistory] = useState([]);
  const [isFulfilled, setIsFulfilled] = useState(false);

  const handleObjectiveSet = (id) => {
    setSessionId(id);
    setHistory([]); // Reset history on new session
  };

  const handleResponse = (response) => {
    const newInteraction = {
      user_text: response.user_text,
      assistant_response: response.assistant_response,
    };
    setHistory((prev) => [...prev, newInteraction]);
    setIsFulfilled(response.fulfilled);
  };

  return (
    <Container maxWidth="sm">
      <Typography variant="h4" align="center" sx={{ mb: 4 }}>Translation App</Typography>
      <Box>
        {!sessionId ? (
          <ObjectiveForm onObjectiveSet={handleObjectiveSet} />
        ) : (
          <>
            <AudioRecorder sessionId={sessionId} onResponse={handleResponse} />
            <ConversationHistory history={history} />
            {isFulfilled && <Summary sessionId={sessionId} />}
          </>
        )}
      </Box>
    </Container>
  );
};

export default App;
