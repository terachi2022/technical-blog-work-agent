# Production Metrics Policy

## Status

このPolicyは将来Phase向けであり、Step 1〜4のMVPではProduction Metrics取得を必須にしない。

## Principle

公開後成果は記事品質と分離する。

高PV記事が高品質とは限らず、低PV記事が低品質とも限らない。

Production Performanceには以下の交絡要因がある。

- テーマ需要
- 検索ボリューム
- 公開時期
- Qiitaタグ
- SNS / referral
- 既存フォロワー
- 記事の経過日数

## Planned metrics

### GA4

- Organic Sessions
- Users
- Engagement
- Traffic source

### Qiita

- Views
- Likes
- Stocks
- Comments

## Standard windows

記事間比較では公開後経過日数を揃える。

```text
Day 7
Day 30
Day 90
```

## MLflow naming proposal

```text
ga4_organic_sessions_7d
ga4_organic_sessions_30d
ga4_engagement_rate_30d
qiita_views_30d
qiita_likes_30d
qiita_stocks_30d
```

## Improvement guardrail

Production metricだけを最大化するようAgentを変更しない。
Offline Qualityを維持した上で、Production Performanceとの関連を分析する。
