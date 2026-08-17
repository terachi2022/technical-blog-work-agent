# STEP 1 — GitHubバージョニング

## Goal

「どのAgent / Skill / Resourceの状態でこの記事・評価結果が生成されたか」をGit commitから必ず追跡できる状態にする。

## 1. Repositoryを初期化

既にGit管理されている場合は不要。

```bash
git init
git branch -M main
```

GitHub repositoryを作成後:

```bash
git remote add origin <YOUR_GITHUB_REPOSITORY>
git push -u origin main
```

## 2. Versionの正本を確認

MVPでは以下を使用する。

```text
MANIFEST.json -> version
git commit     -> exact implementation state
Git tag        -> release point
```

SkillごとのSemantic Versionはまだ作らない。

## 3. Version snapshotを取得

```bash
uv run python tools/version_snapshot.py \
  --output results/version-snapshot.json
```

出力例:

```json
{
  "agent_version": "0.3.0",
  "git_commit": "...",
  "git_branch": "main",
  "git_dirty": false
}
```

正式なbaseline評価は `git_dirty=false` を原則とする。

## 4. Branch運用

Agent改善は直接mainへ積み上げず、変更単位でbranchを作る。

```bash
git switch -c feature/add-offline-evaluation
```

変更後:

```bash
uv run python tools/validate_skills.py
git status
git diff
```

問題がなければcommitする。

```bash
git add .
git commit -m "feat: add offline evaluation workflow"
```

## 5. Release tag

固定Datasetで評価し、採用するversionにtagを付ける。

```bash
git tag -a v0.3.0 -m "Content MLOps baseline"
git push origin main --tags
```

GitHub Releaseも同じtagから作成する。

## 6. Branch protection

GitHubのmain branchには、運用が安定したら以下を設定する。

- Pull Request経由でmerge
- validator / evaluation status checkをrequire
- force push禁止
- branch deletion禁止

最初からCIを複雑化せず、STEP 1ではlocal validatorを必須にしてよい。

## 7. PROJECT_STATE.mdへ記録

記事生成開始時または評価前に以下を保存する。

```text
Article ID
Agent version
Git commit
Git branch
Git dirty
```

## Completion check

```text
□ GitHubがSource of Truth
□ mainが存在
□ MANIFEST versionがある
□ exact commitを取得可能
□ formal baselineはclean commit
□ release candidateにGit tagを付けられる
□ PROJECT_STATE.mdからcommitへ遡れる
```

## Official references

- GitHub Releases: https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository
- Protected branches: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches
- MLflow Git version tracking: https://mlflow.org/docs/latest/genai/version-tracking/track-application-versions-with-mlflow/
