"""
MCP 連携の例
"""
import asyncio
from claude_agent_sdk import tool, create_sdk_mcp_server, ClaudeAgentOptions, query


# インプロセス MCP サーバー
@tool("echo", "入力をそのまま返します", {"message": str})
async def echo(args: dict) -> dict:
    return {"content": [{"type": "text", "text": args["message"]}]}


@tool("reverse", "文字列を逆順にします", {"text": str})
async def reverse(args: dict) -> dict:
    return {"content": [{"type": "text", "text": args["text"][::-1]}]}


@tool("uppercase", "文字列を大文字にします", {"text": str})
async def uppercase(args: dict) -> dict:
    return {"content": [{"type": "text", "text": args["text"].upper()}]}


# インプロセスサーバーを作成
internal_server = create_sdk_mcp_server(
    name="text-utils",
    version="1.0.0",
    tools=[echo, reverse, uppercase]
)


async def main():
    """MCP サーバーとの連携"""
    # インプロセスサーバーのみ使用
    options = ClaudeAgentOptions(
        mcp_servers={
            "text": internal_server
        },
        allowed_tools=[
            "mcp__text__echo",
            "mcp__text__reverse",
            "mcp__text__uppercase"
        ]
    )

    async for message in query(
        prompt="""
        以下を実行してください:
        1. 'Hello World' をエコー
        2. 'Hello World' を逆順に
        3. 'Hello World' を大文字に
        """,
        options=options
    ):
        print(message)


# 外部 MCP サーバーの設定例（参考）
def get_hybrid_options():
    """ハイブリッド構成の例"""
    return ClaudeAgentOptions(
        mcp_servers={
            # インプロセス
            "text": internal_server,

            # 外部サーバー（stdio）
            # "filesystem": {
            #     "type": "stdio",
            #     "command": "mcp-server-filesystem",
            #     "args": ["/workspace"]
            # },

            # 外部サーバー（環境変数付き）
            # "database": {
            #     "type": "stdio",
            #     "command": "mcp-server-sqlite",
            #     "args": ["--db-path", "data.db"],
            #     "env": {
            #         "LOG_LEVEL": "debug"
            #     }
            # }
        },
        allowed_tools=[
            "mcp__text__*",
            # "mcp__filesystem__read_file",
            # "mcp__database__query"
        ]
    )


if __name__ == "__main__":
    asyncio.run(main())
