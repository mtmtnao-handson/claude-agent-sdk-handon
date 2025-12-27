"""
bypassPermissions モードの使用例

Usage:
    python 04_bypass.py --safe --prompt "テンプレートファイルを作成して"
    python 04_bypass.py --ci --prompt "テストを実行して"
    python 04_bypass.py --sandbox --prompt "スクリプトを実行して"

Modes:
    --safe    : 一時ディレクトリで安全に実行（Bash 除外）
    --ci      : CI/CD 環境での使用例
    --sandbox : サンドボックス環境での使用例

警告: bypassPermissions は全ての確認をスキップします。
以下の条件を満たす場合のみ使用してください：
- 隔離された環境（コンテナ、サンドボックス）
- 信頼できるプロンプトのみを使用
- allowed_tools を厳格に制限
"""
import argparse
import asyncio
import os
import tempfile
from claude_agent_sdk import (
    ClaudeAgentOptions,
    query,
    AssistantMessage,
    ResultMessage,
    TextBlock,
    ToolUseBlock
)


def parse_args() -> argparse.Namespace:
    """コマンドライン引数をパース"""
    parser = argparse.ArgumentParser(
        description="bypassPermissions モードの使用例"
    )
    parser.add_argument(
        "-p", "--prompt",
        default="sample.txt ファイルを作成し、Hello World と書き込んでください",
        help="実行するプロンプト"
    )
    parser.add_argument(
        "--safe",
        action="store_true",
        help="一時ディレクトリで安全に実行（Bash 除外）"
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="CI/CD 環境での使用例"
    )
    parser.add_argument(
        "--sandbox",
        action="store_true",
        help="サンドボックス環境での使用例"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="警告を無視して実行"
    )
    return parser.parse_args()


def print_warning():
    """警告を表示"""
    print("!" * 60)
    print("警告: bypassPermissions モード")
    print("!" * 60)
    print("""
このモードは全ての確認をスキップします。
以下のリスクを理解した上で使用してください：

1. ファイルの作成・編集が自動承認されます
2. シェルコマンドが自動実行されます（許可している場合）
3. 予期しない変更が発生する可能性があります

安全な使用のためのガイドライン：
- 隔離された環境（コンテナ、VM）で使用
- 一時ディレクトリで作業
- Bash ツールを除外することを検討
- allowed_tools を最小限に制限
""")
    print("!" * 60)


async def safe_automation(prompt: str):
    """一時ディレクトリで安全に自動実行"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        print("=" * 60)
        print("安全な自動化モード")
        print("=" * 60)
        print(f"作業ディレクトリ: {tmp_dir}")
        print("Bash ツール: 除外")
        print("-" * 60)
        print(f"プロンプト: {prompt}")
        print("=" * 60)

        # Bash を除外したオプション
        options = ClaudeAgentOptions(
            permission_mode="bypassPermissions",
            cwd=tmp_dir,
            allowed_tools=["Read", "Write", "Edit", "Glob"]  # Bash 除外
        )

        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"[Text] {block.text[:200]}...")
                    elif isinstance(block, ToolUseBlock):
                        print(f"[Tool] {block.name} -> 自動承認")

            elif isinstance(message, ResultMessage):
                print("\n" + "=" * 60)
                print("完了")
                print(f"使用ターン: {message.num_turns}")
                print(f"コスト: ${message.total_cost_usd:.4f}")

        # 結果を確認
        print("\n" + "=" * 60)
        print("作成されたファイル:")
        print("=" * 60)
        for root, dirs, files in os.walk(tmp_dir):
            for f in files:
                filepath = os.path.join(root, f)
                relpath = os.path.relpath(filepath, tmp_dir)
                size = os.path.getsize(filepath)
                print(f"  {relpath} ({size} bytes)")

        print("\n注意: 一時ディレクトリは終了時に自動削除されます")


async def ci_mode(prompt: str):
    """CI/CD 環境での使用例"""
    # CI 環境の検出
    is_ci = os.getenv("CI", "").lower() == "true"
    github_actions = os.getenv("GITHUB_ACTIONS", "").lower() == "true"

    print("=" * 60)
    print("CI/CD モード")
    print("=" * 60)
    print(f"CI 環境検出: {is_ci}")
    print(f"GitHub Actions: {github_actions}")
    print("-" * 60)

    if not is_ci and not github_actions:
        print("\n警告: CI 環境が検出されませんでした")
        print("環境変数 CI=true を設定してシミュレートします")
        print()

    # CI 環境用のオプション
    options = ClaudeAgentOptions(
        permission_mode="bypassPermissions" if (is_ci or github_actions) else "default",
        allowed_tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep"],
        max_turns=30
    )

    print(f"permission_mode: {options.permission_mode}")
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
                    if options.permission_mode == "bypassPermissions":
                        print(f"[CI] {block.name} -> 自動承認")
                    else:
                        print(f"[Tool] {block.name}")

        elif isinstance(message, ResultMessage):
            print("\n" + "=" * 60)
            print("完了")
            print(f"使用ターン: {message.num_turns}")
            print(f"コスト: ${message.total_cost_usd:.4f}")


async def sandbox_mode(prompt: str):
    """サンドボックス環境での使用例"""
    print("=" * 60)
    print("サンドボックスモード")
    print("=" * 60)
    print("""
このモードは以下の制限を適用します：
- 読み取り専用ツールのみ許可
- Bash は除外
- Write/Edit は除外

これにより、bypassPermissions を使用しながらも
システムへの変更を防止します。
""")
    print("-" * 60)
    print(f"プロンプト: {prompt}")
    print("=" * 60)

    # サンドボックス用オプション（読み取り専用）
    options = ClaudeAgentOptions(
        permission_mode="bypassPermissions",
        allowed_tools=["Read", "Glob", "Grep"]  # 読み取り専用
    )

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)
                elif isinstance(block, ToolUseBlock):
                    print(f"[Sandbox] {block.name}")

        elif isinstance(message, ResultMessage):
            print("\n" + "=" * 60)
            print("完了")
            print(f"使用ターン: {message.num_turns}")
            print(f"コスト: ${message.total_cost_usd:.4f}")


async def main():
    args = parse_args()

    # 警告表示（--force がない場合）
    if not args.force and not (args.safe or args.ci or args.sandbox):
        print_warning()
        try:
            confirm = input("\n続行しますか？ (y/n): ")
        except EOFError:
            confirm = "n"

        if confirm.lower() != "y":
            print("キャンセルしました")
            return

    if args.safe:
        await safe_automation(args.prompt)
    elif args.ci:
        await ci_mode(args.prompt)
    elif args.sandbox:
        await sandbox_mode(args.prompt)
    else:
        # デフォルトは safe モード
        await safe_automation(args.prompt)


if __name__ == "__main__":
    asyncio.run(main())
