# src/tests/test_webhook.py
import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from core.retriever import MemoryDB

@pytest.fixture
def memory_db():
    """Initialize a temporary MemoryDB for testing with mocked N8N_WEBHOOK_URL."""
    with patch.dict("os.environ", {"N8N_WEBHOOK_URL": "http://localhost:5678/webhook-test/mock"}):
        db = MemoryDB()
        yield db

@pytest.mark.asyncio
async def test_negative_webhook(memory_db):
    """
    Test that a negative sentiment triggers the n8n webhook.
    """
    # Patch the _send_webhook_async method to prevent actual HTTP requests
    with patch.object(memory_db, "_send_webhook_async", new_callable=AsyncMock) as mock_webhook:
        memory_db.save_conversation(
            user_text="I feel terrible today",
            ai_text="I'm here to listen",
            sentiment_label="negative",
            score=0.1
        )

        # Allow async task to run
        await asyncio.sleep(0.1)

        # Assert that the webhook method was called
        mock_webhook.assert_called_once()
