"""
会話中の設定変更 - パーミッションモードの動的変更
"""
import asyncio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions
from claude_agent_sdk.types import AssistantMessage, TextBlock


async def change_settings():
    options = ClaudeAgentOptions(
        permission_mode="default",
        allowed_tools=["Read", "Write", "Edit"]
    )

    async with ClaudeSDKClient(options) as client:
        # 最初は確認が必要なモード
        await client.query("現在のディレクトリのファイルを確認して")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text)

        # 編集を自動承認するモードに変更
        await client.set_permission_mode("acceptEdits")
        print("\n[パーミッションモードを acceptEdits に変更]\n")

        # ファイル編集が自動承認される
        await client.query("README.md に説明を追加して")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text)


asyncio.run(change_settings())
