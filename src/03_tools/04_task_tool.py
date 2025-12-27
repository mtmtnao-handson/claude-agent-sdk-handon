"""
Task ツール（サブエージェント）の使用例
"""
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions


async def main():
    """Task ツールによる並列処理"""
    options = ClaudeAgentOptions(
        allowed_tools=["Task", "Read", "Glob", "Grep"]
    )

    async for message in query(
        prompt="""
        以下のタスクを並列で実行してください:
        1. src/basics/ のすべてのファイルを分析
        2. src/options/ のすべてのファイルを分析
        3. 両方の結果をまとめてレポート
        """,
        options=options
    ):
        print(message)


if __name__ == "__main__":
    asyncio.run(main())
