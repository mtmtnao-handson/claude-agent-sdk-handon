"""
SDK の例外クラスのインポート
"""
from claude_agent_sdk import (
    ClaudeSDKError,
    CLINotFoundError,
    CLIConnectionError,
    ProcessError,
    CLIJSONDecodeError
)

# 例外階層:
# ClaudeSDKError (基底クラス)
# ├── CLINotFoundError      # Claude Code CLI が見つからない
# ├── CLIConnectionError    # CLI との接続エラー
# ├── ProcessError          # プロセス実行エラー
# └── CLIJSONDecodeError    # JSON パースエラー
