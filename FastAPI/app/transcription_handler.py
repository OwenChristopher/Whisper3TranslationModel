# app/transcription_handler.py

import torch
import whisper

class TranscriptionHandler:
    def __init__(self, model_name='large', device=None):
        self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")
        print("Loading Whisper model...")
        self.model = whisper.load_model(model_name).to(self.device)
        print("Whisper model loaded.")

    def transcribe(self, audio_path):
        print("Transcribing with Whisper...")
        result = self.model.transcribe(audio_path)
        return result['text']
