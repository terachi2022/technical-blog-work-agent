from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "resources" / "project-state-template.md"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Initialize one technical-blog article project outside the Agent repository."
    )
    parser.add_argument("--projects-root", type=Path, required=True)
    parser.add_argument("--article-id", required=True)
    parser.add_argument("--topic", required=True)
    parser.add_argument("--name")
    args = parser.parse_args()

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
    state = state.replace("- Name:\n", f"- Name: {args.name or args.article_id}\n", 1)
    state = state.replace("- Topic:\n", f"- Topic: {args.topic}\n", 1)
    state = state.replace("- Article ID:\n", f"- Article ID: {args.article_id}\n", 1)
    state = state.replace(
        "- Last updated:\n",
        f"- Last updated: {datetime.now().astimezone().isoformat(timespec='seconds')}\n",
        1,
    )
    state = state.replace("- Current phase:\n", "- Current phase: 1 Research\n", 1)
    state = state.replace(
        "- Next action:\n",
        "- Next action: Run technical-research and create research.md\n",
        1,
    )
    (project_dir / "PROJECT_STATE.md").write_text(state, encoding="utf-8")

    readme = (
        f"# {args.article_id}\n\n"
        f"- Topic: {args.topic}\n"
        f"- Article ID: {args.article_id}\n"
        "- Agent repository: managed separately\n\n"
        "This directory is the Source of Truth for this article's research, "
        "experiment evidence, analysis, and draft.\n"
    )
    (project_dir / "README.md").write_text(readme, encoding="utf-8")

    print(project_dir)
    print(project_dir / "PROJECT_STATE.md")


if __name__ == "__main__":
    main()
