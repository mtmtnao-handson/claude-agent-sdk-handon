import asyncio
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock,
    ToolUseBlock
)
from dataclasses import dataclass

@dataclass
class QueryResult:
    texts: list[str]
    tool_uses: list[dict]
    total_cost: float

async def collect_messages(prompt: str) -> QueryResult:
    options = ClaudeAgentOptions(allowed_tools=["Read", "Glob"])

    texts = []
    tool_uses = []
    total_cost = 0.0

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    texts.append(block.text)
                elif isinstance(block, ToolUseBlock):
                    tool_uses.append({
                        "name": block.name,
                        "input": block.input,
                        "id": block.id
                    })
        elif hasattr(message, 'total_cost_usd'):
            total_cost = message.total_cost_usd

    return QueryResult(texts=texts, tool_uses=tool_uses, total_cost=total_cost)

async def main():
    result = await collect_messages("README.md ファイルを探して内容を要約して")
    print(f"テキスト応答数: {len(result.texts)}")
    print(f"ツール使用数: {len(result.tool_uses)}")
    print(f"合計コスト: ${result.total_cost:.4f}")

    for tool in result.tool_uses:
        print(f"  - {tool['name']}")

asyncio.run(main())
