from __future__ import annotations

import argparse
import html
import os
import secrets
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import markdown
import mlflow
from mlflow.entities import AssessmentSource
from mlflow.genai import review_queues


QUALITY_QUESTIONS = {
    "experience": "実環境、操作、ログまたは画面、実測、判断、試行錯誤を記事の主題に十分な粒度で追跡できるか。",
    "expertise": "仕組みに加え、解決課題、今回の採用構成、採用理由、適用条件・制約を正確に説明しているか。採用理由はResearch Question、実験制約、実測または一次情報へ結びついているか。",
    "authoritativeness": "主要な主張が一次情報や公式資料で支えられているか。",
    "trustworthiness": "事実、実測、仮説、推測、未確認事項を分離しているか。",
    "originality": "この実験固有の知見から、公式資料だけでは得られない再利用可能な洞察を導いているか。",
    "reproducibility": "条件、バージョン、コード、ロックファイルが揃っているか。",
    "usefulness": "読者の具体的な問いに答え、技術選定基準と実行可能な失敗回避策を再利用できるか。",
    "evidence": "結論を支えるEvidenceが追跡可能な形で存在するか。",
    "clarity": "結果と考察が分離され、仕組みだけでなく、なぜその構成なのかを明瞭に追えるか。",
}

QUALITY_ANCHORS = {
    "experience": "0=実行過程なし / 1=環境・結果はあるが判断や試行錯誤が不足 / 2=操作・観測・判断・修正・再実行を十分に追跡可能",
    "expertise": "0=手順の羅列 / 1=仕組み図または理由の一部だけ / 2=解決課題・採用構成・採用理由・適用条件と制約をEvidenceと結びつけて説明",
    "authoritativeness": "0=重要主張の一次情報なし / 1=一次情報はあるが対応不足 / 2=主張近傍でversion・確認対象まで追跡可能",
    "trustworthiness": "0=事実と推論の混同 / 1=分離はあるが対応不足 / 2=仮説・実測・失敗結果・制約を明示",
    "originality": "0=既存情報の要約 / 1=実機検証のみ / 2=実験・比較・失敗・追加検証から再利用可能な洞察を導出",
    "reproducibility": "0=追試不能 / 1=基本手順のみ / 2=version・lock・入力・コード・判定条件が揃う",
    "usefulness": "0=次の行動へ進めない / 1=回答または一般的TIPSのみ / 2=具体的行動・技術選定基準・失敗回避・利用可能な成果物がある",
    "evidence": "0=中心主張を追跡不能 / 1=Evidenceが遠いまたは内部限定 / 2=主張・記事位置・Source・ログ・成果物を追跡可能",
    "clarity": "0=構造不明 / 1=仕組みはあるが選定意図が不明 / 2=仕組み・なぜその構成か・手順・結果・考察が明瞭",
}


@dataclass(frozen=True)
class ReviewConfig:
    article_path: Path
    tracking_uri: str
    queue_id: str
    trace_id: str
    reviewer_id: str


def render_article(markdown_text: str) -> str:
    return markdown.markdown(
        markdown_text,
        extensions=["fenced_code", "tables", "sane_lists"],
        output_format="html5",
    )


def parse_review(values: dict[str, list[str]]) -> tuple[dict[str, str], dict[str, str]]:
    answers: dict[str, str] = {}
    rationales: dict[str, str] = {}
    for name in QUALITY_QUESTIONS:
        value = values.get(f"score.{name}", [""])[0]
        if value not in {"0", "1", "2"}:
            raise ValueError(f"human_review.{name} は0、1、2のいずれかを選択してください。")
        answers[f"human_review.{name}"] = value
        rationale = values.get(f"rationale.{name}", [""])[0].strip()
        if not rationale:
            raise ValueError(f"human_review.{name}のRationaleを入力してください。")
        rationales[f"human_review.{name}"] = rationale

    publishable = values.get("publishable", [""])[0]
    if publishable not in {"PASS", "FAIL"}:
        raise ValueError("PublishableはPASSまたはFAILを選択してください。")
    answers["human_review.publishable"] = publishable

    critical_issue = values.get("critical_issue", [""])[0].strip()
    if not critical_issue:
        raise ValueError("Critical issueは、問題がなければ「なし」と入力してください。")
    answers["human_review.critical_issue"] = critical_issue
    return answers, rationales


def submit_review(
    config: ReviewConfig,
    answers: dict[str, str],
    rationales: dict[str, str],
) -> None:
    mlflow.set_tracking_uri(config.tracking_uri)
    source = AssessmentSource(source_type="HUMAN", source_id=config.reviewer_id)
    for name, value in answers.items():
        mlflow.log_feedback(
            trace_id=config.trace_id,
            name=name,
            value=value,
            source=source,
            rationale=rationales.get(name),
            metadata={"review_surface": "full_article_review"},
        )
    review_queues.set_review_queue_item_status(
        config.queue_id,
        item_id=config.trace_id,
        status="complete",
        completed_by=config.reviewer_id,
    )


def page_template(article_html: str, config: ReviewConfig, csrf_token: str) -> str:
    question_fields = "\n".join(
        f"""
        <fieldset>
          <legend>human_review.{html.escape(name)}</legend>
          <p>{html.escape(instruction)}</p>
          <p><strong>{html.escape(QUALITY_ANCHORS[name])}</strong></p>
          <div class="score-options">
            {''.join(f'<label><input required type="radio" name="score.{html.escape(name)}" value="{score}"> {score}</label>' for score in ('0', '1', '2'))}
          </div>
          <textarea required name="rationale.{html.escape(name)}" rows="3" placeholder="記事中の該当箇所と、この点数にした理由"></textarea>
        </fieldset>
        """
        for name, instruction in QUALITY_QUESTIONS.items()
    )
    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>全文記事 Human Review</title>
  <style>
    :root {{ color-scheme: light; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; color: #17202a; background: #f4f7fb; }}
    header {{ position: sticky; top: 0; z-index: 10; padding: 12px 24px; background: #fff; border-bottom: 1px solid #dce3ec; }}
    header strong {{ margin-right: 18px; }}
    header code {{ font-size: 12px; }}
    main {{ display: grid; grid-template-columns: minmax(0, 1fr) 420px; gap: 20px; padding: 20px; align-items: start; }}
    article {{ max-width: 1050px; width: 100%; margin: 0 auto; padding: 38px 48px; background: #fff; border-radius: 12px; box-shadow: 0 2px 12px #1f2d3d12; line-height: 1.8; }}
    article h1 {{ font-size: 2.15rem; line-height: 1.3; }}
    article h2 {{ margin-top: 2.5rem; border-bottom: 2px solid #e5eaf0; padding-bottom: .35rem; }}
    article h3 {{ margin-top: 2rem; }}
    article img {{ max-width: 100%; height: auto; }}
    article table {{ border-collapse: collapse; width: 100%; display: block; overflow-x: auto; }}
    article th, article td {{ border: 1px solid #cfd7e3; padding: 8px 10px; }}
    article th {{ background: #f3f6fa; }}
    article pre {{ overflow-x: auto; padding: 16px; border-radius: 8px; background: #17202a; color: #f7f9fb; }}
    article code {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
    aside {{ position: sticky; top: 66px; max-height: calc(100vh - 86px); overflow-y: auto; padding: 18px; background: #fff; border-radius: 12px; box-shadow: 0 2px 12px #1f2d3d18; }}
    aside h2 {{ margin-top: 0; }}
    fieldset {{ margin: 0 0 18px; padding: 14px; border: 1px solid #d8e0ea; border-radius: 8px; }}
    legend {{ font-weight: 700; }}
    fieldset p {{ margin: 6px 0 10px; color: #4a5968; font-size: 14px; }}
    .score-options {{ display: flex; gap: 16px; margin-bottom: 10px; }}
    textarea {{ width: 100%; resize: vertical; }}
    .submit {{ width: 100%; padding: 12px; border: 0; border-radius: 8px; color: #fff; background: #1677ff; font-weight: 700; cursor: pointer; }}
    .warning {{ padding: 10px; border-radius: 8px; background: #fff4d6; color: #6e4b00; font-size: 13px; }}
    @media (max-width: 1050px) {{ main {{ grid-template-columns: 1fr; }} aside {{ position: static; max-height: none; }} article {{ padding: 26px 22px; }} }}
  </style>
</head>
<body>
  <header>
    <strong>全文記事 Human Review</strong>
    Trace <code>{html.escape(config.trace_id)}</code>
  </header>
  <main>
    <article id="article">{article_html}</article>
    <aside>
      <h2>人間評価</h2>
      <p class="warning">記事の末尾「参考資料」まで確認してください。実障害ではエラーメッセージを最重要Evidenceとして確認し、欠落時はReader-visible GateがFAILです。このGateから品質点の上限を機械的に決めず、各項目は記事全体から判断してください。送信結果はMLflow Traceへ記録されます。</p>
      <form method="post" action="/submit">
        <input type="hidden" name="csrf_token" value="{html.escape(csrf_token)}">
        {question_fields}
        <fieldset>
          <legend>human_review.publishable</legend>
          <p>現状の内容を公開候補として受け入れられるか。</p>
          <div class="score-options">
            <label><input required type="radio" name="publishable" value="PASS"> PASS</label>
            <label><input required type="radio" name="publishable" value="FAIL"> FAIL</label>
          </div>
        </fieldset>
        <fieldset>
          <legend>human_review.critical_issue</legend>
          <p>公開を妨げる重大な問題。問題がなければ「なし」。</p>
          <textarea required name="critical_issue" rows="4"></textarea>
        </fieldset>
        <button class="submit" type="submit">MLflowへレビューを送信</button>
      </form>
    </aside>
  </main>
</body>
</html>"""


def success_page(config: ReviewConfig) -> str:
    return f"""<!doctype html><html lang="ja"><meta charset="utf-8">
<title>レビュー送信完了</title><style>body{{font-family:sans-serif;max-width:720px;margin:80px auto;line-height:1.8}}</style>
<h1>レビューを送信しました</h1>
<p>Trace <code>{html.escape(config.trace_id)}</code> に11件のHuman Feedbackを記録し、Review Queueをcompleteにしました。</p>
<p>この画面を閉じて、Codexへ「レビュー送信した」と伝えてください。</p></html>"""


def make_handler(config: ReviewConfig, csrf_token: str):
    class ReviewHandler(BaseHTTPRequestHandler):
        def _send_html(self, body: str, status: HTTPStatus = HTTPStatus.OK) -> None:
            payload = body.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def do_GET(self) -> None:  # noqa: N802
            path = urlparse(self.path).path
            if path == "/health":
                self._send_html("ok")
                return
            if path.startswith("/images/"):
                image = (config.article_path.parent / path.lstrip("/")).resolve()
                images_root = (config.article_path.parent / "images").resolve()
                if images_root not in image.parents or not image.is_file():
                    self.send_error(HTTPStatus.NOT_FOUND)
                    return
                payload = image.read_bytes()
                content_type = "image/png" if image.suffix.lower() == ".png" else "image/jpeg"
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                return
            if path != "/":
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            article = config.article_path.read_text(encoding="utf-8")
            self._send_html(page_template(render_article(article), config, csrf_token))

        def do_POST(self) -> None:  # noqa: N802
            if urlparse(self.path).path != "/submit":
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            try:
                size = int(self.headers.get("Content-Length", "0"))
                values = parse_qs(self.rfile.read(size).decode("utf-8"), keep_blank_values=True)
                if values.get("csrf_token", [""])[0] != csrf_token:
                    raise ValueError("送信tokenが一致しません。画面を再読み込みしてください。")
                answers, rationales = parse_review(values)
                submit_review(config, answers, rationales)
            except Exception as exc:
                self._send_html(
                    f"<h1>送信できませんでした</h1><pre>{html.escape(str(exc))}</pre><p><a href='/'>評価画面へ戻る</a></p>",
                    HTTPStatus.BAD_REQUEST,
                )
                return
            self._send_html(success_page(config))

        def log_message(self, format: str, *args: object) -> None:
            print(f"review-ui {self.address_string()} {format % args}")

    return ReviewHandler


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--article", type=Path, default=Path(os.environ.get("ARTICLE_PATH", "/article/article.md")))
    parser.add_argument("--tracking-uri", default=os.environ.get("MLFLOW_TRACKING_URI", "http://mlflow:5000"))
    parser.add_argument("--queue-id", default=os.environ.get("REVIEW_QUEUE_ID", ""))
    parser.add_argument("--trace-id", default=os.environ.get("REVIEW_TRACE_ID", ""))
    parser.add_argument("--reviewer-id", default=os.environ.get("REVIEWER_ID", "tera"))
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=5051)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.article.is_file():
        raise SystemExit(f"article not found: {args.article}")
    if not args.queue_id or not args.trace_id:
        raise SystemExit("REVIEW_QUEUE_ID and REVIEW_TRACE_ID are required")
    config = ReviewConfig(
        article_path=args.article.resolve(),
        tracking_uri=args.tracking_uri,
        queue_id=args.queue_id,
        trace_id=args.trace_id,
        reviewer_id=args.reviewer_id,
    )
    server = ThreadingHTTPServer((args.host, args.port), make_handler(config, secrets.token_urlsafe(32)))
    print(f"full_article_review_url=http://127.0.0.1:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
