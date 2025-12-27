"""
基本的な ClaudeSDKClient の使い方 - コンテキストマネージャーを使った基本形
"""
import asyncio
from claude_agent_sdk import ClaudeSDKClient, AssistantMessage, TextBlock


async def main():
    async with ClaudeSDKClient() as client:
        await client.query("Pythonとは何ですか？")

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text)


asyncio.run(main())
