# app/summary_generator.py

from langchain import LLMChain
from langchain.prompts import PromptTemplate

class SummaryGenerator:
    def __init__(self, llm):
        self.llm = llm

    def generate_summary(self, history):
        summary_text = "Conversation History:\n" + "\n".join(
            [f"User: {item['user']}\nAssistant: {item['assistant']}" for item in history]
        )
        prompt_template = PromptTemplate(
            input_variables=["history"],
            template="""
You are an assistant that summarizes conversations.

{history}

Generate a concise summary of the conversation, focusing on the objectives achieved and any unresolved issues.

Summary:
"""
        )
        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        summary = chain.run(history=summary_text)
        return summary.strip()
