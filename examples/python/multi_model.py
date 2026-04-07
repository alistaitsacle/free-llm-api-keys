"""FreeLLMShare — Compare responses from different models. Usage: pip install openai && python multi_model.py"""
from openai import OpenAI

client = OpenAI(base_url="https://aiapiv2.pekpik.com/v1", api_key="YOUR_KEY_HERE")
models = ["gpt-5.4", "claude-sonnet-4-6", "deepseek-chat", "mistral-medium-latest"]
question = "Explain quantum computing in one paragraph."

for model in models:
    print(f"\n{'='*50}\n{model}\n{'='*50}")
    try:
        r = client.chat.completions.create(model=model, messages=[{"role": "user", "content": question}])
        print(r.choices[0].message.content)
    except Exception as e:
        print(f"Error: {e}")
