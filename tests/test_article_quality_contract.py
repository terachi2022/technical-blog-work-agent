from __future__ import annotations

import unittest
import json
import tempfile
from pathlib import Path

from evals.calibrate_review_scores import calibration_report
from evals.quality_review_contract import (
    CRITERIA,
    expected_quality_status,
    validate_quality_review,
)
from evals.scorers.article_scorers import quality_contract_metrics


class ArticleQualityContractTest(unittest.TestCase):
    def test_reader_visible_contract_detects_complete_tutorial(self) -> None:
        article = """# Title

## TL;DR
結論。

## Research Question
問い。

## 仕組みとデータフロー
clientからserverへ送信する。[公式仕様](https://example.com/official)

## 検証環境
M5 Max / Python 3.14.6 / uv

## 検証手順
**実行**
```bash
uv run python app.py
```
**観測結果**
exit code 0

## 結果
結果。

## 仮説と結果の対応
| ID | 実測 | 判定 |
|---|---|---|
| H1 | exit 0 | SUPPORTED |

## 考察
考察。

## 失敗したこと・TIPS
操作、観測、原因、切り分け、修正、再実行を記録した。

## 再現用成果物
- [Repository](https://github.com/example/project)
- [Notebook](https://github.com/example/project/blob/main/demo.ipynb)

## 参考資料
- [Official](https://example.com/official)
"""
        metrics = quality_contract_metrics(article)
        self.assertEqual(1.0, metrics["required_section_coverage"])
        self.assertTrue(metrics["has_inline_source_links"])
        self.assertTrue(metrics["has_hypothesis_result_matrix"])
        self.assertEqual(1.0, metrics["procedure_observation_coverage"])
        self.assertEqual(1.0, metrics["reader_artifact_coverage"])
        self.assertEqual(1.0, metrics["failure_journey_coverage"])

    def test_reference_list_only_is_not_inline_authority(self) -> None:
        article = "# Title\n\n本文\n\n## 参考資料\n\n- [Official](https://example.com)\n"
        self.assertFalse(quality_contract_metrics(article)["has_inline_source_links"])

    def test_quality_ready_requires_threshold_no_zero_and_reader_gate(self) -> None:
        scores = {criterion: 2 for criterion in CRITERIA}
        self.assertEqual(
            "QUALITY_READY",
            expected_quality_status(
                scores=scores,
                publishable="PASS",
                reader_visible_gate="PASS",
                blocking_issues=[],
            ),
        )
        scores["expertise"] = 0
        self.assertEqual(
            "NEEDS_REVISION",
            expected_quality_status(
                scores=scores,
                publishable="PASS",
                reader_visible_gate="PASS",
                blocking_issues=[],
            ),
        )

    def test_score_two_requires_article_location(self) -> None:
        scores = {criterion: 2 for criterion in CRITERIA}
        review = {
            "schema_version": "2.0",
            "review_mode": "article_only_then_evidence_verification",
            "publishable": "PASS",
            "quality_status": "QUALITY_READY",
            "scores": scores,
            "score_evidence": {
                criterion: {
                    "article_locations": [],
                    "rationale": "根拠",
                    "gaps": [],
                }
                for criterion in CRITERIA
            },
            "total": 18,
            "reader_visible_gate": "PASS",
            "blocking_issues": [],
        }
        errors = validate_quality_review(review)
        self.assertEqual(9, sum("needs an article location" in e for e in errors))

    def test_calibration_detects_human_zero_agent_two(self) -> None:
        human_scores = {criterion: 1 for criterion in CRITERIA}
        agent_scores = {criterion: 2 for criterion in CRITERIA}
        human_scores["expertise"] = 0
        with tempfile.TemporaryDirectory() as temp_dir:
            human_path = Path(temp_dir) / "human.json"
            agent_path = Path(temp_dir) / "agent.json"
            human_path.write_text(
                json.dumps({"scores": human_scores, "total": sum(human_scores.values())}),
                encoding="utf-8",
            )
            agent_path.write_text(
                json.dumps({"scores": agent_scores, "total": sum(agent_scores.values())}),
                encoding="utf-8",
            )
            report = calibration_report(human_path, agent_path)
        self.assertIn("expertise", report["critical_false_positive"])
        self.assertFalse(report["acceptance"]["no_human_zero_scored_agent_two"])


if __name__ == "__main__":
    unittest.main()
