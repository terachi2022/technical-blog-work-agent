from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from evals.check_article_contract import contract_acceptance
from evals.scorers.article_scorers import quality_contract_metrics


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
                    "## 仕組みとデータフロー",
                    "clientからserverへEvidenceを送る。[公式仕様](https://example.com/official)",
                    "## 技術選定理由",
                    "**解決したい課題**",
                    "clientとserverの依存を分離する。",
                    "**採用した構成**",
                    "uv clientとCompose server。",
                    "**この構成を選んだ理由**",
                    "今回は依存分離の検証を優先する。",
                    "**判断根拠**",
                    "Research QuestionとCompose実行ログ。",
                    "**適用条件・制約**",
                    "local serverが必要な場合。managed server比較は対象外。",
                    "## 検証環境",
                    "Apple M5 Max、Python 3.14.6。",
                    "## 検証手順",
                    "**実行**",
                    "```bash\nuv run python app.py\n```",
                    "**観測結果**",
                    "exit code 0。",
                    "## 結果",
                    "実行ログから確認した結果です。",
                    "## 仮説と結果の対応",
                    "| ID | 実測 | 判定 |\n|---|---|---|\n| H1 | exit 0 | SUPPORTED |",
                    "## 考察",
                    "結果と一次情報を分離して考察します。",
                    "## 失敗したこと・TIPS",
                    "### F-01 API error",
                    "**発生条件**",
                    "hostからAPIへ接続。",
                    "**失敗した操作**",
                    "```bash\nuv run python app.py\n```",
                    "**エラー全文または主要行**",
                    "```text\nHTTP 403 Invalid Host header\n```",
                    "**原因**",
                    "port付きHostが未許可。",
                    "**切り分け**",
                    "healthとAPIを比較。",
                    "**効果がなかった方法**",
                    "Host名だけの追加。",
                    "**修正内容**",
                    "```diff\n- localhost\n+ localhost:*\n```",
                    "**再実行**",
                    "```bash\nuv run python app.py\n```",
                    "**再実行結果**",
                    "```text\nexit code 0\n```",
                    "## 再現用成果物",
                    "- [Repository](https://github.com/example/project)",
                    "- [Notebook](https://github.com/example/project/blob/main/demo.ipynb)",
                    "## 参考資料",
                    "公式資料を参照します。",
                    "検証手順とEvidenceの説明。" * 40,
                ]
            )
            (project_dir / "article.md").write_text(article, encoding="utf-8")
            metrics = quality_contract_metrics(article)
            (project_dir / "results" / "article-contract.json").write_text(
                json.dumps(
                    {"metrics": metrics, "acceptance": contract_acceptance(metrics)}
                ),
                encoding="utf-8",
            )

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
                "schema_version": "2.2",
                "review_mode": "article_only_then_evidence_verification",
                "publishable": "PASS",
                "quality_status": "QUALITY_READY",
                "scores": {
                    "experience": 2,
                    "expertise": 2,
                    "authoritativeness": 2,
                    "trustworthiness": 2,
                    "originality": 2,
                    "reproducibility": 2,
                    "usefulness": 2,
                    "evidence": 2,
                    "clarity": 2,
                },
                "score_evidence": {
                    criterion: {
                        "article_locations": ["## 結果"],
                        "rationale": "テスト用の根拠",
                        "gaps": [],
                    }
                    for criterion in [
                        "experience",
                        "expertise",
                        "authoritativeness",
                        "trustworthiness",
                        "originality",
                        "reproducibility",
                        "usefulness",
                        "evidence",
                        "clarity",
                    ]
                },
                "total": 18,
                "reader_visible_gate": "PASS",
                "blocking_issues": [],
            }
            (project_dir / "results" / "quality-review.json").write_text(
                json.dumps(review), encoding="utf-8"
            )
            evidence_map = {
                "schema_version": "1.1",
                "article": "article.md",
                "claims": [{"id": "C-01", "reader_visible": True}],
                "hypotheses": [],
                "decisions": [{"id": "D-01", "selected": "uv + Compose"}],
                "failures": [{"id": "F-01", "status": "RESOLVED"}],
                "reader_assets": [{"type": "repository", "url": "https://example.com"}],
            }
            (project_dir / "results" / "article-evidence-map.json").write_text(
                json.dumps(evidence_map), encoding="utf-8"
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
