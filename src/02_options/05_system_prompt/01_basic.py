"""
system_prompt のカスタマイズ例
"""
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

# コードレビュアーとしてのペルソナ
CODE_REVIEWER_PROMPT = """
あなたは経験豊富なシニアエンジニアです。
コードレビューを行う際は以下の観点で評価してください:

1. コードの可読性
2. パフォーマンス
3. セキュリティ
4. ベストプラクティスへの準拠

フィードバックは建設的で具体的に行ってください。
"""

# JSON出力フォーマット
JSON_OUTPUT_PROMPT = """
回答は必ず以下のJSON形式で出力してください:

{
  "summary": "概要",
  "details": ["詳細1", "詳細2"],
  "recommendations": ["推奨事項1", "推奨事項2"]
}
"""


async def main():
    """カスタムシステムプロンプトでの実行"""
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Glob"],
        system_prompt=CODE_REVIEWER_PROMPT
    )

    async for message in query(
        prompt="src/basics/01_query_basic.py をレビューしてください",
        options=options
    ):
        print(message)


if __name__ == "__main__":
    asyncio.run(main())
