import time
import requests

CHATBOT_URL = "http://localhost:8000/financial-rag-agent"

questions = [
   "What is the most popular stocks now?",
   "Can I buy 10 Apple shares?",
   "What is candle plot?"
]

request_bodies = [{"text": q} for q in questions]

start_time = time.perf_counter()
outputs = [requests.post(CHATBOT_URL, json=data) for data in request_bodies]
end_time = time.perf_counter()

print(f"Run time: {end_time - start_time} seconds")