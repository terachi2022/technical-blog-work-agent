# uv / Python Bootstrap Correction Report — v0.3.1

## Problem corrected

v0.3.0 implementation guides used `uv run` without first documenting the required target environment bootstrap. This contradicted the fixed project rule that Python 3.14.6 and dependencies are managed with `uv`, and it hid the active interpreter from the operator.

## Corrected standard sequence

```bash
uv python install 3.14.6
uv python pin 3.14.6
uv sync
source .venv/bin/activate
python --version
```

Expected:

```text
Python 3.14.6
```

## Files changed

- `docs/implementation/00-environment-bootstrap.md` — added
- `docs/implementation/01-github-versioning.md` — bootstrap moved before Git/version Python tools
- `docs/implementation/02-mlflow-offline-evaluation.md` — explicit activate + Python 3.14.6 check
- `docs/implementation/03-fixed-evaluation-dataset.md` — explicit activate + Python 3.14.6 check
- `docs/implementation/04-human-review.md` — explicit activate before SDK/helper usage
- `resources/environment-policy.md` — Python itself must be installed by uv
- `agent/AGENT_INSTRUCTIONS.md` — fixed environment summary corrected
- `skills/*/SKILL.md` — Python execution rule aligned
- `skills/04-environment-build/SKILL.md` — full bootstrap workflow added
- `README.md` — initial bootstrap added
- `tools/version_snapshot.py` — Python executable/version and uv version captured
- `tools/validate_skills.py` — bootstrap omissions now fail validation
- `MANIFEST.json` / `pyproject.toml` / `CHANGELOG.md` — version bumped to 0.3.1

## Validation

Structural validation result:

```text
OK: 11 skills, package policies, and Content MLOps files validated
```

The audit container is not the target M5 Max/macOS environment, so target-runtime validation must be performed after the bootstrap above on the user's Mac.
