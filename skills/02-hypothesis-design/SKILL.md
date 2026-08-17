---
name: hypothesis-design
description: 技術調査の結果から、反証可能な仮説、検証質問、成功・失敗条件を定義するときに使う。
---

# Hypothesis Design

## Purpose

「試してみる」だけの検証を避け、何を確かめる実験なのかを明確にする。

## Inputs

- technical-research の調査メモ
- ユーザーの目的
- 技術上の疑問


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

1. 調査メモから未確定の論点を抽出する。
2. 各論点をYes/Noまたは測定可能な問いへ変換する。
3. 仮説を「もしXなら、条件YではZになる」の形で記述する。
4. 仮説を支持する観測結果を定義する。
5. 仮説を棄却する観測結果を定義する。
6. 交絡要因と固定すべき条件を列挙する。
7. 優先順位を付ける。
8. 実験で確認不能なものは「調査のみ」と分離する。

## Output

`project-layout.md` に従い、Research Questionと各仮説を原則 `hypothesis.md` に保存する。各仮説は以下を含む。

```markdown
## H1: <仮説>

- Question:
- Hypothesis:
- Rationale:
- Supporting evidence:
- Falsification condition:
- Controlled conditions:
- Priority:
```

## Completion checks

- 反証可能である。
- 「良くなる」など測定不能な表現だけで終わっていない。
- 公式仕様を仮説として再検証するだけになっていない。
- `experiment-design` で手順化可能である。

## Project state update

完了時に `PROJECT_STATE.md` の Research Question / Hypothesis を更新し、仮説IDと状態を記録する。
