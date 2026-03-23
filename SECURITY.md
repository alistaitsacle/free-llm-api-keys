# Security Policy

## About the Keys

All API keys in this repository (prefixed with `sk-`) are **tokens issued by our own gateway platform**. They are NOT upstream provider keys.

- Each key has independent rate limits and daily quotas
- Keys expire automatically (typically within 24-48 hours)
- No upstream credentials are exposed in this repository

## Reporting a Vulnerability

If you discover a security vulnerability, please **DO NOT** open a public issue. Email us instead and we will respond within 48 hours.

## Responsible Use

- Do not attempt to bypass rate limits or quota restrictions
- Do not use the keys for illegal or harmful purposes
- Do not attempt to reverse-engineer the gateway
