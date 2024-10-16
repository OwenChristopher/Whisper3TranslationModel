// src/App.js

import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import NavigationBar from './components/NavigationBar';
import { Container } from '@mui/material';
import { SessionProvider, SessionContext } from './contexts/SessionContext';

// Lazy load pages
const HomePage = lazy(() => import('./pages/HomePage'));
const TranslationPage = lazy(() => import('./pages/TranslationPage'));
const HistoryPage = lazy(() => import('./pages/HistoryPage'));

const ProtectedRoute = ({ children }) => {
  const { sessionId } = React.useContext(SessionContext);
  return sessionId ? children : <Navigate to="/" />;
};

const App = () => {
  return (
    <SessionProvider>
      <Router>
        <NavigationBar />
        <Container sx={{ mt: 4 }}>
          <Suspense fallback={<div>Loading...</div>}>
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
          </Suspense>
        </Container>
      </Router>
    </SessionProvider>
  );
};

export default App;