"""
オプション付きでクライアントを初期化 - ClaudeAgentOptions との組み合わせ
"""
import asyncio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions
from claude_agent_sdk.types import AssistantMessage, TextBlock


async def with_options():
    options = ClaudeAgentOptions(
        system_prompt="あなたは親切な日本語アシスタントです。簡潔に回答してください。",
        max_turns=5,
        permission_mode="acceptEdits"
    )

    async with ClaudeSDKClient(options) as client:
        await client.query("再帰関数とは何ですか？")

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text)


asyncio.run(with_options())
