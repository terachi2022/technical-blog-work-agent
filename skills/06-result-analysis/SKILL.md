---
name: result-analysis
description: 技術実験の生データを整理し、仮説ごとの支持・棄却・不確定を判定し、結果と解釈を分離して分析するときに使う。
---

# Result Analysis

## Purpose

実験ログを「見た感じ」で評価せず、事前の判定基準と照合して分析する。

## Inputs

- experiment plan
- hypothesis list
- experiment evidence


## 実行環境の固定条件

このSkillでローカル検証を行う場合、以下を既定条件として扱う。

- ハードウェア: Apple M5 Max / 128GB RAM
- OS: macOS
- Python: 3.14.6
- Pythonパッケージ管理: `uv`
- Python環境: `uv python install 3.14.6` / `uv python pin 3.14.6` / `uv sync` 後、`source .venv/bin/activate` を標準とする
- 仮想環境・依存関係: `uv` で管理する
- 常駐サービス、DB、Web UI、補助サーバーが必要な場合: `docker compose` で構成する
- Apple SiliconでGPUアクセラレーションが使える場合: MPS/Metalを優先する
- CUDA/NVIDIA GPUを前提にしない
- シェル例はmacOS標準のzshで実行可能な形を優先する

固定条件で実行不能な場合は、勝手にPython版・OS・ハードウェア条件を変更しない。
「非互換・未対応」という検証結果として記録し、原因、根拠、代替案を提示する。


## Workflow

1. 証拠の欠落を確認する。
2. 各仮説と対応する実験結果を紐づける。
3. 実測値を表へ整理する。
4. 必要なら差分、比率、平均、中央値、最大値、最小値、ばらつき等を計算する。
5. 事前定義のPass/Fail基準と比較する。
6. 仮説を `SUPPORTED / REJECTED / INCONCLUSIVE` に分類する。
7. 観測事実と解釈を別段落にする。
8. 外れ値、測定誤差、交絡要因を評価する。
9. 数値比較が読者理解に有効ならグラフ化し、タイトル、X軸、Y軸、単位、比較条件、凡例を明示する。再生成コードは原則 `scripts/`、画像は `images/` に保存する。
10. 追加実験が必要な論点を列挙する。

## Output

```markdown
## H1

### Observed facts

### Comparison with criterion

### Decision
SUPPORTED / REJECTED / INCONCLUSIVE

### Limitations

### Additional evidence needed
```

## Completion checks

- 結果と考察を混ぜていない。
- 事前基準を都合よく変更していない。
- 証拠のない因果関係を断定していない。

## Canonical output

分析結果は原則 `analysis.md`、処理済みデータは `data/processed/` または `results/` に保存する。

## Project state update

完了時に `PROJECT_STATE.md` の Results / Analysis と各仮説状態を更新する。
