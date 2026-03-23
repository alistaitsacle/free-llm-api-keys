#!/bin/bash
# FreeLLMShare — cURL Examples. Replace YOUR_KEY_HERE with a key from the README.
curl -s https://aiapiv2.pekpik.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_KEY_HERE" \
  -d '{"model":"gpt-5.4","messages":[{"role":"user","content":"Hello!"}]}' | python3 -m json.tool
