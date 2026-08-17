# Changelog

## 0.3.1

- uv管理ルールを修正し、Python本体を `uv python install 3.14.6` で導入する必須手順を追加
- `uv python pin 3.14.6`、`uv sync`、`.venv` activate、`python --version`確認を標準化
- `docs/implementation/00-environment-bootstrap.md` を追加
- STEP 1〜4をactivate済みPython 3.14.6環境前提へ修正
- Agent / Environment Policy / Environment Build Skill / READMEの実行規則を統一
- validatorにPython bootstrap手順の欠落検知を追加

## 0.3.0

- Content MLOps conceptをAgentへ追加
- GitHubをSource of Truth、MLflowを評価台帳とする責務分離を追加
- Offline QualityとProduction Performanceを分離
- Versioning / Evaluation / Production Metrics policyを追加
- PROJECT_STATEへversion/evaluation/publication lifecycleを追加
- STEP 1〜4 implementation guidesを追加
- MLflow local Docker Compose MVPを追加
- version snapshot / offline evaluator / code scorers / Golden Setを追加
- quality-reviewのmachine-readable JSON outputを追加

## 0.2.0

- Evidence Gate、Google品質方針、Project State、18点Rubric等を追加
