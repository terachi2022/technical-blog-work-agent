from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from evals.scorers.article_scorers import quality_contract_metrics


STRICT_REQUIREMENTS = {
    "required_section_coverage": 1.0,
    "has_inline_source_links": True,
    "has_hypothesis_result_matrix": True,
    "procedure_observation_coverage": 1.0,
    "reader_artifact_coverage": 1.0,
    "actionable_troubleshooting_coverage": 1.0,
    "troubleshooting_error_gate_pass": True,
    "has_technology_selection_rationale": True,
    "no_unresolved_publication_placeholders": True,
}


def contract_acceptance(metrics: dict[str, Any]) -> dict[str, Any]:
    failures = {
        name: {"expected": expected, "actual": metrics.get(name)}
        for name, expected in STRICT_REQUIREMENTS.items()
        if metrics.get(name) != expected
    }
    return {"pass": not failures, "failures": failures}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check the deterministic reader-visible article contract."
    )
    parser.add_argument("--article", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    article = args.article.read_text(encoding="utf-8")
    metrics = quality_contract_metrics(article)
    result = {
        "article": str(args.article.resolve()),
        "metrics": metrics,
        "acceptance": contract_acceptance(metrics),
    }
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    if args.strict and not result["acceptance"]["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
