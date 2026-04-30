#!/usr/bin/env python3
"""Publish temporary free LLM API keys to the public README.

The script is intentionally self-contained because it runs from cron/GitHub Actions
against Key Manager. It cleans dead keys, tops up featured public models, updates
README.md/README_CN.md, then commits and pushes the generated result.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

REPO_PATH = str(Path(__file__).resolve().parents[1])
README_PATH = str(Path(REPO_PATH) / "README.md")
README_CN_PATH = str(Path(REPO_PATH) / "README_CN.md")

KM_URL = os.getenv("KEY_MANAGER_URL", "https://aiapiv2.pekpik.com/km")
KM_TOKEN = os.getenv("KEY_MANAGER_TOKEN") or os.getenv("KEY_MANAGER_ADMIN_TOKEN", "")

BOT_NAME = os.getenv("GIT_AUTHOR_NAME", "FreeLLMShare Bot")
BOT_EMAIL = os.getenv("GIT_AUTHOR_EMAIL", "bot@freellmshare.com")

MULTI_MODEL_GROUP_EN = "Multi-Model (GPT-5.5 / Claude / DeepSeek / Gemini auto-rotate)"
MULTI_MODEL_GROUP_CN = "多模型聚合（GPT-5.5 / Claude / DeepSeek / Gemini 自动轮询）"
MULTI_MODEL_GROUP_LEGACY_EN = "Multi-Model (GPT-5.4 / Claude / DeepSeek / Gemini auto-rotate)"
MULTI_MODEL_GROUP_LEGACY_CN = "多模型聚合（GPT-5.4 / Claude / DeepSeek / Gemini 自动轮询）"

FEATURED_GROUP_ORDER = [
    "GPT-5.5",
    "Claude Opus 4.7",
    "Gemini",
    "DeepSeek",
    MULTI_MODEL_GROUP_EN,
]

FEATURED_MODEL_SPECS = [
    {
        "group": "GPT-5.5",
        "model": "gpt-5.5",
        "target": 6,
        "budget_usd": 20,
        "rpm": 5,
        "duration_hours": 48,
        "desc_en": "Premium GPT flagship",
        "desc_cn": "GPT 旗舰模型",
    },
    {
        "group": "Claude Opus 4.7",
        "model": "claude-opus-4-7",
        "target": 6,
        "budget_usd": 20,
        "rpm": 5,
        "duration_hours": 48,
        "desc_en": "Claude Opus flagship",
        "desc_cn": "Claude Opus 旗舰模型",
    },
    {
        "group": "Gemini",
        "model": "gemini-2.5-flash",
        "target": 6,
        "budget_usd": 20,
        "rpm": 20,
        "duration_hours": 48,
        "desc_en": "Fast Gemini option for long-context general chat",
        "desc_cn": "Gemini 快速模型，适合长上下文通用对话",
    },
    {
        "group": "DeepSeek",
        "model": "deepseek-chat",
        "target": 6,
        "budget_usd": 20,
        "rpm": 20,
        "duration_hours": 48,
        "desc_en": "Everyday chat, coding, translation, writing",
        "desc_cn": "日常对话、代码生成、翻译写作",
    },
    {
        "group": MULTI_MODEL_GROUP_EN,
        "model": "smart-chat",
        "target": 6,
        "budget_usd": 20,
        "rpm": 10,
        "duration_hours": 48,
        "desc_en": "Auto-routes across currently healthy low-cost chat backends",
        "desc_cn": "自动路由到当前健康的低成本聊天模型",
    },
]

GROUP_ALIASES = {
    MULTI_MODEL_GROUP_EN: [
        MULTI_MODEL_GROUP_EN,
        MULTI_MODEL_GROUP_CN,
        MULTI_MODEL_GROUP_LEGACY_EN,
        MULTI_MODEL_GROUP_LEGACY_CN,
    ],
    "GPT-5.5": ["GPT-5.5", "GPT-5.4"],
    "Claude Opus 4.7": ["Claude Opus 4.7", "Claude Sonnet", "Claude"],
    "Claude Sonnet": ["Claude Sonnet"],
    "DeepSeek": ["DeepSeek"],
    "Gemini": ["Gemini"],
    "Image / Audio / Embedding": ["Image / Audio / Embedding", "图像 / 语音 / 向量化"],
    "Kimi": ["Kimi"],
}

MODEL_TO_GROUP = {spec["model"]: spec["group"] for spec in FEATURED_MODEL_SPECS}
MODEL_TO_SPEC = {spec["model"]: spec for spec in FEATURED_MODEL_SPECS}


def now_utc8() -> datetime:
    return datetime.now(timezone.utc) + timedelta(hours=8)


def display_stamp() -> str:
    return now_utc8().strftime("%m-%d %H:%M")


def date_stamp() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def api_request(method: str, path: str, body: dict | None = None) -> dict:
    if not KM_TOKEN:
        raise RuntimeError("KEY_MANAGER_TOKEN or KEY_MANAGER_ADMIN_TOKEN is required")
    url = f"{KM_URL.rstrip('/')}/{path.lstrip('/')}"
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {KM_TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "free-llm-api-keys-publisher/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {url} failed: {exc.code} {detail[:500]}") from exc


def normalize_models(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v) for v in value if str(v)]
    if isinstance(value, str):
        return [part.strip() for part in value.split(",") if part.strip()]
    return [str(value)]


def list_active_keys() -> list[dict]:
    keys: list[dict] = []
    page = 1
    while True:
        data = api_request("GET", f"/keys?status=active&page={page}&page_size=100")
        batch = data.get("keys", [])
        keys.extend(batch)
        total = int(data.get("total", len(keys)))
        if len(keys) >= total or not batch:
            return keys
        page += 1


def fetch_recommended_models() -> list[dict]:
    data = api_request("GET", "/models")
    models = data.get("models", data if isinstance(data, list) else [])
    return [m for m in models if m.get("recommended")]


def check_budget() -> float:
    data = api_request("GET", "/budget")
    return float(data.get("remaining_budget_usd", 0) or 0)


def build_featured_key_requests(active_keys: Iterable[dict], available_models: Iterable[str], remaining_budget_usd: float) -> list[dict]:
    """Return Key Manager batch-create payload entries for missing featured keys."""
    available = set(available_models)
    counts = {spec["model"]: 0 for spec in FEATURED_MODEL_SPECS}
    for item in active_keys:
        for model in normalize_models(item.get("models") or item.get("model_limits") or item.get("model")):
            if model in counts:
                counts[model] += 1

    remaining = float(remaining_budget_usd)
    today = now_utc8().strftime("%m%d")
    requests: list[dict] = []
    for spec in FEATURED_MODEL_SPECS:
        model = spec["model"]
        if model not in available:
            continue
        missing = max(0, int(spec["target"]) - counts.get(model, 0))
        for idx in range(missing):
            budget = float(spec["budget_usd"])
            if remaining < budget:
                return requests
            safe_model = re.sub(r"[^a-z0-9]+", "", model.lower())[:14]
            requests.append(
                {
                    "name": f"free-{safe_model}-featured-{today}-{idx + 1}",
                    "models": [model],
                    "budget_usd": budget,
                    "duration_hours": int(spec["duration_hours"]),
                    "rpm": int(spec["rpm"]),
                    "note": "public README featured key",
                }
            )
            remaining -= budget
    return requests


def create_keys(recommended_models: list[dict], remaining_budget_usd: float) -> dict[str, list[dict]]:
    active_keys = list_active_keys()
    available = {m.get("id") or m.get("model") for m in recommended_models}
    available.update({spec["model"] for spec in FEATURED_MODEL_SPECS})
    requests = build_featured_key_requests(active_keys, available, remaining_budget_usd)
    if not requests:
        return {}
    data = api_request("POST", "/keys/batch", {"keys": requests})
    created = data.get("created", [])
    grouped: dict[str, list[dict]] = {}
    for item in created:
        models = normalize_models(item.get("models"))
        model = models[0] if models else ""
        group = MODEL_TO_GROUP.get(model, model)
        spec = MODEL_TO_SPEC.get(model, {})
        grouped.setdefault(group, []).append(
            {
                "key": item.get("key", ""),
                "model": model,
                "budget": f"${int(float(item.get('budget_usd', 0)))}",
                "rpm": f"{int(item.get('rpm', spec.get('rpm', 5)))} RPM",
                "expires": str(item.get("expires_at", ""))[:10],
                "use_case": spec.get("desc_en", ""),
                "use_case_cn": spec.get("desc_cn", spec.get("desc_en", "")),
            }
        )
    return grouped


def extract_readme_keys(text: str) -> list[str]:
    return re.findall(r"`(sk-[A-Za-z0-9]+)`", text)


def extract_bad_keys_from_status(data: dict) -> tuple[list[str], list[str]]:
    raw = data.get("results", data.get("keys", []))
    if isinstance(raw, dict):
        items = [{"key": key, **(value if isinstance(value, dict) else {"status": value})} for key, value in raw.items()]
    else:
        items = raw
    deleted_statuses = {"expired", "exhausted", "not_found", "deleted", "inactive", "revoked"}
    deleted: list[str] = []
    warn: list[str] = []
    for item in items:
        key = item.get("key") if isinstance(item, dict) else None
        status = item.get("status") if isinstance(item, dict) else None
        if not key:
            continue
        if status in deleted_statuses:
            deleted.append(key)
        elif status and status != "active":
            warn.append(key)
    return deleted, warn


def clean_expired_keys() -> tuple[list[str], list[str]]:
    text = Path(README_PATH).read_text(encoding="utf-8") if Path(README_PATH).exists() else ""
    keys = extract_readme_keys(text)
    if not keys:
        return [], []
    data = api_request("POST", "/keys/status", {"keys": keys})
    deleted, warn = extract_bad_keys_from_status(data)
    if deleted:
        try:
            api_request("DELETE", "/keys/batch", {"keys": deleted})
        except RuntimeError:
            pass
    return deleted, warn


def remove_key_rows(text: str, deleted_keys: Iterable[str]) -> str:
    deleted = {k for k in deleted_keys if k}
    if not deleted:
        return text
    lines = []
    for line in text.splitlines():
        if line.startswith("| `sk-") and any(f"`{key}`" in line for key in deleted):
            continue
        lines.append(line)
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")


def section_pattern(group: str) -> re.Pattern:
    aliases = GROUP_ALIASES.get(group, [group])
    names = "|".join(re.escape(alias) for alias in aliases)
    return re.compile(rf"^### (?:{names})(?: `[^`]+`)?\n(?:(?!^### |^## ).*\n?)*", re.M)


def remove_group_sections(text: str, groups: Iterable[str]) -> str:
    for group in groups:
        text = section_pattern(group).sub("", text)
    return re.sub(r"\n{4,}", "\n\n\n", text)


def start_here_block(lang: str) -> str:
    if lang == "cn":
        return (
            "### 重点模型\n\n"
            "覆盖 GPT-5.5、Claude Opus 4.7、Gemini、DeepSeek、smart-chat 等模型。\n"
            "Key 会全天轮换；当旗舰模型暂时补货中时，自动以 smart-chat 兜底 Key 替代，复制即可请求。\n\n"
        )
    return (
        "### Featured models\n\n"
        "GPT-5.5, Claude Opus 4.7, Gemini, DeepSeek, smart-chat and more.\n"
        "Keys rotate throughout the day. When a flagship is restocking we surface a smart-chat fallback key so you can always copy and call.\n\n"
    )


def strip_start_here_blocks(text: str, lang: str) -> str:
    markers = [
        "### 重点模型" if lang == "cn" else "### Featured models",
        "### 优先从这里开始：DeepSeek → smart-chat → Gemini" if lang == "cn" else "### Start here: DeepSeek → smart-chat → Gemini",
        "### 优先从这里开始：GPT → Claude → DeepSeek" if lang == "cn" else "### Start here: GPT → Claude → DeepSeek",
    ]
    cursor = min((pos for marker in markers if (pos := text.find(marker)) != -1), default=-1)
    while cursor != -1:
        current_marker = next(marker for marker in markers if text.startswith(marker, cursor))
        next_h3 = text.find("\n### ", cursor + len(current_marker))
        next_h2 = text.find("\n## ", cursor + len(current_marker))
        candidates = [pos for pos in (next_h3, next_h2) if pos != -1]
        block_end = min(candidates) if candidates else len(text)
        block = text[cursor:block_end]
        sep = block.rfind("---")
        if sep != -1:
            block_end = cursor + sep + len("---")
            while block_end < len(text) and text[block_end] in " \t\r\n":
                block_end += 1
        text = text[:cursor].rstrip() + "\n\n" + text[block_end:].lstrip("\n")
        cursor = min((pos for marker in markers if (pos := text.find(marker)) != -1), default=-1)
    return text


def ensure_start_here(text: str, lang: str) -> str:
    text = strip_start_here_blocks(text, lang)
    verify = "**[在这里验证你的 Key]" if lang == "cn" else "**[Verify your key here]"
    idx = text.find(verify)
    if idx == -1:
        return text
    line_end = text.find("\n", idx)
    if line_end == -1:
        return text + "\n\n" + start_here_block(lang)
    return text[: line_end + 1] + "\n" + start_here_block(lang) + text[line_end + 1 :]


def localized_group_name(group: str, lang: str) -> str:
    if lang == "cn" and group in (MULTI_MODEL_GROUP_EN, MULTI_MODEL_GROUP_LEGACY_EN):
        return MULTI_MODEL_GROUP_CN
    if group == MULTI_MODEL_GROUP_LEGACY_EN:
        return MULTI_MODEL_GROUP_EN
    return group


def render_group_section(group: str, rows: list[dict], lang: str) -> str:
    title = localized_group_name(group, lang)
    if lang == "cn":
        header = "| Key | 模型 | 状态 | 预算 | 速率限制 | 过期时间 | 说明 |\n|-----|------|------|------|---------|---------|------|\n"
        rendered_rows = []
        for row in rows:
            desc = row.get("use_case_cn") or row.get("use_case") or ""
            rendered_rows.append(
                f"| `{row['key']}` | {row['model']} | 🆕 新增 | {row['budget']} | {row['rpm']} | {row['expires']} | {desc} |"
            )
    else:
        header = "| Key | Model | Status | Budget | Rate Limit | Expires | Description |\n|-----|-------|--------|--------|------------|---------|-------------|\n"
        rendered_rows = [
            f"| `{row['key']}` | {row['model']} | 🆕 New | {row['budget']} | {row['rpm']} | {row['expires']} | {row.get('use_case', '')} |"
            for row in rows
        ]
    return f"### {title} `{display_stamp()}`\n\n" + header + "\n".join(rendered_rows) + "\n\n---\n\n"


def first_existing_heading_index(text: str, groups: Iterable[str]) -> int | None:
    positions = []
    for group in groups:
        for alias in GROUP_ALIASES.get(group, [group]):
            m = re.search(rf"^### {re.escape(alias)}(?: `[^`]+`)?", text, re.M)
            if m:
                positions.append(m.start())
    return min(positions) if positions else None


def insert_sections(text: str, grouped_keys: dict[str, list[dict]], lang: str) -> str:
    if not grouped_keys:
        return text
    text = ensure_start_here(text, lang)
    groups_to_replace = [group for group in FEATURED_GROUP_ORDER if grouped_keys.get(group)]
    groups_to_replace += [group for group in grouped_keys if group not in groups_to_replace]
    text = remove_group_sections(text, groups_to_replace)

    anchor_after_group = {
        "DeepSeek": [MULTI_MODEL_GROUP_EN, "Gemini", "GPT-5.5", "Claude Sonnet", "Kimi", "Image / Audio / Embedding"],
        MULTI_MODEL_GROUP_EN: ["Gemini", "GPT-5.5", "Claude Sonnet", "Kimi", "Image / Audio / Embedding"],
        "Gemini": ["GPT-5.5", "Claude Sonnet", "Kimi", "Image / Audio / Embedding"],
        "GPT-5.5": ["Claude Sonnet", "Kimi", "Image / Audio / Embedding"],
        "Claude Sonnet": ["Kimi", "Image / Audio / Embedding"],
    }

    inserted_groups = []
    for group in FEATURED_GROUP_ORDER:
        if not grouped_keys.get(group):
            continue
        section = render_group_section(group, grouped_keys[group], lang)
        anchor = first_existing_heading_index(text, anchor_after_group.get(group, []))
        if anchor is None:
            anchor = text.find("## 📅 Changelog")
        text = text[:anchor] + section + text[anchor:] if anchor != -1 else text + "\n" + section
        inserted_groups.append(group)

    other_groups = [group for group in grouped_keys if group not in inserted_groups]
    for group in other_groups:
        section = render_group_section(group, grouped_keys[group], lang)
        if group == MULTI_MODEL_GROUP_EN:
            anchor = first_existing_heading_index(text, ["Image / Audio / Embedding"])
            if anchor is None:
                anchor = text.find("## 📅 Changelog")
        elif group == "DeepSeek":
            anchor = first_existing_heading_index(text, ["Gemini", "Kimi", MULTI_MODEL_GROUP_EN])
            if anchor is None:
                anchor = text.find("## 📅 Changelog")
        else:
            anchor = text.find("## 📅 Changelog")
        text = text[:anchor] + section + text[anchor:] if anchor != -1 else text + "\n" + section
    return re.sub(r"\n{4,}", "\n\n\n", text)


def dedupe_start_here(text: str, lang: str) -> str:
    marker = "### 优先从这里开始：DeepSeek → smart-chat → Gemini" if lang == "cn" else "### Start here: DeepSeek → smart-chat → Gemini"
    first = text.find(marker)
    if first == -1:
        return text
    cursor = text.find(marker, first + len(marker))
    while cursor != -1:
        end = text.find("\n### ", cursor + len(marker))
        next_h2 = text.find("\n## ", cursor + len(marker))
        candidates = [pos for pos in (end, next_h2) if pos != -1]
        block_end = min(candidates) if candidates else len(text)
        block = text[cursor:block_end]
        sep = block.rfind("---")
        if sep != -1:
            block_end = cursor + sep + len("---")
            while block_end < len(text) and text[block_end] in " \t\r\n":
                block_end += 1
        text = text[:cursor].rstrip() + "\n\n" + text[block_end:].lstrip("\n")
        cursor = text.find(marker, first + len(marker))
    return text


def update_timestamp(text: str, lang: str) -> str:
    if lang == "cn":
        pattern = r"> ⏰ 最后更新： .*?\(UTC\+8\)"
        replacement = f"> ⏰ 最后更新： {now_utc8().strftime('%Y-%m-%d %H:%M')} (UTC+8)"
    else:
        pattern = r"> ⏰ Last updated: .*?\(UTC\+8\)"
        replacement = f"> ⏰ Last updated: {now_utc8().strftime('%Y-%m-%d %H:%M')} (UTC+8)"
    return re.sub(pattern, replacement, text, count=1)


def count_table_keys(text: str) -> int:
    """Count unique real `sk-` keys in Markdown tables.

    - Rows that carry the smart-chat `<!-- fallback -->` marker are ignored
      (they are a duplicate of a smart-chat row already counted elsewhere).
    - The same `sk-` token appearing in multiple rows only counts once so the
      shelf never double-counts fallback references.
    """
    seen: set[str] = set()
    for line in text.splitlines():
        if FALLBACK_MARKER in line:
            continue
        m = re.match(r"^\|\s*`(sk-[A-Za-z0-9]+)`\s*\|", line)
        if m:
            seen.add(m.group(1))
    return len(seen)


FALLBACK_MARKER = "<!-- fallback -->"


def update_badge(text: str, count: int, lang: str) -> str:
    if lang == "cn":
        return re.sub(r"可用_Key-\d+-brightgreen", f"可用_Key-{count}-brightgreen", text, count=1)
    return re.sub(r"Available_Keys-\d+-brightgreen", f"Available_Keys-{count}-brightgreen", text, count=1)


MODEL_SHELF = [
    {
        "group": "GPT-5.5",
        "title_en": "GPT-5.5",
        "title_cn": "GPT-5.5",
        "model": "gpt-5.5",
        "desc_en": "Premium GPT flagship",
        "desc_cn": "GPT 旗舰模型",
        "aliases": ["GPT-5.5", "GPT-5.4"],
    },
    {
        "group": "Claude Opus 4.7",
        "title_en": "Claude Opus 4.7",
        "title_cn": "Claude Opus 4.7",
        "model": "claude-opus-4-7",
        "desc_en": "Claude Opus flagship",
        "desc_cn": "Claude Opus 旗舰模型",
        "aliases": ["Claude Opus 4.7", "Claude Sonnet", "Claude"],
    },
    {
        "group": "Gemini",
        "title_en": "Gemini",
        "title_cn": "Gemini",
        "model": "gemini-2.5-flash",
        "desc_en": "Fast Gemini option for long-context general chat",
        "desc_cn": "Gemini 快速模型，适合长上下文通用对话",
        "aliases": ["Gemini"],
    },
    {
        "group": "DeepSeek",
        "title_en": "DeepSeek",
        "title_cn": "DeepSeek",
        "model": "deepseek-chat",
        "desc_en": "Everyday chat, coding, translation, writing",
        "desc_cn": "日常对话、代码生成、翻译写作",
        "aliases": ["DeepSeek"],
    },
    {
        "group": MULTI_MODEL_GROUP_EN,
        "title_en": MULTI_MODEL_GROUP_EN,
        "title_cn": MULTI_MODEL_GROUP_CN,
        "model": "smart-chat",
        "desc_en": "Auto-routes across currently healthy low-cost chat backends",
        "desc_cn": "自动路由到当前健康的低成本聊天模型",
        "aliases": [
            MULTI_MODEL_GROUP_EN,
            MULTI_MODEL_GROUP_CN,
            MULTI_MODEL_GROUP_LEGACY_EN,
            MULTI_MODEL_GROUP_LEGACY_CN,
        ],
    },
    {
        "group": "Kimi",
        "title_en": "Kimi",
        "title_cn": "Kimi",
        "model": "kimi-k2.5",
        "desc_en": "Kimi long-context general model",
        "desc_cn": "Kimi 长上下文通用模型",
        "aliases": ["Kimi"],
    },
    {
        "group": "Image / Audio / Embedding",
        "title_en": "Image / Audio / Embedding",
        "title_cn": "图像 / 语音 / 向量化",
        "model": "dall-e-3 / tts / embeddings",
        "desc_en": "Image, audio, and embedding models",
        "desc_cn": "图像、语音和向量模型",
        "aliases": ["Image / Audio / Embedding", "图像 / 语音 / 向量化"],
    },
]


def shelf_title(spec: dict, lang: str) -> str:
    return spec["title_cn"] if lang == "cn" else spec["title_en"]


def shelf_header(lang: str) -> str:
    if lang == "cn":
        return "| Key | 模型 | 状态 | 预算 | 速率限制 | 过期时间 | 说明 |\n|-----|------|------|------|---------|---------|------|"
    return "| Key | Model | Status | Budget | Rate Limit | Expires | Description |\n|-----|-------|--------|--------|------------|---------|-------------|"


def restocking_row(spec: dict, lang: str) -> str:
    if lang == "cn":
        return (
            f"| 补货中 | {spec['model']} | 暂时无可用 Key | - | - | 下次刷新 | "
            f"{spec['desc_cn']} |"
        )
    return (
        f"| Restocking | {spec['model']} | Temporarily unavailable | - | - | Next refresh | "
        f"{spec['desc_en']} |"
    )


def pick_fallback_key(rows_by_group: dict[str, list[str]]) -> str | None:
    """Return the first real `sk-` row from the smart-chat / Multi-Model group."""
    for group in (MULTI_MODEL_GROUP_EN, MULTI_MODEL_GROUP_LEGACY_EN):
        for row in rows_by_group.get(group, []):
            if FALLBACK_MARKER in row:
                continue
            if re.match(r"^\|\s*`sk-[A-Za-z0-9]+`\s*\|", row):
                return row
    return None


def _split_table_cells(row: str) -> list[str] | None:
    if not row.startswith("|") or not row.rstrip().endswith("|"):
        return None
    parts = row.strip().strip("|").split("|")
    return [part.strip() for part in parts]


def adapt_fallback_row(smart_row: str, spec: dict, lang: str) -> str | None:
    """Rewrite a smart-chat key row to act as a fallback for a flagship shelf.

    Keeps `key`, `budget`, `rate limit`, `expires` from smart-chat; overrides
    the `model` column (so users clearly see it routes to the target flagship),
    the `status` column, and the `description` column. A trailing HTML comment
    lets `count_table_keys` skip this duplicate to avoid inflating the badge.
    """
    cells = _split_table_cells(smart_row)
    if not cells or len(cells) < 7:
        return None
    key_cell, _model, _status, budget, rpm, expires, *rest_desc = cells
    if not re.match(r"^`sk-[A-Za-z0-9]+`$", key_cell):
        return None
    if lang == "cn":
        model_cell = f"smart-chat ({spec['model']} 兜底)"
        status_cell = "🛟 兜底"
        desc_cell = f"{spec['desc_cn']} — 补货期间由 smart-chat 自动路由"
    else:
        model_cell = f"smart-chat ({spec['model']} fallback)"
        status_cell = "🛟 Fallback"
        desc_cell = f"{spec['desc_en']} — auto-routes via smart-chat while restocking"
    row = (
        f"| {key_cell} | {model_cell} | {status_cell} | {budget} | {rpm} | "
        f"{expires} | {desc_cell} | {FALLBACK_MARKER}"
    )
    return row


def rows_for_shelf_spec(spec: dict, rows_by_group: dict[str, list[str]], fallback: str | None, lang: str) -> list[str]:
    """Resolve rows for a given shelf entry, using smart-chat fallback when empty.

    - Real rows always win.
    - If the shelf entry is the smart-chat / Multi-Model itself, fall through
      to `restocking_row` (we never point smart-chat at itself as fallback).
    - Other flagship/shelf entries with no real key adopt the fallback row if
      available; otherwise show the legacy Restocking placeholder.
    """
    real_rows = [row for row in rows_by_group.get(spec["group"], []) if FALLBACK_MARKER not in row]
    if real_rows:
        return real_rows
    if spec["group"] in (MULTI_MODEL_GROUP_EN, MULTI_MODEL_GROUP_LEGACY_EN):
        return [restocking_row(spec, lang)]
    if fallback:
        adapted = adapt_fallback_row(fallback, spec, lang)
        if adapted:
            return [adapted]
    return [restocking_row(spec, lang)]


def spec_for_heading(title: str) -> dict | None:
    plain_title = title.split(" `", 1)[0].strip()
    for spec in MODEL_SHELF:
        if any(plain_title.startswith(alias) for alias in spec["aliases"]):
            return spec
    return None


def collect_shelf_rows(section: str) -> dict[str, list[str]]:
    rows = {spec["group"]: [] for spec in MODEL_SHELF}
    headings = list(re.finditer(r"^### (.+)$", section, re.MULTILINE))
    for idx, heading in enumerate(headings):
        spec = spec_for_heading(heading.group(1))
        if not spec:
            continue
        block_end = headings[idx + 1].start() if idx + 1 < len(headings) else len(section)
        block = section[heading.end():block_end]
        for line in block.splitlines():
            if FALLBACK_MARKER in line:
                # Fallback rows are re-generated from smart-chat each render;
                # never carry them over as if they were real keys of this shelf.
                continue
            if re.match(r"^\|\s*`sk-[A-Za-z0-9]+`\s*\|", line):
                rows[spec["group"]].append(line)
    return rows


def available_keys_bounds(text: str) -> tuple[int, int] | None:
    start = text.find("## 📋")
    if start == -1:
        return None
    tail_match = re.search(r"\n## (?!📋)", text[start + len("## 📋"):])
    end = start + len("## 📋") + tail_match.start() if tail_match else len(text)
    return start, end


def render_shelf_section(rows_by_group: dict[str, list[str]], lang: str) -> str:
    sections = []
    stamp = display_stamp()
    fallback = pick_fallback_key(rows_by_group)
    for spec in MODEL_SHELF:
        rows = rows_for_shelf_spec(spec, rows_by_group, fallback, lang)
        sections.append(
            f"### {shelf_title(spec, lang)} `{stamp}`\n\n"
            + shelf_header(lang)
            + "\n"
            + "\n".join(rows)
            + "\n\n---"
        )
    return "\n\n".join(sections).rstrip("-").rstrip()


def normalize_model_shelf(text: str, lang: str) -> str:
    bounds = available_keys_bounds(text)
    if bounds is None:
        return text
    start, end = bounds
    section = strip_unavailable_details(text[start:end])

    headings = list(re.finditer(r"^### (.+)$", section, re.MULTILINE))
    if not headings:
        return text
    shelf_start = None
    shelf_end = None
    for idx, heading in enumerate(headings):
        if spec_for_heading(heading.group(1)):
            if shelf_start is None:
                shelf_start = heading.start()
            shelf_end = headings[idx + 1].start() if idx + 1 < len(headings) else len(section)

    if shelf_start is None:
        return text

    rows_by_group = collect_shelf_rows(section)
    normalized = (
        section[:shelf_start].rstrip()
        + "\n\n"
        + render_shelf_section(rows_by_group, lang)
        + "\n\n"
        + section[shelf_end:].lstrip()
    )
    normalized = re.sub(r"\n{4,}", "\n\n\n", normalized)
    return text[:start] + normalized + text[end:]


def remove_empty_shelf_sections_from_segment(segment: str) -> str:
    headings = list(re.finditer(r"^### (.+)$", segment, re.MULTILINE))
    if not headings:
        return segment

    pieces = []
    cursor = 0
    for idx, heading in enumerate(headings):
        block_start = heading.start()
        block_end = headings[idx + 1].start() if idx + 1 < len(headings) else len(segment)
        block = segment[block_start:block_end]
        pieces.append(segment[cursor:block_start])
        if not (spec_for_heading(heading.group(1)) and is_empty_key_group(block)):
            pieces.append(block)
        cursor = block_end
    pieces.append(segment[cursor:])
    return re.sub(r"\n{4,}", "\n\n\n", "".join(pieces))


def remove_orphan_empty_model_sections(text: str) -> str:
    bounds = available_keys_bounds(text)
    if bounds is None:
        return text
    start, end = bounds
    return (
        remove_empty_shelf_sections_from_segment(text[:start])
        + text[start:end]
        + remove_empty_shelf_sections_from_segment(text[end:])
    )


MAX_VISIBLE_EMPTY_GROUPS = 2
_UNAVAILABLE_SUMMARY = {
    "en": "Temporarily unavailable models",
    "cn": "暂时不可用模型",
}


def strip_unavailable_details(section: str) -> str:
    summaries = "|".join(re.escape(text) for text in _UNAVAILABLE_SUMMARY.values())
    pattern = re.compile(
        rf"\n*<details>\n<summary><b>(?:{summaries})</b></summary>\n\n.*?\n</details>\n*",
        re.DOTALL,
    )
    return pattern.sub("\n\n", section)


def is_empty_key_group(block: str) -> bool:
    has_key_table = re.search(r"^\|\s*Key\s*\|", block, re.MULTILINE) is not None
    has_key_row = re.search(r"^\|\s*`sk-[A-Za-z0-9]+`\s*\|", block, re.MULTILINE) is not None
    return has_key_table and not has_key_row


def limit_empty_groups(text: str, lang: str, max_visible: int = MAX_VISIBLE_EMPTY_GROUPS) -> str:
    """Keep a small number of empty model groups visible and fold the rest."""
    start = text.find("## 📋")
    if start == -1:
        return text

    tail_match = re.search(r"\n## (?!📋)", text[start + len("## 📋"):])
    end = start + len("## 📋") + tail_match.start() if tail_match else len(text)
    section = strip_unavailable_details(text[start:end])

    headings = list(re.finditer(r"^### (.+)$", section, re.MULTILINE))
    if not headings:
        return text[:start] + section + text[end:]

    pieces = []
    extras = []
    cursor = 0
    empty_seen = 0
    for idx, heading in enumerate(headings):
        block_start = heading.start()
        block_end = headings[idx + 1].start() if idx + 1 < len(headings) else len(section)
        block = section[block_start:block_end]
        pieces.append(section[cursor:block_start])
        if is_empty_key_group(block):
            empty_seen += 1
            if empty_seen > max_visible:
                extras.append(block.strip())
            else:
                pieces.append(block)
        else:
            pieces.append(block)
        cursor = block_end
    pieces.append(section[cursor:])

    section = "".join(pieces).rstrip()
    if extras:
        summary = _UNAVAILABLE_SUMMARY.get(lang, _UNAVAILABLE_SUMMARY["en"])
        section += (
            f"\n\n<details>\n<summary><b>{summary}</b></summary>\n\n"
            + "\n\n".join(extras)
            + "\n</details>\n"
        )

    return text[:start] + section + text[end:]


def models_summary(grouped_keys: dict[str, list[dict]]) -> str:
    models = []
    for rows in grouped_keys.values():
        for row in rows:
            model = row.get("model", "")
            if model and model not in models:
                models.append(model)
    return ", ".join(models)


def changelog_line(grouped_keys: dict[str, list[dict]], deleted_count: int, lang: str) -> str | None:
    created_count = sum(len(rows) for rows in grouped_keys.values())
    if created_count == 0 and deleted_count == 0:
        return None
    summary = models_summary(grouped_keys) or "no new keys"
    if lang == "cn":
        return f"- 🆕 新增 {created_count} 个 Key ({summary})，清理 {deleted_count} 个过期 Key"
    return f"- 🆕 Added {created_count} keys ({summary}), cleaned {deleted_count} expired"


def ensure_changelog_details(text: str, lang: str) -> str:
    idx = text.find("## 📅 Changelog")
    if idx == -1 or "<details>" in text[idx : idx + 300]:
        return text
    next_idx = text.find("\n## ", idx + 1)
    if next_idx == -1:
        body = text[idx + len("## 📅 Changelog") :]
        rest = ""
    else:
        body = text[idx + len("## 📅 Changelog") : next_idx]
        rest = text[next_idx:]
    summary = "<summary><b>显示更新历史</b></summary>" if lang == "cn" else "<summary><b>Show changelog history</b></summary>"
    body_text = re.sub(r"\n*---\s*$", "", body.strip()).replace("</details>", "").strip()
    wrapped = f"## 📅 Changelog\n\n<details>\n{summary}\n\n{body_text}\n</details>\n\n---\n"
    return text[:idx] + wrapped + rest


def normalize_changelog_markup(text: str) -> str:
    idx = text.find("## 📅 Changelog")
    if idx == -1:
        return text
    next_idx = text.find("\n## ", idx + 1)
    if next_idx == -1:
        next_idx = len(text)
    section = text[idx:next_idx]
    first_details = section.find("<details>")
    if first_details == -1:
        return text
    prefix = section[: first_details + len("<details>")]
    body = section[first_details + len("<details>") :]
    body = re.sub(r"\n<details>\n<summary><b>.*?</b></summary>\n", "\n", body)
    body = re.sub(r"(</details>\n)(?:\s*</details>\n)+", r"\1", body)
    return text[:idx] + prefix + body + text[next_idx:]


def update_changelog(text: str, grouped_keys: dict[str, list[dict]], deleted_count: int, lang: str) -> str:
    text = ensure_changelog_details(text, lang)
    line = changelog_line(grouped_keys, deleted_count, lang)
    if not line:
        return text
    idx = text.find("## 📅 Changelog")
    if idx == -1:
        return text
    today = date_stamp()
    today_header = f"### {today}\n"
    if line in text:
        return text
    close_idx = text.find("</details>", idx)
    section_end = close_idx if close_idx != -1 else (text.find("\n## ", idx + 1) if text.find("\n## ", idx + 1) != -1 else len(text))
    today_idx = text.find(today_header, idx, section_end)
    if today_idx != -1:
        insert_at = today_idx + len(today_header)
        return text[:insert_at] + line + "\n" + text[insert_at:]
    insert_at = text.find("\n", idx + len("## 📅 Changelog"))
    if "<details>" in text[idx:section_end]:
        summary_end = text.find("</summary>", idx, section_end)
        insert_at = text.find("\n", summary_end, section_end) + 1 if summary_end != -1 else insert_at + 1
    else:
        insert_at = insert_at + 1
    return text[:insert_at] + f"\n{today_header}{line}\n" + text[insert_at:]


def update_readme(path: str, grouped_keys: dict[str, list[dict]], deleted_keys: list[str], warn_keys: list[str], lang: str = "en") -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    text = remove_key_rows(text, deleted_keys)
    text = update_timestamp(text, lang)
    text = ensure_start_here(text, lang)
    text = dedupe_start_here(text, lang)
    text = insert_sections(text, grouped_keys, lang)
    text = dedupe_start_here(text, lang)
    text = update_changelog(text, grouped_keys, len(deleted_keys), lang)
    text = re.sub(r"(\|[-| ]+\|)\n\n(\| `sk-)", r"\1\n\2", text)
    text = normalize_changelog_markup(text)
    text = re.sub(r"(</details>\n)(?:\s*</details>\n)+", r"\1", text)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    text = normalize_model_shelf(text, lang=lang)
    text = remove_orphan_empty_model_sections(text)
    text = update_badge(text, count_table_keys(text), lang)
    p.write_text(text, encoding="utf-8")


def contains_conflict_markers(paths: Iterable[str]) -> bool:
    for path in paths:
        p = Path(path)
        if p.exists() and re.search(r"^(<<<<<<<|=======|>>>>>>>)", p.read_text(encoding="utf-8", errors="replace"), re.M):
            return True
    return False


def sync_repo_before_publish() -> bool:
    result = subprocess.run(["git", "-C", REPO_PATH, "pull", "--rebase", "origin", "main"], capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr or result.stdout, file=sys.stderr)
        return False
    return True


def _readme_has_meaningful_diff(paths: Iterable[str]) -> bool:
    """Return True when the staged README diff contains changes other than
    the `Last updated` timestamp + shelf stamps.

    Filters out lines that start with `+> ⏰`, `-> ⏰`, and rows that only
    differ in their `` `MM-DD HH:MM` `` stamp near shelf headings. When the
    only diff is a cosmetic timestamp bump we skip the commit entirely so
    that hourly cleanup runs don't flood the public repo with empty
    `+0 keys, -1 expired` churn.
    """
    diff = subprocess.run(
        ["git", "-C", REPO_PATH, "diff", "--cached", "--unified=0", "--", *paths],
        capture_output=True,
        text=True,
    )
    if diff.returncode != 0:
        return True  # err on the safe side
    for line in diff.stdout.splitlines():
        if not line or line[0] not in "+-":
            continue
        if line.startswith("+++ ") or line.startswith("--- "):
            continue
        content = line[1:]
        stripped = content.strip()
        if not stripped:
            continue
        if stripped.startswith("> ⏰"):
            continue
        # Shelf heading timestamp lines, e.g. `### GPT-5.5 \`04-30 17:52\``
        if re.match(r"^### .+ `\d{2}-\d{2} \d{2}:\d{2}`$", stripped):
            continue
        return True
    return False


def git_commit_and_push(new_count: int, deleted_count: int) -> None:
    paths = [README_PATH, README_CN_PATH]
    if contains_conflict_markers(paths):
        print("README contains conflict markers; skip commit", file=sys.stderr)
        return
    subprocess.run(["git", "-C", REPO_PATH, "add", "README.md", "README_CN.md"], capture_output=True, text=True)
    diff = subprocess.run(["git", "-C", REPO_PATH, "diff", "--cached", "--quiet"], capture_output=True, text=True)
    if diff.returncode == 0:
        return
    # When nothing new or interesting changed (only timestamps), drop the
    # diff quietly instead of shipping a noisy commit. This keeps the public
    # repo history readable and maximises SEO / star-worthy "activity" signal.
    if new_count == 0 and deleted_count == 0 and not _readme_has_meaningful_diff(["README.md", "README_CN.md"]):
        subprocess.run(["git", "-C", REPO_PATH, "reset", "HEAD", "--", "README.md", "README_CN.md"], capture_output=True, text=True)
        subprocess.run(["git", "-C", REPO_PATH, "checkout", "--", "README.md", "README_CN.md"], capture_output=True, text=True)
        return
    msg = f"feat: +{new_count} keys, -{deleted_count} expired ({date_stamp()} {now_utc8().strftime('%H:%M')})"
    env = os.environ.copy()
    env.update({
        "GIT_AUTHOR_NAME": BOT_NAME,
        "GIT_AUTHOR_EMAIL": BOT_EMAIL,
        "GIT_COMMITTER_NAME": BOT_NAME,
        "GIT_COMMITTER_EMAIL": BOT_EMAIL,
    })
    subprocess.run(["git", "-C", REPO_PATH, "commit", "-m", msg], capture_output=True, text=True)
    subprocess.run(["git", "-C", REPO_PATH, "push"], capture_output=True, text=True)


def log_usage_stats() -> None:
    try:
        data = api_request("GET", "/budget")
        print(json.dumps(data, ensure_ascii=False))
    except Exception as exc:
        print(f"budget log skipped: {exc}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cleanup-only", action="store_true")
    args = parser.parse_args()

    if not sync_repo_before_publish():
        return

    deleted_keys, warn_keys = clean_expired_keys()
    if args.cleanup_only:
        update_readme(README_PATH, {}, deleted_keys, warn_keys, lang="en")
        update_readme(README_CN_PATH, {}, deleted_keys, warn_keys, lang="cn")
        git_commit_and_push(0, len(deleted_keys))
        log_usage_stats()
        return

    remaining = check_budget()
    if remaining <= 0:
        update_readme(README_PATH, {}, deleted_keys, warn_keys, lang="en")
        update_readme(README_CN_PATH, {}, deleted_keys, warn_keys, lang="cn")
        git_commit_and_push(0, len(deleted_keys))
        log_usage_stats()
        return

    recommended_models = fetch_recommended_models()
    grouped_keys = create_keys(recommended_models, remaining)
    update_readme(README_PATH, grouped_keys, deleted_keys, warn_keys, lang="en")
    update_readme(README_CN_PATH, grouped_keys, deleted_keys, warn_keys, lang="cn")
    git_commit_and_push(sum(len(rows) for rows in grouped_keys.values()), len(deleted_keys))
    log_usage_stats()


if __name__ == "__main__":
    main()
