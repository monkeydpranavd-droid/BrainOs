import os
import time
import httpx
import logging
from typing import List, Generator, Optional
from app.services.llm.BaseLLM import BaseLLM
from app.services.llm.OpenAIProvider import generate_mock_embedding

logger = logging.getLogger(__name__)

class GeminiProvider(BaseLLM):
    def __init__(self, model: str = "gemini-2.5-flash") -> None:
        self.model = model
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.is_mock = not self.api_key

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if self.is_mock:
            time.sleep(0.5)
            return f"[Simulated Gemini {self.model}] Answer grounded in documentation: Received prompt '{prompt[:60]}...'"

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        contents = []
        if system_prompt:
            contents.append({
                "role": "user",
                "parts": [{"text": f"System Instruction: {system_prompt}"}]
            })
        contents.append({
            "role": "user",
            "parts": [{"text": prompt}]
        })
        
        data = {"contents": contents}
        try:
            resp = httpx.post(url, json=data, timeout=30.0)
            resp.raise_for_status()
            res_json = resp.json()
            return res_json["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            logger.error("Gemini API call failed: %s", e)
            return f"[Gemini Error Fallback] Failed to call real API: {e}"

    def stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        if self.is_mock:
            mock_resp = (
                f"[Simulated Gemini {self.model}]\n\n"
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

        # Real streaming via SSE / Stream endpoint
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:streamGenerateContent?key={self.api_key}"
        contents = []
        if system_prompt:
            contents.append({
                "role": "user",
                "parts": [{"text": f"System Instruction: {system_prompt}"}]
            })
        contents.append({
            "role": "user",
            "parts": [{"text": prompt}]
        })
        
        data = {"contents": contents}
        try:
            with httpx.stream("POST", url, json=data, timeout=30.0) as r:
                r.raise_for_status()
                for line in r.iter_lines():
                    if line.strip():
                        # Parse chunk output from stream
                        try:
                            import json
                            # Google streams JSON arrays or individual JSON segments
                            chunk_data = json.loads(line)
                            # Handle stream JSON arrays or segments
                            text = chunk_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                            if text:
                                yield text
                        except Exception:
                            pass
        except Exception as e:
            logger.error("Gemini Streaming failed: %s", e)
            yield f"[Streaming Error: {e}]"

    def embeddings(self, texts: List[str]) -> List[List[float]]:
        # Returns 1536 size dimensions by default matching default structure
        if self.is_mock:
            return [generate_mock_embedding(t) for t in texts]

        # Call real Gemini embeddings API
        try:
            results = []
            for text in texts:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={self.api_key}"
                data = {
                    "model": "models/text-embedding-004",
                    "content": {"parts": [{"text": text}]}
                }
                resp = httpx.post(url, json=data, timeout=20.0)
                resp.raise_for_status()
                # Gemini text-embedding-004 is 768 dimensions. We pad to 1536 to match OpenAI alignment.
                vec = resp.json()["embedding"]["values"]
                if len(vec) < 1536:
                    vec = vec + [0.0] * (1536 - len(vec))
                results.append(vec[:1536])
            return results
        except Exception as e:
            logger.error("Gemini Embeddings call failed: %s", e)
            return [generate_mock_embedding(t) for t in texts]
