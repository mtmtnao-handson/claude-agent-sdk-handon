# メッセージ型の理解

## 概要

このセクションでは、Claude Agent SDK が返す様々なメッセージ型について学習します。

`query()` 関数は複数の種類のメッセージを返します。これらを適切に処理することで、テキスト出力、ツール使用、結果情報などを取得できます。

---

## 手順1: メッセージ型の全体像

### 1. 主なメッセージ型

| メッセージ型 | 説明 | 含まれる情報 |
|------------|------|-------------|
| `AssistantMessage` | Claude からの応答 | テキスト、ツール使用 |
| `UserMessage` | ユーザーからのメッセージ | ツール結果 |
| `SystemMessage` | システムメッセージ | システムプロンプト |
| `ResultMessage` | 実行結果 | コスト、セッションID |

### 2. Content Block 型

AssistantMessage 内の `content` には以下のブロックが含まれます：

| ブロック型 | 説明 |
|-----------|------|
| `TextBlock` | テキスト応答 |
| `ToolUseBlock` | ツール呼び出し情報 |
| `ToolResultBlock` | ツール実行結果 |

---

## 手順2: AssistantMessage の処理

### 1. テキストとツール使用の両方を処理

**コード:**

```python
import asyncio
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock,
    ToolUseBlock
)

async def process_assistant_message():
    options = ClaudeAgentOptions(
        allowed_tools=["Bash"]
    )

    prompt = "現在のディレクトリにあるファイルを一覧表示して、その後何が見つかったか教えてください"

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):

            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"[テキスト] {block.text}...")
                elif isinstance(block, ToolUseBlock):
                    print(f"[ツール使用] {block.name}")
                    print(f"    入力: {block.input}")
                    print(f"    ID: {block.id}")

asyncio.run(process_assistant_message())
```

<details>
<summary><strong>実行結果を見る</strong></summary>

```
python ./src/basics/02_message_types/docs_samples/02_01_process_assistant_message.py 
[ツール使用] Bash
    入力: {'command': 'ls -la', 'description': 'List all files in current directory'}
    ID: toolu_01N2GUzr8jb69zPEF8GLnrJn
[テキスト] 現在のディレクトリには以下のファイルとフォルダがあります：

## ディレクトリ（フォルダ）
| 名前 | 説明 |
|------|------|
| `docs/` | ドキュメント関連のファイルが格納されているフォルダ（9項目） |
| `external_material/` | 外部資料用のフォルダ（3項目） |
| `src/` | ソースコード用のフォルダ（9項目） |

## ファイル
| 名前 | サイズ | 説明 |
|------|--------|------|
| `mkdocs.yml` | 1,933バイト | MkDocsの設定ファイル（静的サイトジェネレーター用） |

## まとめ
これはMkDocsを使用したドキュメントサイトのプロジェクトのようです。`docs/`フォルダにドキュメントのコンテンツ、`src/`フォルダにソースコード、`mkdocs.yml`に設定が含まれている構成です。

詳しく調べたいフォルダやファイルがあれば、お知らせください！
```

</details>

---

## 手順3: ToolUseBlock の詳細

### 1. ツール使用情報の構造

**コード:**

```python
import asyncio
import json
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    ToolUseBlock
)

async def analyze_tool_use():
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Glob"]
    )

    prompt = "src/ ディレクトリ内の .py ファイルを探して、最初のファイルを読んでください"

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ToolUseBlock):
                    print(f"=== ツール使用 ===")
                    print(f"ツール名: {block.name}")
                    print(f"ツールID: {block.id}")
                    print(f"入力パラメータ:")
                    print(json.dumps(block.input, indent=2, ensure_ascii=False))
                    print()

asyncio.run(analyze_tool_use())
```

<details>
<summary><strong>実行結果を見る</strong></summary>

```
=== ツール使用 ===
ツール名: Glob
ツールID: toolu_011xy9CyfDcynEcPYJ6L6bTH
入力パラメータ:
{
  "pattern": "src/**/*.py"
}

=== ツール使用 ===
ツール名: Read
ツールID: toolu_01YJ6xtz89qfgYPrToNSeyxA
入力パラメータ:
{
  "file_path": "/Users/hirotaka/claude_agent_sdk_hands_on/src/basics/01_query_basic.py"
}
```

</details>

<div style="background-color: #f0f8ff; border: 1px solid #cce5ff; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #0d6efd; line-height: 1;">&#x24D8;</span>
    <span style="font-weight: bold; color: #0d6efd; font-size: 15px;">Note</span>
  </div>
  <div style="color: #454545; line-height: 1.6;">
    <code>ToolUseBlock.id</code> は各ツール呼び出しを一意に識別します。Hooks でツール実行を制御する際に使用します。
  </div>
</div>

---

## 手順4: ResultMessage の活用

### 1. ResultMessage の subtype

`ResultMessage` には `subtype` プロパティがあり、処理結果の状態を示します。

| subtype | 説明 |
|---------|------|
| `success` | 正常完了（session_id, cost_usd, num_turns 等が利用可能） |
| `error` | エラー発生 |
| `interrupted` | 中断された |

<div style="background-color: #fff3cd; border: 1px solid #ffc107; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #856404; line-height: 1;">&#x26A0;</span>
    <span style="font-weight: bold; color: #856404; font-size: 15px;">重要</span>
  </div>
  <div style="color: #454545; line-height: 1.6;">
    <code>session_id</code>, <code>cost_usd</code>, <code>num_turns</code> などのメンバ変数にアクセスする前に、必ず <code>subtype == "success"</code> をチェックしてください。
  </div>
</div>

### 2. 詳細な結果情報

**コード:**

```python
import asyncio
from claude_agent_sdk import query, ResultMessage

async def analyze_result():
    async for message in query(prompt="簡単な挨拶をしてください"):
        if isinstance(message, ResultMessage):
            print("=== 実行結果 ===")
            # subtype をチェックしてからメンバ変数にアクセス
            if message.subtype == "success":
                print(f"セッションID: {message.session_id}")
                print(f"API コスト: ${message.total_cost_usd:.6f}")
                print(f"合計ターン数: {message.num_turns}")
                print(f"実行時間: {message.duration_ms}ms")
                print(f"API実行時間: {message.duration_api_ms}ms")
                if message.usage:
                    print(f"使用量: {message.usage}")
            else:
                print(f"subtype: {message.subtype}")

asyncio.run(analyze_result())
```

<details>
<summary><strong>実行結果を見る</strong></summary>

```
=== 実行結果 ===
セッションID: 58349249-b67c-4434-9532-f77022bd223a
API コスト: $0.019125
合計ターン数: 1
実行時間: 3737ms
API実行時間: 10455ms
使用量: {'input_tokens': 3, 'cache_creation_input_tokens': 0, 'cache_read_input_tokens': 15112, 'output_tokens': 99, 'server_tool_use': {'web_search_requests': 0, 'web_fetch_requests': 0}, 'service_tier': 'standard', 'cache_creation': {'ephemeral_1h_input_tokens': 0, 'ephemeral_5m_input_tokens': 0}}
```

</details>

---

## 手順5: 型安全なメッセージ処理

### 1. パターンマッチングによる処理

Python 3.10+ では `match` 文を使った型による分岐が可能です。

**コード:**

```python
import asyncio
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    UserMessage,
    SystemMessage,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    ToolResultBlock
)

async def pattern_match_messages():
    options = ClaudeAgentOptions(allowed_tools=["Bash"])

    async for message in query(prompt="pwd コマンドを実行して", options=options):
        match message:
            case AssistantMessage(content=content):
                for block in content:
                    match block:
                        case TextBlock(text=text):
                            print(f"[テキスト] {text}")
                        case ToolUseBlock(name=name, input=input_data):
                            print(f"[ツール] {name}: {input_data}")

            case ResultMessage(subtype="success", cost_usd=cost, num_turns=turns):
                print(f"[結果] コスト: ${cost:.4f}, ターン数: {turns}")

            case ResultMessage(subtype=subtype):
                print(f"[結果] subtype: {subtype}")

            case _:
                print(f"[その他] {type(message).__name__}")

asyncio.run(pattern_match_messages())
```

---

## 手順6: メッセージのフィルタリング

### 1. 特定のメッセージ型だけを収集

**コード:**

```python
import asyncio
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock,
    ToolUseBlock
)
from dataclasses import dataclass

@dataclass
class QueryResult:
    texts: list[str]
    tool_uses: list[dict]
    total_cost: float

async def collect_messages(prompt: str) -> QueryResult:
    options = ClaudeAgentOptions(allowed_tools=["Read", "Glob"])

    texts = []
    tool_uses = []
    total_cost = 0.0

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    texts.append(block.text)
                elif isinstance(block, ToolUseBlock):
                    tool_uses.append({
                        "name": block.name,
                        "input": block.input,
                        "id": block.id
                    })
        elif hasattr(message, 'total_cost_usd'):
            total_cost = message.total_cost_usd

    return QueryResult(texts=texts, tool_uses=tool_uses, total_cost=total_cost)

async def main():
    result = await collect_messages("README.md ファイルを探して内容を要約して")
    print(f"テキスト応答数: {len(result.texts)}")
    print(f"ツール使用数: {len(result.tool_uses)}")
    print(f"合計コスト: ${result.total_cost:.4f}")

    for tool in result.tool_uses:
        print(f"  - {tool['name']}")

asyncio.run(main())
```

---

## 手順7: メッセージストリームのロギング

### 1. すべてのメッセージをログに記録

**コード:**

```python
import asyncio
import json
from datetime import datetime
from claude_agent_sdk import query, ClaudeAgentOptions

async def logged_query(prompt: str, log_file: str = "query_log.jsonl"):
    options = ClaudeAgentOptions(allowed_tools=["Read"])

    with open(log_file, "a") as f:
        async for message in query(prompt=prompt, options=options):
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "type": type(message).__name__,
                "data": str(message)[:500]  # 長すぎる場合は切り詰め
            }
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            print(f"[{log_entry['type']}] logged")

asyncio.run(logged_query("このプロジェクトの構造を説明して"))
```

<div style="background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #155724; line-height: 1;">&#x2714;</span>
    <span style="font-weight: bold; color: #155724; font-size: 15px;">ポイント</span>
  </div>
  <div style="color: #155724; line-height: 1.6;">
    JSONL (JSON Lines) 形式でログを記録すると、後から分析しやすくなります。各行が独立した JSON オブジェクトなので、ストリーミング書き込みにも適しています。
  </div>
</div>

---

## 演習問題

### 演習1: メッセージカウンター

各メッセージ型の出現回数をカウントする関数を作成してください。

```python
async def count_message_types(prompt: str) -> dict[str, int]:
    # ここに実装
    pass
```

### 演習2: ツール使用レポート

使用されたツールの統計（ツール名、呼び出し回数、入力パラメータの種類）をレポートする関数を作成してください。

### 演習3: コスト追跡デコレータ

`query()` をラップして、自動的にコストを追跡・累積するデコレータを作成してください。

---

## 次のステップ

メッセージ型を理解しました。次は [エラーハンドリング](03_error_handling.md) で、例外処理とリトライロジックについて学びましょう。
