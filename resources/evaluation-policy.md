# Evaluation Policy

## Goal

Agent / Skillの改善を「感覚」ではなく、同一条件での比較によって判断する。

## Evaluation layers

### 1. Machine checks

LLMに任せる必要がない項目をコードで評価する。

例:

- 必須章の有無
- Reference linkの有無
- M5 Max / Python 3.14.6 / uv等の環境記載
- Evidence Gate通過状態
- 未解決placeholder
- quality-review JSONのschema
- Reader-visibleな仮説/結果表、主張近傍リンク、再現用成果物の構造
- 技術選定理由の課題、採用案、不採用案、適用・非適用条件
- トラブルシューティングの失敗操作、実エラー、修正差分、再実行Evidence

Machine checksは形式と契約の検査であり、単独で記事品質18点を出さない。
固定anti-gaming caseは`evals/datasets/article-contract-regressions-v1.jsonl`で回帰検査する。

### 2. LLM Judge

主観性がある品質評価に利用する。

例:

- Expertise
- Originality
- Usefulness
- Clarity
- Discussion quality

LLM Judgeだけを正解としない。
各scoreに記事中の引用箇所、理由、不足を要求し、根拠のない全項目満点を認めない。

### 3. Human Review

人間が重要記事・固定Datasetの一部をレビューし、LLM Judgeと人間評価のズレを確認する。

記事レビューの表示・引き渡しは `human-review-policy.md` に従う。Traceには全文MarkdownをOpenAI互換assistant messageとして保存し、Trace画面でMarkdown表示を確認する。長文記事は標準Review previewではなく全文Review UIで評価する。

## Human calibration

- 人間評価済み記事をRubric version付きCalibration Datasetへ登録する。
- Calibrationに使った記事だけで改善判定せず、別記事をholdoutとして評価する。
- 合計点差、項目別絶対誤差、重大な0点のfalse READYを確認する。
- 初期受入基準は合計点差2点以内、項目差は原則1点以内、重大な0点を持つ記事を`QUALITY_READY`にしないこととする。
- Rubricを変更した場合はversionを上げ、旧scoreと同じ尺度として直接比較しない。

## Offline vs Production

Offline QualityとProduction Performanceを同一scoreへ単純合算しない。

```text
Offline Quality != PV
```

公開後成果は別metricとして保持する。

## Baseline comparison

Agentの変更前後は、同じEvaluation Dataset versionで比較する。

比較時に異なるもの:

- agent_version
- git_commit

固定するもの:

- evaluation dataset version
- 評価rubric
- 可能ならjudge model / judge settings

ScorerやRubricを変更した場合、その変更もversionとして記録し、過去runとの単純比較を避ける。

## Official MLflow concepts

MLflow Evaluation Datasetは固定test suite / benchmarkとして利用できる。
Evaluation Dataset機能にはSQL backendが必要である。

Official references:

- https://mlflow.org/docs/latest/genai/datasets/
- https://mlflow.org/docs/latest/genai/eval-monitor/scorers/
- https://mlflow.org/docs/latest/genai/eval-monitor/scorers/custom/tutorial/
