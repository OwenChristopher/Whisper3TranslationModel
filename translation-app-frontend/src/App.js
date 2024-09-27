// src/App.js

import React, { useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import NavigationBar from './components/NavigationBar';
import HomePage from './pages/HomePage';
import TranslationPage from './pages/TranslationPage';
import HistoryPage from './pages/HistoryPage';
import { Container } from '@mui/material';
import { SessionProvider, SessionContext } from './contexts/SessionContext';

const ProtectedRoute = ({ children }) => {
  const { sessionId } = useContext(SessionContext);
  return sessionId ? children : <Navigate to="/" />;
};

const App = () => {
  return (
    <SessionProvider>
    <Router>
        <NavigationBar />
        <Container sx={{ mt: 4 }}>
      <Routes>
            <Route path="/" element={<HomePage />} />
            <Route
              path="/translate"
              element={
                <ProtectedRoute>
                  <TranslationPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/history"
              element={
                <ProtectedRoute>
                  <HistoryPage />
                </ProtectedRoute>
              }
            />
            {/* Add more routes as needed */}
      </Routes>
        </Container>
    </Router>
    </SessionProvider>
  );
};

export default App;
