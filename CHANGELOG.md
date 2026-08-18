# Changelog

## Unreleased

- STEP 1.5を将来工程の説明から実行可能なBaseline Article Generation手順へ再構成
- Project初期化時にVersion Snapshot保存、`PROJECT_STATE.md`更新、実値入り`AGENT_TASK.md`生成を自動化
- Evidence Gate PASS後に`article-drafting`を実行して`article.md`へ保存する処理を明文化
- `tools/verify_article_project.py`を追加し、記事とCanonical Evidenceの存在・内容を機械検証
- 人間によるAgent version / Git commit / branch / dirtyの転記を廃止
- `--resume-existing`で旧initializer作成済みProjectをEvidenceを保ったまま移行可能にした
- Python bytecode cacheと`.DS_Store`を除外し、initializer実行によるRepository dirty化を防止

## 0.3.2

- STEP 1.5 `Baseline Article Generation` を追加し、実際の `article.md` を生成する工程を明文化
- 記事ProjectをAgent Repositoryの外側 `~/dev/technical-blog-projects/` に分離する標準構成へ変更
- `agent/START_PROMPT.md` をArticle ID / Project Directory / Agent Version / Git Commit / Phase成果物まで指定する実運用版へ刷新
- `tools/init_article_project.py` を追加し、外部記事Projectの初期化と `PROJECT_STATE.md` 生成を再現可能にした
- STEP 2からAgent Repository内 `work/` 前提を削除し、外部Projectの `article.md` を直接評価する方式へ変更
- Agent / Project Layout / README / Roadmap / Evaluation Dataset手順を同じProject境界へ統一
- validatorにSTEP 1.5、START_PROMPT、外部Project分離、`work/`再混入の検査を追加

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
