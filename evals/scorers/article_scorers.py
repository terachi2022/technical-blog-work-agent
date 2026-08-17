from __future__ import annotations

import re

from mlflow.genai import scorer

REQUIRED_SECTIONS = [
    "## TL;DR",
    "## Research Question",
    "## 検証環境",
    "## 結果",
    "## 考察",
    "## 参考資料",
]


@scorer
def required_section_coverage(outputs: str) -> float:
    """Return the fraction of required article sections that are present."""
    found = sum(section in outputs for section in REQUIRED_SECTIONS)
    return found / len(REQUIRED_SECTIONS)


@scorer
def environment_constraint_coverage(outputs: str) -> float:
    """Check whether the fixed local validation environment is documented."""
    required = ["M5 Max", "Python 3.14.6", "uv"]
    found = sum(term in outputs for term in required)
    return found / len(required)


@scorer
def has_reference_links(outputs: str) -> bool:
    """Require at least one Markdown or plain HTTPS reference link."""
    markdown_link = re.search(r"\[[^\]]+\]\(https://[^)]+\)", outputs)
    plain_link = re.search(r"https://[^\s)>]+", outputs)
    return bool(markdown_link or plain_link)


@scorer
def no_unresolved_publication_placeholders(outputs: str) -> bool:
    """Detect common placeholders that should not remain in a publication candidate."""
    markers = [
        "TODO",
        "TBD",
        "<YOUR_",
        "<!--\n📸 Screenshot",
        "[スクリーンショットを挿入]",
    ]
    return not any(marker in outputs for marker in markers)


SCORERS = [
    required_section_coverage,
    environment_constraint_coverage,
    has_reference_links,
    no_unresolved_publication_placeholders,
]
