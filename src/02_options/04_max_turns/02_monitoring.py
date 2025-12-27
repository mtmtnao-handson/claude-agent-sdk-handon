"""
ターン数のモニタリング

Usage:
    python 02_monitoring.py --max-turns 10 --prompt "プロジェクトを分析して"
    python 02_monitoring.py -t 5 -p "README.mdを読んで"
    python 02_monitoring.py --verbose -t 15 -p "src/を調査して"

このスクリプトは、ターン数をリアルタイムでモニタリングし、
進捗状況やツール使用状況を詳細に表示します。
"""
import argparse
import asyncio
from datetime import datetime
from claude_agent_sdk import (
    ClaudeAgentOptions,
    query,
    AssistantMessage,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    ToolResultBlock
)


class TurnMonitor:
    """ターン数をモニタリングするクラス"""

    def __init__(self, max_turns: int):
        self.max_turns = max_turns
        self.current_turn = 0
        self.tool_usage = {}  # ツール名 -> 使用回数
        self.start_time = None
        self.turn_times = []  # 各ターンの所要時間

    def start(self):
        """モニタリングを開始"""
        self.start_time = datetime.now()
        print(f"[モニター] 開始時刻: {self.start_time.strftime('%H:%M:%S')}")
        print(f"[モニター] 最大ターン数: {self.max_turns}")
        print("-" * 50)

    def on_turn_start(self):
        """ターン開始時のコールバック"""
        self.current_turn += 1
        turn_start = datetime.now()
        self.turn_times.append({"start": turn_start, "end": None})

        progress = (self.current_turn / self.max_turns) * 100
        bar_length = 20
        filled = int(bar_length * self.current_turn / self.max_turns)
        bar = "█" * filled + "░" * (bar_length - filled)

        print(f"\n[ターン {self.current_turn}/{self.max_turns}] [{bar}] {progress:.0f}%")

    def on_tool_use(self, tool_name: str, tool_input: dict):
        """ツール使用時のコールバック"""
        self.tool_usage[tool_name] = self.tool_usage.get(tool_name, 0) + 1
        print(f"  🔧 ツール: {tool_name}")
        # 入力を短く表示
        input_str = str(tool_input)
        if len(input_str) > 80:
            input_str = input_str[:80] + "..."
        print(f"     入力: {input_str}")

    def on_turn_end(self):
        """ターン終了時のコールバック"""
        if self.turn_times and self.turn_times[-1]["end"] is None:
            self.turn_times[-1]["end"] = datetime.now()

    def get_summary(self) -> dict:
        """モニタリング結果のサマリーを取得"""
        end_time = datetime.now()
        total_time = (end_time - self.start_time).total_seconds() if self.start_time else 0

        return {
            "total_turns": self.current_turn,
            "max_turns": self.max_turns,
            "turns_remaining": self.max_turns - self.current_turn,
            "total_time_seconds": total_time,
            "avg_time_per_turn": total_time / self.current_turn if self.current_turn > 0 else 0,
            "tool_usage": self.tool_usage,
            "total_tool_calls": sum(self.tool_usage.values()),
        }

    def print_summary(self, result_message: ResultMessage = None):
        """サマリーを表示"""
        summary = self.get_summary()

        print("\n" + "=" * 50)
        print("📊 モニタリングサマリー")
        print("=" * 50)

        print(f"\n【ターン数】")
        print(f"  実際のターン数: {summary['total_turns']}")
        print(f"  最大ターン数:   {summary['max_turns']}")
        print(f"  残りターン数:   {summary['turns_remaining']}")

        print(f"\n【処理時間】")
        print(f"  合計時間:       {summary['total_time_seconds']:.2f}秒")
        print(f"  平均(ターン):   {summary['avg_time_per_turn']:.2f}秒/ターン")

        print(f"\n【ツール使用状況】")
        print(f"  合計ツール呼び出し: {summary['total_tool_calls']}回")
        if summary['tool_usage']:
            for tool, count in sorted(summary['tool_usage'].items(), key=lambda x: -x[1]):
                print(f"    - {tool}: {count}回")
        else:
            print("    (ツール使用なし)")

        if result_message:
            print(f"\n【コスト】")
            print(f"  合計コスト:     ${result_message.total_cost_usd:.4f}")
            if summary['total_turns'] > 0:
                cost_per_turn = result_message.total_cost_usd / summary['total_turns']
                print(f"  平均(ターン):   ${cost_per_turn:.4f}/ターン")


async def monitored_query(prompt: str, max_turns: int, verbose: bool = False):
    """モニタリング付きでクエリを実行"""
    options = ClaudeAgentOptions(
        max_turns=max_turns,
        allowed_tools=["Read", "Write", "Edit", "Glob", "Grep", "Bash"]
    )

    monitor = TurnMonitor(max_turns)
    monitor.start()

    result_message = None

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            monitor.on_turn_start()

            for block in message.content:
                if isinstance(block, TextBlock):
                    if verbose:
                        # 詳細モードでは全文表示
                        print(f"  📝 {block.text}")
                    else:
                        # 通常モードでは最初の100文字のみ
                        text = block.text[:100] + "..." if len(block.text) > 100 else block.text
                        print(f"  📝 {text}")

                elif isinstance(block, ToolUseBlock):
                    monitor.on_tool_use(block.name, block.input)

            monitor.on_turn_end()

        elif isinstance(message, ResultMessage):
            result_message = message

    monitor.print_summary(result_message)

    return monitor.get_summary()


def parse_args() -> argparse.Namespace:
    """コマンドライン引数をパース"""
    parser = argparse.ArgumentParser(
        description="ターン数のモニタリング"
    )
    parser.add_argument(
        "-t", "--max-turns",
        type=int,
        default=10,
        help="最大ターン数 (default: 10)"
    )
    parser.add_argument(
        "-p", "--prompt",
        default="このプロジェクトの構造を分析してください",
        help="実行するプロンプト"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="詳細な出力を表示"
    )
    return parser.parse_args()


async def main():
    args = parse_args()

    print("=" * 50)
    print("ターン数モニタリング")
    print("=" * 50)
    print(f"プロンプト: {args.prompt}")
    print(f"最大ターン数: {args.max_turns}")
    print(f"詳細モード: {'ON' if args.verbose else 'OFF'}")
    print("=" * 50)

    await monitored_query(
        prompt=args.prompt,
        max_turns=args.max_turns,
        verbose=args.verbose
    )


if __name__ == "__main__":
    asyncio.run(main())
