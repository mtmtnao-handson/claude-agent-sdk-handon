import asyncio
from claude_agent_sdk import query, ResultMessage

async def analyze_result():
    async for message in query(prompt="簡単な挨拶をしてください"):
        if isinstance(message, ResultMessage):
            print("=== 実行結果 ===")
            # subtype をチェックしてからメンバ変数にアクセス
            if message.subtype == "success":
                print(f"セッションID: {message.session_id}")
                print(f"API コスト: ${message.total_cost_usd:.6f}")
                print(f"合計ターン数: {message.num_turns}")
                print(f"実行時間: {message.duration_ms}ms")
                print(f"API実行時間: {message.duration_api_ms}ms")
                if message.usage:
                    print(f"使用量: {message.usage}")
            else:
                print(f"subtype: {message.subtype}")

asyncio.run(analyze_result())
