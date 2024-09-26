# app/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import tempfile
import uvicorn
from uuid import uuid4
import json

from .models import SessionState
from .audio_handler import AudioHandler
from .transcription_handler import TranscriptionHandler
from .conversation_manager import ConversationManager
from .summary_generator import SummaryGenerator
from .utils import initialize_language_model
from .schemas import ObjectiveRequest, MessageRequest  # Import the new MessageRequest
from .chat_model import LLMChat

app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    session.initialize_chat()  # Initialize LLMChat
    sessions[session_id] = session
    return {"session_id": session_id, "message": "Objective and target language set successfully."}

@app.post("/send_message/{session_id}")
def send_message(session_id: str, request: MessageRequest):
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=400, detail="Invalid session ID.")

    if not session.chat_model:
        session.initialize_chat()

    assistant_response = session.chat_model.send_message(request.message)
    session.add_interaction(user_text=request.message, assistant_response=assistant_response)

    # Check if the conversation is fulfilled based on the assistant's response
    if "fulfilled" in assistant_response.lower() or session.chat_model.history[-1]['type'] == 'SUMMARY':
        session.update_status('fulfilled')

    return {
        "assistant_response": assistant_response,
        "history": json.loads(session.chat_model.get_history_json())
    }


@app.post("/process_audio/{session_id}")
async def process_audio(session_id: str, file: UploadFile = File(...)):
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=400, detail="Invalid session ID.")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
            tmpfile.write(await file.read())
            input_audio_path = tmpfile.name

        audio_handler = AudioHandler(duration=5, sample_rate=16000)
        denoised_audio = audio_handler.preprocess_audio(input_audio_path)

        transcription_handler = TranscriptionHandler()
        user_text = transcription_handler.transcribe(denoised_audio)

        # Use the chat model to get assistant response
        if not session.chat_model:
            session.initialize_chat()
        
        assistant_response = session.chat_model.send_message(user_text)
        session.add_interaction(user_text=user_text, assistant_response=assistant_response)

        os.remove(input_audio_path)
        os.remove(denoised_audio)

        response = {
            "user_text": user_text,
            "assistant_response": assistant_response
        }

        if "fulfilled" in assistant_response.lower() or session.chat_model.history[-1]['type'] == 'SUMMARY':
            session.update_status('fulfilled')
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
