# 共通前提 — uv / Python 3.14.6 環境の初期化

## Purpose

STEP 1〜4を始める前に、今回の固定環境を `uv` で再現可能な状態にする。

この手順は**新しいMac / 新しいclone / `.venv` を削除した後に一度実施**する。
新しいターミナルを開いた場合は、少なくとも `.venv` のactivateをやり直す。

## Fixed environment

```text
Hardware        : Apple M5 Max
Memory          : 128 GB
Architecture    : Apple Silicon / arm64
OS              : macOS（実バージョンを取得）
Python          : 3.14.6
Package Manager : uv
Virtual Env     : .venv
Services        : Docker Compose
```

## 1. Project rootへ移動

```bash
cd technical-blog-work-agent
```

以降のコマンドはrepository rootで実行する。

## 2. uvの存在を確認

```bash
uv --version
```

`uv` が未導入の場合のみ、Astral公式installerを使用する。

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

installer実行後は新しいshellを開くか、installerが案内するPATH反映手順を実行してから再確認する。

```bash
uv --version
```

## 3. Python 3.14.6をuvでインストール

**システムPythonやHomebrew Pythonを今回の実行Pythonとして流用しない。**

```bash
uv python install 3.14.6
```

確認:

```bash
uv python find 3.14.6
```

## 4. ProjectのPythonを3.14.6へ固定

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

また、`pyproject.toml` は以下を維持する。

```toml
requires-python = "==3.14.6"
```

`.python-version` と `pyproject.toml` の双方で意図しないPython変更を防ぐ。

## 5. 依存関係を同期し `.venv` を作成

```bash
uv sync
```

`uv sync` により、project environment `.venv` と `uv.lock` を作成・同期する。

確認:

```bash
ls -ld .venv
ls -l uv.lock
```

## 6. `.venv` をactivate

macOS標準のzshでは:

```bash
source .venv/bin/activate
```

activate後に以下を確認する。

```bash
which python
python --version
```

期待例:

```text
.../technical-blog-work-agent/.venv/bin/python
Python 3.14.6
```

`python --version` が3.14.6でなければ、以降へ進まない。

## 7. uv / project状態を確認

```bash
uv --version
uv python find 3.14.6
python --version
```

必要なら環境情報も記録する。

```bash
sw_vers
uname -m
system_profiler SPHardwareDataType
```

## 8. Local validatorを実行

activate済みshellで:

```bash
python tools/validate_skills.py
```

期待結果:

```text
OK: 11 skills, package policies, and Content MLOps files validated
```

## Daily / new shell workflow

Python自体を毎回再installする必要はない。
新しいshellではrepository rootへ移動してactivateする。

```bash
cd technical-blog-work-agent
source .venv/bin/activate
python --version
```

依存関係や `uv.lock` が更新された場合は:

```bash
uv sync
source .venv/bin/activate
```

## Rule

本プロジェクトの人間向け手順では、Pythonコマンドを提示する前に、少なくとも以下が成立していることを前提とする。

```text
uv python install 3.14.6 済み
uv python pin 3.14.6 済み
uv sync 済み
source .venv/bin/activate 済み
python --version == 3.14.6
```

`uv run` はuvとして正しい実行方法だが、**このプロジェクトの手順書では環境が見える状態を優先し、明示的activateを標準手順とする。**

## Official references

- uv installation: https://docs.astral.sh/uv/getting-started/installation/
- Installing Python: https://docs.astral.sh/uv/guides/install-python/
- Python versions: https://docs.astral.sh/uv/concepts/python-versions/
- Project environments / activation: https://docs.astral.sh/uv/guides/projects/
- Locking and syncing: https://docs.astral.sh/uv/concepts/projects/sync/
