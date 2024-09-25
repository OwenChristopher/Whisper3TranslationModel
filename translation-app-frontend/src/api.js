// src/api.js
import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000'; 

export const setObjective = async (objective, targetLanguage) => {
  const response = await axios.post(`${API_BASE_URL}/set_objective`, {
    objective,
    target_language: targetLanguage,
  });
  return response.data;
};

export const processAudio = async (sessionId, audioFile) => {
  const formData = new FormData();
  formData.append('file', audioFile);

  const response = await axios.post(
    `${API_BASE_URL}/process_audio/${sessionId}`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );
  return response.data;
};

export const getSummary = async (sessionId) => {
  const response = await axios.get(`${API_BASE_URL}/summary/${sessionId}`);
  return response.data;
};
