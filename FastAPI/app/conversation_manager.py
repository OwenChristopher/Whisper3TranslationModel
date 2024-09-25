from langchain import LLMChain
from langchain.prompts import PromptTemplate
from .intent_recognizer import IntentRecognizer
from .language_processor import LanguageProcessor


class ConversationManager:
    def __init__(self, llm, session):
        self.llm = llm
        self.session = session
        self.intent_recognizer = IntentRecognizer(llm)
        self.language_processor = LanguageProcessor(llm)

    def evaluate_objective(self, user_text, assistant_response):
        # Define how to evaluate if the objective is met
        # This could be based on keywords, specific responses, or a more complex analysis
        # For simplicity, let's assume if the assistant confirms the objective, it's fulfilled
        if any(keyword in assistant_response.lower() for keyword in ["completed", "achieved", "done"]):
            self.session.update_status('fulfilled')
            return True
        return False

    def generate_response(self, translated_text):
        prompt_template = PromptTemplate(
            input_variables=["translated_text", "objective"],
            template="""
You are an assistant tasked with helping the user achieve their objective.

Objective: {objective}

User Input: "{translated_text}"

Generate a response that moves towards achieving the user's objective.
"""
        )
        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        response = chain.run(translated_text=translated_text, objective=self.session.objective)
        return response.strip()

    def manage_conversation(self, user_text):
        # Detect language
        source_lang = self.language_processor.detect_language(user_text)
        if not source_lang:
            return "Sorry, I couldn't detect the language of your input.", False

        # Translate to target language
        translated_text = self.language_processor.translate_text(user_text, source_lang, self.session.target_language)
        print(f"Translated Text: {translated_text}")

        # Recognize intent (if needed)
        intent_info = self.intent_recognizer.recognize_intent(translated_text)
        print(f"Recognized Intent: {intent_info}")

        # Generate assistant response
        assistant_response = self.generate_response(translated_text)
        print(f"Assistant Response: {assistant_response}")

        # Optionally, translate assistant response back to user's language
        final_response = self.language_processor.translate_text(assistant_response, self.session.target_language, source_lang)
        print(f"Final Response (Translated Back): {final_response}")

        # Add to session history
        self.session.add_interaction(user_text, final_response)

        # Evaluate if objective is met
        if self.evaluate_objective(user_text, assistant_response):
            return final_response, True  # Objective fulfilled
        else:
            return final_response, False  # Continue conversation