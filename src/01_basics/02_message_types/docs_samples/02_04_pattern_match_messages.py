import asyncio
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    UserMessage,
    SystemMessage,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    ToolResultBlock
)

async def pattern_match_messages():
    options = ClaudeAgentOptions(allowed_tools=["Bash"])

    async for message in query(prompt="pwd コマンドを実行して", options=options):
        match message:
            case AssistantMessage(content=content):
                for block in content:
                    match block:
                        case TextBlock(text=text):
                            print(f"[テキスト] {text}")
                        case ToolUseBlock(name=name, input=input_data):
                            print(f"[ツール] {name}: {input_data}")

            case ResultMessage(subtype="success", total_cost_usd=cost, num_turns=turns):
                print(f"[結果] コスト: ${cost:.4f}, ターン数: {turns}")

            case ResultMessage(subtype=subtype):
                print(f"[結果] subtype: {subtype}")

            case _:
                print(f"[その他] {type(message).__name__}")

asyncio.run(pattern_match_messages())
