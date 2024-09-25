// src/components/Summary.js
import React, { useEffect, useState } from 'react';
import { getSummary } from '../api';

const Summary = ({ sessionId }) => {
  const [summary, setSummary] = useState('');

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const data = await getSummary(sessionId);
        setSummary(data.summary);
      } catch (error) {
        console.error('Error fetching summary:', error);
      }
    };

    fetchSummary();
  }, [sessionId]);

  if (!summary) return null;

  return (
    <div>
      <h2>Conversation Summary</h2>
      <p>{summary}</p>
    </div>
  );
};

export default Summary;
