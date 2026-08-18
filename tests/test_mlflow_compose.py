from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class MlflowComposeTest(unittest.TestCase):
    def test_allowed_hosts_accept_local_api_requests_with_ports(self) -> None:
        compose = (ROOT / "infra" / "mlflow" / "compose.yaml").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "localhost:*,127.0.0.1:*,mlflow,mlflow:5000",
            compose,
        )

    def test_review_ui_can_select_unpublished_article_version(self) -> None:
        compose = (ROOT / "infra" / "mlflow" / "compose.yaml").read_text(
            encoding="utf-8"
        )
        self.assertIn("ARTICLE_PATH: ${ARTICLE_PATH:-/article/article.md}", compose)


if __name__ == "__main__":
    unittest.main()
