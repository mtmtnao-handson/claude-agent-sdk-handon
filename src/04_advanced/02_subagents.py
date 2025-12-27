"""
サブエージェントの定義と使用
"""
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AgentDefinition

# コードレビューエージェント
code_reviewer = AgentDefinition(
    name="code-reviewer",
    description="コードの品質をレビューします",
    system_prompt="""
    あなたはコードレビューの専門家です。
    以下の観点でコードを評価してください:
    - 可読性
    - パフォーマンス
    - セキュリティ
    - ベストプラクティス
    """,
    allowed_tools=["Read", "Glob", "Grep"]
)

# ドキュメント生成エージェント
doc_generator = AgentDefinition(
    name="doc-generator",
    description="コードからドキュメントを生成します",
    system_prompt="""
    あなたはドキュメント作成の専門家です。
    コードを分析し、以下を生成してください:
    - 関数/クラスの説明
    - 引数と戻り値の説明
    - 使用例
    """,
    allowed_tools=["Read", "Glob"]
)


async def main():
    """サブエージェントを使った分析"""
    options = ClaudeAgentOptions(
        allowed_tools=["Task", "Read", "Glob"],
        agents=[code_reviewer, doc_generator]
    )

    async for message in query(
        prompt="""
        src/basics/ ディレクトリのコードについて:
        1. code-reviewer エージェントでレビュー
        2. doc-generator エージェントでドキュメント生成
        両方の結果をまとめてください。
        """,
        options=options
    ):
        print(message)


if __name__ == "__main__":
    asyncio.run(main())
