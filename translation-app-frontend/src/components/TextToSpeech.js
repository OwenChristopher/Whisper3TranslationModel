// src/components/TextToSpeech.js

import React, { useEffect, useState } from 'react';

// Simple language detection function
const detectLanguage = (text) => {
  // Regex to detect Chinese characters
  const chineseRegex = /[\u4e00-\u9fff]/;
  if (chineseRegex.test(text)) {
    return 'zh-CN';
  }
  // Default to English
  return 'en-US';
};

export const TextToSpeech = ({ text }) => {
  const [voices, setVoices] = useState([]);

  useEffect(() => {
    // Function to load voices
    const loadVoices = () => {
      const availableVoices = speechSynthesis.getVoices();
      setVoices(availableVoices);
    };

    // Load voices when they are loaded
    if (speechSynthesis.onvoiceschanged !== undefined) {
      speechSynthesis.onvoiceschanged = loadVoices;
    }

    // Initial load
    loadVoices();
  }, []);

  useEffect(() => {
    if (text) {
      // Detect language
      const detectedLanguage = detectLanguage(text);
      console.log(`Detected Language: ${detectedLanguage}`);

      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = detectedLanguage;

      // Select voice based on detected language
      let selectedVoice;
      if (detectedLanguage.startsWith('zh')) {
        // Attempt to find a Chinese voice
        selectedVoice = voices.find(
          (voice) =>
            voice.lang.startsWith('zh') &&
            (voice.name.toLowerCase().includes('google') ||
              voice.name.toLowerCase().includes('zh'))
        );
      } else if (detectedLanguage.startsWith('en')) {
        // Attempt to find an English voice
        selectedVoice = voices.find(
          (voice) =>
            voice.lang.startsWith('en') &&
            (voice.name.toLowerCase().includes('google') ||
              voice.name.toLowerCase().includes('english'))
        );
      }

      if (selectedVoice) {
        console.log(`Selected Voice: ${selectedVoice.name}, Lang: ${selectedVoice.lang}`);
        utterance.voice = selectedVoice;
      } else {
        console.warn(`No specific voice found for ${detectedLanguage}. Using default voice.`);
      }

      window.speechSynthesis.speak(utterance);
    }
  }, [text, voices]);

  return null; // This component does not render anything
};
