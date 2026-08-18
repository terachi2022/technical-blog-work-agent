from __future__ import annotations

from typing import Any


CRITERIA = (
    "experience",
    "expertise",
    "authoritativeness",
    "trustworthiness",
    "originality",
    "reproducibility",
    "usefulness",
    "evidence",
    "clarity",
)

QUALITY_READY_MINIMUM = 14


def expected_quality_status(
    *,
    scores: dict[str, int],
    publishable: str,
    reader_visible_gate: str,
    blocking_issues: list[object],
) -> str:
    if publishable == "BLOCK":
        return "BLOCKED"
    if (
        sum(scores.values()) >= QUALITY_READY_MINIMUM
        and all(score > 0 for score in scores.values())
        and reader_visible_gate == "PASS"
        and not blocking_issues
    ):
        return "QUALITY_READY"
    return "NEEDS_REVISION"


def validate_quality_review(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["review must be a JSON object"]

    if data.get("schema_version") not in {"2.0", "2.1"}:
        errors.append("schema_version must be '2.0' or '2.1'")
    if data.get("review_mode") != "article_only_then_evidence_verification":
        errors.append(
            "review_mode must be 'article_only_then_evidence_verification'"
        )

    publishable = data.get("publishable")
    if publishable not in {"PASS", "WARN", "BLOCK"}:
        errors.append("publishable must be PASS, WARN, or BLOCK")

    reader_gate = data.get("reader_visible_gate")
    if reader_gate not in {"PASS", "FAIL"}:
        errors.append("reader_visible_gate must be PASS or FAIL")

    blocking_issues = data.get("blocking_issues")
    if not isinstance(blocking_issues, list):
        errors.append("blocking_issues must be a list")
        blocking_issues = []

    scores = data.get("scores")
    valid_scores: dict[str, int] = {}
    if not isinstance(scores, dict):
        errors.append("scores must be an object")
    else:
        for criterion in CRITERIA:
            score = scores.get(criterion)
            if type(score) is not int or score not in {0, 1, 2}:
                errors.append(f"scores.{criterion} must be 0, 1, or 2")
            else:
                valid_scores[criterion] = score

    score_evidence = data.get("score_evidence")
    if not isinstance(score_evidence, dict):
        errors.append("score_evidence must be an object")
    else:
        for criterion in CRITERIA:
            evidence = score_evidence.get(criterion)
            if not isinstance(evidence, dict):
                errors.append(f"score_evidence.{criterion} must be an object")
                continue
            locations = evidence.get("article_locations")
            if not isinstance(locations, list):
                errors.append(
                    f"score_evidence.{criterion}.article_locations must be a list"
                )
                locations = []
            if not isinstance(evidence.get("rationale"), str) or not evidence.get(
                "rationale", ""
            ).strip():
                errors.append(
                    f"score_evidence.{criterion}.rationale must be non-empty"
                )
            if not isinstance(evidence.get("gaps"), list):
                errors.append(f"score_evidence.{criterion}.gaps must be a list")
            if valid_scores.get(criterion) == 2 and not locations:
                errors.append(
                    f"score_evidence.{criterion} needs an article location for score 2"
                )

    if len(valid_scores) == len(CRITERIA):
        calculated_total = sum(valid_scores.values())
        if data.get("total") != calculated_total:
            errors.append(f"total must equal the score sum ({calculated_total})")
        if (
            publishable in {"PASS", "WARN", "BLOCK"}
            and reader_gate in {"PASS", "FAIL"}
        ):
            expected = expected_quality_status(
                scores=valid_scores,
                publishable=publishable,
                reader_visible_gate=reader_gate,
                blocking_issues=blocking_issues,
            )
            if data.get("quality_status") != expected:
                errors.append(f"quality_status must be {expected}")

    return errors
