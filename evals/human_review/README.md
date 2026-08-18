# Human Review

詳細手順は `docs/implementation/04-human-review.md` を参照。

初期MVPではMLflow UIからCustom Review Queueを作成する。
Review Queuesはexperimental featureなので、APIを固定実装しすぎずUIベースから始める。

## Queueを再現可能にセットアップする

Offline EvaluationでTraceを作成した後、次を実行する。

```bash
export MLFLOW_TRACKING_URI=http://127.0.0.1:5000

uv run python evals/human_review/setup_review_queue.py \
  --experiment technical-blog-agent-offline-eval \
  --queue-name technical-blog-golden-v1-human-review
```

このスクリプトは次を冪等に作成する。

- Experience〜Clarityの9問（0 / 1 / 2）
- Publishable（PASS / FAIL）
- Critical issue（自由記述）
- Custom Review Queue
- 対象Experiment内の最新TraceのQueue登録

MLflow OSSでは`InputNumeric`、Questionの`title`、`overwrite`の一部がDatabricks専用である。
そのため9品質項目は数値の意味を保ったCategorical `0 / 1 / 2`として定義する。
