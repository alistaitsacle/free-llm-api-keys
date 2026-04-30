import importlib.util
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from subprocess import CompletedProcess
from unittest import mock


def load_publish_keys_module():
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "publish_keys.py"
    spec = importlib.util.spec_from_file_location("publish_keys", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


publish_keys = load_publish_keys_module()


class PublishKeysTests(unittest.TestCase):
    def write_temp_readme(self, content: str) -> Path:
        tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(tmpdir.cleanup)
        path = Path(tmpdir.name) / "README.md"
        path.write_text(content, encoding="utf-8")
        return path

    def test_update_readme_counts_only_table_key_rows_for_badge(self):
        readme = self.write_temp_readme(
            "[![Keys](https://img.shields.io/badge/Available_Keys-0-brightgreen?style=for-the-badge)]()\n"
            "\n"
            "## 📋 Available Keys\n"
            "\n"
            "> ⏰ Last updated: 2026-03-24 06:30 (UTC+8)\n"
            "\n"
            "### GPT-5.4 `03-24 06:30`\n"
            "\n"
            "| Key | Model | Status | Budget | Rate Limit | Expires |\n"
            "|-----|-------|--------|--------|------------|---------|\n"
            "| `sk-oldkey123` | gpt-5.4 | 🆕 New | $50 | 5 RPM | 2026-03-25 |\n"
            "\n"
            "API tokens (`sk-xxx`) issued by our own platform.\n"
            "\n"
            "## 📅 Changelog\n"
        )

        publish_keys.update_readme(str(readme), {}, deleted_keys=[], warn_keys=[], lang="en")

        updated = readme.read_text(encoding="utf-8")
        self.assertIn("Available_Keys-1-brightgreen", updated)

    def test_update_readme_preserves_description_column_for_multi_model_group(self):
        readme = self.write_temp_readme(
            "## 📋 Available Keys\n"
            "\n"
            "> ⏰ Last updated: 2026-03-24 06:30 (UTC+8)\n"
            "\n"
            "### Multi-Model (GPT-5.4 / Claude / DeepSeek / Gemini auto-rotate) `03-24 06:30`\n"
            "\n"
            "| Key | Model | Status | Budget | Rate Limit | Expires | Description |\n"
            "|-----|-------|--------|--------|------------|---------|-------------|\n"
            "| `sk-existing111` | smart-chat | 🆕 New | $30 | 10 RPM | 2026-03-25 | Auto-selects best model |\n"
            "\n"
            "## 📅 Changelog\n"
        )

        grouped_keys = {
            "Multi-Model (GPT-5.4 / Claude / DeepSeek / Gemini auto-rotate)": [
                {
                    "key": "sk-newmulti222",
                    "model": "flagship-chat",
                    "budget": "$30",
                    "rpm": "10 RPM",
                    "expires": "2026-03-26",
                    "use_case": "GPT-5.4 / Claude rotate",
                }
            ]
        }

        publish_keys.update_readme(str(readme), grouped_keys, deleted_keys=[], warn_keys=[], lang="en")

        updated = readme.read_text(encoding="utf-8")
        self.assertIn(
            "| `sk-newmulti222` | flagship-chat | 🆕 New | $30 | 10 RPM | 2026-03-26 | GPT-5.4 / Claude rotate |",
            updated,
        )

    def test_update_readme_removes_blank_line_between_table_header_and_first_row(self):
        readme = self.write_temp_readme(
            "## 📋 Available Keys\n"
            "\n"
            "> ⏰ Last updated: 2026-03-24 06:30 (UTC+8)\n"
            "\n"
            "### GPT-5.4 / GPT-5.4-mini `04-06 06:30`\n"
            "\n"
            "| Key | Model | Status | Budget | Rate Limit | Expires |\n"
            "|-----|-------|--------|--------|------------|---------|\n"
            "\n"
            "| `sk-old111` | gpt-5.4 | 🆕 New | $50 | 5 RPM | 2026-04-08 |\n"
            "\n"
            "## 📅 Changelog\n"
        )

        grouped_keys = {
            "GPT-5.4 / GPT-5.4-mini": [
                {
                    "key": "sk-new222",
                    "model": "gpt-5.4-mini",
                    "budget": "$30",
                    "rpm": "20 RPM",
                    "expires": "2026-04-08",
                    "use_case": "",
                }
            ]
        }

        publish_keys.update_readme(str(readme), grouped_keys, deleted_keys=[], warn_keys=[], lang="en")

        updated = readme.read_text(encoding="utf-8")
        self.assertNotIn("|-----|-------|--------|--------|------------|---------|\n\n| `sk-old111`", updated)

    def test_update_readme_does_not_duplicate_identical_changelog_line_for_same_day(self):
        today = datetime.now().strftime("%Y-%m-%d")
        readme = self.write_temp_readme(
            "## 📋 Available Keys\n"
            "\n"
            "> ⏰ Last updated: 2026-03-24 06:30 (UTC+8)\n"
            "\n"
            "### GPT-5.4 `03-24 06:30`\n"
            "\n"
            "| Key | Model | Status | Budget | Rate Limit | Expires |\n"
            "|-----|-------|--------|--------|------------|---------|\n"
            "| `sk-existing111` | gpt-5.4 | 🆕 New | $50 | 5 RPM | 2026-03-25 |\n"
            "\n"
            "## 📅 Changelog\n"
            "\n"
            f"### {today}\n"
            "- 🆕 Added 1 keys (gpt-5.4), cleaned 0 expired\n"
        )

        grouped_keys = {
            "GPT-5.4": [
                {
                    "key": "sk-one111",
                    "model": "gpt-5.4",
                    "budget": "$50",
                    "rpm": "5 RPM",
                    "expires": "2026-03-25",
                    "use_case": "",
                }
            ]
        }

        publish_keys.update_readme(str(readme), grouped_keys, deleted_keys=[], warn_keys=[], lang="en")
        publish_keys.update_readme(str(readme), grouped_keys, deleted_keys=[], warn_keys=[], lang="en")

        updated = readme.read_text(encoding="utf-8")
        today_section = updated.split(f"### {today}\n", 1)[1].split("\n### ", 1)[0]
        self.assertEqual(today_section.count("- 🆕 Added 1 keys (gpt-5.4), cleaned 0 expired"), 1)

    def test_update_readme_wraps_changelog_in_details_block(self):
        readme = self.write_temp_readme(
            "## 📋 Available Keys\n"
            "\n"
            "> ⏰ Last updated: 2026-03-24 06:30 (UTC+8)\n"
            "\n"
            "## 📅 Changelog\n"
            "\n"
            "### 2026-03-24\n"
            "- 🆕 Added 1 keys (gpt-5.4), cleaned 0 expired\n"
            "\n"
            "---\n"
            "\n"
            "## 📈 Star History\n"
        )

        publish_keys.update_readme(str(readme), {}, deleted_keys=[], warn_keys=[], lang="en")

        updated = readme.read_text(encoding="utf-8")
        self.assertIn("## 📅 Changelog\n\n<details>", updated)
        self.assertIn("<summary><b>Show changelog history</b></summary>", updated)
        self.assertIn("### 2026-03-24\n- 🆕 Added 1 keys (gpt-5.4), cleaned 0 expired", updated)
        self.assertIn("</details>\n\n---\n\n## 📈 Star History", updated)

    def test_update_readme_appends_changelog_inside_existing_details_block(self):
        today = datetime.now().strftime("%Y-%m-%d")
        readme = self.write_temp_readme(
            "## 📋 Available Keys\n"
            "\n"
            "> ⏰ Last updated: 2026-03-24 06:30 (UTC+8)\n"
            "\n"
            "## 📅 Changelog\n"
            "\n"
            "<details>\n"
            "<summary><b>Show changelog history</b></summary>\n"
            "\n"
            f"### {today}\n"
            "- 🆕 Added 1 keys (gpt-5.4), cleaned 0 expired\n"
            "</details>\n"
            "\n"
            "---\n"
            "\n"
            "## 📈 Star History\n"
        )

        grouped_keys = {
            "GPT-5.4": [
                {
                    "key": "sk-two222",
                    "model": "gpt-5.4",
                    "budget": "$50",
                    "rpm": "5 RPM",
                    "expires": "2026-03-25",
                    "use_case": "",
                }
            ]
        }

        publish_keys.update_readme(str(readme), grouped_keys, deleted_keys=["sk-old333"], warn_keys=[], lang="en")

        updated = readme.read_text(encoding="utf-8")
        self.assertIn("<details>\n<summary><b>Show changelog history</b></summary>", updated)
        self.assertIn(f"### {today}", updated)
        self.assertIn("- 🆕 Added 1 keys (gpt-5.4), cleaned 0 expired", updated)
        self.assertIn(f"- 🆕 Added 1 keys (gpt-5.4), cleaned 1 expired\n- 🆕 Added 1 keys (gpt-5.4), cleaned 0 expired", updated)


    def test_update_readme_puts_stable_defaults_before_premium_gpt_and_claude(self):
        readme = self.write_temp_readme(
            "[![Keys](https://img.shields.io/badge/Available_Keys-1-brightgreen?style=for-the-badge)]()\n"
            "\n"
            "## 📋 Available Keys\n"
            "\n"
            "> ⏰ Last updated: 2026-04-25 13:30 (UTC+8)\n"
            "\n"
            "> **[Verify your key here](https://alistaitsacle.github.io/free-llm-api-keys/)** — one-click check if a key still works.\n"
            "\n"
            "### DeepSeek `04-25 13:30`\n"
            "\n"
            "| Key | Model | Status | Budget | Rate Limit | Expires | Description |\n"
            "|-----|-------|--------|--------|------------|---------|-------------|\n"
            "| `sk-deepseek111` | deepseek-chat | 🆕 New | $20 | 20 RPM | 2026-04-26 | Stable |\n"
            "\n"
            "## 📅 Changelog\n"
        )

        grouped_keys = {
            "GPT-5.5": [
                {"key": "sk-gpt111", "model": "gpt-5.5", "budget": "$20", "rpm": "5 RPM", "expires": "2026-04-27", "use_case": "GPT flagship"}
            ],
            "Claude Sonnet": [
                {"key": "sk-claude111", "model": "claude-sonnet-4-6", "budget": "$20", "rpm": "5 RPM", "expires": "2026-04-27", "use_case": "Claude flagship"}
            ],
            "Gemini": [
                {"key": "sk-gemini111", "model": "gemini-2.5-flash", "budget": "$20", "rpm": "20 RPM", "expires": "2026-04-27", "use_case": "Gemini fast"}
            ],
            publish_keys.MULTI_MODEL_GROUP_EN: [
                {"key": "sk-smart111", "model": "smart-chat", "budget": "$20", "rpm": "10 RPM", "expires": "2026-04-27", "use_case": "Auto-route"}
            ],
        }

        publish_keys.update_readme(str(readme), grouped_keys, deleted_keys=[], warn_keys=[], lang="en")

        updated = readme.read_text(encoding="utf-8")
        gpt_pos = updated.index("### GPT-5.5")
        claude_pos = updated.index("### Claude Opus 4.7")
        gemini_pos = updated.index("### Gemini")
        deepseek_pos = updated.index("### DeepSeek")
        multi_pos = updated.index("### Multi-Model")
        self.assertLess(gpt_pos, claude_pos)
        self.assertLess(claude_pos, gemini_pos)
        self.assertLess(gemini_pos, deepseek_pos)
        self.assertLess(deepseek_pos, multi_pos)
        self.assertIn("### Featured models", updated)
        self.assertIn("| `sk-smart111` | smart-chat | 🆕 New | $20 | 10 RPM | 2026-04-27 | Auto-route |", updated)
        self.assertNotIn("|-----|-------|--------|--------|------------|---------|-------------|\n\n|", updated)




    def test_update_readme_places_cn_multi_model_before_media_section(self):
        readme = self.write_temp_readme(
            "## 📋 可用 Key 列表\n\n"
            "> **[在这里验证你的 Key](https://alistaitsacle.github.io/free-llm-api-keys/)** — 一键检查 Key 是否可用。\n\n"
            "### DeepSeek `04-25 13:30`\n\n"
            "| Key | 模型 | 状态 | 预算 | 速率限制 | 过期时间 | 说明 |\n"
            "|-----|------|------|------|---------|---------|------|\n"
            "| `sk-deepseek111` | deepseek-chat | 🆕 新增 | $20 | 20 RPM | 2026-04-26 | 稳定 |\n\n"
            "### 图像 / 语音 / 向量化 `04-25 13:30`\n\n"
            "| Key | 模型 | 状态 | 预算 | 速率限制 | 过期时间 |\n"
            "|-----|------|------|------|---------|---------|\n"
            "| `sk-embed111` | embed-english-v3.0 | 🆕 新增 | $50 | 5 RPM | 2026-04-27 |\n\n"
            "## 📅 Changelog\n"
        )
        grouped_keys = {
            publish_keys.MULTI_MODEL_GROUP_EN: [
                {"key": "sk-smart-cn", "model": "smart-chat", "budget": "$100", "rpm": "10 RPM", "expires": "2026-04-27", "use_case_cn": "自动路由"}
            ]
        }

        publish_keys.update_readme(str(readme), grouped_keys, deleted_keys=[], warn_keys=[], lang="cn")

        updated = readme.read_text(encoding="utf-8")
        self.assertLess(updated.index("### 多模型聚合"), updated.index("### 图像 / 语音 / 向量化"))

    def test_update_readme_removes_duplicate_start_here_blocks(self):
        readme = self.write_temp_readme(
            "## 📋 Available Keys\n\n"
            "> **[Verify your key here](https://alistaitsacle.github.io/free-llm-api-keys/)** — one-click check if a key still works.\n\n"
            "### Start here: GPT → Claude → DeepSeek\n\n"
            "- `gpt-5.5` — best first impression for general chat and coding.\n"
            "- `claude-sonnet-4-6` — best for writing, code review, and long answers.\n"
            "- `deepseek-chat` — fast, stable, and great for everyday use.\n\n"
            "If a fresh single-model key is temporarily unavailable, use `flagship-chat` or `smart-chat` from the multi-model section.\n\n"
            "---\n\n"
            "### DeepSeek `04-25 13:30`\n\n"
            "| Key | Model | Status | Budget | Rate Limit | Expires | Description |\n"
            "|-----|-------|--------|--------|------------|---------|-------------|\n"
            "| `sk-deepseek111` | deepseek-chat | 🆕 New | $20 | 20 RPM | 2026-04-26 | Stable |\n\n"
            "### Start here: DeepSeek → smart-chat → Gemini\n\n"
            "- `deepseek-chat` — fast, stable, and best for everyday use.\n"
            "- `smart-chat` — auto-routes across currently healthy low-cost chat backends.\n"
            "- `gemini-2.5-flash` — fast Gemini option for long-context general chat.\n\n"
            "Use `gpt-5.5` or `claude-sonnet-4-6` when you need premium quality; they are intentionally not the default free high-volume path.\n\n"
            "---\n\n"
            "## 🚀 How to Use\n"
        )

        publish_keys.update_readme(str(readme), {}, deleted_keys=[], warn_keys=[], lang="en")

        updated = readme.read_text(encoding="utf-8")
        self.assertNotIn("### Start here: GPT → Claude → DeepSeek", updated)
        self.assertEqual(updated.count("### Featured models"), 1)
        self.assertLess(updated.index("### Featured models"), updated.index("### GPT-5.5"))

    def test_update_readme_renders_full_model_shelf_with_restocking_rows(self):
        readme = self.write_temp_readme(
            "## 📋 Available Keys\n\n"
            "> ⏰ Last updated: 2026-04-25 13:30 (UTC+8)\n\n"
            "### DeepSeek `04-25 13:30`\n\n"
            "| Key | Model | Status | Budget | Rate Limit | Expires | Description |\n"
            "|-----|-------|--------|--------|------------|---------|-------------|\n"
            "\n"
            "### GPT-5.5 `04-25 13:30`\n\n"
            "| Key | Model | Status | Budget | Rate Limit | Expires | Description |\n"
            "|-----|-------|--------|--------|------------|---------|-------------|\n\n"
            "### Gemini `04-25 13:30`\n\n"
            "| Key | Model | Status | Budget | Rate Limit | Expires | Description |\n"
            "|-----|-------|--------|--------|------------|---------|-------------|\n"
            "| `sk-gemini111` | gemini-2.5-flash | 🆕 New | $20 | 20 RPM | 2026-04-26 | Fast |\n\n"
            "### Kimi `04-25 13:30`\n\n"
            "| Key | Model | Status | Budget | Rate Limit | Expires | Description |\n"
            "|-----|-------|--------|--------|------------|---------|-------------|\n\n"
            "### Image / Audio / Embedding `04-25 13:30`\n\n"
            "| Key | Model | Status | Budget | Rate Limit | Expires |\n"
            "|-----|-------|--------|--------|------------|---------|\n\n"
            "## 🚀 How to Use\n"
        )

        publish_keys.update_readme(str(readme), {}, deleted_keys=[], warn_keys=[], lang="en")

        updated = readme.read_text(encoding="utf-8")
        ordered_titles = [
            "### GPT-5.5",
            "### Claude Opus 4.7",
            "### Gemini",
            "### DeepSeek",
            "### Multi-Model",
            "### Kimi",
            "### Image / Audio / Embedding",
        ]
        positions = [updated.index(title) for title in ordered_titles]
        self.assertEqual(positions, sorted(positions))
        self.assertNotIn("<summary><b>Temporarily unavailable models</b></summary>", updated)
        # smart-chat itself has no real key, so everyone falls back to Restocking here.
        self.assertIn("| Restocking | gpt-5.5 | Temporarily unavailable | - | - | Next refresh | Premium GPT flagship |", updated)
        self.assertIn("| Restocking | claude-opus-4-7 | Temporarily unavailable | - | - | Next refresh | Claude Opus flagship |", updated)
        self.assertIn("| Restocking | deepseek-chat | Temporarily unavailable | - | - | Next refresh | Everyday chat, coding, translation, writing |", updated)
        self.assertIn("| `sk-gemini111` | gemini-2.5-flash | 🆕 New | $20 | 20 RPM | 2026-04-26 | Fast |", updated)
        self.assertEqual(updated.count("| Restocking |"), 6)

    def test_update_readme_removes_orphan_empty_model_sections_outside_key_list(self):
        readme = self.write_temp_readme(
            "## 📋 Available Keys\n\n"
            "> ⏰ Last updated: 2026-04-25 13:30 (UTC+8)\n\n"
            "### Gemini `04-25 13:30`\n\n"
            "| Key | Model | Status | Budget | Rate Limit | Expires | Description |\n"
            "|-----|-------|--------|--------|------------|---------|-------------|\n"
            "| `sk-gemini111` | gemini-2.5-flash | 🆕 New | $20 | 20 RPM | 2026-04-26 | Fast |\n\n"
            "## 🚀 How to Use\n\n"
            "Use the keys above.\n\n"
            "---\n\n"
            "### GPT-5.5 `04-24 19:30`\n\n"
            "| Key | Model | Status | Budget | Rate Limit | Expires | Description |\n"
            "|-----|-------|--------|--------|------------|---------|-------------|\n\n"
            "---\n\n"
            "### Claude Sonnet `04-24 19:30`\n\n"
            "| Key | Model | Status | Budget | Rate Limit | Expires | Description |\n"
            "|-----|-------|--------|--------|------------|---------|-------------|\n\n"
            "---\n"
        )

        publish_keys.update_readme(str(readme), {}, deleted_keys=[], warn_keys=[], lang="en")

        updated = readme.read_text(encoding="utf-8")
        self.assertEqual(updated.count("### GPT-5.5"), 1)
        self.assertNotIn("### Claude Sonnet", updated)
        self.assertIn("## 🚀 How to Use", updated)
        self.assertIn("| `sk-gemini111` | gemini-2.5-flash | 🆕 New | $20 | 20 RPM | 2026-04-26 | Fast |", updated)

    def test_extract_bad_keys_from_status_handles_results_dict(self):
        payload = {
            "results": {
                "sk-good": {"status": "active"},
                "sk-revoked": {"status": "revoked"},
                "sk-expired": {"status": "expired"},
                "sk-warning": {"status": "rate_limited"},
            }
        }

        deleted, warned = publish_keys.extract_bad_keys_from_status(payload)

        self.assertEqual(deleted, ["sk-revoked", "sk-expired"])
        self.assertEqual(warned, ["sk-warning"])

    def test_build_featured_key_requests_fills_missing_priority_models(self):
        active_keys = [
            {"models": ["deepseek-chat"]},
            {"models": ["gpt-5.5"]},
        ]
        available_models = {"gpt-5.5", "claude-opus-4-7", "deepseek-chat", "smart-chat", "gemini-2.5-flash"}

        requests = publish_keys.build_featured_key_requests(active_keys, available_models, remaining_budget_usd=2000)

        requested_models = [req["models"][0] for req in requests]
        # Each featured group targets 6 keys. One deepseek-chat and one
        # gpt-5.5 already exist, so we should request 5 more of each plus the
        # full 6 for groups without any active keys yet.
        self.assertEqual(requested_models.count("deepseek-chat"), 5)
        self.assertEqual(requested_models.count("gpt-5.5"), 5)
        self.assertEqual(requested_models.count("claude-opus-4-7"), 6)
        self.assertEqual(requested_models.count("smart-chat"), 6)
        self.assertEqual(requested_models.count("gemini-2.5-flash"), 6)
        self.assertNotIn("gpt-5.4", requested_models)
        # FEATURED_GROUP_ORDER puts GPT-5.5 first, so the missing 5 gpt-5.5
        # requests should lead the batch.
        self.assertEqual(requested_models[:5], ["gpt-5.5"] * 5)
        self.assertTrue(all(req["budget_usd"] <= 50 for req in requests))

    def test_sync_repo_before_publish_runs_pull_rebase(self):
        calls = []

        def fake_run(cmd, capture_output=True, text=True):
            calls.append(cmd)
            return CompletedProcess(cmd, 0, stdout="", stderr="")

        with mock.patch.object(publish_keys.subprocess, "run", side_effect=fake_run):
            self.assertTrue(publish_keys.sync_repo_before_publish())

        self.assertEqual(
            calls,
            [["git", "-C", publish_keys.REPO_PATH, "pull", "--rebase", "origin", "main"]],
        )

    def test_git_commit_and_push_does_not_use_stash_or_pull_during_commit_phase(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            (repo / "README.md").write_text("clean\n", encoding="utf-8")
            (repo / "README_CN.md").write_text("clean\n", encoding="utf-8")

            calls = []

            def fake_run(cmd, capture_output=True, text=False):
                calls.append(cmd)
                if cmd[-2:] == ["diff", "--cached"] or cmd[-3:] == ["diff", "--cached", "--quiet"]:
                    return CompletedProcess(cmd, 1, stdout="", stderr="")
                if cmd[-1] == "push":
                    return CompletedProcess(cmd, 0, stdout="", stderr="")
                return CompletedProcess(cmd, 0, stdout="", stderr="")

            with mock.patch.object(publish_keys, "REPO_PATH", str(repo)), \
                 mock.patch.object(publish_keys, "README_PATH", str(repo / "README.md")), \
                 mock.patch.object(publish_keys, "README_CN_PATH", str(repo / "README_CN.md")), \
                 mock.patch.object(publish_keys.subprocess, "run", side_effect=fake_run):
                publish_keys.git_commit_and_push(1, 0)

        flattened = [" ".join(cmd) for cmd in calls]
        self.assertFalse(any(" stash" in f" {cmd}" for cmd in flattened))
        self.assertFalse(any(" pull --rebase" in cmd for cmd in flattened))
        self.assertTrue(any(cmd.endswith(" commit -m feat: +1 keys, -0 expired") is False for cmd in flattened))

    def test_git_commit_and_push_skips_commit_when_readme_contains_conflict_markers(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            (repo / "README.md").write_text(
                "<<<<<<< Updated upstream\nleft\n=======\nright\n>>>>>>> Stashed changes\n",
                encoding="utf-8",
            )
            (repo / "README_CN.md").write_text("clean\n", encoding="utf-8")

            calls = []

            def fake_run(cmd, capture_output=True, text=False):
                calls.append(cmd)
                return CompletedProcess(cmd, 0, stdout="", stderr="")

            with mock.patch.object(publish_keys, "REPO_PATH", str(repo)), \
                 mock.patch.object(publish_keys, "README_PATH", str(repo / "README.md")), \
                 mock.patch.object(publish_keys, "README_CN_PATH", str(repo / "README_CN.md")), \
                 mock.patch.object(publish_keys.subprocess, "run", side_effect=fake_run):
                publish_keys.git_commit_and_push(1, 0)

        flattened = [" ".join(cmd) for cmd in calls]
        self.assertFalse(any(" commit " in f" {cmd} " for cmd in flattened))
        self.assertFalse(any(" push" in f" {cmd}" for cmd in flattened))

    def test_main_cleanup_only_skips_creation_and_commits_cleanup_changes(self):
        with mock.patch("sys.argv", ["publish_keys.py", "--cleanup-only"]), \
             mock.patch.object(publish_keys, "KM_TOKEN", "token"), \
             mock.patch.object(publish_keys, "sync_repo_before_publish", return_value=True), \
             mock.patch.object(publish_keys, "clean_expired_keys", return_value=(["sk-old1"], [])), \
             mock.patch.object(publish_keys, "update_readme") as update_readme, \
             mock.patch.object(publish_keys, "git_commit_and_push") as git_commit_and_push, \
             mock.patch.object(publish_keys, "log_usage_stats") as log_usage_stats, \
             mock.patch.object(publish_keys, "check_budget") as check_budget, \
             mock.patch.object(publish_keys, "fetch_recommended_models") as fetch_recommended_models, \
             mock.patch.object(publish_keys, "create_keys") as create_keys:
            publish_keys.main()

        self.assertEqual(update_readme.call_count, 2)
        update_readme.assert_any_call(publish_keys.README_PATH, {}, ["sk-old1"], [], lang="en")
        update_readme.assert_any_call(publish_keys.README_CN_PATH, {}, ["sk-old1"], [], lang="cn")
        git_commit_and_push.assert_called_once_with(0, 1)
        log_usage_stats.assert_called_once()
        check_budget.assert_not_called()
        fetch_recommended_models.assert_not_called()
        create_keys.assert_not_called()

    def test_main_publishes_cleanup_even_when_budget_is_exhausted(self):
        with mock.patch("sys.argv", ["publish_keys.py"]), \
             mock.patch.object(publish_keys, "KM_TOKEN", "token"), \
             mock.patch.object(publish_keys, "sync_repo_before_publish", return_value=True), \
             mock.patch.object(publish_keys, "clean_expired_keys", return_value=(["sk-old1", "sk-old2"], [])), \
             mock.patch.object(publish_keys, "check_budget", return_value=0), \
             mock.patch.object(publish_keys, "update_readme") as update_readme, \
             mock.patch.object(publish_keys, "git_commit_and_push") as git_commit_and_push, \
             mock.patch.object(publish_keys, "log_usage_stats") as log_usage_stats, \
             mock.patch.object(publish_keys, "fetch_recommended_models") as fetch_recommended_models, \
             mock.patch.object(publish_keys, "create_keys") as create_keys:
            publish_keys.main()

        self.assertEqual(update_readme.call_count, 2)
        update_readme.assert_any_call(publish_keys.README_PATH, {}, ["sk-old1", "sk-old2"], [], lang="en")
        update_readme.assert_any_call(publish_keys.README_CN_PATH, {}, ["sk-old1", "sk-old2"], [], lang="cn")
        git_commit_and_push.assert_called_once_with(0, 2)
        log_usage_stats.assert_called_once()
        fetch_recommended_models.assert_not_called()
        create_keys.assert_not_called()

    def test_update_readme_removes_orphan_shelf_sections_even_when_filled(self):
        # Regression for a cc77a47-era rendering glitch where a fully-populated
        # Claude Opus block ended up duplicated after the License section.
        # Those trailing blocks must be stripped regardless of content.
        readme = self.write_temp_readme(
            "## 📋 Available Keys\n\n"
            "> ⏰ Last updated: 2026-04-30 19:09 (UTC+8)\n\n"
            "### Gemini `04-30 19:09`\n\n"
            "| Key | Model | Status | Budget | Rate Limit | Expires | Description |\n"
            "|-----|-------|--------|--------|------------|---------|-------------|\n"
            "| `sk-g` | gemini-2.5-flash | 🆕 New | $20 | 20 RPM | 2026-05-02 | Fast |\n\n"
            "## 🚀 How to Use\n\n"
            "Use the keys above.\n\n"
            "## 📜 License\n\n"
            "[MIT License](./LICENSE)\n\n"
            "### Claude Opus 4.7 `04-30 19:03`\n\n"
            "| Key | Model | Status | Budget | Rate Limit | Expires | Description |\n"
            "|-----|-------|--------|--------|------------|---------|-------------|\n"
            "| `sk-orphan1` | claude-opus-4-7 | 🆕 New | $20 | 5 RPM | 2026-05-02 | Opus |\n"
            "| `sk-orphan2` | claude-opus-4-7 | 🆕 New | $20 | 5 RPM | 2026-05-02 | Opus |\n\n"
            "---\n"
        )

        publish_keys.update_readme(str(readme), {}, deleted_keys=[], warn_keys=[], lang="en")

        updated = readme.read_text(encoding="utf-8")
        self.assertEqual(updated.count("### Claude Opus 4.7"), 1)
        self.assertLess(updated.index("### Claude Opus 4.7"), updated.index("## 🚀 How to Use"))
        self.assertNotIn("sk-orphan1", updated)
        self.assertNotIn("sk-orphan2", updated)


    def test_update_readme_uses_smart_chat_fallback_for_empty_flagship_groups(self):
        readme = self.write_temp_readme(
            "[![Keys](https://img.shields.io/badge/Available_Keys-0-brightgreen?style=for-the-badge)]()\n\n"
            "## 📋 Available Keys\n\n"
            "> ⏰ Last updated: 2026-04-30 17:52 (UTC+8)\n\n"
            "### Gemini `04-30 17:52`\n\n"
            "| Key | Model | Status | Budget | Rate Limit | Expires | Description |\n"
            "|-----|-------|--------|--------|------------|---------|-------------|\n"
            "| `sk-gemini111` | gemini-2.5-flash | 🆕 New | $20 | 20 RPM | 2026-04-30 | Fast |\n\n"
            f"### {publish_keys.MULTI_MODEL_GROUP_EN} `04-30 17:52`\n\n"
            "| Key | Model | Status | Budget | Rate Limit | Expires | Description |\n"
            "|-----|-------|--------|--------|------------|---------|-------------|\n"
            "| `sk-smartfallback` | smart-chat | 🆕 New | $50 | 10 RPM | 2026-05-02 | Auto-routes |\n\n"
            "## 🚀 How to Use\n"
        )

        publish_keys.update_readme(str(readme), {}, deleted_keys=[], warn_keys=[], lang="en")

        updated = readme.read_text(encoding="utf-8")

        # Every flagship shelf group (GPT-5.5, Opus 4.7, Kimi, Image) that has
        # no real key should surface a smart-chat fallback row carrying the
        # same `sk-` token, so users always have something to copy.
        for group_title in ("### GPT-5.5", "### Claude Opus 4.7", "### Kimi", "### Image / Audio / Embedding"):
            self.assertIn(group_title, updated)
        self.assertIn("smart-chat (gpt-5.5 fallback)", updated)
        self.assertIn("smart-chat (claude-opus-4-7 fallback)", updated)
        self.assertIn("🛟 Fallback", updated)
        self.assertIn(publish_keys.FALLBACK_MARKER, updated)

        # Fallback rows reuse the smart-chat sk- token but must NOT appear as
        # Restocking placeholders — the whole point is to keep the shelf full.
        self.assertNotIn("| Restocking | gpt-5.5 |", updated)
        self.assertNotIn("| Restocking | claude-opus-4-7 |", updated)

        # Badge must still count unique keys: 1 smart-chat + 1 gemini = 2.
        self.assertIn("Available_Keys-2-brightgreen", updated)

    def test_update_readme_cn_smart_chat_fallback_writes_chinese_labels(self):
        readme = self.write_temp_readme(
            "[![Keys](https://img.shields.io/badge/可用_Key-0-brightgreen?style=for-the-badge)]()\n\n"
            "## 📋 可用 Key 列表\n\n"
            "> ⏰ 最后更新: 2026-04-30 17:52 (UTC+8)\n\n"
            f"### {publish_keys.MULTI_MODEL_GROUP_CN} `04-30 17:52`\n\n"
            "| Key | 模型 | 状态 | 预算 | 速率限制 | 过期时间 | 说明 |\n"
            "|-----|------|------|------|---------|---------|------|\n"
            "| `sk-smartcn` | smart-chat | 🆕 新增 | $50 | 10 RPM | 2026-05-02 | 自动路由 |\n\n"
            "## 🚀 如何使用\n"
        )

        publish_keys.update_readme(str(readme), {}, deleted_keys=[], warn_keys=[], lang="cn")

        updated = readme.read_text(encoding="utf-8")
        self.assertIn("🛟 兜底", updated)
        self.assertIn("smart-chat (gpt-5.5 兜底)", updated)
        self.assertIn("补货期间由 smart-chat 自动路由", updated)
        # Unique-key badge still counts the smart-chat token only once.
        self.assertIn("可用_Key-1-brightgreen", updated)

    def test_count_table_keys_dedupes_fallback_rows(self):
        text = (
            "| `sk-a` | smart-chat | 🆕 New | $50 | 10 RPM | 2026-05-02 | Auto |\n"
            "| `sk-a` | smart-chat (gpt-5.5 fallback) | 🛟 Fallback | $50 | 10 RPM | 2026-05-02 | Premium — fallback | "
            + publish_keys.FALLBACK_MARKER
            + "\n"
            "| `sk-b` | deepseek-chat | 🆕 New | $20 | 20 RPM | 2026-05-02 | Stable |\n"
        )
        self.assertEqual(publish_keys.count_table_keys(text), 2)

    def test_git_commit_and_push_skips_pure_timestamp_diff(self):
        with mock.patch.object(publish_keys, "contains_conflict_markers", return_value=False), \
             mock.patch.object(publish_keys.subprocess, "run") as run:
            # 1st call: git add; 2nd: diff --cached --quiet (returns 1 = has
            # changes); 3rd: diff --cached --unified=0 (timestamp-only diff);
            # 4th & 5th: reset + checkout to drop the cosmetic change.
            run.side_effect = [
                CompletedProcess(args=[], returncode=0),
                CompletedProcess(args=[], returncode=1),
                CompletedProcess(
                    args=[],
                    returncode=0,
                    stdout=(
                        "--- a/README.md\n"
                        "+++ b/README.md\n"
                        "@@\n"
                        "-> ⏰ Last updated: 2026-04-30 17:37 (UTC+8)\n"
                        "+> ⏰ Last updated: 2026-04-30 17:52 (UTC+8)\n"
                        "@@\n"
                        "-### GPT-5.5 `04-30 17:37`\n"
                        "+### GPT-5.5 `04-30 17:52`\n"
                    ),
                ),
                CompletedProcess(args=[], returncode=0),
                CompletedProcess(args=[], returncode=0),
            ]
            publish_keys.git_commit_and_push(0, 0)

        commands = [call.args[0] for call in run.call_args_list]
        # Must have issued a reset + checkout to drop the cosmetic diff.
        self.assertTrue(any(cmd[3] == "reset" for cmd in commands if len(cmd) > 3))
        self.assertTrue(any(cmd[3] == "checkout" for cmd in commands if len(cmd) > 3))
        # Must NOT have issued commit / push.
        self.assertFalse(any(cmd[3] == "commit" for cmd in commands if len(cmd) > 3))
        self.assertFalse(any(cmd[3] == "push" for cmd in commands if len(cmd) > 3))

    def test_git_commit_and_push_still_commits_real_diff(self):
        with mock.patch.object(publish_keys, "contains_conflict_markers", return_value=False), \
             mock.patch.object(publish_keys.subprocess, "run") as run:
            run.side_effect = [
                CompletedProcess(args=[], returncode=0),  # git add
                CompletedProcess(args=[], returncode=1),  # diff --cached --quiet
                CompletedProcess(
                    args=[],
                    returncode=0,
                    stdout=(
                        "--- a/README.md\n"
                        "+++ b/README.md\n"
                        "@@\n"
                        "+| `sk-new` | deepseek-chat | 🆕 New | $20 | 20 RPM | 2026-05-02 | Stable |\n"
                    ),
                ),  # meaningful diff check
                CompletedProcess(args=[], returncode=0),  # commit
                CompletedProcess(args=[], returncode=0),  # push
            ]
            publish_keys.git_commit_and_push(1, 0)

        commands = [call.args[0] for call in run.call_args_list]
        self.assertTrue(any(cmd[3] == "commit" for cmd in commands if len(cmd) > 3))
        self.assertTrue(any(cmd[3] == "push" for cmd in commands if len(cmd) > 3))


if __name__ == "__main__":
    unittest.main()
