# allowed_tools 設定

## 概要

このセクションでは、`allowed_tools` オプションを使って Claude が使用できるツールを制御する方法を学習します。

ツールを適切に制限することで、セキュリティを確保しながら必要な機能だけを提供できます。

**サンプルスクリプト:**

このドキュメントの例は、以下のスクリプトで実際に試すことができます：

```bash
src/02_options/02_allowed_tools/
├── 01_basic.py          # 手順2-3: 基本的な使い方、ユースケース別設定
├── 02_mcp_tools.py      # 手順4: MCP ツールの指定
├── 03_dynamic_control.py # 手順5: 動的なツール制御
└── 04_tool_testing.py   # 手順6: ツール制限のテスト
```

```bash
# 基本的な使い方 (手順2-3)
python src/02_options/02_allowed_tools/01_basic.py -l    # モード一覧
python src/02_options/02_allowed_tools/01_basic.py -h    # ヘルプ

# MCP ツール (手順4)
python src/02_options/02_allowed_tools/02_mcp_tools.py -l

# 動的ツール制御 (手順5)
python src/02_options/02_allowed_tools/03_dynamic_control.py -l

# ツール制限テスト (手順6)
python src/02_options/02_allowed_tools/04_tool_testing.py --test-restriction
python src/02_options/02_allowed_tools/04_tool_testing.py --monitor
```

---

## 手順1: ビルトインツール一覧

### 1. 利用可能なツール

| ツール名 | 機能 | リスクレベル |
|---------|------|-------------|
| `Read` | ファイル読み取り | 低 |
| `Write` | ファイル作成/上書き | 中 |
| `Edit` | ファイル編集 | 中 |
| `Bash` | シェルコマンド実行 | **高** |
| `Glob` | ファイルパターン検索 | 低 |
| `Grep` | テキスト検索 | 低 |
| `WebSearch` | Web 検索 | 低 |
| `WebFetch` | Web ページ取得 | 低 |
| `Task` | タスク管理 | 低 |

### 2. リスクレベルの説明

- **低**: 情報取得のみ、システムへの影響なし
- **中**: ファイルを変更可能、適切な確認が必要
- **高**: システムコマンド実行可能、慎重な制御が必要

---

## 手順2: 基本的な使い方

### 1. 特定ツールのみを許可

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

# 読み取り専用ツールのみ許可
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Glob", "Grep"]
)

async def analyze_code():
    prompt = "src/ ディレクトリ内のPythonファイルを分析して"

    async for message in query(prompt=prompt, options=options):
        print(message)
```

**実際に試す:**

```bash
# 読み取り専用モードで実行
python src/02_options/02_allowed_tools/01_basic.py -m read-only -p "src/ ディレクトリ内のPythonファイルを分析して"
```

### 2. 全ツールを許可（デフォルト）

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

# allowed_tools を指定しない = 全ツール利用可能
options = ClaudeAgentOptions()

# または明示的に全ツールを指定
options_explicit = ClaudeAgentOptions(
    allowed_tools=[
        "Read", "Write", "Edit", "Bash",
        "Glob", "Grep", "WebSearch", "WebFetch", "Task"
    ]
)
```

**実際に試す:**

```bash
# フルアクセスモードで実行
python src/02_options/02_allowed_tools/01_basic.py -m full-access -p "このプロジェクトの構造を調査して"
```

<div style="background-color: #fff3cd; border: 1px solid #ffc107; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #856404; line-height: 1;">&#x26A0;</span>
    <span style="font-weight: bold; color: #856404; font-size: 15px;">注意</span>
  </div>
  <div style="color: #454545; line-height: 1.6;">
    <code>allowed_tools</code> を指定しない場合、全ツールが利用可能になります。本番環境では必要なツールのみを明示的に指定することを推奨します。
  </div>
</div>

---

## 手順3: ユースケース別の設定

### 1. コードレビュー用

ファイルを変更せずに分析のみを行う構成。

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions

code_review_options = ClaudeAgentOptions(
    system_prompt="あなたはコードレビューの専門家です。コードを分析し、問題点を指摘してください。",
    allowed_tools=["Read", "Glob", "Grep"]
)
```

**実際に試す:**

```bash
# コードレビューモードで実行
python src/02_options/02_allowed_tools/01_basic.py -m code-review -p "src/02_options/02_allowed_tools/01_basic.py をレビューして"
```

### 2. ドキュメント作成用

既存コードを読んでドキュメントを生成する構成。

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions

doc_writer_options = ClaudeAgentOptions(
    system_prompt="あなたは技術ドキュメントの専門家です。",
    allowed_tools=["Read", "Write", "Glob", "Grep"]
)
```

**実際に試す:**

```bash
# ドキュメント作成モードで実行
python src/02_options/02_allowed_tools/01_basic.py -m doc-writer -p "src/02_options/ のコードを説明するドキュメントを作成して"
```

### 3. 開発作業用

ファイル編集とコマンド実行を許可する構成。

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions

development_options = ClaudeAgentOptions(
    allowed_tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep"],
    permission_mode="acceptEdits"
)
```

**実際に試す:**

```bash
# 開発モードで実行 (permission_mode=acceptEdits)
python src/02_options/02_allowed_tools/01_basic.py -m development -p "hello.py を作成して、Hello World を出力するコードを書いて"
```

### 4. リサーチ用

Web 検索とファイル読み取りを許可する構成。

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions

research_options = ClaudeAgentOptions(
    system_prompt="技術調査を行い、結果をまとめてください。",
    allowed_tools=["Read", "Write", "WebSearch", "WebFetch", "Glob"]
)
```

**実際に試す:**

```bash
# リサーチモードで実行 (Web検索可能)
python src/02_options/02_allowed_tools/01_basic.py -m research -p "Python asyncio の最新のベストプラクティスを調べて"
```

---

## 手順4: MCP ツールの指定

### 1. MCP ツールの命名規則

MCP (Model Context Protocol) サーバーのツールは以下の形式で指定します：

```
mcp__{サーバー名}__{ツール名}
```

### 2. MCP ツールを含む設定

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions

# ビルトインツールと MCP ツールを組み合わせ
options = ClaudeAgentOptions(
    allowed_tools=[
        # ビルトインツール
        "Read",
        "Write",
        "Glob",

        # MCP ツール
        "mcp__filesystem__read_file",
        "mcp__filesystem__write_file",
        "mcp__database__query",
        "mcp__slack__send_message"
    ]
)
```

**実際に試す:**

```bash
# MCP ツール設定の一覧を表示
python src/02_options/02_allowed_tools/02_mcp_tools.py -l

# ビルトインツールのみで実行
python src/02_options/02_allowed_tools/02_mcp_tools.py -m builtin -p "ファイル一覧を表示して"

# MCP ツールを含む設定で実行
python src/02_options/02_allowed_tools/02_mcp_tools.py -m with-mcp -p "利用可能なツールを確認して"
```

<div style="background-color: #f0f8ff; border: 1px solid #cce5ff; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #0d6efd; line-height: 1;">&#x24D8;</span>
    <span style="font-weight: bold; color: #0d6efd; font-size: 15px;">Note</span>
  </div>
  <div style="color: #454545; line-height: 1.6;">
    MCP ツールを使用するには、対応する MCP サーバーが <code>mcp_servers</code> オプションで設定されている必要があります。
  </div>
</div>

---

## 手順5: 動的なツール制御

### 1. 条件に基づくツール選択

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

def get_tools_for_task(task_type: str) -> list[str]:
    """タスクタイプに応じたツールリストを返す"""

    base_tools = ["Read", "Glob", "Grep"]

    task_tools = {
        "analyze": base_tools,
        "document": base_tools + ["Write"],
        "develop": base_tools + ["Write", "Edit", "Bash"],
        "research": base_tools + ["WebSearch", "WebFetch"],
    }

    return task_tools.get(task_type, base_tools)

async def execute_task(task_type: str, prompt: str):
    tools = get_tools_for_task(task_type)
    print(f"使用ツール: {tools}")

    options = ClaudeAgentOptions(allowed_tools=tools)

    async for message in query(prompt=prompt, options=options):
        print(message)
```

**実際に試す:**

```bash
# 設定一覧を表示
python src/02_options/02_allowed_tools/03_dynamic_control.py -l

# タスクタイプベースで実行
python src/02_options/02_allowed_tools/03_dynamic_control.py -t analyze -p "コードを分析して"
python src/02_options/02_allowed_tools/03_dynamic_control.py -t document -p "ドキュメントを作成して"
python src/02_options/02_allowed_tools/03_dynamic_control.py -t develop -p "機能を実装して"
python src/02_options/02_allowed_tools/03_dynamic_control.py -t research -p "技術を調査して"
```

### 2. ユーザー権限に基づく制御

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions
from enum import Enum

class UserRole(Enum):
    VIEWER = "viewer"
    EDITOR = "editor"
    ADMIN = "admin"

def get_tools_for_role(role: UserRole) -> list[str]:
    """ユーザー権限に応じたツールを返す"""

    role_tools = {
        UserRole.VIEWER: ["Read", "Glob", "Grep"],
        UserRole.EDITOR: ["Read", "Write", "Edit", "Glob", "Grep"],
        UserRole.ADMIN: ["Read", "Write", "Edit", "Bash", "Glob", "Grep", "WebSearch", "WebFetch"],
    }

    return role_tools[role]

# 使用例
viewer_options = ClaudeAgentOptions(
    allowed_tools=get_tools_for_role(UserRole.VIEWER)
)

admin_options = ClaudeAgentOptions(
    allowed_tools=get_tools_for_role(UserRole.ADMIN)
)
```

**実際に試す:**

```bash
# ユーザー権限ベースで実行
python src/02_options/02_allowed_tools/03_dynamic_control.py -r viewer -p "プロジェクトの構造を確認して"
python src/02_options/02_allowed_tools/03_dynamic_control.py -r editor -p "README.md を更新して"
python src/02_options/02_allowed_tools/03_dynamic_control.py -r admin -p "プロジェクトをセットアップして"
```

---

## 手順6: ツール制限のテスト

### 1. 許可されていないツールの動作確認

**コード:**

```python
import asyncio
from claude_agent_sdk import ClaudeAgentOptions, query, AssistantMessage, TextBlock

async def test_tool_restriction():
    # Write ツールを禁止
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Glob"]
    )

    # Write が必要なタスクを要求
    prompt = "hello.py というファイルを作成してください"

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)

asyncio.run(test_tool_restriction())
```

**実際に試す:**

```bash
# 許可されていないツールの動作確認
python src/02_options/02_allowed_tools/04_tool_testing.py --test-restriction
python src/02_options/02_allowed_tools/04_tool_testing.py --test-restriction -p "hello.py を作成して"

# カスタムツールセットで制限テスト
python src/02_options/02_allowed_tools/04_tool_testing.py --tools Read,Glob -p "ファイルを作成して"
```

<details>
<summary><strong>実行結果を見る</strong></summary>


申し訳ありませんが、Write ツールが利用できないため、ファイルを作成することができません。
代わりに、以下のコード例をお見せします：

```python
# hello.py
print("Hello, World!")
```

このコードをご自身でファイルに保存してください。


</details>

### 2. ツール使用状況のモニタリング

**コード:**

```python
import asyncio
from collections import Counter
from claude_agent_sdk import (
    ClaudeAgentOptions,
    query,
    AssistantMessage,
    ToolUseBlock
)

async def monitor_tool_usage(prompt: str, options: ClaudeAgentOptions):
    """ツール使用状況をモニタリング"""

    tool_counter = Counter()

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ToolUseBlock):
                    tool_counter[block.name] += 1

    print("\n=== ツール使用統計 ===")
    for tool, count in tool_counter.most_common():
        print(f"  {tool}: {count}回")

    return tool_counter

# 使用例
asyncio.run(monitor_tool_usage(
    "プロジェクトの構造を分析して",
    ClaudeAgentOptions(allowed_tools=["Read", "Glob", "Grep"])
))
```

**実際に試す:**

```bash
# ツール使用状況をモニタリング
python src/02_options/02_allowed_tools/04_tool_testing.py --monitor -p "プロジェクトの構造を分析して"

# 詳細出力付きでモニタリング
python src/02_options/02_allowed_tools/04_tool_testing.py --monitor -v -p "src/ ディレクトリを調査して"

# カスタムツールセットでモニタリング
python src/02_options/02_allowed_tools/04_tool_testing.py --monitor --tools Read,Glob,Grep,Edit -p "コードを分析して"
```

<div style="background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #155724; line-height: 1;">&#x2714;</span>
    <span style="font-weight: bold; color: #155724; font-size: 15px;">ポイント</span>
  </div>
  <div style="color: #155724; line-height: 1.6;">
    ツール使用状況をモニタリングすることで、最適なツール構成を見つけることができます。不要なツールを許可している場合は、セキュリティ向上のために制限を検討しましょう。
  </div>
</div>

---

## 演習問題

### 演習1: ツールプリセット

以下のプリセットを持つツール管理クラスを作成してください：
- `readonly`: 読み取り専用
- `developer`: 開発者向け（ファイル編集可）
- `admin`: 管理者向け（全ツール）

### 演習2: ツール監査ログ

使用されたツールを監査ログとして記録するラッパー関数を作成してください。

### 演習3: ツールクォータ

特定のツール（例: Bash）の使用回数を制限するメカニズムを実装してください。

---

## 次のステップ

ツールの許可設定を理解しました。次は [permission_mode](03_permission_mode.md) で、権限モードの設定について学びましょう。
