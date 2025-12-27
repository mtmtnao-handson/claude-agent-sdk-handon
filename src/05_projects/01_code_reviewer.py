"""
実践プロジェクト: コードレビューア
"""
import asyncio
import json
from datetime import datetime
from pathlib import Path
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AgentDefinition,
    HookMatcher,
    tool,
    create_sdk_mcp_server
)


# カスタムツール: レポート保存
@tool("save_report", "レビューレポートを保存します", {
    "filename": str,
    "content": str
})
async def save_report(args: dict) -> dict:
    filename = args["filename"]
    content = args["content"]

    output_dir = Path("review_reports")
    output_dir.mkdir(exist_ok=True)

    filepath = output_dir / filename
    filepath.write_text(content, encoding="utf-8")

    return {
        "content": [{
            "type": "text",
            "text": f"レポートを保存しました: {filepath}"
        }]
    }


# MCP サーバー
report_server = create_sdk_mcp_server(
    name="reporter",
    version="1.0.0",
    tools=[save_report]
)

# エージェント定義
security_reviewer = AgentDefinition(
    name="security-reviewer",
    description="セキュリティの観点でコードをレビューします",
    system_prompt="""
    あなたはセキュリティ専門家です。以下の観点でコードをレビューしてください:
    - インジェクション攻撃の脆弱性
    - 認証・認可の問題
    - 機密情報の露出
    - 入力バリデーション
    JSON形式で結果を出力してください。
    """,
    allowed_tools=["Read", "Glob", "Grep"]
)

style_reviewer = AgentDefinition(
    name="style-reviewer",
    description="コードスタイルをレビューします",
    system_prompt="""
    あなたはコードスタイルの専門家です。以下の観点でレビューしてください:
    - 命名規則
    - コードの構造
    - コメントの適切さ
    - PEP 8 準拠
    JSON形式で結果を出力してください。
    """,
    allowed_tools=["Read", "Glob", "Grep"]
)


# 監査フック
class ReviewAuditLogger:
    def __init__(self):
        self.logs = []

    async def log_tool_use(self, input_data, tool_use_id, context):
        self.logs.append({
            "timestamp": datetime.now().isoformat(),
            "tool": input_data["tool_name"],
            "input": str(input_data["tool_input"])[:100]
        })
        return {}

    def get_summary(self):
        return {
            "total_tool_calls": len(self.logs),
            "tools_used": list(set(log["tool"] for log in self.logs))
        }


async def review_code(target_path: str):
    """コードレビューを実行"""
    logger = ReviewAuditLogger()

    options = ClaudeAgentOptions(
        allowed_tools=[
            "Read", "Glob", "Grep", "Task",
            "mcp__reporter__save_report"
        ],
        mcp_servers={"reporter": report_server},
        agents=[security_reviewer, style_reviewer],
        permission_mode="acceptEdits",
        system_prompt="""
        あなたはコードレビューの統括者です。
        複数の専門エージェントを使ってコードをレビューし、
        最終的なレポートをまとめてください。
        """,
        hooks={
            "PreToolUse": [HookMatcher(hooks=[logger.log_tool_use])]
        }
    )

    print(f"=== コードレビュー開始: {target_path} ===\n")

    async for message in query(
        prompt=f"""
        {target_path} のコードをレビューしてください。

        1. security-reviewer エージェントでセキュリティレビュー
        2. style-reviewer エージェントでスタイルレビュー
        3. 結果を統合してレポートを作成
        4. save_report ツールで保存

        レポートファイル名: review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md
        """,
        options=options
    ):
        print(message)

    print(f"\n=== 監査サマリー ===")
    print(json.dumps(logger.get_summary(), indent=2, ensure_ascii=False))


async def main():
    # src/basics/ をレビュー
    await review_code("src/basics/")


if __name__ == "__main__":
    asyncio.run(main())
