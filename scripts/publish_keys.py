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

FEATURED_GROUP_ORDER = [
    "DeepSeek",
    "Multi-Model (GPT-5.4 / Claude / DeepSeek / Gemini auto-rotate)",
    "Gemini",
    "GPT-5.4",
    "Claude Sonnet",
]

FEATURED_MODEL_SPECS = [
    {
        "group": "DeepSeek",
        "model": "deepseek-chat",
        "target": 2,
        "budget_usd": 20,
        "rpm": 20,
        "duration_hours": 48,
        "desc_en": "Everyday chat, coding, translation, writing — most stable default",
        "desc_cn": "日常对话、代码生成、翻译写作，最稳定默认入口",
    },
    {
        "group": "Multi-Model (GPT-5.4 / Claude / DeepSeek / Gemini auto-rotate)",
        "model": "smart-chat",
        "target": 2,
        "budget_usd": 50,
        "rpm": 10,
        "duration_hours": 48,
        "desc_en": "Auto-routes across currently healthy low-cost chat backends",
        "desc_cn": "自动路由到当前健康的低成本聊天模型",
    },
    {
        "group": "Gemini",
        "model": "gemini-2.5-flash",
        "target": 2,
        "budget_usd": 20,
        "rpm": 20,
        "duration_hours": 48,
        "desc_en": "Fast Gemini option for long-context general chat",
        "desc_cn": "Gemini 快速模型，适合长上下文通用对话",
    },
    {
        "group": "GPT-5.4",
        "model": "gpt-5.4",
        "target": 1,
        "budget_usd": 50,
        "rpm": 5,
        "duration_hours": 48,
        "desc_en": "Premium GPT flagship for quality-sensitive chat and coding",
        "desc_cn": "GPT 旗舰模型，适合高质量对话和代码场景",
    },
    {
        "group": "Claude Sonnet",
        "model": "claude-sonnet-4-6",
        "target": 1,
        "budget_usd": 50,
        "rpm": 5,
        "duration_hours": 48,
        "desc_en": "Premium Claude Sonnet for writing, code review, and long answers",
        "desc_cn": "Claude Sonnet，适合写作、代码审查和长回答",
    },
]

GROUP_ALIASES = {
    "Multi-Model (GPT-5.4 / Claude / DeepSeek / Gemini auto-rotate)": [
        "Multi-Model (GPT-5.4 / Claude / DeepSeek / Gemini auto-rotate)",
        "多模型聚合（GPT-5.4 / Claude / DeepSeek / Gemini 自动轮询）",
    ],
    "GPT-5.4": ["GPT-5.4"],
    "Claude Sonnet": ["Claude Sonnet"],
    "DeepSeek": ["DeepSeek"],
    "Gemini": ["Gemini"],
    "Image / Audio / Embedding": ["Image / Audio / Embedding", "图像 / 语音 / 向量化"],
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
        data = api_request("GET", f"/api/keys?status=active&page={page}&page_size=100")
        batch = data.get("keys", [])
        keys.extend(batch)
        total = int(data.get("total", len(keys)))
        if len(keys) >= total or not batch:
            return keys
        page += 1


def fetch_recommended_models() -> list[dict]:
    data = api_request("GET", "/api/models")
    models = data.get("models", data if isinstance(data, list) else [])
    return [m for m in models if m.get("recommended")]


def check_budget() -> float:
    data = api_request("GET", "/api/budget")
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
    data = api_request("POST", "/api/keys/batch", {"keys": requests})
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
    data = api_request("POST", "/api/keys/status", {"keys": keys})
    deleted, warn = extract_bad_keys_from_status(data)
    if deleted:
        try:
            api_request("DELETE", "/api/keys/batch", {"keys": deleted})
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
            "### 优先从这里开始：DeepSeek → smart-chat → Gemini\n\n"
            "- `deepseek-chat` — 响应快、稳定，适合日常使用。\n"
            "- `smart-chat` — 自动路由到当前健康的低成本聊天模型。\n"
            "- `gemini-2.5-flash` — Gemini 快速模型，适合长上下文通用对话。\n\n"
            "需要更高质量时再使用 `gpt-5.4` 或 `claude-sonnet-4-6`，它们不会作为默认免费高并发入口。\n\n"
        )
    return (
        "### Start here: DeepSeek → smart-chat → Gemini\n\n"
        "- `deepseek-chat` — fast, stable, and best for everyday use.\n"
        "- `smart-chat` — auto-routes across currently healthy low-cost chat backends.\n"
        "- `gemini-2.5-flash` — fast Gemini option for long-context general chat.\n\n"
        "Use `gpt-5.4` or `claude-sonnet-4-6` when you need premium quality; they are intentionally not the default free high-volume path.\n\n"
    )


def strip_start_here_blocks(text: str, lang: str) -> str:
    markers = [
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
    if lang == "cn" and group == "Multi-Model (GPT-5.4 / Claude / DeepSeek / Gemini auto-rotate)":
        return "多模型聚合（GPT-5.4 / Claude / DeepSeek / Gemini 自动轮询）"
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
        "DeepSeek": ["Multi-Model (GPT-5.4 / Claude / DeepSeek / Gemini auto-rotate)", "Gemini", "GPT-5.4", "Claude Sonnet", "Kimi", "Image / Audio / Embedding"],
        "Multi-Model (GPT-5.4 / Claude / DeepSeek / Gemini auto-rotate)": ["Gemini", "GPT-5.4", "Claude Sonnet", "Kimi", "Image / Audio / Embedding"],
        "Gemini": ["GPT-5.4", "Claude Sonnet", "Kimi", "Image / Audio / Embedding"],
        "GPT-5.4": ["Claude Sonnet", "Kimi", "Image / Audio / Embedding"],
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
        if group == "Multi-Model (GPT-5.4 / Claude / DeepSeek / Gemini auto-rotate)":
            anchor = first_existing_heading_index(text, ["Image / Audio / Embedding"])
            if anchor is None:
                anchor = text.find("## 📅 Changelog")
        elif group == "DeepSeek":
            anchor = first_existing_heading_index(text, ["Gemini", "Kimi", "Multi-Model (GPT-5.4 / Claude / DeepSeek / Gemini auto-rotate)"])
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
    return len(re.findall(r"^\| `sk-[A-Za-z0-9]+` \|", text, re.M))


def update_badge(text: str, count: int, lang: str) -> str:
    if lang == "cn":
        return re.sub(r"可用_Key-\d+-brightgreen", f"可用_Key-{count}-brightgreen", text, count=1)
    return re.sub(r"Available_Keys-\d+-brightgreen", f"Available_Keys-{count}-brightgreen", text, count=1)


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


def git_commit_and_push(new_count: int, deleted_count: int) -> None:
    paths = [README_PATH, README_CN_PATH]
    if contains_conflict_markers(paths):
        print("README contains conflict markers; skip commit", file=sys.stderr)
        return
    subprocess.run(["git", "-C", REPO_PATH, "add", "README.md", "README_CN.md"], capture_output=True, text=True)
    diff = subprocess.run(["git", "-C", REPO_PATH, "diff", "--cached", "--quiet"], capture_output=True, text=True)
    if diff.returncode == 0:
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
        data = api_request("GET", "/api/budget")
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
