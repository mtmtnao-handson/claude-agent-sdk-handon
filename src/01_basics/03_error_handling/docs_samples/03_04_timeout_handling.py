"""
タイムアウトの設定 - asyncio.timeout を使用
"""
import asyncio
from claude_agent_sdk import query, ResultMessage


async def query_with_timeout(prompt: str, timeout_seconds: float = 30.0):
    """タイムアウト付きでクエリを実行"""

    try:
        async with asyncio.timeout(timeout_seconds):
            results = []
            async for message in query(prompt=prompt):
                results.append(message)
            return results

    except asyncio.TimeoutError:
        print(f"タイムアウト: {timeout_seconds}秒を超えました")
        return None


async def main():
    # 短いタイムアウトでテスト
    result = await query_with_timeout("大量のデータを分析して", timeout_seconds=5.0)

    if result is None:
        print("処理がタイムアウトしました。より長い時間を設定してください。")
    else:
        print(f"正常完了: {len(result)} メッセージ")


asyncio.run(main())
