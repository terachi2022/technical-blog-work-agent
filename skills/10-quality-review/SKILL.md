---
name: quality-review
description: 技術ブログ草稿を記事だけの読者視点とProject Evidence検証の二段階で独立レビューし、公開安全性とTechnical Article Offline Qualityを分離判定して、MLflow TraceとHuman Reviewへ全文Markdownを引き渡すときに使う。
---

# Quality Review

## Purpose

文章の美しさだけではなく、公開可能な技術記事としての根拠と再現性を検査する。

## Inputs

- article draft
- all evidence
- source list
- review rubric
- `article-quality-contract.md`
- `results/article-evidence-map.json`


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

1. Writerの自己説明やProject Evidenceを見ず、最初に`article.md`だけを読む。
2. 記事だけから重要主張、仕組み、技術選定理由、実行過程、仮説と結果、失敗、読者向け成果物を確認する。
3. `article-quality-contract.md`のReader-visible Gateを実行する。
4. 9項目をアンカーに従って仮採点し、各項目へ記事中の引用箇所、理由、不足を記録する。
5. 次に`results/article-evidence-map.json`とProject Evidenceを読み、各主張をSourceまたはEvidenceへ検証する。
6. 実行手順、バージョン、固定環境、入力と出力、画像、リンクを検証する。
7. 未検証の断定、架空の出力、URL、数値、内部矛盾を探す。
8. `google-search-quality-policy.md`と`review-rubric.md`に従い、Google方針が関係する場合は現行公式情報を再確認する。
9. Original Value Gateを実行し、公式資料を読むだけでは得られない再利用可能な洞察とEvidenceを示す。
10. Evidence検証後の9項目を0〜2点で確定し、合計18点を出す。
11. Publishableを`PASS / WARN / BLOCK`、Quality statusを`QUALITY_READY / NEEDS_REVISION / BLOCKED`で別々に判定する。
12. `QUALITY_READY`は14/18以上、0点なし、Reader-visible GateにMISSINGなし、未解決BLOCKなしの場合だけ許可する。
13. 証拠のない2点、理由のない全項目2点を禁止する。
14. `仕組みとデータフロー`だけがあり、解決課題、候補比較、選定・不採用理由、適用・非適用条件が記事にない場合はExpertiseとClarityを2点にしない。
15. 発生した失敗が要約だけで、実エラー、失敗操作、修正差分、再実行結果を読者が追えない場合はExperienceとUsefulnessを2点にしない。その失敗をOriginal Valueの根拠にする場合はOriginalityも2点にしない。
16. Machine Scorerのラベル検出PASSを意味品質の代替にしない。固定ラベルの内容が同じ失敗・同じ選定判断を支えるか確認する。
17. 記事修正で解決する不足はArticle Draftingへ、Evidence不足は該当する上流Phaseへ戻す。
18. 修正後はArticle-only Reviewから再実行する。
19. Human Reviewを行う場合は`human-review-policy.md`を読み、`article.md`全文をOpenAI互換assistant messageとしてTraceへ保存する。
20. `View full trace`でMarkdown表示、先頭見出し、末尾`参考資料`を確認する。Trace保存成功だけで表示確認済みと判定しない。
21. 長文記事は標準Review previewではなく全文Review UIへ振り分け、全画像、9品質項目、Publishable、Critical issue、MLflow接続を実画面でforward-testする。
22. Human handoff gateが1項目でも不合格なら採点を依頼せず、`BLOCKED: REVIEW_SURFACE_INCOMPLETE`として修正する。人間の評価値をAgentが入力・送信しない。

## Output

### Review summary

- PASS:
- WARN:
- BLOCK:

### Blocking issues

### Improvements

### Technical Article Offline Quality score

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

### Publication decisions

- Publishable: `PASS / WARN / BLOCK`
- Quality status: `QUALITY_READY / NEEDS_REVISION / BLOCKED`

### Machine-readable output

同内容を `results/quality-review.json` に保存する。

```json
{
  "schema_version": "2.1",
  "review_mode": "article_only_then_evidence_verification",
  "publishable": "PASS",
  "quality_status": "NEEDS_REVISION",
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
  "score_evidence": {
    "experience": {
      "article_locations": [],
      "rationale": "",
      "gaps": []
    }
  },
  "total": 0,
  "reader_visible_gate": "FAIL",
  "blocking_issues": [],
  "warnings": [],
  "original_value": ""
}
```

このJSONはMLflow Offline Evaluationへ取り込むため、key名を理由なく変更しない。
`score_evidence`は省略せず9項目すべてを含める。例の`experience`だけを出力して完了しない。

## Completion checks

`QUALITY_READY`は14/18以上、0点なし、Reader-visible GateにMISSINGなし、未解決BLOCKなしの場合のみ。

Human Reviewを依頼する場合、`human-review-policy.md` のTrace全文Markdown確認とHuman handoff gateも全項目PASSであること。

## Project state update

レビュー結果を`PROJECT_STATE.md`へ反映する。PublishableとQuality statusを別々に記録する。
