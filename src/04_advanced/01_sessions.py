"""
セッション管理の例
"""
import asyncio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions


async def main():
    """会話の継続とコンテキスト保持"""
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Write"],
        permission_mode="acceptEdits"
    )

    async with ClaudeSDKClient(options=options) as client:
        # 最初の会話
        print("=== 会話 1 ===")
        async for message in client.process_query(
            "私の名前は田中です。覚えておいてください。"
        ):
            print(message)

        # 継続した会話（コンテキストが保持される）
        print("\n=== 会話 2 ===")
        async for message in client.process_query(
            "私の名前を覚えていますか？"
        ):
            print(message)

        # さらに継続
        print("\n=== 会話 3 ===")
        async for message in client.process_query(
            "これまでの会話を要約してください。"
        ):
            print(message)


if __name__ == "__main__":
    asyncio.run(main())
