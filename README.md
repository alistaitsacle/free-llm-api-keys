<!--
  SEO: free llm api key, free gpt api key, free claude api key, free deepseek api,
  free ai api, free openai api key, free gemini api key, free grok api key,
  free llm api, openai compatible api, multi model api gateway
-->

<div align="center">

<img src="./assets/banner.jpg" alt="Free LLM API Keys — GPT-5.4, Claude, DeepSeek, Gemini, Grok, 90+ Models" width="100%">

<br>

The easiest way to access LLM APIs for free — no credit card, no registration.
<br>
Copy a key from the table below, paste it into your app, and start building.

<br>

[![Stars](https://img.shields.io/github/stars/alistaitsacle/free-llm-api-keys?style=for-the-badge&logo=github)](https://github.com/alistaitsacle/free-llm-api-keys/stargazers)
[![Last Commit](https://img.shields.io/github/last-commit/alistaitsacle/free-llm-api-keys?style=for-the-badge)](https://github.com/alistaitsacle/free-llm-api-keys/commits)
[![Keys](https://img.shields.io/badge/Available_Keys-5-brightgreen?style=for-the-badge)]()
[![Models](https://img.shields.io/badge/Models-90+-blue?style=for-the-badge)]()

**⭐ Star this repo = more free keys for everyone**

[English](./README.md) | [中文](./README_CN.md) | [日本語](./README_JA.md) | [한국어](./README_KO.md) | [Español](./README_ES.md) | [Português](./README_PT.md)

</div>

---

<div align="center">

🧪 **[Try it in the Playground →](https://alistaitsacle.github.io/free-llm-api-keys/)** — paste a key, chat with 90+ models in your browser, no install

</div>

---

## 💡 Why This Project?

AI is changing everything, but most APIs are locked behind credit cards and paywalls. Not everyone has access — especially students, hobbyists, and developers in regions where these services aren't available.

I use LLM APIs heavily in my own work. I have spare capacity that would otherwise go to waste. So I decided to share it — free keys, no strings attached, updated daily.

**No credit card. No registration. Just copy, paste, and build.**

---

## 💼 Need higher availability?

For production-grade LLM keys, contact **alistaitscale@gmail.com**.

---

## 📋 Available Keys

> ⏰ Last updated: 2026-04-29 18:52 (UTC+8)
>
> All keys are API tokens compatible with **OpenAI SDK** — use them with any tool that supports custom OpenAI endpoints.
> Keys are refreshed **3-5 times daily**. Each key has a budget ($20-$100) and expires in 24-48 hours.
>
> ⚠️ **Note:** Keys are shared publicly. Budget may already be consumed by other users. If a key doesn't work, try another one or check back later for fresh keys.
>
> **[Verify your key here](https://alistaitsacle.github.io/free-llm-api-keys/)** — one-click check if a key still works.

### Start here: DeepSeek → smart-chat → Gemini

- `deepseek-chat` — fast, stable, and best for everyday use.
- `smart-chat` — auto-routes across currently healthy low-cost chat backends.
- `gemini-2.5-flash` — fast Gemini option for long-context general chat.

Use `gpt-5.4` or `claude-sonnet-4-6` when you need premium quality; they are intentionally not the default free high-volume path.


### DeepSeek `04-28 17:53`

| Key | Model | Status | Budget | Rate Limit | Expires | Description |
|-----|-------|--------|--------|------------|---------|-------------|
| `sk-kOaU3co3XXW4UG4Moz0YDQqxKhosybd6WyDwLBOgmtVxNwEF` | deepseek-chat | 🆕 New | $20 | 20 RPM | 2026-04-30 | Everyday chat, coding, translation, writing — most stable default |
| `sk-AJiFNHQOggsDlfNtr6W8zFsAdlfAqTYOZVVv97joMdEuAhU6` | deepseek-chat | 🆕 New | $20 | 20 RPM | 2026-04-30 | Everyday chat, coding, translation, writing — most stable default |

---

### Multi-Model (GPT-5.4 / Claude / DeepSeek / Gemini auto-rotate) `04-29 18:01`

| Key | Model | Status | Budget | Rate Limit | Expires | Description |
|-----|-------|--------|--------|------------|---------|-------------|
| `sk-6QW4kyxdKvayQ4oUste6bIkKHIhPWekzxAExJzKNJkoT4XBL` | smart-chat | 🆕 New | $50 | 10 RPM | 2026-05-01 | Auto-routes across currently healthy low-cost chat backends |

---

### Gemini `04-28 17:53`

| Key | Model | Status | Budget | Rate Limit | Expires | Description |
|-----|-------|--------|--------|------------|---------|-------------|
| `sk-OUcnJt879jYJKj2r7AMD9MvIduQVvinSwPMGHbRXlMlzf3xu` | gemini-2.5-flash | 🆕 New | $20 | 20 RPM | 2026-04-30 | Fast Gemini option for long-context general chat |
| `sk-86fwmWZSNxRaLgdzFZRuKvRkVhhtqPXaXzSV7i40EneN36H9` | gemini-2.5-flash | 🆕 New | $20 | 20 RPM | 2026-04-30 | Fast Gemini option for long-context general chat |

---

### GPT-5.4 `04-29 18:01`

| Key | Model | Status | Budget | Rate Limit | Expires | Description |
|-----|-------|--------|--------|------------|---------|-------------|

---

### Claude Sonnet `04-29 18:01`

| Key | Model | Status | Budget | Rate Limit | Expires | Description |
|-----|-------|--------|--------|------------|---------|-------------|

---

### Kimi `04-25 13:30`

| Key | Model | Status | Budget | Rate Limit | Expires | Description |
|-----|-------|--------|--------|------------|---------|-------------|

---


### Image / Audio / Embedding `04-25 13:30`

| Key | Model | Status | Budget | Rate Limit | Expires |
|-----|-------|--------|--------|------------|---------|

## 🚀 How to Use

All keys work with the **OpenAI API format**. Just set the base URL and paste your key.

**Base URL:** `https://aiapiv2.pekpik.com/v1`

### cURL

```bash
curl https://aiapiv2.pekpik.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer PASTE_KEY_HERE" \
  -d '{
    "model": "gpt-5.4",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### Python

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://aiapiv2.pekpik.com/v1",
    api_key="PASTE_KEY_HERE"
)

response = client.chat.completions.create(
    model="gpt-5.4",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

### Node.js

```javascript
import OpenAI from 'openai';

const client = new OpenAI({
  baseURL: 'https://aiapiv2.pekpik.com/v1',
  apiKey: 'PASTE_KEY_HERE',
});

const response = await client.chat.completions.create({
  model: 'gpt-5.4',
  messages: [{ role: 'user', content: 'Hello!' }],
});
console.log(response.choices[0].message.content);
```

### Image Generation (DALL-E 3)

```python
response = client.images.generate(
    model="dall-e-3",
    prompt="A cat astronaut floating in space, digital art",
    size="1024x1024",
    n=1
)
print(response.data[0].url)
```

### Text-to-Speech (TTS)

```python
response = client.audio.speech.create(
    model="tts-1-hd",
    voice="alloy",
    input="Hello! This is a free text-to-speech demo."
)
response.stream_to_file("output.mp3")
```

### Embeddings

```python
response = client.embeddings.create(
    model="text-embedding-3-small",
    input="The quick brown fox jumps over the lazy dog"
)
print(f"Vector dimension: {len(response.data[0].embedding)}")
```

### Works With

| Tool | How to connect |
|------|----------------|
| **Cursor** | Settings → Models → API Key + Base URL |
| **ChatBox** | Settings → API → Custom Provider |
| **LobeChat** | Settings → Language Model → OpenAI |
| **NextChat** | Settings → OpenAI → API Key + Base URL |
| **Open WebUI** | Admin → Settings → Connections → OpenAI API |
| **Immersive Translate** | Settings → Translation → OpenAI |
| **Bob Translate** | Preferences → Services → Translation → OpenAI |
| **Any OpenAI-compatible app** | Set base URL to `https://aiapiv2.pekpik.com/v1` |

> More integration guides: [examples/guides/](./examples/guides/)

---

## 🤖 Supported Models

**90+ models** from 8+ providers, all accessible through a single API key.

| Provider | Models | Notes |
|----------|--------|-------|
| **OpenAI** | gpt-5.4, gpt-5.4-mini, gpt-5.4-nano, gpt-5.4-pro, gpt-4 | Latest GPT lineup |
| **Anthropic** | claude-opus-4-6, claude-sonnet-4-6, claude-haiku-4-5 | Latest Claude |
| **DeepSeek** | deepseek-chat (V3), deepseek-reasoner (R1) | Chat + reasoning |
| **Google** | gemini-3.1-flash-lite, gemini-3.1-flash-image | Gemini 3.1 |
| **xAI** | grok-4.20-beta, grok-4.20-multi-agent-beta | Latest Grok |
| **Mistral** | mistral-medium, codestral, devstral, mistral-small | Code + chat |
| **Cohere** | command-a-vision, command-a-reasoning, embed, rerank | Enterprise AI |
| **More** | Qwen, GLM-5, Mercury, MiniMax, Seed | Continuously expanding |

**Beyond chat:** Image generation (DALL-E 3), text-to-speech (TTS-1-HD), embeddings, reranking.

---

## ❓ FAQ

<details>
<summary><b>What are these keys?</b></summary>

API tokens (`sk-xxx`) issued by our own platform. They are compatible with the OpenAI API format — one key can access 90+ models from multiple providers.
</details>

<details>
<summary><b>How is this different from OpenAI?</b></summary>

| | This Project | OpenAI Direct |
|---|---|---|
| Credit card required | ❌ No | ✅ Yes |
| Free quota | ✅ $20-$100 per key | ❌ None |
| Multi-model access | ✅ One key, all models | ❌ One provider only |
| Works in China | ✅ Direct access | ⚠️ VPN needed |
| Latest models | ✅ GPT-5.4, Claude 4.6, Grok 4.20, Gemini 3.1 | ✅ OpenAI only |
</details>

<details>
<summary><b>What are the limits?</b></summary>

- Each key has a budget of **$20 – $100**
- Rate limit: 3-20 requests per minute (RPM)
- Keys expire in 24-48 hours
- Keys are shared — budget may be used by others
</details>

<details>
<summary><b>Key not working?</b></summary>

Keys are shared publicly, so they may run out of budget. This repo is **auto-updated 3-5 times daily** — just come back later for fresh keys. You can also **Watch → Releases** to get notified.
</details>

<details>
<summary><b>Is this safe?</b></summary>

- These are tokens from our own platform, NOT third-party provider keys
- Each key has independent budget and rate limits
- We do not log conversations
- Keys auto-expire after 24-48 hours
</details>

<details>
<summary><b>What regions are supported?</b></summary>

Available globally. Direct access from China — no VPN needed.
</details>

---

## 📅 Changelog

### 2026-04-26
- 🆕 Added 0 keys (), cleaned 1 expired

<details>
<summary><b>Show changelog history</b></summary>

### 2026-04-29
- 🆕 Added 3 keys (smart-chat, gpt-5.4, claude-sonnet-4-6), cleaned 1 expired

### 2026-04-28
- 🆕 Added 0 keys (no new keys), cleaned 3 expired
- 🆕 Added 4 keys (smart-chat, gpt-5.4, claude-sonnet-4-6), cleaned 1 expired
- 🆕 Added 0 keys (no new keys), cleaned 2 expired
- 🆕 Added 8 keys (deepseek-chat, smart-chat, gemini-2.5-flash, gpt-5.4, claude-sonnet-4-6), cleaned 1 expired
- 🆕 Added 0 keys (no new keys), cleaned 1 expired
- 🆕 Added 0 keys (no new keys), cleaned 220 expired

### 2026-04-25
- 🆕 Added 6 keys (gpt-5.4, claude-sonnet-4-6, smart-chat), cleaned 0 expired
- 🆕 Added 22 keys (claude-opus-4-7, deepseek-chat, gemini-2.5-flash, gemini-2.5-pro, gpt-5.4, kimi-k2.5 +2 more), cleaned 1 expired
- 🆕 Added 0 keys (), cleaned 8 expired
- 🆕 Added 28 keys (claude-opus-4-7, claude-sonnet-4-6, deepseek-chat, deepseek-reasoner, embed-english-v3.0, gemini-2.5-flash +6 more), cleaned 1 expired
- 🆕 Added 0 keys (), cleaned 4 expired
- 🆕 Added 0 keys (), cleaned 15 expired
- 🆕 Added 0 keys (), cleaned 2 expired
- 🆕 Added 0 keys (), cleaned 5 expired
- 🆕 Added 0 keys (), cleaned 3 expired
- 🆕 Added 0 keys (), cleaned 16 expired
- 🆕 Added 36 keys (claude-opus-4-7, claude-sonnet-4-6, deepseek-chat, deepseek-reasoner, embed-english-v3.0, embed-multilingual-v3.0 +9 more), cleaned 1 expired
- 🆕 Added 0 keys (), cleaned 1 expired

### 2026-04-24
- 🆕 Added 0 keys (), cleaned 7 expired
- 🆕 Added 0 keys (), cleaned 15 expired
- 🆕 Added 0 keys (), cleaned 6 expired
- 🆕 Added 0 keys (), cleaned 4 expired
- 🆕 Added 0 keys (), cleaned 16 expired
- 🆕 Added 36 keys (claude-opus-4-7, claude-sonnet-4-6, deepseek-chat, deepseek-reasoner, embed-english-v3.0, embed-multilingual-v3.0 +9 more), cleaned 1 expired
- 🆕 Added 0 keys (), cleaned 2 expired
- 🆕 Added 0 keys (), cleaned 5 expired
- 🆕 Added 0 keys (), cleaned 9 expired
- 🆕 Added 0 keys (), cleaned 3 expired
- 🆕 Added 0 keys (), cleaned 21 expired
- 🆕 Added 19 keys (embed-english-v3.0, embed-multilingual-v3.0, gemini-2.5-flash, gemini-2.5-flash-lite, gemini-2.5-pro, gpt-5.4 +5 more), cleaned 1 expired
- 🆕 Added 0 keys (), cleaned 1 expired

### 2026-04-23
- 🆕 Added 0 keys (), cleaned 18 expired
- 🆕 Added 0 keys (), cleaned 23 expired
- 🆕 Added 0 keys (), cleaned 2 expired
- 🆕 Added 0 keys (), cleaned 21 expired
- 🆕 Added 0 keys (), cleaned 4 expired
- 🆕 Added 0 keys (), cleaned 24 expired
- 🆕 Added 19 keys (embed-english-v3.0, embed-multilingual-v3.0, gemini-2.5-flash, gemini-2.5-flash-lite, gemini-2.5-pro, gpt-5.4 +5 more), cleaned 1 expired
- 🆕 Added 0 keys (), cleaned 1 expired

### 2026-04-22
- 🆕 Added 0 keys (), cleaned 5 expired
- 🆕 Added 0 keys (), cleaned 3 expired
- 🆕 Added 0 keys (), cleaned 20 expired
- 🆕 Added 19 keys (embed-english-v3.0, embed-multilingual-v3.0, gemini-2.5-flash, gemini-2.5-flash-lite, gemini-2.5-pro, gpt-5.4 +5 more), cleaned 1 expired
- 🆕 Added 0 keys (), cleaned 4 expired
- 🆕 Added 0 keys (), cleaned 2 expired
- 🆕 Added 10 keys (embed-english-v3.0, embed-multilingual-v3.0, gemini-2.5-flash, gemini-2.5-flash-lite, gemini-2.5-pro, gpt-5.4 +4 more), cleaned 1 expired
- 🆕 Added 0 keys (), cleaned 22 expired
- 🆕 Added 26 keys (GLM-4.7, codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat +19 more), cleaned 1 expired
- 🆕 Added 0 keys (), cleaned 1 expired

### 2026-04-21
- 🆕 Added 0 keys (), cleaned 3 expired
- 🆕 Added 0 keys (), cleaned 20 expired
- 🆕 Added 23 keys (GLM-4.7, codestral-latest, dall-e-3, deepseek-chat, deepseek-reasoner, devstral-latest +16 more), cleaned 1 expired
- 🆕 Added 0 keys (), cleaned 21 expired
- 🆕 Added 0 keys (), cleaned 24 expired
- 🆕 Added 24 keys (GLM-4.7, codestral-latest, dall-e-3, deepseek-chat, deepseek-reasoner, devstral-latest +17 more), cleaned 1 expired
- 🆕 Added 0 keys (), cleaned 23 expired
- 🆕 Added 26 keys (GLM-4.7, codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat +19 more), cleaned 1 expired
- 🆕 Added 0 keys (), cleaned 2 expired
- 🆕 Added 0 keys (), cleaned 1 expired

### 2026-04-20
- 🆕 Added 0 keys (), cleaned 23 expired
- 🆕 Added 22 keys (GLM-4.7, codestral-latest, dall-e-3, deepseek-chat, deepseek-reasoner, devstral-latest +15 more), cleaned 1 expired
- 🆕 Added 21 keys (GLM-4.7, codestral-latest, dall-e-3, deepseek-chat, deepseek-reasoner, devstral-latest +14 more), cleaned 1 expired
- 🆕 Added 0 keys (), cleaned 17 expired
- 🆕 Added 25 keys (GLM-4.7, codestral-latest, command-a-vision-07-2025, dall-e-3, deepseek-chat, deepseek-reasoner +18 more), cleaned 2 expired
- 🆕 Added 0 keys (), cleaned 22 expired
- 🆕 Added 0 keys (), cleaned 3 expired
- 🆕 Added 0 keys (), cleaned 2 expired
- 🆕 Added 0 keys (), cleaned 21 expired
- 🆕 Added 26 keys (GLM-4.7, codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat +19 more), cleaned 1 expired
- 🆕 Added 0 keys (), cleaned 1 expired

### 2026-04-19
- 🆕 Added 0 keys (), cleaned 3 expired
- 🆕 Added 22 keys (GLM-4.7, codestral-latest, dall-e-3, deepseek-chat, deepseek-reasoner, devstral-latest +15 more), cleaned 1 expired
- 🆕 Added 0 keys (), cleaned 20 expired
- 🆕 Added 0 keys (), cleaned 21 expired
- 🆕 Added 26 keys (GLM-4.7, codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat +19 more), cleaned 1 expired
- 🆕 Added 0 keys (), cleaned 1 expired
- 🆕 Added 0 keys (), cleaned 2 expired

### 2026-04-18
- 🆕 Added 0 keys (), cleaned 21 expired
- 🆕 Added 0 keys (), cleaned 6 expired
- 🆕 Added 0 keys (), cleaned 22 expired
- 🆕 Added 26 keys (GLM-4.7, codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat +19 more), cleaned 4 expired
- 🆕 Added 0 keys (), cleaned 5 expired
- 🆕 Added 0 keys (), cleaned 3 expired
- 🆕 Added 0 keys (), cleaned 19 expired
- 🆕 Added 20 keys (GLM-4.7, codestral-latest, dall-e-3, deepseek-chat, deepseek-reasoner, devstral-latest +13 more), cleaned 1 expired
- 🆕 Added 0 keys (), cleaned 2 expired
- 🆕 Added 0 keys (), cleaned 18 expired
- 🆕 Added 26 keys (GLM-4.7, codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat +19 more), cleaned 1 expired
- 🆕 Added 0 keys (), cleaned 1 expired

### 2026-04-17
- 🆕 Added 0 keys (), cleaned 4 expired
- 🆕 Added 0 keys (), cleaned 19 expired
- 🆕 Added 26 keys (GLM-4.7, codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat +19 more), cleaned 1 expired
- 🆕 Added 0 keys (), cleaned 1 expired
- 🆕 Added 0 keys (), cleaned 2 expired

### 2026-04-16
- 🆕 Added 0 keys (), cleaned 19 expired
- 🆕 Added 26 keys (GLM-4.7, codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat +19 more), cleaned 2 expired
- 🆕 Added 0 keys (), cleaned 5 expired
- 🆕 Added 26 keys (GLM-4.7, codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat +19 more), cleaned 4 expired
- 🆕 Added 0 keys (), cleaned 2 expired
- 🆕 Added 0 keys (), cleaned 3 expired
- 🆕 Added 0 keys (), cleaned 20 expired
- 🆕 Added 26 keys (GLM-4.7, codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat +19 more), cleaned 1 expired
- 🆕 Added 0 keys (), cleaned 1 expired

### 2026-04-15
- 🆕 Added 0 keys (), cleaned 3 expired
- 🆕 Added 0 keys (), cleaned 18 expired
- 🆕 Added 0 keys (), cleaned 4 expired
- 🆕 Added 0 keys (), cleaned 2 expired
- 🆕 Added 0 keys (), cleaned 20 expired
- 🆕 Added 25 keys (GLM-4.7, codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat +18 more), cleaned 1 expired
- 🆕 Added 0 keys (), cleaned 1 expired

### 2026-04-14
- 🆕 Added 0 keys (), cleaned 11 expired
- 🆕 Added 0 keys (), cleaned 6 expired
- 🆕 Added 0 keys (), cleaned 4 expired
- 🆕 Added 0 keys (), cleaned 18 expired
- 🆕 Added 0 keys (), cleaned 3 expired
- 🆕 Added 0 keys (), cleaned 22 expired
- 🆕 Added 24 keys (GLM-4.7, codestral-latest, command-a-vision-07-2025, dall-e-3, deepseek-chat, deepseek-reasoner +17 more), cleaned 1 expired
- 🆕 Added 0 keys (), cleaned 25 expired
- 🆕 Added 23 keys (GLM-4.7, codestral-latest, dall-e-3, deepseek-chat, deepseek-reasoner, devstral-latest +16 more), cleaned 1 expired
- 🆕 Added 0 keys (), cleaned 23 expired
- 🆕 Added 0 keys (), cleaned 2 expired
- 🆕 Added 0 keys (), cleaned 24 expired
- 🆕 Added 25 keys (GLM-4.7, codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat +18 more), cleaned 1 expired
- 🆕 Added 0 keys (), cleaned 1 expired

### 2026-04-13
- 🆕 Added 0 keys (), cleaned 3 expired
- 🆕 Added 0 keys (), cleaned 23 expired
- 🆕 Added 0 keys (), cleaned 24 expired
- 🆕 Added 0 keys (), cleaned 21 expired
- 🆕 Added 20 keys (GLM-4.7, codestral-latest, dall-e-3, deepseek-chat, deepseek-reasoner, devstral-latest +13 more), cleaned 1 expired
- 🆕 Added 0 keys (), cleaned 2 expired
- 🆕 Added 0 keys (), cleaned 19 expired
- 🆕 Added 25 keys (GLM-4.7, codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat +18 more), cleaned 1 expired
- 🆕 Added 0 keys (), cleaned 1 expired

### 2026-04-12
- 🆕 Added 18 keys (GLM-4.7, codestral-latest, dall-e-3, deepseek-chat, deepseek-reasoner, devstral-latest +11 more), cleaned 1 expired
- 🆕 Added 0 keys (), cleaned 18 expired
- 🆕 Added 22 keys (GLM-4.7, codestral-latest, dall-e-3, deepseek-chat, deepseek-reasoner, devstral-latest +15 more), cleaned 1 expired
- 🆕 Added 0 keys (), cleaned 20 expired
- 🆕 Added 0 keys (), cleaned 2 expired
- 🆕 Added 0 keys (), cleaned 24 expired
- 🆕 Added 24 keys (GLM-4.7, codestral-latest, command-a-vision-07-2025, dall-e-3, deepseek-chat, deepseek-reasoner +17 more), cleaned 1 expired
- 🆕 Added 0 keys (), cleaned 25 expired
- 🆕 Added 25 keys (GLM-4.7, codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat +18 more), cleaned 1 expired
- 🆕 Added 0 keys (), cleaned 1 expired

### 2026-04-11
- 🆕 Added 0 keys (), cleaned 24 expired
- 🆕 Added 25 keys (GLM-4.7, codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat +18 more), cleaned 1 expired
- 🆕 Added 24 keys (GLM-4.7, codestral-latest, dall-e-3, deepseek-chat, deepseek-reasoner, devstral-latest +17 more), cleaned 1 expired
- 🆕 Added 0 keys (), cleaned 25 expired
- 🆕 Added 21 keys (GLM-4.7, codestral-latest, dall-e-3, deepseek-chat, deepseek-reasoner, devstral-latest +14 more), cleaned 1 expired
- 🆕 Added 0 keys (), cleaned 3 expired
- 🆕 Added 0 keys (), cleaned 2 expired
- 🆕 Added 0 keys (), cleaned 19 expired
- 🆕 Added 20 keys (GLM-4.7, codestral-latest, dall-e-3, deepseek-chat, deepseek-reasoner, devstral-latest +13 more), cleaned 2 expired
- 🆕 Added 0 keys (), cleaned 1 expired

### 2026-04-10
- 🆕 Added 0 keys (), cleaned 17 expired
- 🆕 Added 0 keys (), cleaned 25 expired
- 🆕 Added 19 keys (GLM-4.7, codestral-latest, dall-e-3, deepseek-chat, deepseek-reasoner, devstral-latest +12 more), cleaned 1 expired
- 🆕 Added 22 keys (GLM-4.7, codestral-latest, dall-e-3, deepseek-chat, deepseek-reasoner, devstral-latest +15 more), cleaned 1 expired
- 🆕 Added 0 keys (), cleaned 2 expired
- 🆕 Added 0 keys (), cleaned 18 expired
- 🆕 Added 0 keys (), cleaned 3 expired
- 🆕 Added 0 keys (), cleaned 24 expired
- 🆕 Added 26 keys (GLM-4.7, codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat +19 more), cleaned 1 expired
- 🆕 Added 0 keys (), cleaned 1 expired

### 2026-04-09
- 🆕 Added 0 keys (), cleaned 3 expired
- 🆕 Added 0 keys (), cleaned 25 expired
- 🆕 Added 26 keys (GLM-4.7, codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat +19 more), cleaned 1 expired
- 🆕 Added 0 keys (), cleaned 2 expired
- 🆕 Added 0 keys (), cleaned 4 expired
- 🆕 Added 0 keys (), cleaned 26 expired
- 🆕 Added 21 keys (GLM-4.7, codestral-latest, dall-e-3, deepseek-chat, deepseek-reasoner, devstral-latest +14 more), cleaned 1 expired
- 🆕 Added 0 keys (), cleaned 1 expired

### 2026-04-08
- 🆕 Added 0 keys (), cleaned 21 expired
- 🆕 Added 17 keys (GLM-4.7, codestral-latest, dall-e-3, deepseek-chat, devstral-latest, flagship-chat +10 more), cleaned 1 expired
- 🆕 Added 0 keys (), cleaned 19 expired
- 🆕 Added 0 keys (), cleaned 22 expired
- 🆕 Added 18 keys (GLM-4.7, codestral-latest, dall-e-3, deepseek-chat, deepseek-reasoner, devstral-latest +11 more), cleaned 1 expired
- 🆕 Added 0 keys (), cleaned 2 expired
- 🆕 Added 0 keys (), cleaned 18 expired
- 🆕 Added 25 keys (GLM-4.7, codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat +18 more), cleaned 1 expired
- 🆕 Added 0 keys (), cleaned 1 expired


### 2026-04-07
- 🆕 Added 25 keys (GLM-4.7, codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat +18 more), cleaned 1 expired
- 🆕 Added 0 keys (), cleaned 24 expired
- 🆕 Added 0 keys (), cleaned 25 expired
- 🆕 Added 26 keys (GLM-4.7, codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat +19 more), cleaned 1 expired
- 🆕 Added 0 keys (), cleaned 2 expired
- 🆕 Added 0 keys (), cleaned 1 expired

### 2026-04-06
- 🆕 Added 0 keys (), cleaned 25 expired
- 🆕 Added 22 keys (GLM-4.7, codestral-latest, dall-e-3, deepseek-chat, deepseek-reasoner, devstral-latest +15 more), cleaned 1 expired
- 🆕 Added 0 keys (), cleaned 2 expired
- 🆕 Added 0 keys (), cleaned 21 expired
- 🆕 Added 1 keys (glm-5), cleaned 1 expired
- 🆕 Added 0 keys (), cleaned 1 expired
- 🆕 Added 0 keys (), cleaned 3 expired
- 🆕 Added 20 keys (GLM-4.7, codestral-latest, dall-e-3, deepseek-chat, deepseek-reasoner, devstral-latest +13 more), cleaned 21 expired
- 🆕 Added 23 keys (GLM-4.7, codestral-latest, dall-e-3, deepseek-chat, deepseek-reasoner, devstral-latest +16 more), cleaned 23 expired
- 🆕 Added 19 keys (GLM-4.7, codestral-latest, dall-e-3, deepseek-chat, deepseek-reasoner, devstral-latest +12 more), cleaned 19 expired
- 🆕 Added 19 keys (GLM-4.7, codestral-latest, dall-e-3, deepseek-chat, deepseek-reasoner, devstral-latest +12 more), cleaned 19 expired

### 2026-04-05
- 🆕 Added 24 keys (GLM-4.7, codestral-latest, command-a-vision-07-2025, dall-e-3, deepseek-chat, deepseek-reasoner +17 more), cleaned 26 expired
- 🆕 Added 25 keys (GLM-4.7, codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat +18 more), cleaned 26 expired
- 🆕 Added 24 keys (GLM-4.7, codestral-latest, command-a-vision-07-2025, dall-e-3, deepseek-chat, deepseek-reasoner +17 more), cleaned 25 expired
- 🆕 Added 25 keys (GLM-4.7, codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat +18 more), cleaned 23 expired
- 🆕 Added 25 keys (GLM-4.7, codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat +18 more), cleaned 30 expired

### 2026-04-04
- 🆕 Added 25 keys (GLM-4.7, codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat +18 more), cleaned 26 expired
- 🆕 Added 21 keys (GLM-4.7, codestral-latest, dall-e-3, deepseek-chat, deepseek-reasoner, devstral-latest +14 more), cleaned 22 expired
- 🆕 Added 20 keys (GLM-4.7, codestral-latest, dall-e-3, deepseek-chat, deepseek-reasoner, devstral-latest +13 more), cleaned 21 expired
- 🆕 Added 24 keys (GLM-4.7, codestral-latest, command-a-vision-07-2025, dall-e-3, deepseek-chat, deepseek-reasoner +17 more), cleaned 25 expired
- 🆕 Added 18 keys (GLM-4.7, codestral-latest, dall-e-3, deepseek-chat, deepseek-reasoner, devstral-latest +11 more), cleaned 19 expired

### 2026-04-03
- 🆕 Added 15 keys (GLM-4.7, dall-e-3, deepseek-chat, devstral-latest, flagship-chat, gemini-2.5-flash +8 more), cleaned 15 expired
- 🆕 Added 24 keys (GLM-4.7, codestral-latest, dall-e-3, deepseek-chat, deepseek-reasoner, devstral-latest +17 more), cleaned 24 expired
- 🆕 Added 26 keys (GLM-4.7, codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat +19 more), cleaned 26 expired
- 🆕 Added 26 keys (GLM-4.7, codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat +19 more), cleaned 29 expired
- 🆕 Added 24 keys (GLM-4.7, codestral-latest, dall-e-3, deepseek-chat, deepseek-reasoner, devstral-latest +17 more), cleaned 25 expired

### 2026-04-02
- 🆕 Added 24 keys (GLM-4.7, codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat +17 more), cleaned 2 expired
- 🆕 Added 24 keys (GLM-4.7, codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat +17 more), cleaned 49 expired
- 🆕 Added 23 keys (GLM-4.7, codestral-latest, dall-e-3, deepseek-chat, deepseek-reasoner, devstral-latest +16 more), cleaned 23 expired
- 🆕 Added 22 keys (GLM-4.7, codestral-latest, dall-e-3, deepseek-chat, deepseek-reasoner, devstral-latest +15 more), cleaned 23 expired
- 🆕 Added 26 keys (GLM-4.7, codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat +19 more), cleaned 28 expired

### 2026-04-01
- 🆕 Added 18 keys (GLM-4.7, codestral-latest, dall-e-3, deepseek-chat, deepseek-reasoner, devstral-latest +11 more), cleaned 19 expired
- 🆕 Added 14 keys (GLM-4.7, dall-e-3, deepseek-chat, devstral-latest, flagship-chat, gemini-2.5-flash +7 more), cleaned 15 expired
- 🆕 Added 23 keys (GLM-4.7, codestral-latest, dall-e-3, deepseek-chat, deepseek-reasoner, devstral-latest +16 more), cleaned 22 expired
- 🆕 Added 26 keys (GLM-4.7, codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat +19 more), cleaned 30 expired
- 🆕 Added 26 keys (GLM-4.7, codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat +19 more), cleaned 27 expired

### 2026-03-31
- 🆕 Added 26 keys (GLM-4.7, codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat +19 more), cleaned 26 expired
- 🆕 Added 26 keys (GLM-4.7, codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat +19 more), cleaned 28 expired
- 🆕 Added 24 keys (GLM-4.7, codestral-latest, dall-e-3, deepseek-chat, deepseek-reasoner, devstral-latest +17 more), cleaned 25 expired
- 🆕 Added 24 keys (GLM-4.7, codestral-latest, dall-e-3, deepseek-chat, deepseek-reasoner, devstral-latest +17 more), cleaned 25 expired
- 🆕 Added 24 keys (GLM-4.7, codestral-latest, dall-e-3, deepseek-chat, deepseek-reasoner, devstral-latest +17 more), cleaned 25 expired

### 2026-03-30
- 🆕 Added 23 keys (GLM-4.7, codestral-latest, dall-e-3, deepseek-chat, deepseek-reasoner, devstral-latest +16 more), cleaned 24 expired
- 🆕 Added 20 keys (GLM-4.7, codestral-latest, dall-e-3, deepseek-chat, deepseek-reasoner, devstral-latest +13 more), cleaned 21 expired
- 🆕 Added 15 keys (GLM-4.7, dall-e-3, deepseek-chat, devstral-latest, flagship-chat, gemini-2.5-pro +8 more), cleaned 16 expired
- 🆕 Added 21 keys (GLM-4.7, codestral-latest, dall-e-3, deepseek-chat, deepseek-reasoner, devstral-latest +14 more), cleaned 18 expired
- 🆕 Added 26 keys (GLM-4.7, codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat +19 more), cleaned 29 expired

### 2026-03-29
- 🆕 Added 26 keys (GLM-4.7, codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat +19 more), cleaned 27 expired
- 🆕 Added 26 keys (GLM-4.7, codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat +19 more), cleaned 27 expired
- 🆕 Added 26 keys (GLM-4.7, codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat +19 more), cleaned 29 expired
- 🆕 Added 25 keys (GLM-4.7, codestral-latest, command-a-vision-07-2025, dall-e-3, deepseek-chat, deepseek-reasoner +18 more), cleaned 26 expired
- 🆕 Added 25 keys (GLM-4.7, codestral-latest, command-a-vision-07-2025, dall-e-3, deepseek-chat, deepseek-reasoner +18 more), cleaned 26 expired

### 2026-03-28
- 🆕 Added 25 keys (GLM-4.7, codestral-latest, command-a-vision-07-2025, dall-e-3, deepseek-chat, deepseek-reasoner +18 more), cleaned 26 expired
- 🆕 Added 21 keys (GLM-4.7, codestral-latest, dall-e-3, deepseek-chat, deepseek-reasoner, devstral-latest +14 more), cleaned 20 expired
- 🆕 Added 22 keys (GLM-4.7, codestral-latest, dall-e-3, deepseek-chat, deepseek-reasoner, devstral-latest +15 more), cleaned 26 expired
- 🆕 Added 17 keys (GLM-4.7, codestral-latest, dall-e-3, deepseek-chat, devstral-latest, flagship-chat +10 more), cleaned 18 expired
- 🆕 Added 19 keys (GLM-4.7, codestral-latest, dall-e-3, deepseek-chat, deepseek-reasoner, devstral-latest +12 more), cleaned 19 expired

### 2026-03-27
- 🆕 Added 21 keys (GLM-4.7, codestral-latest, dall-e-3, deepseek-chat, deepseek-reasoner, devstral-latest +14 more), cleaned 18 expired
- 🆕 Added 26 keys (GLM-4.7, codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat +19 more), cleaned 18 expired
- 🆕 Added 26 keys (GLM-4.7, codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat +19 more), cleaned 12 expired
- 🆕 Added 26 keys (GLM-4.7, codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat +19 more), cleaned 20 expired
- 🆕 Added 26 keys (GLM-4.7, codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat +19 more), cleaned 19 expired

### 2026-03-26
- 🆕 Added 26 keys (GLM-4.7, codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat +19 more), cleaned 21 expired
- 🆕 Added 26 keys (GLM-4.7, codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat +19 more), cleaned 21 expired
- 🆕 Added 19 keys (codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat, deepseek-reasoner +12 more), cleaned 3 expired
- 🆕 Added 19 keys (codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat, deepseek-reasoner +12 more), cleaned 6 expired
- 🆕 Added 19 keys (codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat, deepseek-reasoner +12 more), cleaned 9 expired

### 2026-03-25
- 🆕 Added 19 keys (codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat, deepseek-reasoner +12 more), cleaned 1 expired
- 🆕 Added 19 keys (codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat, deepseek-reasoner +12 more), cleaned 1 expired
- 🆕 Added 19 keys (codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat, deepseek-reasoner +12 more), cleaned 19 expired
- 🆕 Added 12 keys (codestral-latest, dall-e-3, deepseek-chat, devstral-latest, flagship-chat, gpt-5.4 +5 more), cleaned 1 expired
- 🆕 Added 19 keys (codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat, deepseek-reasoner +12 more), cleaned 1 expired

### 2026-03-24
- 🆕 Added 19 keys (codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat, deepseek-reasoner +12 more), cleaned 1 expired
- 🆕 Added 19 keys (codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat, deepseek-reasoner +12 more), cleaned 1 expired
- 🆕 Added 19 keys (codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat, deepseek-reasoner +12 more), cleaned 1 expired
- 🆕 Added 19 keys (codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat, deepseek-reasoner +12 more), cleaned 1 expired
- 🆕 Added 19 keys (codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat, deepseek-reasoner +12 more), cleaned 1 expired
- 🆕 Added 7 keys (dall-e-3, deepseek-chat, gpt-5.4, gpt-5.4-mini, smart-chat, tts-1-hd), cleaned 2 expired

### 2026-03-23
- 🆕 Added 19 keys (codestral-latest, command-a-reasoning-08-2025, command-a-vision-07-2025, dall-e-3, deepseek-chat, deepseek-reasoner +12 more), cleaned 1 expired
- 🆕 Added 6 keys (dall-e-3, deepseek-chat, gpt-5.4, gpt-5.4-mini, smart-chat, tts-1-hd), cleaned 1 expired
- 🆕 Published 19 keys across 8 model families: GPT-5.4, DeepSeek, Mistral, Cohere, DALL-E 3, TTS, Embeddings
- 📝 Project launched
</details>

---

## 🔗 Related Free Resources

If this repo helped you, you may also like:

- **[free-vpn-subscriptions](https://github.com/Au1rxx/free-vpn-subscriptions)** — hourly-refreshed Clash / sing-box / v2ray subscription URLs, every node TCP-probed and ranked by latency. No signup, no binary to install.
- **[proxykit](https://github.com/Au1rxx/proxykit)** — Swiss-army knife for proxy subscriptions. Convert Clash / sing-box / v2ray / Surge formats, probe TCP+TLS liveness, detect Netflix / Disney+ / ChatGPT unlock. Single Go binary, no Docker.

---

## 📈 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=alistaitsacle/free-llm-api-keys&type=Date)](https://star-history.com/#alistaitsacle/free-llm-api-keys&Date)

---

## 🤝 Contributing

- 💬 [Discussions](../../discussions) — Feedback, model requests, use cases
- 🐛 [Issues](../../issues) — Report expired keys or problems
- 📖 [Contributing Guide](./CONTRIBUTING.md) — How to contribute
- ⭐ **Star this repo** — Help more people discover free AI resources

---

## ⚠️ Disclaimer

- Keys are platform-issued tokens for **learning and development** only
- No SLA or uptime guarantee
- Do not use for illegal purposes or production workloads
- Maintainers reserve the right to adjust quotas or revoke keys at any time

---

## 📜 License

[MIT License](./LICENSE)
