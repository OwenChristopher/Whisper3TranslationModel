// src/api.js

import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000'; // Ensure this matches your backend's URL

/**
 * Sets the objective and initializes a session.
 * @param {string} objective - The user's objective.
 * @param {string} targetLanguage - The target language (e.g., 'en', 'es').
 * @param {string} userLanguage - The user's language (e.g., 'en', 'es').
 * @param {string} country - The user's country/region (e.g., 'US', 'ES').
 * @returns {Promise<Object>} - The response containing session_id and message.
 */
export const setObjective = async (objective, targetLanguage, userLanguage, country) => {
  console.log('Setting objective with:', { objective, targetLanguage, userLanguage, country });
  try {
    const response = await axios.post(`${API_BASE_URL}/set_objective`, {
      objective,
      target_language: targetLanguage,
      user_language: userLanguage,
      country: country,
    });
    console.log('setObjective response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error in setObjective:', error.response ? error.response.data : error.message);
    throw error;
  }
};

/**
 * Sends a text message for processing.
 * @param {string} sessionId - The session ID.
 * @param {string} message - The user's message.
 * @returns {Promise<Object>} - The backend JSON response.
 */
export const sendTextMessage = async (sessionId, message) => {
  try {
    console.log(`Sending message to session ${sessionId}:`, message);
    const response = await axios.post(
      `${API_BASE_URL}/send_message/${sessionId}`,
      { message }, // Correct structure
      {
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );
    console.log('sendTextMessage response:', response.data);
    return response.data; // Expected response: { assistant_response, history }
  } catch (error) {
    console.error('Error in sendTextMessage:', error.response ? error.response.data : error.message);
    throw error;
  }
};

/**
 * Sends an audio file for processing.
 * @param {string} sessionId - The session ID.
 * @param {File} audioFile - The audio file to process.
 * @returns {Promise<Object>} - The backend JSON response containing user_text and assistant_response.
 */
export const sendAudioMessage = async (sessionId, audioFile) => {
  console.log('Sending audio message:', { sessionId, audioFile });
  const formData = new FormData();
  formData.append('file', audioFile); // Ensure the key is 'file'

  try {
    const response = await axios.post(`${API_BASE_URL}/process_audio/${sessionId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data', // Correct header
      },
    });
    console.log('sendAudioMessage response:', response.data);
    return response.data; // Expected response: { user_text, assistant_response, summary (optional) }
  } catch (error) {
    console.error('Error in sendAudioMessage:', error.response ? error.response.data : error.message);
    throw error;
  }
};

/**
 * Retrieves the summary of the conversation.
 * @param {string} sessionId - The session ID.
 * @returns {Promise<Object>} - The summary response.
 */
export const getSummary = async (sessionId) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/summary/${sessionId}`);
    return response.data; // Expected response: { summary: "..." }
  } catch (error) {
    console.error('Error in getSummary:', error.response ? error.response.data : error.message);
    throw error;
  }
};

/**
 * Synthesizes text to speech (if applicable).
 * @param {string} text - The text to synthesize.
 * @returns {Promise<Blob>} - The synthesized audio Blob.
 */
export const synthesizeText = async (text) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/synthesize_text`, { text }, {
      responseType: 'blob', // Assuming backend returns audio Blob
    });
    return response.data; // Binary audio data
  } catch (error) {
    console.error('Error in synthesizeText:', error.response ? error.response.data : error.message);
    throw error;
  }
};

// Export all functions as named exports
export default {
  setObjective,
  sendTextMessage,
  sendAudioMessage,
  getSummary,
  synthesizeText,
};
