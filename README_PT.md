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
[![Keys](https://img.shields.io/badge/Chaves_Disponíveis-35-brightgreen?style=for-the-badge)]()
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

> ⏰ Última atualização: 2026-06-29 14:37 (UTC+8)

### Modelos em destaque

### Multi-Modelo (GPT-5.5 / Claude / DeepSeek / Gemini roteamento automático) `06-29 14:37`

| Key | Modelo | Status | Orçamento | Taxa | Expira | Descrição |
|-----|--------|--------|-----------|------|--------|-------------|
| `sk-YmxOOOiccUXRF2iLOhW49m5UFNqlho1rZhM8ux9kSmq7Wp6f` | smart-chat | 🆕 Nova | $20 | 10 RPM | 2026-07-01 | Auto-routes across currently healthy low-cost chat backends |
| `sk-bjGKU9coQpNhyOS5dulWGkoxZm56kCHNDtlAVBzA4V1LL16j` | smart-chat | 🆕 Nova | $20 | 10 RPM | 2026-07-01 | Auto-routes across currently healthy low-cost chat backends |
| `sk-ewxywnq9wzKjACfDKwerEWM0TU8ZgiWamr1Lqc7OCJ1xOeJI` | smart-chat | 🆕 Nova | $20 | 10 RPM | 2026-07-01 | Auto-routes across currently healthy low-cost chat backends |
| `sk-68GjVDsW9Rl03FRNPY2tfvgPp97KfO0HQTB6RIoP490tlLWa` | smart-chat | 🆕 Nova | $20 | 10 RPM | 2026-07-01 | Auto-routes across currently healthy low-cost chat backends |
| `sk-CcsRY3MKpHmumkcjo8F9h214JfjOSprsB6VM0nKcBCkNuy8W` | smart-chat | 🆕 Nova | $20 | 10 RPM | 2026-07-01 | Auto-routes across currently healthy low-cost chat backends |
| `sk-OtQEPQeCHK9ckaYjQKY1hZsj1aFuXegZOdd0dMH1Bh1RjKW8` | smart-chat | 🆕 Nova | $20 | 10 RPM | 2026-07-01 | Auto-routes across currently healthy low-cost chat backends |

### Kimi `06-29 14:37`

| Key | Modelo | Status | Orçamento | Taxa | Expira | Descrição |
|-----|--------|--------|-----------|------|--------|-------------|
| `sk-BMGL2dkghtJa7BC4oGUxvgVMGQHMJ29IURqssDhcy5Gh4tZE` | kimi-k2.5 | 🆕 Nova | $19 | 10 RPM | 2026-07-01 | Kimi long-context general model |
| `sk-HXWkefR0ZvVveLEr3Gcq3DWzBjTKNCBY5jOwAUrJau2tVujH` | kimi-k2.5 | 🆕 Nova | $19 | 10 RPM | 2026-07-01 | Kimi long-context general model |
| `sk-0oQpUsbHJxpAr2cnVC8Lfozx6FdZUXzQOlKS3Qmvknehe6aI` | kimi-k2.5 | 🆕 Nova | $16 | 10 RPM | 2026-07-01 | Kimi long-context general model |
| `sk-JTmttYjjrcYvUfa5Wy8x2QzLhrMJfdK8G9IN0chN6GGZiVzl` | kimi-k2.5 | 🆕 Nova | $19 | 10 RPM | 2026-07-01 | Kimi long-context general model |

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
