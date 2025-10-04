# src/core/llm.py
import os
from google import genai

class LLM:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY not set! Please add it to your .env file."
            )
        self.client = genai.Client(api_key=api_key)

    def respond(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
