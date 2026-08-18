# Evaluations

GitHubに評価ロジックとGolden Set原本を保存し、MLflowに実行結果を保存する。

```text
evals/
├── datasets/
│   ├── golden-set-v1.jsonl
│   ├── human-calibration-v1.jsonl
│   └── register_dataset.py
├── scorers/
│   └── article_scorers.py
├── human_review/
└── run_offline_eval.py
```

MVPではSTEP 1.5でAgent Repository外部のArticle Projectへ生成した実 `article.md` を `run_offline_eval.py` へ渡す半自動方式とする。

`human-calibration-v1.jsonl`は人間評価済み記事のlabelを保存する。Calibration caseだけに合わせて改善せず、別記事をholdoutとして評価する。

Before/AfterのReader-visible contractとreview scoreは次で比較する。

```bash
uv run python -m evals.compare_article_versions \
  --before /path/to/article.md \
  --after /path/to/article-v2.md \
  --before-review /path/to/human-review.json \
  --after-review /path/to/quality-review-v2.json
```

Agent scoreとHuman scoreの誤差は次で計測する。

```bash
uv run python -m evals.calibrate_review_scores \
  --human-review /path/to/human-review.json \
  --agent-review /path/to/quality-review.json
```
