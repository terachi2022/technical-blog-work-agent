---
name: experiment-design
description: 技術仮説を再現可能な実験計画へ変換し、手順、測定値、証拠、成功判定、ロールバックを設計するときに使う。
---

# Experiment Design

## Purpose

仮説ごとに再現可能で安全な検証計画を作る。

## Inputs

- 仮説一覧
- 調査メモ
- 固定環境
- 利用可能なツール


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

1. 仮説と測定対象を1対1で対応させ、独立変数・従属変数・固定条件を定義する。
2. 変更する変数と固定する変数を定義する。
3. 必要なソフトウェア、データ、サービスを列挙する。
4. 実行手順を具体的なコマンド単位まで落とす。
5. 取得する証拠を事前定義する。
6. 成功・失敗・不確定の判定基準を定義する。
7. 破壊的変更があればバックアップ・ロールバックを設計する。
8. 複数比較ではBefore/After、A/B、Control/Experimental等の比較条件をそろえ、試行回数と交絡要因を事前定義する。
9. 実験順序が結果へ影響する場合は順序を記録する。
10. 実験計画を実行前成果物として保存する。

## Required evidence

- バージョン
- 実行コマンド
- stdout/stderr
- 設定差分
- 測定値
- 必要なスクリーンショット
- 生成物のパス

## Output

`experiment-plan-template.md` の構造で原則 `experiment-plan.md` として保存・返す。

## Completion checks

- 仮説を本当に判定できる計画か。
- 追試可能か。
- 証拠取得が後付けになっていないか。
- 環境固定条件に違反していないか。

## Project state update

完了時に `PROJECT_STATE.md` の Experiment Design を `COMPLETED` にする。
