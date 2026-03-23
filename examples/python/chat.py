"""FreeLLMShare — Basic Chat Example. Usage: pip install openai && python chat.py"""
from openai import OpenAI

client = OpenAI(base_url="https://aiapiv2.pekpik.com/v1", api_key="YOUR_KEY_HERE")
response = client.chat.completions.create(
    model="gpt-5.4",
    messages=[{"role": "user", "content": "Hello!"}],
)
print(response.choices[0].message.content)
