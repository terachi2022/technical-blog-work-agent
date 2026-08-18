# Project Layout Policy

## Purpose

長期の技術検証を途中から再開でき、Agent / Skill / Memoryの会話状態に依存せず監査可能にする。
実験結果や進捗のSource of TruthはMemoryではなくProject Filesとする。

## Repository / Article Project boundary

**Agent Repositoryと記事Projectは分離する。**

標準配置:

```text
~/dev/
├── technical-blog-work-agent/       # GitHubでAgent / Skills / Resources / evalsを管理
└── technical-blog-projects/         # 記事・実験Project。Agent Repositoryの外側
    ├── 20260818-mlflow-m5max-001/
    └── ...
```

理由:

- 記事生成中の `research.md`、ログ、画像、`article.md` でAgent Repositoryをdirtyにしない。
- 正式baselineの `git_dirty=false` と記事作業中のファイル変更を分離する。
- Agent versionと記事Evidenceのライフサイクルを独立させる。

原則として `technical-blog-work-agent/work/` のようにAgent Repository内へ記事Projectを作らない。

## Standard article project layout

```text
technical-blog-projects/<article-id>/
├── PROJECT_STATE.md
├── README.md
├── research.md
├── hypothesis.md
├── experiment-plan.md
├── experiment-log.md
├── analysis.md
├── discussion.md
├── article.md
├── pyproject.toml          # 記事側でPythonコードを独立管理する必要がある場合のみ
├── uv.lock                 # 同上
├── compose.yaml            # 記事固有の常駐サービス利用時
├── src/                    # 必要時
├── scripts/                # 実験・分析・グラフ生成
├── data/
│   ├── raw/
│   └── processed/
├── results/
│   ├── quality-review.json
│   └── version-snapshot.json
├── logs/
└── images/
```

使用しないファイルを無理に作らない。`article.md` もPhase 11で実内容が生成されるまで空ファイルを作らない。

## Project initialization

Agent Repositoryのactivate済みPythonから標準initializerを使う。

```bash
cd ~/dev/technical-blog-work-agent
source .venv/bin/activate

python tools/init_article_project.py \
  --projects-root ~/dev/technical-blog-projects \
  --article-id 20260818-mlflow-m5max-001 \
  --topic "M5 Max環境でMLflowの公式チュートリアルを実行する" \
  --audience "MLflowを初めて使用するエンジニア"
```

initializerはProject Directory、`PROJECT_STATE.md`、README、データ・結果・ログ・画像用ディレクトリに加え、
`results/version-snapshot.json` と実値入り `AGENT_TASK.md` を作る。
Agent version / Git commit / branch / dirtyは `PROJECT_STATE.md` へ自動記録し、人間に転記させない。
`research.md` や `article.md` を空ファイルとして先に作らない。

## Canonical artifacts

- `PROJECT_STATE.md`: 現在Phase、完了済み工程、次に行うこと
- `research.md`: 一次情報調査、Source Record、未確認事項
- `hypothesis.md`: Research Question、仮説、反証条件
- `experiment-plan.md`: 実験計画
- `experiment-log.md`: 実行コマンド、変更、失敗、再試行の時系列
- `analysis.md`: 実測値から直接言える結果
- `discussion.md`: 解釈、制約、追加検証
- `article.md`: Phase 11で生成するQiita公開候補。空ファイルは禁止
- `data/raw/`, `logs/`: 加工前証拠
- `results/`: 集計・レビュー・Agent version snapshot
- `scripts/`: 再生成可能な分析・グラフコード
- `images/`: 実験Evidenceとなるグラフ・スクリーンショット

## Resume rule

Agent開始時に既存Projectがある場合:

1. 指定されたProject Directoryの `PROJECT_STATE.md` を読む。
2. Canonical artifactsの存在と内容を確認する。
3. `PROJECT_STATE.md` と実ファイルが矛盾する場合、実ファイルを確認し状態を修正する。
4. 完了済みPhaseを理由なく再実行しない。
5. 未完了Phase、またはEvidence Gateで戻されたPhaseから再開する。
6. 追加検証は既存成果を上書きせず履歴として残す。

## Memory boundary

Memoryへ保存する:
- 長期間変わらない作業嗜好
- 表現・記事作成方針

Project Filesへ保存する:
- Research Question
- 仮説
- 実験結果
- ベンチマーク
- 失敗ログ
- 現在Phase
- 追加検証状態
- 公開可否

## Content MLOps repository layout

Agent repository itself may contain:

```text
technical-blog-work-agent/
├── evals/
│   ├── datasets/          # Golden Set原本（GitHubがSource of Truth）
│   ├── scorers/           # Machine evaluation
│   ├── human_review/      # Human Review補助
│   └── run_offline_eval.py
├── infra/mlflow/          # Docker Composeによるlocal MLflow
├── tools/                 # validator / project initializer / version snapshot
└── docs/implementation/   # STEP 0〜4手順
```

評価run / traces / artifactsの正本はMLflow、評価ロジックとDataset原本はGitHub、記事のResearch/Experiment/Article成果物は外部Article ProjectをSource of Truthとする。
