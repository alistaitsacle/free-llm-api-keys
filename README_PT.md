<!--
  SEO: chaves API LLM grátis, API GPT grátis, API Claude grátis, API DeepSeek grátis,
  chaves API IA grátis, API compatível com OpenAI, modelos de linguagem grátis
-->

<div align="center">

<img src="./assets/banner.jpg" alt="Chaves API LLM Grátis — GPT-5.5, Claude, DeepSeek, Gemini, Grok, 90+ Modelos" width="100%">

<br>

A forma mais fácil de acessar APIs de LLM gratuitamente — sem cartão de crédito, sem cadastro
<br>
Copie uma chave da tabela, cole no seu app e comece a construir

<br>

[![Stars](https://img.shields.io/github/stars/alistaitsacle/free-llm-api-keys?style=for-the-badge&logo=github)](https://github.com/alistaitsacle/free-llm-api-keys/stargazers)
[![Last Commit](https://img.shields.io/github/last-commit/alistaitsacle/free-llm-api-keys?style=for-the-badge)](https://github.com/alistaitsacle/free-llm-api-keys/commits)
[![Keys](https://img.shields.io/badge/Chaves_Disponíveis-37-brightgreen?style=for-the-badge)]()
[![Models](https://img.shields.io/badge/Modelos-90+-blue?style=for-the-badge)]()
[![Follow on X](https://img.shields.io/badge/Siga_no_X-novas_chaves-000000?style=for-the-badge&logo=x)](https://x.com/getkeyway)

**⭐ Star neste repo = mais chaves grátis para todos**
<br>
**🔔 [Siga @getkeyway no X](https://x.com/getkeyway) para novas chaves, modelos e status de disponibilidade**

[English](./README.md) | [中文](./README_CN.md) | [日本語](./README_JA.md) | [한국어](./README_KO.md) | [Español](./README_ES.md) | Português

</div>

---

## 💡 Por que este projeto?

A IA está mudando tudo, mas a maioria das APIs está trancada atrás de cartões de crédito e paywalls. Nem todos têm acesso — especialmente estudantes, hobbyistas e desenvolvedores em regiões onde esses serviços não estão disponíveis.

Eu uso APIs de LLM intensivamente no meu trabalho. Tenho capacidade ociosa que seria desperdiçada. Então decidi compartilhar — chaves grátis, sem condições, atualizadas diariamente.

**Sem cartão de crédito. Sem cadastro. Copie, cole e comece a construir.**

---

## 📋 Chaves Disponíveis

> ⏰ Última atualização: 2026-06-17 01:52 (UTC+8)

### Modelos em destaque

### Claude Opus 4.7 `06-17 01:52`

| Key | Modelo | Status | Orçamento | Taxa | Expira | Descrição |
|-----|--------|--------|-----------|------|--------|-------------|
| `sk-FdL9Ej9GoPAtISe7FihuJFbb2rpuLi6yXCfVC2Q2eBakp6R7` | claude-opus-4-7 | 🆕 Nova | $19 | 5 RPM | 2026-06-18 | Claude Opus flagship |
| `sk-l1y11wVV1t1Bo1bHijjSQjn1aCNebgf3fhtLz7zZg61IfVAr` | claude-opus-4-7 | 🆕 Nova | $19 | 5 RPM | 2026-06-18 | Claude Opus flagship |
| `sk-FFeCdCNr0q87U3KxL4Yk4b43XlExLSb2zJxvxsxBkI0RhknE` | claude-opus-4-7 | 🆕 Nova | $19 | 5 RPM | 2026-06-18 | Claude Opus flagship |
| `sk-r2U9eBeefc2bozPLK54ycSI8Z5kJrLRfPeZGA507xffRHD7S` | claude-opus-4-7 | 🆕 Nova | $19 | 5 RPM | 2026-06-18 | Claude Opus flagship |
| `sk-6QKd19iDga9wevkxASe8zPHOCu0D3FKwCrNfqsXq5Fl8hOXi` | claude-opus-4-7 | 🆕 Nova | $14 | 5 RPM | 2026-06-18 | Claude Opus flagship |

### Kimi `06-17 01:52`

| Key | Modelo | Status | Orçamento | Taxa | Expira | Descrição |
|-----|--------|--------|-----------|------|--------|-------------|
| `sk-esGqzsH0pAHTuXSLqIec6gsPo9rF4Q9varLYHBm6HowfFHlQ` | kimi-k2.5 | 🆕 Nova | $20 | 10 RPM | 2026-06-18 | Kimi long-context general model |
| `sk-G0Imv2dGtIJBAsN4zaawGhzzXu3JEtLE2xuXh6c52GjrwEC0` | kimi-k2.5 | 🆕 Nova | $20 | 10 RPM | 2026-06-18 | Kimi long-context general model |
| `sk-wCsRmdxdoRp6C8gFwgb0mAOc6JqM2BA789FO2xUC5lF69NAn` | kimi-k2.5 | 🆕 Nova | $20 | 10 RPM | 2026-06-18 | Kimi long-context general model |
| `sk-0TQkcXVNFaslZK0aLznDjKPxNfSXAsiGyXnQ9i2bxWH4UBFo` | kimi-k2.5 | 🆕 Nova | $20 | 10 RPM | 2026-06-18 | Kimi long-context general model |

## 🚀 Como Usar

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://aiapiv2.pekpik.com/v1",
    api_key="COLE_SUA_CHAVE_AQUI"
)

response = client.chat.completions.create(
    model="gpt-5.5",
    messages=[{"role": "user", "content": "Olá!"}]
)
print(response.choices[0].message.content)
```

### Ferramentas Compatíveis

| Ferramenta | Configuração |
|------------|-------------|
| **Cursor** | Settings → Models → API Key + Base URL `https://aiapiv2.pekpik.com/v1` |
| **ChatBox** | Configurações → API → Provedor personalizado |
| **LobeChat** | Configurações → Modelo de linguagem → OpenAI → API Key + Proxy URL |
| **Qualquer app compatível com OpenAI** | Configurar Base URL como `https://aiapiv2.pekpik.com/v1` |

---

## 🤖 Modelos Suportados

**90+ modelos** de 8+ provedores.

| Provedor | Modelos | Notas |
|----------|---------|-------|
| **OpenAI** | gpt-5.5, gpt-5.5-mini, gpt-4 | Último GPT |
| **Anthropic** | claude-opus-4-6, claude-sonnet-4-6, claude-haiku-4-5 | Último Claude |
| **DeepSeek** | deepseek-chat (V3), deepseek-reasoner (R1) | Chat + raciocínio |
| **Google** | gemini-3.1-flash-lite, gemini-3.1-flash-image | Gemini 3.1 |
| **xAI** | grok-4.20-beta | Último Grok |
| **Mistral** | mistral-medium, codestral, devstral | Código + chat |
| **Mais** | Cohere, Qwen, GLM-5, DALL-E 3, TTS, Embeddings | Em expansão contínua |

---

## ❓ Perguntas Frequentes

**Chave não funciona?** As chaves são compartilhadas publicamente. O orçamento pode ter sido consumido por outros usuários. Este repo é **atualizado automaticamente 3-5 vezes por dia**. Volte mais tarde.

**É seguro?** São tokens da nossa própria plataforma, NÃO chaves de provedores terceiros. Cada chave tem orçamento e limites de velocidade independentes.

**Quais regiões são suportadas?** Disponível globalmente. Acesso direto de qualquer país.

---

## 🔗 Recursos gratuitos relacionados

- **[free-vpn-subscriptions](https://github.com/Au1rxx/free-vpn-subscriptions)** — Links de assinatura Clash / sing-box / v2ray atualizados a cada hora. Todos os nós verificados por TCP e ordenados por latência. Sem cadastro, sem instalar nenhum binário.

---

## 📜 Licença

[MIT License](./LICENSE)
