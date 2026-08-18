from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class InitArticleProjectTest(unittest.TestCase):
    def test_initializer_automates_identity_and_task_generation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            projects_root = Path(temp_dir) / "projects"
            article_id = "test-article-001"
            project_dir = projects_root / article_id

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools" / "init_article_project.py"),
                    "--projects-root",
                    str(projects_root),
                    "--article-id",
                    article_id,
                    "--topic",
                    "実行可能な記事生成フローを検証する",
                    "--audience",
                    "技術ブログ運用者",
                    "--allow-dirty",
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("NEXT ACTION", result.stdout)
            self.assertFalse((project_dir / "article.md").exists())

            state = (project_dir / "PROJECT_STATE.md").read_text(encoding="utf-8")
            self.assertIn("- Agent version: 0.6.0", state)
            self.assertRegex(state, r"- Git commit: [0-9a-f]{40}")

            snapshot = json.loads(
                (project_dir / "results" / "version-snapshot.json").read_text(encoding="utf-8")
            )
            self.assertEqual(article_id, snapshot["article_id"])
            self.assertIn("git_commit", snapshot)
            self.assertIn(f"- Git dirty: {str(snapshot['git_dirty']).lower()}", state)

            task = (project_dir / "AGENT_TASK.md").read_text(encoding="utf-8")
            self.assertNotIn("{{ARTICLE_ID}}", task)
            self.assertNotIn("{{PROJECT_DIR}}", task)
            self.assertIn(str(project_dir / "article.md"), task)
            self.assertIn("article-drafting", task)

    def test_article_id_cannot_escape_projects_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools" / "init_article_project.py"),
                    "--projects-root",
                    str(Path(temp_dir) / "projects"),
                    "--article-id",
                    "../escape",
                    "--topic",
                    "不正なパスを拒否する",
                    "--audience",
                    "技術ブログ運用者",
                    "--allow-dirty",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(0, result.returncode)
            self.assertIn("article-id must be one directory name", result.stderr)

    def test_resume_existing_preserves_artifacts_and_adds_automation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            projects_root = Path(temp_dir) / "projects"
            article_id = "test-resume-001"
            project_dir = projects_root / article_id
            common_args = [
                sys.executable,
                str(ROOT / "tools" / "init_article_project.py"),
                "--projects-root",
                str(projects_root),
                "--article-id",
                article_id,
                "--topic",
                "既存Projectを安全に再開する",
                "--audience",
                "技術ブログ運用者",
                "--allow-dirty",
            ]

            subprocess.run(common_args, cwd=ROOT, check=True, capture_output=True, text=True)
            evidence_path = project_dir / "research.md"
            evidence_path.write_text("# Existing evidence\n", encoding="utf-8")
            readme_path = project_dir / "README.md"
            readme_path.write_text("# User-maintained README\n", encoding="utf-8")
            original_snapshot = json.loads(
                (project_dir / "results" / "version-snapshot.json").read_text(encoding="utf-8")
            )
            (project_dir / "AGENT_TASK.md").unlink()

            result = subprocess.run(
                [*common_args, "--resume-existing"],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertEqual("# Existing evidence\n", evidence_path.read_text(encoding="utf-8"))
            self.assertEqual("# User-maintained README\n", readme_path.read_text(encoding="utf-8"))
            self.assertTrue((project_dir / "AGENT_TASK.md").is_file())
            archive = project_dir / "results" / (
                f"version-snapshot.{original_snapshot['git_commit'][:12]}.json"
            )
            self.assertTrue(archive.is_file())
            self.assertIn("Existing phase artifacts were preserved.", result.stdout)


if __name__ == "__main__":
    unittest.main()
