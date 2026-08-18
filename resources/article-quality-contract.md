# Article Quality Contract

## Purpose

Project内にEvidenceが存在することと、読者が記事からEvidenceへ到達できることを分けて検査する。
このContractはArticle Drafting後、Quality Review前に適用する。

## Required reader-visible elements

記事テーマに対して妥当な`NOT_APPLICABLE`を除き、次を本文へ含める。

- `## 仕組みとデータフロー`: コンポーネント、処理順、入力、出力、保存先を説明する。
- `## 仮説と結果の対応`: 仮説ID、反証条件、実測、判定、Evidenceを同じ表で示す。
- 検証手順ごとの`目的 / 実行 / 観測結果 / 判断`: コマンドを貼るだけで終えない。
- 重要な公式仕様の主張近傍に一次情報リンクを置く。末尾の参考資料だけで代替しない。
- 発生した失敗の`操作 / 観測 / 原因仮説 / 切り分け / 修正 / 再実行結果`を時系列で示す。
- 比較可能な数値がある場合は、表またはグラフで差と条件を示す。
- `## 再現用成果物`: 公開可能な記事ではRepository、Notebook、データ、完全ログへの導線を示す。
- 追加検証の実施結果、または実施しない判断理由と残る不確実性を示す。

## Article evidence map

`results/article-evidence-map.json`へ、記事の中心主張と読者向け成果物を保存する。

```json
{
  "schema_version": "1.0",
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
- [ ] 仮説、実測、判定、Evidenceが表で対応する
- [ ] 主要コマンドに観測結果と判断が続く
- [ ] 重要仕様の近くに一次情報リンクがある
- [ ] 失敗が時系列の試行錯誤として説明されている
- [ ] 必要な比較表またはグラフがある
- [ ] 読者が再現用成果物へアクセスできる
- [ ] 追加検証の実施または不実施判断が説明されている
- [ ] 記事中の画像とリンクが公開先で解決可能である

`MISSING`が1件でもあれば`QUALITY_READY`にしない。Project Evidence不足なら上流Phaseへ戻し、記事への反映不足ならArticle Draftingへ戻す。

## Non-applicable rule

`NOT_APPLICABLE`は省略の言い換えに使わない。対象外である理由、読者価値への影響、代替Evidenceを記録する。

例:

- 数値比較が存在しないためグラフは対象外。ただし構成図と実画面Evidenceを掲載する。
- 機密ProjectのためRepositoryは非公開。記事内に最小再現コードと依存関係を掲載する。

## Anti-gaming rule

見出し、URL、画像、コードブロックが存在するだけではPASSにしない。内容が中心主張を支え、読者の理解または追試に使えることを確認する。
