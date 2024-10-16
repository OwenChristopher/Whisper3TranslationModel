# app/utils.py

from dotenv import load_dotenv

load_dotenv()

LANGUAGE_CODE_MAP = {
    'english': 'en',
    'spanish': 'es',
    'french': 'fr',
    'chinese': 'cn',
    'indonesian': 'in',
    'russian':'rs'
    # Add more mappings as needed
}

def get_user_settings():
    print("Welcome to the Translation App!")
    objective = input("Please enter your objective (e.g., Schedule a meeting): ").strip()
    target_language_input = input("Please enter the target language (e.g., English, Spanish): ").strip().lower()
    target_language = LANGUAGE_CODE_MAP.get(target_language_input, 'en')  # Default to English
    return objective, target_language

def initialize_language_model():
    from langchain_google_genai import ChatGoogleGenerativeAI
    import os

    model = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0
    )
    return model
