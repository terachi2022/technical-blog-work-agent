from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import mlflow
from mlflow.genai.datasets import create_dataset, search_datasets


def read_jsonl(path: Path) -> list[dict]:
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, type=Path)
    parser.add_argument("--name", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--experiment", default="technical-blog-agent-offline-eval")
    parser.add_argument(
        "--tracking-uri",
        default=os.environ.get("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000"),
    )
    args = parser.parse_args()

    mlflow.set_tracking_uri(args.tracking_uri)
    experiment = mlflow.set_experiment(args.experiment)

    existing = search_datasets(
        experiment_ids=[experiment.experiment_id],
        filter_string=f"name = '{args.name}'",
        max_results=10,
    )
    if existing:
        dataset = existing[0]
    else:
        dataset = create_dataset(
            name=args.name,
            experiment_id=[experiment.experiment_id],
            tags={"version": args.version, "status": "active", "source": "git"},
        )

    records = read_jsonl(args.file)
    dataset.merge_records(records)
    print(f"dataset_id={dataset.dataset_id}")
    print(f"records={len(dataset.to_df())}")


if __name__ == "__main__":
    main()
