from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from evals.run_offline_eval import load_article
from evals.scorers.article_scorers import article_text


class _RecordingSpan:
    def __init__(self) -> None:
        self.attributes: dict[str, object] = {}

    def set_attribute(self, key: str, value: object) -> None:
        self.attributes[key] = value


class ArticleReviewRenderingTest(unittest.TestCase):
    def test_chat_completion_and_span_messages_preserve_markdown(self) -> None:
        markdown = "# Heading\n\n## TL;DR\n\n- item\n"
        messages = [{"role": "user", "content": "Review this article."}]
        span = _RecordingSpan()

        with tempfile.TemporaryDirectory() as temp_dir:
            article = Path(temp_dir) / "article.md"
            article.write_text(markdown, encoding="utf-8")
            with patch(
                "evals.run_offline_eval.mlflow.get_current_active_span",
                return_value=span,
            ):
                response = load_article.__wrapped__(str(article), messages)

        self.assertEqual(markdown, article_text(response))
        self.assertEqual(
            [*messages, {"role": "assistant", "content": markdown}],
            span.attributes["mlflow.chat.messages"],
        )
        self.assertEqual("chat.completion", response["object"])

    def test_article_text_accepts_supported_output_shapes(self) -> None:
        markdown = "# Heading"
        message = {"role": "assistant", "content": markdown}
        response = {"choices": [{"message": message}]}

        self.assertEqual(markdown, article_text(markdown))
        self.assertEqual(markdown, article_text(message))
        self.assertEqual(markdown, article_text(response))


if __name__ == "__main__":
    unittest.main()
