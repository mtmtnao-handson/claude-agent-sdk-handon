"""
カスタムツールの作成例
"""
import asyncio
from datetime import datetime
import uuid
from claude_agent_sdk import tool, create_sdk_mcp_server, ClaudeAgentOptions, query


@tool("greet", "ユーザーに挨拶を返します", {"name": str})
async def greet(args: dict) -> dict:
    name = args["name"]
    return {
        "content": [
            {"type": "text", "text": f"こんにちは、{name}さん！"}
        ]
    }


@tool("get_datetime", "現在の日時を取得します", {})
async def get_datetime(args: dict) -> dict:
    now = datetime.now()
    return {
        "content": [
            {"type": "text", "text": now.strftime("%Y-%m-%d %H:%M:%S")}
        ]
    }


@tool("generate_uuid", "UUID を生成します", {})
async def generate_uuid(args: dict) -> dict:
    return {
        "content": [
            {"type": "text", "text": str(uuid.uuid4())}
        ]
    }


@tool(
    "calculate",
    "数式を計算します",
    {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "計算する数式"
            }
        },
        "required": ["expression"]
    }
)
async def calculate(args: dict) -> dict:
    try:
        # 安全な計算のみ許可
        allowed = set("0123456789+-*/.() ")
        expr = args["expression"]
        if not all(c in allowed for c in expr):
            raise ValueError("許可されていない文字が含まれています")
        result = eval(expr, {"__builtins__": {}}, {})
        return {"content": [{"type": "text", "text": f"結果: {result}"}]}
    except Exception as e:
        return {"content": [{"type": "text", "text": f"エラー: {e}"}]}


# MCP サーバーを作成
utility_server = create_sdk_mcp_server(
    name="utilities",
    version="1.0.0",
    tools=[greet, get_datetime, generate_uuid, calculate]
)


async def main():
    """カスタムツールの使用"""
    options = ClaudeAgentOptions(
        mcp_servers={"utils": utility_server},
        allowed_tools=[
            "mcp__utils__greet",
            "mcp__utils__get_datetime",
            "mcp__utils__generate_uuid",
            "mcp__utils__calculate"
        ]
    )

    async for message in query(
        prompt="""
        以下を実行してください:
        1. 「田中」さんに挨拶
        2. 現在の日時を取得
        3. UUID を生成
        4. 123 + 456 を計算
        """,
        options=options
    ):
        print(message)


if __name__ == "__main__":
    asyncio.run(main())
