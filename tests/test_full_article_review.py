from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from evals.human_review.full_article_review import (
    QUALITY_QUESTIONS,
    ReviewConfig,
    page_template,
    parse_review,
    render_article,
    submit_review,
)


class FullArticleReviewTest(unittest.TestCase):
    def test_full_markdown_renders_through_last_section(self) -> None:
        markdown = "# Title\n\n## TL;DR\n\ntext\n\n## 参考資料\n\n- https://example.com\n"
        rendered = render_article(markdown)
        with tempfile.TemporaryDirectory() as temp_dir:
            config = ReviewConfig(Path(temp_dir) / "article.md", "http://mlflow:5000", "rq-1", "tr-1", "tera")
            page = page_template(rendered, config, "csrf")
        self.assertIn("<h1>Title</h1>", page)
        self.assertIn("<h2>参考資料</h2>", page)
        self.assertIn("解決課題・採用案・不採用案", page)
        self.assertIn("失敗操作・エラー主要行・修正差分", page)
        self.assertNotIn("text...", page)

    def test_parse_review_requires_all_eleven_answers(self) -> None:
        values = {f"score.{name}": ["2"] for name in QUALITY_QUESTIONS}
        values.update(
            {f"rationale.{name}": ["記事中の該当箇所"] for name in QUALITY_QUESTIONS}
        )
        values.update({"publishable": ["PASS"], "critical_issue": ["なし"]})
        answers, _ = parse_review(values)
        self.assertEqual(11, len(answers))
        self.assertEqual("PASS", answers["human_review.publishable"])

    @patch("evals.human_review.full_article_review.review_queues.set_review_queue_item_status")
    @patch("evals.human_review.full_article_review.mlflow.log_feedback")
    @patch("evals.human_review.full_article_review.mlflow.set_tracking_uri")
    def test_submit_records_feedback_then_completes_queue(self, set_uri, log_feedback, set_status) -> None:
        config = ReviewConfig(Path("article.md"), "http://mlflow:5000", "rq-1", "tr-1", "tera")
        answers = {f"human_review.{name}": "2" for name in QUALITY_QUESTIONS}
        answers.update({"human_review.publishable": "PASS", "human_review.critical_issue": "なし"})
        submit_review(config, answers, {})
        set_uri.assert_called_once_with("http://mlflow:5000")
        self.assertEqual(11, log_feedback.call_count)
        set_status.assert_called_once_with("rq-1", item_id="tr-1", status="complete", completed_by="tera")


if __name__ == "__main__":
    unittest.main()
