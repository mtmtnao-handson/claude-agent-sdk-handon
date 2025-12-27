"""
MCP ツールの指定例 (手順4)

MCP (Model Context Protocol) サーバーのツールを allowed_tools で指定する方法を示します。

Usage:
    python 02_mcp_tools.py -l              # 利用可能な設定一覧
    python 02_mcp_tools.py -m builtin      # ビルトインツールのみ
    python 02_mcp_tools.py -m with-mcp     # MCP ツールを含む
    python 02_mcp_tools.py -m mcp-only     # MCP ツールのみ

Note:
    MCP ツールを使用するには、対応する MCP サーバーが mcp_servers オプションで
    設定されている必要があります。このスクリプトは設定例のデモンストレーションです。
"""
import argparse
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage, TextBlock, ToolUseBlock

# =============================================================================
# MCP ツールの命名規則: mcp__{サーバー名}__{ツール名}
# =============================================================================

# ビルトインツールのみ
BUILTIN_ONLY_OPTIONS = ClaudeAgentOptions(
    allowed_tools=["Read", "Write", "Glob"]
)

# ビルトインツールと MCP ツールを組み合わせ
WITH_MCP_OPTIONS = ClaudeAgentOptions(
    allowed_tools=[
        # ビルトインツール
        "Read",
        "Write",
        "Glob",

        # MCP ツール (例)
        "mcp__filesystem__read_file",
        "mcp__filesystem__write_file",
        "mcp__database__query",
        "mcp__slack__send_message"
    ]
)

# MCP ツールのみ (ビルトインを制限)
MCP_ONLY_OPTIONS = ClaudeAgentOptions(
    allowed_tools=[
        "mcp__filesystem__read_file",
        "mcp__filesystem__write_file",
        "mcp__filesystem__list_directory",
        "mcp__database__query",
        "mcp__database__execute",
    ]
)

# データベース操作用
DATABASE_OPTIONS = ClaudeAgentOptions(
    allowed_tools=[
        "Read",
        "Glob",
        "mcp__database__query",
        "mcp__database__execute",
        "mcp__database__list_tables",
    ]
)

# Slack 連携用
SLACK_OPTIONS = ClaudeAgentOptions(
    allowed_tools=[
        "Read",
        "Glob",
        "mcp__slack__send_message",
        "mcp__slack__list_channels",
        "mcp__slack__get_messages",
    ]
)

# =============================================================================
# モード名からオプションへのマッピング
# =============================================================================

MODE_OPTIONS = {
    "builtin": BUILTIN_ONLY_OPTIONS,
    "with-mcp": WITH_MCP_OPTIONS,
    "mcp-only": MCP_ONLY_OPTIONS,
    "database": DATABASE_OPTIONS,
    "slack": SLACK_OPTIONS,
}

MODE_DESCRIPTIONS = {
    "builtin": "ビルトインツールのみ (Read, Write, Glob)",
    "with-mcp": "ビルトイン + MCP ツール",
    "mcp-only": "MCP ツールのみ",
    "database": "データベース操作用 MCP",
    "slack": "Slack 連携用 MCP",
}


def parse_args() -> argparse.Namespace:
    """コマンドライン引数をパース"""
    parser = argparse.ArgumentParser(
        description="MCP ツールの指定例",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-m", "--mode",
        choices=list(MODE_OPTIONS.keys()),
        default="builtin",
        help="ツール設定モード (default: builtin)"
    )
    parser.add_argument(
        "-p", "--prompt",
        default="利用可能なツールを確認して、何ができるか教えてください",
        help="実行するプロンプト"
    )
    parser.add_argument(
        "-l", "--list-modes",
        action="store_true",
        help="利用可能なモードの詳細を表示して終了"
    )
    return parser.parse_args()


def print_mode_details():
    """全モードの詳細を表示"""
    print("=" * 60)
    print("MCP ツール設定モード一覧")
    print("=" * 60)

    for mode_name, options in MODE_OPTIONS.items():
        desc = MODE_DESCRIPTIONS.get(mode_name, "")
        print(f"\n[{mode_name}] {desc}")
        print(f"  allowed_tools:")
        for tool in options.allowed_tools:
            prefix = "    (MCP) " if tool.startswith("mcp__") else "    "
            print(f"{prefix}{tool}")


async def main():
    """コマンドライン引数に基づいて実行"""
    args = parse_args()

    if args.list_modes:
        print_mode_details()
        return

    options = MODE_OPTIONS[args.mode]
    desc = MODE_DESCRIPTIONS.get(args.mode, "")

    print("=" * 60)
    print(f"モード: {args.mode} ({desc})")
    print("-" * 60)
    print("allowed_tools:")
    for tool in options.allowed_tools:
        prefix = "  (MCP) " if tool.startswith("mcp__") else "  "
        print(f"{prefix}{tool}")
    print("-" * 60)
    print(f"プロンプト: {args.prompt}")
    print("=" * 60)

    print("\n[Note] MCP ツールを実際に使用するには、mcp_servers の設定が必要です。")
    print("このスクリプトは設定例のデモンストレーションです。\n")

    async for message in query(
        prompt=args.prompt,
        options=options
    ):
        if isinstance(message, AssistantMessage):
            print("=== AssistantMessage ===")
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"[Text] {block.text}")
                elif isinstance(block, ToolUseBlock):
                    tool_type = "(MCP)" if block.name.startswith("mcp__") else ""
                    print(f"[Tool] {tool_type} {block.name}: {block.input}")

        elif isinstance(message, ResultMessage):
            print("=== ResultMessage ===")
            if message.subtype == "success":
                print(f"セッションID: {message.result}")
            else:
                print(f"subtype: {message.subtype}")


if __name__ == "__main__":
    asyncio.run(main())
