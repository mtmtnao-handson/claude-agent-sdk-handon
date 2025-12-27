# 実践プロジェクト: ドキュメント生成

## 概要

このプロジェクトでは、Claude Agent SDK を使ってコードから自動的にドキュメントを生成するツールを構築します。

API ドキュメント、README、使用例などを自動生成します。

---

## プロジェクト構成

```
doc_generator/
├── __init__.py
├── agents.py        # ドキュメント生成エージェント
├── analyzers.py     # コード解析ツール
├── templates.py     # ドキュメントテンプレート
├── config.py        # 設定
└── main.py          # メインアプリケーション
```

---

## 手順1: 設定ファイルの作成

### config.py

**コード:**

```python
"""ドキュメント生成の設定"""
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum

class OutputFormat(Enum):
    MARKDOWN = "markdown"
    RST = "rst"
    HTML = "html"

@dataclass
class DocConfig:
    """ドキュメント生成設定"""
    source_path: Path
    output_path: Path = field(default_factory=lambda: Path("./docs"))
    format: OutputFormat = OutputFormat.MARKDOWN
    language: str = "ja"
    include_examples: bool = True
    include_source_links: bool = True

    # 除外設定
    excluded_dirs: list[str] = field(default_factory=lambda: [
        "tests", "test", "__pycache__", ".git", "node_modules"
    ])
    excluded_files: list[str] = field(default_factory=lambda: [
        "setup.py", "conftest.py"
    ])

@dataclass
class StyleConfig:
    """スタイル設定"""
    heading_style: str = "atx"  # atx (#) or setext (underline)
    code_fence: str = "```"
    list_indent: int = 2
    max_line_length: int = 80

DEFAULT_DOC_CONFIG = DocConfig(source_path=Path("."))
DEFAULT_STYLE_CONFIG = StyleConfig()
```

---

## 手順2: コード解析ツールの実装

### analyzers.py

**コード:**

```python
"""コード解析ツール"""
import ast
from pathlib import Path
from dataclasses import dataclass
from claude_agent_sdk import tool, create_sdk_mcp_server

@dataclass
class FunctionInfo:
    name: str
    docstring: str
    args: list[str]
    returns: str
    decorators: list[str]
    line_number: int

@dataclass
class ClassInfo:
    name: str
    docstring: str
    bases: list[str]
    methods: list[FunctionInfo]
    line_number: int

@tool(
    "analyze_python_file",
    "Python ファイルを解析し、クラスと関数の情報を抽出します",
    {"file_path": str}
)
async def analyze_python_file(args: dict) -> dict:
    """Python ファイルを解析"""
    file_path = Path(args["file_path"])

    if not file_path.exists():
        return {"content": [{"type": "text", "text": f"ファイルが存在しません: {file_path}"}]}

    try:
        content = file_path.read_text()
        tree = ast.parse(content)
    except SyntaxError as e:
        return {"content": [{"type": "text", "text": f"構文エラー: {e}"}]}

    result = {
        "module_docstring": ast.get_docstring(tree) or "",
        "classes": [],
        "functions": [],
        "imports": []
    }

    for node in ast.walk(tree):
        # インポート
        if isinstance(node, ast.Import):
            for alias in node.names:
                result["imports"].append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                result["imports"].append(f"{module}.{alias.name}")

        # クラス
        elif isinstance(node, ast.ClassDef):
            methods = []
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    methods.append({
                        "name": item.name,
                        "docstring": ast.get_docstring(item) or "",
                        "args": [arg.arg for arg in item.args.args],
                        "line": item.lineno
                    })

            result["classes"].append({
                "name": node.name,
                "docstring": ast.get_docstring(node) or "",
                "bases": [base.id if isinstance(base, ast.Name) else str(base) for base in node.bases],
                "methods": methods,
                "line": node.lineno
            })

        # トップレベル関数
        elif isinstance(node, ast.FunctionDef) and isinstance(node, ast.FunctionDef):
            # クラスメソッドは除外（すでに処理済み）
            if not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree)):
                result["functions"].append({
                    "name": node.name,
                    "docstring": ast.get_docstring(node) or "",
                    "args": [arg.arg for arg in node.args.args],
                    "line": node.lineno
                })

    # 結果をフォーマット
    output = f"# {file_path.name} の解析結果\n\n"

    if result["module_docstring"]:
        output += f"## モジュール説明\n{result['module_docstring']}\n\n"

    if result["classes"]:
        output += f"## クラス ({len(result['classes'])} 個)\n"
        for cls in result["classes"]:
            output += f"### {cls['name']}\n"
            output += f"- 行: {cls['line']}\n"
            output += f"- 継承: {', '.join(cls['bases']) or 'なし'}\n"
            if cls["docstring"]:
                output += f"- 説明: {cls['docstring'][:100]}...\n"
            output += f"- メソッド: {len(cls['methods'])} 個\n\n"

    if result["functions"]:
        output += f"## 関数 ({len(result['functions'])} 個)\n"
        for func in result["functions"]:
            output += f"- `{func['name']}({', '.join(func['args'])})`\n"

    return {"content": [{"type": "text", "text": output}]}

@tool(
    "get_project_structure",
    "プロジェクトの構造を取得します",
    {"path": str, "max_depth": int}
)
async def get_project_structure(args: dict) -> dict:
    """プロジェクト構造を取得"""
    path = Path(args["path"])
    max_depth = args.get("max_depth", 3)

    if not path.exists():
        return {"content": [{"type": "text", "text": f"パスが存在しません: {path}"}]}

    def build_tree(current_path: Path, depth: int = 0, prefix: str = "") -> str:
        if depth > max_depth:
            return ""

        result = ""
        items = sorted(current_path.iterdir(), key=lambda x: (x.is_file(), x.name))

        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            connector = "└── " if is_last else "├── "
            extension = "    " if is_last else "│   "

            # 除外ディレクトリをスキップ
            if item.name in [".git", "__pycache__", "node_modules", ".venv", "venv"]:
                continue

            result += f"{prefix}{connector}{item.name}\n"

            if item.is_dir():
                result += build_tree(item, depth + 1, prefix + extension)

        return result

    tree = f"{path.name}/\n{build_tree(path)}"

    return {"content": [{"type": "text", "text": f"```\n{tree}```"}]}

# MCP サーバーを作成
analyzer_server = create_sdk_mcp_server(
    name="analyzers",
    version="1.0.0",
    tools=[analyze_python_file, get_project_structure]
)
```

---

## 手順3: ドキュメント生成エージェント

### agents.py

**コード:**

```python
"""ドキュメント生成エージェント"""
from claude_agent_sdk import AgentDefinition

# API ドキュメント生成エージェント
api_doc_generator = AgentDefinition(
    description="API ドキュメントを生成するエージェント",
    prompt="""あなたはテクニカルライターです。Python コードから API ドキュメントを生成してください。

## 出力形式

各クラス/関数について以下を含めてください：

### クラス名 / 関数名

**説明**
[クラス/関数の目的と機能]

**パラメータ**
| 名前 | 型 | 説明 |
|------|-----|------|
| param1 | str | 説明 |

**戻り値**
[戻り値の説明]

**使用例**
```python
# 使用例コード
```

**注意事項**
[注意点があれば]
""",
    tools=["Read", "Glob"],
    model="sonnet"
)

# README 生成エージェント
readme_generator = AgentDefinition(
    description="README.md を生成するエージェント",
    prompt="""あなたはテクニカルライターです。プロジェクトの README.md を生成してください。

## 構成

# プロジェクト名

## 概要
[プロジェクトの説明]

## 特徴
- 特徴1
- 特徴2

## インストール
```bash
pip install xxx
```

## クイックスタート
```python
# 基本的な使用例
```

## ドキュメント
[ドキュメントへのリンク]

## ライセンス
[ライセンス情報]
""",
    tools=["Read", "Glob", "Write"],
    model="sonnet"
)

# 使用例生成エージェント
example_generator = AgentDefinition(
    description="使用例を生成するエージェント",
    prompt="""あなたはテクニカルライターです。コードの使用例を生成してください。

## ルール
1. 実行可能なコード例を提供
2. 段階的に複雑さを増す
3. エラーハンドリングも含める
4. コメントで説明を追加
""",
    tools=["Read", "Glob", "Write"],
    model="sonnet"
)

# エージェント辞書
DOC_AGENTS = {
    "api": api_doc_generator,
    "readme": readme_generator,
    "examples": example_generator
}
```

---

## 手順4: ドキュメントテンプレート

### templates.py

**コード:**

```python
"""ドキュメントテンプレート"""

API_DOC_TEMPLATE = """# {module_name} API リファレンス

## 概要

{module_description}

---

## クラス

{classes_section}

---

## 関数

{functions_section}

---

*このドキュメントは Claude Agent SDK によって自動生成されました。*
"""

CLASS_TEMPLATE = """### {class_name}

{class_description}

**継承**: {bases}

#### コンストラクタ

```python
{class_name}({init_args})
```

#### メソッド

{methods_section}
"""

METHOD_TEMPLATE = """##### {method_name}

```python
{method_signature}
```

{method_description}

**パラメータ**

{parameters_table}

**戻り値**

{return_description}
"""

README_TEMPLATE = """# {project_name}

{project_description}

## インストール

```bash
pip install {package_name}
```

## クイックスタート

```python
{quickstart_code}
```

## ドキュメント

詳細なドキュメントは [docs/](./docs/) を参照してください。

## ライセンス

{license}
"""

def render_api_doc(module_info: dict) -> str:
    """API ドキュメントをレンダリング"""
    return API_DOC_TEMPLATE.format(**module_info)

def render_readme(project_info: dict) -> str:
    """README をレンダリング"""
    return README_TEMPLATE.format(**project_info)
```

---

## 手順5: メインアプリケーション

### main.py

**コード:**

```python
"""ドキュメント生成のメインアプリケーション"""
import asyncio
from pathlib import Path
from datetime import datetime
from claude_agent_sdk import ClaudeAgentOptions, query, ResultMessage

from .config import DocConfig, DEFAULT_DOC_CONFIG
from .agents import DOC_AGENTS
from .analyzers import analyzer_server

async def generate_documentation(
    source_path: str,
    output_path: str = None,
    doc_types: list[str] = None,
    language: str = "ja"
):
    """ドキュメントを生成"""

    config = DocConfig(
        source_path=Path(source_path),
        language=language
    )

    if output_path:
        config.output_path = Path(output_path)

    config.output_path.mkdir(parents=True, exist_ok=True)

    # ドキュメントタイプ
    if doc_types is None:
        doc_types = ["api", "readme", "examples"]

    # オプションを設定
    options = ClaudeAgentOptions(
        cwd=config.source_path,
        agents=DOC_AGENTS,
        mcp_servers={"analyzer": analyzer_server},
        allowed_tools=[
            "Read", "Write", "Glob", "Grep", "Task",
            "mcp__analyzer__analyze_python_file",
            "mcp__analyzer__get_project_structure"
        ],
        permission_mode="acceptEdits",
        max_turns=50,
        system_prompt=f"""あなたはドキュメント生成アシスタントです。

## 設定
- ソース: {config.source_path}
- 出力先: {config.output_path}
- 言語: {config.language}

## ドキュメント生成手順
1. get_project_structure でプロジェクト構造を把握
2. analyze_python_file で各ファイルを解析
3. 適切なエージェントでドキュメントを生成
4. 出力先にファイルを保存
"""
    )

    # 生成プロンプト
    prompt = f"""以下のドキュメントを生成してください：

生成タイプ: {', '.join(doc_types)}
出力先: {config.output_path}

手順:
1. プロジェクト構造を取得
2. Python ファイルを解析
3. 以下のドキュメントを生成:
"""

    if "readme" in doc_types:
        prompt += f"   - README.md を {config.output_path}/README.md に生成\n"
    if "api" in doc_types:
        prompt += f"   - API ドキュメントを {config.output_path}/api/ に生成\n"
    if "examples" in doc_types:
        prompt += f"   - 使用例を {config.output_path}/examples/ に生成\n"

    print(f"ドキュメント生成開始: {config.source_path}")
    print(f"出力先: {config.output_path}")
    print("-" * 50)

    total_cost = 0.0
    generated_files = []

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, ResultMessage):
            total_cost = message.total_cost_usd
        else:
            print(".", end="", flush=True)

    print("\n" + "-" * 50)
    print(f"ドキュメント生成完了")
    print(f"出力先: {config.output_path}")
    print(f"コスト: ${total_cost:.4f}")

    # 生成されたファイルを一覧
    print("\n生成されたファイル:")
    for file in config.output_path.rglob("*.md"):
        print(f"  - {file.relative_to(config.output_path)}")

    return config.output_path

# CLI エントリーポイント
def main():
    import argparse

    parser = argparse.ArgumentParser(description="AI ドキュメント生成ツール")
    parser.add_argument("source", help="ソースコードのパス")
    parser.add_argument("-o", "--output", help="出力先ディレクトリ")
    parser.add_argument(
        "-t", "--types",
        nargs="+",
        choices=["api", "readme", "examples"],
        default=["api", "readme"],
        help="生成するドキュメントタイプ"
    )
    parser.add_argument(
        "-l", "--language",
        default="ja",
        choices=["ja", "en"],
        help="ドキュメントの言語"
    )

    args = parser.parse_args()

    asyncio.run(generate_documentation(
        source_path=args.source,
        output_path=args.output,
        doc_types=args.types,
        language=args.language
    ))

if __name__ == "__main__":
    main()
```

---

## 使用例

### コマンドラインから実行

```bash
# 全ドキュメントを生成
python -m doc_generator /path/to/project

# API ドキュメントのみ
python -m doc_generator /path/to/project -t api

# 英語でドキュメント生成
python -m doc_generator /path/to/project -l en -o ./english_docs
```

### Python から呼び出し

```python
import asyncio
from doc_generator.main import generate_documentation

async def main():
    output = await generate_documentation(
        source_path="/path/to/project",
        doc_types=["api", "readme"],
        language="ja"
    )
    print(f"ドキュメントを生成しました: {output}")

asyncio.run(main())
```

---

## まとめ

このハンズオンでは、Claude Agent SDK を使って以下を学習しました：

1. **基本操作**: query() 関数、メッセージ型、エラーハンドリング
2. **オプション設定**: allowed_tools, permission_mode, system_prompt など
3. **ビルトインツール**: ファイル操作、検索、Bash、Web ツール
4. **応用機能**: セッション、サブエージェント、Hooks、カスタムツール、MCP
5. **実践プロジェクト**: コードレビューア、ドキュメント生成

これらの知識を活用して、独自のエージェントアプリケーションを構築してください！

---

## 参考リンク

- [Claude Agent SDK 公式ドキュメント](https://docs.anthropic.com/claude-code/agent-sdk)
- [MCP (Model Context Protocol)](https://modelcontextprotocol.io/)
- [Claude Code](https://claude.ai/claude-code)
