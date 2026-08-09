import contextlib
import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]


def load_script(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SyncScriptTests(unittest.TestCase):
    def test_skill_sync_removes_generated_orphan_but_keeps_handwritten_skill(self):
        module = load_script(
            "sync_codex_skills_test",
            ROOT / "scripts/sync-codex-skills.py",
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sources = root / "skills"
            targets = root / "codex-skills"
            sources.mkdir()
            (sources / "active.md").write_text("# Active\n", encoding="utf-8")
            orphan = targets / "orphan"
            orphan.mkdir(parents=True)
            (orphan / "SKILL.md").write_text(
                "## Codex adapter note\n"
                "This skill is generated from `skills/orphan.md`\n",
                encoding="utf-8",
            )
            handwritten = targets / "handwritten"
            handwritten.mkdir()
            (handwritten / "SKILL.md").write_text("# Custom\n", encoding="utf-8")

            with mock.patch.object(module, "ROOT", root), mock.patch.object(
                module, "CLAUDE_SKILLS", sources
            ), mock.patch.object(module, "CODEX_SKILLS", targets), mock.patch.object(
                sys, "argv", ["sync-codex-skills.py"]
            ), contextlib.redirect_stdout(io.StringIO()):
                module.main()

            self.assertFalse(orphan.exists())
            self.assertTrue((handwritten / "SKILL.md").exists())
            self.assertTrue((targets / "active/SKILL.md").exists())

    def test_prompt_sync_removes_orphan(self):
        module = load_script(
            "sync_codex_prompts_test",
            ROOT / "scripts/sync-codex-prompts.py",
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sources = root / "skills"
            targets = root / "codex-prompts"
            sources.mkdir()
            targets.mkdir()
            (sources / "active.md").write_text("# Active\n", encoding="utf-8")
            orphan = targets / "orphan.md"
            orphan.write_text("stale", encoding="utf-8")

            with mock.patch.object(module, "ROOT", root), mock.patch.object(
                module, "CLAUDE_SKILLS", sources
            ), mock.patch.object(module, "CODEX_PROMPTS", targets), mock.patch.object(
                sys, "argv", ["sync-codex-prompts.py"]
            ), contextlib.redirect_stdout(io.StringIO()):
                module.main()

            self.assertFalse(orphan.exists())
            self.assertTrue((targets / "active.md").exists())


if __name__ == "__main__":
    unittest.main()
