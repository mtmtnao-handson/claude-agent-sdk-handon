"""
コンテキストマネージャーによるリソース管理 - クリーンアップを保証する
"""
import asyncio
from contextlib import asynccontextmanager
from claude_agent_sdk import query, ClaudeSDKError, ResultMessage


@asynccontextmanager
async def managed_query(prompt: str):
    """クエリ実行をラップし、リソース管理とエラーハンドリングを提供"""

    results = []
    error = None

    try:
        async for message in query(prompt=prompt):
            results.append(message)
        yield results

    except ClaudeSDKError as e:
        error = e
        yield []  # 空の結果を返す

    finally:
        # クリーンアップ処理
        if error:
            print(f"エラーが発生しました: {error}")

        # コスト情報を出力
        for msg in results:
            if isinstance(msg, ResultMessage):
                print(f"セッション {msg.session_id} 完了 (${msg.total_cost_usd:.4f})")


async def main():
    async with managed_query("簡単なPython関数を書いて") as results:
        for msg in results:
            print(msg)


asyncio.run(main())
