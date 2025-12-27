# カスタムツール

## 概要

このセクションでは、@tool デコレータを使って独自のカスタムツールを作成する方法を学習します。

カスタムツールを使うと、Claude の機能を自由に拡張できます。

---

## 手順1: @tool デコレータの基本

### 1. 基本的なツール定義

**コード:**

```python
from claude_agent_sdk import tool, create_sdk_mcp_server, ClaudeAgentOptions

@tool(
    "greet",
    "ユーザーに挨拶を返します",
    {"name": str}
)
async def greet(args: dict) -> dict:
    name = args["name"]
    return {
        "content": [
            {"type": "text", "text": f"こんにちは、{name}さん！"}
        ]
    }

# MCP サーバーを作成
server = create_sdk_mcp_server(
    name="my-tools",
    version="1.0.0",
    tools=[greet]
)

# オプションに追加
options = ClaudeAgentOptions(
    mcp_servers={"custom": server},
    allowed_tools=["mcp__custom__greet"]
)
```

### 2. @tool デコレータのパラメータ

| パラメータ | 説明 |
|-----------|------|
| 第1引数 | ツール名（一意の識別子） |
| 第2引数 | ツールの説明（Claude が参照） |
| 第3引数 | 入力スキーマ（パラメータの型定義） |

### 3. 戻り値の形式

```python
{
    "content": [
        {"type": "text", "text": "テキスト結果"},
        # または
        {"type": "image", "data": "base64...", "mimeType": "image/png"}
    ]
}
```

---

## 手順2: 入力スキーマの定義

### 1. 様々な型の定義

**コード:**

```python
from claude_agent_sdk import tool

# 基本型
@tool("basic_types", "基本型のテスト", {
    "text": str,
    "number": int,
    "decimal": float,
    "flag": bool
})
async def basic_types(args):
    return {"content": [{"type": "text", "text": str(args)}]}

# オプショナル型（デフォルト値あり）
@tool("optional_params", "オプショナルパラメータのテスト", {
    "required_param": str,
    "optional_param": str  # None を許容
})
async def optional_params(args):
    required = args["required_param"]
    optional = args.get("optional_param", "デフォルト値")
    return {"content": [{"type": "text", "text": f"{required}, {optional}"}]}

# 複合型
@tool("complex_types", "複合型のテスト", {
    "items": list,
    "config": dict
})
async def complex_types(args):
    return {"content": [{"type": "text", "text": str(args)}]}
```

### 2. 詳細なスキーマ定義

**コード:**

```python
from claude_agent_sdk import tool

# JSON Schema 形式での詳細定義
@tool(
    "detailed_schema",
    "詳細なスキーマを持つツール",
    {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "検索クエリ"
            },
            "limit": {
                "type": "integer",
                "description": "結果の最大数",
                "default": 10,
                "minimum": 1,
                "maximum": 100
            },
            "filters": {
                "type": "array",
                "items": {"type": "string"},
                "description": "フィルタ条件"
            }
        },
        "required": ["query"]
    }
)
async def detailed_schema(args):
    return {"content": [{"type": "text", "text": str(args)}]}
```

---

## 手順3: 実践的なカスタムツール

### 1. データベースクエリツール

**コード:**

```python
import sqlite3
from claude_agent_sdk import tool, create_sdk_mcp_server

@tool(
    "query_database",
    "SQLiteデータベースにクエリを実行します（SELECT のみ）",
    {
        "query": str,
        "database": str
    }
)
async def query_database(args: dict) -> dict:
    query = args["query"]
    database = args["database"]

    # セキュリティチェック
    if not query.strip().upper().startswith("SELECT"):
        return {
            "content": [{"type": "text", "text": "エラー: SELECT クエリのみ許可されています"}]
        }

    try:
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()

        # 結果をフォーマット
        output = f"カラム: {columns}\n"
        for row in results[:100]:  # 最大100行
            output += f"{row}\n"

        return {"content": [{"type": "text", "text": output}]}

    except Exception as e:
        return {"content": [{"type": "text", "text": f"エラー: {e}"}]}
```

### 2. HTTP API 呼び出しツール

**コード:**

```python
import httpx
from claude_agent_sdk import tool

@tool(
    "call_api",
    "外部 API を呼び出します",
    {
        "url": str,
        "method": str,
        "headers": dict,
        "body": dict
    }
)
async def call_api(args: dict) -> dict:
    url = args["url"]
    method = args.get("method", "GET").upper()
    headers = args.get("headers", {})
    body = args.get("body")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                json=body if body else None,
                timeout=30.0
            )

        return {
            "content": [
                {"type": "text", "text": f"ステータス: {response.status_code}"},
                {"type": "text", "text": f"レスポンス:\n{response.text[:2000]}"}
            ]
        }

    except Exception as e:
        return {"content": [{"type": "text", "text": f"エラー: {e}"}]}
```

### 3. 通知ツール

**コード:**

```python
from claude_agent_sdk import tool

@tool(
    "send_notification",
    "Slack に通知を送信します",
    {
        "channel": str,
        "message": str,
        "urgency": str  # "low", "normal", "high"
    }
)
async def send_notification(args: dict) -> dict:
    channel = args["channel"]
    message = args["message"]
    urgency = args.get("urgency", "normal")

    # 実際の Slack API 呼び出し（例）
    # webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    # async with httpx.AsyncClient() as client:
    #     await client.post(webhook_url, json={"text": message})

    return {
        "content": [{
            "type": "text",
            "text": f"通知を送信しました: #{channel} ({urgency})\n{message}"
        }]
    }
```

<div style="background-color: #f0f8ff; border: 1px solid #cce5ff; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #0d6efd; line-height: 1;">&#x24D8;</span>
    <span style="font-weight: bold; color: #0d6efd; font-size: 15px;">Note</span>
  </div>
  <div style="color: #454545; line-height: 1.6;">
    カスタムツールは非同期関数（async def）で定義します。外部 API 呼び出しなどの I/O 処理に適しています。
  </div>
</div>

---

## 手順4: MCP サーバーの作成

### 1. 複数ツールのサーバー

**コード:**

```python
from claude_agent_sdk import tool, create_sdk_mcp_server, ClaudeAgentOptions

# ツール1: 計算
@tool("calculate", "数式を計算します", {"expression": str})
async def calculate(args):
    try:
        # 安全な計算のみ（eval は本番環境では避ける）
        result = eval(args["expression"], {"__builtins__": {}}, {})
        return {"content": [{"type": "text", "text": f"結果: {result}"}]}
    except Exception as e:
        return {"content": [{"type": "text", "text": f"エラー: {e}"}]}

# ツール2: 日時取得
@tool("get_datetime", "現在の日時を取得します", {})
async def get_datetime(args):
    from datetime import datetime
    now = datetime.now()
    return {"content": [{"type": "text", "text": now.isoformat()}]}

# ツール3: UUID 生成
@tool("generate_uuid", "UUID を生成します", {})
async def generate_uuid(args):
    import uuid
    return {"content": [{"type": "text", "text": str(uuid.uuid4())}]}

# サーバーを作成
utility_server = create_sdk_mcp_server(
    name="utilities",
    version="1.0.0",
    tools=[calculate, get_datetime, generate_uuid]
)

# オプションに追加
options = ClaudeAgentOptions(
    mcp_servers={"utils": utility_server},
    allowed_tools=[
        "mcp__utils__calculate",
        "mcp__utils__get_datetime",
        "mcp__utils__generate_uuid"
    ]
)
```

### 2. ツール名の規則

```
mcp__{サーバー名}__{ツール名}

例:
- mcp__utils__calculate
- mcp__custom__greet
- mcp__database__query
```

---

## 手順5: エラーハンドリング

### 1. 堅牢なツール実装

**コード:**

```python
from claude_agent_sdk import tool

@tool("robust_tool", "エラーハンドリングの例", {"input": str})
async def robust_tool(args: dict) -> dict:
    try:
        input_value = args.get("input")

        if not input_value:
            return {
                "content": [{
                    "type": "text",
                    "text": "エラー: input パラメータは必須です"
                }]
            }

        # メイン処理
        result = process_input(input_value)

        return {
            "content": [{
                "type": "text",
                "text": f"成功: {result}"
            }]
        }

    except ValueError as e:
        return {
            "content": [{
                "type": "text",
                "text": f"入力エラー: {e}"
            }]
        }

    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"予期しないエラー: {e}"
            }]
        }

def process_input(value: str) -> str:
    # 処理ロジック
    return value.upper()
```

<div style="background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #155724; line-height: 1;">&#x2714;</span>
    <span style="font-weight: bold; color: #155724; font-size: 15px;">ポイント</span>
  </div>
  <div style="color: #155724; line-height: 1.6;">
    カスタムツールでは必ず適切なエラーハンドリングを行い、Claude が次のアクションを判断できる情報を返しましょう。
  </div>
</div>

---

## 演習問題

### 演習1: ファイル変換ツール

JSON → YAML、YAML → JSON などの形式変換を行うツールを作成してください。

### 演習2: Git 操作ツール

安全な Git 操作（status, log, diff など読み取り系）を行うカスタムツールを作成してください。

### 演習3: メトリクス収集ツール

システムメトリクス（CPU、メモリ、ディスク使用量）を収集するツールを作成してください。

---

## 次のステップ

カスタムツールを理解しました。次は [MCP 連携](05_mcp_integration.md) で、外部 MCP サーバーとの連携について学びましょう。
