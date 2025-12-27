import asyncio
import json
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    ToolUseBlock
)

async def analyze_tool_use():
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Glob"]
    )

    prompt = "src/ ディレクトリ内の .py ファイルを探して、最初のファイルを読んでください"

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ToolUseBlock):
                    print(f"=== ツール使用 ===")
                    print(f"ツール名: {block.name}")
                    print(f"ツールID: {block.id}")
                    print(f"入力パラメータ:")
                    print(json.dumps(block.input, indent=2, ensure_ascii=False))
                    print()

asyncio.run(analyze_tool_use())
