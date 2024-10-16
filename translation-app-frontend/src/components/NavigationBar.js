// src/components/NavigationBar.js

import React, { useContext } from 'react';
import { AppBar, Toolbar, Typography, Button, IconButton } from '@mui/material';
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
          sx={{
            borderRadius: '50px',
            transition: 'background-color 0.3s, transform 0.3s',
            '&:hover': {
              backgroundColor: 'primary.dark',
              transform: 'scale(1.05)',
            },
          }}
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
              sx={{
                borderRadius: '50px',
                transition: 'background-color 0.3s, transform 0.3s',
                '&:hover': {
                  backgroundColor: 'primary.dark',
                  transform: 'scale(1.05)',
                },
                ml: 2,
              }}
            >
              Translate
            </Button>
            <Button
              color="inherit"
              startIcon={<HistoryIcon />}
              component={RouterLink}
              to="/history"
              sx={{
                borderRadius: '50px',
                transition: 'background-color 0.3s, transform 0.3s',
                '&:hover': {
                  backgroundColor: 'primary.dark',
                  transform: 'scale(1.05)',
                },
                ml: 2,
              }}
            >
              History
            </Button>
            <Button
              color="inherit"
              onClick={handleResetSession}
              sx={{ 
                ml: 2,
                borderRadius: '50px',
                transition: 'background-color 0.3s, transform 0.3s',
                '&:hover': {
                  backgroundColor: 'secondary.dark',
                  transform: 'scale(1.05)',
                },
              }}
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
