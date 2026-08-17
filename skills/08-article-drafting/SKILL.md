---
name: article-drafting
description: 調査、仮説、実験、分析、考察の証拠を統合し、Qiita掲載用の再現可能な技術記事Markdownを作成するときに使う。
---

# Article Drafting

## Purpose

検証済みの成果を、初学者でも追試できるQiita記事へ変換する。

## Preconditions

- `evidence-gate.md` が `PASS` であること。FAILなら記事完成形を作らず不足Phaseへ戻す。

## Inputs

- research notes
- hypothesis
- experiment plan
- evidence
- result analysis
- discussion
- visual evidence
- article template
- Qiita style guide


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

1. `article-template.md` に従いTL;DR、対象読者、Research Question、結論を先に設計する。TL;DRには「何を調べたか / 何が分かったか / 何をすればよいか / 検証環境」を含める。
2. 背景と検証目的を書く。
3. 検証環境を表で明示する。
4. 公式情報を要約し参照URLを付ける。
5. 仮説を書く。
6. 検証計画を簡潔に説明する。
7. 環境構築を再現可能な手順で書く。
8. 実行したコード・コマンドを省略せず掲載する。
9. 結果を事実として示す。
10. 分析と考察を分ける。
11. 実際に発生した失敗と修正は `失敗したこと・TIPS` として、症状、原因、切り分け、解決、なぜ解決したかを可能な範囲で残す。
12. 制約と未確認事項を書く。
13. 参考資料をまとめる。
14. スクリーンショットが未取得なら明確なプレースホルダーを置く。
15. `quality-review` へ渡す。

## Writing rules

- 「簡単です」「当然」など初心者を置き去りにする表現を避ける。
- 先に目的、次にコマンド。
- 公式仕様を自分の実測のように書かない。
- 実測していない出力をコードブロックへ捏造しない。
- 長いログは必要行に絞り、全文保存先があれば示す。
- 「非常に強力です」「効率化できます」のような一般論だけで価値を作らず、具体的な環境・操作・結果を中心に書く。
- 公式資料の言い換えだけで記事を完成させない。

## Output

Qiita掲載用Markdown。

## Completion checks

- article-templateの主要セクションが満たされている。
- すべての重要主張に証拠がある。
- コードと説明が対応する。

## Canonical output

最終草稿は原則 `article.md` として保存する。

## Project state update

草稿作成後、`PROJECT_STATE.md` の Articleを更新し `quality-review` へ進む。
