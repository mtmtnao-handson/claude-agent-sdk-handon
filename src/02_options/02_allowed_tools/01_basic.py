"""
allowed_tools の設定例

Usage:
    python 01_allowed_tools.py --mode read-only --prompt "ファイル一覧を表示して"
    python 01_allowed_tools.py -m file-ops -p "README.mdを作成して"
    python 01_allowed_tools.py -m full-access -p "このプロジェクトを調査して"

Available modes:
    基本モード:
        read-only   : 読み取り専用 (Read, Glob, Grep)
        file-ops    : ファイル操作 (Read, Write, Edit, Glob, Grep)
        full-access : フルアクセス (全ツール)

    ユースケース別:
        code-review : コードレビュー用 (読み取りのみ + 専用プロンプト)
        doc-writer  : ドキュメント作成用 (読み取り + Write)
        development : 開発作業用 (編集 + Bash + acceptEdits)
        research    : リサーチ用 (読み取り + Web検索)

    ユーザー権限別:
        viewer      : 閲覧者 (読み取り専用)
        editor      : 編集者 (ファイル編集可)
        admin       : 管理者 (全ツール)
"""
import argparse
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage, TextBlock, ToolUseBlock

# =============================================================================
# 基本モード
# =============================================================================

# 読み取り専用モード
READ_ONLY_OPTIONS = ClaudeAgentOptions(
    allowed_tools=["Read", "Glob", "Grep"]
)

# ファイル操作モード
FILE_OPS_OPTIONS = ClaudeAgentOptions(
    allowed_tools=["Read", "Write", "Edit", "Glob", "Grep"]
)

# フルアクセスモード
FULL_ACCESS_OPTIONS = ClaudeAgentOptions(
    allowed_tools=[
        "Read", "Write", "Edit",
        "Bash", "Glob", "Grep",
        "WebSearch", "WebFetch", "Task"
    ]
)

# =============================================================================
# ユースケース別モード
# =============================================================================

# コードレビュー用
CODE_REVIEW_OPTIONS = ClaudeAgentOptions(
    system_prompt="あなたはコードレビューの専門家です。コードを分析し、問題点を指摘してください。",
    allowed_tools=["Read", "Glob", "Grep"]
)

# ドキュメント作成用
DOC_WRITER_OPTIONS = ClaudeAgentOptions(
    system_prompt="あなたは技術ドキュメントの専門家です。",
    allowed_tools=["Read", "Write", "Glob", "Grep"]
)

# 開発作業用
DEVELOPMENT_OPTIONS = ClaudeAgentOptions(
    allowed_tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep"],
    permission_mode="acceptEdits"
)

# リサーチ用
RESEARCH_OPTIONS = ClaudeAgentOptions(
    system_prompt="技術調査を行い、結果をまとめてください。",
    allowed_tools=["Read", "Write", "WebSearch", "WebFetch", "Glob"]
)

# =============================================================================
# ユーザー権限別モード
# =============================================================================

# 閲覧者 (Viewer)
VIEWER_OPTIONS = ClaudeAgentOptions(
    allowed_tools=["Read", "Glob", "Grep"]
)

# 編集者 (Editor)
EDITOR_OPTIONS = ClaudeAgentOptions(
    allowed_tools=["Read", "Write", "Edit", "Glob", "Grep"]
)

# 管理者 (Admin)
ADMIN_OPTIONS = ClaudeAgentOptions(
    allowed_tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep", "WebSearch", "WebFetch"]
)

# =============================================================================
# モード名からオプションへのマッピング
# =============================================================================

MODE_OPTIONS = {
    # 基本モード
    "read-only": READ_ONLY_OPTIONS,
    "file-ops": FILE_OPS_OPTIONS,
    "full-access": FULL_ACCESS_OPTIONS,
    # ユースケース別
    "code-review": CODE_REVIEW_OPTIONS,
    "doc-writer": DOC_WRITER_OPTIONS,
    "development": DEVELOPMENT_OPTIONS,
    "research": RESEARCH_OPTIONS,
    # ユーザー権限別
    "viewer": VIEWER_OPTIONS,
    "editor": EDITOR_OPTIONS,
    "admin": ADMIN_OPTIONS,
}


MODE_DESCRIPTIONS = {
    "read-only": "読み取り専用",
    "file-ops": "ファイル操作",
    "full-access": "フルアクセス",
    "code-review": "コードレビュー用",
    "doc-writer": "ドキュメント作成用",
    "development": "開発作業用",
    "research": "リサーチ用",
    "viewer": "閲覧者権限",
    "editor": "編集者権限",
    "admin": "管理者権限",
}


def parse_args() -> argparse.Namespace:
    """コマンドライン引数をパース"""
    # モード一覧の文字列を生成
    mode_help_lines = ["利用可能なモード:"]
    mode_help_lines.append("  [基本] read-only, file-ops, full-access")
    mode_help_lines.append("  [ユースケース] code-review, doc-writer, development, research")
    mode_help_lines.append("  [権限別] viewer, editor, admin")

    parser = argparse.ArgumentParser(
        description="allowed_tools の設定例",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="\n".join(mode_help_lines)
    )
    parser.add_argument(
        "-m", "--mode",
        choices=list(MODE_OPTIONS.keys()),
        default="read-only",
        help="パーミッションモード (default: read-only)"
    )
    parser.add_argument(
        "-p", "--prompt",
        default="このディレクトリの Python ファイルを探して内容を確認してください",
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
    print("利用可能なモード一覧")
    print("=" * 60)

    for mode_name, options in MODE_OPTIONS.items():
        desc = MODE_DESCRIPTIONS.get(mode_name, "")
        print(f"\n[{mode_name}] {desc}")
        print(f"  allowed_tools: {options.allowed_tools}")
        if options.system_prompt:
            print(f"  system_prompt: {options.system_prompt[:50]}...")
        if options.permission_mode:
            print(f"  permission_mode: {options.permission_mode}")


async def main():
    """コマンドライン引数に基づいて実行"""
    args = parse_args()

    # --list-modes オプション
    if args.list_modes:
        print_mode_details()
        return

    options = MODE_OPTIONS[args.mode]
    desc = MODE_DESCRIPTIONS.get(args.mode, "")

    print("=" * 60)
    print(f"モード: {args.mode} ({desc})")
    print(f"allowed_tools: {options.allowed_tools}")
    if options.system_prompt:
        print(f"system_prompt: {options.system_prompt}")
    if options.permission_mode:
        print(f"permission_mode: {options.permission_mode}")
    print("-" * 60)
    print(f"プロンプト: {args.prompt}")
    print("=" * 60)

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
                    print(f"[Tool] {block.name}: {block.input}")

        elif isinstance(message, ResultMessage):
            print("=== ResultMessage ===")
            # subtype をチェックしてからメンバ変数にアクセス
            if message.subtype == "success":
                print(f"セッションID: {message.result}")
            else:
                print(f"subtype: {message.subtype}")


if __name__ == "__main__":
    asyncio.run(main())
