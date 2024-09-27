// src/components/NavigationBar.js

import React, { useContext } from 'react';
import { AppBar, Toolbar, Typography, Button } from '@mui/material';
import TranslateIcon from '@mui/icons-material/Translate';
import HistoryIcon from '@mui/icons-material/History';
import HomeIcon from '@mui/icons-material/Home';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { SessionContext } from '../contexts/SessionContext';

const NavigationBar = () => {
  const { sessionId, setSessionId } = useContext(SessionContext);
  const navigate = useNavigate();

  const handleResetSession = () => {
    setSessionId(null);
    navigate('/');
  };

  return (
    <AppBar position="static">
      <Toolbar>
        <HomeIcon sx={{ mr: 2 }} />
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Translation App
        </Typography>
        <Button
          color="inherit"
          startIcon={<HomeIcon />}
          component={RouterLink}
          to="/"
        >
          Home
        </Button>
        {sessionId && (
          <>
            <Button
              color="inherit"
              startIcon={<TranslateIcon />}
              component={RouterLink}
              to="/translate"
            >
              Translate
            </Button>
            <Button
              color="inherit"
              startIcon={<HistoryIcon />}
              component={RouterLink}
              to="/history"
            >
              History
            </Button>
            <Button
              color="inherit"
              onClick={handleResetSession}
              sx={{ ml: 2 }}
            >
              Reset Session
            </Button>
          </>
        )}
      </Toolbar>
    </AppBar>
  );
};

export default NavigationBar;
