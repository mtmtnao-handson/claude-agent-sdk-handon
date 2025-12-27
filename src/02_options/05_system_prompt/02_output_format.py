"""
出力形式の指定 (手順3)

system_prompt で出力形式（JSON、Markdown など）を指定します。
構造化された出力により、プログラムでの処理が容易になります。

Usage:
    python 02_output_format.py -l                    # フォーマット一覧
    python 02_output_format.py -f json -p "src/ を分析して"
    python 02_output_format.py -f markdown -p "レポートを作成して"
    python 02_output_format.py -f yaml -p "設定を生成して"
"""
import argparse
import asyncio
import json
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, TextBlock, ToolUseBlock

# =============================================================================
# 出力形式プロンプト定義
# =============================================================================

JSON_FORMAT_PROMPT = """分析結果は必ず以下の JSON 形式で出力してください:

{
    "summary": "分析の要約",
    "findings": [
        {
            "type": "bug" | "improvement" | "info",
            "severity": "high" | "medium" | "low",
            "description": "説明",
            "location": "ファイル:行番号"
        }
    ],
    "recommendations": ["推奨事項1", "推奨事項2"]
}

JSON 以外のテキストは出力しないでください。"""

MARKDOWN_FORMAT_PROMPT = """レポートは以下の Markdown 形式で出力してください:

# レポートタイトル

## 概要
[1-2 文の要約]

## 詳細分析

### セクション1
- ポイント1
- ポイント2

### セクション2
```python
# コード例があれば含める
```

## 結論
[推奨事項と次のステップ]

---
生成日時: [現在の日時]
"""

YAML_FORMAT_PROMPT = """設定は以下の YAML 形式で出力してください:

# 設定ファイル
name: プロジェクト名
version: 1.0.0

settings:
  - key: value
  - key2: value2

options:
  enabled: true
  config:
    param1: value1
    param2: value2

YAML 以外のテキストは出力しないでください。
"""

CSV_FORMAT_PROMPT = """結果は以下の CSV 形式で出力してください:

ファイル名,行数,関数数,クラス数,コメント率
file1.py,100,5,2,15%
file2.py,200,10,3,20%

CSV のヘッダー行を必ず含めてください。
CSV 以外のテキストは出力しないでください。
"""

TABLE_FORMAT_PROMPT = """結果を以下の Markdown テーブル形式で出力してください:

| 項目 | 値 | 説明 |
|-----|-----|------|
| 項目1 | 値1 | 説明1 |
| 項目2 | 値2 | 説明2 |

テーブルは見やすく整形してください。
"""

LIST_FORMAT_PROMPT = """結果を以下の番号付きリスト形式で出力してください:

1. 最初の項目
   - サブ項目1
   - サブ項目2

2. 2番目の項目
   - サブ項目1
   - サブ項目2

3. 3番目の項目

簡潔で分かりやすい形式で出力してください。
"""

# =============================================================================
# フォーマットマッピング
# =============================================================================

FORMATS = {
    "json": {
        "name": "JSON",
        "prompt": JSON_FORMAT_PROMPT,
        "validator": lambda text: json.loads(text),  # JSON 検証
    },
    "markdown": {
        "name": "Markdown",
        "prompt": MARKDOWN_FORMAT_PROMPT,
        "validator": None,
    },
    "yaml": {
        "name": "YAML",
        "prompt": YAML_FORMAT_PROMPT,
        "validator": None,
    },
    "csv": {
        "name": "CSV",
        "prompt": CSV_FORMAT_PROMPT,
        "validator": None,
    },
    "table": {
        "name": "Markdown Table",
        "prompt": TABLE_FORMAT_PROMPT,
        "validator": None,
    },
    "list": {
        "name": "Numbered List",
        "prompt": LIST_FORMAT_PROMPT,
        "validator": None,
    },
}


def parse_args() -> argparse.Namespace:
    """コマンドライン引数をパース"""
    parser = argparse.ArgumentParser(
        description="system_prompt による出力形式指定",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-f", "--format",
        choices=list(FORMATS.keys()),
        default="json",
        help="出力形式 (default: json)"
    )
    parser.add_argument(
        "-p", "--prompt",
        default="このプロジェクトの Python ファイルを分析してください",
        help="実行するプロンプト"
    )
    parser.add_argument(
        "-l", "--list-formats",
        action="store_true",
        help="利用可能な形式の一覧を表示して終了"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="詳細出力"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="出力の検証を実行（JSON のみ）"
    )
    return parser.parse_args()


def print_formats():
    """全フォーマットの詳細を表示"""
    print("=" * 60)
    print("利用可能な出力形式一覧")
    print("=" * 60)

    for key, fmt in FORMATS.items():
        print(f"\n[{key}] {fmt['name']}")
        # 最初の5行を表示
        lines = fmt['prompt'].strip().split('\n')[:5]
        for line in lines:
            print(f"  {line}")
        print("  ...")


async def main():
    """メイン処理"""
    args = parse_args()

    if args.list_formats:
        print_formats()
        return

    fmt = FORMATS[args.format]
    options = ClaudeAgentOptions(
        system_prompt=fmt['prompt'],
        allowed_tools=["Read", "Glob", "Grep"]
    )

    print("=" * 60)
    print(f"出力形式: {fmt['name']} ({args.format})")
    if args.verbose:
        print("-" * 60)
        print("システムプロンプト:")
        print(fmt['prompt'])
    print("-" * 60)
    print(f"プロンプト: {args.prompt}")
    print("=" * 60)
    print()

    output_text = ""

    async for message in query(
        prompt=args.prompt,
        options=options
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    output_text += block.text
                    print(block.text)
                elif isinstance(block, ToolUseBlock):
                    if args.verbose:
                        print(f"\n[Tool] {block.name}: {block.input}")

    # 検証
    if args.validate and args.format == "json" and output_text:
        print("\n" + "=" * 60)
        print("JSON 検証")
        print("=" * 60)
        try:
            parsed = json.loads(output_text)
            print("✓ 有効な JSON です")
            print(f"整形版:\n{json.dumps(parsed, indent=2, ensure_ascii=False)}")
        except json.JSONDecodeError as e:
            print(f"✗ JSON パースエラー: {e}")


if __name__ == "__main__":
    asyncio.run(main())
