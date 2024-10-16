// src/index.js

import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

// Create a custom theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2', // Customize primary color
    },
    secondary: {
      main: '#dc004e', // Customize secondary color
    },
    error: {
      main: '#f44336', // Customize error color
    },
    success: {
      main: '#4caf50', // Customize success color
    },
  },
  shape: {
    borderRadius: 50, // Increase global border radius for more rounded elements
  },
  typography: {
    fontFamily: 'Roboto, Arial, sans-serif', // Customize font
  },
});

ReactDOM.render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline /> {/* Normalize CSS across browsers */}
      <App />
    </ThemeProvider>
  </React.StrictMode>,
  document.getElementById('root')
);