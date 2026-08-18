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
- `article-quality-contract.md`


## 実行環境の固定条件

このSkillでローカル検証を行う場合、以下を既定条件として扱う。

- ハードウェア: Apple M5 Max / 128GB RAM
- OS: macOS
- Python: 3.14.6
- Pythonパッケージ管理: `uv`
- Python環境: `uv python install 3.14.6` / `uv python pin 3.14.6` / `uv sync` 後、`source .venv/bin/activate` を標準とする
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
5. 重要な公式仕様は、その主張の同じ段落または直後へ一次情報リンクを置く。参考資料一覧だけで代替しない。
6. `中核技術の役割`で`中核技術の定義 / 解決する課題 / 今回なぜ必要か`を固定ラベルの実内容として書く。定義を一次情報へ結び、今回のResearch Questionと検証へ必要な理由を説明する。一般的な製品紹介だけで済ませない。
7. `仕組みとデータフロー`でコンポーネント、処理順、入力、出力、保存先を説明する。
8. `技術選定理由`で次を固定ラベルの実内容として書く: `解決したい課題 / 採用した構成 / この構成を選んだ理由 / 適用条件・制約`。採用理由は最適性の断定に限らず、「複数の可能性から今回はこの仮説を優先して試す」という検証上の決断でもよい。仕組み図を採用理由の代替にしない。
9. 採用理由をResearch Question、実験制約、実測または一次情報へ結ぶ。比較候補や不採用案は、実際に比較した場合だけ任意で記載する。確認していない候補の性能や優劣を捏造しない。
10. 仮説と検証計画を簡潔に説明する。
11. 環境構築を再現可能な手順で書く。
12. 主要な実行単位を`目的 / 実行 / 観測結果 / 判断`で書く。コード全文は公開Repositoryへ置き、記事では理解に必要な部分へ絞ってよい。
13. `仮説と結果の対応`表で仮説ID、反証条件、実測、判定、Evidenceを結ぶ。
14. 結果を事実として示し、分析と考察を分ける。
15. 実際に発生した失敗は`失敗したこと・TIPS`へ、`発生条件 / 失敗した操作 / エラー全文または主要行 / 原因 / 切り分け / 効果がなかった方法 / 修正内容 / 再実行 / 再実行結果`の固定ラベルで残す。エラーメッセージを最重要Evidenceとする。操作、エラー、修正、再実行、結果には実際のコードブロックまたはログを置き、GUI障害では該当スクリーンショットまたは公開ログへのMarkdownリンクを置く。要約文だけで完了しない。
16. 失敗が実際になかった場合だけ、`判定: NOT_APPLICABLE / 理由 / 代替Evidence`を記録する。記録不足をNOT_APPLICABLEにしない。
17. 比較可能な数値がある場合は表またはグラフを使い、比較条件と限界を説明する。
18. `再現用成果物`にRepository、Notebook、raw data、完全ログへの読者向け導線を置く。公開不能なら理由と代替を示す。
19. 追加検証の結果、または実施しない理由と残る不確実性を書く。
20. 制約と未確認事項、参考資料をまとめる。
21. スクリーンショットが未取得なら明確なプレースホルダーを置く。
22. `article-quality-contract.md`を実行し、`results/article-evidence-map.json`を保存する。
23. Agent Repositoryのactivate済みuv環境から次を実行し、決定的検査結果をProjectへ保存する: `python -m evals.check_article_contract --article <Project>/article.md --strict --output <Project>/results/article-contract.json`。
24. commandがexit 0かつReader-visible GateがPASSした場合だけ`quality-review`へ渡す。exit 1なら不足項目を記事修正または上流Evidenceへrouteする。

## Writing rules

- 「簡単です」「当然」など初心者を置き去りにする表現を避ける。
- 先に目的、次にコマンド。
- 公式仕様を自分の実測のように書かない。
- 実測していない出力をコードブロックへ捏造しない。
- 長いログは必要行に絞り、全文保存先があれば示す。
- 「非常に強力です」「効率化できます」のような一般論だけで価値を作らず、具体的な環境・操作・結果を中心に書く。
- 公式資料の言い換えだけで記事を完成させない。
- Project内だけにあるEvidenceを、読者が確認可能なEvidenceとして扱わない。
- 見出し、URL、画像の存在だけで品質要件を満たしたと判断しない。

## Output

Qiita掲載用Markdown。

## Completion checks

- article-templateの主要セクションが満たされている。
- すべての重要主張に証拠がある。
- コードと説明が対応する。
- `results/article-evidence-map.json`で中心主張と記事位置、Evidence、読者向け成果物を追跡できる。
- `results/article-contract.json`の`acceptance.pass`がtrueで、現在のarticle.mdから再計算したmetricsと一致する。
- Reader-visible GateにMISSINGがない。
- 中核技術の定義、解決する課題、今回必要な理由が対応し、定義が一次情報へ結びついている。
- 技術選定理由が課題、採用構成、採用理由、適用条件・制約へ対応し、理由がResearch Question、実験制約、実測または一次情報へ結びついている。比較候補や不採用案は必須ではない。
- 実際の失敗が、エラーEvidence、修正差分、再実行Evidenceまで固定ラベルで追跡できる。失敗なしなら理由付きNOT_APPLICABLEである。

## Canonical output

最終草稿は原則 `article.md` として保存する。

## Project state update

草稿作成後、`PROJECT_STATE.md` の Articleを更新し `quality-review` へ進む。
