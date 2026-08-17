# Project Layout Policy

## Purpose

長期の技術検証を途中から再開でき、Agent / Skill / Memoryの会話状態に依存せず監査可能にする。
実験結果や進捗のSource of TruthはMemoryではなくProject Filesとする。

## Standard layout

```text
project/
├── PROJECT_STATE.md
├── README.md
├── research.md
├── hypothesis.md
├── experiment-plan.md
├── experiment-log.md
├── analysis.md
├── discussion.md
├── article.md
├── pyproject.toml          # Python利用時
├── uv.lock                 # Python利用時
├── compose.yaml            # 常駐サービス利用時
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

使用しないファイルを無理に作らない。

## Canonical artifacts

- `PROJECT_STATE.md`: 現在Phase、完了済み工程、次に行うこと
- `research.md`: 一次情報調査、Source Record、未確認事項
- `hypothesis.md`: Research Question、仮説、反証条件
- `experiment-plan.md`: 実験計画
- `experiment-log.md`: 実行コマンド、変更、失敗、再試行の時系列
- `analysis.md`: 実測値から直接言える結果
- `discussion.md`: 解釈、制約、追加検証
- `article.md`: Qiita公開候補
- `data/raw/`, `logs/`: 加工前証拠
- `results/`: 集計結果
- `scripts/`: 再生成可能な分析・グラフコード
- `images/`: 実験Evidenceとなるグラフ・スクリーンショット

## Resume rule

Agent開始時に既存Projectがある場合:

1. `PROJECT_STATE.md` を読む。
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
└── docs/implementation/   # STEP 1〜4手順
```

評価run / traces / artifactsの正本はMLflow、評価ロジックとDataset原本はGitHubとする。
