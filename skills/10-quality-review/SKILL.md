---
name: quality-review
description: 技術ブログ草稿を証拠、再現性、技術的正確性、初心者可読性、Qiita形式、公開リスクの観点から最終レビューするときに使う。
---

# Quality Review

## Purpose

文章の美しさだけではなく、公開可能な技術記事としての根拠と再現性を検査する。

## Inputs

- article draft
- all evidence
- source list
- review rubric


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

1. 記事中の重要な技術主張を抽出する。
2. 各主張をSourceまたはEvidenceへトレースする。
3. 実行手順を順番に読み、欠落コマンドを探す。
4. バージョンと固定環境を確認する。
5. 未検証の断定を探す。
6. 架空の出力、URL、数値がないか確認する。
7. 初学者が詰まる前提知識を探す。
8. スクリーンショットの必要箇所を確認する。
9. Qiita Markdownとして構造を確認する。
10. `google-search-quality-policy.md` と `review-rubric.md` に従い、Google方針が関係する場合は現行公式情報を再確認する。
11. Original Value Gateを実行し、公式資料を読むだけでは得られない価値を1文で示す。
12. 9項目を0〜2点で採点し合計18点を出す。
13. Publication Gateとして `PASS / WARN / BLOCK` を付ける。
14. BLOCKは記事へ直接修正案を反映できるものは修正し、Evidence不足は該当Phaseへ戻す。
15. 修正後に再レビューする。

## Output

### Review summary

- PASS:
- WARN:
- BLOCK:

### Blocking issues

### Improvements

### E-E-A-T / Quality score

- Experience: /2
- Expertise: /2
- Authoritativeness: /2
- Trustworthiness: /2
- Originality: /2
- Reproducibility: /2
- Usefulness: /2
- Evidence: /2
- Clarity: /2
- Total: /18

### Original value

- 公式資料を読むだけでは得られない価値:

### Publication status

`READY / NEEDS_REVISION / BLOCKED`

### Machine-readable output

同内容を `results/quality-review.json` に保存する。

```json
{
  "publication_status": "READY",
  "scores": {
    "experience": 0,
    "expertise": 0,
    "authoritativeness": 0,
    "trustworthiness": 0,
    "originality": 0,
    "reproducibility": 0,
    "usefulness": 0,
    "evidence": 0,
    "clarity": 0
  },
  "total": 0,
  "blocking_issues": [],
  "warnings": [],
  "original_value": ""
}
```

このJSONはMLflow Offline Evaluationへ取り込むため、key名を理由なく変更しない。

## Completion checks

`READY` はBLOCKが0件の場合のみ。

## Project state update

レビュー結果を `PROJECT_STATE.md` に反映する。`READY` はEvidence Gate PASSかつPublication BLOCKが0件の場合のみ。
