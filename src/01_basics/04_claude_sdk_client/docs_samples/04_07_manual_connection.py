"""
手動での接続管理 - コンテキストマネージャーを使わない方法
"""
import asyncio
from claude_agent_sdk import ClaudeSDKClient
from claude_agent_sdk.types import AssistantMessage, TextBlock


async def manual_connection():
    client = ClaudeSDKClient()

    try:
        # 明示的に接続
        await client.connect()

        await client.query("こんにちは")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text)

    finally:
        # 明示的に切断
        await client.disconnect()


asyncio.run(manual_connection())
