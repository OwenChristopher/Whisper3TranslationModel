# app/language_processor.py

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langdetect import detect, DetectorFactory, LangDetectException

DetectorFactory.seed = 0

class LanguageProcessor:
    def __init__(self, llm):
        self.llm = llm  # Instance of ChatGoogleGenerativeAI or similar

    def detect_language(self, text):
        try:
            language = detect(text)
            print(f"Detected language: {language}")
            return language
        except LangDetectException:
            print("Could not detect language.")
            return None

    def translate_text(self, text, source_lang, target_lang):
        prompt_template = PromptTemplate(
            input_variables=["text", "source_lang", "target_lang"],
            template="""
You are a proficient translator.

Source Language: {source_lang}
Target Language: {target_lang}

Please translate the following text from {source_lang} to {target_lang}:

"{text}"

Translation:
"""
        )
        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        translation = chain.run(text=text, source_lang=source_lang, target_lang=target_lang)
        return translation.strip()
