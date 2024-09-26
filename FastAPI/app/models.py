# app/models.py
from .chat_model import LLMChat  # Import the LLMChat class

class SessionState:
    def __init__(self, objective, target_language):
        self.objective = objective
        self.target_language = target_language
        self.history = []  # List of dictionaries: {'user': ..., 'assistant': ...}
        self.current_status = 'ongoing'  # Can be 'ongoing', 'fulfilled', 'failed'
        self.chat_model = None  # Instance of LLMChat

    def initialize_chat(self):
        """
        Initializes the LLMChat instance with the session's objective and target language.
        """
        self.chat_model = LLMChat(
            user_language='English',  # You can modify this based on user settings
            target_language=self.target_language,
            initial_message=self.objective
        )

    def add_interaction(self, user_text, assistant_response):
        self.history.append({"user": user_text, "assistant": assistant_response})

    def update_status(self, status):
        self.current_status = status

    def get_summary(self):
        return "\n".join([f"User: {item['user']}\nAssistant: {item['assistant']}" for item in self.history])
