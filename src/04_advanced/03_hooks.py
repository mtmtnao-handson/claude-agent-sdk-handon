"""
フック機能の実装例
"""
import asyncio
import json
from datetime import datetime
from pathlib import Path
from claude_agent_sdk import query, ClaudeAgentOptions, HookMatcher


class AuditLogger:
    """監査ログを記録するフック"""

    def __init__(self, log_file: str = "audit.jsonl"):
        self.log_file = Path(log_file)

    async def pre_tool_hook(self, input_data, tool_use_id, context):
        """ツール実行前のログ"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event": "pre_tool_use",
            "tool_name": input_data["tool_name"],
            "tool_input": input_data["tool_input"]
        }
        self._write_log(entry)
        print(f"[PRE] {input_data['tool_name']}")
        return {}

    async def post_tool_hook(self, input_data, tool_use_id, context):
        """ツール実行後のログ"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event": "post_tool_use",
            "tool_name": input_data["tool_name"]
        }
        self._write_log(entry)
        print(f"[POST] {input_data['tool_name']}")
        return {}

    def _write_log(self, entry: dict):
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


async def bash_guard(input_data, tool_use_id, context):
    """危険なコマンドをブロック"""
    command = input_data["tool_input"].get("command", "")
    dangerous = ["rm -rf", "sudo", "> /dev/"]

    for pattern in dangerous:
        if pattern in command:
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": f"危険なパターン: {pattern}"
                }
            }
    return {}


async def main():
    """フック付きでの実行"""
    logger = AuditLogger()

    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Glob", "Bash"],
        hooks={
            "PreToolUse": [
                HookMatcher(hooks=[logger.pre_tool_hook]),
                HookMatcher(matcher="Bash", hooks=[bash_guard])
            ],
            "PostToolUse": [
                HookMatcher(hooks=[logger.post_tool_hook])
            ]
        }
    )

    async for message in query(
        prompt="現在のディレクトリのファイル一覧を確認してください",
        options=options
    ):
        print(message)


if __name__ == "__main__":
    asyncio.run(main())
