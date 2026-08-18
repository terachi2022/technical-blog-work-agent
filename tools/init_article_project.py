from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

from version_snapshot import build_snapshot

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "resources" / "project-state-template.md"
TASK_TEMPLATE = ROOT / "agent" / "START_PROMPT.md"


def replace_field(text: str, field: str, value: str) -> str:
    marker = f"- {field}:"
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line == marker or line.startswith(f"{marker} "):
            lines[index] = f"{marker} {value}"
            return "\n".join(lines) + "\n"
    raise ValueError(f"missing field in project state template: {field}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Initialize one technical-blog article project outside the Agent repository."
    )
    parser.add_argument("--projects-root", type=Path, required=True)
    parser.add_argument("--article-id", required=True)
    parser.add_argument("--topic", required=True)
    parser.add_argument("--audience", required=True)
    parser.add_argument("--name")
    parser.add_argument("--model-runtime", default="ChatGPT Work")
    parser.add_argument(
        "--allow-dirty",
        action="store_true",
        help="Allow initialization from a dirty Agent repository for non-baseline testing.",
    )
    args = parser.parse_args()

    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", args.article_id):
        raise SystemExit(
            "article-id must be one directory name using only letters, numbers, dot, underscore, or hyphen"
        )
    if not args.topic.strip() or not args.audience.strip():
        raise SystemExit("topic and audience must not be empty")

    projects_root = args.projects_root.expanduser().resolve()
    project_dir = projects_root / args.article_id

    try:
        project_dir.relative_to(ROOT.resolve())
    except ValueError:
        pass
    else:
        raise SystemExit(
            f"refusing to create article project inside Agent repository: {project_dir}\n"
            "Use a separate root such as ~/dev/technical-blog-projects."
        )

    snapshot = build_snapshot(args.article_id)
    if snapshot["git_dirty"] and not args.allow_dirty:
        raise SystemExit(
            "refusing to initialize a formal baseline from a dirty Agent repository\n"
            "Commit or restore Agent changes first. Use --allow-dirty only for a non-baseline test."
        )

    if project_dir.exists() and any(project_dir.iterdir()):
        raise SystemExit(f"project directory already exists and is not empty: {project_dir}")

    for rel in [
        "data/raw",
        "data/processed",
        "results",
        "logs",
        "images",
        "scripts",
    ]:
        (project_dir / rel).mkdir(parents=True, exist_ok=True)

    state = TEMPLATE.read_text(encoding="utf-8")
    values = {
        "Name": args.name or args.article_id,
        "Topic": args.topic,
        "Article ID": args.article_id,
        "Last updated": datetime.now().astimezone().isoformat(timespec="seconds"),
        "Current phase": "1 Research",
        "Next action": "Read AGENT_TASK.md and run Phase 1 through article generation",
        "Agent version": str(snapshot["agent_version"]),
        "Git commit": str(snapshot["git_commit"]),
        "Git branch": str(snapshot["git_branch"]),
        "Git dirty": str(snapshot["git_dirty"]).lower(),
        "Model / runtime": args.model_runtime,
    }
    for field, value in values.items():
        state = replace_field(state, field, value)
    (project_dir / "PROJECT_STATE.md").write_text(state, encoding="utf-8")

    snapshot_path = project_dir / "results" / "version-snapshot.json"
    snapshot_path.write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    task = TASK_TEMPLATE.read_text(encoding="utf-8")
    replacements = {
        "{{ARTICLE_ID}}": args.article_id,
        "{{PROJECT_DIR}}": str(project_dir),
        "{{AGENT_REPOSITORY}}": str(ROOT),
        "{{TOPIC}}": args.topic,
        "{{AUDIENCE}}": args.audience,
        "{{MODEL_RUNTIME}}": args.model_runtime,
    }
    for marker, value in replacements.items():
        task = task.replace(marker, value)
    unresolved = [marker for marker in replacements if marker in task]
    if unresolved:
        raise RuntimeError(f"unresolved task template markers: {unresolved}")
    task_path = project_dir / "AGENT_TASK.md"
    task_path.write_text(task, encoding="utf-8")

    readme = (
        f"# {args.article_id}\n\n"
        f"- Topic: {args.topic}\n"
        f"- Audience: {args.audience}\n"
        f"- Article ID: {args.article_id}\n"
        f"- Agent repository: {ROOT}\n"
        "- Execution task: AGENT_TASK.md\n\n"
        "This directory is the Source of Truth for this article's research, "
        "experiment evidence, analysis, and draft.\n"
    )
    (project_dir / "README.md").write_text(readme, encoding="utf-8")

    print(project_dir)
    print(project_dir / "PROJECT_STATE.md")
    print(snapshot_path)
    print(task_path)
    print()
    print("NEXT ACTION")
    print(f"Read {task_path} and execute it continuously through article.md generation.")


if __name__ == "__main__":
    main()
