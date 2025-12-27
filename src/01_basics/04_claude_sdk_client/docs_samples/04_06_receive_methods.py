"""
receive_messages() と receive_response() の違い
"""
import asyncio
from claude_agent_sdk import ClaudeSDKClient, ResultMessage
from claude_agent_sdk.types import AssistantMessage, TextBlock


async def receive_response_example():
    """receive_response() の例 - ResultMessage まで受信して停止"""
    print("=== receive_response() ===")
    async with ClaudeSDKClient() as client:
        await client.query("こんにちは")

        # ResultMessage を受信すると自動的に停止
        async for message in client.receive_response():
            print(f"受信: {type(message).__name__}")
        # ここに到達 = 応答完了
        print("応答完了\n")


async def receive_messages_example():
    """receive_messages() の例 - 明示的に break が必要"""
    print("=== receive_messages() ===")
    async with ClaudeSDKClient() as client:
        await client.query("こんにちは")

        # 明示的に break しないと無限に待機
        async for message in client.receive_messages():
            print(f"受信: {type(message).__name__}")
            if isinstance(message, ResultMessage):
                break  # 手動で終了
        print("応答完了")


async def main():
    await receive_response_example()
    await receive_messages_example()


asyncio.run(main())
