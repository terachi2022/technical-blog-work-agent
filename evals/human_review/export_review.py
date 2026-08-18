from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

import mlflow
from mlflow import MlflowClient
from mlflow.genai import review_queues

from evals.quality_review_contract import CRITERIA


REQUIRED_FEEDBACK = [
    *(f"human_review.{criterion}" for criterion in CRITERIA),
    "human_review.publishable",
    "human_review.critical_issue",
]


def normalize_human_assessments(assessments: list[dict[str, Any]]) -> dict[str, Any]:
    latest: dict[str, dict[str, Any]] = {}
    for assessment in assessments:
        name = assessment.get("assessment_name")
        source = assessment.get("source") or {}
        if (
            name not in REQUIRED_FEEDBACK
            or source.get("source_type") != "HUMAN"
            or not assessment.get("valid", True)
        ):
            continue
        current = latest.get(name)
        if current is None or str(assessment.get("last_update_time", "")) >= str(
            current.get("last_update_time", "")
        ):
            latest[name] = assessment

    missing = [name for name in REQUIRED_FEEDBACK if name not in latest]
    if missing:
        raise ValueError(f"missing Human Feedback: {', '.join(missing)}")

    scores: dict[str, int] = {}
    rationales: dict[str, str] = {}
    for criterion in CRITERIA:
        assessment = latest[f"human_review.{criterion}"]
        raw_value = (assessment.get("feedback") or {}).get("value")
        try:
            value = int(raw_value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"invalid Human score {criterion}: {raw_value!r}") from exc
        if value not in {0, 1, 2}:
            raise ValueError(f"invalid Human score {criterion}: {value}")
        scores[criterion] = value
        rationales[criterion] = str(assessment.get("rationale") or "")

    publishable = str(
        (latest["human_review.publishable"].get("feedback") or {}).get("value")
    )
    if publishable not in {"PASS", "FAIL"}:
        raise ValueError(f"invalid publishable value: {publishable!r}")

    completed = max(
        str(assessment.get("last_update_time") or assessment.get("create_time") or "")
        for assessment in latest.values()
    )
    reviewer_ids = {
        str((assessment.get("source") or {}).get("source_id"))
        for assessment in latest.values()
    }
    if len(reviewer_ids) != 1:
        raise ValueError(f"Human Feedback has multiple reviewers: {sorted(reviewer_ids)}")

    return {
        "completed_at": completed,
        "reviewer": reviewer_ids.pop(),
        "scores": scores,
        "total": sum(scores.values()),
        "max_total": 18,
        "publishable": publishable,
        "critical_issue": str(
            (latest["human_review.critical_issue"].get("feedback") or {}).get("value")
            or ""
        ),
        "rationales": rationales,
    }


def dataset_record(
    *,
    review: dict[str, Any],
    case_id: str,
    article_id: str,
    article_path: Path,
    rubric_version: str,
    source_url: str | None,
    holdout: bool,
) -> dict[str, Any]:
    article_bytes = article_path.read_bytes()
    return {
        "case_id": case_id,
        "article_id": article_id,
        "article_sha256": hashlib.sha256(article_bytes).hexdigest(),
        "article_bytes": len(article_bytes),
        "source_url": source_url,
        "rubric_version": rubric_version,
        "reviewer": review["reviewer"],
        "reviewed_at": review["completed_at"],
        "scores": review["scores"],
        "total": review["total"],
        "publishable": review["publishable"],
        "label_source": "human",
        "holdout": holdout,
        "notes": "Exported from MLflow Human Feedback; retain rationales in the project review artifact.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export completed MLflow Human Feedback without manual transcription."
    )
    parser.add_argument("--trace-id", required=True)
    parser.add_argument("--queue-id", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--tracking-uri",
        default=os.environ.get("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000"),
    )
    parser.add_argument("--agent-review", type=Path)
    parser.add_argument("--dataset-output", type=Path)
    parser.add_argument("--case-id")
    parser.add_argument("--article-id")
    parser.add_argument("--article-path", type=Path)
    parser.add_argument("--rubric-version", default="2.1")
    parser.add_argument("--source-url")
    parser.add_argument("--holdout", action="store_true")
    args = parser.parse_args()

    mlflow.set_tracking_uri(args.tracking_uri)
    trace = MlflowClient().get_trace(args.trace_id)
    assessments = [item.to_dictionary() for item in trace.info.assessments]
    review = normalize_human_assessments(assessments)

    queue_items = list(
        review_queues.list_review_queue_items(args.queue_id, max_results=1000)
    )
    item = next((item for item in queue_items if item.item_id == args.trace_id), None)
    if item is None:
        raise SystemExit(f"Trace is not in Review Queue: {args.trace_id}")
    if str(item.status) != "complete":
        raise SystemExit(f"Human Review is not complete: {item.status}")

    result: dict[str, Any] = {
        "schema_version": "2.0",
        **review,
        "trace_id": args.trace_id,
        "queue_id": args.queue_id,
        "queue_item_status": str(item.status),
        "review_surface": "full_article_review",
    }
    if args.agent_review:
        agent = json.loads(args.agent_review.read_text(encoding="utf-8"))
        agent_scores = agent.get("scores") or {}
        absolute_errors = {
            criterion: abs(int(agent_scores[criterion]) - review["scores"][criterion])
            for criterion in CRITERIA
        }
        result["automated_or_agent_review"] = {
            "artifact": str(args.agent_review),
            "total": agent.get("total"),
            "difference_human_minus_agent": review["total"] - int(agent["total"]),
            "absolute_errors": absolute_errors,
            "mean_absolute_error": sum(absolute_errors.values()) / len(CRITERIA),
            "max_absolute_error": max(absolute_errors.values()),
        }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    if args.dataset_output:
        required = {
            "--case-id": args.case_id,
            "--article-id": args.article_id,
            "--article-path": args.article_path,
        }
        missing = [flag for flag, value in required.items() if value is None]
        if missing:
            raise SystemExit(
                "dataset export requires " + ", ".join(missing)
            )
        record = dataset_record(
            review=review,
            case_id=args.case_id,
            article_id=args.article_id,
            article_path=args.article_path,
            rubric_version=args.rubric_version,
            source_url=args.source_url,
            holdout=args.holdout,
        )
        args.dataset_output.parent.mkdir(parents=True, exist_ok=True)
        args.dataset_output.write_text(
            json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
