# ConvoFlow 💬

ConvoFlow is an AI-powered conversational assistant built with **FastAPI**, **LangChain**, and **Streamlit**, featuring persistent memory, sentiment analysis, TTS audio, and real-time webhook notifications for negative sentiments.

It uses **Google Gemini 2.5 Flash** as the LLM backend and stores conversations in **ChromaDB**. Negative user sentiments automatically trigger **n8n webhooks**.

## Features

* **Conversational AI:** Context-aware responses powered by Google Gemini LLM via LangChain.
* **Persistent Memory:** Stores conversations in ChromaDB with semantic embeddings.
* **Sentiment Analysis:** Detects negative inputs and triggers webhook alerts.
* **Text-to-Speech (TTS):** AI responses played as audio in the browser.
* **Modern Chat UI:** Streamlit frontend with styled chat bubbles, timestamps, and gradient title.
* **Source Documents:** Optionally returns context documents from memory for AI answers.

## Architecture

```
User Input
    ↓
FastAPI /respond endpoint
    ↓
ConvoFlowChain (LangChain ConversationalRetrievalChain)
    ↓
MemoryDB (ChromaDB + embeddings)
    ↓
SentimentAnalyzer
    ↓
Webhook Trigger (n8n)
    ↓
AI Response + Audio
    ↓
Frontend (Streamlit)
```

## Tech Stack

* **Backend:** FastAPI, Python 3.11
* **LLM:** Google Gemini 2.5 Flash
* **LangChain:**
  * LLM wrapper for Gemini
  * Conversational Retrieval Chain for context-aware responses
* **Vector DB:** ChromaDB + SentenceTransformer embeddings (`all-MiniLM-L6-v2`)
* **Frontend:** Streamlit
* **TTS:** gTTS (in-memory, no files saved)
* **Webhook Automation:** n8n for async alerts on negative sentiment
* **Logging:** Python logging module

## Setup

### 1. Clone repository

```cmd
git clone https://github.com/GunaPavan/ConvoFlow.git
cd ConvoFlow
```

### 2. Create virtual environment and install dependencies

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

### 3. Set environment variables

Create a `.env` file in the project root with the following content:

```
GEMINI_API_KEY=your_gemini_api_key_here
N8N_WEBHOOK_URL=http://localhost:5678/webhook-test/your-webhook-id
```

### 4. Run n8n and create webhook

Install n8n globally (if not installed):

```cmd
npm install n8n -g
```

Start n8n:

```cmd
n8n start
```

By default, n8n runs at `http://localhost:5678`.

1. Create a **new workflow** → Add **Webhook** node → Method: POST.
2. Copy the generated webhook URL and use it in `.env` as `N8N_WEBHOOK_URL`.
3. Optionally, add additional nodes after the webhook (e.g., email or Slack notifications).

### 5. Run backend

```cmd
uvicorn src.api.main:app --reload
```

### 6. Run frontend

```cmd
streamlit run src\frontend\app.py
```

## Usage

1. Type your message in the input box.
2. Click **Send**.
3. AI responds with text and plays audio.
4. Negative sentiments trigger n8n webhook notifications.
5. Chat history persists in ChromaDB.

## Project Structure

```
ConvoFlow\
├─ src\
│  ├─ api\
│  │  ├─ main.py
│  │  ├─ routes\
│  │  │  └─ respond.py
│  │  └─ utils\
│  │     └─ helpers.py
│  ├─ core\
│  │  ├─ llm.py
│  │  ├─ langchain_llm.py
│  │  ├─ retriever.py
│  │  ├─ sentiment.py
│  │  ├─ tts.py
│  │  ├─ conversation_chain.py
│  │  
│  ├─ frontend\
│  │  └─ app.py
│  └─ tests\
│     ├─ test_webhook_call.py
│     └─ test_webhook.py
├─ .env
├─ LICENSE
├─ pyproject.toml
├─ requirements.txt
└─ README.md
```

> ✅ Included the `tests\` folder in public repo. It helps run automated tests and verify webhook functionality.

## LangChain Usage Clarification

LangChain is used in **two ways**:

1. **LLM Wrapper:** `GeminiLangChainLLM` wraps Google Gemini LLM for LangChain compatibility.
2. **Conversational Retrieval Chain:** `ConvoFlowChain` retrieves relevant conversation history from `MemoryDB` and feeds it to the LLM for context-aware responses.

This allows **contextual AI responses** while keeping the LLM code clean and modular.

## License

MIT License.