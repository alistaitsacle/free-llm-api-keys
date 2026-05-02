<!--
  SEO: claves API LLM gratis, API GPT gratis, API Claude gratis, API DeepSeek gratis,
  claves API IA gratis, API compatible con OpenAI, modelos de lenguaje gratis
-->

<div align="center">

<img src="./assets/banner.jpg" alt="Claves API LLM Gratis — GPT-5.5, Claude, DeepSeek, Gemini, Grok, 90+ Modelos" width="100%">

<br>

La forma más fácil de acceder a APIs de LLM gratis — sin tarjeta de crédito, sin registro
<br>
Copia una clave de la tabla, pégala en tu app y empieza a construir

<br>

[![Stars](https://img.shields.io/github/stars/alistaitsacle/free-llm-api-keys?style=for-the-badge&logo=github)](https://github.com/alistaitsacle/free-llm-api-keys/stargazers)
[![Last Commit](https://img.shields.io/github/last-commit/alistaitsacle/free-llm-api-keys?style=for-the-badge)](https://github.com/alistaitsacle/free-llm-api-keys/commits)
[![Keys](https://img.shields.io/badge/Claves_Disponibles-19-brightgreen?style=for-the-badge)]()
[![Models](https://img.shields.io/badge/Modelos-90+-blue?style=for-the-badge)]()

**⭐ Star este repo = más claves gratis para todos**

[English](./README.md) | [中文](./README_CN.md) | [日本語](./README_JA.md) | [한국어](./README_KO.md) | Español | [Português](./README_PT.md)

</div>

---

## 💡 ¿Por qué este proyecto?

La IA está cambiando todo, pero la mayoría de las APIs están bloqueadas detrás de tarjetas de crédito y muros de pago. No todos tienen acceso — especialmente estudiantes, aficionados y desarrolladores en regiones donde estos servicios no están disponibles.

Uso APIs de LLM intensivamente en mi trabajo. Tengo capacidad sobrante que de otro modo se desperdiciaría. Así que decidí compartirla — claves gratis, sin condiciones, actualizadas diariamente.

**Sin tarjeta de crédito. Sin registro. Solo copia, pega y construye.**

---

## 📋 Claves Disponibles

Consulta la lista actualizada de claves en el **[README en inglés](./README.md#-available-keys)**.

Todas las claves son compatibles con **OpenAI SDK**. Base URL: `https://aiapiv2.pekpik.com/v1`

---

## 🚀 Cómo Usar

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://aiapiv2.pekpik.com/v1",
    api_key="PEGA_TU_CLAVE_AQUI"
)

response = client.chat.completions.create(
    model="gpt-5.5",
    messages=[{"role": "user", "content": "¡Hola!"}]
)
print(response.choices[0].message.content)
```

### Herramientas Compatibles

| Herramienta | Configuración |
|-------------|---------------|
| **Cursor** | Settings → Models → API Key + Base URL `https://aiapiv2.pekpik.com/v1` |
| **ChatBox** | Configuración → API → Proveedor personalizado |
| **LobeChat** | Configuración → Modelo de lenguaje → OpenAI → API Key + Proxy URL |
| **Cualquier app compatible con OpenAI** | Configurar Base URL como `https://aiapiv2.pekpik.com/v1` |

---

## 🤖 Modelos Soportados

**90+ modelos** de 8+ proveedores.

| Proveedor | Modelos | Notas |
|-----------|---------|-------|
| **OpenAI** | gpt-5.5, gpt-5.4-mini, gpt-4 | Último GPT |
| **Anthropic** | claude-opus-4-6, claude-sonnet-4-6, claude-haiku-4-5 | Último Claude |
| **DeepSeek** | deepseek-chat (V3), deepseek-reasoner (R1) | Chat + razonamiento |
| **Google** | gemini-3.1-flash-lite, gemini-3.1-flash-image | Gemini 3.1 |
| **xAI** | grok-4.20-beta | Último Grok |
| **Mistral** | mistral-medium, codestral, devstral | Código + chat |
| **Más** | Cohere, Qwen, GLM-5, DALL-E 3, TTS, Embeddings | En expansión continua |

---

## ❓ Preguntas Frecuentes

**¿La clave no funciona?** Las claves se comparten públicamente. El presupuesto puede haber sido consumido por otros usuarios. Este repo se **actualiza automáticamente 3-5 veces al día**. Vuelve más tarde.

**¿Es seguro?** Son tokens de nuestra propia plataforma, NO claves de proveedores terceros. Cada clave tiene presupuesto y límites de velocidad independientes.

**¿Qué regiones son compatibles?** Disponible globalmente. Acceso directo desde cualquier país.

---

## 🔗 Recursos gratuitos relacionados

- **[free-vpn-subscriptions](https://github.com/Au1rxx/free-vpn-subscriptions)** — Enlaces de suscripción Clash / sing-box / v2ray actualizados cada hora. Todos los nodos verificados por TCP y ordenados por latencia. Sin registro, sin instalar ningún binario.

---

## 📜 Licencia

[MIT License](./LICENSE)
