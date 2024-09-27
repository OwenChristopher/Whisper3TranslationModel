// src/pages/HistoryPage.js
import React, { useEffect, useState, useContext } from 'react';
import {
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
} from '@mui/material';
import { Delete, Replay } from '@mui/icons-material';
import { SessionContext } from '../contexts/SessionContext';
import axios from 'axios';

const HistoryPage = () => {
  const { sessionId } = useContext(SessionContext);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    if (!sessionId) {
      alert('Please set your objective first.');
      window.location.href = '/';
      return;
    }

    const fetchHistory = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/history/${sessionId}`);
        setHistory(response.data.history);
      } catch (error) {
        console.error('Error fetching history:', error);
        alert('Failed to fetch history.');
      }
    };

    fetchHistory();
  }, [sessionId]);

  const handleDelete = async (id) => {
    try {
      await axios.delete(`http://localhost:8000/history/${sessionId}/${id}`);
      setHistory((prev) => prev.filter((item) => item.id !== id));
    } catch (error) {
      console.error('Error deleting history item:', error);
      alert('Failed to delete history item.');
    }
  };

  const handleReuse = (item) => {
    // Logic to reuse past translation
    // For example, redirect to TranslationPage with pre-filled text
    // This might require using React Router's navigate function
    // or lifting the state up to App.js
    alert('Reuse feature not implemented yet.');
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Translation History
      </Typography>
      {history.length === 0 ? (
        <Typography>No past translations found.</Typography>
      ) : (
        <TableContainer component={Paper}>
          <Table aria-label="translation history">
            <TableHead>
              <TableRow>
                <TableCell>Timestamp</TableCell>
                <TableCell>Source Language</TableCell>
                <TableCell>Target Language</TableCell>
                <TableCell>Original Text</TableCell>
                <TableCell>Translated Text</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {history.map((item) => (
                <TableRow key={item.id}>
                  <TableCell>{item.timestamp}</TableCell>
                  <TableCell>{item.source_language}</TableCell>
                  <TableCell>{item.target_language}</TableCell>
                  <TableCell>{item.original_text}</TableCell>
                  <TableCell>{item.translated_text}</TableCell>
                  <TableCell>
                    <IconButton
                      color="primary"
                      onClick={() => handleReuse(item)}
                    >
                      <Replay />
                    </IconButton>
                    <IconButton
                      color="secondary"
                      onClick={() => handleDelete(item.id)}
                    >
                      <Delete />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
};

export default HistoryPage;
