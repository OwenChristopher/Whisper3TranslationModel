// src/components/TextToSpeech.js

import React, { useEffect, useState } from 'react';

export const TextToSpeech = ({ text, language }) => {
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
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'zh-CN';
    
      // Manually select the Chinese voice by name
      const selectedVoice = voices.find(voice => voice.name === 'Google 普通话（中国大陆）');
    
      if (selectedVoice) {
        console.log(`Manually selected Voice: ${selectedVoice.name}, Lang: ${selectedVoice.lang}`);
        utterance.voice = selectedVoice;
      } else {
        console.warn(`Chinese voice not found. Using default voice.`);
      }
    
      window.speechSynthesis.speak(utterance);
    }
  }, [text, language, voices]);

  return null; // This component does not render anything
};
