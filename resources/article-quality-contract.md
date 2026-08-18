# Article Quality Contract

## Purpose

Project内にEvidenceが存在することと、読者が記事からEvidenceへ到達できることを分けて検査する。
このContractはArticle Drafting後、Quality Review前に適用する。

## Required reader-visible elements

記事テーマに対して妥当な`NOT_APPLICABLE`を除き、次を本文へ含める。

- `## 仕組みとデータフロー`: コンポーネント、処理順、入力、出力、保存先を説明する。
- `## 技術選定理由`: 解決したい課題、今回採用した構成、その構成を優先して試すと決めた理由、適用条件・制約を対応させる。採用理由は最適性の断定でなく、検証上の優先判断でもよく、Research Question、実験制約、実測または一次情報へ結ぶ。仕組み図だけで代替しない。比較候補や不採用案は実際に比較した場合だけ任意で示す。
- `## 仮説と結果の対応`: 仮説ID、反証条件、実測、判定、Evidenceを同じ表で示す。
- 検証手順ごとの`目的 / 実行 / 観測結果 / 判断`: コマンドを貼るだけで終えない。
- 重要な公式仕様の主張近傍に一次情報リンクを置く。末尾の参考資料だけで代替しない。
- 発生した失敗の`発生条件 / 失敗した操作 / エラー全文または主要行 / 原因 / 切り分け / 効果がなかった方法 / 修正内容 / 再実行 / 再実行結果`を固定ラベルで時系列に示す。エラーメッセージを最重要Evidenceとする。失敗操作、エラー、修正、再実行、再実行結果は実コードまたは実ログをコードブロックで示す。GUI障害では該当スクリーンショットまたは公開ログへのMarkdownリンクをEvidenceとして許可する。
- 失敗がなかった場合は`判定: NOT_APPLICABLE / 理由 / 代替Evidence`を示す。記録不足をNOT_APPLICABLEにしない。
- 比較可能な数値がある場合は、表またはグラフで差と条件を示す。
- `## 再現用成果物`: 公開可能な記事ではRepository、Notebook、データ、完全ログへの導線を示す。
- 追加検証の実施結果、または実施しない判断理由と残る不確実性を示す。

## Article evidence map

`results/article-evidence-map.json`へ、記事の中心主張と読者向け成果物を保存する。

```json
{
  "schema_version": "1.1",
  "article": "article.md",
  "claims": [
    {
      "id": "C-01",
      "claim": "",
      "article_section": "",
      "article_quote": "",
      "source_or_evidence": ["EV-01"],
      "reader_visible": true
    }
  ],
  "hypotheses": [
    {
      "id": "H1",
      "article_section": "## 仮説と結果の対応",
      "decision": "SUPPORTED",
      "evidence": ["EV-01"]
    }
  ],
  "decisions": [
    {
      "id": "D-01",
      "problem": "",
      "selected": "",
      "decision_reason": "",
      "selection_evidence": ["EV-01"],
      "constraints": "",
      "article_section": "## 技術選定理由"
    }
  ],
  "failures": [
    {
      "id": "F-01",
      "status": "RESOLVED",
      "error_evidence": ["EV-02"],
      "fix_evidence": ["EV-03"],
      "rerun_evidence": ["EV-04"],
      "article_section": "## 失敗したこと・TIPS"
    }
  ],
  "reader_assets": [
    {
      "type": "repository",
      "url": "https://github.com/...",
      "availability": "PUBLIC"
    }
  ]
}
```

## Reader-visible gate

各項目を`PASS / MISSING / NOT_APPLICABLE`で判定する。

- [ ] 中心主張が記事内の引用箇所とSource/Evidenceへ対応する
- [ ] 仕組みとデータフローが説明されている
- [ ] 技術選定が課題、採用構成、採用理由、適用条件・制約へ対応し、理由がResearch Question、実験制約、実測または一次情報へ結びついている
- [ ] 仮説、実測、判定、Evidenceが表で対応する
- [ ] 主要コマンドに観測結果と判断が続く
- [ ] 重要仕様の近くに一次情報リンクがある
- [ ] 実際の失敗がある場合、エラー全文または主要行を最重要Evidenceとして、失敗操作、原因、切り分け、効果がなかった方法、修正内容、再実行、再実行結果まで説明されている。GUI障害はスクリーンショットまたは公開ログを許可する。失敗なしの場合だけ、理由と代替Evidence付きでNOT_APPLICABLEである
- [ ] 必要な比較表またはグラフがある
- [ ] 読者が再現用成果物へアクセスできる
- [ ] 追加検証の実施または不実施判断が説明されている
- [ ] 記事中の画像とリンクが公開先で解決可能である

`MISSING`が1件でもあれば`QUALITY_READY`にしない。Project Evidence不足なら上流Phaseへ戻し、記事への反映不足ならArticle Draftingへ戻す。

## Deterministic precheck

Agent Repositoryのactivate済みuv環境から実行し、結果を記事Projectへ保存する。

```bash
python -m evals.check_article_contract \
  --article /absolute/path/to/article.md \
  --strict \
  --output /absolute/path/to/results/article-contract.json
```

exit 0は構造契約の合格だけを表す。固定ラベル間の意味的一貫性、選定理由の妥当性、失敗原因の正しさは独立ReviewerとHuman Reviewで確認する。

## Non-applicable rule

`NOT_APPLICABLE`は省略の言い換えに使わない。対象外である理由、読者価値への影響、代替Evidenceを記録する。

実際の失敗がない場合も`article-evidence-map.json`の`failures`へ`status: NOT_APPLICABLE`、理由、代替Evidenceを1件記録する。

例:

- 数値比較が存在しないためグラフは対象外。ただし構成図と実画面Evidenceを掲載する。
- 機密ProjectのためRepositoryは非公開。記事内に最小再現コードと依存関係を掲載する。

## Anti-gaming rule

見出し、URL、画像、コードブロックが存在するだけではPASSにしない。内容が中心主張を支え、読者の理解または追試に使えることを確認する。

`技術選定理由`や失敗記録の固定ラベルが存在しても、採用理由、エラー、修正、再実行Evidenceが空または相互に無関係ならFAILとする。実障害でエラーメッセージEvidenceが欠ける場合はReader-visible GateをFAILにし、`QUALITY_READY`にしない。このGateから品質項目の点数上限を機械的に決めない。
