---
name: visual-evidence
description: 技術ブログに必要なスクリーンショット、GUI状態、グラフ、ログ画面などの視覚証拠を計画・取得・配置指示化するときに使う。
---

# Visual Evidence

## Purpose

「画像を入れること」が目的ではなく、記事の主張を読者が視覚的に確認できる証拠を用意する。

## Inputs

- experiment evidence
- article outline
- GUI/Web画面
- graph candidates


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

1. 画像が本当に理解または証拠に必要な箇所を選ぶ。
2. 各画像について「何を証明するか」を1文で定義する。
3. コンポーネントが3つ以上、またはデータが複数工程を通る場合は、仕組みとデータフローの図を用意する。
4. 比較可能な数値が複数条件にある場合はグラフを作る。作らない場合は理由と代替表を記録する。
5. 可能なら実際の画面を取得する。
6. APIキー、メール、ユーザー名、内部URL、秘密情報を確認しマスクする。
7. グラフではタイトル、X軸、Y軸、単位、比較条件、凡例が分かるようにし、生成コードがある場合は `scripts/` に保存する。
8. 画像ファイル名を意味のある名前にする。
9. 記事上の挿入位置を指定する。
10. 取得不能なら、架空画像を生成せず具体的な撮影指示を置く。

## Output

```markdown
## Visual EV-01
- Article section:
- Screen:
- Purpose:
- Highlight:
- Sensitive data check:
- File:
- Alt text:
```

取得不能なら:

```markdown
<!-- SCREENSHOT:
画面:
操作:
目的:
注目箇所:
マスク対象:
-->
```

## Completion checks

- 装飾だけの画像を増やしていない。
- 画像だけに重要情報を依存していない。
- 秘密情報が写っていない。
- 各図が答える読者の問いと、本文中の解釈がある。

## Canonical output

画像は原則 `images/` に保存し、Evidence IDまたは記事節との対応を残す。

## Project state update

必要なVisual Evidenceの取得または具体的な撮影指示が揃ったら `PROJECT_STATE.md` を更新する。
