# Environment Policy

## Fixed local environment

ローカル検証では以下を既定条件として固定する。

```text
Hardware        : Apple Mac
SoC             : Apple M5 Max
Memory          : 128 GB
Architecture    : Apple Silicon / arm64
OS              : macOS（具体バージョンは実機から取得）
Python          : 3.14.6
Package Manager : uv
Services        : Docker Compose
```

未確認のmacOS、Docker、uv、ライブラリのバージョンを推測しない。

## Environment capture

可能な範囲で実値を記録する。

```bash
sw_vers
uname -a
uname -m
system_profiler SPHardwareDataType
uv --version
uv run python --version
docker version
docker compose version
```

Pythonを使わない場合、Python関連項目は `NOT_APPLICABLE` としてよい。
Dockerを使わない場合も同様。

## Python

Pythonを使う検証では原則:

```bash
uv init
uv python pin 3.14.6
uv add <package>
uv sync
uv run python <script.py>
```

既存プロジェクトでは `uv sync` と `uv run` を使う。
`pyproject.toml` と `uv.lock` を再現性の根拠として残す。

理由なく以下へ変更しない。

```text
pip install
pipenv
poetry
conda
mamba
virtualenv
python -m venv
```

公式手順が `pip install` でも、互換性がある限りuvへ置換する。
Python 3.14.6非対応が疑われる場合は公式対応状況を調査し、非互換性を結果として記録する。
別Pythonへの変更は勝手に行わず、必要性・影響・代替案を提示する。

## Docker Compose

DB、Web UI、監視ツール、API、MLflow Server等の常駐サービスは原則Docker Composeで構築する。
新規ファイル名は `compose.yaml` を優先する。

```bash
docker compose up -d
docker compose ps
docker compose logs
docker compose down
```

理由なく単発 `docker run` を標準手順にしない。
PostgreSQL、MySQL/MariaDB、Redis等を検証目的だけでmacOSへ常駐インストールしない。

## Apple Silicon / container architecture

- `linux/arm64` またはmulti-archイメージを優先する。
- x86_64専用イメージしかない場合は、Rosetta / QEMU等のエミュレーション有無を明記する。
- エミュレーションが性能へ影響する可能性を記録する。
- x86_64エミュレーション結果をApple Siliconネイティブ性能として扱わない。

## ML / GPU

CUDA/NVIDIAを既定にしない。候補は実際に対応状況を確認して選ぶ。

優先順の目安:

```text
Apple Silicon native
→ MPS / Metal / MLX / framework-native backend
→ CPU
→ x86_64 emulation（必要な場合のみ）
```

PyTorchでMPSを使う場合は必要に応じて:

```python
import torch
print(torch.backends.mps.is_available())
print(torch.backends.mps.is_built())
```

CUDA前提の公式チュートリアルをM5 Max向けに置換するときは、記事と実験記録に次を残す。

```text
公式チュートリアルの該当手順
→ 公式の前提
→ M5 Maxで使えない点
→ M5 Max向け置換
→ 置換による差異・制約
```

## Do not pollute the host

優先順位:

```text
1. uvによるプロジェクト分離
2. Docker Compose
3. プロジェクト配下の設定
4. ホストOSへの直接変更（必要時のみ）
```

理由なくHomebrewパッケージを大量追加したり、システムPython・macOS設定・常駐Daemonを変更しない。
ホスト変更が必要なら、その理由とロールバック方法を記録する。

## Compatibility failure

固定条件で実行不能な場合は環境を黙って変更しない。

記録する:

- 非対応であること
- 根拠となる公式情報または実測エラー
- 影響
- 代替案
- 環境変更によって検証の意味がどう変わるか

## Environment change approval

以下を都合のよい回避策として黙って変更しない。

- Python 3.14.6から別バージョンへの変更
- uvから別パッケージ管理方式への変更
- Docker Composeから別サービス起動方式への変更
- Apple Silicon / arm64からx86_64環境への変更
- macOSからLinux VM等への変更

変更が必要な場合は、必要理由、公式サポート状況、検証結果への影響、代替案を示す。

