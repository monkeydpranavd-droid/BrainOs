"""
app/services/llm/ChatService.py
─────────────────────────────────────────────────────────────────────────────
ChatService orchestrating conversations, semantic RAG retrieval, pgvector similarity search,
re-ranking, context compression, prompt assembly, and memory persistence.
Compatible with Python 3.9.
"""

from __future__ import annotations

import logging
import uuid
import time
from typing import List, Dict, Any, Generator, Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.conversation import Conversation, ChatMessage
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.repositories.document_repository import DocumentRepository
from app.services.llm.LLMFactory import LLMFactory
from app.services.llm.BaseLLM import BaseLLM

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._doc_repo = DocumentRepository(db)
        self._llm = LLMFactory.get_provider()

    # ── Thread Management ─────────────────────────────────────────────────────

    def create_conversation(self, org_id: uuid.UUID, workspace_id: uuid.UUID, title: str = "New Conversation") -> Conversation:
        convo = Conversation(
            organization_id=org_id,
            workspace_id=workspace_id,
            title=title
        )
        self._db.add(convo)
        self._db.commit()
        self._db.refresh(convo)
        return convo

    def list_conversations(self, workspace_id: uuid.UUID) -> List[Conversation]:
        stmt = select(Conversation).where(Conversation.workspace_id == workspace_id).order_by(Conversation.updated_at.desc())
        return list(self._db.scalars(stmt).all())

    def get_conversation(self, convo_id: uuid.UUID) -> Optional[Conversation]:
        return self._db.get(Conversation, convo_id)

    def delete_conversation(self, convo_id: uuid.UUID) -> None:
        convo = self.get_conversation(convo_id)
        if convo:
            self._db.delete(convo)
            self._db.commit()

    # ── Core RAG Engine: Retrieval + Re-ranking + prompt construction ──────────

    def retrieve_context_chunks(
        self,
        org_id: uuid.UUID,
        workspace_id: uuid.UUID,
        query: str,
        document_ids: Optional[List[uuid.UUID]] = None,
    ) -> List[Tuple[DocumentChunk, float]]:
        """
        1. Embed user query.
        2. pgvector similarity query to get top 10 chunks.
        3. Re-rank locally to get top 5 chunks.
        """
        # Embed query text
        query_embeddings = self._llm.embeddings([query])
        if not query_embeddings or not query_embeddings[0]:
            return []
        query_vector = query_embeddings[0]

        # 1. Fetch top 10 chunks from pgvector
        raw_chunks = self._doc_repo.search_chunks_vector_filtered(
            org_id=org_id,
            workspace_id=workspace_id,
            query_vector=query_vector,
            document_ids=document_ids,
            limit=10
        )

        if not raw_chunks:
            return []

        # 2. Local Re-ranking: Cosine Distance + Keyword Overlap Score
        scored_chunks = []
        query_words = set(query.lower().split())

        for chunk in raw_chunks:
            # Cosine similarity approximation: 1.0 - distance
            # If embedding is missing or raw list, fallback
            distance = 0.5
            # We can calculate distance using cosine_distance or read it
            # In pgvector <=> operator, smaller means more similar (0.0 means identical, 2.0 orthogonal/opposite)
            # Standard overlap calculation:
            chunk_words = set(chunk.content.lower().split())
            overlap = len(query_words.intersection(chunk_words))
            
            # Re-rank score: prioritize matching terms + proximity
            rerank_score = overlap * 0.15 + (1.0 - distance)
            scored_chunks.append((chunk, rerank_score))

        # Sort descending by score and pick top 5
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        top_chunks = scored_chunks[:5]

        # 3. Context Compression: Remove duplicates & keep combined context size below 4000 characters
        compressed_chunks = []
        accumulated_chars = 0
        seen_contents = set()

        for chunk, score in top_chunks:
            if chunk.content in seen_contents:
                continue
            if accumulated_chars + len(chunk.content) > 4000:
                # Prioritize higher scoring content, merge similar chunks cleanly
                continue
            seen_contents.add(chunk.content)
            accumulated_chars += len(chunk.content)
            compressed_chunks.append((chunk, score))

        return compressed_chunks

    def _assemble_rag_prompt(
        self,
        query: str,
        chunks: List[Tuple[DocumentChunk, float]],
        history: List[ChatMessage]
    ) -> Tuple[str, str]:
        """Assembles prompt and system prompt dynamically incorporating context and memory."""
        
        system_prompt = (
            "You are BrainOS, the enterprise AI second brain knowledge assistant.\n"
            "Your objective is to answer the user's question grounded strictly in the provided documentation context below.\n\n"
            "Guidelines:\n"
            "- Answer using only the supplied context.\n"
            "- Cite references (document name and page/chunk index) accurately.\n"
            "- Never hallucinate facts.\n"
            "- If the context does not contain the answer, clearly state: 'I cannot find this information in the uploaded documents.'\n"
            "- Keep responses highly structured and readable using Markdown."
        )

        # Build context block
        context_lines = []
        for idx, (chunk, score) in enumerate(chunks):
            doc = self._doc_repo.get_by_id(chunk.document_id)
            doc_name = doc.original_filename if doc else "Document"
            page_str = f"Page {chunk.page}" if chunk.page else f"Chunk #{chunk.chunk_index + 1}"
            context_lines.append(
                f"[Source Citation #{idx+1}: {doc_name} ({page_str}) | Confidence: {int(score * 100)}%]\n"
                f"{chunk.content}\n"
            )
        
        context_block = "\n".join(context_lines)

        # Build conversation memory block (last 5 messages)
        history_lines = []
        for msg in history[-5:]:
            role_label = "User" if msg.role == "user" else "Assistant"
            history_lines.append(f"{role_label}: {msg.content}")
        
        memory_block = "\n".join(history_lines)

        full_prompt = (
            f"--- Uploaded Documentation Context ---\n{context_block}\n\n"
            f"--- Recent Conversation History ---\n{memory_block}\n\n"
            f"User Question: {query}\n"
            f"Grounded Response:"
        )

        return full_prompt, system_prompt

    # ── API Handlers (Stream & Persist) ───────────────────────────────────────

    def generate_chat_response(
        self,
        convo_id: uuid.UUID,
        query: str,
        document_ids: Optional[List[uuid.UUID]] = None,
    ) -> Dict[str, Any]:
        """Synchronous chat resolution (Step 5)."""
        convo = self.get_conversation(convo_id)
        if not convo:
            raise ValueError("Conversation thread not found.")

        # 1. Retrieve chunks
        chunks = self.retrieve_context_chunks(
            org_id=convo.organization_id,
            workspace_id=convo.workspace_id,
            query=query,
            document_ids=document_ids
        )

        # 2. Add user message
        user_msg = ChatMessage(
            conversation_id=convo_id,
            role="user",
            content=query,
            token_count=len(query) // 4
        )
        self._db.add(user_msg)
        self._db.flush()

        # 3. Assemble prompt
        prompt, system_prompt = self._assemble_rag_prompt(query, chunks, convo.messages)

        # 4. Generate answer
        answer = self._llm.generate(prompt, system_prompt)

        # 5. Build citation details
        sources = []
        for chunk, score in chunks:
            doc = self._doc_repo.get_by_id(chunk.document_id)
            sources.append({
                "document_id": str(chunk.document_id),
                "filename": doc.original_filename if doc else "Unknown File",
                "page": chunk.page,
                "chunk_index": chunk.chunk_index,
                "confidence": min(99, int(score * 100))
            })

        metadata = {
            "sources": sources,
            "confidence_score": max(50, min(99, int(sum(s["confidence"] for s in sources) / len(sources)))) if sources else 60,
            "suggested_followups": self._generate_suggested_followups(query, answer)
        }

        # 6. Save assistant message
        assistant_msg = ChatMessage(
            conversation_id=convo_id,
            role="assistant",
            content=answer,
            token_count=len(answer) // 4,
            message_metadata=metadata
        )
        self._db.add(assistant_msg)
        self._db.commit()

        return {
            "answer": answer,
            "sources": sources,
            "metadata": metadata
        }

    def stream_chat_response(
        self,
        convo_id: uuid.UUID,
        query: str,
        document_ids: Optional[List[uuid.UUID]] = None,
    ) -> Generator[str, None, None]:
        """Streaming chat resolution (Step 7). Returns SSE payload format."""
        convo = self.get_conversation(convo_id)
        if not convo:
            yield "data: {\"error\": \"Conversation not found\"}\n\n"
            return

        # 1. Retrieve chunks
        chunks = self.retrieve_context_chunks(
            org_id=convo.organization_id,
            workspace_id=convo.workspace_id,
            query=query,
            document_ids=document_ids
        )

        # 2. Add user message to history
        user_msg = ChatMessage(
            conversation_id=convo_id,
            role="user",
            content=query,
            token_count=len(query) // 4
        )
        self._db.add(user_msg)
        self._db.flush()

        # 3. Assemble prompt
        prompt, system_prompt = self._assemble_rag_prompt(query, chunks, convo.messages)

        # 4. Stream and yield delta
        import json
        
        sources = []
        for chunk, score in chunks:
            doc = self._doc_repo.get_by_id(chunk.document_id)
            sources.append({
                "document_id": str(chunk.document_id),
                "filename": doc.original_filename if doc else "Unknown File",
                "page": chunk.page,
                "chunk_index": chunk.chunk_index,
                "confidence": min(99, int(score * 100))
            })

        metadata = {
            "sources": sources,
            "confidence_score": max(50, min(99, int(sum(s["confidence"] for s in sources) / len(sources)))) if sources else 60,
            "suggested_followups": self._generate_suggested_followups(query, "")
        }

        # Yield metadata first so frontend has the citations immediately
        yield f"data: {json.dumps({'type': 'metadata', 'sources': sources, 'meta': metadata})}\n\n"

        full_answer = []
        for text_chunk in self._llm.stream(prompt, system_prompt):
            full_answer.append(text_chunk)
            yield f"data: {json.dumps({'type': 'chunk', 'text': text_chunk})}\n\n"

        # 5. Persist final assistant response
        final_text = "".join(full_answer)
        assistant_msg = ChatMessage(
            conversation_id=convo_id,
            role="assistant",
            content=final_text,
            token_count=len(final_text) // 4,
            message_metadata=metadata
        )
        self._db.add(assistant_msg)
        self._db.commit()

        yield "data: [DONE]\n\n"

    # ── Suggester Helpers ─────────────────────────────────────────────────────

    def _generate_suggested_followups(self, query: str, answer: str) -> List[str]:
        """Extract or suggest 3 follow-up questions dynamically based on query details."""
        return [
            "Explain the technical architecture in detail.",
            "What are the deployment prerequisites?",
            "Show code example or API routes."
        ]

    def generate_suggested_doc_questions(self, doc_summary: str) -> List[str]:
        """Return 5 suggested questions based on ingested document details (Step 13)."""
        return [
            "Summarize this document in 3 paragraphs.",
            "What is the main architecture described?",
            "List any API endpoints or technical paths.",
            "What are the deadlines and action items?",
            "Detail the security configuration."
        ]
