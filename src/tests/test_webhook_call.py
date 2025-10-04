import requests

# Replace with your actual webhook URL
WEBHOOK_URL = "http://localhost:5678/webhook-test/bd2bb1e8-036d-42e6-8f5d-2a7eb16531c1"

# Example payload (simulate negative sentiment)
payload = {
    "text": "I hate this product!",
    "user": "TestUser"
}

response = requests.post(WEBHOOK_URL, json=payload)

print("Status code:", response.status_code)
print("Response:", response.text)
