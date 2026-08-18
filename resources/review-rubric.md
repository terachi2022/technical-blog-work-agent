# Technical Article Offline Quality Rubric

## 目次

- [位置づけ](#位置づけ)
- [公開安全性と品質達成](#公開安全性と品質達成)
- [採点原則](#採点原則)
- [9項目のアンカー](#9項目のアンカー)
- [Original Value Gate](#original-value-gate)
- [品質判定](#品質判定)
- [Machine-readable output](#machine-readable-output)

## 位置づけ

これはGoogleのランキングスコアではなく、実証型技術記事のためのProject独自Offline Quality Rubricである。
E-E-A-Tは自己点検の概念として参照するが、「Google準拠」「検索順位保証」と表現しない。

## 公開安全性と品質達成

2つの判定を分離する。

### Publishable

- `PASS`: 捏造、重大な誤情報、秘密情報、危険な欠落がない。
- `WARN`: 公開は可能だが、制約または軽微な不足がある。
- `BLOCK`: 捏造、出典のない重大仕様、再現不能な主要手順、秘密情報、危険な操作、Evidence Gate未通過のいずれかがある。

### Quality status

- `QUALITY_READY`: 14/18以上、0点なし、Reader-visible GateにMISSINGなし、未解決BLOCKなし。
- `NEEDS_REVISION`: Publishableだが品質条件を満たさない。
- `BLOCKED`: PublishableがBLOCK、またはProject Evidence GateがFAIL。

PublishableがPASSでもQuality statusはNEEDS_REVISIONになり得る。

## 採点原則

- 最初に記事本文だけを読み、読者が確認できる内容だけで採点する。
- 次にProject Evidenceを読み、記事中の主張を検証する。
- 各点数へ`article_locations`、`rationale`、`gaps`を付ける。
- 2点には記事中の具体的な引用または節を最低1件示す。
- Project内にだけ存在し記事へ表れていないEvidenceは、Article-only Reviewの加点に使わない。
- 証拠を示せない2点、理由のない全項目2点を認めない。
- グラフ、Notebook、公開Repositoryは記事形式に応じて判断し、対象外なら理由と代替を記録する。

## 9項目のアンカー

### Experience

- `0`: 実行環境、操作、観測結果が確認できず、実体験を追跡できない。
- `1`: 環境、コマンド、結果の一部はあるが、実行過程、試行錯誤、失敗の切り分けが不足する。
- `2`: 操作、stdout/stderrまたは画面、判断、失敗、修正、再実行結果が時系列で追跡できる。

### Expertise

- `0`: 手順の羅列で、仕組み、設定理由、データフロー、適用範囲を説明していない。
- `1`: 理由や制約の一部を説明するが、全体構造または代替説明が不足する。
- `2`: 仕組みとデータフロー、設定理由、代替案、制約、一般化範囲を実測と結びつけて説明する。

### Authoritativeness

- `0`: 重要仕様の一次情報がない、または参考資料欄へURLを並べるだけで主張との対応がない。
- `1`: 一次情報はあるが、主張近傍の配置、対象version、確認日のいずれかが不足する。
- `2`: 重要仕様の近くに一次情報があり、対象versionまたは確認日と支持する主張を追跡できる。

### Trustworthiness

- `0`: 事実、推論、未確認を混同する、重大な矛盾がある、または不都合な結果を隠す。
- `1`: 分離と制約は概ねあるが、仮説と結果の対応、失敗の扱い、主張の強さに不足がある。
- `2`: 事実、仕様、解釈、推奨、未確認を分離し、仮説と結果を対応させ、不採用結果と制約を開示する。

### Originality

- `0`: 公式資料や既存記事の要約で、実験固有の知見がない。
- `1`: 実機検証や環境差分はあるが、観測の列挙に留まり、深い分析または新しい判断へ結びつかない。
- `2`: 実験、比較、失敗、追加検証のいずれかから、公式資料だけでは得られない再利用可能な洞察を導く。

### Reproducibility

- `0`: 主要手順、version、依存関係、入力の欠落により追試できない。
- `1`: 基本手順はあるが、lock、設定、データ、完全コード、成果物の一部が不足する。
- `2`: 環境、version、依存lock、コマンド、入力、コード、判定条件が揃い、読者が同条件で追試できる。

### Usefulness

- `0`: 読者が次の操作または判断へ進めず、必要な成果物への導線もない。
- `1`: 課題への回答または手順はあるが、再利用可能な成果物、選択基準、詰まりどころの一部が不足する。
- `2`: 読者の問いに答え、具体的な行動、判断基準、失敗回避策、アクセス可能な再現成果物を提供する。

### Evidence

- `0`: 中心主張とSource/Evidenceの対応を確認できない。
- `1`: Evidenceはあるが、一部がProject内部だけ、主張から遠い、または対応が曖昧である。
- `2`: 中心主張、記事位置、一次情報、ログ、データ、画像、公開成果物を一貫して追跡できる。

### Clarity

- `0`: 対象読者、結論、手順、結果の構造が不明で、読了が困難である。
- `1`: 基本構造はあるが、長いコード、重複、図表不足、説明順の問題が残る。
- `2`: TL;DR、前提、仕組み、手順、結果、考察、制約が明瞭で、図表と本文が相互補完する。

**Total: /18**

## Original Value Gate

「公式ドキュメントを読むだけでは得られない情報」を1文で説明し、対応する実測Evidenceと考察を示す。

実機で動かした、M5 Maxを使った、エラーが出た、という存在確認だけでは2点にしない。次のいずれかへ結びつける。

- 条件差による結果の比較
- 公式手順と実環境の差分
- 失敗原因の切り分けと再利用可能な回避策
- 追加検証による仮説の更新
- 実務での選択条件または非適用条件

中心が転載・要約のみならPublishableを`BLOCK`とする。独自Evidenceはあるが分析が浅い場合はOriginalityを1点以下とする。

## 品質判定

低評価項目には次を出す。

- 不足しているReader-visible Evidence
- Project Evidenceの有無
- 記事修正で解決するか、上流Phaseへ戻るか
- 改善方法
- 追加調査または追加検証

点数を上げるためにEvidenceを捏造しない。

## Machine-readable output

```json
{
  "schema_version": "2.0",
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

実出力の`score_evidence`は9項目すべてを含める。上記は1項目の構造例であり、省略を許可するschemaではない。
