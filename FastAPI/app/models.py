# app/models.py

class SessionState:
    def __init__(self, objective, target_language):
        self.objective = objective
        self.target_language = target_language
        self.history = []  # List of dictionaries: {'user': ..., 'assistant': ...}
        self.current_status = 'ongoing'  # Can be 'ongoing', 'fulfilled', 'failed'

    def add_interaction(self, user_text, assistant_response):
        self.history.append({"user": user_text, "assistant": assistant_response})

    def update_status(self, status):
        self.current_status = status

    def get_summary(self):
        return "\n".join([f"User: {item['user']}\nAssistant: {item['assistant']}" for item in self.history])
