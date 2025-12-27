"""
検索ツール (Glob, Grep) の使用例
"""
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions


async def main():
    """ファイル検索とコンテンツ検索の例"""
    options = ClaudeAgentOptions(
        allowed_tools=["Glob", "Grep", "Read"]
    )

    async for message in query(
        prompt="""
        以下の検索を行ってください:
        1. src ディレクトリ内のすべての .py ファイルを探す
        2. その中から "async def" を含むファイルを検索
        3. 見つかったファイルの内容を確認
        """,
        options=options
    ):
        print(message)


if __name__ == "__main__":
    asyncio.run(main())
