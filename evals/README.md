# Evaluations

GitHubに評価ロジックとGolden Set原本を保存し、MLflowに実行結果を保存する。

```text
evals/
├── datasets/
│   ├── golden-set-v1.jsonl
│   └── register_dataset.py
├── scorers/
│   └── article_scorers.py
├── human_review/
└── run_offline_eval.py
```

MVPではSTEP 1.5でAgent Repository外部のArticle Projectへ生成した実 `article.md` を `run_offline_eval.py` へ渡す半自動方式とする。
