<!--
  SEO: 無料 LLM API キー, 無料 GPT API, 無料 Claude API, 無料 DeepSeek API,
  無料 AI API キー, OpenAI 互換 API, 無料 大規模言語モデル API
-->

<div align="center">

<img src="./assets/banner.jpg" alt="無料 LLM API キー — GPT-5.4, Claude, DeepSeek, Gemini, Grok, 90以上のモデル" width="100%">

<br>

LLM APIを無料で利用する最も簡単な方法 — クレジットカード不要、登録不要
<br>
下の表からキーをコピーして、アプリに貼り付けるだけ

<br>

[![Stars](https://img.shields.io/github/stars/alistaitsacle/free-llm-api-keys?style=for-the-badge&logo=github)](https://github.com/alistaitsacle/free-llm-api-keys/stargazers)
[![Last Commit](https://img.shields.io/github/last-commit/alistaitsacle/free-llm-api-keys?style=for-the-badge)](https://github.com/alistaitsacle/free-llm-api-keys/commits)
[![Keys](https://img.shields.io/badge/利用可能なKey-19-brightgreen?style=for-the-badge)]()
[![Models](https://img.shields.io/badge/モデル-90+-blue?style=for-the-badge)]()

**⭐ Starすると = みんなに無料キーが増えます**

[English](./README.md) | [中文](./README_CN.md) | 日本語 | [한국어](./README_KO.md) | [Español](./README_ES.md) | [Português](./README_PT.md)

</div>

---

<div align="center">

🧪 **[Playground で試す →](https://alistaitsacle.github.io/free-llm-api-keys/)** — API キーを貼って、90+ モデルとブラウザで即チャット

</div>

---

## 💡 このプロジェクトについて

AIはすべてを変えていますが、ほとんどのAPIはクレジットカードや有料の壁の向こうにあります。特に学生、趣味の開発者、サービスが利用できない地域の開発者にとって、アクセスは困難です。

私は自分の仕事でLLM APIを多く使用しており、余った容量があります。無駄にするよりも共有することにしました — 無料キー、条件なし、毎日更新。

**クレジットカード不要。登録不要。コピー、ペースト、すぐ使えます。**

---

## 💼 高可用性が必要な方へ

本番用 LLM キーについては **alistaitscale@gmail.com** までご連絡ください。

---

## 📋 利用可能なキー

最新のキー一覧は **[英語版 README](./README.md#-available-keys)** をご覧ください。

すべてのキーは **OpenAI SDK互換** です。Base URL: `https://aiapiv2.pekpik.com/v1`

---

## 🚀 使い方

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://aiapiv2.pekpik.com/v1",
    api_key="上の表からキーをコピー"
)

response = client.chat.completions.create(
    model="gpt-5.4",
    messages=[{"role": "user", "content": "こんにちは！"}]
)
print(response.choices[0].message.content)
```

### 対応ツール

| ツール | 設定方法 |
|--------|---------|
| **Cursor** | Settings → Models → API Key + Base URL `https://aiapiv2.pekpik.com/v1` |
| **ChatBox** | 設定 → API → カスタムプロバイダー |
| **LobeChat** | 設定 → 言語モデル → OpenAI → API Key + Proxy URL |
| **OpenAI SDK互換アプリ** | Base URLを `https://aiapiv2.pekpik.com/v1` に設定 |

---

## 🤖 対応モデル

**90以上のモデル**、8社以上のプロバイダーに対応。

| プロバイダー | モデル | 説明 |
|-------------|--------|------|
| **OpenAI** | gpt-5.4, gpt-5.4-mini, gpt-5.4-nano, gpt-5.4-pro | 最新GPT |
| **Anthropic** | claude-opus-4-6, claude-sonnet-4-6, claude-haiku-4-5 | 最新Claude |
| **DeepSeek** | deepseek-chat (V3), deepseek-reasoner (R1) | チャット + 推論 |
| **Google** | gemini-3.1-flash-lite, gemini-3.1-flash-image | Gemini 3.1 |
| **xAI** | grok-4.20-beta | 最新Grok |
| **Mistral** | mistral-medium, codestral, devstral | コード + チャット |
| **その他** | Cohere, Qwen, GLM-5, DALL-E 3, TTS, Embeddings | 継続的に拡大中 |

---

## ❓ よくある質問

**キーが使えない？** キーは公開共有です。予算が使い切られている場合があります。このリポジトリは**毎日3-5回自動更新**されます。後で再度ご確認ください。

**安全ですか？** 当プラットフォーム独自のトークンです。第三者のAPIキーではありません。各キーに独立した予算と速度制限があります。

**対応地域は？** 全世界で利用可能。VPN不要。

---

## 🔗 関連する無料リソース

- **[free-vpn-subscriptions](https://github.com/Au1rxx/free-vpn-subscriptions)** — 毎時自動更新される Clash / sing-box / v2ray 購読リンク。全ノード TCP プローブ済み、レイテンシ順にソート。登録不要、バイナリ不要。
- **[proxykit](https://github.com/Au1rxx/proxykit)** — プロキシ購読のスイスアーミーナイフ。Clash / sing-box / v2ray / Surge 形式変換、TCP+TLS 活性プローブ、Netflix / Disney+ / ChatGPT アンロック検出。Go 単一バイナリ、Docker 不要。

---

## 📜 License

[MIT License](./LICENSE)
