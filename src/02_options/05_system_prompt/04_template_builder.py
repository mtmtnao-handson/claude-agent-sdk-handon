"""
複合的なシステムプロンプト (手順5-6)

役割、プロジェクト情報、制約条件、出力形式を組み合わせて
カスタマイズされたシステムプロンプトを構築します。

Usage:
    python 04_template_builder.py --role "Python 開発者" --project-name MyApp
    python 04_template_builder.py --role "アーキテクト" --framework FastAPI
    python 04_template_builder.py --show-template  # テンプレート表示
"""
import argparse
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, TextBlock

# =============================================================================
# プロンプトビルダー
# =============================================================================

def build_system_prompt(
    role: str,
    project_info: dict = None,
    constraints: list[str] = None,
    output_format: str = None,
    coding_rules: dict = None
) -> str:
    """システムプロンプトを組み立てる"""

    parts = []

    # 役割
    parts.append(f"# 役割\n{role}")

    # プロジェクト情報
    if project_info:
        parts.append("# プロジェクト情報")
        for key, value in project_info.items():
            parts.append(f"- {key}: {value}")

    # コーディング規約
    if coding_rules:
        parts.append("# コーディング規約")
        for category, rules in coding_rules.items():
            parts.append(f"\n## {category}")
            if isinstance(rules, list):
                for rule in rules:
                    parts.append(f"- {rule}")
            else:
                parts.append(f"- {rules}")

    # 制約条件
    if constraints:
        parts.append("# 制約条件")
        for c in constraints:
            parts.append(f"- {c}")

    # 出力形式
    if output_format:
        parts.append(f"# 出力形式\n{output_format}")

    return "\n\n".join(parts)


# =============================================================================
# プリセット
# =============================================================================

ROLE_PRESETS = {
    "python-dev": "あなたはシニア Python 開発者です。Pythonic なコードを書き、ベストプラクティスに従います。",
    "fullstack-dev": "あなたはフルスタック開発者です。フロントエンドとバックエンドの両方に精通しています。",
    "devops": "あなたは DevOps エンジニアです。インフラ、デプロイメント、モニタリングに精通しています。",
    "architect": "あなたはソフトウェアアーキテクトです。システム全体の設計とスケーラビリティを重視します。",
    "qa": "あなたは QA エンジニアです。テスト戦略、品質保証、バグ検出に精通しています。",
}

FRAMEWORK_INFO = {
    "fastapi": {"name": "FastAPI", "description": "Python の高速な Web フレームワーク"},
    "django": {"name": "Django", "description": "Python のフルスタック Web フレームワーク"},
    "flask": {"name": "Flask", "description": "Python の軽量 Web フレームワーク"},
    "react": {"name": "React", "description": "UI 構築のための JavaScript ライブラリ"},
    "vue": {"name": "Vue.js", "description": "プログレッシブ JavaScript フレームワーク"},
}

DEFAULT_CONSTRAINTS = [
    "本番環境のファイルを直接編集しない",
    "機密情報を出力しない",
    "変更前に影響範囲を確認",
    "テストを必ず書く",
]

DEFAULT_CODING_RULES = {
    "命名規則": [
        "クラス: PascalCase",
        "関数/変数: snake_case",
        "定数: UPPER_SNAKE_CASE",
    ],
    "フォーマット": [
        "Black でコード整形",
        "isort でインポート整理",
        "行の最大長: 100文字",
    ],
    "品質": [
        "型ヒントを使用 (mypy でチェック)",
        "docstring を必ず書く",
        "複雑な関数は分割",
    ],
}


def parse_args() -> argparse.Namespace:
    """コマンドライン引数をパース"""
    parser = argparse.ArgumentParser(
        description="テンプレートベースのシステムプロンプト構築",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # 役割
    parser.add_argument(
        "--role",
        choices=list(ROLE_PRESETS.keys()),
        default="python-dev",
        help="役割プリセット"
    )

    # プロジェクト情報
    parser.add_argument(
        "--project-name",
        default="MyProject",
        help="プロジェクト名"
    )
    parser.add_argument(
        "--framework",
        choices=list(FRAMEWORK_INFO.keys()),
        help="使用フレームワーク"
    )
    parser.add_argument(
        "--language",
        default="Python 3.11",
        help="プログラミング言語"
    )

    # オプション
    parser.add_argument(
        "--add-constraint",
        action="append",
        help="追加の制約条件"
    )
    parser.add_argument(
        "--output-format",
        help="出力形式の指定"
    )

    parser.add_argument(
        "-p", "--prompt",
        default="プロジェクトの構造を確認してください",
        help="実行するプロンプト"
    )
    parser.add_argument(
        "--show-template",
        action="store_true",
        help="生成されたテンプレートを表示して終了"
    )
    parser.add_argument(
        "--list-presets",
        action="store_true",
        help="利用可能なプリセットを表示"
    )

    return parser.parse_args()


def print_presets():
    """プリセット一覧を表示"""
    print("=" * 60)
    print("役割プリセット")
    print("=" * 60)
    for key, desc in ROLE_PRESETS.items():
        print(f"\n[{key}]")
        print(f"  {desc}")

    print("\n" + "=" * 60)
    print("フレームワーク")
    print("=" * 60)
    for key, info in FRAMEWORK_INFO.items():
        print(f"\n[{key}] {info['name']}")
        print(f"  {info['description']}")


async def main():
    """メイン処理"""
    args = parse_args()

    if args.list_presets:
        print_presets()
        return

    # システムプロンプトを構築
    role = ROLE_PRESETS[args.role]

    project_info = {
        "プロジェクト名": args.project_name,
        "言語": args.language,
    }

    if args.framework:
        fw = FRAMEWORK_INFO[args.framework]
        project_info["フレームワーク"] = f"{fw['name']} - {fw['description']}"

    constraints = DEFAULT_CONSTRAINTS.copy()
    if args.add_constraint:
        constraints.extend(args.add_constraint)

    system_prompt = build_system_prompt(
        role=role,
        project_info=project_info,
        constraints=constraints,
        output_format=args.output_format,
        coding_rules=DEFAULT_CODING_RULES
    )

    if args.show_template:
        print("=" * 60)
        print("生成されたシステムプロンプト")
        print("=" * 60)
        print(system_prompt)
        return

    options = ClaudeAgentOptions(
        system_prompt=system_prompt,
        allowed_tools=["Read", "Glob", "Grep", "Write", "Edit"]
    )

    print("=" * 60)
    print(f"役割: {args.role}")
    print(f"プロジェクト: {args.project_name}")
    if args.framework:
        print(f"フレームワーク: {FRAMEWORK_INFO[args.framework]['name']}")
    print("-" * 60)
    print(f"プロンプト: {args.prompt}")
    print("=" * 60)
    print()

    async for message in query(
        prompt=args.prompt,
        options=options
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)


if __name__ == "__main__":
    asyncio.run(main())
