"""
Bash ツールの使用例
"""
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions


async def main():
    """Bash コマンド実行の例"""
    options = ClaudeAgentOptions(
        allowed_tools=["Bash"],
        permission_mode="default"  # 確認ありモード（安全）
    )

    async for message in query(
        prompt="""
        以下のコマンドを実行してください:
        1. Python のバージョンを確認
        2. pip でインストール済みのパッケージ一覧を表示
        """,
        options=options
    ):
        print(message)


if __name__ == "__main__":
    asyncio.run(main())
