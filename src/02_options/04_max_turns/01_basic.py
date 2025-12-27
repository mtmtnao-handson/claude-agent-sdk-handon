"""
max_turns の基本設定例

Usage:
    python 01_basic.py --mode qa --prompt "Pythonとは何ですか？"
    python 01_basic.py -m file-read -p "README.mdを読んで要約して"
    python 01_basic.py -m code-gen -p "hello.pyを作成して"
    python 01_basic.py -m refactor -p "src/を分析して改善点を提案して"

Available modes:
    基本モード:
        qa          : Q&A用 (max_turns=3)
        file-read   : ファイル読み取り用 (max_turns=10)
        code-gen    : コード生成用 (max_turns=20)
        refactor    : リファクタリング用 (max_turns=50)
        automation  : 自動化タスク用 (max_turns=100)

    ユースケース別:
        code-review : コードレビュー用 (max_turns=10)
        doc-writer  : ドキュメント作成用 (max_turns=15)
        development : 開発作業用 (max_turns=30)
        analysis    : 大規模分析用 (max_turns=50)
"""
import argparse
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage, TextBlock, ToolUseBlock

# =============================================================================
# 基本モード（ターン数による分類）
# =============================================================================

# Q&A用（シンプルな質問応答）
QA_OPTIONS = ClaudeAgentOptions(
    max_turns=3,
    allowed_tools=[]  # ツールなし
)

# ファイル読み取り用
FILE_READ_OPTIONS = ClaudeAgentOptions(
    max_turns=10,
    allowed_tools=["Read", "Glob", "Grep"]
)

# コード生成用
CODE_GEN_OPTIONS = ClaudeAgentOptions(
    max_turns=20,
    allowed_tools=["Read", "Write", "Edit", "Glob", "Grep"]
)

# リファクタリング用
REFACTOR_OPTIONS = ClaudeAgentOptions(
    max_turns=50,
    allowed_tools=["Read", "Write", "Edit", "Glob", "Grep"]
)

# 自動化タスク用
AUTOMATION_OPTIONS = ClaudeAgentOptions(
    max_turns=100,
    allowed_tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep"]
)

# =============================================================================
# ユースケース別モード
# =============================================================================

# コードレビュー用
CODE_REVIEW_OPTIONS = ClaudeAgentOptions(
    max_turns=10,
    system_prompt="あなたはコードレビューの専門家です。コードを分析し、問題点や改善点を指摘してください。",
    allowed_tools=["Read", "Glob", "Grep"]
)

# ドキュメント作成用
DOC_WRITER_OPTIONS = ClaudeAgentOptions(
    max_turns=15,
    system_prompt="あなたは技術ドキュメントの専門家です。わかりやすいドキュメントを作成してください。",
    allowed_tools=["Read", "Write", "Glob", "Grep"]
)

# 開発作業用
DEVELOPMENT_OPTIONS = ClaudeAgentOptions(
    max_turns=30,
    allowed_tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep"],
    permission_mode="acceptEdits"
)

# 大規模分析用
ANALYSIS_OPTIONS = ClaudeAgentOptions(
    max_turns=50,
    system_prompt="コードベース全体を分析し、詳細なレポートを作成してください。",
    allowed_tools=["Read", "Glob", "Grep"]
)

# =============================================================================
# モード名からオプションへのマッピング
# =============================================================================

MODE_OPTIONS = {
    # 基本モード
    "qa": QA_OPTIONS,
    "file-read": FILE_READ_OPTIONS,
    "code-gen": CODE_GEN_OPTIONS,
    "refactor": REFACTOR_OPTIONS,
    "automation": AUTOMATION_OPTIONS,
    # ユースケース別
    "code-review": CODE_REVIEW_OPTIONS,
    "doc-writer": DOC_WRITER_OPTIONS,
    "development": DEVELOPMENT_OPTIONS,
    "analysis": ANALYSIS_OPTIONS,
}

MODE_DESCRIPTIONS = {
    "qa": "Q&A用 (3ターン)",
    "file-read": "ファイル読み取り用 (10ターン)",
    "code-gen": "コード生成用 (20ターン)",
    "refactor": "リファクタリング用 (50ターン)",
    "automation": "自動化タスク用 (100ターン)",
    "code-review": "コードレビュー用 (10ターン)",
    "doc-writer": "ドキュメント作成用 (15ターン)",
    "development": "開発作業用 (30ターン)",
    "analysis": "大規模分析用 (50ターン)",
}


def parse_args() -> argparse.Namespace:
    """コマンドライン引数をパース"""
    mode_help_lines = ["利用可能なモード:"]
    mode_help_lines.append("  [基本] qa, file-read, code-gen, refactor, automation")
    mode_help_lines.append("  [ユースケース] code-review, doc-writer, development, analysis")

    parser = argparse.ArgumentParser(
        description="max_turns の設定例",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="\n".join(mode_help_lines)
    )
    parser.add_argument(
        "-m", "--mode",
        choices=list(MODE_OPTIONS.keys()),
        default="file-read",
        help="ターン数モード (default: file-read)"
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
        print(f"  max_turns: {options.max_turns}")
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
    print(f"max_turns: {options.max_turns}")
    print(f"allowed_tools: {options.allowed_tools}")
    if options.system_prompt:
        print(f"system_prompt: {options.system_prompt}")
    if options.permission_mode:
        print(f"permission_mode: {options.permission_mode}")
    print("-" * 60)
    print(f"プロンプト: {args.prompt}")
    print("=" * 60)

    turn_count = 0
    async for message in query(
        prompt=args.prompt,
        options=options
    ):
        if isinstance(message, AssistantMessage):
            turn_count += 1
            print(f"\n=== ターン {turn_count}/{options.max_turns} ===")
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"[Text] {block.text}")
                elif isinstance(block, ToolUseBlock):
                    print(f"[Tool] {block.name}: {block.input}")

        elif isinstance(message, ResultMessage):
            print("\n" + "=" * 60)
            print("=== 完了 ===")
            print(f"実際のターン数: {message.num_turns}")
            print(f"最大ターン数: {options.max_turns}")
            print(f"コスト: ${message.total_cost_usd:.4f}")
            if message.subtype == "success":
                print(f"セッションID: {message.result}")
            else:
                print(f"subtype: {message.subtype}")


if __name__ == "__main__":
    asyncio.run(main())
