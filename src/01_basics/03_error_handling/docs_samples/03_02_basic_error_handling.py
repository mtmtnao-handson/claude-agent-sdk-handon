"""
基本的なエラーハンドリング - try-except による例外処理
"""
import asyncio
from claude_agent_sdk import (
    query,
    ClaudeSDKError,
    CLINotFoundError,
    CLIConnectionError,
    ProcessError,
    CLIJSONDecodeError
)


async def safe_query(prompt: str):
    try:
        async for message in query(prompt=prompt):
            print(message)

    except CLINotFoundError:
        print("エラー: Claude Code CLI がインストールされていません")
        print("解決方法: brew install --cask claude-code")

    except CLIConnectionError as e:
        print(f"エラー: CLI との接続に失敗しました")
        print(f"詳細: {e}")

    except ProcessError as e:
        print(f"エラー: プロセスが異常終了しました")
        print(f"終了コード: {e.exit_code}")
        print(f"stderr: {e.stderr}")

    except CLIJSONDecodeError as e:
        print(f"エラー: レスポンスのパースに失敗しました")
        print(f"詳細: {e}")

    except ClaudeSDKError as e:
        print(f"SDK エラー: {e}")


asyncio.run(safe_query("Hello!"))
