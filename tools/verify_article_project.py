from __future__ import annotations

import argparse
import json
from pathlib import Path


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
    "## 検証環境",
    "## 結果",
    "## 考察",
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
        review = require_json(project_dir, "results/quality-review.json")
        for field in ["publication_status", "scores", "total", "blocking_issues"]:
            if field not in review:
                raise SystemExit(f"ERROR: quality review is missing field: {field}")

    print(f"OK: STEP 1.5 article project is complete: {project_dir}")
    print(project_dir / "article.md")


if __name__ == "__main__":
    main()
