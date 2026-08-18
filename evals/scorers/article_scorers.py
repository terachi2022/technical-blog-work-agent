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


@scorer
def required_section_coverage(outputs: object) -> float:
    """Return the fraction of required article sections that are present."""
    text = article_text(outputs)
    found = sum(section in text for section in REQUIRED_SECTIONS)
    return found / len(REQUIRED_SECTIONS)


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
    no_unresolved_publication_placeholders,
]
