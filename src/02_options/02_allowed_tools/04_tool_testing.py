"""
ツール制限のテスト (手順6)

許可されていないツールの動作確認やツール使用状況のモニタリングを行います。

Usage:
    # 許可されていないツールの動作確認
    python 04_tool_testing.py --test-restriction
    python 04_tool_testing.py --test-restriction -p "hello.py を作成して"

    # ツール使用状況のモニタリング
    python 04_tool_testing.py --monitor -p "プロジェクトの構造を分析して"
    python 04_tool_testing.py --monitor --tools Read,Glob,Grep,Edit

    # カスタムツールセットでテスト
    python 04_tool_testing.py --tools Read,Glob -p "ファイルを作成して"
"""
import argparse
import asyncio
from collections import Counter
from claude_agent_sdk import (
    ClaudeAgentOptions,
    query,
    AssistantMessage,
    ResultMessage,
    TextBlock,
    ToolUseBlock
)

# =============================================================================
# テスト用のツール設定
# =============================================================================

# 読み取り専用 (Write を禁止)
READ_ONLY_TOOLS = ["Read", "Glob", "Grep"]

# 編集なし (Edit を禁止)
NO_EDIT_TOOLS = ["Read", "Write", "Glob", "Grep"]

# Bash なし
NO_BASH_TOOLS = ["Read", "Write", "Edit", "Glob", "Grep"]


def parse_args() -> argparse.Namespace:
    """コマンドライン引数をパース"""
    parser = argparse.ArgumentParser(
        description="ツール制限のテスト",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--test-restriction",
        action="store_true",
        help="許可されていないツールの動作確認 (Write を禁止してファイル作成を要求)"
    )
    mode_group.add_argument(
        "--monitor",
        action="store_true",
        help="ツール使用状況をモニタリング"
    )

    parser.add_argument(
        "--tools",
        type=str,
        help="カンマ区切りのツールリスト (例: Read,Glob,Grep)"
    )
    parser.add_argument(
        "-p", "--prompt",
        help="実行するプロンプト"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="詳細出力"
    )

    return parser.parse_args()


async def test_tool_restriction(tools: list[str], prompt: str, verbose: bool = False):
    """
    許可されていないツールの動作確認

    指定されたツールのみを許可し、それ以外のツールが必要なタスクを要求した際の
    Claude の応答を確認します。
    """
    options = ClaudeAgentOptions(allowed_tools=tools)

    print("=" * 60)
    print("ツール制限テスト")
    print("=" * 60)
    print(f"allowed_tools: {tools}")
    print(f"プロンプト: {prompt}")
    print("-" * 60)

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"\n[Claude の応答]\n{block.text}")
                elif isinstance(block, ToolUseBlock):
                    if verbose:
                        print(f"\n[ツール使用] {block.name}: {block.input}")

        elif isinstance(message, ResultMessage):
            if verbose:
                print(f"\n[Result] subtype: {message.subtype}")


async def monitor_tool_usage(tools: list[str], prompt: str, verbose: bool = False):
    """
    ツール使用状況をモニタリング

    実行中に使用されたツールをカウントし、統計を表示します。
    """
    options = ClaudeAgentOptions(allowed_tools=tools)
    tool_counter = Counter()
    tool_details = []

    print("=" * 60)
    print("ツール使用状況モニタリング")
    print("=" * 60)
    print(f"allowed_tools: {tools}")
    print(f"プロンプト: {prompt}")
    print("-" * 60)
    print("\n[実行中...]\n")

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    if verbose:
                        print(f"[Text] {block.text[:100]}...")
                elif isinstance(block, ToolUseBlock):
                    tool_counter[block.name] += 1
                    tool_details.append({
                        "name": block.name,
                        "input": block.input
                    })
                    print(f"  -> {block.name} を使用")

        elif isinstance(message, ResultMessage):
            pass

    # 統計を表示
    print("\n" + "=" * 60)
    print("ツール使用統計")
    print("=" * 60)

    if tool_counter:
        total = sum(tool_counter.values())
        print(f"\n合計ツール呼び出し: {total} 回\n")

        for tool, count in tool_counter.most_common():
            percentage = (count / total) * 100
            bar = "#" * int(percentage / 5)
            print(f"  {tool:15} : {count:3} 回 ({percentage:5.1f}%) {bar}")

        # 未使用ツールを表示
        unused = set(tools) - set(tool_counter.keys())
        if unused:
            print(f"\n未使用ツール: {list(unused)}")
    else:
        print("ツールは使用されませんでした。")

    if verbose and tool_details:
        print("\n" + "-" * 60)
        print("詳細ログ:")
        for i, detail in enumerate(tool_details, 1):
            print(f"\n  [{i}] {detail['name']}")
            input_str = str(detail['input'])
            if len(input_str) > 100:
                input_str = input_str[:100] + "..."
            print(f"      input: {input_str}")

    return tool_counter


async def main():
    """メイン処理"""
    args = parse_args()

    # ツールリストを決定
    if args.tools:
        tools = [t.strip() for t in args.tools.split(",")]
    else:
        tools = READ_ONLY_TOOLS

    # テスト制限モード
    if args.test_restriction:
        prompt = args.prompt or "hello.py というファイルを作成してください"
        await test_tool_restriction(tools, prompt, args.verbose)

    # モニタリングモード
    elif args.monitor:
        prompt = args.prompt or "プロジェクトの構造を分析して"
        await monitor_tool_usage(tools, prompt, args.verbose)

    # デフォルト: テスト制限モード
    else:
        print("使用方法:")
        print("  --test-restriction : 許可されていないツールの動作確認")
        print("  --monitor          : ツール使用状況をモニタリング")
        print("\n例:")
        print("  python 04_tool_testing.py --test-restriction")
        print("  python 04_tool_testing.py --monitor -p 'コードを分析して'")
        print("  python 04_tool_testing.py --tools Read,Glob -p 'ファイルを作成して'")


if __name__ == "__main__":
    asyncio.run(main())
