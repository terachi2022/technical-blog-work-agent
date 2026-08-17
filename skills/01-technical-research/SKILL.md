---
name: technical-research
description: 技術ブログのテーマについて一次情報を中心に調査し、検証すべき論点と証拠付きの調査メモを作るときに使う。
---

# Technical Research

## Purpose

記事を書く前に、対象技術の現行仕様、前提、制約、既知の問題を調査する。

## Inputs

- 技術テーマ
- 想定読者
- 検証したい疑問
- ユーザーから渡されたURLや資料


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

1. テーマを「調査可能な技術問い」に分解する。
2. バージョン依存・最新仕様・互換性に関係する項目を特定する。
3. `source-policy.md` に従い、公式ドキュメント、公式リポジトリ、原著論文、標準仕様を優先して調査する。Google Search品質に関係するテーマでは `google-search-quality-policy.md` の公式ページも現行確認する。
4. 各情報についてURL、提供元、日付または対象バージョンを記録する。
5. 重要な主張ごとに「公式に確認済み / 二次情報のみ / 未確認」を付ける。
6. 資料間の矛盾や曖昧さを抽出する。
7. 実機検証で確認すべき論点へ変換する。
8. 記事本文はまだ完成させない。

## Output

`project-layout.md` に従い、原則 `research.md` として以下を保存・返す。

- 調査テーマ
- 用語
- 公式仕様
- バージョン情報
- 制約
- 未確認事項
- 矛盾
- 検証候補
- 参照資料

## Completion checks

- 重要主張に出典がある。
- 最新性が必要な項目を古い知識だけで断定していない。
- 調査結果と推測が分離されている。
- 次の `hypothesis-design` に渡せる検証論点がある。

## Project state update

完了時に `PROJECT_STATE.md` の Research を `COMPLETED` にし、次Phaseを更新する。
