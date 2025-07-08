import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

class GeminiChatBot:
    def __init__(self, model="gemini-2.0-flash", history_file="history.txt"):
        load_dotenv()
        self.api_key = os.getenv("GEMINI_API_KEY")

        self.temperature = 0.7
        self.top_p = 0.9
        self.top_k = 40
        self.max_output_tokens = 10000

        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        self.headers = {
            'Content-Type': 'application/json',
            'X-goog-api-key': self.api_key
        }

        self.chat_history = []
        self.history_file = history_file
        
        with open(self.history_file, "a", encoding="utf-8") as f:
            f.write("Gemini Chat History\n")
            f.write("-" * 50 + "\n")

        self.print_intro()

    def print_intro(self):
        print("Gemini Chat - Type 'exit' to quit")
        print(f"Settings: temp={self.temperature}, top_p={self.top_p}, top_k={self.top_k}, max_tokens={self.max_output_tokens}")
        print("-" * 50)

    def send_message(self, message):
        self.chat_history.append({"role": "user", "parts": [{"text": message}]})
        
        payload = {
            "contents": self.chat_history,
            "generationConfig": {
                "temperature": self.temperature,
                "topP": self.top_p,
                "topK": self.top_k,
                "maxOutputTokens": self.max_output_tokens
            }
        }

        response = requests.post(self.url, headers=self.headers, json=payload)

        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            return "API Error"

        reply = response.json()['candidates'][0]['content']['parts'][0]['text']
        self.chat_history.append({"role": "model", "parts": [{"text": reply}]})
        return reply

    def chat_loop(self):
        while True:
            user_input = input("\nYou: ")

            if user_input.lower() == "exit":
                print(f"Conversation saved to {self.history_file}")
                break

            response = self.send_message(user_input)
            print("Gemini:", response)

            with open(self.history_file, "a", encoding="utf-8") as f:
                f.write(f"You: {user_input}\n")
                f.write(f"Gemini: {response}\n\n")


if __name__ == "__main__":
    bot = GeminiChatBot()
    bot.chat_loop()