# Technical Article Review Rubric

公開判定は `PASS / WARN / BLOCK`、品質スコアは9項目を `0 / 1 / 2` で評価する。
両方を使う。

## Publication gate

### Evidence

- 主要主張に根拠がある
- 実測値を捏造していない
- 公式仕様と実測を区別している
- 参照URLがある
- Evidence Gateを通過している

### Reproducibility

- 環境が書かれている
- バージョンがある
- コマンドが省略されていない
- 入力と出力が対応する
- 必要なファイルが記事内またはプロジェクトに存在する
- Python利用時は `pyproject.toml` / `uv.lock` で再現可能
- サービス利用時はDocker Composeで再現可能

### Reasoning

- Research Questionがある
- 仮説が明示されている
- 検証方法が仮説に対応する
- 結果と考察が分離されている
- 結果から言えないことを断定していない
- 追加検証の必要性を評価している

### Reader experience

- 初学者が目的を理解できる
- 手順だけでなく理由がある
- 長大なログをそのまま貼っていない
- 必要な図やスクリーンショットがある
- TL;DRで結論と検証環境が分かる

### Google / originality

- Google公式方針を扱う場合、最新のGoogle Search Centralを確認している
- 公式ドキュメントの単なる言い換えではない
- 実機検証・実測値・失敗・比較・環境固有知見など独自価値がある
- 検索順位やAI引用を保証していない

## Original Value Gate

最低限、以下のうち記事テーマに適した独自価値が1つ以上あり、中心的主張と結びついていること。

- 実機検証
- 実測値
- 比較結果
- Apple M5 Max固有の知見
- Python 3.14.6固有の知見
- uvへの置換・互換性知見
- Docker Composeによる再現構成
- 実際に発生したエラー
- 失敗した方法と解決過程
- 公式資料間の矛盾を実験で確認した結果

「公式ドキュメントを読むだけでは得られない情報は何か」を1文で答えられなければ `WARN`、記事の中心が転載・要約だけなら `BLOCK`。

## Publication block conditions

以下が1つでもあれば `BLOCK`。

- 架空の実験結果
- 出典のない重要仕様
- 再現不能な主要手順
- 認証情報・秘密情報の露出
- 破壊的操作に注意書きがない
- 未検証事項を成功済みとして記述
- Evidence Gate未通過
- 重要な結論を支えるEvidenceが欠落

## E-E-A-T / Quality score

各項目を評価する。

```text
0 = 不十分
1 = 一部満たす
2 = 十分
```

| Criterion | 0-2 | What to inspect |
|---|---:|---|
| Experience | | 実環境、コマンド、失敗、スクリーンショット、実測値 |
| Expertise | | 仕組み、理由、制約、適用範囲の説明 |
| Authoritativeness | | 一次情報、公式資料、バージョン・確認日 |
| Trustworthiness | | 事実/推論/未確認の分離、捏造なし |
| Originality | | 公式資料だけでは得られない独自価値 |
| Reproducibility | | 環境、依存関係、コマンド、データ |
| Usefulness | | 読者の課題解決・判断に結びつくか |
| Evidence | | Source / Evidenceへの追跡性 |
| Clarity | | 初学者可読性、構造、図表 |

**Total: /18**

低評価項目には必ず以下を出す。

- 不足しているEvidence
- 改善方法
- 追加調査
- 追加検証

点数を上げるために証拠を捏造してはならない。
