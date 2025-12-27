import asyncio
from claude_agent_sdk import query, AssistantMessage, TextBlock

async def get_text_response(prompt: str) -> str:
    """プロンプトを送信し、テキストレスポンスを返す"""
    text_parts = []

    async for message in query(prompt=prompt):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    text_parts.append(block.text)

    return "".join(text_parts)

async def main():
    response = await get_text_response("Pythonの主な特徴を3つ教えてください")
    print(response)

asyncio.run(main())
