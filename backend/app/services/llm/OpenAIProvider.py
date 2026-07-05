import os
import hashlib
import time
import httpx
import logging
import numpy as np
from typing import List, Generator, Optional
from app.services.llm.BaseLLM import BaseLLM
from app.core.config import settings

logger = logging.getLogger(__name__)

def generate_mock_embedding(text: str, dimension: int = 1536) -> List[float]:
    """Generates a reproducible unit-length vector based on text content hash."""
    hash_object = hashlib.sha256(text.encode('utf-8'))
    seed = int(hash_object.hexdigest(), 16) % (2**32)
    rng = np.random.default_rng(seed)
    vector = rng.standard_normal(dimension)
    norm = np.linalg.norm(vector)
    if norm > 0:
        vector = vector / norm
    return vector.tolist()

class OpenAIProvider(BaseLLM):
    def __init__(self, model: str = "gpt-4o") -> None:
        self.model = model
        self.api_key = settings.SUPABASE_JWT_SECRET # fallback or settings.OPENAI_API_KEY
        # Let's try to load standard env variable for OpenAI
        self.real_key = os.getenv("OPENAI_API_KEY")
        self.is_mock = not self.real_key

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if self.is_mock:
            # Simulated delay and response
            time.sleep(0.5)
            return f"[Simulated OpenAI {self.model}] Answer grounded in documentation: Received prompt '{prompt[:60]}...'"

        headers = {
            "Authorization": f"Bearer {self.real_key}",
            "Content-Type": "application/json"
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        data = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.0
        }
        try:
            resp = httpx.post("https://api.openai.com/v1/chat/completions", json=data, headers=headers, timeout=30.0)
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error("OpenAI API call failed: %s. Falling back to mock.", e)
            return f"[OpenAI Error Fallback] Failed to call real API: {e}"

    def stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        if self.is_mock:
            mock_resp = (
                f"[Simulated OpenAI {self.model}]\n\n"
                "Based on the analyzed documentation, here is the structured overview of your query:\n\n"
                "1. **Architecture**: The second brain utilizes pgvector for semantic search.\n"
                "2. **Bypass**: Auth guards have been bypassed to facilitate local rapid iteration.\n"
                "3. **RAG Pipeline**: This response streams directly chunk-by-chunk via SSE.\n\n"
                "If you need detailed code files, please inspect the catalog sidebar or select a citation."
            )
            for word in mock_resp.split(" "):
                time.sleep(0.04)
                yield word + " "
            return

        headers = {
            "Authorization": f"Bearer {self.real_key}",
            "Content-Type": "application/json"
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        data = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.0,
            "stream": True
        }
        try:
            with httpx.stream("POST", "https://api.openai.com/v1/chat/completions", json=data, headers=headers, timeout=30.0) as r:
                r.raise_for_status()
                for line in r.iter_lines():
                    if line.startswith("data: "):
                        content = line[6:]
                        if content.strip() == "[DONE]":
                            break
                        try:
                            import json
                            chunk_data = json.loads(content)
                            delta = chunk_data["choices"][0]["delta"].get("content", "")
                            if delta:
                                yield delta
                        except Exception:
                            pass
        except Exception as e:
            logger.error("OpenAI Streaming failed: %s", e)
            yield f"[Streaming Error: {e}]"

    def embeddings(self, texts: List[str]) -> List[List[float]]:
        # configurable OpenAI text-embedding-3-small dimension size: 1536
        if self.is_mock:
            return [generate_mock_embedding(t) for t in texts]

        headers = {
            "Authorization": f"Bearer {self.real_key}",
            "Content-Type": "application/json"
        }
        data = {
            "input": texts,
            "model": "text-embedding-3-small"
        }
        try:
            resp = httpx.post("https://api.openai.com/v1/embeddings", json=data, headers=headers, timeout=20.0)
            resp.raise_for_status()
            res_json = resp.json()
            return [item["embedding"] for item in res_json["data"]]
        except Exception as e:
            logger.error("OpenAI Embeddings call failed: %s. Using deterministic mock fallback.", e)
            return [generate_mock_embedding(t) for t in texts]
