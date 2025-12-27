"""
権限モードの段階的エスカレーション

Usage:
    python 05_escalation.py --prompt "README.mdを更新して"
    python 05_escalation.py --start acceptEdits --prompt "コードを修正して"
    python 05_escalation.py --auto-escalate --prompt "大規模な変更を実行"

Options:
    --start MODE       : 開始モード（plan, default, acceptEdits）
    --auto-escalate    : 自動でエスカレート（確認なし）
    --max-mode MODE    : 最大エスカレートモード

段階的エスカレーションにより、安全性を維持しながら
必要に応じて権限を拡大できます。
"""
import argparse
import asyncio
from typing import Optional
from claude_agent_sdk import (
    ClaudeAgentOptions,
    query,
    AssistantMessage,
    ResultMessage,
    TextBlock,
    ToolUseBlock
)


class PermissionEscalator:
    """必要に応じて権限をエスカレート"""

    MODES = ["plan", "default", "acceptEdits", "bypassPermissions"]
    MODE_DESCRIPTIONS = {
        "plan": "プランニングのみ（実行なし）",
        "default": "対話的確認",
        "acceptEdits": "ファイル編集を自動承認",
        "bypassPermissions": "全操作を自動承認",
    }

    def __init__(
        self,
        initial_mode: str = "plan",
        max_mode: str = "acceptEdits",
        allowed_tools: list = None
    ):
        if initial_mode not in self.MODES:
            raise ValueError(f"Invalid mode: {initial_mode}")
        if max_mode not in self.MODES:
            raise ValueError(f"Invalid max_mode: {max_mode}")

        self.current_index = self.MODES.index(initial_mode)
        self.max_index = self.MODES.index(max_mode)
        self.allowed_tools = allowed_tools or ["Read", "Write", "Edit", "Glob", "Grep"]
        self.history = []

    @property
    def current_mode(self) -> str:
        return self.MODES[self.current_index]

    @property
    def can_escalate(self) -> bool:
        return self.current_index < self.max_index

    def escalate(self) -> bool:
        """次のモードにエスカレート"""
        if self.can_escalate:
            old_mode = self.current_mode
            self.current_index += 1
            self.history.append({
                "from": old_mode,
                "to": self.current_mode,
            })
            return True
        return False

    def reset(self):
        """初期モードにリセット"""
        self.current_index = 0
        self.history = []

    def get_options(self) -> ClaudeAgentOptions:
        return ClaudeAgentOptions(
            permission_mode=self.current_mode,
            allowed_tools=self.allowed_tools
        )

    def print_status(self):
        """現在の状態を表示"""
        print("\n" + "-" * 40)
        print("権限エスカレーション状態")
        print("-" * 40)

        for i, mode in enumerate(self.MODES):
            if i <= self.max_index:
                if i == self.current_index:
                    print(f"  [●] {mode} <- 現在")
                elif i < self.current_index:
                    print(f"  [✓] {mode} (通過)")
                else:
                    print(f"  [ ] {mode}")
            else:
                print(f"  [x] {mode} (上限外)")

        print("-" * 40)


async def escalating_execution(
    prompt: str,
    escalator: PermissionEscalator,
    auto_escalate: bool = False
):
    """エスカレーション付き実行"""
    print("=" * 60)
    print("段階的エスカレーション実行")
    print("=" * 60)
    print(f"開始モード: {escalator.current_mode}")
    print(f"最大モード: {escalator.MODES[escalator.max_index]}")
    print(f"自動エスカレート: {'ON' if auto_escalate else 'OFF'}")
    print("-" * 60)
    print(f"プロンプト: {prompt}")
    print("=" * 60)

    iteration = 0
    while True:
        iteration += 1
        escalator.print_status()

        print(f"\n=== イテレーション {iteration}: {escalator.current_mode} モード ===")
        print(f"説明: {escalator.MODE_DESCRIPTIONS[escalator.current_mode]}")

        options = escalator.get_options()

        tool_calls = []
        result = None

        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        text = block.text[:200] + "..." if len(block.text) > 200 else block.text
                        print(f"[Text] {text}")
                    elif isinstance(block, ToolUseBlock):
                        tool_calls.append(block.name)
                        print(f"[Tool] {block.name}")

            elif isinstance(message, ResultMessage):
                result = message
                print(f"\n完了: {message.num_turns}ターン, ${message.total_cost_usd:.4f}")

        # plan モードの場合は確認
        if escalator.current_mode == "plan":
            print("\n" + "-" * 40)
            print(f"計画されたツール呼び出し: {len(tool_calls)}")
            for tool in tool_calls:
                print(f"  - {tool}")

            if escalator.can_escalate:
                if auto_escalate:
                    print("\n自動エスカレート: 実行モードに移行します")
                    escalator.escalate()
                else:
                    try:
                        proceed = input("\n実行を続けますか？ (y/n): ")
                    except EOFError:
                        proceed = "n"

                    if proceed.lower() == "y":
                        escalator.escalate()
                        print(f"エスカレート: {escalator.current_mode} モードに移行")
                    else:
                        print("終了します")
                        break
            else:
                print("最大モードに達しています")
                break
        else:
            # 実行モードの場合は終了
            break

    # 最終レポート
    print("\n" + "=" * 60)
    print("エスカレーション履歴")
    print("=" * 60)
    if escalator.history:
        for i, entry in enumerate(escalator.history, 1):
            print(f"  {i}. {entry['from']} -> {entry['to']}")
    else:
        print("  エスカレーションなし")


def parse_args() -> argparse.Namespace:
    """コマンドライン引数をパース"""
    parser = argparse.ArgumentParser(
        description="権限モードの段階的エスカレーション"
    )
    parser.add_argument(
        "-p", "--prompt",
        default="このプロジェクトを分析して改善点を提案してください",
        help="実行するプロンプト"
    )
    parser.add_argument(
        "--start",
        choices=["plan", "default", "acceptEdits"],
        default="plan",
        help="開始モード (default: plan)"
    )
    parser.add_argument(
        "--max-mode",
        choices=["default", "acceptEdits", "bypassPermissions"],
        default="acceptEdits",
        help="最大エスカレートモード (default: acceptEdits)"
    )
    parser.add_argument(
        "--auto-escalate",
        action="store_true",
        help="自動でエスカレート（確認なし）"
    )
    parser.add_argument(
        "-l", "--list",
        action="store_true",
        help="モード一覧を表示"
    )
    return parser.parse_args()


def print_mode_list():
    """モード一覧を表示"""
    print("=" * 60)
    print("権限モードの段階")
    print("=" * 60)
    print("""
安全性: 高 ◄──────────────────────────► 低
        plan > default > acceptEdits > bypassPermissions
""")

    for mode, desc in PermissionEscalator.MODE_DESCRIPTIONS.items():
        print(f"  [{mode}]")
        print(f"    {desc}")
        print()

    print("=" * 60)
    print("エスカレーション例:")
    print("  1. plan で計画を確認")
    print("  2. 承認後、acceptEdits で実行")
    print("=" * 60)


async def main():
    args = parse_args()

    if args.list:
        print_mode_list()
        return

    escalator = PermissionEscalator(
        initial_mode=args.start,
        max_mode=args.max_mode
    )

    await escalating_execution(
        prompt=args.prompt,
        escalator=escalator,
        auto_escalate=args.auto_escalate
    )


if __name__ == "__main__":
    asyncio.run(main())
