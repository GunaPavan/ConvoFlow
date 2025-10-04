from dotenv import load_dotenv
load_dotenv()  # <- this is necessary

import os
import requests

WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")
if not WEBHOOK_URL:
    raise RuntimeError(
        "N8N_WEBHOOK_URL not set! Please add it to your .env file."
    )

payload = { "text": "I hate this product!", "user": "TestUser" }

def test_webhook_call():
    response = requests.post(WEBHOOK_URL, json=payload)
    assert response.status_code == 200
