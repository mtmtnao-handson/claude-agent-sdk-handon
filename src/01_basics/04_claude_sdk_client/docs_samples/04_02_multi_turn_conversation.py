"""
マルチターン会話 - コンテキストを維持した連続会話
"""
import asyncio
from claude_agent_sdk import ClaudeSDKClient, AssistantMessage, TextBlock, ResultMessage


async def multi_turn_conversation():
    async with ClaudeSDKClient() as client:
        # 最初の質問
        print("--- 質問1 ---")
        await client.query("私の名前は田中です。覚えておいてください。")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")

        # フォローアップ（コンテキストが維持される）
        print("\n--- 質問2 ---")
        await client.query("私の名前を覚えていますか？")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")

        # さらにフォローアップ
        print("\n--- 質問3 ---")
        await client.query("私の名前を使って挨拶してください。")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")


asyncio.run(multi_turn_conversation())
