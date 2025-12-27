# 検索ツール (Glob, Grep)

## 概要

このセクションでは、Glob と Grep ツールを使ってファイルとテキストを検索する方法を学習します。

これらのツールはコードベースの探索と分析に不可欠です。

---

## 手順1: Glob ツール

### 1. 基本的な使い方

Glob ツールはファイルパターンでファイルを検索します。

**コード:**

```python
import asyncio
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    allowed_tools=["Glob"]
)

async def find_files():
    prompt = "src/ ディレクトリ内の全ての Python ファイルを検索してください"

    async for message in query(prompt=prompt, options=options):
        print(message)

asyncio.run(find_files())
```

### 2. Glob パターン構文

| パターン | 説明 | 例 |
|---------|------|-----|
| `*` | 任意の文字列（/以外） | `*.py` → `main.py`, `utils.py` |
| `**` | 任意のディレクトリ階層 | `**/*.py` → 全階層の.pyファイル |
| `?` | 任意の1文字 | `file?.txt` → `file1.txt` |
| `[abc]` | a, b, c のいずれか | `[abc].py` → `a.py`, `b.py` |
| `[!abc]` | a, b, c 以外 | `[!abc].py` → `d.py`, `e.py` |
| `{a,b}` | a または b | `*.{js,ts}` → `.js` と `.ts` |

### 3. 実用的なパターン例

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    allowed_tools=["Glob"],
    system_prompt="""よく使う Glob パターン：
- **/*.py: 全 Python ファイル
- src/**/*.{js,ts}: src 内の JS/TS ファイル
- **/test_*.py: テストファイル
- **/__init__.py: パッケージ初期化ファイル
- !**/node_modules/**: node_modules を除外"""
)

async def search_patterns():
    prompts = [
        "プロジェクト内の全テストファイルを検索",
        "設定ファイル（*.json, *.yaml, *.toml）を検索",
        "README ファイルを全階層から検索"
    ]

    for prompt in prompts:
        print(f"\n--- {prompt} ---")
        async for message in query(prompt=prompt, options=options):
            print(message)
```

---

## 手順2: Grep ツール

### 1. 基本的な使い方

Grep ツールはファイル内のテキストを正規表現で検索します。

**コード:**

```python
import asyncio
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    allowed_tools=["Grep"]
)

async def search_text():
    prompt = "プロジェクト内で 'TODO' コメントを検索してください"

    async for message in query(prompt=prompt, options=options):
        print(message)

asyncio.run(search_text())
```

### 2. Grep ツールのパラメータ

| パラメータ | 型 | 説明 |
|-----------|-----|------|
| `pattern` | string | 検索する正規表現パターン |
| `path` | string | 検索するパス |
| `glob` | string | ファイルフィルタ（例: `*.py`） |
| `output_mode` | string | `content`, `files_with_matches`, `count` |
| `-i` | boolean | 大文字小文字を無視 |
| `-A`, `-B`, `-C` | number | 前後のコンテキスト行数 |

### 3. 出力モードの違い

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

# files_with_matches: マッチしたファイル名のみ
# content: マッチした行の内容
# count: マッチ数

options = ClaudeAgentOptions(
    allowed_tools=["Grep"],
    system_prompt="""Grep 出力モードの使い分け：
- files_with_matches: どのファイルにあるか確認したい時
- content: 具体的な内容を確認したい時
- count: 統計を取りたい時"""
)
```

### 4. 正規表現パターン例

| 目的 | パターン |
|-----|---------|
| 関数定義 | `def\s+\w+\s*\(` |
| クラス定義 | `class\s+\w+` |
| インポート | `^import\s+\|^from\s+` |
| TODO コメント | `#\s*TODO` |
| 型ヒント | `:\s*\w+\s*=` |
| API エンドポイント | `@app\.(get\|post\|put\|delete)` |

---

## 手順3: Glob と Grep の組み合わせ

### 1. ファイル検索 → 内容検索

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    allowed_tools=["Glob", "Grep", "Read"]
)

async def find_and_search():
    prompt = """以下の手順で検索してください：
1. src/ 内の全 .py ファイルを Glob で検索
2. その中から 'async def' を含むファイルを Grep で検索
3. 見つかったファイルの非同期関数を一覧化"""

    async for message in query(prompt=prompt, options=options):
        print(message)
```

### 2. コード分析パイプライン

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    allowed_tools=["Glob", "Grep", "Read"],
    system_prompt="""コード分析の手順：
1. Glob でファイルを特定
2. Grep で関連箇所を検索
3. Read で詳細を確認
4. 分析結果をまとめる"""
)

async def analyze_codebase():
    prompt = """このプロジェクトの API エンドポイントを分析してください：
1. ルーティング定義のあるファイルを検索
2. 各エンドポイントの HTTP メソッドとパスを抽出
3. エンドポイント一覧を作成"""

    async for message in query(prompt=prompt, options=options):
        print(message)
```

---

## 手順4: 高度な検索テクニック

### 1. 除外パターン

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    allowed_tools=["Glob", "Grep"],
    system_prompt="""検索時の除外パターン：
- node_modules/, __pycache__/, .git/ を除外
- *.min.js, *.map などのビルド成果物を除外
- テストファイルを本番コードと分離して検索"""
)

async def search_with_exclusions():
    prompt = "本番コード（テストを除く）内の未使用インポートを検索"

    async for message in query(prompt=prompt, options=options):
        print(message)
```

### 2. 複合検索

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    allowed_tools=["Glob", "Grep"]
)

async def complex_search():
    prompt = """以下の条件で検索してください：
1. src/ 内の .py ファイル
2. 'class' で始まる行を含む
3. かつ 'def __init__' も含む
4. 結果をクラス名でグループ化"""

    async for message in query(prompt=prompt, options=options):
        print(message)
```

### 3. 統計収集

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    allowed_tools=["Glob", "Grep"],
    system_prompt="検索結果は統計的にまとめてください"
)

async def collect_statistics():
    prompt = """プロジェクトの統計を収集してください：
- ファイル数（言語別）
- 総行数
- TODO/FIXME の数
- 関数/クラスの数"""

    async for message in query(prompt=prompt, options=options):
        print(message)
```

---

## 手順5: 検索結果の活用

### 1. 検索結果からのアクション

**コード:**

```python
import asyncio
from claude_agent_sdk import (
    ClaudeAgentOptions,
    query,
    AssistantMessage,
    ToolUseBlock
)

async def search_and_act():
    options = ClaudeAgentOptions(
        allowed_tools=["Glob", "Grep", "Read", "Edit"],
        permission_mode="acceptEdits"
    )

    prompt = """以下の手順を実行してください：
1. 全 .py ファイルで deprecated な関数呼び出しを検索
2. 各ファイルで新しい関数に置換"""

    search_results = []
    edits_made = []

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ToolUseBlock):
                    if block.name == "Grep":
                        search_results.append(block.input)
                    elif block.name == "Edit":
                        edits_made.append(block.input.get("file_path"))

    print(f"検索: {len(search_results)} 回")
    print(f"編集: {len(edits_made)} ファイル")

asyncio.run(search_and_act())
```

### 2. 検索結果のレポート

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    allowed_tools=["Glob", "Grep"],
    system_prompt="""検索結果は以下の形式でレポート：

## 検索結果サマリー
- 検索パターン: [パターン]
- マッチ数: [数]

## ファイル別結果
### [ファイル名]
- 行 [番号]: [内容]
"""
)

async def generate_search_report():
    prompt = "セキュリティリスクのある箇所（eval, exec, shell=True 等）を検索してレポート"

    async for message in query(prompt=prompt, options=options):
        print(message)
```

<div style="background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #155724; line-height: 1;">&#x2714;</span>
    <span style="font-weight: bold; color: #155724; font-size: 15px;">ポイント</span>
  </div>
  <div style="color: #155724; line-height: 1.6;">
    Glob と Grep は読み取り専用のため、安全に使用できます。コードベースの探索には積極的に活用しましょう。
  </div>
</div>

---

## 演習問題

### 演習1: コードベース分析ツール

Glob と Grep を使って、プロジェクトの健全性レポートを生成する関数を作成してください（ファイル数、TODO数、複雑度など）。

### 演習2: 依存関係マップ

import/require 文を検索し、ファイル間の依存関係グラフを生成する機能を実装してください。

### 演習3: デッドコード検出

定義されているが使用されていない関数/クラスを検出するツールを作成してください。

---

## 次のステップ

検索ツールを理解しました。次は [Web ツール](05_web_tools.md) で、インターネット検索と Web ページ取得について学びましょう。
