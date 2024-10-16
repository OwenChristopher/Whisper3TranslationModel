# # app/tts_handler.py

# from TTS.api import TTS

# class TTSHandler:
#     def __init__(self, model_name="tts_models/en/ljspeech/tacotron2-DDC", device="cpu"):
#         self.tts = TTS(model_name=model_name, device=device)

#     def synthesize(self, text, output_path="output.wav"):
#         self.tts.tts_to_file(text=text, file_path=output_path)
#         return output_path


# # app/main.py (Add the following endpoint)

# from fastapi.responses import FileResponse
# from app.tts_handler import TTSHandler

# tts_handler = TTSHandler()

# @app.post("/synthesize")
# def synthesize_text(request: MessageRequest):
#     try:
#         audio_path = tts_handler.synthesize(request.message)
#         return FileResponse(audio_path, media_type="audio/wav", filename="output.wav")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"TTS synthesis failed: {e}")
