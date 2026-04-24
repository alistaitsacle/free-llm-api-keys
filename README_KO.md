<!--
  SEO: 무료 LLM API 키, 무료 GPT API, 무료 Claude API, 무료 DeepSeek API,
  무료 AI API 키, OpenAI 호환 API, 무료 대규모 언어 모델 API
-->

<div align="center">

<img src="./assets/banner.jpg" alt="무료 LLM API 키 — GPT-5.4, Claude, DeepSeek, Gemini, Grok, 90+ 모델" width="100%">

<br>

LLM API를 무료로 이용하는 가장 쉬운 방법 — 신용카드 불필요, 가입 불필요
<br>
아래 표에서 키를 복사하여 앱에 붙여넣기만 하면 됩니다

<br>

[![Stars](https://img.shields.io/github/stars/alistaitsacle/free-llm-api-keys?style=for-the-badge&logo=github)](https://github.com/alistaitsacle/free-llm-api-keys/stargazers)
[![Last Commit](https://img.shields.io/github/last-commit/alistaitsacle/free-llm-api-keys?style=for-the-badge)](https://github.com/alistaitsacle/free-llm-api-keys/commits)
[![Keys](https://img.shields.io/badge/사용_가능_Key-19-brightgreen?style=for-the-badge)]()
[![Models](https://img.shields.io/badge/모델-90+-blue?style=for-the-badge)]()

**⭐ Star = 모두에게 더 많은 무료 키**

[English](./README.md) | [中文](./README_CN.md) | [日本語](./README_JA.md) | 한국어 | [Español](./README_ES.md) | [Português](./README_PT.md)

</div>

---

<div align="center">

🧪 **[Playground에서 체험 →](https://alistaitsacle.github.io/free-llm-api-keys/)** — 키를 붙여넣으면 90+ 모델과 브라우저에서 바로 대화

</div>

---

## 💡 이 프로젝트에 대해

AI가 모든 것을 바꾸고 있지만, 대부분의 API는 신용카드와 유료 장벽 뒤에 잠겨 있습니다. 특히 학생, 취미 개발자, 서비스를 이용할 수 없는 지역의 개발자들에게는 접근이 어렵습니다.

저는 업무에서 LLM API를 많이 사용하며, 여유 용량이 있습니다. 낭비하느니 공유하기로 했습니다 — 무료 키, 조건 없음, 매일 업데이트.

**신용카드 불필요. 가입 불필요. 복사, 붙여넣기, 바로 사용.**

---

## 💼 높은 가용성이 필요하신가요?

프로덕션용 LLM 키가 필요하시면 **alistaitscale@gmail.com** 으로 연락 주세요.

---

## 📋 사용 가능한 키

최신 키 목록은 **[영문 README](./README.md#-available-keys)**를 참조하세요.

모든 키는 **OpenAI SDK 호환**입니다. Base URL: `https://aiapiv2.pekpik.com/v1`

---

## 🚀 사용 방법

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://aiapiv2.pekpik.com/v1",
    api_key="위 표에서 키를 복사"
)

response = client.chat.completions.create(
    model="gpt-5.4",
    messages=[{"role": "user", "content": "안녕하세요!"}]
)
print(response.choices[0].message.content)
```

### 지원 도구

| 도구 | 설정 방법 |
|------|---------|
| **Cursor** | Settings → Models → API Key + Base URL `https://aiapiv2.pekpik.com/v1` |
| **ChatBox** | 설정 → API → 사용자 정의 제공자 |
| **LobeChat** | 설정 → 언어 모델 → OpenAI → API Key + Proxy URL |
| **OpenAI SDK 호환 앱** | Base URL을 `https://aiapiv2.pekpik.com/v1`으로 설정 |

---

## 🤖 지원 모델

**90개 이상의 모델**, 8개 이상의 제공업체 지원.

| 제공업체 | 모델 | 설명 |
|---------|------|------|
| **OpenAI** | gpt-5.4, gpt-5.4-mini, gpt-5.4-nano, gpt-5.4-pro | 최신 GPT |
| **Anthropic** | claude-opus-4-6, claude-sonnet-4-6, claude-haiku-4-5 | 최신 Claude |
| **DeepSeek** | deepseek-chat (V3), deepseek-reasoner (R1) | 대화 + 추론 |
| **Google** | gemini-3.1-flash-lite, gemini-3.1-flash-image | Gemini 3.1 |
| **xAI** | grok-4.20-beta | 최신 Grok |
| **Mistral** | mistral-medium, codestral, devstral | 코드 + 대화 |
| **기타** | Cohere, Qwen, GLM-5, DALL-E 3, TTS, Embeddings | 지속 확장 중 |

---

## ❓ 자주 묻는 질문

**키가 작동하지 않나요?** 키는 공개 공유됩니다. 예산이 다른 사용자에 의해 소진되었을 수 있습니다. 이 저장소는 **매일 3-5회 자동 업데이트**됩니다. 나중에 다시 확인해 주세요.

**안전한가요?** 자체 플랫폼에서 발급한 토큰입니다. 타사 API 키가 아닙니다. 각 키에 독립적인 예산과 속도 제한이 있습니다.

**지원 지역은?** 전 세계에서 이용 가능. VPN 불필요.

---

## 🔗 관련 무료 리소스

- **[free-vpn-subscriptions](https://github.com/Au1rxx/free-vpn-subscriptions)** — 매시간 자동 갱신되는 Clash / sing-box / v2ray 구독 링크. 모든 노드 TCP 프로브 완료, 레이턴시 순 정렬. 가입 불필요, 바이너리 설치 불필요.
- **[proxykit](https://github.com/Au1rxx/proxykit)** — 프록시 구독 스위스 아미 나이프. Clash / sing-box / v2ray / Surge 형식 변환, TCP+TLS 활성 프로브, Netflix / Disney+ / ChatGPT 언락 감지. 단일 Go 바이너리, Docker 불필요.

---

## 📜 License

[MIT License](./LICENSE)
