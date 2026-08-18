from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from evals.human_review.export_review import (
    dataset_record,
    normalize_human_assessments,
)
from evals.quality_review_contract import CRITERIA


class ExportHumanReviewTest(unittest.TestCase):
    def assessments(self) -> list[dict]:
        items = []
        for criterion in CRITERIA:
            items.append(
                {
                    "assessment_name": f"human_review.{criterion}",
                    "source": {"source_type": "HUMAN", "source_id": "reviewer"},
                    "last_update_time": "2026-08-18T00:00:00Z",
                    "feedback": {"value": "2"},
                    "rationale": f"{criterion} rationale",
                    "valid": True,
                }
            )
        items.extend(
            [
                {
                    "assessment_name": "human_review.publishable",
                    "source": {"source_type": "HUMAN", "source_id": "reviewer"},
                    "last_update_time": "2026-08-18T00:00:01Z",
                    "feedback": {"value": "PASS"},
                    "valid": True,
                },
                {
                    "assessment_name": "human_review.critical_issue",
                    "source": {"source_type": "HUMAN", "source_id": "reviewer"},
                    "last_update_time": "2026-08-18T00:00:02Z",
                    "feedback": {"value": "なし"},
                    "valid": True,
                },
            ]
        )
        return items

    def test_normalizes_all_human_feedback(self) -> None:
        review = normalize_human_assessments(self.assessments())
        self.assertEqual(18, review["total"])
        self.assertEqual("PASS", review["publishable"])
        self.assertEqual("reviewer", review["reviewer"])
        self.assertEqual(9, len(review["rationales"]))

    def test_dataset_record_hashes_exact_article(self) -> None:
        review = normalize_human_assessments(self.assessments())
        with tempfile.TemporaryDirectory() as temp_dir:
            article = Path(temp_dir) / "article.md"
            article.write_text("# article\n", encoding="utf-8")
            record = dataset_record(
                review=review,
                case_id="HC002",
                article_id="article-v2",
                article_path=article,
                rubric_version="2.0",
                source_url=None,
                holdout=True,
            )
        self.assertEqual(10, record["article_bytes"])
        self.assertEqual(64, len(record["article_sha256"]))
        self.assertTrue(record["holdout"])

    def test_missing_feedback_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "missing Human Feedback"):
            normalize_human_assessments(self.assessments()[:-1])


if __name__ == "__main__":
    unittest.main()
