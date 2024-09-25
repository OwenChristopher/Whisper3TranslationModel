# app/main.py

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import tempfile
import uvicorn
from uuid import uuid4

# Import your classes and functions from the modules
from .models import SessionState
from .audio_handler import AudioHandler
from .transcription_handler import TranscriptionHandler
from .conversation_manager import ConversationManager
from .summary_generator import SummaryGenerator
from .utils import initialize_language_model
from .schemas import ObjectiveRequest


app = FastAPI()

# Allow CORS (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend's origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the language model once at startup
@app.on_event("startup")
def startup_event():
    global llm
    llm = initialize_language_model()

# In-memory session storage (use a database in production)
sessions = {}

@app.post("/set_objective")
def set_objective(request: ObjectiveRequest):
    session_id = str(uuid4())
    session = SessionState(objective=request.objective, target_language=request.target_language)
    sessions[session_id] = session
    return {"session_id": session_id, "message": "Objective and target language set successfully."}

@app.post("/process_audio/{session_id}")
async def process_audio(session_id: str, file: UploadFile = File(...)):
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=400, detail="Invalid session ID.")

    # Save the uploaded audio file to a temporary location
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
            tmpfile.write(await file.read())
            input_audio_path = tmpfile.name
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save audio file: {e}")

    try:
        # Preprocess Audio
        audio_handler = AudioHandler(duration=5, sample_rate=16000)
        denoised_audio = audio_handler.preprocess_audio(input_audio_path)

        # Transcribe Audio
        transcription_handler = TranscriptionHandler()
        user_text = transcription_handler.transcribe(denoised_audio)

        # Manage Conversation
        conversation_manager = ConversationManager(llm=llm, session=session)
        assistant_response, fulfilled = conversation_manager.manage_conversation(user_text)

        # Cleanup temporary audio files
        os.remove(input_audio_path)
        os.remove(denoised_audio)

        response = {
            "user_text": user_text,
            "assistant_response": assistant_response,
            "fulfilled": fulfilled
        }

        if fulfilled:
            summary_generator = SummaryGenerator(llm=llm)
            summary = summary_generator.generate_summary(session.history)
            response["summary"] = summary

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing audio: {e}")

@app.get("/summary/{session_id}")
def get_summary(session_id: str):
    session = sessions.get(session_id)
    if not session or not session.history:
        raise HTTPException(status_code=400, detail="No conversation history available.")

    summary_generator = SummaryGenerator(llm=llm)
    summary = summary_generator.generate_summary(session.history)
    return {"summary": summary}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
