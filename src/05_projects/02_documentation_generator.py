"""
実践プロジェクト: ドキュメント生成ツール
"""
import asyncio
from datetime import datetime
from pathlib import Path
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AgentDefinition,
    tool,
    create_sdk_mcp_server
)


# カスタムツール
@tool("save_markdown", "Markdownファイルを保存します", {
    "filename": str,
    "content": str
})
async def save_markdown(args: dict) -> dict:
    output_dir = Path("generated_docs")
    output_dir.mkdir(exist_ok=True)

    filepath = output_dir / args["filename"]
    filepath.write_text(args["content"], encoding="utf-8")

    return {
        "content": [{
            "type": "text",
            "text": f"ドキュメントを保存しました: {filepath}"
        }]
    }


@tool("list_python_files", "Pythonファイルの一覧を取得します", {
    "directory": str
})
async def list_python_files(args: dict) -> dict:
    directory = Path(args["directory"])
    if not directory.exists():
        return {
            "content": [{
                "type": "text",
                "text": f"ディレクトリが存在しません: {directory}"
            }]
        }

    files = list(directory.rglob("*.py"))
    file_list = "\n".join(str(f) for f in files)

    return {
        "content": [{
            "type": "text",
            "text": f"Pythonファイル一覧:\n{file_list}"
        }]
    }


# MCP サーバー
doc_server = create_sdk_mcp_server(
    name="doc-tools",
    version="1.0.0",
    tools=[save_markdown, list_python_files]
)

# エージェント定義
function_analyzer = AgentDefinition(
    name="function-analyzer",
    description="関数を分析してドキュメントを生成します",
    system_prompt="""
    あなたはPythonコードアナライザーです。
    関数を分析し、以下の情報を抽出してください:
    - 関数名
    - 引数と型
    - 戻り値
    - 機能の説明
    - 使用例
    Markdown形式で出力してください。
    """,
    allowed_tools=["Read", "Glob", "Grep"]
)

class_analyzer = AgentDefinition(
    name="class-analyzer",
    description="クラスを分析してドキュメントを生成します",
    system_prompt="""
    あなたはPythonクラスアナライザーです。
    クラスを分析し、以下の情報を抽出してください:
    - クラス名
    - 継承関係
    - 属性
    - メソッド
    - 使用例
    Markdown形式で出力してください。
    """,
    allowed_tools=["Read", "Glob", "Grep"]
)


async def generate_documentation(target_path: str, output_name: str):
    """ドキュメントを生成"""
    options = ClaudeAgentOptions(
        allowed_tools=[
            "Read", "Glob", "Grep", "Task",
            "mcp__doc-tools__save_markdown",
            "mcp__doc-tools__list_python_files"
        ],
        mcp_servers={"doc-tools": doc_server},
        agents=[function_analyzer, class_analyzer],
        permission_mode="acceptEdits",
        system_prompt="""
        あなたはドキュメント生成の統括者です。
        Pythonコードを分析し、包括的なAPIドキュメントを生成してください。

        ドキュメントには以下を含めてください:
        - 概要
        - モジュール構成
        - 関数リファレンス
        - クラスリファレンス
        - 使用例
        """
    )

    print(f"=== ドキュメント生成開始: {target_path} ===\n")

    async for message in query(
        prompt=f"""
        {target_path} のPythonコードからドキュメントを生成してください。

        1. list_python_files でファイル一覧を取得
        2. function-analyzer で関数を分析
        3. class-analyzer でクラスを分析
        4. 結果を統合してMarkdownドキュメントを作成
        5. save_markdown で {output_name} として保存
        """,
        options=options
    ):
        print(message)


async def main():
    await generate_documentation(
        "src/",
        f"api_reference_{datetime.now().strftime('%Y%m%d')}.md"
    )


if __name__ == "__main__":
    asyncio.run(main())
