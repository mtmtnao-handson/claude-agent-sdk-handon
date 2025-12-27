"""
ターン数とコスト管理の組み合わせ

Usage:
    python 03_budget_control.py --max-cost 0.10 --max-turns 50
    python 03_budget_control.py -c 0.05 -t 30 --prompts "README.mdを読んで" "src/を分析して"
    python 03_budget_control.py --interactive

このスクリプトは、ターン数とコストの両方を予算として管理し、
どちらかの上限に達した時点で処理を停止します。
"""
import argparse
import asyncio
from dataclasses import dataclass, field
from typing import List
from claude_agent_sdk import ClaudeAgentOptions, query, ResultMessage, AssistantMessage, TextBlock


@dataclass
class BudgetManager:
    """ターン数とコストの予算を管理するクラス"""
    max_cost_usd: float
    max_turns: int
    total_cost: float = 0.0
    total_turns: int = 0
    query_history: List[dict] = field(default_factory=list)

    def check_budget(self, cost: float, turns: int) -> tuple[bool, str]:
        """
        予算内かどうかをチェック

        Returns:
            (is_within_budget, message)
        """
        self.total_cost += cost
        self.total_turns += turns

        self.query_history.append({
            "cost": cost,
            "turns": turns,
            "cumulative_cost": self.total_cost,
            "cumulative_turns": self.total_turns,
        })

        if self.total_cost > self.max_cost_usd:
            return False, f"コスト上限 (${self.max_cost_usd:.4f}) を超過: ${self.total_cost:.4f}"

        if self.total_turns > self.max_turns:
            return False, f"ターン上限 ({self.max_turns}) を超過: {self.total_turns}ターン"

        return True, "予算内"

    def get_remaining(self) -> dict:
        """残りの予算を取得"""
        return {
            "remaining_cost": max(0, self.max_cost_usd - self.total_cost),
            "remaining_turns": max(0, self.max_turns - self.total_turns),
            "cost_percentage": (self.total_cost / self.max_cost_usd) * 100 if self.max_cost_usd > 0 else 0,
            "turns_percentage": (self.total_turns / self.max_turns) * 100 if self.max_turns > 0 else 0,
        }

    def can_continue(self, min_turns: int = 1) -> bool:
        """処理を継続できるかどうかを判定"""
        remaining = self.get_remaining()
        return remaining["remaining_turns"] >= min_turns and remaining["remaining_cost"] > 0

    def print_status(self):
        """現在の予算状況を表示"""
        remaining = self.get_remaining()

        print("\n" + "-" * 40)
        print("💰 予算状況")
        print("-" * 40)
        print(f"  コスト:  ${self.total_cost:.4f} / ${self.max_cost_usd:.4f} ({remaining['cost_percentage']:.1f}%)")
        print(f"  ターン:  {self.total_turns} / {self.max_turns} ({remaining['turns_percentage']:.1f}%)")
        print(f"  残り:    ${remaining['remaining_cost']:.4f}, {remaining['remaining_turns']}ターン")
        print("-" * 40)

    def print_history(self):
        """クエリ履歴を表示"""
        if not self.query_history:
            print("履歴がありません")
            return

        print("\n" + "=" * 50)
        print("📜 クエリ履歴")
        print("=" * 50)

        for i, entry in enumerate(self.query_history, 1):
            print(f"\n  [{i}] コスト: ${entry['cost']:.4f}, ターン: {entry['turns']}")
            print(f"       累計: ${entry['cumulative_cost']:.4f}, {entry['cumulative_turns']}ターン")


async def budget_aware_query(
    prompt: str,
    budget: BudgetManager,
    turns_per_query: int = 10
) -> bool:
    """
    予算を考慮してクエリを実行

    Returns:
        処理が正常に完了したかどうか
    """
    remaining = budget.get_remaining()

    # 残りターンが足りない場合
    if remaining["remaining_turns"] < 1:
        print("⚠️ ターン予算が不足しています")
        return False

    # このクエリで使用するターン数を決定
    turns_to_use = min(turns_per_query, remaining["remaining_turns"])

    options = ClaudeAgentOptions(
        max_turns=turns_to_use,
        allowed_tools=["Read", "Glob", "Grep"]
    )

    print(f"\n🚀 クエリ実行: max_turns={turns_to_use}")

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    # 最初の200文字のみ表示
                    text = block.text[:200] + "..." if len(block.text) > 200 else block.text
                    print(f"  📝 {text}")

        elif isinstance(message, ResultMessage):
            is_ok, msg = budget.check_budget(
                message.total_cost_usd,
                message.num_turns
            )

            if not is_ok:
                print(f"\n⛔ 予算超過: {msg}")
                return False

    return True


async def run_multiple_queries(
    prompts: List[str],
    budget: BudgetManager,
    turns_per_query: int = 10
):
    """複数のクエリを予算内で実行"""
    print("=" * 50)
    print("複数クエリの予算管理実行")
    print("=" * 50)
    print(f"クエリ数: {len(prompts)}")
    print(f"予算: ${budget.max_cost_usd:.4f}, {budget.max_turns}ターン")
    print("=" * 50)

    completed = 0
    for i, prompt in enumerate(prompts, 1):
        print(f"\n--- クエリ {i}/{len(prompts)} ---")
        print(f"プロンプト: {prompt[:50]}{'...' if len(prompt) > 50 else ''}")

        if not budget.can_continue():
            print("⚠️ 予算が不足しているため、残りのクエリをスキップします")
            break

        success = await budget_aware_query(prompt, budget, turns_per_query)

        if success:
            completed += 1
            budget.print_status()
        else:
            print("⚠️ 予算超過のため処理を中断")
            break

    # 最終レポート
    print("\n" + "=" * 50)
    print("📊 最終レポート")
    print("=" * 50)
    print(f"完了クエリ: {completed}/{len(prompts)}")
    budget.print_status()
    budget.print_history()


async def interactive_mode(budget: BudgetManager):
    """インタラクティブモードで実行"""
    print("=" * 50)
    print("インタラクティブ予算管理モード")
    print("=" * 50)
    print(f"予算: ${budget.max_cost_usd:.4f}, {budget.max_turns}ターン")
    print("'quit' または 'exit' で終了")
    print("=" * 50)

    while budget.can_continue():
        budget.print_status()

        try:
            prompt = input("\nプロンプト> ").strip()
        except EOFError:
            break

        if prompt.lower() in ["quit", "exit", "q"]:
            break

        if not prompt:
            continue

        await budget_aware_query(prompt, budget)

    print("\n" + "=" * 50)
    print("セッション終了")
    budget.print_history()


def parse_args() -> argparse.Namespace:
    """コマンドライン引数をパース"""
    parser = argparse.ArgumentParser(
        description="ターン数とコスト管理の組み合わせ"
    )
    parser.add_argument(
        "-c", "--max-cost",
        type=float,
        default=0.10,
        help="最大コスト (USD) (default: 0.10)"
    )
    parser.add_argument(
        "-t", "--max-turns",
        type=int,
        default=50,
        help="最大ターン数 (default: 50)"
    )
    parser.add_argument(
        "--turns-per-query",
        type=int,
        default=10,
        help="1クエリあたりの最大ターン数 (default: 10)"
    )
    parser.add_argument(
        "--prompts",
        nargs="+",
        help="実行するプロンプト (複数指定可)"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="インタラクティブモードで実行"
    )
    return parser.parse_args()


async def main():
    args = parse_args()

    budget = BudgetManager(
        max_cost_usd=args.max_cost,
        max_turns=args.max_turns
    )

    if args.interactive:
        await interactive_mode(budget)
    elif args.prompts:
        await run_multiple_queries(
            args.prompts,
            budget,
            args.turns_per_query
        )
    else:
        # デフォルトの実行
        default_prompts = [
            "README.md を読んで内容を要約して",
            "src/ ディレクトリの構造を分析して",
            "主要なファイルの役割を説明して"
        ]
        await run_multiple_queries(
            default_prompts,
            budget,
            args.turns_per_query
        )


if __name__ == "__main__":
    asyncio.run(main())
