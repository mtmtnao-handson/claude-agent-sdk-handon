"""
ClaudeSDKClient の基本
"""
import asyncio
from claude_agent_sdk import ClaudeSDKClient, AssistantMessage, TextBlock


async def main():
    """ClaudeSDKClient の基本的な使い方"""
    async with ClaudeSDKClient() as client:
        await client.query("Pythonとは何ですか？")

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text)


if __name__ == "__main__":
    asyncio.run(main())
