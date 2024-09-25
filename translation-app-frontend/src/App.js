// src/App.js
import React, { useState } from 'react';
import ObjectiveForm from './components/ObjectiveForm';
import AudioRecorder from './components/AudioRecorder';
import ConversationHistory from './components/ConversationHistory';
import Summary from './components/Summary';

const App = () => {
  const [sessionId, setSessionId] = useState(null);
  const [history, setHistory] = useState([]);
  const [isFulfilled, setIsFulfilled] = useState(false);

  const handleObjectiveSet = (id) => {
    setSessionId(id);
  };

  const handleResponse = (response) => {
    const newInteraction = {
      user_text: response.user_text,
      assistant_response: response.assistant_response,
    };
    setHistory((prev) => [...prev, newInteraction]);
    setIsFulfilled(response.fulfilled);

    if (response.fulfilled && response.summary) {
      // Optionally, you can handle the summary here
    }
  };

  return (
    <div className="App">
      <h1>Translation App</h1>
      {!sessionId ? (
        <ObjectiveForm onObjectiveSet={handleObjectiveSet} />
      ) : (
        <>
          <AudioRecorder sessionId={sessionId} onResponse={handleResponse} />
          <ConversationHistory history={history} />
          {isFulfilled && <Summary sessionId={sessionId} />}
        </>
      )}
    </div>
  );
};

export default App;
