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
    "article-quality-contract.md",
    "review-rubric.md",
    "content-mlops-concept.md",
    "versioning-policy.md",
    "evaluation-policy.md",
    "human-review-policy.md",
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
    "Technical Article Offline Quality score",
    "Reader-visible Evidence Gate",
    "article-quality-contract.md",
    "Content MLOps",
    "GitHub",
    "MLflow",
    "Offline Quality",
    "Production Performance",
    "human-review-policy.md",
    "OpenAI互換assistant message",
    "全文Review UI",
    "技術選定理由",
    "エラー全文または主要行",
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
    "06-result-analysis/SKILL.md": ["scripts/", "images/", "中央値", "analysis.md", "仮説と結果の対応"],
    "08-article-drafting/SKILL.md": ["evidence-gate.md", "article-quality-contract.md", "TL;DR", "技術選定理由", "この構成を選んだ理由", "エラー全文または主要行", "失敗したこと・TIPS", "article.md", "article-evidence-map.json", "article-contract.json", "evals.check_article_contract"],
    "10-quality-review/SKILL.md": ["Original Value Gate", "18点", "QUALITY_READY", "技術選定理由", "修正内容", "article_only_then_evidence_verification", "google-search-quality-policy.md", "PROJECT_STATE.md", "quality-review.json", "human-review-policy.md", "OpenAI互換assistant message", "View full trace", "BLOCKED: REVIEW_SURFACE_INCOMPLETE"],
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

for rel, forbidden_terms in {
    "08-article-drafting/SKILL.md": ["最低1つの不採用案", "候補・採否・選定理由・不採用理由"],
    "10-quality-review/SKILL.md": ["ExperienceとUsefulnessを2点にしない", "Originalityも2点にしない", "ExpertiseとClarityを2点にしない"],
}.items():
    text = (SKILLS / rel).read_text(encoding="utf-8")
    for term in forbidden_terms:
        if term in text:
            errors.append(f"{rel}: obsolete policy term remains {term!r}")

rubric_text = (RES / "review-rubric.md").read_text(encoding="utf-8")
for term in [
    "採用構成または採用理由が記事にない場合だけ、Expertiseは最大1点",
    "固定的な点数上限へ変換しない",
]:
    if term not in rubric_text:
        errors.append(f"resources/review-rubric.md: missing score-boundary term {term!r}")

# Resource content checks
resource_terms = {
    "environment-policy.md": ["Apple Silicon / arm64", "Python          : 3.14.6", "Docker Compose", "linux/arm64", "MPS / Metal / MLX", "torch.backends.mps.is_available", "uv python install 3.14.6", "uv python pin 3.14.6", "source .venv/bin/activate"],
    "evidence-gate.md": ["Research Question", "Missing Evidence", "article-drafting", "Anti-fabrication"],
    "project-layout.md": ["PROJECT_STATE.md", "research.md", "experiment-log.md", "article.md", "article-contract.json", "Resume rule"],
    "review-rubric.md": ["Original Value Gate", "Experience", "Clarity", "採用理由", "エラーメッセージGate", "Total: /18"],
    "article-quality-contract.md": ["Reader-visible gate", "article-evidence-map.json", "article-contract.json", "evals.check_article_contract", "技術選定理由", "エラー全文または主要行", "Anti-gaming rule"],
    "human-review-policy.md": ["mlflow.message.format=openai", "mlflow.chat.messages", "OpenAI互換", "View full trace", "参考資料", "Full Article Review UI", "9 + 2", "Agentが人間の代わりに値を送信しない"],
    "article-template.md": ["## TL;DR", "## 対象読者", "## Research Question", "## 仕組みとデータフロー", "## 技術選定理由", "この構成を選んだ理由", "エラー全文または主要行", "## 仮説と結果の対応", "## 再現用成果物", "## 失敗したこと・TIPS"],
}
for name, terms in resource_terms.items():
    t = (RES / name).read_text(encoding="utf-8") if (RES / name).is_file() else ""
    for term in terms:
        if term not in t:
            errors.append(f"resources/{name}: missing required term {term!r}")


# Content MLOps implementation checks
required_paths = [
    ROOT / "docs" / "implementation" / "00-environment-bootstrap.md",
    ROOT / "docs" / "implementation" / "01-github-versioning.md",
    ROOT / "docs" / "implementation" / "01.5-baseline-article-generation.md",
    ROOT / "docs" / "implementation" / "02-mlflow-offline-evaluation.md",
    ROOT / "docs" / "implementation" / "03-fixed-evaluation-dataset.md",
    ROOT / "docs" / "implementation" / "04-human-review.md",
    ROOT / "infra" / "mlflow" / "compose.yaml",
    ROOT / "evals" / "datasets" / "golden-set-v1.jsonl",
    ROOT / "evals" / "datasets" / "article-contract-regressions-v1.jsonl",
    ROOT / "evals" / "datasets" / "human-calibration-v1.jsonl",
    ROOT / "evals" / "datasets" / "human-calibration-v2.jsonl",
    ROOT / "evals" / "quality_review_contract.py",
    ROOT / "evals" / "compare_article_versions.py",
    ROOT / "evals" / "calibrate_review_scores.py",
    ROOT / "evals" / "check_article_contract.py",
    ROOT / "evals" / "run_offline_eval.py",
    ROOT / "evals" / "human_review" / "full_article_review.py",
    ROOT / "evals" / "human_review" / "export_review.py",
    ROOT / "tools" / "version_snapshot.py",
    ROOT / "tools" / "init_article_project.py",
    ROOT / "tools" / "verify_article_project.py",
]
for p in required_paths:
    if not p.is_file():
        errors.append(f"missing Content MLOps file: {p.relative_to(ROOT)}")

offline_eval = ROOT / "evals" / "run_offline_eval.py"
if offline_eval.is_file():
    offline_text = offline_eval.read_text(encoding="utf-8")
    for term in [
        'attributes={"mlflow.message.format": "openai"}',
        '"mlflow.chat.messages"',
        '"role": "assistant"',
        '"object": "chat.completion"',
    ]:
        if term not in offline_text:
            errors.append(f"evals/run_offline_eval.py: missing Trace Markdown contract {term!r}")

human_review_guide = ROOT / "docs" / "implementation" / "04-human-review.md"
if human_review_guide.is_file():
    guide_text = human_review_guide.read_text(encoding="utf-8")
    for term in ["View full trace", "全文Markdown表示", "参考資料", "全文Review UI"]:
        if term not in guide_text:
            errors.append(f"docs/implementation/04-human-review.md: missing display gate {term!r}")

# Mandatory uv/Python bootstrap checks
bootstrap = ROOT / "docs" / "implementation" / "00-environment-bootstrap.md"
if bootstrap.is_file():
    bt = bootstrap.read_text(encoding="utf-8")
    for term in [
        "uv python install 3.14.6",
        "uv python pin 3.14.6",
        "uv sync",
        "source .venv/bin/activate",
        "python --version",
    ]:
        if term not in bt:
            errors.append(f"00-environment-bootstrap.md: missing required bootstrap term {term!r}")

for guide in [
    ROOT / "docs" / "implementation" / "01-github-versioning.md",
    ROOT / "docs" / "implementation" / "01.5-baseline-article-generation.md",
    ROOT / "docs" / "implementation" / "02-mlflow-offline-evaluation.md",
    ROOT / "docs" / "implementation" / "03-fixed-evaluation-dataset.md",
    ROOT / "docs" / "implementation" / "04-human-review.md",
]:
    if guide.is_file():
        gt = guide.read_text(encoding="utf-8")
        if "source .venv/bin/activate" not in gt:
            errors.append(f"{guide.relative_to(ROOT)}: missing explicit virtual environment activation")

step1 = ROOT / "docs" / "implementation" / "01-github-versioning.md"
if step1.is_file():
    st = step1.read_text(encoding="utf-8")
    for term in ["uv python install 3.14.6", "uv python pin 3.14.6", "uv sync"]:
        if term not in st:
            errors.append(f"docs/implementation/01-github-versioning.md: missing {term!r}")

# Baseline article generation / project-boundary checks
step15 = ROOT / "docs" / "implementation" / "01.5-baseline-article-generation.md"
if step15.is_file():
    st = step15.read_text(encoding="utf-8")
    for term in ["technical-blog-projects", "init_article_project.py", "--resume-existing", "AGENT_TASK.md", "Evidence Gate", "article-drafting", "article.md", "article-evidence-map.json", "article-contract.json", "evals.check_article_contract", "version-snapshot.json", "verify_article_project.py", "手作業で転記しない"]:
        if term not in st:
            errors.append(f"01.5-baseline-article-generation.md: missing {term!r}")

start_prompt = ROOT / "agent" / "START_PROMPT.md"
if start_prompt.is_file():
    spt = start_prompt.read_text(encoding="utf-8")
    for term in ["{{ARTICLE_ID}}", "{{PROJECT_DIR}}", "{{AGENT_REPOSITORY}}", "{{TOPIC}}", "{{AUDIENCE}}", "Evidence Gate", "article-drafting", "article.md", "技術選定理由", "エラー全文または主要行", "quality-review.json", "人間に再入力・転記させず"]:
        if term not in spt:
            errors.append(f"agent/START_PROMPT.md: missing operational field {term!r}")
else:
    errors.append("missing agent/START_PROMPT.md")

layout = RES / "project-layout.md"
if layout.is_file():
    lt = layout.read_text(encoding="utf-8")
    for term in ["Agent Repositoryと記事Projectは分離", "technical-blog-projects", "init_article_project.py", "AGENT_TASK.md", "自動記録", "空ファイル"]:
        if term not in lt:
            errors.append(f"resources/project-layout.md: missing project-boundary term {term!r}")

step2 = ROOT / "docs" / "implementation" / "02-mlflow-offline-evaluation.md"
if step2.is_file():
    s2 = step2.read_text(encoding="utf-8")
    if "01.5-baseline-article-generation.md" not in s2:
        errors.append("02-mlflow-offline-evaluation.md: must point to STEP 1.5")
    if "work/20260818" in s2 or "$(pwd)/work/" in s2:
        errors.append("02-mlflow-offline-evaluation.md: article project must not live under Agent repository work/")

article_scorers = ROOT / "evals" / "scorers" / "article_scorers.py"
if article_scorers.is_file():
    scorer_text = article_scorers.read_text(encoding="utf-8")
    for term in [
        "technology_selection_metrics",
        "has_technology_selection_rationale",
        "actionable_troubleshooting_coverage",
        "troubleshooting_error_gate_pass",
        "has_labeled_evidence",
    ]:
        if term not in scorer_text:
            errors.append(f"evals/scorers/article_scorers.py: missing {term!r}")

if count == 0:
    errors.append("No SKILL.md files found")

if errors:
    print("FAILED")
    for e in errors:
        print(f"- {e}")
    sys.exit(1)

print(f"OK: {count} skills, package policies, and Content MLOps files validated")
