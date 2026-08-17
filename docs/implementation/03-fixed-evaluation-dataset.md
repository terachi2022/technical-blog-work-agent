# STEP 3 — 固定Evaluation Dataset

## Goal

Agent v0.3とv0.4を**同じ問題**で評価できるようにする。

Evaluation DatasetはAgent品質の「定点観測用テストセット」として扱う。

## Source of Truth

Dataset原本はGitHubで管理する。

```text
evals/datasets/golden-set-v1.jsonl
```

MLflow Evaluation Datasetは実行・比較用コピーとする。

## 1. Golden Setを確認

初期版は10ケースを用意する。

対象カテゴリ:

1. インストール/チュートリアル
2. 障害解析
3. 性能ベンチマーク
4. CUDA手順のM5 Max変換
5. 技術比較
6. MLflow GUI/実験管理
7. Docker Compose構築
8. 失敗・再計画
9. 公式資料間の差分調査
10. Evidence不足時の停止判断

ケース数は最初から100件にしない。
まず10件程度で運用上の問題を発見する。

## 2. MLflow Datasetへ登録

MLflow serverが起動している状態で:

```bash
export MLFLOW_TRACKING_URI=http://127.0.0.1:5000

uv run python evals/datasets/register_dataset.py \
  --file evals/datasets/golden-set-v1.jsonl \
  --name technical-blog-golden-v1 \
  --version 1.0.0
```

MLflow Evaluation DatasetはSQL backendが必要なため、STEP 2のSQLite MLflow Serverを使用する。

## 3. Datasetを固定する

`golden-set-v1.jsonl` を変更したら、過去versionの内容を上書きして比較条件を壊さない。

大きな変更は新しいdatasetを作る。

```text
golden-set-v1.jsonl  -> 1.x系
golden-set-v2.jsonl  -> 新しい評価方針
```

## 4. ChatGPT Workで各caseを実行

現段階では半自動でよい。

1. caseの `inputs` をChatGPT Work Agentへ渡す
2. Agentの通常フローを実行する
3. `article.md` とProject artifactsを保存する
4. STEP 2のOffline Evaluatorへ渡す
5. case ID / dataset versionをMLflowへ記録する

## 5. 比較ルール

Agent version比較時には以下を揃える。

```text
Evaluation Dataset version
Rubric version
Scorer implementation
Judge model（使用する場合）
```

比較対象だけを変える。

```text
Agent version
Git commit
```

## 6. Datasetの育て方

失敗した実例をGolden Setへ追加する。

例:

- hallucinated URL
- Python 3.14非互換を勝手に3.12へ変更
- docker runへ逸脱
- Evidence不足なのに記事化
- 分析と考察の混同

ただしDatasetを増やした時点でversionを更新し、比較条件が変わったことを明示する。

## Completion check

```text
□ GitHubにGolden Set原本がある
□ MLflowにDatasetを登録できた
□ 10 caseのIDが固定
□ Dataset versionを記録
□ Agent version間で同じcaseを使える
□ 過去Datasetを破壊的に上書きしない
```

## Official references

- Evaluation Datasets: https://mlflow.org/docs/latest/genai/datasets/
- Dataset SDK: https://mlflow.org/docs/latest/genai/datasets/sdk-guide/
