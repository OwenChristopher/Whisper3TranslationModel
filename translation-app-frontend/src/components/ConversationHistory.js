// src/components/ConversationHistory.js

import React, { useEffect, useRef } from 'react';
import { Box, Typography, Paper, List, ListItem, ListItemText, Divider } from '@mui/material';

/**
 * ConversationHistory component displays the list of messages exchanged between the user and the assistant.
 * @param {Array} history - An array of message objects containing type, recipient, and content.
 */
const ConversationHistory = ({ history }) => {
  const listEndRef = useRef(null);

  useEffect(() => {
    // Scroll to the bottom when a new message is added
    if (listEndRef.current) {
      listEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [history]);

  /**
   * Parses each message to ensure it has type, recipient, and content.
   * Provides default values if necessary to prevent runtime errors.
   * @param {Object} item - A message object from the history.
   * @returns {Object} - Parsed message with type, recipient, and content.
   */
  const parseMessage = (item) => {
    // Ensure that 'type' and 'recipient' exist; provide defaults if not
    const messageType = item.type ? item.type.toUpperCase() : 'ASSISTANT';
    const recipient = item.recipient ? item.recipient : (messageType === 'USER' ? 'User' : 'Assistant');
    const content = item.content ? item.content : '';

    return {
      type: messageType, // 'USER', 'TARGET', 'CAUTION', 'SUMMARY', 'SYSTEM', etc.
      recipient: recipient, // 'User', 'Target', 'Caution', 'Summary', 'Assistant', 'System'
      content: content,
    };
  };

  return (
    <Box sx={{ mt: 4 }}>
      <Typography variant="h5" gutterBottom>
        Conversation Logs
      </Typography>
      <Paper elevation={3} sx={{ maxHeight: 400, overflowY: 'auto', padding: 2 }}>
        <List>
          {history.map((item, index) => {
            const { type, recipient, content } = parseMessage(item);

            // Determine the color based on message type
            let color;
            switch (type) {
              case 'USER':
                color = 'primary';
                break;
              case 'TARGET':
                color = 'secondary';
                break;
              case 'CAUTION':
              case 'SUMMARY':
                color = 'error';
                break;
              case 'SYSTEM':
                color = 'textSecondary';
                break;
              default:
                color = 'textPrimary';
                break;
            }

            // Determine the display name based on recipient
            let displayName;
            switch (type) {
              case 'USER':
                displayName = 'You';
                break;
              case 'TARGET':
                displayName = 'Target';
                break;
              case 'CAUTION':
                displayName = 'Caution';
                break;
              case 'SUMMARY':
                displayName = 'Summary';
                break;
              case 'SYSTEM':
                displayName = 'System';
                break;
              default:
                displayName = 'Assistant';
                break;
            }

            return (
              <React.Fragment key={index}>
                <ListItem alignItems="flex-start">
                  <ListItemText
                    primary={
                      <Typography
                        variant="subtitle2"
                        color={color}
                      >
                        {displayName}
                      </Typography>
                    }
                    secondary={
                      <Typography variant="body1" color="textPrimary">
                        {content}
                      </Typography>
                    }
                  />
                </ListItem>
                <Divider component="li" />
              </React.Fragment>
            );
          })}
          <div ref={listEndRef} />
        </List>
      </Paper>
    </Box>
  );
};

export default ConversationHistory;
