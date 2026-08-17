# STEP 2 — MLflow Offline Evaluation

## Goal

Agentのversionごとに「記事品質が上がったか」をMLflowで比較できるようにする。

MVPではChatGPT WorkをPythonから自動実行しない。
ChatGPT Workで生成済みの `article.md` をMLflowへ渡し、code-based scorerと既存Quality Review結果を記録する。

## 1. MLflow ServerをDocker Composeで起動

```bash
cd infra/mlflow

docker buildx imagetools inspect ghcr.io/mlflow/mlflow:v3.15.1
```

出力に `linux/arm64` が存在することを確認する。
存在しない場合はx86_64 emulationへ勝手に進まず、環境差として記録する。

起動:

```bash
docker compose up -d
docker compose ps
```

UI:

```text
http://127.0.0.1:5000
```

このComposeはSQLite backendを使用する。
MLflow Evaluation DatasetはSQL backendを要求するため、FileStoreではなくSQLiteを使用する。

## 2. Client dependencyをuvで追加

Agent repository rootで:

```bash
uv add "mlflow==3.15.1"
uv sync
```

`pyproject.toml` と `uv.lock` の変更をGit管理する。

## 3. Tracking URI

```bash
export MLFLOW_TRACKING_URI=http://127.0.0.1:5000
```

## 4. articleを準備

例:

```text
project/article.md
project/results/quality-review.json
```

Quality Review Skillは `results/quality-review.json` も生成する。

## 5. Offline Evaluationを実行

```bash
uv run python evals/run_offline_eval.py \
  --project-dir /path/to/project \
  --article-id 20260818-mlflow-m5max-01
```

MVPのmachine scorers:

- required section coverage
- environment constraint coverage
- reference link presence
- unresolved placeholder check

加えて `quality-review.json` があれば9項目/18点をMLflow metricsとしてlogする。

## 6. MLflow UIで確認

Experiment:

```text
technical-blog-agent-offline-eval
```

確認するもの:

- Run name
- Agent version
- Git commit
- Git dirty
- Article ID
- Metrics
- Trace
- article artifact

## 7. Git-based version tracking

Evaluatorは可能な場合 `mlflow.genai.enable_git_model_versioning()` を有効化する。
このMLflow機能はexperimentalなので、Git metadataはrun tags / paramsにも明示的に残す。

## 8. 最初のbaseline

最初は「良い点数」を狙わない。
現在のAgent versionをbaselineとして記録する。

```text
baseline_agent_version = 0.3.0
baseline_dataset       = 後続STEP 3で固定
```

## Completion check

```text
□ MLflow UIがDocker Composeで起動
□ SQLite backendで起動
□ uvでMLflow client導入
□ article.mdを1件評価
□ traceがMLflowに見える
□ Git commitが追える
□ quality scoreがmetricとして残る
```

## Official references

- Self-hosting / Docker Compose: https://mlflow.org/docs/latest/self-hosting/
- GenAI Evaluation: https://mlflow.org/docs/latest/genai/eval-monitor/notebooks/quickstart-eval/
- Code-based scorers: https://mlflow.org/docs/latest/genai/eval-monitor/scorers/custom/tutorial/
- Git version tracking: https://mlflow.org/docs/latest/genai/version-tracking/track-application-versions-with-mlflow/
