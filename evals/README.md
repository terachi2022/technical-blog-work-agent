# Evaluations

GitHubに評価ロジックとGolden Set原本を保存し、MLflowに実行結果を保存する。

```text
evals/
├── datasets/
│   ├── golden-set-v1.jsonl
│   ├── article-contract-regressions-v1.jsonl
│   ├── human-calibration-v1.jsonl
│   ├── human-calibration-v2.jsonl
│   └── register_dataset.py
├── scorers/
│   └── article_scorers.py
├── human_review/
│   └── export_review.py
└── run_offline_eval.py
```

MVPではSTEP 1.5でAgent Repository外部のArticle Projectへ生成した実 `article.md` を `run_offline_eval.py` へ渡す半自動方式とする。

`human-calibration-v1.jsonl`は人間評価済み記事のlabelを保存する。Calibration caseだけに合わせて改善せず、別記事をholdoutとして評価する。

`article-contract-regressions-v1.jsonl`は、仕組み図だけの記事、キーワードだけのTIPS、完全な選定・失敗記録、妥当なNOT_APPLICABLEを固定し、Scorerのanti-gaming挙動を回帰検査する。

記事候補はHuman Reviewへ渡す前に、Reader-visible構造契約を直接検査できる。

```bash
uv run python -m evals.check_article_contract \
  --article /path/to/article.md \
  --strict \
  --output /path/to/results/article-contract.json
```

Human Review送信後は、画面の値を人手で転記せずMLflow Traceから取得する。

```bash
uv run python -m evals.human_review.export_review \
  --trace-id tr-xxxxxxxx \
  --queue-id rq-xxxxxxxx \
  --output /path/to/results/human-review-v2.json \
  --agent-review /path/to/results/quality-review-v2.json \
  --dataset-output evals/datasets/human-calibration-v2.jsonl \
  --case-id HC002 \
  --article-id article-v2 \
  --article-path /path/to/article-v2.md \
  --rubric-version 2.2 \
  --holdout
```

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
