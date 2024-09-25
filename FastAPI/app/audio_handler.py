# app/audio_handler.py

import os
import soundfile as sf
from pydub import AudioSegment, effects
import noisereduce as nr
import sounddevice as sd
import tempfile

class AudioHandler:
    def __init__(self, sample_rate=16000, duration=5):
        self.sample_rate = sample_rate
        self.duration = duration

    def record_audio(self):
        print("Recording...")
        try:
            recording = sd.rec(int(self.duration * self.sample_rate), samplerate=self.sample_rate, channels=1, dtype='float32')
            sd.wait()  # Wait until recording is finished
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
                sf.write(tmpfile.name, recording, self.sample_rate)
                print(f"Audio recorded and saved to {tmpfile.name}")
                return tmpfile.name
        except Exception as e:
            print(f"Failed to record audio: {e}")
            return None

    def preprocess_audio(self, input_path):
        normalized_path = "normalized_audio.wav"
        denoised_path = "denoised_audio.wav"
        
        # Normalize Audio
        audio = AudioSegment.from_file(input_path)
        normalized_audio = effects.normalize(audio, headroom=-20.0)
        normalized_audio.export(normalized_path, format="wav")
        print(f"Normalized audio saved to {normalized_path}")

        # Reduce Noise
        data, rate = sf.read(normalized_path)
        reduced_noise = nr.reduce_noise(y=data, sr=rate)
        sf.write(denoised_path, reduced_noise, rate)
        print(f"Noise-reduced audio saved to {denoised_path}")

        return denoised_path
