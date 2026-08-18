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

MLflow UIのTracesから対象traceを選択し:

```text
Flag for review
```

またはSDKを使う場合は `mlflow.genai.review_queues` を利用する。
最初はUI操作を推奨する。

## 4. Review sampling

全記事を毎回人間レビューする必要はない。

初期段階ではGolden Set 10件を全件確認する。
安定後は例えば:

- release candidate全件
- regressionが発生したcase
- LLM Judgeとmachine scoreが大きく食い違うcase
- 新しい記事タイプ

を優先する。

## 5. Human vs Automatedを比較

確認したいのはHuman Score自体だけではない。

```text
Human Review
      ↕
Machine Scorer / LLM Judge
```

例えばLLM JudgeがOriginality=2、人間が0を付けるケースが続くなら、Judge prompt / scorer設計の改善対象である。

## 6. Agent変更の判断

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
□ 9 quality questionsが定義済み
□ Publishable / Critical issueがある
□ Golden Set tracesをreviewできる
□ Human resultがtraceに残る
□ automated scoreとのズレを確認できる
```

## Official reference

- Review Queues: https://mlflow.org/docs/latest/genai/assessments/review-queues/
- Feedback: https://mlflow.org/docs/latest/genai/assessments/feedback/
