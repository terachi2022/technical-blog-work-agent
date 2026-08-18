# Human Review Display Policy

## Goal

人間が記事の内容を実際に読める状態を作ってから評価を依頼する。
Traceに全文が保存されていることと、Review画面で全文を読めることを別々に検証する。

## Trace representation

`article.md` はMLflow Traceへ、OpenAI互換のassistant messageとして全文を保存する。

```json
{
  "role": "assistant",
  "content": "# 記事タイトル\n\n## TL;DR\n...\n\n## 参考資料\n..."
}
```

実装では次を満たす。

- traced spanへ `mlflow.message.format=openai` を設定する
- `mlflow.chat.messages` にuser messageとassistant messageを保存する
- assistant messageの`content`へ`article.md`のMarkdown全文を改変せず入れる
- outputもOpenAI互換`chat.completion`形式にし、同じassistant messageを返す
- 記事をescaped JSON文字列、Python dictの文字列表現、先頭だけのpreviewとして保存しない

Trace表示の合格条件:

- `View full trace`で記事タイトルがMarkdown見出しとして表示される
- 箇条書き、表、コードブロックが生のJSONではなくMarkdownとして読める
- 末尾見出し `参考資料` とその内容が存在する
- Trace内の全文と評価対象`article.md`が一致する

## Review surface routing

MLflow OSS標準Review本文欄の`request_preview` / `response_preview`だけで長文記事を評価しない。previewは途中省略され得るため、Traceに全文があってもHuman Reviewの全文表示を保証しない。

長文記事はRepositoryの全文Review UIへ振り分ける。

```text
MLflow Trace
  ├─ View full trace: 全文Markdownの保存・表示を確認
  └─ Full Article Review UI: 全文を読みながら11問を評価
```

## Human handoff gate

人間へ評価を依頼する前に、実際に起動した画面で次を確認する。

- 記事の最初の見出しが表示される
- 記事の末尾見出し `参考資料` が表示される
- 途中が省略記号やpreviewへ置換されていない
- 全画像URLがHTTP 200で、本文中に表示される
- Experience〜Clarityの9問がある
- 各9問に0/1/2の具体的アンカーが表示され、記事箇所と理由の入力が必須である
- PublishableとCritical issueがある
- 対象Traceへread-onlyで接続できる
- Trace側でも全文Markdown表示を確認できる

1項目でも確認できなければ、人間へ採点を依頼せず`BLOCKED: REVIEW_SURFACE_INCOMPLETE`として修正する。

## Human + AI boundary

Agentは表示・接続・設問の事前確認までを自動化する。9項目の点数、各Rationale、Publishable、Critical issueは人間だけが入力する。Agentが人間の代わりに値を送信しない。

## Required evidence

Human Review準備完了を報告するときは次を残す。

- article path
- trace ID
- review queue ID
- Trace全文Markdown確認結果
- 先頭見出しと末尾見出しの確認結果
- 画像件数とHTTP確認結果
- 設問数（9 + 2）
- Review UI URL
