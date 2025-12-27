# ビルトインツール概要

## 概要

このセクションでは、Claude Agent SDK に組み込まれているビルトインツールの全体像を学習します。

Claude は様々なツールを使って、ファイル操作、コマンド実行、Web 検索などを自律的に実行できます。

---

## 手順1: ツール一覧

### 1. 全ビルトインツール

| ツール名 | カテゴリ | 機能 | リスク |
|---------|---------|------|-------|
| `Read` | ファイル | ファイル読み取り | 低 |
| `Write` | ファイル | ファイル作成/上書き | 中 |
| `Edit` | ファイル | ファイル部分編集 | 中 |
| `Glob` | 検索 | ファイルパターン検索 | 低 |
| `Grep` | 検索 | テキスト内容検索 | 低 |
| `Bash` | システム | シェルコマンド実行 | **高** |
| `WebSearch` | Web | インターネット検索 | 低 |
| `WebFetch` | Web | Web ページ取得 | 低 |
| `Task` | 管理 | タスク管理 | 低 |

### 2. カテゴリ別の特徴

```
ファイル操作: Read → Write → Edit
  読み取り → 新規作成 → 部分編集

検索: Glob → Grep
  ファイル発見 → 内容検索

Web: WebSearch → WebFetch
  検索 → 詳細取得

システム: Bash
  任意コマンド実行
```

---

## 手順2: ツールの使用パターン

### 1. 基本的なフロー

**コード:**

```python
import asyncio
from claude_agent_sdk import (
    ClaudeAgentOptions,
    query,
    AssistantMessage,
    ToolUseBlock
)

async def observe_tool_usage():
    """ツール使用を観察"""

    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Glob", "Grep"],
        permission_mode="acceptEdits"
    )

    prompt = "src/ ディレクトリ内の Python ファイルを探し、main という関数を含むファイルを見つけてください"

    tools_used = []

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ToolUseBlock):
                    tools_used.append({
                        "tool": block.name,
                        "input": block.input
                    })
                    print(f"[{block.name}] {block.input}")

    print(f"\n使用されたツール: {[t['tool'] for t in tools_used]}")

asyncio.run(observe_tool_usage())
```

<details>
<summary><strong>実行結果を見る</strong></summary>

```
[Glob] {'pattern': 'src/**/*.py'}
[Grep] {'pattern': 'def main', 'path': 'src/'}
[Read] {'file_path': 'src/main.py'}

使用されたツール: ['Glob', 'Grep', 'Read']
```

</details>

### 2. 典型的なツール連携

| タスク | ツール連携パターン |
|-------|-------------------|
| コード分析 | Glob → Read → (繰り返し) |
| 関数検索 | Glob → Grep → Read |
| ファイル作成 | Read(既存確認) → Write |
| コード修正 | Read → Edit |
| リファクタリング | Glob → Read → Edit → (繰り返し) |
| ビルド実行 | Bash |
| 情報調査 | WebSearch → WebFetch |

---

## 手順3: ツールの入出力

### 1. 各ツールの入出力形式

**Read:**
```python
# 入力
{"file_path": "/path/to/file.py", "offset": 0, "limit": 1000}

# 出力
{"content": "ファイルの内容...", "truncated": False}
```

**Write:**
```python
# 入力
{"file_path": "/path/to/file.py", "content": "新しい内容"}

# 出力
{"success": True}
```

**Edit:**
```python
# 入力
{"file_path": "/path/to/file.py", "old_string": "古い文字列", "new_string": "新しい文字列"}

# 出力
{"success": True}
```

**Glob:**
```python
# 入力
{"pattern": "src/**/*.py", "path": "/project"}

# 出力
{"files": ["src/main.py", "src/utils.py", ...]}
```

**Grep:**
```python
# 入力
{"pattern": "def main", "path": "src/", "glob": "*.py"}

# 出力
{"matches": [{"file": "src/main.py", "line": 10, "content": "def main():"}]}
```

**Bash:**
```python
# 入力
{"command": "ls -la", "timeout": 30000}

# 出力
{"stdout": "...", "stderr": "", "exit_code": 0}
```

---

## 手順4: ツール使用の制御

### 1. ツールの有効化/無効化

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions

# 読み取り専用
readonly = ClaudeAgentOptions(
    allowed_tools=["Read", "Glob", "Grep"]
)

# ファイル操作のみ（Bash 禁止）
file_only = ClaudeAgentOptions(
    allowed_tools=["Read", "Write", "Edit", "Glob", "Grep"]
)

# 全ツール有効
all_tools = ClaudeAgentOptions(
    allowed_tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep", "WebSearch", "WebFetch", "Task"]
)

# ツール指定なし = 全ツール有効
default = ClaudeAgentOptions()
```

### 2. ツール使用のモニタリング

**コード:**

```python
import asyncio
from collections import Counter
from claude_agent_sdk import (
    ClaudeAgentOptions,
    query,
    AssistantMessage,
    ToolUseBlock,
    ResultMessage
)

async def tool_statistics(prompt: str):
    """ツール使用統計を収集"""

    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Write", "Edit", "Glob", "Grep", "Bash"]
    )

    tool_counter = Counter()
    tool_inputs = []

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ToolUseBlock):
                    tool_counter[block.name] += 1
                    tool_inputs.append({
                        "tool": block.name,
                        "input": block.input
                    })

        if isinstance(message, ResultMessage):
            print("\n=== ツール使用統計 ===")
            print(f"合計ツール呼び出し: {sum(tool_counter.values())}")
            print("\nツール別:")
            for tool, count in tool_counter.most_common():
                print(f"  {tool}: {count}回")
            print(f"\nAPI コスト: ${message.total_cost_usd:.4f}")

    return tool_counter, tool_inputs

asyncio.run(tool_statistics("このプロジェクトの構造を分析してレポートを作成して"))
```

---

## 手順5: ツールのベストプラクティス

### 1. 安全なツール選択

<div style="background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #155724; line-height: 1;">&#x2714;</span>
    <span style="font-weight: bold; color: #155724; font-size: 15px;">推奨</span>
  </div>
  <div style="color: #155724; line-height: 1.6;">
    <ul style="margin: 0; padding-left: 20px;">
      <li>必要最小限のツールのみを有効化</li>
      <li>本番環境では Bash を慎重に制限</li>
      <li>機密ファイルへのアクセスを制限</li>
    </ul>
  </div>
</div>

<div style="background-color: #fff3cd; border: 1px solid #ffc107; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #856404; line-height: 1;">&#x26A0;</span>
    <span style="font-weight: bold; color: #856404; font-size: 15px;">注意</span>
  </div>
  <div style="color: #454545; line-height: 1.6;">
    <ul style="margin: 0; padding-left: 20px;">
      <li>Bash ツールは最も強力だが最も危険</li>
      <li>Write/Edit は意図しない上書きの可能性</li>
      <li>全ツール有効はテスト環境でのみ推奨</li>
    </ul>
  </div>
</div>

### 2. タスク別推奨構成

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions

# コードレビュー: 読み取りのみ
CODE_REVIEW_TOOLS = ["Read", "Glob", "Grep"]

# ドキュメント作成: 読み取り + 書き込み
DOCUMENTATION_TOOLS = ["Read", "Write", "Glob", "Grep"]

# 開発作業: ファイル操作 + コマンド
DEVELOPMENT_TOOLS = ["Read", "Write", "Edit", "Bash", "Glob", "Grep"]

# リサーチ: 読み取り + Web
RESEARCH_TOOLS = ["Read", "Glob", "Grep", "WebSearch", "WebFetch"]

def get_task_options(task_type: str) -> ClaudeAgentOptions:
    tools_map = {
        "review": CODE_REVIEW_TOOLS,
        "document": DOCUMENTATION_TOOLS,
        "develop": DEVELOPMENT_TOOLS,
        "research": RESEARCH_TOOLS,
    }

    return ClaudeAgentOptions(
        allowed_tools=tools_map.get(task_type, CODE_REVIEW_TOOLS)
    )
```

---

## 演習問題

### 演習1: ツール使用ログ

全てのツール使用をログファイルに記録するラッパー関数を作成してください。

### 演習2: ツール使用制限

特定のツール（例: Bash）の使用回数を制限するメカニズムを実装してください。

### 演習3: ツール推薦システム

プロンプトを分析し、最適なツール構成を推薦する関数を作成してください。

---

## 次のステップ

ビルトインツールの全体像を理解しました。次は [ファイル操作](02_file_operations.md) で、Read, Write, Edit ツールの詳細を学びましょう。
