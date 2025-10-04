# src/api/routes/respond.py
from fastapi import APIRouter, Form
from core.sentiment import SentimentAnalyzer
from core.retriever import MemoryDB
from core.conversation_chain import ConvoFlowChain
from api.utils.helpers import logger

router = APIRouter()

# Initialize the conversational chain
convo_chain = ConvoFlowChain()

# Existing sentiment analyzer & memory
sentiment_analyzer = SentimentAnalyzer()
memory_db = MemoryDB()

@router.post("/respond")
async def respond(user_input: str = Form(...)):
    try:
        # 1. Ask the conversational chain (LangChain handles memory retrieval)
        result = convo_chain.ask(user_input)
        ai_response = result.get("answer", "[Error]")
        source_docs = result.get("source_documents", [])

        # 2. Analyze sentiment
        sentiment_label, sentiment_score = sentiment_analyzer.analyze(user_input)

        # 3. Save conversation to MemoryDB (handles async webhook internally)
        memory_db.save_conversation(user_input, ai_response, sentiment_label, sentiment_score)

        return {
            "ai_response": ai_response,
            "sentiment": sentiment_label,
            "score": sentiment_score,
            "source_docs": [doc.page_content for doc in source_docs]  # simplified content
        }

    except Exception as e:
        logger.error(f"Error in /respond endpoint: {e}", exc_info=True)
        return {"error": "Failed to process request"}
