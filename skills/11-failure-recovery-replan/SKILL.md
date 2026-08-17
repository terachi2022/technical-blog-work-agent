---
name: failure-recovery-replan
description: 技術検証中のインストール失敗、非互換、実行エラー、期待外の結果を解析し、証拠を失わずに修正案と再検証計画を作るときに使う。
---

# Failure Recovery and Replan

## Purpose

失敗を隠したり場当たり的にコマンドを変えたりせず、
原因仮説→切り分け→修正→再検証の形で扱う。

## Inputs

- failed command
- stdout/stderr
- environment
- experiment plan
- changes already attempted


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

1. 失敗した操作をそのまま保存する。
2. エラーメッセージを要約する前に原文を保存する。
3. 最後に正常だった状態を確認する。
4. 変更履歴を時系列で整理する。
5. 原因候補を列挙し、証拠のある順に並べる。
6. 公式ドキュメントやIssueで既知問題を確認する。
7. 原因候補ごとに最小の切り分けテストを設計する。
8. 1回の再試行で複数要因を同時変更しない。
9. Python 3.14.6やM5 Max非対応が原因なら、固定条件を勝手に変更しない。
10. 修正可能なら再実験手順を作る。
11. 修正不能なら「環境制約による再現不能」という重要な結果として残す。
12. `experiment-design` へ戻す。

## Output

```markdown
# Failure Record

## Failed step
## Raw error
## Last known good state
## Changes before failure
## Root-cause hypotheses
## Evidence
## Isolation tests
## Selected fix
## Why this fix
## Re-test plan
## Article value
```

## Completion checks

- エラーを消して成功だけ残していない。
- 原因と修正を混同していない。
- 根拠なく依存パッケージを大量更新していない。
- 固定環境条件を黙って変更していない。

## Project state update

Failure Recordの要約と戻り先を `PROJECT_STATE.md` に記録する。既存の失敗履歴を上書きせず追記する。
