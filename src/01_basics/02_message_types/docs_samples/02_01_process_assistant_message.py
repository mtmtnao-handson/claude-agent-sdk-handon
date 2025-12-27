import asyncio
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock,
    ToolUseBlock
)

async def process_assistant_message():
    options = ClaudeAgentOptions(
        allowed_tools=["Bash"]
    )

    prompt = "現在のディレクトリにあるファイルを一覧表示して、その後何が見つかったか教えてください"

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
        
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"[テキスト] {block.text}")
                elif isinstance(block, ToolUseBlock):
                    print(f"[ツール使用] {block.name}")
                    print(f"    入力: {block.input}")
                    print(f"    ID: {block.id}")

asyncio.run(process_assistant_message())
