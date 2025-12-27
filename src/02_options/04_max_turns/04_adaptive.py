"""
動的なターン数調整と継続実行パターン

Usage:
    python 04_adaptive.py --mode estimate --prompt "全ファイルを分析してリファクタリングして"
    python 04_adaptive.py -m continue --prompt "大規模なコード分析を実行"
    python 04_adaptive.py -m progressive --prompt "プロジェクトを調査して"

Available modes:
    estimate    : プロンプトからターン数を推定して実行
    continue    : 必要に応じてターンを継続
    progressive : 段階的にターン数を増やして実行

このスクリプトは、タスクの複雑さに応じてターン数を動的に調整します。
"""
import argparse
import asyncio
import re
from typing import Optional
from claude_agent_sdk import ClaudeAgentOptions, query, ResultMessage, AssistantMessage, TextBlock


class TurnEstimator:
    """プロンプトからターン数を推定するクラス"""

    # キーワードと推定ターン数のマッピング
    KEYWORD_TURNS = {
        # 分析系
        "分析": 5,
        "調査": 5,
        "確認": 3,
        "レビュー": 8,
        # 読み取り系
        "読んで": 3,
        "確認して": 3,
        "表示": 2,
        # 作成系
        "作成": 10,
        "生成": 10,
        "書いて": 8,
        # 編集系
        "修正": 8,
        "変更": 8,
        "編集": 8,
        "更新": 8,
        # 大規模作業
        "リファクタリング": 20,
        "リファクタ": 20,
        "全ファイル": 15,
        "すべて": 12,
        "全て": 12,
        # テスト
        "テスト": 10,
        "検証": 8,
        # ドキュメント
        "ドキュメント": 12,
        "説明": 5,
        "要約": 4,
    }

    # 修飾語による倍率
    MODIFIER_MULTIPLIERS = {
        "詳細": 1.5,
        "詳しく": 1.5,
        "完全": 2.0,
        "徹底的": 2.0,
        "簡単": 0.5,
        "簡潔": 0.5,
        "ざっくり": 0.5,
    }

    def estimate(self, prompt: str) -> int:
        """プロンプトからターン数を推定"""
        base_turns = 5

        # キーワードマッチング
        for keyword, turns in self.KEYWORD_TURNS.items():
            if keyword in prompt:
                base_turns = max(base_turns, turns)

        # 修飾語による調整
        multiplier = 1.0
        for modifier, mult in self.MODIFIER_MULTIPLIERS.items():
            if modifier in prompt:
                multiplier = mult
                break

        estimated = int(base_turns * multiplier)

        # 上限と下限
        return max(3, min(100, estimated))

    def explain(self, prompt: str) -> dict:
        """推定の根拠を説明"""
        matched_keywords = []
        for keyword in self.KEYWORD_TURNS:
            if keyword in prompt:
                matched_keywords.append((keyword, self.KEYWORD_TURNS[keyword]))

        matched_modifiers = []
        for modifier in self.MODIFIER_MULTIPLIERS:
            if modifier in prompt:
                matched_modifiers.append((modifier, self.MODIFIER_MULTIPLIERS[modifier]))

        return {
            "estimated_turns": self.estimate(prompt),
            "matched_keywords": matched_keywords,
            "matched_modifiers": matched_modifiers,
        }


async def adaptive_query(prompt: str, explain: bool = False):
    """推定ターン数で実行"""
    estimator = TurnEstimator()
    estimated = estimator.estimate(prompt)

    if explain:
        explanation = estimator.explain(prompt)
        print("\n📊 ターン数推定")
        print("-" * 40)
        print(f"推定ターン数: {explanation['estimated_turns']}")

        if explanation['matched_keywords']:
            print("マッチしたキーワード:")
            for kw, turns in explanation['matched_keywords']:
                print(f"  - '{kw}' -> {turns}ターン")

        if explanation['matched_modifiers']:
            print("マッチした修飾語:")
            for mod, mult in explanation['matched_modifiers']:
                print(f"  - '{mod}' -> x{mult}")
        print("-" * 40)

    print(f"\n🚀 実行: max_turns={estimated}")

    options = ClaudeAgentOptions(
        max_turns=estimated,
        allowed_tools=["Read", "Write", "Edit", "Glob", "Grep"]
    )

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"📝 {block.text[:200]}...")

        elif isinstance(message, ResultMessage):
            print(f"\n✅ 完了: {message.num_turns}/{estimated}ターン使用")
            print(f"💰 コスト: ${message.total_cost_usd:.4f}")


async def continue_if_needed(
    prompt: str,
    initial_turns: int = 10,
    max_total_turns: int = 50
):
    """必要に応じてターンを継続"""
    total_turns = 0
    iteration = 0
    total_cost = 0.0

    print("=" * 50)
    print("継続実行モード")
    print("=" * 50)
    print(f"初期ターン数: {initial_turns}")
    print(f"最大合計ターン数: {max_total_turns}")
    print("=" * 50)

    while total_turns < max_total_turns:
        iteration += 1
        remaining = max_total_turns - total_turns

        turns_for_this_iteration = min(initial_turns, remaining)

        options = ClaudeAgentOptions(
            max_turns=turns_for_this_iteration,
            allowed_tools=["Read", "Write", "Edit", "Glob", "Grep"]
        )

        print(f"\n=== イテレーション {iteration} ===")
        print(f"このイテレーションのターン数: {turns_for_this_iteration}")
        print(f"累計ターン: {total_turns}/{max_total_turns}")

        current_prompt = prompt if iteration == 1 else "続きを実行してください。前回の作業を継続し、完了させてください。"

        iteration_turns = 0
        task_completed = False

        async for message in query(prompt=current_prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        text = block.text[:150] + "..." if len(block.text) > 150 else block.text
                        print(f"📝 {text}")

                        # タスク完了の判定（簡易的な実装）
                        completion_indicators = [
                            "完了しました",
                            "終了しました",
                            "以上です",
                            "完了です",
                        ]
                        if any(ind in block.text for ind in completion_indicators):
                            task_completed = True

            elif isinstance(message, ResultMessage):
                iteration_turns = message.num_turns
                total_turns += iteration_turns
                total_cost += message.total_cost_usd

                print(f"\n--- イテレーション {iteration} 結果 ---")
                print(f"このイテレーション: {iteration_turns}ターン")
                print(f"累計: {total_turns}/{max_total_turns}ターン")
                print(f"累計コスト: ${total_cost:.4f}")

                # タスクが完了したと判断
                if iteration_turns < turns_for_this_iteration or task_completed:
                    print("\n✅ タスク完了")
                    return {
                        "total_turns": total_turns,
                        "iterations": iteration,
                        "total_cost": total_cost,
                        "completed": True,
                    }

    print("\n⚠️ 最大ターン数に達しました")
    return {
        "total_turns": total_turns,
        "iterations": iteration,
        "total_cost": total_cost,
        "completed": False,
    }


async def progressive_execution(
    prompt: str,
    initial_turns: int = 5,
    max_turns: int = 50,
    growth_factor: float = 2.0
):
    """段階的にターン数を増やして実行"""
    print("=" * 50)
    print("段階的実行モード")
    print("=" * 50)
    print(f"初期ターン数: {initial_turns}")
    print(f"最大ターン数: {max_turns}")
    print(f"増加係数: {growth_factor}")
    print("=" * 50)

    current_turns = initial_turns
    iteration = 0
    total_cost = 0.0

    while current_turns <= max_turns:
        iteration += 1

        options = ClaudeAgentOptions(
            max_turns=current_turns,
            allowed_tools=["Read", "Write", "Edit", "Glob", "Grep"]
        )

        print(f"\n=== 試行 {iteration}: max_turns={current_turns} ===")

        current_prompt = prompt if iteration == 1 else f"前回は{current_turns // int(growth_factor)}ターンでは足りませんでした。続きを実行してください。"

        async for message in query(prompt=current_prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"📝 {block.text[:100]}...")

            elif isinstance(message, ResultMessage):
                total_cost += message.total_cost_usd
                used_turns = message.num_turns

                print(f"\n結果: {used_turns}/{current_turns}ターン使用")
                print(f"累計コスト: ${total_cost:.4f}")

                # ターンを使い切らなかった = タスク完了
                if used_turns < current_turns:
                    print("\n✅ タスク完了")
                    return {
                        "turns_used": used_turns,
                        "iterations": iteration,
                        "total_cost": total_cost,
                    }

        # 次の試行のためにターン数を増加
        current_turns = int(current_turns * growth_factor)
        print(f"\n⏫ ターン数を増加: {current_turns}")

    print(f"\n⚠️ 最大ターン数 ({max_turns}) に達しました")
    return {
        "turns_used": max_turns,
        "iterations": iteration,
        "total_cost": total_cost,
    }


def parse_args() -> argparse.Namespace:
    """コマンドライン引数をパース"""
    parser = argparse.ArgumentParser(
        description="動的なターン数調整"
    )
    parser.add_argument(
        "-m", "--mode",
        choices=["estimate", "continue", "progressive"],
        default="estimate",
        help="実行モード (default: estimate)"
    )
    parser.add_argument(
        "-p", "--prompt",
        default="このプロジェクトを分析してください",
        help="実行するプロンプト"
    )
    parser.add_argument(
        "--initial-turns",
        type=int,
        default=10,
        help="初期ターン数 (default: 10)"
    )
    parser.add_argument(
        "--max-turns",
        type=int,
        default=50,
        help="最大ターン数 (default: 50)"
    )
    parser.add_argument(
        "--explain",
        action="store_true",
        help="ターン数推定の根拠を表示 (estimate モード用)"
    )
    return parser.parse_args()


async def main():
    args = parse_args()

    print("=" * 50)
    print(f"モード: {args.mode}")
    print(f"プロンプト: {args.prompt}")
    print("=" * 50)

    if args.mode == "estimate":
        await adaptive_query(args.prompt, explain=args.explain)

    elif args.mode == "continue":
        result = await continue_if_needed(
            args.prompt,
            initial_turns=args.initial_turns,
            max_total_turns=args.max_turns
        )
        print("\n" + "=" * 50)
        print("📊 最終結果")
        print(f"  合計ターン: {result['total_turns']}")
        print(f"  イテレーション: {result['iterations']}")
        print(f"  合計コスト: ${result['total_cost']:.4f}")
        print(f"  完了: {'はい' if result['completed'] else 'いいえ'}")

    elif args.mode == "progressive":
        result = await progressive_execution(
            args.prompt,
            initial_turns=args.initial_turns,
            max_turns=args.max_turns
        )
        print("\n" + "=" * 50)
        print("📊 最終結果")
        print(f"  使用ターン: {result['turns_used']}")
        print(f"  試行回数: {result['iterations']}")
        print(f"  合計コスト: ${result['total_cost']:.4f}")


if __name__ == "__main__":
    asyncio.run(main())
