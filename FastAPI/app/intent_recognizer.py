# app/intent_recognizer.py

from langchain import LLMChain
from langchain.prompts import PromptTemplate

class IntentRecognizer:
    def __init__(self, llm):
        self.llm = llm

    def recognize_intent(self, text):
        prompt_template = PromptTemplate(
            input_variables=["text"],
            template="""
You are an assistant that extracts the user's intent from their input.

User Input: "{text}"

Determine the user's intent and extract relevant information.

Intent and Information:
"""
        )
        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        response = chain.run(text=text)
        return response.strip()
