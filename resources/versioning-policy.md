# Versioning Policy

## Source of Truth

Agent / Skills / Resources / Scorers / Evaluation Dataset原本はGitHubをSource of Truthとする。

MLflowはGitの代替ではなく、Git commitと評価結果を関連付ける。

## MVP version unit

MVPではSkillごとに独立Semantic Versionを持たせない。

以下の2つを必須識別子とする。

- `agent_version`: Agentパッケージ全体のSemantic Version
- `git_commit`: 実際に評価・生成に使用したcommit hash

Skill単位の差分はcommitから追跡する。
運用上必要になった時点で個別Skill versionを追加する。

## Semantic Versioning rule

例: `0.3.0`

- PATCH: 誤字、説明改善、評価基準を変えない小修正
- MINOR: Skill / Resource / Scorerの動作変更、評価機能追加
- MAJOR: Phase構造や互換性を壊す変更

Git tagは `v0.3.0` の形式を標準とする。

## Required metadata per article/evaluation

最低限以下を保存する。

```text
article_id
agent_version
git_commit
git_branch
git_dirty
mlflow_experiment
mlflow_run_id
evaluation_dataset_name
evaluation_dataset_version
model_or_runtime
created_at
```

`git_dirty=true` の評価は探索用途には使用できるが、正式なbaseline / release candidateとして扱わない。

## Article ID

推奨形式:

```text
YYYYMMDD-<short-slug>-NN
```

例:

```text
20260818-mlflow-m5max-001
```

## Release flow

```text
feature branch
  ↓
local validation
  ↓
fixed evaluation dataset
  ↓
quality comparison
  ↓
review
  ↓
main merge
  ↓
Git tag / GitHub Release
```

## MLflow Git integration

MLflowのGit-based application version trackingを使用する場合でも、GitHubを正本とする。

MLflowの `mlflow.genai.enable_git_model_versioning()` はGit branch / commit / dirty stateを追跡できるが、experimental featureとして扱い、明示的なrun tagsにも重要識別子を残す。

Official reference:
https://mlflow.org/docs/latest/genai/version-tracking/track-application-versions-with-mlflow/
