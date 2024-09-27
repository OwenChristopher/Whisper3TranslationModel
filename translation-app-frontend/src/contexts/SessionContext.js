// src/contexts/SessionContext.js

import React, { createContext, useState } from 'react';

export const SessionContext = createContext();

// export const SessionProvider = ({ children }) => {
//   const [sessionId, setSessionId] = useState(null);
//   const [userLanguage, setUserLanguage] = useState('en'); // Initialized with language code
//   const [targetLanguage, setTargetLanguage] = useState('en'); // Initialized with language code
//   const [country, setCountry] = useState('US'); // Country code as per your implementation

export const SessionProvider = ({ children }) => {
  const [sessionId, setSessionId] = useState(null);
  const [userLanguage, setUserLanguage] = useState('zh'); // Initialized with language code
  const [targetLanguage, setTargetLanguage] = useState('zh'); // Initialized with language code
  const [country, setCountry] = useState('CN'); // Country code as per your implementation

  return (
    <SessionContext.Provider
      value={{
        sessionId,
        setSessionId,
        userLanguage,
        setUserLanguage,
        targetLanguage,
        setTargetLanguage,
        country,
        setCountry,
      }}
    >
      {children}
    </SessionContext.Provider>
  );
};
