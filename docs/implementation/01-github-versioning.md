# STEP 1 — GitHubバージョニング

## Goal

「どのAgent / Skill / Resourceの状態でこの記事・評価結果が生成されたか」をGit commitから必ず追跡できる状態にする。

---

# 0. 必須: uv / Python環境を先に作る

Git操作そのものにPythonは不要だが、このSTEPではvalidatorとversion snapshotを実行するため、**GitHub設定より先にプロジェクト標準Python環境を完成させる。**

詳細は `00-environment-bootstrap.md` をSource of Truthとする。

repository rootで実行する。

```bash
cd technical-blog-work-agent
```

## 0-1. uvを確認

```bash
uv --version
```

未導入の場合のみ:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

PATH反映後に再確認する。

```bash
uv --version
```

## 0-2. Python 3.14.6をuvでインストール

```bash
uv python install 3.14.6
```

確認:

```bash
uv python find 3.14.6
```

## 0-3. Python 3.14.6をprojectへ固定

```bash
uv python pin 3.14.6
```

確認:

```bash
cat .python-version
```

期待値:

```text
3.14.6
```

`pyproject.toml` も次のままであることを確認する。

```toml
requires-python = "==3.14.6"
```

## 0-4. `.venv` と依存関係を作る

```bash
uv sync
```

確認:

```bash
ls -ld .venv
ls -l uv.lock
```

## 0-5. `.venv` をactivate

```bash
source .venv/bin/activate
```

必ず確認する。

```bash
which python
python --version
```

期待:

```text
.../technical-blog-work-agent/.venv/bin/python
Python 3.14.6
```

**Python 3.14.6でなければSTEP 1へ進まない。**

## 0-6. Agent package validator

activate済みshellで:

```bash
python tools/validate_skills.py
```

---

# 1. Repositoryを初期化

既にGit管理されている場合は不要。

```bash
git init
git branch -M main
```

最初のcommit前に状態を確認する。

```bash
git status
```

初回commit:

```bash
git add .
git commit -m "chore: initialize technical blog work agent"
```

GitHub repositoryを作成した後:

```bash
git remote add origin <YOUR_GITHUB_REPOSITORY>
git push -u origin main
```

---

# 2. Versionの正本を確認

MVPでは以下を使用する。

```text
MANIFEST.json -> Agent release version
git commit     -> exact implementation state
Git tag        -> release point
```

SkillごとのSemantic VersionはMVPでは増やさず、Agent release version + exact commitで追跡する。

---

# 3. Version snapshotを取得

この時点でも `.venv` はactivate済みであること。

```bash
python --version
```

期待:

```text
Python 3.14.6
```

Version snapshot:

```bash
python tools/version_snapshot.py \
  --output results/version-snapshot.json
```

出力例:

```json
{
  "agent_version": "0.3.1",
  "git_commit": "...",
  "git_branch": "main",
  "git_dirty": false,
  "python_version": "3.14.6",
  "python_executable": ".../.venv/bin/python",
  "uv_version": "uv ..."
}
```

正式なbaseline評価は `git_dirty=false` を原則とする。

---

# 4. Branch運用

Agent改善は直接mainへ積み上げず、変更単位でbranchを作る。

```bash
git switch -c feature/add-offline-evaluation
```

変更後:

```bash
python tools/validate_skills.py
git status
git diff
```

問題がなければcommitする。

```bash
git add .
git commit -m "feat: add offline evaluation workflow"
```

---

# 5. Release tag

固定Datasetで評価し、採用するversionにtagを付ける。

```bash
git tag -a v0.3.1 -m "Content MLOps baseline"
git push origin main --tags
```

GitHub Releaseも同じtagから作成する。

---

# 6. Branch protection

GitHubのmain branchには、運用が安定したら以下を設定する。

- Pull Request経由でmerge
- validator / evaluation status checkをrequire
- force push禁止
- branch deletion禁止

最初からCIを複雑化せず、STEP 1ではlocal validatorを必須としてよい。

---

# 7. PROJECT_STATE.mdへ記録

記事生成開始時または評価前に以下を保存する。

```text
Article ID
Agent version
Git commit
Git branch
Git dirty
Python version
uv version
```

Python versionは必ず実環境から取得する。

```bash
python --version
uv --version
```

---

# 新しいshellを開いた場合

Pythonを再installする必要はないが、`.venv` のactivateは必要。

```bash
cd technical-blog-work-agent
source .venv/bin/activate
python --version
```

3.14.6であることを確認してから作業を再開する。

---

# Completion check

```text
□ uvが導入済み
□ uv python install 3.14.6を実行済み
□ .python-versionが3.14.6
□ pyproject.toml requires-python == 3.14.6
□ uv sync済み
□ .venvが存在
□ source .venv/bin/activate済み
□ python --version == 3.14.6
□ GitHubがSource of Truth
□ mainが存在
□ MANIFEST versionがある
□ exact commitを取得可能
□ formal baselineはclean commit
□ release candidateにGit tagを付けられる
□ PROJECT_STATE.mdからcommitへ遡れる
```

## Official references

- uv installation: https://docs.astral.sh/uv/getting-started/installation/
- uv Python management: https://docs.astral.sh/uv/guides/install-python/
- uv project workflow / activation: https://docs.astral.sh/uv/guides/projects/
- GitHub Releases: https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository
- Protected branches: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches
- MLflow Git version tracking: https://mlflow.org/docs/latest/genai/version-tracking/track-application-versions-with-mlflow/
