# STEP 2 — MLflow Offline Evaluation

## Goal

Agentのversionごとに「記事品質が上がったか」をMLflowで比較できるようにする。

MVPではChatGPT WorkをPythonから自動実行しない。
STEP 1.5でChatGPT Work Agentが生成した実 `article.md` をMLflowへ渡し、code-based scorerと既存Quality Review結果を記録する。

**`article.md` がまだ存在しない場合はSTEP 2を続行せず、`01.5-baseline-article-generation.md` を先に実施する。**

## 0. Prerequisite — uv環境をactivate

STEP 1で作成したproject environmentを使用する。

```bash
cd technical-blog-work-agent
source .venv/bin/activate
python --version
```

期待値:

```text
Python 3.14.6
```

`.venv` が存在しない、またはPython 3.14.6でない場合はSTEP 2を続行せず、`00-environment-bootstrap.md` を実行する。

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

Agent repository rootで、activate済み状態を確認する。

```bash
python --version
```

MLflow dependencyをuvで追加する。

```bash
uv add "mlflow==3.15.1"
uv sync
```

`uv sync` 後もactivate状態を確認する。

```bash
source .venv/bin/activate
python -c "import mlflow; print(mlflow.__version__)"
```


`pyproject.toml` と `uv.lock` の変更をGit管理する。

## 3. Tracking URI

```bash
export MLFLOW_TRACKING_URI=http://127.0.0.1:5000
```

## 4. STEP 1.5で生成したArticle Projectを指定

STEP 2では新しく `article.md` を作成しない。
`01.5-baseline-article-generation.md` で作成済みの、Agent Repository外部Article Projectを使用する。

```bash
export ARTICLE_ID="20260818-mlflow-m5max-001"
export PROJECT_DIR="$HOME/dev/technical-blog-projects/$ARTICLE_ID"
```

構成例:

```text
~/dev/technical-blog-projects/20260818-mlflow-m5max-001/
├── PROJECT_STATE.md
├── research.md
├── hypothesis.md
├── experiment-plan.md
├── experiment-log.md
├── analysis.md
├── discussion.md
├── article.md                       # 必須。Phase 11で生成した実記事
├── results/
│   ├── version-snapshot.json
│   └── quality-review.json          # Phase 12実施済みの場合のみ
├── logs/
└── images/
```

### 4.1 `article.md` を確認

```bash
test -s "$PROJECT_DIR/article.md" \
  && echo "OK: article.md is not empty" \
  || { echo "ERROR: run STEP 1.5 first"; exit 1; }

sed -n '1,80p' "$PROJECT_DIR/article.md"
```

空ファイル、見出しだけのダミー、架空Evidenceで作った記事をBaseline評価へ使わない。

### 4.2 Agent version snapshotを確認

```bash
python -m json.tool "$PROJECT_DIR/results/version-snapshot.json"
```

`version-snapshot.json` がない場合はAgent Repository rootで:

```bash
python tools/version_snapshot.py \
  --article-id "$ARTICLE_ID" \
  --output "$PROJECT_DIR/results/version-snapshot.json"
```

### 4.3 `quality-review.json` は任意

Quality Review未実施ならファイルを作らない。空ファイルは禁止。

```bash
if [ -f "$PROJECT_DIR/results/quality-review.json" ]; then
  test -s "$PROJECT_DIR/results/quality-review.json" || {
    echo "ERROR: quality-review.json is empty"
    exit 1
  }
  python -m json.tool "$PROJECT_DIR/results/quality-review.json" >/dev/null
fi
```

STEP 2の最初の疎通確認では `article.md` だけでもよい。
Phase 12まで完了済みなら `quality-review.json` も一緒にMLflowへ記録する。

## 5. Offline Evaluationを実行

STEP 4の例をそのまま使う場合:

```bash
python evals/run_offline_eval.py \
  --project-dir "$PROJECT_DIR" \
  --article-id "$ARTICLE_ID"
```

別のProjectを評価する場合は、`--project-dir` に**そのProjectの `article.md` が存在するディレクトリ**を指定する。

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
baseline_agent_version = 0.3.2
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
□ quality-review.jsonがある場合はquality scoreがmetricとして残る
□ quality-review.jsonがない場合でもMachine Scorersが記録される
```

## Official references

- Self-hosting / Docker Compose: https://mlflow.org/docs/latest/self-hosting/
- GenAI Evaluation: https://mlflow.org/docs/latest/genai/eval-monitor/notebooks/quickstart-eval/
- Code-based scorers: https://mlflow.org/docs/latest/genai/eval-monitor/scorers/custom/tutorial/
- Git version tracking: https://mlflow.org/docs/latest/genai/version-tracking/track-application-versions-with-mlflow/
