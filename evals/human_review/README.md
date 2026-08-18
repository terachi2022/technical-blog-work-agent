# Human Review

詳細手順は `docs/implementation/04-human-review.md` を参照。

Human Reviewへ渡す前に `resources/human-review-policy.md` を適用する。Offline EvaluationのTraceは`article.md`全文をOpenAI互換assistant messageとして保持し、`View full trace`でMarkdown表示と末尾`参考資料`までを確認する。Traceの保存成功だけでは表示確認完了としない。

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

## 長文記事を全文レビューする

MLflow 3.15.1の標準Review画面はTraceの`response_preview`を表示する。OSSのpreviewは最大1000文字で、画面上でも長いメッセージが省略されるため、長文記事の全文評価には使用しない。

全文記事と11問を同じ画面で扱うCompose serviceを起動する。

```bash
export ARTICLE_PROJECT_DIR=/absolute/path/to/article-project
export REVIEW_QUEUE_ID=rq-xxxxxxxx
export REVIEW_TRACE_ID=tr-xxxxxxxx
export REVIEWER_ID=reviewer-name

docker compose -f infra/mlflow/compose.yaml \
  --profile human-review up -d --build review-ui
```

画面:

```text
http://127.0.0.1:5051
```

この画面は次を行う。

- `article.md`を省略せずMarkdownからHTMLへ変換
- Article Projectの`images/`を同じ画面へ表示
- Experience〜Clarity、Publishable、Critical issueを入力
- 送信時に11件のHuman Feedbackを対象MLflow Traceへ記録
- 記録成功後にReview Queue itemを`complete`へ変更

停止:

```bash
docker compose -f infra/mlflow/compose.yaml \
  --profile human-review stop review-ui
```
