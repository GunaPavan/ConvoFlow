# src/core/retriever.py
import os
import uuid
import logging
from datetime import datetime
import asyncio
import httpx

from sentence_transformers import SentenceTransformer
from chromadb import Settings, Client
from langchain_community.vectorstores import Chroma  # updated import
from langchain.embeddings.base import Embeddings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class SentenceTransformerEmbeddings(Embeddings):
    """LangChain wrapper around SentenceTransformer."""
    def __init__(self, model):
        self.model = model

    def embed_documents(self, texts):
        # Ensure input is a list
        if isinstance(texts, str):
            texts = [texts]
        return [self.model.encode(text).tolist() for text in texts]

    def embed_query(self, text):
        return self.model.encode(text).tolist()


class MemoryDB:
    def __init__(self, n8n_webhook_url: str = None):
        # Persistent ChromaDB client
        self.client = Client(
            Settings(
                chroma_db_impl=None,
                persist_directory="src/storage/chroma",
                is_persistent=True,
            )
        )

        # SentenceTransformer embeddings
        self.embed_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.langchain_embeddings = SentenceTransformerEmbeddings(self.embed_model)

        # LangChain vectorstore wrapper
        self.vectorstore = Chroma(
            collection_name="convoflow_memory",
            persist_directory="src/storage/chroma",
            embedding_function=self.langchain_embeddings  # pass object, not method
        )

        # Webhook URL
        self.n8n_webhook_url = n8n_webhook_url or os.getenv(
            "N8N_WEBHOOK_URL", "http://localhost:5678/webhook-test/bd2bb1e8-036d-42e6-8f5d-2a7eb16531c1"
        )

        # Sentiment triggers
        self.trigger_sentiments = {"negative", "very negative"}

    def save_conversation(self, user_text: str, ai_text: str, sentiment_label: str, score: float):
        """Save conversation to ChromaDB and LangChain vectorstore, trigger webhook if needed."""
        doc_id = str(uuid.uuid4())
        metadata = {
            "sentiment": sentiment_label.lower(),
            "score": score,
            "timestamp": datetime.utcnow().isoformat(),
        }
        content = f"{user_text}\n{ai_text}"

        # Save in LangChain/Chroma
        self.vectorstore.add_texts(
            texts=[content],
            metadatas=[metadata],
            ids=[doc_id]
        )

        # Trigger webhook if negative
        if sentiment_label.lower() in self.trigger_sentiments:
            asyncio.create_task(self._send_webhook_async(user_text, ai_text, metadata))

    async def _send_webhook_async(self, user_text: str, ai_text: str, metadata: dict):
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                payload = {
                    "user_text": user_text,
                    "ai_text": ai_text,
                    "metadata": metadata,
                }
                response = await client.post(self.n8n_webhook_url, json=payload)
                response.raise_for_status()
                logger.info("Webhook sent successfully: %s", response.status_code)
            except Exception as e:
                logger.error("Failed to send webhook: %s", e)

    def get_all_conversations(self):
        """Retrieve all conversations from ChromaDB/Vectorstore."""
        return self.vectorstore._collection.get(
            include=["documents", "metadatas", "embeddings"]
        )
