from __future__ import annotations

import json
import unittest
from pathlib import Path

from evals.scorers.article_scorers import quality_contract_metrics


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "evals" / "datasets" / "article-contract-regressions-v1.jsonl"


class ArticleContractDatasetTest(unittest.TestCase):
    def test_fixed_regression_cases(self) -> None:
        records = [
            json.loads(line)
            for line in DATASET.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self.assertEqual(7, len(records))
        for record in records:
            with self.subTest(case_id=record["case_id"]):
                metrics = quality_contract_metrics(record["article"])
                for metric, expected in record["expectations"].items():
                    self.assertEqual(expected, metrics[metric])


if __name__ == "__main__":
    unittest.main()
