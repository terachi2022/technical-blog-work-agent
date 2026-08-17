# Baseline Article Workflow Correction Report — v0.3.2

## Problem

以前の手順はSTEP 1 GitHubからSTEP 2 MLflowへ直接進み、MLflow入力である実 `article.md` をどの工程で生成するかが欠落していた。
またSTEP 2の例がAgent Repository内 `work/` を使い、記事作業でAgent Repositoryをdirtyにする可能性があった。

## Corrections

1. STEP 1.5 `Baseline Article Generation` を追加。
2. `article.md` はEvidence Gate PASS後のPhase 11で初めて生成。
3. Agent RepositoryとArticle Projectを分離。
4. 標準Article Project rootを `~/dev/technical-blog-projects/` とした。
5. `tools/init_article_project.py` を追加。
6. `START_PROMPT.md` を実運用版へ変更。
7. STEP 2から `work/` 前提を削除。
8. `version-snapshot.json` をArticle Projectへ保存。
9. Roadmap / README / Step 3 / Agent Instructions / validatorを統一。

## Correct flow

```text
STEP 0 -> STEP 1 -> STEP 1.5 -> Phase 1〜10 -> Evidence Gate PASS -> Phase 11 article.md -> Phase 12 Quality Review -> STEP 2 -> STEP 3 -> STEP 4
```
