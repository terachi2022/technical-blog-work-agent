# MLflow local service

M5 Max上のMVP Offline Evaluation用MLflow Tracking Server。

## Preflight

```bash
docker buildx imagetools inspect ghcr.io/mlflow/mlflow:v3.15.1
```

`linux/arm64` を確認する。

## Start

```bash
docker compose up -d
docker compose ps
```

UI:

```text
http://127.0.0.1:5000
```

長文記事のHuman ReviewはMLflow標準previewではなく、`human-review` profileの全文Review UIを使う。起動方法は `evals/human_review/README.md` を参照する。

```text
http://127.0.0.1:5051
```

## Stop

```bash
docker compose down
```

データを消す場合のみ:

```bash
docker compose down -v
```

`-v` はMLflow DB / artifactsを削除するため、通常停止では使わない。

このMVPはSQLite backendを使う。Evaluation DatasetにはSQL backendが必要なため、FileStoreではなくSQLiteを使用する。
