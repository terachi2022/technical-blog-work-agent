# Technical Blog Agent — Operational Start Prompt

以下をChatGPT WorkのTechnical Blog Agentへ渡し、**実際のArticle Projectを開始または再開する**。

---

今回作成したTechnical Blog Agentを使用して、技術ブログProjectを開始してください。

## Project identity

- Article ID: `<例: 20260818-mlflow-m5max-001>`
- Project Directory: `<例: /Users/tera/dev/technical-blog-projects/20260818-mlflow-m5max-001>`
- Agent Repository: `<例: /Users/tera/dev/technical-blog-work-agent>`

## テーマ

`<ここに検証テーマを書く>`

## 想定読者

`<例: MLflowを初めて使うインフラエンジニア>`

## 実行ルール

1. 最初にProject Directoryの `PROJECT_STATE.md` を読み、新規Projectか再開か判定してください。
2. Agent RepositoryとArticle Projectを混同しないでください。記事成果物は必ずProject Directoryへ保存してください。
3. Agent Repositoryの `MANIFEST.json` とGit状態を確認し、Agent version / Git commit / Git branch / git_dirtyを `PROJECT_STATE.md` へ記録してください。
4. 正式baselineとして利用する場合、Agent Repositoryは原則 `git_dirty=false` としてください。dirtyならその事実を報告し、勝手にclean扱いしないでください。
5. 最初から `article.md` を作らず、以下のPhaseを順に実行してください。

## Required phases

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
12. Quality Review → `results/quality-review.json`

## Evidence rules

- 検証可能な内容は実際に検証してください。
- 実際に確認していないログ、エラー、数値、グラフ、スクリーンショットを捏造しないでください。
- 公式資料の記述、今回の実測結果、推測・考察を明確に分離してください。
- 失敗は削除せず `experiment-log.md` と記事のTIPSへ残してください。
- Evidence不足なら `article.md` を完成させず、不足Phaseへ戻してください。

## Fixed environment

- Apple M5 Max / 128GB
- macOS / arm64
- Python 3.14.6
- Pythonはuvで管理
- 常駐サービスはDocker Compose
- MPS / Metal / MLX等Apple Silicon nativeを優先
- CUDA/NVIDIAを前提にしない

Pythonを使用する場合、Agent Repositoryまたは検証対象Projectで定義された環境ポリシーに従い、Python 3.14.6から勝手に変更しないでください。

## Final deliverables

最低限、Evidenceが揃った時点で次を作成してください。

```text
PROJECT_STATE.md
research.md
hypothesis.md
experiment-plan.md
experiment-log.md
analysis.md
discussion.md
article.md
results/quality-review.json
```

`article.md` はQiita掲載可能なMarkdownとし、空ファイルやダミー内容で作成しないでください。

各Phase終了時に `PROJECT_STATE.md` を更新し、終了時に「完了Phase / 未完了Phase / Missing Evidence / 次のアクション」を報告してください。
