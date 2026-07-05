import os
from typing import Optional
from app.services.llm.BaseLLM import BaseLLM
from app.services.llm.OpenAIProvider import OpenAIProvider
from app.services.llm.GeminiProvider import GeminiProvider

class LLMFactory:
    @staticmethod
    def get_provider(provider_name: Optional[str] = None) -> BaseLLM:
        """
        Factory method to resolve the active LLM provider.
        Reads default provider from environment variable LLM_PROVIDER ('openai' or 'gemini').
        """
        if not provider_name:
            provider_name = os.getenv("LLM_PROVIDER", "openai").lower()

        if provider_name == "gemini":
            model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
            return GeminiProvider(model=model)
        else:
            model = os.getenv("OPENAI_MODEL", "gpt-4o")
            return OpenAIProvider(model=model)
