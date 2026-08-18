from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import mlflow

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evals.scorers.article_scorers import SCORERS  # noqa: E402


@mlflow.trace(
    name="chatgpt_work_article_candidate",
    span_type="CHAT_MODEL",
    attributes={"mlflow.message.format": "openai"},
)
def load_article(article_path: str, messages: list[dict]) -> dict:
    article = Path(article_path).read_text(encoding="utf-8")
    assistant_message = {"role": "assistant", "content": article}

    # The Review UI reads this canonical conversation attribute first.  Keeping
    # it on the traced span makes the article render as Markdown instead of an
    # escaped JSON payload.
    if span := mlflow.get_current_active_span():
        span.set_attribute(
            "mlflow.chat.messages",
            [*messages, assistant_message],
        )

    return {
        "id": f"article-{Path(article_path).stem}",
        "object": "chat.completion",
        "created": 0,
        "model": "technical-blog-article-review",
        "choices": [
            {
                "index": 0,
                "message": assistant_message,
                "finish_reason": "stop",
            }
        ],
    }


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True, text=True
    )
    return result.stdout.strip()


def load_quality_review(project_dir: Path) -> dict:
    path = project_dir / "results" / "quality-review.json"
    if not path.exists():
        return {}
    if path.stat().st_size == 0:
        raise SystemExit(
            "quality review is empty: "
            f"{path}\n"
            "Remove the empty file if Quality Review has not been run, "
            "or generate a valid results/quality-review.json with the quality-review Skill."
        )
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid quality review JSON: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"quality review must be a JSON object: {path}")
    return data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", required=True, type=Path)
    parser.add_argument("--article-id", required=True)
    parser.add_argument(
        "--experiment", default="technical-blog-agent-offline-eval"
    )
    parser.add_argument(
        "--tracking-uri",
        default=os.environ.get("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000"),
    )
    parser.add_argument("--dataset-name", default="ad-hoc")
    parser.add_argument("--dataset-version", default="unversioned")
    args = parser.parse_args()

    article = args.project_dir / "article.md"
    if not article.is_file():
        raise SystemExit(f"article not found: {article}")
    if not article.read_text(encoding="utf-8").strip():
        raise SystemExit(
            "article is empty: "
            f"{article}\n"
            "Use the real article.md produced by the article-drafting phase; "
            "do not create an empty placeholder file for evaluation."
        )

    manifest = json.loads((ROOT / "MANIFEST.json").read_text(encoding="utf-8"))
    git_dirty = bool(git("status", "--porcelain"))
    git_commit = git("rev-parse", "HEAD")
    git_branch = git("branch", "--show-current")

    mlflow.set_tracking_uri(args.tracking_uri)
    mlflow.set_experiment(args.experiment)

    # Experimental MLflow feature; explicit tags below remain the canonical link.
    try:
        mlflow.genai.enable_git_model_versioning()
    except Exception as exc:  # pragma: no cover - version-dependent feature
        print(f"warning: Git model versioning not enabled: {exc}", file=sys.stderr)

    run_name = f"{args.article_id}-{manifest['version']}"
    tags = {
        "article_id": args.article_id,
        "agent_version": manifest["version"],
        "git_commit": git_commit,
        "git_branch": git_branch,
        "git_dirty": str(git_dirty).lower(),
        "evaluation_dataset_name": args.dataset_name,
        "evaluation_dataset_version": args.dataset_version,
        "source": "chatgpt-work",
    }

    quality = load_quality_review(args.project_dir)

    with mlflow.start_run(run_name=run_name, tags=tags) as run:
        mlflow.log_params(
            {
                "agent_version": manifest["version"],
                "git_commit": git_commit,
                "git_branch": git_branch,
                "git_dirty": git_dirty,
                "evaluation_dataset_name": args.dataset_name,
                "evaluation_dataset_version": args.dataset_version,
            }
        )
        mlflow.log_artifact(str(article), artifact_path="article")

        scores = quality.get("scores", {})
        for key, value in scores.items():
            if isinstance(value, (int, float)):
                mlflow.log_metric(f"human_or_agent_review.{key}", float(value))
        if isinstance(quality.get("total"), (int, float)):
            mlflow.log_metric("human_or_agent_review.total", float(quality["total"]))

        with mlflow.tracing.context(tags=tags):
            mlflow.genai.evaluate(
                data=[
                    {
                        "inputs": {
                            "article_path": str(article.resolve()),
                            "messages": [
                                {
                                    "role": "user",
                                    "content": (
                                        "Review the following article candidate "
                                        "using the configured quality rubric."
                                    ),
                                }
                            ],
                        }
                    }
                ],
                predict_fn=load_article,
                scorers=SCORERS,
            )

        print(f"run_id={run.info.run_id}")


if __name__ == "__main__":
    main()
