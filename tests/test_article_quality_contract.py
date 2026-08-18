from __future__ import annotations

import unittest
import json
import tempfile
from pathlib import Path

from evals.calibrate_review_scores import calibration_report
from evals.check_article_contract import contract_acceptance
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

## 中核技術の役割
**中核技術の定義**
Trackingは実験のparameter、metric、modelをRunとして記録・可視化する仕組みである。[公式仕様](https://example.com/tracking)

**解決する課題**
実験条件と結果の対応を後から比較できる形で残す。

**今回なぜ必要か**
今回の再現検証で、実行完了だけでなくparameter、metric、modelが保存されたかを判定するために必要である。

## 仕組みとデータフロー
clientからserverへ送信する。[公式仕様](https://example.com/official)

## 技術選定理由
**解決したい課題**
実験clientと常駐serverの依存関係を分離する。

**採用した構成**
uv clientとDocker Compose serverを採用する。

**この構成を選んだ理由**
今回はclientとserverの依存分離を優先して検証する。

**判断根拠**
Research QuestionとComposeの実行ログ。

**適用条件・制約**
ローカルで常駐Tracking Serverが必要な場合。managed serverの比較は対象外。

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
### F-01 Host header error

**発生条件**
hostからTracking APIへ接続した。

**失敗した操作**
```bash
uv run python app.py
```

**エラー全文または主要行**
```text
Invalid Host header: HTTP 403
```

**原因**
port付きHostがallowlistに含まれていなかった。

**切り分け**
healthとAPI endpointを別々に確認した。

**効果がなかった方法**
host名だけをallowlistへ追加してもAPIは403だった。

**修正内容**
```diff
- localhost
+ localhost:*
```

**再実行**
```bash
uv run python app.py
```

**再実行結果**
```text
exit code 0
```

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
        self.assertEqual(1.0, metrics["core_technology_context_coverage"])
        self.assertTrue(metrics["has_core_technology_context"])
        self.assertEqual(1.0, metrics["technology_selection_coverage"])
        self.assertTrue(metrics["has_technology_selection_rationale"])
        self.assertEqual(1.0, metrics["actionable_troubleshooting_coverage"])
        self.assertTrue(metrics["has_error_message_evidence"])
        self.assertTrue(metrics["troubleshooting_error_gate_pass"])
        self.assertTrue(contract_acceptance(metrics)["pass"])

    def test_mechanism_without_selection_rationale_fails_selection_gate(self) -> None:
        article = """# Title

## 仕組みとデータフロー
clientからserverへ送信する。
"""
        metrics = quality_contract_metrics(article)
        self.assertFalse(metrics["has_technology_selection_rationale"])
        self.assertLess(metrics["technology_selection_coverage"], 1.0)
        self.assertFalse(contract_acceptance(metrics)["pass"])

    def test_complete_workflow_without_core_technology_context_fails(self) -> None:
        article = """# Title

## 仕組みとデータフロー
clientからserverへ送信する。

## 技術選定理由
**解決したい課題**
実験を記録する。
**採用した構成**
tracking serverを採用する。
**この構成を選んだ理由**
今回は実験追跡を優先する。
**適用条件・制約**
local tutorialに限る。
"""
        metrics = quality_contract_metrics(article)
        self.assertFalse(metrics["has_core_technology_context"])
        self.assertEqual(0.0, metrics["core_technology_context_coverage"])
        self.assertFalse(contract_acceptance(metrics)["pass"])

    def test_troubleshooting_keywords_without_evidence_do_not_pass(self) -> None:
        article = """# Title

## 失敗したこと・TIPS
操作、観測、原因、切り分け、修正、再実行を記録した。
"""
        metrics = quality_contract_metrics(article)
        self.assertLess(metrics["actionable_troubleshooting_coverage"], 1.0)
        self.assertLess(metrics["failure_journey_coverage"], 1.0)

    def test_empty_not_applicable_reason_does_not_pass(self) -> None:
        article = """# Title

## 失敗したこと・TIPS
**判定**
NOT_APPLICABLE

**理由**

**代替Evidence**
"""
        self.assertLess(
            quality_contract_metrics(article)["actionable_troubleshooting_coverage"],
            1.0,
        )

    def test_actual_failure_without_error_evidence_fails_error_gate(self) -> None:
        article = """# Title

## 失敗したこと・TIPS
**発生条件**
API接続時。
**失敗した操作**
```bash
uv run python app.py
```
**エラー全文または主要行**
エラーが表示された。
**原因**
Host設定。
**切り分け**
endpointを比較した。
**効果がなかった方法**
再読み込み。
**修正内容**
```diff
- localhost
+ localhost:*
```
**再実行**
```bash
uv run python app.py
```
**再実行結果**
```text
exit code 0
```
"""
        metrics = quality_contract_metrics(article)
        self.assertFalse(metrics["has_error_message_evidence"])
        self.assertFalse(metrics["troubleshooting_error_gate_pass"])
        self.assertFalse(contract_acceptance(metrics)["pass"])

    def test_unedited_template_placeholders_do_not_pass_strict_contract(self) -> None:
        article = """# Title

## 技術選定理由
**解決したい課題**
課題。
**採用した構成**
構成。
**この構成を選んだ理由**
今回はこの構成を優先する。
**判断根拠**
Evidenceに基づく理由。
**適用条件・制約**
条件。
    """
        metrics = quality_contract_metrics(article)
        self.assertFalse(metrics["no_unresolved_publication_placeholders"])
        self.assertFalse(contract_acceptance(metrics)["pass"])

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
