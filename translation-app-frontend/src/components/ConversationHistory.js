// src/components/ConversationHistory.js
import React from 'react';

const ConversationHistory = ({ history }) => {
  return (
    <div>
      <h2>Conversation History</h2>
      {history.length === 0 ? (
        <p>No interactions yet.</p>
      ) : (
        history.map((item, index) => (
          <div key={index}>
            <p><strong>User:</strong> {item.user_text}</p>
            <p><strong>Assistant:</strong> {item.assistant_response}</p>
            <hr />
          </div>
        ))
      )}
    </div>
  );
};

export default ConversationHistory;
