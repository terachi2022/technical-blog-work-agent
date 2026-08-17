# Evidence Gate

## Purpose

記事草稿へ進む前に、実証型記事として必要な証拠が揃っているかを検査する。
各SkillのCompletion checksとは別に、**記事化を許可するオーケストレーション上のGate**として使う。

## Required checks

以下を `PASS / MISSING / NOT_APPLICABLE` で判定する。

- [ ] Research Questionが定義されている
- [ ] 仮説が定義されている
- [ ] 仮説の根拠がある
- [ ] 検証計画がある
- [ ] 独立変数・従属変数・固定条件が定義されている
- [ ] 成功 / 失敗 / 不確定の判定条件がある
- [ ] 実際の検証環境が記録されている
- [ ] M5 Max / 128GB / arm64 / macOSの実環境情報が記録されている
- [ ] Pythonを使う場合、Python 3.14.6 / uvの実行条件が記録されている
- [ ] サービスを使う場合、Docker Compose構成が記録されている
- [ ] 実際に使用したコマンドまたはコードがある
- [ ] stdout / stderr / log / raw dataの少なくとも必要な証拠がある
- [ ] 実験結果がある
- [ ] 結果分析がある
- [ ] 考察がある
- [ ] 公式資料または一次情報がある
- [ ] 重要な主張をSourceまたはEvidenceへ追跡できる
- [ ] 制約・未確認事項が明確である
- [ ] 失敗・試行錯誤が発生した場合、その記録が残っている
- [ ] 必要なグラフまたはスクリーンショット計画がある

## Gate decision

### PASS

必須項目がすべて `PASS` または妥当な `NOT_APPLICABLE`。
`article-drafting` へ進んでよい。

### FAIL

1つでも必須項目が `MISSING` の場合は記事完成形へ進まない。
以下の形式で不足証拠を出す。

```markdown
# Missing Evidence

| ID | Missing evidence | Why required | Return to | Action |
|---|---|---|---|---|
| ME-01 |  |  |  |  |
```

## Return routing

不足内容に応じて戻り先を決める。

- 一次情報不足 → `technical-research`
- 仮説不足 → `hypothesis-design`
- 設計不足 → `experiment-design`
- 環境証拠不足 → `environment-build`
- raw evidence不足 → `experiment-execution`
- 分析不足 → `result-analysis`
- 解釈・制約不足 → `discussion`
- 画像不足 → `visual-evidence`

## Anti-fabrication rule

Evidence Gateを通すために、存在しない測定値、ログ、URL、画像、エラー、実行結果を生成してはならない。
取得不能なものは `MISSING` または `NOT_APPLICABLE` とする。
