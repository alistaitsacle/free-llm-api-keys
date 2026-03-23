<!--
  SEO: chaves API LLM grátis, API GPT grátis, API Claude grátis, API DeepSeek grátis,
  chaves API IA grátis, API compatível com OpenAI, modelos de linguagem grátis
-->

<div align="center">

<img src="./assets/banner.jpg" alt="Chaves API LLM Grátis — GPT-5.4, Claude, DeepSeek, Gemini, Grok, 90+ Modelos" width="100%">

<br>

A forma mais fácil de acessar APIs de LLM gratuitamente — sem cartão de crédito, sem cadastro
<br>
Copie uma chave da tabela, cole no seu app e comece a construir

<br>

[![Stars](https://img.shields.io/github/stars/alistaitsacle/free-llm-api-keys?style=for-the-badge&logo=github)](https://github.com/alistaitsacle/free-llm-api-keys/stargazers)
[![Last Commit](https://img.shields.io/github/last-commit/alistaitsacle/free-llm-api-keys?style=for-the-badge)](https://github.com/alistaitsacle/free-llm-api-keys/commits)
[![Keys](https://img.shields.io/badge/Chaves_Disponíveis-19-brightgreen?style=for-the-badge)]()
[![Models](https://img.shields.io/badge/Modelos-90+-blue?style=for-the-badge)]()

**⭐ Star neste repo = mais chaves grátis para todos**

[English](./README.md) | [中文](./README_CN.md) | [日本語](./README_JA.md) | [한국어](./README_KO.md) | [Español](./README_ES.md) | Português

</div>

---

## 💡 Por que este projeto?

A IA está mudando tudo, mas a maioria das APIs está trancada atrás de cartões de crédito e paywalls. Nem todos têm acesso — especialmente estudantes, hobbyistas e desenvolvedores em regiões onde esses serviços não estão disponíveis.

Eu uso APIs de LLM intensivamente no meu trabalho. Tenho capacidade ociosa que seria desperdiçada. Então decidi compartilhar — chaves grátis, sem condições, atualizadas diariamente.

**Sem cartão de crédito. Sem cadastro. Copie, cole e comece a construir.**

---

## 📋 Chaves Disponíveis

Consulte a lista atualizada de chaves no **[README em inglês](./README.md#-available-keys)**.

Todas as chaves são compatíveis com **OpenAI SDK**. Base URL: `https://aiapiv2.pekpik.com/v1`

---

## 🚀 Como Usar

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://aiapiv2.pekpik.com/v1",
    api_key="COLE_SUA_CHAVE_AQUI"
)

response = client.chat.completions.create(
    model="gpt-5.4",
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
| **OpenAI** | gpt-5.4, gpt-5.4-mini, gpt-5.4-nano, gpt-5.4-pro | Último GPT |
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

## 📜 Licença

[MIT License](./LICENSE)
