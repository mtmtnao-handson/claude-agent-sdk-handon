import asyncio
from claude_agent_sdk import query, ResultMessage

async def check_cost():
    async for message in query(prompt="Hello, Claude!"):
        if isinstance(message, ResultMessage):
            print(f"セッションID: {message.session_id}")
            print(f"API コスト: ${message.total_cost_usd:.6f}")
            print(f"合計ターン数: {message.num_turns}")
            print(f"実行時間: {message.duration_ms}ms")
            if message.usage:
                print(f"使用量: {message.usage}")

asyncio.run(check_cost())
