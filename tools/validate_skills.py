from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
RES = ROOT / "resources"
AGENT = ROOT / "agent" / "AGENT_INSTRUCTIONS.md"

errors = []
count = 0

required_resources = [
    "environment-policy.md",
    "source-policy.md",
    "google-search-quality-policy.md",
    "eeat-quality-policy.md",
    "evidence-gate.md",
    "project-layout.md",
    "project-state-template.md",
    "qiita-style-guide.md",
    "article-template.md",
    "experiment-plan-template.md",
    "evidence-record-template.md",
    "review-rubric.md",
    "content-mlops-concept.md",
    "versioning-policy.md",
    "evaluation-policy.md",
    "production-metrics-policy.md",
]

for name in required_resources:
    if not (RES / name).is_file():
        errors.append(f"missing required resource: resources/{name}")

if not AGENT.is_file():
    errors.append("missing agent/AGENT_INSTRUCTIONS.md")
    agent_text = ""
else:
    agent_text = AGENT.read_text(encoding="utf-8")

agent_required_terms = [
    "PROJECT_STATE.md",
    "Evidence Gate",
    "evidence-gate.md",
    "google-search-quality-policy.md",
    "project-layout.md",
    "article-drafting",
    "quality-review",
    "E-E-A-T / Quality score",
    "Content MLOps",
    "GitHub",
    "MLflow",
    "Offline Quality",
    "Production Performance",
]
for term in agent_required_terms:
    if term not in agent_text:
        errors.append(f"AGENT_INSTRUCTIONS.md: missing required term {term!r}")

for skill_md in sorted(SKILLS.glob("*/SKILL.md")):
    count += 1
    text = skill_md.read_text(encoding="utf-8")

    if not text.startswith("---\n"):
        errors.append(f"{skill_md}: YAML frontmatter does not start with ---")
        continue

    parts = text.split("---", 2)
    if len(parts) < 3:
        errors.append(f"{skill_md}: YAML frontmatter is not closed")
        continue

    frontmatter = parts[1]
    body = parts[2]

    name = re.search(r"(?m)^name:\s*(.+?)\s*$", frontmatter)
    description = re.search(r"(?m)^description:\s*(.+?)\s*$", frontmatter)

    if not name:
        errors.append(f"{skill_md}: missing name")
    if not description:
        errors.append(f"{skill_md}: missing description")
    elif len(description.group(1).strip()) < 20:
        errors.append(f"{skill_md}: description is too short")

    for heading in ["# ", "## Purpose"]:
        if heading not in body:
            errors.append(f"{skill_md}: missing heading pattern {heading!r}")

    # Every workflow must preserve fixed environment policy semantics.
    for term in ["Apple M5 Max", "Python: 3.14.6", "`uv`", "docker compose"]:
        if term not in text:
            errors.append(f"{skill_md}: fixed environment constraint missing {term!r}")

# Specific cross-policy checks
specific = {
    "01-technical-research/SKILL.md": ["source-policy.md", "google-search-quality-policy.md", "research.md"],
    "03-experiment-design/SKILL.md": ["experiment-plan-template.md", "独立変数", "従属変数", "交絡要因"],
    "04-environment-build/SKILL.md": ["arm64", "multi-arch", "MPS", "MLX"],
    "06-result-analysis/SKILL.md": ["scripts/", "images/", "中央値", "analysis.md"],
    "08-article-drafting/SKILL.md": ["evidence-gate.md", "TL;DR", "失敗したこと・TIPS", "article.md"],
    "10-quality-review/SKILL.md": ["Original Value Gate", "18点", "google-search-quality-policy.md", "PROJECT_STATE.md", "quality-review.json"],
}
for rel, terms in specific.items():
    p = SKILLS / rel
    if not p.is_file():
        errors.append(f"missing skill: {rel}")
        continue
    t = p.read_text(encoding="utf-8")
    for term in terms:
        if term not in t:
            errors.append(f"{rel}: missing policy term {term!r}")

# Resource content checks
resource_terms = {
    "environment-policy.md": ["Apple Silicon / arm64", "Python          : 3.14.6", "Docker Compose", "linux/arm64", "MPS / Metal / MLX", "torch.backends.mps.is_available"],
    "evidence-gate.md": ["Research Question", "Missing Evidence", "article-drafting", "Anti-fabrication"],
    "project-layout.md": ["PROJECT_STATE.md", "research.md", "experiment-log.md", "article.md", "Resume rule"],
    "review-rubric.md": ["Original Value Gate", "Experience", "Clarity", "Total: /18"],
    "article-template.md": ["## TL;DR", "## 対象読者", "## Research Question", "## 失敗したこと・TIPS"],
}
for name, terms in resource_terms.items():
    t = (RES / name).read_text(encoding="utf-8") if (RES / name).is_file() else ""
    for term in terms:
        if term not in t:
            errors.append(f"resources/{name}: missing required term {term!r}")


# Content MLOps implementation checks
required_paths = [
    ROOT / "docs" / "implementation" / "01-github-versioning.md",
    ROOT / "docs" / "implementation" / "02-mlflow-offline-evaluation.md",
    ROOT / "docs" / "implementation" / "03-fixed-evaluation-dataset.md",
    ROOT / "docs" / "implementation" / "04-human-review.md",
    ROOT / "infra" / "mlflow" / "compose.yaml",
    ROOT / "evals" / "datasets" / "golden-set-v1.jsonl",
    ROOT / "evals" / "run_offline_eval.py",
    ROOT / "tools" / "version_snapshot.py",
]
for p in required_paths:
    if not p.is_file():
        errors.append(f"missing Content MLOps file: {p.relative_to(ROOT)}")

if count == 0:
    errors.append("No SKILL.md files found")

if errors:
    print("FAILED")
    for e in errors:
        print(f"- {e}")
    sys.exit(1)

print(f"OK: {count} skills, package policies, and Content MLOps files validated")
