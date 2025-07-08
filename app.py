import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')


temperature = 0.7
top_p = 0.9
top_k = 40
max_output_tokens = 2048

url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

headers = {
    'Content-Type': 'application/json',
    'X-goog-api-key': api_key
}

def send_message(message):
    payload = {
        "contents": [{"parts": [{"text": message}]}],
        "generationConfig": {
            "temperature": temperature,
            "topP": top_p,
            "topK": top_k,
            "maxOutputTokens": max_output_tokens
        }
    }
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return "API Error"
    data = response.json()
    return data['candidates'][0]['content']['parts'][0]['text']

print("Gemini Chat - Type 'exit' to quit")
print(f"Settings: temp={temperature}, top_p={top_p}, top_k={top_k}, max_tokens={max_output_tokens}")
print("-" * 50)

while True:
    user_input = input("\nYou: ")
    
    if user_input.lower() == 'exit':
        break
    
    print("Gemini:", send_message(user_input))