from abc import ABC, abstractmethod
from typing import List, Generator, Optional

class BaseLLM(ABC):
    """
    Abstract Base Class defining the unified interface for LLM providers.
    All models (OpenAI, Gemini, etc.) must implement these methods.
    """

    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Synchronously generate complete text response."""
        pass

    @abstractmethod
    def stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        """Stream response chunk-by-chunk."""
        pass

    @abstractmethod
    def embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings vectors for a batch of input texts."""
        pass
