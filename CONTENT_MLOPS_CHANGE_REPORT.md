# Content MLOps Change Report — v0.3.0

## Purpose

既存の実証型技術ブログAgentへ、GitHub + MLflowを使った継続評価・改善コンセプトを追加した。

## Added resources

- `resources/content-mlops-concept.md`
- `resources/versioning-policy.md`
- `resources/evaluation-policy.md`
- `resources/production-metrics-policy.md`

## Modified core files

- `agent/AGENT_INSTRUCTIONS.md`
  - GitHub = Source of Truth
  - MLflow = evaluation / trace / review
  - Offline QualityとProduction Performanceの分離
  - Optional post-quality lifecycle 13〜17
  - version/evaluation identity追加
- `resources/project-state-template.md`
  - Article ID / Git / MLflow / Dataset / Publication identity追加
- `resources/project-layout.md`
  - evaluation / MLflow / results artifactsを追加
- `skills/10-quality-review/SKILL.md`
  - `results/quality-review.json` を追加
- `MANIFEST.json`, `pyproject.toml`
  - version `0.3.0`
- `tools/validate_skills.py`
  - Content MLOps必須ファイル検査を追加

## Added implementation files

- `docs/implementation/01-github-versioning.md`
- `docs/implementation/02-mlflow-offline-evaluation.md`
- `docs/implementation/03-fixed-evaluation-dataset.md`
- `docs/implementation/04-human-review.md`
- `infra/mlflow/compose.yaml`
- `tools/version_snapshot.py`
- `evals/run_offline_eval.py`
- `evals/scorers/article_scorers.py`
- `evals/datasets/golden-set-v1.jsonl`
- `evals/datasets/register_dataset.py`

## Validation

`tools/validate_skills.py` result:

```text
OK: 11 skills, package policies, and Content MLOps files validated
```

Python scripts were syntax-checked with `py_compile`.

The current execution container does not provide Docker, so `docker compose config` and actual MLflow container startup were not executed here. These are explicit verification steps in STEP 2 and should be run on the target Apple M5 Max environment.

## Compatibility with original specification

The original Research → Hypothesis → Experiment → Analysis → Discussion → Evidence Gate → Article → Quality Review flow is unchanged.

Content MLOps is added after and around the existing flow; it does not weaken:

- M5 Max / 128GB
- Python 3.14.6
- uv
- Docker Compose
- Evidence Gate
- E-E-A-T / 18 point review
- failure / trial-and-error preservation
- Qiita Markdown requirements
- project resume / source-of-truth rules
