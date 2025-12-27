"""
動的なツール制御 (手順5)

タスクタイプやユーザー権限に応じて、動的にツールを選択する方法を示します。

Usage:
    # タスクタイプに基づく制御
    python 03_dynamic_control.py -t analyze -p "コードを分析して"
    python 03_dynamic_control.py -t document -p "ドキュメントを作成して"
    python 03_dynamic_control.py -t develop -p "機能を実装して"
    python 03_dynamic_control.py -t research -p "技術を調査して"

    # ユーザー権限に基づく制御
    python 03_dynamic_control.py -r viewer -p "ファイルを確認して"
    python 03_dynamic_control.py -r editor -p "ファイルを編集して"
    python 03_dynamic_control.py -r admin -p "システムを設定して"

    # オプション
    python 03_dynamic_control.py -l  # 利用可能な設定一覧
"""
import argparse
import asyncio
from enum import Enum
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage, TextBlock, ToolUseBlock

# =============================================================================
# タスクタイプに基づくツール選択
# =============================================================================

BASE_TOOLS = ["Read", "Glob", "Grep"]

TASK_TOOLS = {
    "analyze": BASE_TOOLS,
    "document": BASE_TOOLS + ["Write"],
    "develop": BASE_TOOLS + ["Write", "Edit", "Bash"],
    "research": BASE_TOOLS + ["WebSearch", "WebFetch"],
}

TASK_DESCRIPTIONS = {
    "analyze": "コード分析 (読み取り専用)",
    "document": "ドキュメント作成 (読み取り + Write)",
    "develop": "開発作業 (読み取り + 編集 + Bash)",
    "research": "技術調査 (読み取り + Web検索)",
}


def get_tools_for_task(task_type: str) -> list[str]:
    """タスクタイプに応じたツールリストを返す"""
    return TASK_TOOLS.get(task_type, BASE_TOOLS)


# =============================================================================
# ユーザー権限に基づくツール選択
# =============================================================================

class UserRole(Enum):
    VIEWER = "viewer"
    EDITOR = "editor"
    ADMIN = "admin"


ROLE_TOOLS = {
    UserRole.VIEWER: ["Read", "Glob", "Grep"],
    UserRole.EDITOR: ["Read", "Write", "Edit", "Glob", "Grep"],
    UserRole.ADMIN: ["Read", "Write", "Edit", "Bash", "Glob", "Grep", "WebSearch", "WebFetch"],
}

ROLE_DESCRIPTIONS = {
    UserRole.VIEWER: "閲覧者 (読み取り専用)",
    UserRole.EDITOR: "編集者 (ファイル編集可)",
    UserRole.ADMIN: "管理者 (全ツール)",
}


def get_tools_for_role(role: UserRole) -> list[str]:
    """ユーザー権限に応じたツールを返す"""
    return ROLE_TOOLS[role]


# =============================================================================
# コマンドライン引数処理
# =============================================================================

def parse_args() -> argparse.Namespace:
    """コマンドライン引数をパース"""
    parser = argparse.ArgumentParser(
        description="動的なツール制御の例",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-t", "--task-type",
        choices=list(TASK_TOOLS.keys()),
        help="タスクタイプ (analyze, document, develop, research)"
    )
    group.add_argument(
        "-r", "--role",
        choices=[r.value for r in UserRole],
        help="ユーザー権限 (viewer, editor, admin)"
    )

    parser.add_argument(
        "-p", "--prompt",
        default="利用可能なツールを確認して、何ができるか教えてください",
        help="実行するプロンプト"
    )
    parser.add_argument(
        "-l", "--list-modes",
        action="store_true",
        help="利用可能な設定一覧を表示して終了"
    )
    return parser.parse_args()


def print_all_modes():
    """全モードの詳細を表示"""
    print("=" * 60)
    print("動的ツール制御モード一覧")
    print("=" * 60)

    print("\n[タスクタイプベース] -t / --task-type")
    for task, tools in TASK_TOOLS.items():
        desc = TASK_DESCRIPTIONS.get(task, "")
        print(f"  {task}: {desc}")
        print(f"    tools: {tools}")

    print("\n[ユーザー権限ベース] -r / --role")
    for role in UserRole:
        desc = ROLE_DESCRIPTIONS.get(role, "")
        tools = ROLE_TOOLS[role]
        print(f"  {role.value}: {desc}")
        print(f"    tools: {tools}")


async def main():
    """コマンドライン引数に基づいて実行"""
    args = parse_args()

    if args.list_modes:
        print_all_modes()
        return

    # ツールとモード説明を決定
    if args.task_type:
        tools = get_tools_for_task(args.task_type)
        mode_name = f"task:{args.task_type}"
        mode_desc = TASK_DESCRIPTIONS.get(args.task_type, "")
    elif args.role:
        role = UserRole(args.role)
        tools = get_tools_for_role(role)
        mode_name = f"role:{args.role}"
        mode_desc = ROLE_DESCRIPTIONS.get(role, "")
    else:
        # デフォルト: analyze タスク
        tools = get_tools_for_task("analyze")
        mode_name = "task:analyze (default)"
        mode_desc = TASK_DESCRIPTIONS.get("analyze", "")

    options = ClaudeAgentOptions(allowed_tools=tools)

    print("=" * 60)
    print(f"モード: {mode_name}")
    print(f"説明: {mode_desc}")
    print(f"allowed_tools: {tools}")
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
            if message.subtype == "success":
                print(f"セッションID: {message.result}")
            else:
                print(f"subtype: {message.subtype}")


if __name__ == "__main__":
    asyncio.run(main())
