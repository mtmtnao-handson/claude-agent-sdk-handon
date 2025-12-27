"""
acceptEdits モードの詳細な使用例

Usage:
    python 02_accept_edits.py --task refactor --file src/main.py
    python 02_accept_edits.py -t docstring -f utils.py
    python 02_accept_edits.py -t type-hints -f "*.py"
    python 02_accept_edits.py --workflow dev

Available tasks:
    refactor   : コードのリファクタリング
    docstring  : docstring の追加
    type-hints : 型ヒントの追加
    cleanup    : コードのクリーンアップ

Workflows:
    dev        : 開発作業用の設定
    review     : コードレビュー用の設定

acceptEdits モードは Read, Write, Edit を自動承認しますが、
Bash などの他のツールは引き続き確認が必要です。
"""
import argparse
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage, TextBlock, ToolUseBlock

# =============================================================================
# タスク別の設定
# =============================================================================

# リファクタリング用
REFACTOR_OPTIONS = ClaudeAgentOptions(
    permission_mode="acceptEdits",
    allowed_tools=["Read", "Write", "Edit", "Glob", "Grep"],
    system_prompt="""あなたは経験豊富なソフトウェアエンジニアです。
コードのリファクタリングを行う際は：
- 既存の機能を壊さないように注意
- 可読性と保守性を向上
- 適切なコメントを追加
"""
)

# docstring 追加用
DOCSTRING_OPTIONS = ClaudeAgentOptions(
    permission_mode="acceptEdits",
    allowed_tools=["Read", "Write", "Edit", "Glob"],
    system_prompt="""あなたは技術ドキュメントの専門家です。
Pythonの docstring を追加する際は：
- Google スタイルの docstring を使用
- 引数、戻り値、例外を明記
- 使用例を含める
"""
)

# 型ヒント追加用
TYPE_HINTS_OPTIONS = ClaudeAgentOptions(
    permission_mode="acceptEdits",
    allowed_tools=["Read", "Write", "Edit", "Glob"],
    system_prompt="""あなたは Python の型システムの専門家です。
型ヒントを追加する際は：
- typing モジュールを適切に使用
- Optional, Union, List, Dict などを活用
- 複雑な型には TypeAlias を検討
"""
)

# クリーンアップ用
CLEANUP_OPTIONS = ClaudeAgentOptions(
    permission_mode="acceptEdits",
    allowed_tools=["Read", "Write", "Edit", "Glob", "Grep"],
    system_prompt="""あなたはコード品質の専門家です。
コードのクリーンアップを行う際は：
- 未使用のインポートを削除
- 未使用の変数を削除
- フォーマットを整理（PEP 8準拠）
"""
)

# =============================================================================
# ワークフロー別の設定
# =============================================================================

# 開発作業用
DEV_WORKFLOW_OPTIONS = ClaudeAgentOptions(
    permission_mode="acceptEdits",
    allowed_tools=["Read", "Write", "Edit", "Glob", "Grep"],
    system_prompt="あなたは経験豊富な Python 開発者です。",
    max_turns=30
)

# コードレビュー用（読み取りのみ）
REVIEW_WORKFLOW_OPTIONS = ClaudeAgentOptions(
    permission_mode="acceptEdits",  # 読み取りは自動承認
    allowed_tools=["Read", "Glob", "Grep"],  # Write/Edit を除外
    system_prompt="""あなたはコードレビューの専門家です。
コードを分析し、以下の観点からフィードバックを提供してください：
- バグの可能性
- パフォーマンスの問題
- セキュリティの懸念
- コードスタイル
"""
)

# =============================================================================
# マッピング
# =============================================================================

TASK_OPTIONS = {
    "refactor": REFACTOR_OPTIONS,
    "docstring": DOCSTRING_OPTIONS,
    "type-hints": TYPE_HINTS_OPTIONS,
    "cleanup": CLEANUP_OPTIONS,
}

TASK_PROMPTS = {
    "refactor": "以下のファイルをリファクタリングしてください: {file}",
    "docstring": "以下のファイルに docstring を追加してください: {file}",
    "type-hints": "以下のファイルに型ヒントを追加してください: {file}",
    "cleanup": "以下のファイルをクリーンアップしてください: {file}",
}

WORKFLOW_OPTIONS = {
    "dev": DEV_WORKFLOW_OPTIONS,
    "review": REVIEW_WORKFLOW_OPTIONS,
}


def parse_args() -> argparse.Namespace:
    """コマンドライン引数をパース"""
    parser = argparse.ArgumentParser(
        description="acceptEdits モードの詳細な使用例"
    )
    parser.add_argument(
        "-t", "--task",
        choices=list(TASK_OPTIONS.keys()),
        help="実行するタスク"
    )
    parser.add_argument(
        "-f", "--file",
        default=".",
        help="対象ファイル (default: .)"
    )
    parser.add_argument(
        "-w", "--workflow",
        choices=list(WORKFLOW_OPTIONS.keys()),
        help="ワークフローモード"
    )
    parser.add_argument(
        "-p", "--prompt",
        help="カスタムプロンプト（タスクの代わりに使用）"
    )
    parser.add_argument(
        "-l", "--list",
        action="store_true",
        help="利用可能なタスクとワークフローを表示"
    )
    return parser.parse_args()


def print_available_options():
    """利用可能なオプションを表示"""
    print("=" * 60)
    print("acceptEdits モードの使用例")
    print("=" * 60)

    print("\n【タスク一覧】")
    for task, options in TASK_OPTIONS.items():
        print(f"\n  [{task}]")
        print(f"    system_prompt: {options.system_prompt[:50]}...")
        print(f"    allowed_tools: {options.allowed_tools}")

    print("\n【ワークフロー一覧】")
    for workflow, options in WORKFLOW_OPTIONS.items():
        print(f"\n  [{workflow}]")
        print(f"    system_prompt: {options.system_prompt[:50]}...")
        print(f"    allowed_tools: {options.allowed_tools}")
        if options.max_turns:
            print(f"    max_turns: {options.max_turns}")

    print("\n" + "=" * 60)
    print("Note: acceptEdits は Read, Write, Edit を自動承認します。")
    print("      Bash は引き続き確認が必要です。")
    print("=" * 60)


async def run_task(task: str, file: str):
    """タスクを実行"""
    options = TASK_OPTIONS[task]
    prompt = TASK_PROMPTS[task].format(file=file)

    print("=" * 60)
    print(f"タスク: {task}")
    print(f"対象ファイル: {file}")
    print(f"permission_mode: acceptEdits")
    print("-" * 60)
    print(f"プロンプト: {prompt}")
    print("=" * 60)

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            print("\n--- 処理中 ---")
            for block in message.content:
                if isinstance(block, TextBlock):
                    # 長いテキストは最初の200文字のみ
                    text = block.text[:200] + "..." if len(block.text) > 200 else block.text
                    print(f"[Text] {text}")
                elif isinstance(block, ToolUseBlock):
                    print(f"[Tool] {block.name}")
                    if block.name in ["Write", "Edit"]:
                        print("  -> 自動承認されました")

        elif isinstance(message, ResultMessage):
            print("\n" + "=" * 60)
            print("完了")
            print(f"使用ターン: {message.num_turns}")
            print(f"コスト: ${message.total_cost_usd:.4f}")


async def run_workflow(workflow: str, prompt: str = None):
    """ワークフローを実行"""
    options = WORKFLOW_OPTIONS[workflow]

    if prompt is None:
        if workflow == "dev":
            prompt = "このプロジェクトのコードを分析し、改善点があれば修正してください"
        elif workflow == "review":
            prompt = "このプロジェクトのコードをレビューし、フィードバックを提供してください"

    print("=" * 60)
    print(f"ワークフロー: {workflow}")
    print(f"permission_mode: acceptEdits")
    print(f"allowed_tools: {options.allowed_tools}")
    print("-" * 60)
    print(f"プロンプト: {prompt}")
    print("=" * 60)

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)
                elif isinstance(block, ToolUseBlock):
                    print(f"\n[ツール使用] {block.name}")

        elif isinstance(message, ResultMessage):
            print("\n" + "=" * 60)
            print("完了")
            print(f"使用ターン: {message.num_turns}")
            print(f"コスト: ${message.total_cost_usd:.4f}")


async def main():
    args = parse_args()

    if args.list:
        print_available_options()
        return

    if args.workflow:
        await run_workflow(args.workflow, args.prompt)
    elif args.task:
        await run_task(args.task, args.file)
    elif args.prompt:
        # カスタムプロンプトでデフォルトの acceptEdits を使用
        options = ClaudeAgentOptions(
            permission_mode="acceptEdits",
            allowed_tools=["Read", "Write", "Edit", "Glob", "Grep"]
        )
        print("=" * 60)
        print("カスタムプロンプト実行")
        print("permission_mode: acceptEdits")
        print("-" * 60)
        print(f"プロンプト: {args.prompt}")
        print("=" * 60)

        async for message in query(prompt=args.prompt, options=options):
            print(message)
    else:
        print("タスク (-t)、ワークフロー (-w)、またはプロンプト (-p) を指定してください")
        print("ヘルプ: python 02_accept_edits.py -h")
        print("一覧表示: python 02_accept_edits.py -l")


if __name__ == "__main__":
    asyncio.run(main())
