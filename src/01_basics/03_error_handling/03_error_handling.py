"""
エラーハンドリング
"""
import asyncio
from claude_agent_sdk import query, ClaudeSDKError, CLINotFoundError, CLIConnectionError


async def safe_query(prompt: str, max_retries: int = 3):
    """リトライ付きのクエリ実行"""
    for attempt in range(max_retries):
        try:
            results = []
            async for message in query(prompt=prompt):
                results.append(message)
            return results

        except CLIConnectionError as e:
            print(f"接続エラー: {e}")
            # 接続エラーはリトライ可能
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)

        except ClaudeSDKError as e:
            print(f"試行 {attempt + 1}/{max_retries} 失敗: {e}")
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # 指数バックオフ


async def main():
    try:
        results = await safe_query("Hello!")
        for msg in results:
            print(msg)
    except CLINotFoundError:
        print("Claude CLI がインストールされていません")
    except CLIConnectionError as e:
        print(f"接続エラー: {e}")
    except ClaudeSDKError as e:
        print(f"SDK エラー: {e}")


if __name__ == "__main__":
    asyncio.run(main())
