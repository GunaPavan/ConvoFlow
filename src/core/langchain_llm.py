# src/core/langchain_llm.py
from langchain.llms.base import LLM as BaseLLM
from core.llm import LLM
from pydantic import PrivateAttr

class GeminiLangChainLLM(BaseLLM):
    """LangChain-compatible wrapper around your existing Gemini LLM."""
    
    _llm: LLM = PrivateAttr()  # tell Pydantic this is a private attribute

    def __init__(self):
        super().__init__()
        self._llm = LLM()  # use the class from llm.py

    @property
    def _llm_type(self) -> str:
        return "gemini-2.5-flash"

    def _call(self, prompt: str, stop=None) -> str:
        """LangChain calls this method to get a response."""
        return self._llm.respond(prompt)
