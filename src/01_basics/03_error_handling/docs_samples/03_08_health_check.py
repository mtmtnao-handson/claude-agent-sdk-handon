"""
ヘルスチェック関数 - SDK の動作状態をチェック
"""
import asyncio
import time
from claude_agent_sdk import query, CLINotFoundError, ResultMessage


async def health_check() -> dict:
    """SDK の動作状態をチェック"""

    status = {
        "cli_available": False,
        "api_connection": False,
        "response_time_ms": None,
        "error": None
    }

    start = time.time()

    try:
        async for message in query(prompt="ping"):
            if isinstance(message, ResultMessage):
                status["cli_available"] = True
                status["api_connection"] = True
                status["response_time_ms"] = (time.time() - start) * 1000

    except CLINotFoundError:
        status["error"] = "Claude Code CLI not installed"
    except Exception as e:
        status["cli_available"] = True  # CLI はあるがAPI接続失敗
        status["error"] = str(e)

    return status


async def main():
    print("ヘルスチェック実行中...")
    result = await health_check()

    print(f"\nCLI 利用可能: {result['cli_available']}")
    print(f"API 接続: {result['api_connection']}")

    if result['response_time_ms']:
        print(f"応答時間: {result['response_time_ms']:.0f}ms")

    if result['error']:
        print(f"エラー: {result['error']}")


asyncio.run(main())
