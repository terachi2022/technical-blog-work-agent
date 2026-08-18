from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evals.quality_review_contract import validate_quality_review  # noqa: E402
from evals.scorers.article_scorers import quality_contract_metrics  # noqa: E402


REQUIRED_TEXT_FILES = [
    "PROJECT_STATE.md",
    "AGENT_TASK.md",
    "research.md",
    "hypothesis.md",
    "experiment-plan.md",
    "experiment-log.md",
    "analysis.md",
    "discussion.md",
    "article.md",
]

ARTICLE_REQUIRED_HEADINGS = [
    "## TL;DR",
    "## Research Question",
    "## 中核技術の役割",
    "## 仕組みとデータフロー",
    "## 技術選定理由",
    "## 検証環境",
    "## 結果",
    "## 仮説と結果の対応",
    "## 考察",
    "## 失敗したこと・TIPS",
    "## 再現用成果物",
    "## 参考資料",
]


def require_non_empty(project_dir: Path, relative_path: str) -> None:
    path = project_dir / relative_path
    if not path.is_file() or not path.read_text(encoding="utf-8").strip():
        raise SystemExit(f"ERROR: missing or empty: {path}")


def require_json(project_dir: Path, relative_path: str) -> dict[str, object]:
    path = project_dir / relative_path
    require_non_empty(project_dir, relative_path)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"ERROR: invalid JSON: {path}: {exc}") from exc


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verify that STEP 1.5 produced a real article and its canonical evidence artifacts."
    )
    parser.add_argument("--project-dir", type=Path, required=True)
    parser.add_argument("--require-quality-review", action="store_true")
    args = parser.parse_args()

    project_dir = args.project_dir.expanduser().resolve()
    for relative_path in REQUIRED_TEXT_FILES:
        require_non_empty(project_dir, relative_path)

    snapshot = require_json(project_dir, "results/version-snapshot.json")
    for field in ["article_id", "agent_version", "git_commit", "git_branch", "git_dirty"]:
        if field not in snapshot:
            raise SystemExit(f"ERROR: version snapshot is missing field: {field}")

    article = (project_dir / "article.md").read_text(encoding="utf-8")
    if len(article.strip()) < 500:
        raise SystemExit("ERROR: article.md is too short to be a real baseline article")
    for heading in ARTICLE_REQUIRED_HEADINGS:
        if heading not in article:
            raise SystemExit(f"ERROR: article.md is missing required heading: {heading}")

    state = (project_dir / "PROJECT_STATE.md").read_text(encoding="utf-8")
    if not any(
        "| 11 | Article | COMPLETED |" in line
        for line in state.splitlines()
    ):
        raise SystemExit("ERROR: PROJECT_STATE.md does not mark Phase 11 Article as COMPLETED")

    if args.require_quality_review:
        metrics = quality_contract_metrics(article)
        if not metrics["has_technology_selection_rationale"]:
            raise SystemExit(
                "ERROR: article.md is missing a complete technology selection rationale"
            )
        if not metrics["has_core_technology_context"]:
            raise SystemExit(
                "ERROR: article.md is missing the core technology definition, problem, or article-specific need"
            )
        if metrics["actionable_troubleshooting_coverage"] != 1.0:
            raise SystemExit(
                "ERROR: article.md troubleshooting is not actionable or validly NOT_APPLICABLE"
            )
        if not metrics["troubleshooting_error_gate_pass"]:
            raise SystemExit(
                "ERROR: an actual failure is missing reader-visible error message evidence"
            )
        contract_result = require_json(project_dir, "results/article-contract.json")
        acceptance = contract_result.get("acceptance")
        if not isinstance(acceptance, dict) or acceptance.get("pass") is not True:
            raise SystemExit("ERROR: results/article-contract.json is not PASS")
        if contract_result.get("metrics") != metrics:
            raise SystemExit(
                "ERROR: results/article-contract.json metrics are stale for article.md"
            )
        review = require_json(project_dir, "results/quality-review.json")
        errors = validate_quality_review(review)
        if errors:
            formatted = "\n".join(f"- {error}" for error in errors)
            raise SystemExit(f"ERROR: invalid quality review contract:\n{formatted}")
        evidence_map = require_json(project_dir, "results/article-evidence-map.json")
        for field in [
            "schema_version",
            "article",
            "claims",
            "decisions",
            "failures",
            "reader_assets",
        ]:
            if field not in evidence_map:
                raise SystemExit(
                    f"ERROR: article evidence map is missing field: {field}"
                )
        for field in ["claims", "decisions", "failures", "reader_assets"]:
            if not isinstance(evidence_map[field], list) or not evidence_map[field]:
                raise SystemExit(
                    f"ERROR: article evidence map field must be a non-empty list: {field}"
                )

    print(f"OK: STEP 1.5 article project is complete: {project_dir}")
    print(project_dir / "article.md")


if __name__ == "__main__":
    main()
