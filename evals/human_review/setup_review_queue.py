from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import mlflow
from mlflow import MlflowClient
from mlflow.genai import label_schemas, review_queues
from mlflow.genai.label_schemas import InputCategorical, InputPassFail, InputText


QUALITY_QUESTIONS = {
    "experience": "実環境、操作、ログまたは画面、実測、判断、試行錯誤を記事の主題に十分な粒度で追跡できるか。",
    "expertise": "仕組みに加え、解決課題、今回の採用構成、採用理由、適用条件・制約を正確に説明しているか。採用理由はResearch Question、実験制約、実測または一次情報へ結びついているか。",
    "authoritativeness": "主要な主張が一次情報や公式資料で支えられているか。",
    "trustworthiness": "事実、実測、仮説、推測、未確認事項を分離しているか。",
    "originality": "この実験固有の知見から、公式資料だけでは得られない再利用可能な洞察を導いているか。",
    "reproducibility": "条件、バージョン、コード、ロックファイルが揃っているか。",
    "usefulness": "読者の問いに答え、技術選定基準と実行可能な失敗回避策を再利用できるか。",
    "evidence": "結論を支えるEvidenceが追跡可能な形で存在するか。",
    "clarity": "中核技術の定義、解決する課題、今回なぜ必要かが明瞭で、結果と考察、仕組み、構成理由を追えるか。",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--tracking-uri",
        default=os.environ.get("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000"),
    )
    parser.add_argument("--experiment", default="technical-blog-agent-offline-eval")
    parser.add_argument(
        "--queue-name", default="technical-blog-golden-v1-human-review"
    )
    parser.add_argument(
        "--trace-id",
        help="Trace to add. If omitted, use the newest trace in the experiment.",
    )
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def latest_trace_id(experiment_id: str) -> str:
    traces = mlflow.search_traces(locations=[experiment_id], max_results=1)
    if traces.empty:
        raise SystemExit(f"no trace found in experiment {experiment_id}")
    return str(traces.iloc[0]["trace_id"])


def create_or_update_schemas(experiment_id: str) -> list[Any]:
    existing = {
        schema.name: schema
        for schema in label_schemas.list_label_schemas(
            experiment_id=experiment_id, max_results=100
        )
    }

    def upsert(
        *,
        name: str,
        schema_type: str,
        schema_input: Any,
        instruction: str,
        enable_comment: bool = False,
    ) -> Any:
        if current := existing.get(name):
            return label_schemas.update_label_schema(
                current.schema_id,
                instruction=instruction,
                enable_comment=enable_comment,
                input=schema_input,
            )
        return label_schemas.create_label_schema(
            name=name,
            type=schema_type,
            input=schema_input,
            instruction=instruction,
            enable_comment=enable_comment,
            experiment_id=experiment_id,
        )

    schemas = []
    for name, instruction in QUALITY_QUESTIONS.items():
        schemas.append(
            upsert(
                name=f"human_review.{name}",
                schema_type="feedback",
                schema_input=InputCategorical(options=["0", "1", "2"]),
                instruction=(
                    instruction
                    + " 0=不十分、1=一部満たす、2=十分。必ず記事とEvidenceを確認して選択する。"
                ),
                enable_comment=True,
            )
        )
    schemas.append(
        upsert(
            name="human_review.publishable",
            schema_type="feedback",
            schema_input=InputPassFail(positive_label="PASS", negative_label="FAIL"),
            instruction="現状の内容を公開候補として受け入れられるか。重大な問題があればFAIL。",
            enable_comment=True,
        )
    )
    schemas.append(
        upsert(
            name="human_review.critical_issue",
            schema_type="feedback",
            schema_input=InputText(max_length=4000),
            instruction="公開を妨げる重大な問題を記載する。問題がなければ「なし」と入力する。",
        )
    )
    return schemas


def create_or_update_queue(
    experiment_id: str, queue_name: str, schema_ids: list[str]
):
    existing = next(
        (
            queue
            for queue in review_queues.list_review_queues(
                experiment_id=experiment_id, max_results=100
            )
            if queue.name == queue_name
        ),
        None,
    )
    if existing:
        if set(existing.schema_ids) == set(schema_ids):
            return existing
        return review_queues.update_review_queue(
            existing.queue_id, users=[], schema_ids=schema_ids
        )
    return review_queues.create_review_queue(
        queue_name,
        queue_type="custom",
        users=[],
        schema_ids=schema_ids,
        experiment_id=experiment_id,
    )


def add_trace_once(queue_id: str, trace_id: str) -> None:
    existing_ids = {
        item.item_id
        for item in review_queues.list_review_queue_items(
            queue_id, max_results=1000
        )
    }
    if trace_id not in existing_ids:
        review_queues.add_items_to_review_queue(queue_id, item_ids=[trace_id])


def main() -> None:
    args = parse_args()
    mlflow.set_tracking_uri(args.tracking_uri)
    client = MlflowClient()
    experiment = client.get_experiment_by_name(args.experiment)
    if experiment is None:
        raise SystemExit(f"experiment not found: {args.experiment}")

    trace_id = args.trace_id or latest_trace_id(experiment.experiment_id)
    schemas = create_or_update_schemas(experiment.experiment_id)
    queue = create_or_update_queue(
        experiment.experiment_id,
        args.queue_name,
        [schema.schema_id for schema in schemas],
    )
    add_trace_once(queue.queue_id, trace_id)
    items = list(
        review_queues.list_review_queue_items(queue.queue_id, max_results=1000)
    )

    result = {
        "experiment_id": experiment.experiment_id,
        "experiment_name": experiment.name,
        "queue_id": queue.queue_id,
        "queue_name": queue.name,
        "queue_type": str(queue.queue_type),
        "schema_count": len(schemas),
        "schema_names": [schema.name for schema in schemas],
        "trace_id": trace_id,
        "queue_item_count": len(items),
        "queue_item_status": next(
            (str(item.status) for item in items if item.item_id == trace_id), None
        ),
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
