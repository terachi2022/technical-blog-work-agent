from __future__ import annotations

import argparse
import json
from pathlib import Path

from evals.quality_review_contract import CRITERIA


def load_scores(path: Path) -> tuple[dict[str, int], int]:
    data = json.loads(path.read_text(encoding="utf-8"))
    scores = data.get("scores")
    if not isinstance(scores, dict):
        raise SystemExit(f"scores object not found: {path}")
    normalized: dict[str, int] = {}
    for criterion in CRITERIA:
        score = scores.get(criterion)
        if type(score) is not int or score not in {0, 1, 2}:
            raise SystemExit(f"invalid score {criterion}: {path}")
        normalized[criterion] = score
    total = data.get("total")
    if total != sum(normalized.values()):
        raise SystemExit(f"total does not equal score sum: {path}")
    return normalized, total


def calibration_report(human_path: Path, agent_path: Path) -> dict[str, object]:
    human, human_total = load_scores(human_path)
    agent, agent_total = load_scores(agent_path)
    absolute_errors = {
        criterion: abs(agent[criterion] - human[criterion])
        for criterion in CRITERIA
    }
    critical_false_positive = [
        criterion
        for criterion in CRITERIA
        if human[criterion] == 0 and agent[criterion] == 2
    ]
    return {
        "human_review": str(human_path.resolve()),
        "agent_review": str(agent_path.resolve()),
        "human_total": human_total,
        "agent_total": agent_total,
        "total_gap_agent_minus_human": agent_total - human_total,
        "absolute_errors": absolute_errors,
        "mean_absolute_error": sum(absolute_errors.values()) / len(CRITERIA),
        "max_absolute_error": max(absolute_errors.values()),
        "critical_false_positive": critical_false_positive,
        "acceptance": {
            "total_gap_within_2": abs(agent_total - human_total) <= 2,
            "all_item_gaps_within_1": max(absolute_errors.values()) <= 1,
            "no_human_zero_scored_agent_two": not critical_false_positive,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Measure Agent review error against a Human Review label."
    )
    parser.add_argument("--human-review", required=True, type=Path)
    parser.add_argument("--agent-review", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = calibration_report(args.human_review, args.agent_review)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
