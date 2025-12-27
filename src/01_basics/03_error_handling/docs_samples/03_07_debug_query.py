"""
デバッグとトラブルシューティング - 詳細なエラー情報の取得
"""
import asyncio
import traceback
from claude_agent_sdk import query, ClaudeSDKError


async def debug_query(prompt: str):
    try:
        async for message in query(prompt=prompt):
            print(f"[DEBUG] {type(message).__name__}")

    except ClaudeSDKError as e:
        print("=== エラー詳細 ===")
        print(f"例外クラス: {type(e).__name__}")
        print(f"メッセージ: {e}")
        print(f"引数: {e.args}")
        print("\n=== スタックトレース ===")
        traceback.print_exc()

        # ProcessError の場合は追加情報
        if hasattr(e, 'exit_code'):
            print(f"\n終了コード: {e.exit_code}")
        if hasattr(e, 'stderr'):
            print(f"標準エラー: {e.stderr}")


asyncio.run(debug_query("テストプロンプト"))
