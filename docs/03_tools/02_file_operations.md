# ファイル操作ツール

## 概要

このセクションでは、ファイル操作に使用する Read, Write, Edit ツールの詳細を学習します。

これらのツールを使いこなすことで、コードの読み取り、生成、修正を効率的に行えます。

---

## 手順1: Read ツール

### 1. 基本的な使い方

Read ツールはファイルの内容を読み取ります。

**コード:**

```python
import asyncio
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    allowed_tools=["Read"]
)

async def read_file():
    prompt = "README.md ファイルを読んで、その内容を要約してください"

    async for message in query(prompt=prompt, options=options):
        print(message)

asyncio.run(read_file())
```

### 2. Read ツールのパラメータ

| パラメータ | 型 | 説明 | デフォルト |
|-----------|-----|------|-----------|
| `file_path` | string | 読み取るファイルのパス | 必須 |
| `offset` | number | 開始行番号 | 0 |
| `limit` | number | 読み取る行数 | 2000 |

### 3. 大きなファイルの読み取り

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    allowed_tools=["Read"],
    system_prompt="""大きなファイルを読む場合は、offset と limit を使って分割して読んでください。
例: まず最初の500行を読み、必要に応じて続きを読む"""
)

async def read_large_file():
    prompt = """data.csv ファイルの構造を分析してください。
最初の100行を読んで、カラムの意味を推測してください。"""

    async for message in query(prompt=prompt, options=options):
        print(message)
```

<div style="background-color: #f0f8ff; border: 1px solid #cce5ff; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #0d6efd; line-height: 1;">&#x24D8;</span>
    <span style="font-weight: bold; color: #0d6efd; font-size: 15px;">Note</span>
  </div>
  <div style="color: #454545; line-height: 1.6;">
    Read ツールはバイナリファイル（画像、PDF など）にも対応しています。Claude はマルチモーダルなので、画像の内容も理解できます。
  </div>
</div>

---

## 手順2: Write ツール

### 1. 基本的な使い方

Write ツールは新しいファイルを作成するか、既存ファイルを上書きします。

**コード:**

```python
import asyncio
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    allowed_tools=["Write"],
    permission_mode="acceptEdits"
)

async def create_file():
    prompt = """以下の内容で hello.py を作成してください：
- コマンドライン引数で名前を受け取る
- 'Hello, {名前}!' と出力
- 引数がない場合は 'Hello, World!' と出力"""

    async for message in query(prompt=prompt, options=options):
        print(message)

asyncio.run(create_file())
```

### 2. Write ツールのパラメータ

| パラメータ | 型 | 説明 |
|-----------|-----|------|
| `file_path` | string | 作成/上書きするファイルのパス |
| `content` | string | ファイルに書き込む内容 |

### 3. 複数ファイルの作成

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    allowed_tools=["Write"],
    permission_mode="acceptEdits"
)

async def create_project_structure():
    prompt = """以下の構造で Python プロジェクトを作成してください：

myproject/
├── src/
│   ├── __init__.py
│   └── main.py (Hello World プログラム)
├── tests/
│   ├── __init__.py
│   └── test_main.py (簡単なテスト)
└── pyproject.toml (基本的な設定)
"""

    async for message in query(prompt=prompt, options=options):
        print(message)
```

<div style="background-color: #fff3cd; border: 1px solid #ffc107; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #856404; line-height: 1;">&#x26A0;</span>
    <span style="font-weight: bold; color: #856404; font-size: 15px;">注意</span>
  </div>
  <div style="color: #454545; line-height: 1.6;">
    Write ツールは既存ファイルを警告なしに上書きします。重要なファイルを保護するには、permission_mode を "default" にするか、Hooks でチェックを追加してください。
  </div>
</div>

---

## 手順3: Edit ツール

### 1. 基本的な使い方

Edit ツールはファイルの特定部分を編集します。

**コード:**

```python
import asyncio
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    allowed_tools=["Read", "Edit"],
    permission_mode="acceptEdits"
)

async def edit_file():
    prompt = """main.py を編集して、以下の変更を加えてください：
1. 型ヒントを追加
2. docstring を追加
3. エラーハンドリングを追加"""

    async for message in query(prompt=prompt, options=options):
        print(message)

asyncio.run(edit_file())
```

### 2. Edit ツールのパラメータ

| パラメータ | 型 | 説明 |
|-----------|-----|------|
| `file_path` | string | 編集するファイルのパス |
| `old_string` | string | 置換対象の文字列 |
| `new_string` | string | 置換後の文字列 |
| `replace_all` | boolean | 全出現を置換するか（デフォルト: false） |

### 3. Edit の動作原理

```
元のファイル:
┌──────────────────────┐
│ def hello():         │
│     print("Hello")   │
│                      │
│ def goodbye():       │
│     print("Bye")     │
└──────────────────────┘

Edit 操作:
old_string: 'print("Hello")'
new_string: 'print("Hello, World!")'

結果:
┌──────────────────────┐
│ def hello():         │
│     print("Hello, World!")│
│                      │
│ def goodbye():       │
│     print("Bye")     │
└──────────────────────┘
```

### 4. 複数箇所の編集

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    allowed_tools=["Read", "Edit"],
    permission_mode="acceptEdits",
    system_prompt="""ファイルを編集する際のルール：
1. まず Read で現在の内容を確認
2. 変更箇所ごとに個別の Edit を実行
3. 大きな変更は小さな Edit に分割
4. 一括置換は replace_all: true を使用"""
)

async def refactor_code():
    prompt = """utils.py をリファクタリングしてください：
1. 関数名を snake_case に統一
2. 未使用のインポートを削除
3. docstring を追加"""

    async for message in query(prompt=prompt, options=options):
        print(message)
```

---

## 手順4: ツールの組み合わせ

### 1. Read → Edit パターン

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    allowed_tools=["Read", "Edit"],
    permission_mode="acceptEdits"
)

async def improve_code():
    prompt = """config.py を改善してください：
1. まずファイルを読んで現状を把握
2. 型ヒントを追加
3. 環境変数からの読み込みを追加
4. バリデーションを追加"""

    async for message in query(prompt=prompt, options=options):
        print(message)
```

### 2. Read → Write パターン（完全書き換え）

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    allowed_tools=["Read", "Write"],
    permission_mode="acceptEdits"
)

async def rewrite_file():
    prompt = """legacy_code.py を現代的な Python に書き換えてください：
1. 現在のコードを読む
2. 同じ機能を持つ新しいコードを Write で作成
3. asyncio を使用
4. 型ヒントを完備"""

    async for message in query(prompt=prompt, options=options):
        print(message)
```

### 3. Glob → Read → Edit パターン

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    allowed_tools=["Glob", "Read", "Edit"],
    permission_mode="acceptEdits"
)

async def batch_update():
    prompt = """src/ 内の全 .py ファイルに以下の変更を適用：
1. ファイルの先頭に copyright ヘッダーを追加
2. 欠けている __all__ を追加"""

    async for message in query(prompt=prompt, options=options):
        print(message)
```

---

## 手順5: エラーハンドリング

### 1. ファイルが存在しない場合

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    allowed_tools=["Read", "Write"],
    system_prompt="""ファイル操作時のエラーハンドリング：
- ファイルが存在しない場合は、作成するか確認
- 権限エラーの場合は、代替手段を提案
- パースエラーの場合は、問題箇所を特定"""
)

async def safe_file_operation():
    prompt = "config.yaml を読んで、存在しなければ作成してください"

    async for message in query(prompt=prompt, options=options):
        print(message)
```

### 2. Edit の競合

<div style="background-color: #f0f8ff; border: 1px solid #cce5ff; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #0d6efd; line-height: 1;">&#x24D8;</span>
    <span style="font-weight: bold; color: #0d6efd; font-size: 15px;">Note</span>
  </div>
  <div style="color: #454545; line-height: 1.6;">
    Edit ツールの <code>old_string</code> が見つからない場合、Claude は自動的に Read で再確認し、正しい文字列で再試行します。
  </div>
</div>

---

## 手順6: ベストプラクティス

### 1. 安全なファイル操作

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions

# 推奨: 読み取り優先、必要時のみ書き込み
safe_options = ClaudeAgentOptions(
    allowed_tools=["Read", "Edit", "Glob", "Grep"],  # Write は除外
    permission_mode="default",  # 確認あり
    system_prompt="""ファイル操作の原則：
1. 変更前に必ずバックアップの存在を確認
2. 大きな変更は段階的に
3. 各変更後にテストを推奨"""
)
```

### 2. ファイル変更の追跡

**コード:**

```python
import asyncio
from claude_agent_sdk import (
    ClaudeAgentOptions,
    query,
    AssistantMessage,
    ToolUseBlock
)

async def track_file_changes(prompt: str):
    """ファイル変更を追跡"""

    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Write", "Edit", "Glob"],
        permission_mode="acceptEdits"
    )

    changes = []

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ToolUseBlock):
                    if block.name in ["Write", "Edit"]:
                        changes.append({
                            "tool": block.name,
                            "file": block.input.get("file_path"),
                            "action": "created" if block.name == "Write" else "modified"
                        })

    print("\n=== ファイル変更サマリー ===")
    for change in changes:
        print(f"  [{change['action']}] {change['file']}")

    return changes

asyncio.run(track_file_changes("プロジェクトを初期化して"))
```

<div style="background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #155724; line-height: 1;">&#x2714;</span>
    <span style="font-weight: bold; color: #155724; font-size: 15px;">ポイント</span>
  </div>
  <div style="color: #155724; line-height: 1.6;">
    ファイル変更を追跡することで、何が変更されたかを明確に把握でき、問題発生時のロールバックが容易になります。
  </div>
</div>

---

## 演習問題

### 演習1: ファイルバックアップ

Edit/Write 前に自動でバックアップを作成するラッパー関数を作成してください。

### 演習2: 差分表示

Edit 前後の差分を表示する機能を実装してください。

### 演習3: ドライラン

実際には書き込まず、変更内容のプレビューのみを表示するモードを実装してください。

---

## 次のステップ

ファイル操作ツールを理解しました。次は [Bash ツール](03_bash_tool.md) で、シェルコマンドの実行について学びましょう。
