"""
リトライロジックの実装 - 指数バックオフ付きリトライ
"""
import asyncio
from claude_agent_sdk import (
    query,
    ClaudeSDKError,
    CLIConnectionError,
    ResultMessage
)


async def query_with_retry(
    prompt: str,
    max_retries: int = 3,
    base_delay: float = 1.0
):
    """指数バックオフ付きでクエリをリトライ"""

    for attempt in range(max_retries):
        try:
            results = []
            async for message in query(prompt=prompt):
                results.append(message)
            # ループ完了後に成功を報告して結果を返す
            print(f"成功 (試行 {attempt + 1}/{max_retries})")
            return results

        except CLIConnectionError as e:
            delay = base_delay * (2 ** attempt)  # 指数バックオフ
            print(f"接続エラー (試行 {attempt + 1}/{max_retries})")
            print(f"{delay}秒後にリトライします...")

            if attempt < max_retries - 1:
                await asyncio.sleep(delay)
            else:
                raise

        except ClaudeSDKError:
            # その他のSDKエラーはリトライしない
            raise

    raise Exception("最大リトライ回数を超えました")


async def main():
    try:
        results = await query_with_retry("Hello, Claude!")
        print(f"取得メッセージ数: {len(results)}")
    except Exception as e:
        print(f"最終的に失敗: {e}")


asyncio.run(main())
