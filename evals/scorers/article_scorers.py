from __future__ import annotations

import re

from mlflow.genai import scorer

REQUIRED_SECTIONS = [
    "## TL;DR",
    "## Research Question",
    "## 仕組みとデータフロー",
    "## 検証環境",
    "## 結果",
    "## 仮説と結果の対応",
    "## 考察",
    "## 再現用成果物",
    "## 参考資料",
]


def article_text(outputs: object) -> str:
    """Extract Markdown from plain text or OpenAI message/response formats."""
    if isinstance(outputs, str):
        return outputs
    if hasattr(outputs, "model_dump"):
        outputs = outputs.model_dump(exclude_none=True)
    if isinstance(outputs, dict):
        choices = outputs.get("choices")
        if isinstance(choices, list) and choices:
            first = choices[0]
            if isinstance(first, dict) and isinstance(first.get("message"), dict):
                return article_text(first["message"])
        content = outputs.get("content")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = [
                part.get("text", "")
                for part in content
                if isinstance(part, dict) and part.get("type") == "text"
            ]
            if parts:
                return "\n".join(parts)
    raise TypeError("outputs must contain article Markdown text")


def article_body(text: str) -> str:
    """Return the article before the terminal reference list."""
    return re.split(r"(?m)^##\s+参考資料\s*$", text, maxsplit=1)[0]


def markdown_links(text: str) -> list[str]:
    return re.findall(r"\[[^\]]+\]\((https://[^)]+)\)", text)


def quality_contract_metrics(outputs: object) -> dict[str, float | bool]:
    """Compute deterministic structure checks without claiming semantic quality."""
    text = article_text(outputs)
    body = article_body(text)
    hypothesis_rows = re.findall(r"(?m)^\|\s*H\d+\s*\|", text)
    execution_labels = len(re.findall(r"(?m)^\*\*(?:実行|実行コマンド)\*\*", text))
    observation_labels = len(re.findall(r"(?m)^\*\*(?:観測結果|実測結果)\*\*", text))
    procedure_pairs = 0.0
    if execution_labels:
        procedure_pairs = min(execution_labels, observation_labels) / execution_labels

    body_links = markdown_links(body)
    github_repo = bool(
        re.search(r"https://github\.com/[^/\s)]+/[^/\s)#]+(?:[)#\s]|$)", text)
    )
    notebook = bool(
        re.search(r"https://github\.com/[^\s)]+\.ipynb(?:[)#\s]|$)", text)
    )
    reader_artifacts = (int(github_repo) + int(notebook)) / 2

    failure_section = ""
    failure_match = re.search(
        r"(?ms)^##\s+失敗したこと・TIPS\s*$\n(.*?)(?=^##\s+|\Z)", text
    )
    if failure_match:
        failure_section = failure_match.group(1)
    failure_terms = ["操作", "観測", "原因", "切り分け", "修正", "再実行"]
    failure_journey = sum(term in failure_section for term in failure_terms) / len(
        failure_terms
    )

    return {
        "required_section_coverage": sum(section in text for section in REQUIRED_SECTIONS)
        / len(REQUIRED_SECTIONS),
        "has_inline_source_links": bool(body_links),
        "has_hypothesis_result_matrix": (
            "## 仮説と結果の対応" in text and bool(hypothesis_rows)
        ),
        "procedure_observation_coverage": procedure_pairs,
        "reader_artifact_coverage": reader_artifacts,
        "failure_journey_coverage": failure_journey,
        "has_mechanism_section": "## 仕組みとデータフロー" in text,
    }


@scorer
def required_section_coverage(outputs: object) -> float:
    """Return the fraction of required article sections that are present."""
    text = article_text(outputs)
    found = sum(section in text for section in REQUIRED_SECTIONS)
    return found / len(REQUIRED_SECTIONS)


@scorer
def has_inline_source_links(outputs: object) -> bool:
    """Require at least one source link before the terminal reference section."""
    return bool(quality_contract_metrics(outputs)["has_inline_source_links"])


@scorer
def has_hypothesis_result_matrix(outputs: object) -> bool:
    """Require reader-visible hypothesis/result traceability."""
    return bool(quality_contract_metrics(outputs)["has_hypothesis_result_matrix"])


@scorer
def procedure_observation_coverage(outputs: object) -> float:
    """Measure labeled execution units that also include observed results."""
    return float(quality_contract_metrics(outputs)["procedure_observation_coverage"])


@scorer
def reader_artifact_coverage(outputs: object) -> float:
    """Check public repository and direct notebook links for a runnable tutorial."""
    return float(quality_contract_metrics(outputs)["reader_artifact_coverage"])


@scorer
def failure_journey_coverage(outputs: object) -> float:
    """Check that a failure is described as a diagnostic journey, not a result only."""
    return float(quality_contract_metrics(outputs)["failure_journey_coverage"])


@scorer
def environment_constraint_coverage(outputs: object) -> float:
    """Check whether the fixed local validation environment is documented."""
    text = article_text(outputs)
    required = ["M5 Max", "Python 3.14.6", "uv"]
    found = sum(term in text for term in required)
    return found / len(required)


@scorer
def has_reference_links(outputs: object) -> bool:
    """Require at least one Markdown or plain HTTPS reference link."""
    text = article_text(outputs)
    markdown_link = re.search(r"\[[^\]]+\]\(https://[^)]+\)", text)
    plain_link = re.search(r"https://[^\s)>]+", text)
    return bool(markdown_link or plain_link)


@scorer
def no_unresolved_publication_placeholders(outputs: object) -> bool:
    """Detect common placeholders that should not remain in a publication candidate."""
    text = article_text(outputs)
    markers = [
        "TODO",
        "TBD",
        "<YOUR_",
        "<!--\n📸 Screenshot",
        "[スクリーンショットを挿入]",
    ]
    return not any(marker in text for marker in markers)


SCORERS = [
    required_section_coverage,
    environment_constraint_coverage,
    has_reference_links,
    has_inline_source_links,
    has_hypothesis_result_matrix,
    procedure_observation_coverage,
    reader_artifact_coverage,
    failure_journey_coverage,
    no_unresolved_publication_placeholders,
]
