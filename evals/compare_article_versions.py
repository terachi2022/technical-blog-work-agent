from __future__ import annotations

import argparse
import json
from pathlib import Path

from evals.quality_review_contract import CRITERIA
from evals.scorers.article_scorers import quality_contract_metrics


def load_json(path: Path | None) -> dict[str, object]:
    if path is None:
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def article_report(article: Path, review: Path | None) -> dict[str, object]:
    text = article.read_text(encoding="utf-8")
    review_data = load_json(review)
    return {
        "article": str(article.resolve()),
        "bytes": len(text.encode("utf-8")),
        "machine_contract": quality_contract_metrics(text),
        "review": {
            key: review_data.get(key)
            for key in ["schema_version", "publishable", "quality_status", "total"]
            if key in review_data
        },
        "scores": {
            criterion: review_data.get("scores", {}).get(criterion)
            for criterion in CRITERIA
            if isinstance(review_data.get("scores"), dict)
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare reader-visible article contract metrics and review scores."
    )
    parser.add_argument("--before", required=True, type=Path)
    parser.add_argument("--after", required=True, type=Path)
    parser.add_argument("--before-review", type=Path)
    parser.add_argument("--after-review", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    before = article_report(args.before, args.before_review)
    after = article_report(args.after, args.after_review)
    result = {"before": before, "after": after}
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
