# Changelog

## Unreleased

## 0.5.1

- 技術選定理由を今回の採用構成と採用理由中心へ改め、不採用案の記載を任意化
- 実障害のエラーメッセージEvidenceを独立したReader-visible Gateとして追加
- Expertise以外の機械的な2点上限を廃止し、品質点はHuman Reviewアンカーによる判断へ分離
- 採用案だけで通るcaseと、他項目が揃っていてもエラーEvidence欠落で落ちるcaseを固定回帰Datasetへ追加
- Human Review UIで未公開のversioned articleを原本上書きなしに選択できる`ARTICLE_PATH`を追加

## 0.5.0

- 技術選定理由を課題、採用案、不採用案、選定理由、適用・非適用条件へ対応させる記事契約を追加
- トラブルシューティングを実エラー、失敗操作、修正差分、再実行Evidenceまで追跡する固定形式へ変更
- 見出しや単語の存在だけでは通らない選定理由・失敗過程Scorerを追加
- Expertise、Experience、Originality、Usefulness、Clarityの2点条件とHuman Reviewアンカーを強化
- 選定意図欠落、キーワードだけの失敗記録、空のNOT_APPLICABLEを検出し、正当な代替案なし・GUI Evidenceを許可する回帰Datasetを追加

## 0.4.0

- Technical Article Offline Qualityを人間評価で校正できる品質契約へ更新

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
