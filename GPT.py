import requests
import json
import openai


class GPT:
    def __init__(self):
        self.api_key = 'YOUR_API_KEY'
        self.url = 'https://api.openai.com/v1/chat/completions'

    def communicate(self, messages):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}',
        }

        data = {
            'model': 'gpt-4',
            'messages': messages,
            'max_tokens': 4000,
            'temperature': 0.2,
            'top_p': 0.1,
        }

        response = requests.post(self.url, headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            response_data = response.json()
            print('Response:', response_data['choices'][0]['message']['content'].strip())
            return response_data['choices'][0]['message']['content'].strip()
        else:
            print('Error:', response.status_code)
            print('Details:', response.text)

        return response
