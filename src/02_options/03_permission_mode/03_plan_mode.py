"""
plan モード（ドライラン）の使用例

Usage:
    python 03_plan_mode.py --prompt "テストを実行して修正して"
    python 03_plan_mode.py --review --prompt "README.mdを更新して"
    python 03_plan_mode.py --compare --prompt "src/を分析して"

Features:
    --review  : プランニング後に確認し、承認後に実行
    --compare : plan モードと acceptEdits モードの結果を比較

plan モードでは、Claude は実行計画を立てますが、
実際のツール実行は行いません。
"""
import argparse
import asyncio
from claude_agent_sdk import (
    ClaudeAgentOptions,
    query,
    AssistantMessage,
    ResultMessage,
    TextBlock,
    ToolUseBlock
)

# =============================================================================
# オプション定義
# =============================================================================

PLAN_OPTIONS = ClaudeAgentOptions(
    permission_mode="plan",
    allowed_tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep"]
)

EXECUTE_OPTIONS = ClaudeAgentOptions(
    permission_mode="acceptEdits",
    allowed_tools=["Read", "Write", "Edit", "Glob", "Grep"]
)


def parse_args() -> argparse.Namespace:
    """コマンドライン引数をパース"""
    parser = argparse.ArgumentParser(
        description="plan モード（ドライラン）の使用例"
    )
    parser.add_argument(
        "-p", "--prompt",
        default="このプロジェクトを分析して改善点を提案してください",
        help="実行するプロンプト"
    )
    parser.add_argument(
        "--review",
        action="store_true",
        help="プランニング後に確認し、承認後に実行"
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="plan モードと acceptEdits モードの結果を比較"
    )
    return parser.parse_args()


async def simple_plan(prompt: str):
    """シンプルなプランニング"""
    print("=" * 60)
    print("plan モード（ドライラン）")
    print("=" * 60)
    print(f"プロンプト: {prompt}")
    print("-" * 60)
    print("注意: plan モードでは実際のツール実行は行われません")
    print("=" * 60)

    async for message in query(prompt=prompt, options=PLAN_OPTIONS):
        if isinstance(message, AssistantMessage):
            print("\n=== 実行計画 ===")
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)
                elif isinstance(block, ToolUseBlock):
                    print(f"\n[計画されたツール呼び出し]")
                    print(f"  ツール: {block.name}")
                    print(f"  入力: {block.input}")
                    print("  -> plan モードのため実行されません")

        elif isinstance(message, ResultMessage):
            print("\n" + "=" * 60)
            print("プランニング完了")
            print(f"計画されたターン: {message.num_turns}")
            print(f"コスト: ${message.total_cost_usd:.4f}")


async def review_and_execute(prompt: str):
    """プランニング後に確認し、承認後に実行"""
    print("=" * 60)
    print("実行前レビューモード")
    print("=" * 60)
    print(f"プロンプト: {prompt}")
    print("=" * 60)

    # Step 1: プランニング
    print("\n" + "=" * 60)
    print("Step 1: プランニング (plan モード)")
    print("=" * 60)

    plan_text = []
    async for message in query(prompt=prompt, options=PLAN_OPTIONS):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    plan_text.append(block.text)
                    print(block.text)
                elif isinstance(block, ToolUseBlock):
                    tool_info = f"\n[ツール: {block.name}] {block.input}"
                    plan_text.append(tool_info)
                    print(tool_info)

        elif isinstance(message, ResultMessage):
            print(f"\n計画コスト: ${message.total_cost_usd:.4f}")

    # Step 2: 確認
    print("\n" + "=" * 60)
    print("Step 2: 確認")
    print("=" * 60)

    try:
        approval = input("\nこの計画を実行しますか？ (y/n): ")
    except EOFError:
        approval = "n"

    if approval.lower() != "y":
        print("\nキャンセルしました")
        return

    # Step 3: 実行
    print("\n" + "=" * 60)
    print("Step 3: 実行 (acceptEdits モード)")
    print("=" * 60)

    async for message in query(prompt=prompt, options=EXECUTE_OPTIONS):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)
                elif isinstance(block, ToolUseBlock):
                    print(f"\n[実行] {block.name}")

        elif isinstance(message, ResultMessage):
            print("\n" + "=" * 60)
            print("実行完了")
            print(f"使用ターン: {message.num_turns}")
            print(f"コスト: ${message.total_cost_usd:.4f}")


async def compare_modes(prompt: str):
    """plan モードと acceptEdits モードを比較"""
    print("=" * 60)
    print("モード比較")
    print("=" * 60)
    print(f"プロンプト: {prompt}")
    print("=" * 60)

    results = {}

    # plan モード
    print("\n" + "=" * 60)
    print("【plan モード】")
    print("=" * 60)

    plan_tools = []
    async for message in query(prompt=prompt, options=PLAN_OPTIONS):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    # 最初の100文字のみ
                    text = block.text[:100] + "..." if len(block.text) > 100 else block.text
                    print(f"[Text] {text}")
                elif isinstance(block, ToolUseBlock):
                    plan_tools.append(block.name)
                    print(f"[計画ツール] {block.name}")

        elif isinstance(message, ResultMessage):
            results["plan"] = {
                "turns": message.num_turns,
                "cost": message.total_cost_usd,
                "tools": plan_tools
            }

    # acceptEdits モード
    print("\n" + "=" * 60)
    print("【acceptEdits モード】")
    print("=" * 60)

    exec_tools = []
    async for message in query(prompt=prompt, options=EXECUTE_OPTIONS):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    text = block.text[:100] + "..." if len(block.text) > 100 else block.text
                    print(f"[Text] {text}")
                elif isinstance(block, ToolUseBlock):
                    exec_tools.append(block.name)
                    print(f"[実行ツール] {block.name}")

        elif isinstance(message, ResultMessage):
            results["execute"] = {
                "turns": message.num_turns,
                "cost": message.total_cost_usd,
                "tools": exec_tools
            }

    # 比較結果
    print("\n" + "=" * 60)
    print("比較結果")
    print("=" * 60)

    if "plan" in results and "execute" in results:
        print(f"\n{'項目':<20} {'plan':<15} {'acceptEdits':<15}")
        print("-" * 50)
        print(f"{'ターン数':<20} {results['plan']['turns']:<15} {results['execute']['turns']:<15}")
        print(f"{'コスト':<20} ${results['plan']['cost']:.4f}{'':>8} ${results['execute']['cost']:.4f}")
        print(f"{'ツール呼び出し数':<20} {len(results['plan']['tools']):<15} {len(results['execute']['tools']):<15}")

        print("\n[plan モードで計画されたツール]")
        for tool in results["plan"]["tools"]:
            print(f"  - {tool}")

        print("\n[acceptEdits モードで実行されたツール]")
        for tool in results["execute"]["tools"]:
            print(f"  - {tool}")


async def main():
    args = parse_args()

    if args.review:
        await review_and_execute(args.prompt)
    elif args.compare:
        await compare_modes(args.prompt)
    else:
        await simple_plan(args.prompt)


if __name__ == "__main__":
    asyncio.run(main())
