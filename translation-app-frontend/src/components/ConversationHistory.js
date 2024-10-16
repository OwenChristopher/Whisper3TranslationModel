// src/components/ConversationHistory.js

import React, { useEffect, useRef, useState } from 'react';
import { Box, Typography, Paper, List, ListItem, ListItemText, Divider, Button, Collapse, IconButton } from '@mui/material';
import { ExpandLess, ExpandMore, Close } from '@mui/icons-material';

/**
 * ConversationHistory component displays the list of messages exchanged between the user and the assistant.
 * @param {Array} history - An array of message objects containing type, recipient, and content.
 * @param {Function} onClose - Function to handle closing the chat box.
 */
const ConversationHistory = React.memo(({ history, onClose }) => {
  const listEndRef = useRef(null);
  const [isVisible, setIsVisible] = useState(true); // State to manage visibility

  useEffect(() => {
    // Scroll to the bottom when a new message is added
    if (listEndRef.current && isVisible) {
      listEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [history, isVisible]);

  /**
   * Parses each message to ensure it has type, recipient, and content.
   * Provides default values if necessary to prevent runtime errors.
   * @param {Object} item - A message object from the history.
   * @param {number} index - The index of the message in the history array.
   * @returns {Object|null} - Parsed message with type, recipient, and content or null to skip rendering.
   */
  const parseMessage = (item, index) => {
    // **Skip rendering the first message regardless of its type**
    if (index === 0) {
      return null;
    }

    // Ensure that 'type' and 'recipient' exist; provide defaults if not
    const messageType = item.type ? item.type.toUpperCase() : 'ASSISTANT';
    const recipient = item.recipient ? item.recipient : (messageType === 'USER' ? 'User' : 'Assistant');
    const content = item.content ? item.content : '';

    return {
      type: messageType, // 'USER', 'TARGET', 'CAUTION', 'SUMMARY', 'SYSTEM', etc.
      recipient: recipient, // 'You', 'Target', 'Caution', 'Summary', 'Assistant', 'System'
      content: content,
    };
  };

  const toggleVisibility = () => {
    setIsVisible((prev) => !prev);
  };

  return (
    <Box sx={{ mt: 4 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h5" gutterBottom>
          Conversation Logs
        </Typography>
        <Box>
          <Button onClick={toggleVisibility} startIcon={isVisible ? <ExpandLess /> : <ExpandMore />} sx={{ mr: 1 }}>
            {isVisible ? 'Collapse' : 'Expand'}
          </Button>
          <IconButton onClick={onClose} color="secondary" aria-label="Close Chat Box">
            <Close />
          </IconButton>
        </Box>
      </Box>
      <Collapse in={isVisible}>
        <Paper elevation={3} sx={{ maxHeight: 400, overflowY: 'auto', padding: 2 }}>
          <List>
            {history.map((item, index) => {
              const parsedMessage = parseMessage(item, index);
              if (!parsedMessage) return null; // Skip rendering

              const { type, recipient, content } = parsedMessage;

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

              // Handle cases where Assistant message might be blank
              if (type === 'ASSISTANT' && !content.trim()) {
                return null; // Skip rendering empty Assistant messages
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
                          {content || '(No message content)'}
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
      </Collapse>
    </Box>
  );
});

export default ConversationHistory;
