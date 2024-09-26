# app/schemas.py
from pydantic import BaseModel

class ObjectiveRequest(BaseModel):
    objective: str
    target_language: str

class MessageRequest(BaseModel):
    message: str
