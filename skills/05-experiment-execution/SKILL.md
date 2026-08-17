---
name: experiment-execution
description: 事前に定義した技術実験計画を変更履歴と証拠を残しながら実行し、成功・失敗を生データとして記録するときに使う。
---

# Experiment Execution

## Purpose

実験計画どおりに検証し、後から分析可能な証拠を残す。

## Inputs

- experiment plan
- 構築済み環境
- hypothesis IDs


## 実行環境の固定条件

このSkillでローカル検証を行う場合、以下を既定条件として扱う。

- ハードウェア: Apple M5 Max / 128GB RAM
- OS: macOS
- Python: 3.14.6
- Pythonパッケージ管理: `uv`
- Python実行: 原則 `uv run ...`
- 仮想環境・依存関係: `uv` で管理する
- 常駐サービス、DB、Web UI、補助サーバーが必要な場合: `docker compose` で構成する
- Apple SiliconでGPUアクセラレーションが使える場合: MPS/Metalを優先する
- CUDA/NVIDIA GPUを前提にしない
- シェル例はmacOS標準のzshで実行可能な形を優先する

固定条件で実行不能な場合は、勝手にPython版・OS・ハードウェア条件を変更しない。
「非互換・未対応」という検証結果として記録し、原因、根拠、代替案を提示する。


## Workflow

1. 実験IDと開始時刻を記録する。
2. 実行前の環境状態を記録する。
3. 計画されたコマンドを順番に実行する。
4. コマンド、stdout、stderr、exit codeを保存する。
5. メトリクスや生成ファイルを保存する。
6. 必要箇所で `visual-evidence` 用の画面候補を記録する。
7. 計画から変更した場合は、変更内容と理由をその場で記録する。
8. エラーを成功扱いにしない。
9. 予期せぬ失敗は `failure-recovery-replan` へ渡す。
10. 終了状態を記録し、`experiment-log.md`、`data/raw/`、`logs/` 等へ証拠を残す。

## Evidence rule

結果を要約する前に生データを残す。
「たぶん」「おそらく」を実測値へ置き換えない。

## Output

各実験について:

- Experiment ID
- Hypothesis ID
- Command/action
- Raw output
- Metrics
- Artifacts
- Deviation from plan
- Preliminary status: PASS / FAIL / INCONCLUSIVE

## Completion checks

- どのコマンドから結果が得られたか追跡できる。
- 失敗ログを消していない。
- 計画変更の理由が残っている。

## Project state update

各実験の状態とEvidence IDを `PROJECT_STATE.md` に記録する。失敗時は失敗記録を残して `failure-recovery-replan` へ渡す。
