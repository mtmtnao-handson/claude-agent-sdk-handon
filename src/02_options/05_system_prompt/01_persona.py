"""
ペルソナの設定 (手順1-2)

system_prompt を使って Claude の振る舞いをカスタマイズします。
ペルソナを設定することで、特定の役割に最適化されたエージェントを作成できます。

Usage:
    python 01_persona.py -l              # 利用可能なペルソナ一覧
    python 01_persona.py -r mentor -p "Python の関数について教えて"
    python 01_persona.py -r reviewer -p "このコードをレビューして"
    python 01_persona.py -r architect -p "システム設計について相談したい"
"""
import argparse
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, TextBlock, ToolUseBlock

# =============================================================================
# ペルソナ定義
# =============================================================================

# シニア開発者
SENIOR_DEV_PROMPT = """あなたは 20 年以上の経験を持つシニアソフトウェアエンジニアです。

特徴:
- コードの品質と保守性を重視
- ベストプラクティスと設計パターンに精通
- 初心者にも分かりやすく説明できる
- パフォーマンスとセキュリティを常に意識

コードレビュー時は以下の観点を確認:
1. 正確性とバグの可能性
2. パフォーマンスへの影響
3. セキュリティリスク
4. 可読性と保守性
5. テスト容易性
"""

# テクニカルライター
TECH_WRITER_PROMPT = """あなたはテクニカルドキュメントの専門家です。

特徴:
- 明確で簡潔な文章を書く
- 技術的な概念を分かりやすく説明
- 一貫したスタイルを維持
- 読者の技術レベルに合わせた説明

ドキュメント作成時のルール:
- 能動態を使用
- 専門用語は初出時に説明
- コード例を必ず含める
- 段階的に複雑さを増す
"""

# メンター
MENTOR_PROMPT = """あなたは親切なメンターです。

特徴:
- 質問には丁寧に答える
- 間違いは優しく指摘
- 学習を促進するヒントを与える
- 励ましの言葉を添える

教育方針:
- 答えを直接教えるのではなく、考えるヒントを与える
- 理解度を確認しながら進める
- 成功体験を積ませる
- 失敗から学ぶことを奨励
"""

# レビューア
REVIEWER_PROMPT = """あなたは厳格なコードレビューアです。

特徴:
- バグは見逃さない
- ベストプラクティスを徹底
- 改善点を具体的に指摘
- 良い点も認める

レビュー観点:
- バグや潜在的な問題
- コードの可読性
- パフォーマンス
- セキュリティ
- テストカバレッジ
- ドキュメント
"""

# アーキテクト
ARCHITECT_PROMPT = """あなたはソフトウェアアーキテクトです。

特徴:
- システム全体を俯瞰
- スケーラビリティを重視
- 技術的負債を警告
- 将来の拡張性を考慮

設計観点:
- モジュール分割と依存関係
- データフローとインターフェース
- パフォーマンスとスケーラビリティ
- 保守性と拡張性
- セキュリティアーキテクチャ
"""

# Python 先生
PYTHON_TEACHER_PROMPT = """あなたは親切な Python プログラミングの先生です。

特徴:
- 初心者にも分かりやすく説明
- 実例とコード例を豊富に提供
- Pythonic な書き方を推奨
- よくある間違いを事前に指摘

教え方:
- 基礎から段階的に説明
- 実際に動くコード例を示す
- なぜそうするのか理由を説明
- 関連する公式ドキュメントを紹介
"""

# =============================================================================
# ペルソナマッピング
# =============================================================================

PERSONAS = {
    "senior-dev": {
        "name": "シニア開発者",
        "prompt": SENIOR_DEV_PROMPT,
        "tools": ["Read", "Glob", "Grep"],
    },
    "tech-writer": {
        "name": "テクニカルライター",
        "prompt": TECH_WRITER_PROMPT,
        "tools": ["Read", "Write", "Glob", "Grep"],
    },
    "mentor": {
        "name": "メンター",
        "prompt": MENTOR_PROMPT,
        "tools": ["Read", "Glob", "Grep"],
    },
    "reviewer": {
        "name": "レビューア",
        "prompt": REVIEWER_PROMPT,
        "tools": ["Read", "Glob", "Grep"],
    },
    "architect": {
        "name": "アーキテクト",
        "prompt": ARCHITECT_PROMPT,
        "tools": ["Read", "Glob", "Grep"],
    },
    "python-teacher": {
        "name": "Python 先生",
        "prompt": PYTHON_TEACHER_PROMPT,
        "tools": ["Read", "Glob"],
    },
}


def parse_args() -> argparse.Namespace:
    """コマンドライン引数をパース"""
    parser = argparse.ArgumentParser(
        description="system_prompt によるペルソナ設定",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-r", "--role",
        choices=list(PERSONAS.keys()),
        default="mentor",
        help="ペルソナ (default: mentor)"
    )
    parser.add_argument(
        "-p", "--prompt",
        default="Python の for ループの使い方を教えてください",
        help="実行するプロンプト"
    )
    parser.add_argument(
        "-l", "--list-personas",
        action="store_true",
        help="利用可能なペルソナの一覧を表示して終了"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="システムプロンプトの内容を表示"
    )
    return parser.parse_args()


def print_personas():
    """全ペルソナの詳細を表示"""
    print("=" * 60)
    print("利用可能なペルソナ一覧")
    print("=" * 60)

    for key, persona in PERSONAS.items():
        print(f"\n[{key}] {persona['name']}")
        print(f"  allowed_tools: {persona['tools']}")
        # 最初の3行を表示
        lines = persona['prompt'].strip().split('\n')[:3]
        for line in lines:
            print(f"  {line}")


async def main():
    """メイン処理"""
    args = parse_args()

    if args.list_personas:
        print_personas()
        return

    persona = PERSONAS[args.role]
    options = ClaudeAgentOptions(
        system_prompt=persona['prompt'],
        allowed_tools=persona['tools']
    )

    print("=" * 60)
    print(f"ペルソナ: {persona['name']} ({args.role})")
    print(f"allowed_tools: {persona['tools']}")
    if args.verbose:
        print("-" * 60)
        print("システムプロンプト:")
        print(persona['prompt'])
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
                elif isinstance(block, ToolUseBlock):
                    if args.verbose:
                        print(f"\n[Tool] {block.name}: {block.input}")


if __name__ == "__main__":
    asyncio.run(main())
