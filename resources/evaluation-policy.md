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

### 2. LLM Judge

主観性がある品質評価に利用する。

例:

- Expertise
- Originality
- Usefulness
- Clarity
- Discussion quality

LLM Judgeだけを正解としない。

### 3. Human Review

人間が重要記事・固定Datasetの一部をレビューし、LLM Judgeと人間評価のズレを確認する。

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
