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


if __name__ == "__main__":
    unittest.main()
