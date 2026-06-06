"""
FreeLLMShare — Compare responses from different models.

This script demonstrates how to compare responses from multiple AI models using a free API gateway.
It is designed for easy testing and comparison.

Dependencies:
- openai: Install using `pip install openai`.

Configuration:
- API Key: Replace 'YOUR_KEY_HERE' with a valid free API key from the repository.
  Example: api_key="your_actual_key"

Usage:
- Run the script: `python multi_model.py`
- The script will query each model in the list and print the responses.

Expected Output:
- For each model, it prints a separator line, the model name, and the response.
- If successful, the response is printed; otherwise, an error message is shown.

Error Handling:
- Common errors include invalid API key, network issues, or model unavailability.
- The script catches general exceptions and prints error messages.
- Ensure the API key is correct and the endpoint is accessible.
"""
from openai import OpenAI

client = OpenAI(base_url="https://aiapiv2.pekpik.com/v1", api_key="YOUR_KEY_HERE")
models = ["gpt-5.5", "claude-sonnet-4-6", "deepseek-chat", "mistral-medium-latest"]
question = "Explain quantum computing in one paragraph."

for model in models:
    print(f"\n{'='*50}\n{model}\n{'='*50}")
    try:
        r = client.chat.completions.create(model=model, messages=[{"role": "user", "content": question}])
        print(r.choices[0].message.content)
    except Exception as e:
        print(f"Error: {e}")
