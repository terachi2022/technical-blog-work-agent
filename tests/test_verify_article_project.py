from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class VerifyArticleProjectTest(unittest.TestCase):
    def test_complete_project_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "article"
            (project_dir / "results").mkdir(parents=True)

            files = [
                "AGENT_TASK.md",
                "research.md",
                "hypothesis.md",
                "experiment-plan.md",
                "experiment-log.md",
                "analysis.md",
                "discussion.md",
            ]
            for relative_path in files:
                (project_dir / relative_path).write_text("# Evidence\n\n実データ\n", encoding="utf-8")

            state = "| 11 | Article | COMPLETED | article.md | |\n"
            (project_dir / "PROJECT_STATE.md").write_text(state, encoding="utf-8")

            article = "\n".join(
                [
                    "# 実証記事",
                    "## TL;DR",
                    "実測に基づく結論です。",
                    "## Research Question",
                    "何を確認できるか。",
                    "## 検証環境",
                    "Apple M5 Max、Python 3.14.6。",
                    "## 結果",
                    "実行ログから確認した結果です。",
                    "## 考察",
                    "結果と一次情報を分離して考察します。",
                    "## 参考資料",
                    "公式資料を参照します。",
                    "検証手順とEvidenceの説明。" * 40,
                ]
            )
            (project_dir / "article.md").write_text(article, encoding="utf-8")

            snapshot = {
                "article_id": "test",
                "agent_version": "0.3.2",
                "git_commit": "0" * 40,
                "git_branch": "test",
                "git_dirty": False,
            }
            (project_dir / "results" / "version-snapshot.json").write_text(
                json.dumps(snapshot), encoding="utf-8"
            )
            review = {
                "publication_status": "READY",
                "scores": {},
                "total": 18,
                "blocking_issues": [],
            }
            (project_dir / "results" / "quality-review.json").write_text(
                json.dumps(review), encoding="utf-8"
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools" / "verify_article_project.py"),
                    "--project-dir",
                    str(project_dir),
                    "--require-quality-review",
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("OK: STEP 1.5 article project is complete", result.stdout)

    def test_missing_article_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools" / "verify_article_project.py"),
                    "--project-dir",
                    temp_dir,
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(0, result.returncode)
            self.assertIn("missing or empty", result.stderr)
