"""
ファイル操作ツール (Read, Write, Edit) の使用例
"""
import asyncio
import tempfile
from claude_agent_sdk import query, ClaudeAgentOptions


async def main():
    """ファイル操作の例"""
    with tempfile.TemporaryDirectory() as tmpdir:
        options = ClaudeAgentOptions(
            allowed_tools=["Read", "Write", "Edit"],
            permission_mode="bypassPermissions",
            cwd=tmpdir
        )

        # ファイル作成と編集
        async for message in query(
            prompt="""
            以下の作業を行ってください:
            1. config.py というファイルを作成し、DEBUG = False と書く
            2. そのファイルを読み取って内容を確認
            3. DEBUG = True に編集
            """,
            options=options
        ):
            print(message)


if __name__ == "__main__":
    asyncio.run(main())
