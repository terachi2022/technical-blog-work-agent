---
name: environment-build
description: Apple M5 Max/macOS/Python 3.14.6/uvを固定条件として技術検証環境を構築し、サービスが必要ならDocker Composeで再現可能にするときに使う。
---

# Environment Build

## Purpose

実験計画に必要な環境を再現可能な形で構築し、バージョンと設定を記録する。

## Inputs

- experiment plan
- 必要パッケージ
- 必要サービス


## 実行環境の固定条件

このSkillでローカル検証を行う場合、以下を既定条件として扱う。

- ハードウェア: Apple M5 Max / 128GB RAM
- OS: macOS
- Python: 3.14.6
- Pythonパッケージ管理: `uv`
- Python bootstrap: `uv python install 3.14.6` → `uv python pin 3.14.6` → `uv sync` → `source .venv/bin/activate`
- Python実行前: `python --version` が3.14.6であることを確認
- 仮想環境・依存関係: `uv` で管理する
- 常駐サービス、DB、Web UI、補助サーバーが必要な場合: `docker compose` で構成する
- Apple SiliconでGPUアクセラレーションが使える場合: MPS/Metalを優先する
- CUDA/NVIDIA GPUを前提にしない
- シェル例はmacOS標準のzshで実行可能な形を優先する

固定条件で実行不能な場合は、勝手にPython版・OS・ハードウェア条件を変更しない。
「非互換・未対応」という検証結果として記録し、原因、根拠、代替案を提示する。


## Workflow

1. `environment-policy.md` に従い、macOS、arm64、M5 Max、Python/uv、Docker/Compose等の実値を取得して記録する。
2. Pythonプロジェクトなら `uv python install 3.14.6` でPython本体をuv管理下へ導入する。
3. `uv python pin 3.14.6` でproject Pythonを固定する。
4. `uv sync` で `.venv` とlock状態を同期する。
5. `source .venv/bin/activate` で明示的にactivateし、`python --version` が3.14.6であることを確認する。
6. 依存関係は `uv add` / `uv sync` で管理する。
7. 常駐サービスが必要なら `compose.yaml` を作り、arm64またはmulti-archイメージを優先する。x86_64エミュレーションを使う場合は性能上の制約を記録する。
8. 起動後にhealth/statusを確認する。
9. 重要設定をファイルとして保存する。
10. 最小のsmoke testを実施する。
11. 実験開始前の状態を記録する。

## Do not

- `pip install` を標準手順にしない。
- pyenv/condaへ勝手に切り替えない。
- Pythonバージョンを黙って下げない。
- HomebrewでDB等を常駐サービス化しない。
- NVIDIA/CUDA専用コマンドをM5 Max向け手順として出さない。

## Failure

依存関係や製品がPython 3.14.6 / Apple Siliconに非対応なら、
無理に回避せず `failure-recovery-replan` へ渡す。

## Output

- 環境構築手順
- 生成・変更したファイル
- バージョン一覧
- 起動確認
- smoke test結果
- 問題点

## Completion checks

- 0から再構築できる。
- サービスはDocker Composeで定義されている。
- 実験開始前に正常性を確認した。

## Apple Silicon check

ML/GPU検証ではMPS / Metal / MLX等の実際の対応状況を確認する。CUDA前提チュートリアルを置換する場合は、公式手順→M5 Maxで使えない点→置換方法→差異・制約を記録する。

## Project state update

完了時に `PROJECT_STATE.md` の Environment を更新する。
