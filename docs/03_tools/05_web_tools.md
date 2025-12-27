# Web ツール (WebSearch, WebFetch)

## 概要

このセクションでは、WebSearch と WebFetch ツールを使ってインターネットから情報を取得する方法を学習します。

これらのツールを使うと、最新の技術情報やドキュメントを取得できます。

---

## 手順1: WebSearch ツール

### 1. 基本的な使い方

WebSearch ツールはインターネットを検索します。

**コード:**

```python
import asyncio
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    allowed_tools=["WebSearch"]
)

async def search_web():
    prompt = "Python asyncio のベストプラクティスを検索してください"

    async for message in query(prompt=prompt, options=options):
        print(message)

asyncio.run(search_web())
```

### 2. 効果的な検索クエリ

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    allowed_tools=["WebSearch"],
    system_prompt="""効果的な検索クエリの作り方：
- 具体的なキーワードを使用
- 技術名 + バージョンを含める
- エラーメッセージはそのまま検索
- 公式ドキュメントを優先 (site:docs.python.org など)"""
)

async def smart_search():
    prompts = [
        "FastAPI で WebSocket を実装する方法",
        "TypeError: 'NoneType' object is not subscriptable の解決方法",
        "Claude API の最新のレート制限"
    ]

    for prompt in prompts:
        print(f"\n--- {prompt} ---")
        async for message in query(prompt=prompt, options=options):
            print(message)
```

---

## 手順2: WebFetch ツール

### 1. 基本的な使い方

WebFetch ツールは指定した URL からコンテンツを取得します。

**コード:**

```python
import asyncio
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    allowed_tools=["WebFetch"]
)

async def fetch_page():
    prompt = """https://docs.python.org/3/library/asyncio.html から
asyncio の主要な機能を取得して要約してください"""

    async for message in query(prompt=prompt, options=options):
        print(message)

asyncio.run(fetch_page())
```

### 2. WebFetch のパラメータ

| パラメータ | 型 | 説明 |
|-----------|-----|------|
| `url` | string | 取得する URL |
| `prompt` | string | コンテンツに対する指示 |

<div style="background-color: #f0f8ff; border: 1px solid #cce5ff; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #0d6efd; line-height: 1;">&#x24D8;</span>
    <span style="font-weight: bold; color: #0d6efd; font-size: 15px;">Note</span>
  </div>
  <div style="color: #454545; line-height: 1.6;">
    WebFetch は HTML を Markdown に変換し、AI モデルで処理します。大きなページは要約される場合があります。
  </div>
</div>

---

## 手順3: WebSearch と WebFetch の組み合わせ

### 1. 検索 → 詳細取得パターン

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    allowed_tools=["WebSearch", "WebFetch"],
    system_prompt="""リサーチの手順：
1. WebSearch で関連情報を検索
2. 有望な結果の URL を WebFetch で取得
3. 情報を統合してまとめる"""
)

async def research_topic():
    prompt = """Claude Agent SDK の使い方を調査してください：
1. 公式ドキュメントを検索
2. 主要なページを取得
3. 基本的な使い方をまとめる"""

    async for message in query(prompt=prompt, options=options):
        print(message)
```

### 2. ドキュメント収集

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    allowed_tools=["WebSearch", "WebFetch", "Write"],
    permission_mode="acceptEdits"
)

async def collect_documentation():
    prompt = """FastAPI のチュートリアルを調査し、以下を作成してください：
1. 公式ドキュメントから主要なページを取得
2. 日本語で要約した docs/fastapi_guide.md を作成"""

    async for message in query(prompt=prompt, options=options):
        print(message)
```

---

## 手順4: 実用的なユースケース

### 1. エラー調査

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    allowed_tools=["WebSearch", "WebFetch", "Read"],
    system_prompt="""エラー調査の手順：
1. エラーメッセージを分析
2. 関連するキーワードで検索
3. Stack Overflow や GitHub Issues を確認
4. 解決策を提案"""
)

async def investigate_error():
    prompt = """以下のエラーの解決方法を調査してください：
RuntimeError: Event loop is closed"""

    async for message in query(prompt=prompt, options=options):
        print(message)
```

### 2. ライブラリ調査

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    allowed_tools=["WebSearch", "WebFetch"]
)

async def research_library():
    prompt = """以下のライブラリを比較調査してください：
- httpx vs aiohttp vs requests
調査項目：機能、パフォーマンス、使いやすさ、メンテナンス状況"""

    async for message in query(prompt=prompt, options=options):
        print(message)
```

### 3. 最新情報の取得

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    allowed_tools=["WebSearch", "WebFetch"],
    system_prompt="最新の情報を優先し、日付を確認してください"
)

async def get_latest_info():
    prompt = "Python 3.12 の新機能を調査してください"

    async for message in query(prompt=prompt, options=options):
        print(message)
```

---

## 手順5: Web ツールの制限と注意点

### 1. 制限事項

<div style="background-color: #fff3cd; border: 1px solid #ffc107; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #856404; line-height: 1;">&#x26A0;</span>
    <span style="font-weight: bold; color: #856404; font-size: 15px;">注意事項</span>
  </div>
  <div style="color: #454545; line-height: 1.6;">
    <ul style="margin: 0; padding-left: 20px;">
      <li>認証が必要なページは取得できない</li>
      <li>JavaScript で動的に生成されるコンテンツは取得できない場合がある</li>
      <li>レート制限がある（過度な連続リクエストは避ける）</li>
      <li>取得したコンテンツの著作権に注意</li>
    </ul>
  </div>
</div>

### 2. キャッシュの活用

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    allowed_tools=["WebFetch"],
    system_prompt="""Web コンテンツ取得のルール：
- 同じ URL への繰り返しリクエストを避ける
- 15分間のキャッシュがある
- 大きなページは要約されることを考慮"""
)
```

---

## 手順6: 高度な活用

### 1. API ドキュメント取得

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    allowed_tools=["WebFetch", "Write"],
    permission_mode="acceptEdits"
)

async def fetch_api_docs():
    prompt = """以下の API ドキュメントを取得し、クイックリファレンスを作成：
https://docs.anthropic.com/en/api/messages

作成する内容：
- 主要なエンドポイント
- 必須パラメータ
- 使用例"""

    async for message in query(prompt=prompt, options=options):
        print(message)
```

### 2. 競合分析

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    allowed_tools=["WebSearch", "WebFetch"],
    system_prompt="客観的な比較を心がけ、情報源を明記してください"
)

async def competitive_analysis():
    prompt = """以下のサービスを比較分析してください：
- OpenAI API
- Claude API
- Google Gemini API

比較項目：料金、機能、制限、使いやすさ"""

    async for message in query(prompt=prompt, options=options):
        print(message)
```

<div style="background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #155724; line-height: 1;">&#x2714;</span>
    <span style="font-weight: bold; color: #155724; font-size: 15px;">ポイント</span>
  </div>
  <div style="color: #155724; line-height: 1.6;">
    Web ツールは最新情報の取得に最適ですが、情報の正確性は必ず確認してください。複数のソースを参照することを推奨します。
  </div>
</div>

---

## 演習問題

### 演習1: 技術調査レポート

指定した技術トピックについて Web 検索を行い、構造化されたレポートを生成する関数を作成してください。

### 演習2: 更新チェッカー

特定のライブラリの最新バージョンと変更点を取得し、プロジェクトの依存関係と比較するツールを作成してください。

### 演習3: ドキュメント同期

外部ドキュメントの内容をローカルの Markdown ファイルに同期する機能を実装してください。

---

## 次のステップ

Web ツールを理解しました。次は [Task ツール](06_task_tool.md) で、タスク管理について学びましょう。
