import React from 'react';
import { Box, Typography } from '@mui/material';

const ConversationHistory = ({ history }) => {
  return (
    <Box sx={{ p: 2, border: '1px solid #ccc', borderRadius: 2, mb: 2 }}>
      <Typography variant="h5">Conversation History</Typography>
      {history.length === 0 ? (
        <Typography>No interactions yet.</Typography>
      ) : (
        history.map((item, index) => (
          <Box key={index} sx={{ mb: 1 }}>
            <Typography><strong>User:</strong> {item.user_text}</Typography>
            <Typography><strong>Assistant:</strong> {item.assistant_response}</Typography>
            <hr />
          </Box>
        ))
      )}
    </Box>
  );
};

export default ConversationHistory;
