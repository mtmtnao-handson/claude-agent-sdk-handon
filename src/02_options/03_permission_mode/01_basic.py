"""
permission_mode の基本設定例

Usage:
    python 01_basic.py --mode default --prompt "ファイル一覧を表示して"
    python 01_basic.py -m acceptEdits -p "README.mdを作成して"
    python 01_basic.py -m plan -p "プロジェクトを調査して"
    python 01_basic.py -m bypassPermissions -p "テストを実行して"

Available modes:
    default           : ツール実行時に確認を求める（対話的な作業向け）
    acceptEdits       : ファイル編集を自動承認（開発作業向け）
    plan              : プランニングのみ、実行なし（ドライラン）
    bypassPermissions : 全操作を自動承認（CI/CD 自動化向け）

安全性: plan > default > acceptEdits > bypassPermissions
"""
import argparse
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage, TextBlock, ToolUseBlock

# =============================================================================
# 権限モード別のオプション定義
# =============================================================================

# default モード: 対話的な確認
DEFAULT_OPTIONS = ClaudeAgentOptions(
    permission_mode="default",
    allowed_tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep"]
)

# acceptEdits モード: ファイル編集を自動承認
ACCEPT_EDITS_OPTIONS = ClaudeAgentOptions(
    permission_mode="acceptEdits",
    allowed_tools=["Read", "Write", "Edit", "Glob", "Grep"]
)

# plan モード: プランニングのみ
PLAN_OPTIONS = ClaudeAgentOptions(
    permission_mode="plan",
    allowed_tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep"]
)

# bypassPermissions モード: 全操作を自動承認
BYPASS_OPTIONS = ClaudeAgentOptions(
    permission_mode="bypassPermissions",
    allowed_tools=["Read", "Write", "Edit", "Glob", "Grep"]  # Bash は除外
)

# =============================================================================
# モード名からオプションへのマッピング
# =============================================================================

MODE_OPTIONS = {
    "default": DEFAULT_OPTIONS,
    "acceptEdits": ACCEPT_EDITS_OPTIONS,
    "plan": PLAN_OPTIONS,
    "bypassPermissions": BYPASS_OPTIONS,
}

MODE_DESCRIPTIONS = {
    "default": "対話的確認（全ツールで確認を求める）",
    "acceptEdits": "ファイル編集を自動承認",
    "plan": "プランニングのみ（実行なし）",
    "bypassPermissions": "全操作を自動承認（注意が必要）",
}

MODE_SAFETY = {
    "default": "中程度",
    "acceptEdits": "低",
    "plan": "高（最も安全）",
    "bypassPermissions": "最低（注意が必要）",
}


def parse_args() -> argparse.Namespace:
    """コマンドライン引数をパース"""
    mode_help_lines = [
        "利用可能なモード:",
        "  default           - ツール実行時に確認（対話的作業向け）",
        "  acceptEdits       - ファイル編集を自動承認（開発作業向け）",
        "  plan              - プランニングのみ（ドライラン）",
        "  bypassPermissions - 全操作を自動承認（CI/CD向け）",
        "",
        "安全性: plan > default > acceptEdits > bypassPermissions"
    ]

    parser = argparse.ArgumentParser(
        description="permission_mode の設定例",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="\n".join(mode_help_lines)
    )
    parser.add_argument(
        "-m", "--mode",
        choices=list(MODE_OPTIONS.keys()),
        default="default",
        help="権限モード (default: default)"
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
    print("利用可能な権限モード一覧")
    print("=" * 60)

    # 安全性の順に表示
    safety_order = ["plan", "default", "acceptEdits", "bypassPermissions"]

    for mode_name in safety_order:
        options = MODE_OPTIONS[mode_name]
        desc = MODE_DESCRIPTIONS.get(mode_name, "")
        safety = MODE_SAFETY.get(mode_name, "")

        print(f"\n[{mode_name}]")
        print(f"  説明: {desc}")
        print(f"  安全性: {safety}")
        print(f"  allowed_tools: {options.allowed_tools}")

    print("\n" + "=" * 60)
    print("安全性の比較:")
    print("  高 ◄──────────────────────────► 低")
    print("  plan > default > acceptEdits > bypassPermissions")
    print("=" * 60)


async def main():
    """コマンドライン引数に基づいて実行"""
    args = parse_args()

    # --list-modes オプション
    if args.list_modes:
        print_mode_details()
        return

    options = MODE_OPTIONS[args.mode]
    desc = MODE_DESCRIPTIONS.get(args.mode, "")
    safety = MODE_SAFETY.get(args.mode, "")

    print("=" * 60)
    print(f"権限モード: {args.mode}")
    print(f"説明: {desc}")
    print(f"安全性: {safety}")
    print(f"allowed_tools: {options.allowed_tools}")
    print("-" * 60)
    print(f"プロンプト: {args.prompt}")
    print("=" * 60)

    # bypassPermissions の警告
    if args.mode == "bypassPermissions":
        print("\n" + "!" * 60)
        print("警告: bypassPermissions モードは全操作を自動承認します。")
        print("隔離された環境でのみ使用してください。")
        print("!" * 60 + "\n")

    async for message in query(
        prompt=args.prompt,
        options=options
    ):
        if isinstance(message, AssistantMessage):
            print("\n=== AssistantMessage ===")
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"[Text] {block.text}")
                elif isinstance(block, ToolUseBlock):
                    print(f"[Tool] {block.name}: {block.input}")

        elif isinstance(message, ResultMessage):
            print("\n=== ResultMessage ===")
            print(f"使用ターン: {message.num_turns}")
            print(f"コスト: ${message.total_cost_usd:.4f}")
            if message.subtype == "success":
                print(f"セッションID: {message.result}")
            else:
                print(f"subtype: {message.subtype}")


if __name__ == "__main__":
    asyncio.run(main())
