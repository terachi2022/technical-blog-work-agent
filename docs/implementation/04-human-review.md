# STEP 4 — Human Review

## Goal

Machine Scorer / LLM JudgeだけでAgent品質を決めず、人間評価との一致・不一致を確認できる状態にする。

## Important

MLflow Review QueuesはMLflow 3.14.0で追加されたexperimental機能である。
本手順では3.15.1をbaselineとするが、upgrade時には公式ドキュメントを再確認する。

## Prerequisite

STEP 2のOffline Evaluationを実行し、MLflow experimentにarticle traceが存在すること。

SDKや補助スクリプトを使う作業に備え、同じuv project environmentをactivateする。

```bash
cd technical-blog-work-agent
source .venv/bin/activate
python --version
python -c "import mlflow; print(mlflow.__version__)"
```

`Python 3.14.6` でない場合は続行せず `00-environment-bootstrap.md` に戻る。

## 1. Review Questions

最初は現在の9項目Rubricをそのまま人間評価へ使う。

数値評価:

```text
Experience          0 / 1 / 2
Expertise           0 / 1 / 2
Authoritativeness   0 / 1 / 2
Trustworthiness     0 / 1 / 2
Originality         0 / 1 / 2
Reproducibility     0 / 1 / 2
Usefulness          0 / 1 / 2
Evidence            0 / 1 / 2
Clarity             0 / 1 / 2
```

追加:

```text
Publishable         PASS / FAIL
Critical issue      Free text
```

## 2. Custom Review Queueを作成

ローカルMVPではMLflow serverにauthenticationを必須にしない。
非認証serverでは個人reviewer assignmentではなくCustom Queueを使用する。

MLflow UI:

```text
Experiment
  ↓
Review
  ↓
New question
  ↓
Create custom queue
```

Queue名例:

```text
technical-blog-golden-v1-human-review
```

再現可能なセットアップにはRepository内のスクリプトを使用できる。

```bash
export MLFLOW_TRACKING_URI=http://127.0.0.1:5000

uv run python evals/human_review/setup_review_queue.py \
  --experiment technical-blog-agent-offline-eval \
  --queue-name technical-blog-golden-v1-human-review
```

MLflow OSSでは`InputNumeric`のUIサポートに制約があるため、9品質項目は意味を変えずCategorical `0 / 1 / 2`として作成する。`title`と`overwrite`はDatabricks ReviewApp専用なので使用しない。

## 3. TraceをQueueへ追加

Queueへ追加する前に、対象Traceの`View full trace`を開き、`article.md`がOpenAI互換assistant messageとして全文保存され、Markdown表示されることを確認する。最低限、記事タイトル、Markdownの箇条書きまたはコードブロック、末尾`参考資料`が読めることを合格条件とする。escaped JSON、生のdict文字列、先頭だけのpreviewならSTEP 2のTrace生成を修正して再実行する。

MLflow UIのTracesから対象traceを選択し:

```text
Flag for review
```

またはSDKを使う場合は `mlflow.genai.review_queues` を利用する。
最初はUI操作を推奨する。

## 4. 長文記事は全文Review UIで評価

MLflow 3.15.1 OSSの標準Review本文欄はTraceの`request_preview` / `response_preview`を表示する。DB上のpreviewは最大1000文字であり、長文記事では末尾まで表示されない。`View full trace`でTrace自体は確認できるが、記事全文と11問を同時に評価する用途には適さない。

長文記事では、Repositoryの全文Review UIを使用する。

```bash
export ARTICLE_PROJECT_DIR=/absolute/path/to/article-project
export REVIEW_QUEUE_ID=rq-xxxxxxxx
export REVIEW_TRACE_ID=tr-xxxxxxxx
export REVIEWER_ID=reviewer-name

docker compose -f infra/mlflow/compose.yaml \
  --profile human-review up -d --build review-ui
```

ブラウザで次を開く。

```text
http://127.0.0.1:5051
```

合格条件:

```text
□ View full traceでarticle.mdが全文Markdown表示される
□ Traceに先頭見出しと末尾「参考資料」がある
□ article.mdの先頭から参考資料まで表示される
□ 記事画像が表示される
□ 9品質項目、Publishable、Critical issueを入力できる
□ 送信結果が対象TraceのHuman Feedbackとして残る
□ 送信成功後にQueue itemがcompleteになる
```

## 5. Review sampling

全記事を毎回人間レビューする必要はない。

初期段階ではGolden Set 10件を全件確認する。
安定後は例えば:

- release candidate全件
- regressionが発生したcase
- LLM Judgeとmachine scoreが大きく食い違うcase
- 新しい記事タイプ

を優先する。

## 6. Human vs Automatedを比較

確認したいのはHuman Score自体だけではない。

```text
Human Review
      ↕
Machine Scorer / LLM Judge
```

例えばLLM JudgeがOriginality=2、人間が0を付けるケースが続くなら、Judge prompt / scorer設計の改善対象である。

## 7. Agent変更の判断

人間評価が低かったからといって直接Agentを書き換えない。

```text
Human finding
  ↓
Root cause hypothesis
  ↓
Agent / Skill / Resource change branch
  ↓
Fixed Dataset再評価
  ↓
改善確認
  ↓
merge / release
```

## Completion check

```text
□ Review Queueが作成済み
□ TraceがOpenAI互換assistant messageで全文Markdown表示される
□ Traceの末尾「参考資料」まで確認済み
□ 9 quality questionsが定義済み
□ Publishable / Critical issueがある
□ Golden Set tracesをreviewできる
□ Human resultがtraceに残る
□ automated scoreとのズレを確認できる
```

## Official reference

- Review Queues: https://mlflow.org/docs/latest/genai/assessments/review-queues/
- Feedback: https://mlflow.org/docs/latest/genai/assessments/feedback/
