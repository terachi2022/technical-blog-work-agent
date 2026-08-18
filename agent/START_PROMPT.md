# Technical Blog Agent — Executable Article Task Template

このファイルは `tools/init_article_project.py` が実値を埋め、Article Project内の
`AGENT_TASK.md` として生成するテンプレートである。利用者にVersion情報を転記させない。

## Project identity

- Article ID: `{{ARTICLE_ID}}`
- Project Directory: `{{PROJECT_DIR}}`
- Agent Repository: `{{AGENT_REPOSITORY}}`
- Model / runtime: `{{MODEL_RUNTIME}}`

## テーマと読者

- テーマ: `{{TOPIC}}`
- 想定読者: `{{AUDIENCE}}`

## 実行命令

Technical Blog Agentとして、このProjectを開始または再開してください。
計画の提示だけで停止せず、`PROJECT_STATE.md` と実ファイルから最初の未完了Phaseを判定し、
ユーザーの承認または操作が本当に必要な箇所まで連続して実行してください。

記事成果物は必ずProject Directoryへ保存し、Agent Repositoryへ混在させないでください。
Version identityは初期化時に `PROJECT_STATE.md` と
`results/version-snapshot.json` へ記録済みです。人間に再入力・転記させず、内容を読み取ってください。

## Required phases and outputs

1. Research → `research.md`
2. Research Question / Hypothesis → `hypothesis.md`
3. Experiment Design → `experiment-plan.md`
4. Environment → `experiment-log.md` と環境Evidence
5. Experiment → `experiment-log.md`, `data/`, `logs/`
6. Results / Analysis → `analysis.md`, 必要なら `scripts/` と `images/`
7. Discussion → `discussion.md`
8. Additional Experiment → 必要な場合のみ3〜7へ戻る
9. Visual Evidence → `images/` または具体的な撮影指示
10. Evidence Gate → PASS / Missing Evidenceを記録
11. Article Drafting → Evidence Gate PASS時のみ `article.md`
12. Reader-visible Evidence Gate + Quality Review → `results/article-evidence-map.json` / `results/article-contract.json` / `results/quality-review.json`

各Phase終了時に `PROJECT_STATE.md` を更新してください。完了済みPhaseを理由なく再実行しないでください。

## article.mdを実際に生成する手順

Evidence GateがPASSしたら、説明だけで停止せず次を実行してください。

1. Agent Repositoryの `skills/08-article-drafting/SKILL.md` を読み、そこに定義されたArticle Draftingを実行する。
2. `research.md`、`hypothesis.md`、`experiment-plan.md`、`experiment-log.md`、`analysis.md`、`discussion.md`、Evidence Gate結果、画像・ログを入力にする。
3. Qiita掲載用Markdownの実内容を `{{PROJECT_DIR}}/article.md` へ保存する。
4. `article.md` が存在して空でないことを確認する。見出しだけのダミーや架空Evidenceは禁止する。
5. `PROJECT_STATE.md` のPhase 11を `COMPLETED`、Content statusを `DRAFT` 以上へ更新する。
6. `article-quality-contract.md`を適用し、中心主張と記事位置、Evidence、読者向け成果物を`results/article-evidence-map.json`へ保存する。さらに`evals.check_article_contract --strict`を実行し、`results/article-contract.json`へ保存する。
7. `技術選定理由`で課題、今回採用した構成、その構成を優先して試すと決めた理由、適用条件・制約を明示し、採用理由をResearch Question、実験制約、実測または一次情報へ結ぶ。比較候補や不採用案は必須にしない。
8. `中核技術の役割`で`中核技術の定義 / 解決する課題 / 今回なぜ必要か`を明示する。定義を一次情報へ結び、今回のResearch Questionと検証に必要な理由まで説明する。
9. 実際の失敗がある場合は、エラーメッセージを最重要Evidenceとし、失敗した操作、エラー全文または主要行、原因、切り分け、効果がなかった方法、修正内容、再実行、再実行結果を固定ラベルで記録する。GUI障害はスクリーンショットまたは公開ログを許可する。失敗がない場合は理由と代替Evidence付きで`NOT_APPLICABLE`とする。
10. Reader-visible GateがPASSした場合だけ`quality-review`を実行し、結果を`results/quality-review.json`へ保存する。

Evidence GateがFAILなら `article.md` を作らず、Missing Evidenceと戻り先Phaseを記録して不足Phaseへ戻ってください。

## Evidence rules

- 検証可能な内容は実際に検証する。
- 未確認のログ、エラー、数値、グラフ、スクリーンショットを捏造しない。
- 公式資料、今回の実測、推測・考察を分離する。
- 失敗は削除せず `experiment-log.md` と記事のTIPSへ残す。
- Python 3.14.6とuvを使用し、常駐サービスや複数サービスはDocker Composeで管理する。
- Apple Silicon nativeのMPS / Metal / MLXを優先し、CUDA/NVIDIAを前提にしない。

## Completion condition

最低限、次が実内容を持って存在するまでSTEP 1.5は完了ではありません。

```text
PROJECT_STATE.md
results/version-snapshot.json
research.md
hypothesis.md
experiment-plan.md
experiment-log.md
analysis.md
discussion.md
article.md
results/article-evidence-map.json
results/article-contract.json
results/quality-review.json
```

終了時に、完了Phase、未完了Phase、Missing Evidence、生成した `article.md` の絶対パスを報告してください。
