#!/usr/bin/env python3
"""Publish temporary free LLM API keys to the public README.

The script is intentionally self-contained because it runs from the production
server cron against Key Manager. It cleans dead keys, tops up featured public
models, updates README.md/README_CN.md, then commits and pushes the generated
result.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

REPO_PATH = str(Path(__file__).resolve().parents[1])
README_PATH = str(Path(REPO_PATH) / "README.md")
README_CN_PATH = str(Path(REPO_PATH) / "README_CN.md")
DOCS_INDEX_PATH = str(Path(REPO_PATH) / "docs" / "index.html")
DOCS_LIVE_STATUS_CSS = """    /* Live status */
    .live-status {
      margin-bottom: 24px; padding: 18px;
      background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.12);
      border-radius: 12px;
    }
    .live-head {
      display: flex; justify-content: space-between; align-items: flex-start;
      gap: 16px; margin-bottom: 14px;
    }
    .eyebrow {
      display: block; margin-bottom: 4px; color: #60a5fa;
      font-size: 0.72rem; font-weight: 700; text-transform: uppercase;
    }
    .live-head h2 { font-size: 1.25rem; color: #f8fafc; }
    .updated { color: #a0b0c0; font-size: 0.78rem; white-space: nowrap; }
    .status-grid {
      display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 8px;
    }
    .status-card {
      display: flex; justify-content: space-between; align-items: center;
      min-height: 44px; padding: 10px 12px; border-radius: 8px;
      background: rgba(0,0,0,0.18); border: 1px solid rgba(255,255,255,0.08);
    }
    .status-card span { color: #b7c3d0; font-size: 0.78rem; line-height: 1.35; }
    .status-card strong { color: #00d4ff; font-size: 1.05rem; }
    .live-note { margin-top: 12px; color: #8899aa; font-size: 0.78rem; line-height: 1.5; }
"""

KM_URL = os.getenv("KEY_MANAGER_URL") or "https://aiapiv2.pekpik.com/km"
KM_TOKEN = os.getenv("KEY_MANAGER_TOKEN") or os.getenv("KEY_MANAGER_ADMIN_TOKEN", "")
TRANSIENT_HTTP_STATUS = {429, 500, 502, 503, 504}
# Cron interval is 3h, so a 30-60s retry budget is essentially free.
# Linear backoff: sleep = base * attempt; 6 attempts at base=3.0s ⇒ 3+6+9+12+15 = 45s window.
KM_RETRY_ATTEMPTS = int(os.getenv("KM_RETRY_ATTEMPTS", "6"))
KM_RETRY_SLEEP_SECONDS = float(os.getenv("KM_RETRY_SLEEP_SECONDS", "3.0"))

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
    "Kimi",
    "Image / Audio / Embedding",
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
    {
        "group": "Kimi",
        "model": "kimi-k2.5",
        "target": 6,
        "budget_usd": 20,
        "rpm": 10,
        "duration_hours": 48,
        "desc_en": "Kimi long-context general model",
        "desc_cn": "Kimi 长上下文通用模型",
    },
    {
        "group": "Image / Audio / Embedding",
        "model": "dall-e-3",
        "target": 3,
        "budget_usd": 20,
        "rpm": 5,
        "duration_hours": 48,
        "desc_en": "Image generation",
        "desc_cn": "图像生成",
    },
    {
        "group": "Image / Audio / Embedding",
        "model": "tts-1-hd",
        "target": 3,
        "budget_usd": 20,
        "rpm": 5,
        "duration_hours": 48,
        "desc_en": "Text-to-speech",
        "desc_cn": "语音合成",
    },
    {
        "group": "Image / Audio / Embedding",
        "model": "text-embedding-3-small",
        "target": 3,
        "budget_usd": 20,
        "rpm": 20,
        "duration_hours": 48,
        "desc_en": "Text embeddings",
        "desc_cn": "文本向量化",
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
FEATURED_MODEL_IDS = set(MODEL_TO_SPEC)


def now_utc8() -> datetime:
    return datetime.now(timezone.utc) + timedelta(hours=8)


def display_stamp() -> str:
    return now_utc8().strftime("%m-%d %H:%M")


def date_stamp() -> str:
    return now_utc8().strftime("%Y-%m-%d")


def api_request(
    method: str,
    path: str,
    body: dict | None = None,
    *,
    retry_attempts: int = KM_RETRY_ATTEMPTS,
    retry_sleep_seconds: float = KM_RETRY_SLEEP_SECONDS,
) -> dict:
    if not KM_TOKEN:
        raise RuntimeError("KEY_MANAGER_TOKEN or KEY_MANAGER_ADMIN_TOKEN is required")
    url = f"{KM_URL.rstrip('/')}/{path.lstrip('/')}"
    data = None if body is None else json.dumps(body).encode("utf-8")
    attempts = max(1, retry_attempts)
    for attempt in range(1, attempts + 1):
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
            message = f"{method} {url} failed: {exc.code} {detail[:500]}"
            if exc.code not in TRANSIENT_HTTP_STATUS or attempt == attempts:
                raise RuntimeError(message) from exc
            print(f"[WARN] transient Key Manager error; retrying {attempt}/{attempts}: {message}", file=sys.stderr)
        except urllib.error.URLError as exc:
            message = f"{method} {url} failed: {exc.reason}"
            if attempt == attempts:
                raise RuntimeError(message) from exc
            print(f"[WARN] transient Key Manager connection error; retrying {attempt}/{attempts}: {message}", file=sys.stderr)
        time.sleep(retry_sleep_seconds * attempt)

    raise RuntimeError(f"{method} {url} failed after {attempts} attempts")


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


def model_identifier(item) -> str:
    if isinstance(item, str):
        return item
    if not isinstance(item, dict):
        return ""
    return str(item.get("id") or item.get("model") or item.get("name") or "").strip()


def model_slug(model: str, limit: int = 14) -> str:
    return re.sub(r"[^a-z0-9]+", "", model.lower())[:limit]


def request_slug(target_model: str, request_model: str) -> str:
    if request_model == target_model:
        return model_slug(target_model)
    return f"{model_slug(target_model)}-via-{model_slug(request_model)}"[:32]


def active_key_target_model(item: dict) -> str | None:
    name = str(item.get("name", "")).lower()
    note = str(item.get("note", "")).lower()
    for spec in FEATURED_MODEL_SPECS:
        target_model = spec["model"]
        if name.startswith(f"free-{model_slug(target_model)}-via-"):
            return target_model
        if f"for {target_model.lower()} " in note or note.endswith(f"for {target_model.lower()}"):
            return target_model
    return None


def _float_or_none(value) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def recommended_model_has_capacity(item) -> bool:
    if isinstance(item, dict) and item.get("recommended") is False:
        return False
    if not model_identifier(item):
        return False
    if not isinstance(item, dict):
        return True

    for field in ("available", "enabled", "active"):
        if item.get(field) is False:
            return False

    for field in ("status", "state", "availability", "health"):
        value = str(item.get(field, "")).strip().lower()
        if value in {"disabled", "inactive", "unavailable", "unhealthy", "exhausted", "sold_out", "no_quota", "quota_exhausted"}:
            return False

    quota_fields = (
        "remaining_quota",
        "quota_remaining",
        "quota",
        "daily_quota_remaining",
        "remaining_requests",
        "requests_remaining",
        "remaining_budget_usd",
        "available_budget_usd",
        "budget_remaining",
        "remaining_credits",
        "credits_remaining",
        "balance_remaining",
    )
    for field in quota_fields:
        value = _float_or_none(item.get(field))
        if value is not None and value <= 0:
            return False
    return True


def model_capability(model: str, item: dict | None = None) -> str:
    hint = ""
    if item:
        hint = " ".join(str(item.get(field, "")) for field in ("type", "capability", "category", "mode"))
    text = f"{model} {hint}".lower()
    if "embed" in text:
        return "embedding"
    if any(token in text for token in ("tts", "speech", "audio", "voice")):
        return "audio"
    if any(token in text for token in ("image", "dall", "gpt-image", "flux", "sdxl")):
        return "image"
    return "chat"


def model_fallback_family(model: str, item: dict | None = None) -> str:
    capability = model_capability(model, item)
    if capability != "chat":
        return capability

    slug = model_slug(model, limit=80)
    if "gpt55" in slug:
        return "gpt-5.5"
    if "claudeopus47" in slug or "claude47opus" in slug:
        return "claude-opus-4-7"
    if "gemini" in slug:
        return "gemini"
    if "deepseek" in slug:
        return "deepseek"
    if "smartchat" in slug or "flagshipchat" in slug:
        return "multi-model"
    if "kimi" in slug or "moonshot" in slug:
        return "kimi"
    return ""


def can_substitute_model(target_model: str, candidate_model: str, candidate: dict | None = None) -> bool:
    target_family = model_fallback_family(target_model)
    candidate_family = model_fallback_family(candidate_model, candidate)
    return bool(target_family and target_family == candidate_family)


def recommended_model_candidates(recommended_models: Iterable[dict]) -> tuple[dict[str, dict], dict[str, list[dict]]]:
    direct: dict[str, dict] = {}
    by_capability: dict[str, list[dict]] = {"chat": [], "image": [], "audio": [], "embedding": []}
    for item in recommended_models:
        model = model_identifier(item)
        if not model or not recommended_model_has_capacity(item):
            continue
        meta = item if isinstance(item, dict) else {"id": model, "recommended": True}
        direct.setdefault(model, meta)
        by_capability.setdefault(model_capability(model, meta), []).append(meta)
    return direct, by_capability


def select_recommended_model(spec: dict, direct: dict[str, dict], by_capability: dict[str, list[dict]]) -> str | None:
    model = spec["model"]
    if model in direct:
        return model
    capability = model_capability(model)
    for candidate in by_capability.get(capability, []):
        candidate_model = model_identifier(candidate)
        if (
            candidate_model
            and candidate_model not in FEATURED_MODEL_IDS
            and can_substitute_model(model, candidate_model, candidate)
        ):
            return candidate_model
    return None


def public_key_request(request: dict) -> dict:
    return {key: value for key, value in request.items() if not key.startswith("_")}


def build_featured_key_requests(active_keys: Iterable[dict], recommended_models: Iterable[dict], remaining_budget_usd: float) -> list[dict]:
    """Return Key Manager batch-create payload entries for missing featured keys."""
    direct, by_capability = recommended_model_candidates(recommended_models)
    counts = {spec["model"]: 0 for spec in FEATURED_MODEL_SPECS}
    for item in active_keys:
        counted = False
        for model in normalize_models(item.get("models") or item.get("model_limits") or item.get("model")):
            if model in counts:
                counts[model] += 1
                counted = True
        if not counted and isinstance(item, dict):
            target_model = active_key_target_model(item)
            if target_model in counts:
                counts[target_model] += 1

    remaining = float(remaining_budget_usd)
    today = now_utc8().strftime("%m%d")
    requests: list[dict] = []
    for spec in FEATURED_MODEL_SPECS:
        target_model = spec["model"]
        request_model = select_recommended_model(spec, direct, by_capability)
        if not request_model:
            continue
        missing = max(0, int(spec["target"]) - counts.get(target_model, 0))
        for idx in range(missing):
            budget = float(spec["budget_usd"])
            if remaining < budget:
                return requests
            requests.append(
                {
                    "name": f"free-{request_slug(target_model, request_model)}-featured-{today}-{idx + 1}",
                    "models": [request_model],
                    "budget_usd": budget,
                    "duration_hours": int(spec["duration_hours"]),
                    "rpm": int(spec["rpm"]),
                    "note": f"public README featured key for {target_model} using {request_model}",
                    "_display_group": spec["group"],
                    "_display_model": request_model,
                    "_display_desc_en": spec["desc_en"] if request_model == target_model else f"KM recommended alternative for {spec['desc_en']}",
                    "_display_desc_cn": spec["desc_cn"] if request_model == target_model else f"KM 推荐的可用替代模型：{spec['desc_cn']}",
                    "_requested_for_model": target_model,
                }
            )
            remaining -= budget
    return requests


def create_keys(recommended_models: list[dict], remaining_budget_usd: float) -> dict[str, list[dict]]:
    active_keys = list_active_keys()
    requests = build_featured_key_requests(active_keys, recommended_models, remaining_budget_usd)
    if not requests:
        return {}
    data = api_request("POST", "/keys/batch", {"keys": [public_key_request(request) for request in requests]})
    created = data.get("created", [])
    request_meta_by_name = {request["name"]: request for request in requests}
    request_meta_by_model: dict[str, list[dict]] = {}
    for request in requests:
        request_meta_by_model.setdefault(request["models"][0], []).append(request)
    grouped: dict[str, list[dict]] = {}
    for item in created:
        models = normalize_models(item.get("models"))
        model = models[0] if models else ""
        request_meta = request_meta_by_name.get(str(item.get("name", "")))
        if request_meta is None and model in request_meta_by_model and request_meta_by_model[model]:
            request_meta = request_meta_by_model[model].pop(0)
        group = (request_meta or {}).get("_display_group") or MODEL_TO_GROUP.get(model, model)
        spec = MODEL_TO_SPEC.get(model, {})
        desc_en = (request_meta or {}).get("_display_desc_en") or spec.get("desc_en", "")
        desc_cn = (request_meta or {}).get("_display_desc_cn") or spec.get("desc_cn", spec.get("desc_en", ""))
        grouped.setdefault(group, []).append(
            {
                "key": item.get("key", ""),
                "model": (request_meta or {}).get("_display_model") or model,
                "budget": f"${int(float(item.get('budget_usd', 0)))}",
                "rpm": f"{int(item.get('rpm', spec.get('rpm', 5)))} RPM",
                "expires": str(item.get("expires_at", ""))[:10],
                "use_case": desc_en,
                "use_case_cn": desc_cn,
            }
        )
    return grouped


FALLBACK_MARKER = "<!-- fallback -->"


def existing_readme_keys(paths: Iterable[str]) -> set[str]:
    """Return the union of `sk-` tokens currently rendered in the READMEs."""
    seen: set[str] = set()
    for path in paths:
        p = Path(path)
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        for line in text.splitlines():
            if FALLBACK_MARKER in line:
                continue
            m = re.match(r"^\|\s*`(sk-[A-Za-z0-9]+)`\s*\|", line)
            if m:
                seen.add(m.group(1))
    return seen


def grouped_from_active(active_keys: Iterable[dict], already_rendered: set[str]) -> dict[str, list[dict]]:
    """Build a grouped_keys payload for update_readme() from server-side active keys.

    The payload only carries keys whose token is NOT yet present in either
    README. This way insert_sections() will splice them in alongside the rows
    collect_shelf_rows() already preserves, lifting Opus/Kimi/Multi-Model back
    to their real density without re-creating anything on the Key Manager.
    """
    grouped: dict[str, list[dict]] = {}
    for item in active_keys:
        key = item.get("key") or item.get("token") or ""
        if not key or key in already_rendered:
            continue
        models = normalize_models(item.get("models") or item.get("model_limits") or item.get("model"))
        model = models[0] if models else ""
        spec = MODEL_TO_SPEC.get(model)
        if not spec:
            continue
        group = spec["group"]
        rpm_raw = item.get("rpm") or spec.get("rpm", 5)
        try:
            rpm_int = int(rpm_raw) if rpm_raw is not None else int(spec.get("rpm", 5))
        except (TypeError, ValueError):
            rpm_int = int(spec.get("rpm", 5))
        budget_raw = item.get("budget_usd") or spec.get("budget_usd", 0)
        try:
            budget_int = int(float(budget_raw))
        except (TypeError, ValueError):
            budget_int = int(spec.get("budget_usd", 0))
        grouped.setdefault(group, []).append(
            {
                "key": key,
                "model": model,
                "budget": f"${budget_int}",
                "rpm": f"{rpm_int} RPM",
                "expires": str(item.get("expires_at", ""))[:10],
                "use_case": spec.get("desc_en", ""),
                "use_case_cn": spec.get("desc_cn", spec.get("desc_en", "")),
            }
        )
    return grouped


def sync_from_active() -> dict[str, list[dict]]:
    """Merge server-side active keys into the README without creating new keys.

    Useful from `--cleanup-only` and at the start of the full publish run, so
    the shelf always reflects every live key even if a previous render only
    captured a subset.
    """
    try:
        active = list_active_keys()
    except Exception as exc:
        print(f"sync_from_active skipped: {exc}", file=sys.stderr)
        return {}
    already = existing_readme_keys([README_PATH, README_CN_PATH])
    return grouped_from_active(active, already)


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
    try:
        data = api_request("POST", "/keys/status", {"keys": keys})
    except RuntimeError as exc:
        print(f"status cleanup skipped: {exc}", file=sys.stderr)
        return [], []
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
            "覆盖 GPT-5.5、Claude Opus 4.7、Gemini、DeepSeek、smart-chat、Kimi、图像、语音和向量模型。\n"
            "发布器只展示真实 Key；目标模型没有 KM 推荐或额度不足时，会尝试 KM 推荐且有额度的同一模型家族，仍不可用则留空不展示。\n\n"
        )
    return (
        "### Featured models\n\n"
        "GPT-5.5, Claude Opus 4.7, Gemini, DeepSeek, smart-chat, Kimi, image, audio, and embeddings.\n"
        "The publisher only shows real keys. If a target model has no KM recommendation or quota, it tries a quota-backed KM-recommended model in the same model family; otherwise that shelf stays hidden.\n\n"
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


def available_keys_insert_anchor(text: str) -> int:
    bounds = available_keys_bounds(text)
    if bounds is None:
        changelog = text.find("## 📅 Changelog")
        return changelog if changelog != -1 else len(text)

    start, end = bounds
    section = text[start:end]
    headings = list(re.finditer(r"^### (.+)$", section, re.MULTILINE))
    shelf_positions = [heading.start() for heading in headings if spec_for_heading(heading.group(1))]
    if shelf_positions:
        return start + min(shelf_positions)
    return end


def insert_sections(text: str, grouped_keys: dict[str, list[dict]], lang: str) -> str:
    if not grouped_keys:
        return text
    text = ensure_start_here(text, lang)
    groups_to_replace = [group for group in FEATURED_GROUP_ORDER if grouped_keys.get(group)]
    groups_to_replace += [group for group in grouped_keys if group not in groups_to_replace]
    text = remove_group_sections(text, groups_to_replace)

    sections = []
    inserted_groups = set()
    for group in FEATURED_GROUP_ORDER:
        if not grouped_keys.get(group):
            continue
        sections.append(render_group_section(group, grouped_keys[group], lang))
        inserted_groups.add(group)

    for group in grouped_keys:
        if group in inserted_groups:
            continue
        sections.append(render_group_section(group, grouped_keys[group], lang))

    if not sections:
        return text
    anchor = available_keys_insert_anchor(text)
    block = "\n".join(sections)
    text = text[:anchor].rstrip() + "\n\n" + block + "\n" + text[anchor:].lstrip("\n")
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

    - Legacy synthetic rows carrying the `<!-- fallback -->` marker are ignored.
    - The same `sk-` token appearing in multiple rows only counts once.
    """
    seen: set[str] = set()
    for line in text.splitlines():
        if FALLBACK_MARKER in line:
            continue
        m = re.match(r"^\|\s*`(sk-[A-Za-z0-9]+)`\s*\|", line)
        if m:
            seen.add(m.group(1))
    return len(seen)


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
        "model": "dall-e-3 / tts-1-hd / text-embedding-3-small",
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


def rows_for_shelf_spec(spec: dict, rows_by_group: dict[str, list[str]], lang: str) -> list[str]:
    """Resolve rows for a given shelf entry.

    - Real rows always win.
    - Empty shelf entries stay hidden so the README never shows dead rows or
      synthetic replacement rows.
    """
    real_rows = [row for row in rows_by_group.get(spec["group"], []) if FALLBACK_MARKER not in row]
    if real_rows:
        return real_rows
    return []


def table_row_model(row: str) -> str:
    if not row.startswith("|") or not row.rstrip().endswith("|"):
        return ""
    cells = [part.strip() for part in row.strip().strip("|").split("|")]
    if len(cells) < 2:
        return ""
    return cells[1]


def shelf_row_matches_spec(spec: dict, row: str) -> bool:
    model = table_row_model(row)
    if not model:
        return False
    if spec["group"] == "Image / Audio / Embedding":
        return model_capability(model) in {"image", "audio", "embedding"}
    return model == spec["model"] or can_substitute_model(spec["model"], model)


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
                if shelf_row_matches_spec(spec, line):
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
    for spec in MODEL_SHELF:
        rows = rows_for_shelf_spec(spec, rows_by_group, lang=lang)
        if not rows:
            continue
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


def remove_any_shelf_sections_from_segment(segment: str) -> str:
    """Drop any shelf-spec heading block found outside of ## 📋 Available Keys.

    When a previous render placed a duplicate model block after the License
    section, that copy would linger. Shelf blocks belong inside the Available
    Keys section only, so we strip them wholesale — empty or not — wherever we
    find them outside that boundary.
    """
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
        if not spec_for_heading(heading.group(1)):
            pieces.append(block)
        cursor = block_end
    pieces.append(segment[cursor:])
    cleaned = "".join(pieces)
    # Collapse trailing horizontal separators that lose their previous sibling.
    cleaned = re.sub(r"\n{3,}---\n(?=(?:\n|$))", "\n\n", cleaned)
    return re.sub(r"\n{4,}", "\n\n\n", cleaned)


def remove_orphan_empty_model_sections(text: str) -> str:
    bounds = available_keys_bounds(text)
    if bounds is None:
        return text
    start, end = bounds
    return (
        remove_empty_shelf_sections_from_segment(text[:start])
        + text[start:end]
        + remove_any_shelf_sections_from_segment(text[end:])
    )


MAX_VISIBLE_EMPTY_GROUPS = 2
_UNAVAILABLE_SUMMARY = {
    "en": "Models without a current direct key",
    "cn": "当前无直接 Key 的模型",
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


def normalize_static_copy(text: str, lang: str) -> str:
    if lang == "cn":
        text = re.sub(
            r"> 新 Key 每天\u8865\u8d27 \*\*2 次\*\*，失效 Key 全天自动清理。每个 Key 预算 \$20-\$100，有效期 24-48 小时。",
            "> 新 Key 由服务器定时任务每天多次发布，失效 Key 全天自动清理。每个 Key 预算 $20-$100，有效期 24-48 小时。",
            text,
        )
        text = re.sub(
            r"Key 是公开共享的，额度可能已被用完。本项目新 Key \*\*每天\u8865\u8d27 2 次\*\*，失效 Key 全天自动清理——稍后回来即可。也可以 \*\*Watch → Releases\*\* 接收通知。",
            "Key 是公开共享的，额度可能已被用完。服务器定时任务每天多次发布新 Key，并全天清理失效 Key；稍后回来即可看到最新可用 Key。也可以 **Watch → Releases** 接收通知。",
            text,
        )
        return text

    text = re.sub(
        r"> New keys are " + "restock" + r"ed \*\*" + "twice" + r"\s+daily\*\*\. Expired keys are cleaned throughout the day\. Each key has a budget \(\$20-\$100\) and expires in 24-48 hours\.",
        "> New keys are published multiple times per day by the server cron. Expired keys are cleaned throughout the day. Each key has a budget ($20-$100) and expires in 24-48 hours.",
        text,
    )
    text = re.sub(
        r"Keys are shared publicly, so they may run out of budget\. This repo " + "restock" + r"s new keys \*\*" + "twice" + r"\s+daily\*\* and cleans expired keys throughout the day — just come back later for fresh keys\. You can also \*\*Watch → Releases\*\* to get notified\.",
        "Keys are shared publicly, so they may run out of budget. The server cron publishes fresh keys multiple times per day and cleans expired keys throughout the day, so come back later for currently available keys. You can also **Watch → Releases** to get notified.",
        text,
    )
    return text


def extract_docs_index_summary(readme_text: str) -> tuple[str, int, list[tuple[str, int]]]:
    updated_match = re.search(r"> ⏰ Last updated:\s*(.*?)\s*\(UTC\+8\)", readme_text)
    updated = updated_match.group(1) if updated_match else now_utc8().strftime("%Y-%m-%d %H:%M")

    bounds = available_keys_bounds(readme_text)
    section = readme_text
    if bounds is not None:
        start, end = bounds
        section = readme_text[start:end]

    groups: list[tuple[str, int]] = []
    headings = list(re.finditer(r"^### (.+)$", section, re.MULTILINE))
    for idx, heading in enumerate(headings):
        title = heading.group(1).split(" `", 1)[0].strip()
        block_end = headings[idx + 1].start() if idx + 1 < len(headings) else len(section)
        block = section[heading.end():block_end]
        count = sum(1 for line in block.splitlines() if re.match(r"^\|\s*`sk-[A-Za-z0-9]+`\s*\|", line))
        if count:
            groups.append((title, count))

    return updated, count_table_keys(readme_text), groups


def docs_index_live_block(readme_text: str) -> str:
    updated, total, groups = extract_docs_index_summary(readme_text)
    cards = "\n".join(
        f'        <div class="status-card"><span>{html.escape(name)}</span><strong>{count}</strong></div>'
        for name, count in groups
    )
    if not cards:
        cards = '        <div class="status-card"><span>No live key shelf</span><strong>0</strong></div>'
    return (
        "<!-- live-status:start -->\n"
        '  <section class="live-status" aria-label="Live public key inventory">\n'
        '    <div class="live-head">\n'
        "      <div>\n"
        '        <span class="eyebrow">Live public keys</span>\n'
        f"        <h2>{total} keys available now</h2>\n"
        "      </div>\n"
        f'      <span class="updated">Updated {html.escape(updated)} UTC+8</span>\n'
        "    </div>\n"
        '    <div class="status-grid">\n'
        f"{cards}\n"
        "    </div>\n"
        '    <p class="live-note">The server publishes fresh keys every 3 hours and hides shelves without quota-backed real keys.</p>\n'
        "  </section>\n"
        "<!-- live-status:end -->"
    )


def update_docs_index(readme_path: str = README_PATH, docs_index_path: str = DOCS_INDEX_PATH) -> None:
    docs_path = Path(docs_index_path)
    readme_file = Path(readme_path)
    if not docs_path.exists() or not readme_file.exists():
        return

    text = docs_path.read_text(encoding="utf-8")
    readme_text = readme_file.read_text(encoding="utf-8")
    block = docs_index_live_block(readme_text)

    if ".live-status" not in text:
        text = text.replace("    /* Tabs */", DOCS_LIVE_STATUS_CSS + "\n    /* Tabs */", 1)

    if "<!-- live-status:start -->" in text and "<!-- live-status:end -->" in text:
        text = re.sub(r"<!-- live-status:start -->.*?<!-- live-status:end -->", block, text, flags=re.DOTALL)
    else:
        tabs = "  <!-- Tabs -->"
        text = text.replace(tabs, block + "\n\n" + tabs, 1)

    text = text.replace("Free LLM API Playground — Chat with GPT-5.4, Claude, DeepSeek, Gemini for Free", "Free LLM API Playground — Chat with GPT-5.5, Claude, DeepSeek, Gemini for Free")
    text = text.replace("Use free API keys to chat with GPT-5.4, Claude, DeepSeek, Gemini", "Use free API keys to chat with GPT-5.5, Claude Opus, DeepSeek, Gemini")
    text = text.replace("Chat with GPT-5.4, Claude, DeepSeek, Gemini", "Chat with GPT-5.5, Claude Opus, DeepSeek, Gemini")
    text = text.replace("chat with GPT-5.4, Claude, DeepSeek, Gemini", "chat with GPT-5.5, Claude Opus, DeepSeek, Gemini")
    text = text.replace("Supports GPT-5.4, Claude Opus 4.7", "Supports GPT-5.5, Claude Opus 4.7")
    text = text.replace("GPT-5.4, GPT-5.4 Mini, GPT-5.4 Pro, Claude Opus 4.7", "GPT-5.5, GPT-5.4 Mini, Claude Opus 4.7")
    text = text.replace("Free LLM API Playground — GPT-5.4 / Claude / DeepSeek / Gemini / Grok / 90+ Models", "Free LLM API Playground — GPT-5.5 / Claude Opus / DeepSeek / Gemini / Grok / 90+ Models")
    text = text.replace(
        """        <span class="chip active" onclick="pickModel(this,'gpt-5.4')">GPT-5.4</span>
        <span class="chip" onclick="pickModel(this,'claude-sonnet-4-6')">Claude</span>
        <span class="chip" onclick="pickModel(this,'deepseek-chat')">DeepSeek</span>
        <span class="chip" onclick="pickModel(this,'gpt-5.4-mini')">GPT-5.4 Mini</span>
        <span class="chip" onclick="pickModel(this,'gemini-2.5-pro')">Gemini</span>
        <span class="chip" onclick="pickModel(this,'mistral-medium-latest')">Mistral</span>
        <span class="chip" onclick="pickModel(this,'codestral-latest')">Codestral</span>
        <span class="chip" onclick="pickModel(this,'smart-chat')">Smart (Auto)</span>""",
        """        <span class="chip active" onclick="pickModel(this,'smart-chat')">Smart (Auto)</span>
        <span class="chip" onclick="pickModel(this,'gpt-5.5')">GPT-5.5</span>
        <span class="chip" onclick="pickModel(this,'claude-opus-4-7')">Claude Opus</span>
        <span class="chip" onclick="pickModel(this,'deepseek-chat')">DeepSeek</span>
        <span class="chip" onclick="pickModel(this,'gemini-2.5-flash')">Gemini</span>
        <span class="chip" onclick="pickModel(this,'mistral-medium-latest')">Mistral</span>
        <span class="chip" onclick="pickModel(this,'codestral-latest')">Codestral</span>""",
    )
    text = text.replace(
        """        <span class="chip active" onclick="pickVerifyModel(this,'gpt-5.4')">GPT-5.4</span>
        <span class="chip" onclick="pickVerifyModel(this,'claude-sonnet-4-6')">Claude</span>
        <span class="chip" onclick="pickVerifyModel(this,'deepseek-chat')">DeepSeek</span>
        <span class="chip" onclick="pickVerifyModel(this,'gpt-5.4-mini')">GPT-5.4 Mini</span>
        <span class="chip" onclick="pickVerifyModel(this,'gemini-2.5-pro')">Gemini</span>
        <span class="chip" onclick="pickVerifyModel(this,'mistral-medium-latest')">Mistral</span>""",
        """        <span class="chip active" onclick="pickVerifyModel(this,'smart-chat')">Smart (Auto)</span>
        <span class="chip" onclick="pickVerifyModel(this,'gpt-5.5')">GPT-5.5</span>
        <span class="chip" onclick="pickVerifyModel(this,'claude-opus-4-7')">Claude Opus</span>
        <span class="chip" onclick="pickVerifyModel(this,'deepseek-chat')">DeepSeek</span>
        <span class="chip" onclick="pickVerifyModel(this,'gemini-2.5-flash')">Gemini</span>
        <span class="chip" onclick="pickVerifyModel(this,'mistral-medium-latest')">Mistral</span>""",
    )
    text = text.replace("let chatModel = 'gpt-5.4';", "let chatModel = 'smart-chat';")
    text = text.replace("let verifyModel = 'gpt-5.4';", "let verifyModel = 'smart-chat';")

    docs_path.write_text(text, encoding="utf-8")


def changelog_line(grouped_keys: dict[str, list[dict]], deleted_count: int, lang: str) -> str | None:
    created_count = sum(len(rows) for rows in grouped_keys.values())
    if created_count == 0 and deleted_count == 0:
        return None
    summary = models_summary(grouped_keys) or "no new keys"
    if lang == "cn":
        return f"- 🆕 新增 {created_count} 个 Key ({summary})，清理 {deleted_count} 个过期 Key"
    return f"- 🆕 Added {created_count} keys ({summary}), cleaned {deleted_count} expired"


def restore_orphan_changelog(text: str, lang: str) -> str:
    if "## 📅 Changelog" in text:
        return text

    summary = "<summary><b>显示更新历史</b></summary>" if lang == "cn" else "<summary><b>Show changelog history</b></summary>"
    summary_idx = text.find(summary)
    date_matches = list(re.finditer(r"(?:^|\n)### \d{4}-\d{2}-\d{2}\n", text))
    if summary_idx == -1 or not date_matches:
        star_idx = text.find("\n## 📈 Star History")
        insert_at = star_idx if star_idx != -1 else len(text)
        block = f"\n\n## 📅 Changelog\n\n<details>\n{summary}\n\n</details>\n\n---\n"
        return text[:insert_at].rstrip() + block + text[insert_at:]

    start_match = None
    for match in date_matches:
        if match.start() < summary_idx:
            start_match = match
    if start_match is None:
        return text

    start = start_match.start()
    if text[start:start + 1] == "\n":
        start += 1
    sep_start = text.rfind("\n---\n\n", 0, start)
    if sep_start != -1:
        start = sep_start + len("\n---\n\n")

    close_idx = text.find("</details>", summary_idx)
    if close_idx == -1:
        return text
    section_end = close_idx + len("</details>")
    trailing_sep = re.match(r"\n{0,2}---\n{0,2}", text[section_end:])
    if trailing_sep:
        section_end += trailing_sep.end()

    body = text[start:section_end]
    body = re.sub(r"\n*<details>\n<summary><b>.*?</b></summary>\n\n?", "\n", body)
    body = body.replace("</details>", "").strip()
    body = re.sub(r"\n*---\s*$", "", body).strip()
    wrapped = f"## 📅 Changelog\n\n<details>\n{summary}\n\n{body}\n</details>\n\n---\n\n"
    return text[:start] + wrapped + text[section_end:].lstrip("\n")


def ensure_changelog_details(text: str, lang: str) -> str:
    text = restore_orphan_changelog(text, lang)
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
    close_idx = text.find("</details>", idx)
    section_end = close_idx if close_idx != -1 else (text.find("\n## ", idx + 1) if text.find("\n## ", idx + 1) != -1 else len(text))
    today_idx = text.find(today_header, idx, section_end)
    if today_idx != -1:
        next_day_idx = text.find("\n### ", today_idx + len(today_header), section_end)
        today_end = next_day_idx if next_day_idx != -1 else section_end
        if line in text[today_idx:today_end]:
            return text
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
    text = normalize_static_copy(text, lang)
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
    paths = [README_PATH, README_CN_PATH, DOCS_INDEX_PATH]
    if contains_conflict_markers(paths):
        print("README contains conflict markers; skip commit", file=sys.stderr)
        return
    subprocess.run(["git", "-C", REPO_PATH, "add", "README.md", "README_CN.md", "docs/index.html"], capture_output=True, text=True)
    diff = subprocess.run(["git", "-C", REPO_PATH, "diff", "--cached", "--quiet"], capture_output=True, text=True)
    if diff.returncode == 0:
        return
    # When nothing new or interesting changed (only timestamps), drop the
    # diff quietly instead of shipping a noisy commit. This keeps the public
    # repo history readable and maximises SEO / star-worthy "activity" signal.
    if new_count == 0 and deleted_count == 0 and not _readme_has_meaningful_diff(["README.md", "README_CN.md", "docs/index.html"]):
        subprocess.run(["git", "-C", REPO_PATH, "reset", "HEAD", "--", "README.md", "README_CN.md", "docs/index.html"], capture_output=True, text=True)
        subprocess.run(["git", "-C", REPO_PATH, "checkout", "--", "README.md", "README_CN.md", "docs/index.html"], capture_output=True, text=True)
        return
    msg = f"feat: +{new_count} keys, -{deleted_count} expired ({date_stamp()} {now_utc8().strftime('%H:%M')})"
    env = os.environ.copy()
    env.update({
        "GIT_AUTHOR_NAME": BOT_NAME,
        "GIT_AUTHOR_EMAIL": BOT_EMAIL,
        "GIT_COMMITTER_NAME": BOT_NAME,
        "GIT_COMMITTER_EMAIL": BOT_EMAIL,
    })
    commit = subprocess.run(["git", "-C", REPO_PATH, "commit", "-m", msg], capture_output=True, text=True)
    if commit.returncode != 0:
        raise subprocess.CalledProcessError(commit.returncode, commit.args, output=commit.stdout, stderr=commit.stderr)
    push = subprocess.run(["git", "-C", REPO_PATH, "push"], capture_output=True, text=True)
    if push.returncode != 0:
        raise subprocess.CalledProcessError(push.returncode, push.args, output=push.stdout, stderr=push.stderr)


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

    try:
        deleted_keys, warn_keys = clean_expired_keys()
    except RuntimeError as exc:
        print(
            f"[ALERT] cleanup failed (will retry on next cleanup-only cron): {exc}",
            file=sys.stderr,
        )
        deleted_keys, warn_keys = [], []
        if args.cleanup_only:
            # Nothing else for this run to do — bail without touching README.
            return

    if args.cleanup_only:
        # Pull any active server-side keys that the README currently forgets —
        # the main source of "shelf looks half empty" drift. Nothing gets
        # created on the Key Manager side.
        grouped_keys = sync_from_active()
        update_readme(README_PATH, grouped_keys, deleted_keys, warn_keys, lang="en")
        update_readme(README_CN_PATH, grouped_keys, deleted_keys, warn_keys, lang="cn")
        update_docs_index()
        git_commit_and_push(sum(len(rows) for rows in grouped_keys.values()), len(deleted_keys))
        log_usage_stats()
        return

    remaining = check_budget()
    if remaining <= 0:
        grouped_keys = sync_from_active()
        update_readme(README_PATH, grouped_keys, deleted_keys, warn_keys, lang="en")
        update_readme(README_CN_PATH, grouped_keys, deleted_keys, warn_keys, lang="cn")
        update_docs_index()
        git_commit_and_push(sum(len(rows) for rows in grouped_keys.values()), len(deleted_keys))
        log_usage_stats()
        return

    recommended_models = fetch_recommended_models()
    grouped_keys = create_keys(recommended_models, remaining)
    # Merge any active keys that aren't in the create payload — otherwise a
    # fresh run right after a cleanup would lose density until the next cron.
    backfill = sync_from_active()
    for group, rows in backfill.items():
        grouped_keys.setdefault(group, [])
        existing_tokens = {row["key"] for row in grouped_keys[group]}
        grouped_keys[group].extend(r for r in rows if r["key"] not in existing_tokens)

    update_readme(README_PATH, grouped_keys, deleted_keys, warn_keys, lang="en")
    update_readme(README_CN_PATH, grouped_keys, deleted_keys, warn_keys, lang="cn")
    update_docs_index()
    git_commit_and_push(sum(len(rows) for rows in grouped_keys.values()), len(deleted_keys))
    log_usage_stats()


if __name__ == "__main__":
    main()
