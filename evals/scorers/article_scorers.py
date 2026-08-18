from __future__ import annotations

import re

from mlflow.genai import scorer

REQUIRED_SECTIONS = [
    "## TL;DR",
    "## Research Question",
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


def markdown_section(text: str, heading: str) -> str:
    match = re.search(
        rf"(?ms)^##\s+{re.escape(heading)}\s*$\n(.*?)(?=^##\s+|\Z)", text
    )
    return match.group(1) if match else ""


def labeled_content(section: str, label: str) -> str:
    match = re.search(
        rf"(?ms)^\*\*{re.escape(label)}\*\*\s*$\n"
        rf"(.*?)(?=^\*\*|^###?\s+|\Z)",
        section,
    )
    return match.group(1).strip() if match else ""


def has_labeled_evidence(section: str, label: str) -> bool:
    content = labeled_content(section, label)
    fenced_block = re.search(r"(?ms)```[^\n]*\n.+?\n```", content)
    markdown_asset = re.search(r"!?\[[^\]]+\]\([^)]+\)", content)
    return bool(fenced_block or markdown_asset)


def table_rows(section: str) -> list[list[str]]:
    rows = []
    for line in section.splitlines():
        if not line.startswith("|") or re.fullmatch(r"[|:\-\s]+", line):
            continue
        rows.append([cell.strip() for cell in line.strip("|").split("|")])
    return rows


def technology_selection_metrics(text: str) -> tuple[float, bool]:
    section = markdown_section(text, "技術選定理由")
    label_checks = [
        bool(labeled_content(section, label))
        for label in ["解決したい課題", "採用した構成", "適用条件", "非適用条件"]
    ]
    rows = table_rows(section)
    adopted_row = any(
        len(row) >= 4 and row[1] == "採用" and row[2] not in {"", "—", "-"}
        for row in rows
    )
    rejected_row = any(
        len(row) >= 4 and row[1] == "不採用" and row[3] not in {"", "—", "-"}
        for row in rows
    )
    no_alternative = (
        "NOT_APPLICABLE" in labeled_content(section, "代替案の判定")
        and bool(labeled_content(section, "代替案がない理由"))
        and bool(labeled_content(section, "代替Evidence"))
    )
    checks = [
        *label_checks,
        "選定理由" in section,
        "不採用理由" in section,
        adopted_row,
        rejected_row or no_alternative,
    ]
    coverage = sum(checks) / len(checks)
    return coverage, all(checks)


def actionable_troubleshooting_coverage(text: str) -> float:
    section = markdown_section(text, "失敗したこと・TIPS")
    not_applicable = (
        "NOT_APPLICABLE" in labeled_content(section, "判定")
        and bool(labeled_content(section, "理由"))
        and bool(labeled_content(section, "代替Evidence"))
    )
    if not_applicable:
        return 1.0

    required_labels = [
        "発生条件",
        "失敗した操作",
        "エラー全文または主要行",
        "原因",
        "切り分け",
        "効果がなかった方法",
        "修正内容",
        "再実行",
        "再実行結果",
    ]
    label_checks = [bool(labeled_content(section, label)) for label in required_labels]
    evidence_labels = [
        "失敗した操作",
        "エラー全文または主要行",
        "修正内容",
        "再実行",
        "再実行結果",
    ]
    evidence_checks = [
        has_labeled_evidence(section, label) for label in evidence_labels
    ]
    checks = [*label_checks, *evidence_checks]
    return sum(checks) / len(checks)


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

    selection_coverage, has_selection_rationale = technology_selection_metrics(text)
    troubleshooting_coverage = actionable_troubleshooting_coverage(text)

    unresolved_markers = [
        "TODO",
        "TBD",
        "<YOUR_",
        "<!--\n📸 Screenshot",
        "[スクリーンショットを挿入]",
        "採用候補",
        "代替候補",
        "Evidenceに基づく理由",
        "<失敗名>",
        "# 実際に失敗したcommand",
        "# 実際のstderr",
        "# 実際の設定差分",
        "# 実際の再実行command",
        "# 実際のstdout",
    ]

    return {
        "required_section_coverage": sum(section in text for section in REQUIRED_SECTIONS)
        / len(REQUIRED_SECTIONS),
        "has_inline_source_links": bool(body_links),
        "has_hypothesis_result_matrix": (
            "## 仮説と結果の対応" in text and bool(hypothesis_rows)
        ),
        "procedure_observation_coverage": procedure_pairs,
        "reader_artifact_coverage": reader_artifacts,
        "failure_journey_coverage": troubleshooting_coverage,
        "actionable_troubleshooting_coverage": troubleshooting_coverage,
        "has_mechanism_section": "## 仕組みとデータフロー" in text,
        "technology_selection_coverage": selection_coverage,
        "has_technology_selection_rationale": has_selection_rationale,
        "no_unresolved_publication_placeholders": not any(
            marker in text for marker in unresolved_markers
        ),
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
def has_technology_selection_rationale(outputs: object) -> bool:
    """Require an explicit decision, alternative, and applicability rationale."""
    return bool(
        quality_contract_metrics(outputs)["has_technology_selection_rationale"]
    )


@scorer
def actionable_troubleshooting(outputs: object) -> float:
    """Require error, failed command, fix, and rerun evidence in a standard record."""
    return float(
        quality_contract_metrics(outputs)["actionable_troubleshooting_coverage"]
    )


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
    return bool(
        quality_contract_metrics(outputs)["no_unresolved_publication_placeholders"]
    )


SCORERS = [
    required_section_coverage,
    environment_constraint_coverage,
    has_reference_links,
    has_inline_source_links,
    has_hypothesis_result_matrix,
    procedure_observation_coverage,
    reader_artifact_coverage,
    failure_journey_coverage,
    has_technology_selection_rationale,
    actionable_troubleshooting,
    no_unresolved_publication_placeholders,
]
