from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def build_snapshot(article_id: str | None = None) -> dict[str, object]:
    manifest = json.loads((ROOT / "MANIFEST.json").read_text(encoding="utf-8"))
    status = git("status", "--porcelain")

    uv_version = subprocess.run(["uv", "--version"], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()

    return {
        "article_id": article_id,
        "agent_version": manifest["version"],
        "git_commit": git("rev-parse", "HEAD"),
        "git_branch": git("branch", "--show-current"),
        "git_dirty": bool(status),
        "git_describe": git("describe", "--tags", "--always", "--dirty"),
        "python_version": sys.version.split()[0],
        "python_executable": sys.executable,
        "uv_version": uv_version,
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--article-id")
    args = parser.parse_args()

    payload = build_snapshot(args.article_id)

    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
        print(args.output)
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
