---
name: discussion
description: 技術実験の分析結果から意味、制約、代替説明、実務上の含意を考察し、必要な追加検証を決定するときに使う。
---

# Discussion

## Purpose

「結果がこうだった」から一歩進み、なぜそうなった可能性があるか、
実務上どこまで一般化できるかを慎重に整理する。

## Inputs

- result analysis
- research notes
- experiment evidence


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

1. 各分析結果の意味を説明する。
2. 公式仕様と整合するか比較する。
3. 想定と違った点を抽出する。
4. 代替説明を最低1つ検討する。
5. 環境固有要因を評価する。
6. 一般化できる範囲を限定する。
7. 実務上の推奨事項候補を作る。
8. 追加検証で結論が大きく変わる可能性を評価する。
9. Originalityを深める追加検証候補を最低1件検討し、情報利得、費用、Research Questionへの影響を評価する。
10. 必要なら `experiment-design` へ戻る。
11. 不要なら「実施しない理由」「残る不確実性」「読者への影響」を記録して記事化へ進む。

## Fact / inference separation

必ず以下を分ける。

- Fact: 今回観測した事実
- Specification: 公式資料に記載された内容
- Interpretation: 事実からの解釈
- Recommendation: 実務上の提案

## Output

- 主要な考察
- 代替説明
- 制約
- 一般化範囲
- 実務上の示唆
- 追加検証の要否
- 記事の中心メッセージ候補
- 公式資料だけでは得られない再利用可能な洞察
- 追加検証の採用/不採用理由

## Canonical output

考察は原則 `discussion.md` に保存し、Fact / Specification / Interpretation / Recommendationを区別する。

## Project state update

追加検証が必要なら `PROJECT_STATE.md` の Additional Experimentを `IN_PROGRESS` とし `experiment-design` へ戻す。不要ならDiscussionを `COMPLETED` にする。
