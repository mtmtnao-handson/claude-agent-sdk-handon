# Task ツール

## 概要

このセクションでは、Task ツールを使ってタスク管理を行う方法を学習します。

Task ツールは複雑なワークフローを整理し、進捗を追跡するのに役立ちます。

---

## 手順1: Task ツールの基本

### 1. 基本的な使い方

Task ツールは TODO リストの管理に使用されます。

**コード:**

```python
import asyncio
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    allowed_tools=["Task", "Read", "Write", "Edit"],
    permission_mode="acceptEdits"
)

async def managed_workflow():
    prompt = """以下のタスクを順番に実行してください：
1. README.md を読んでプロジェクトを理解
2. 改善点をリストアップ
3. README.md を更新

各タスクの進捗を追跡してください。"""

    async for message in query(prompt=prompt, options=options):
        print(message)

asyncio.run(managed_workflow())
```

### 2. タスクの状態

| 状態 | 説明 |
|-----|------|
| `pending` | 未着手 |
| `in_progress` | 実行中 |
| `completed` | 完了 |

---

## 手順2: 複雑なワークフロー管理

### 1. マルチステップタスク

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    allowed_tools=["Task", "Read", "Write", "Edit", "Glob", "Grep", "Bash"],
    permission_mode="acceptEdits",
    system_prompt="""タスク管理のルール：
- 大きなタスクは小さなサブタスクに分割
- 各タスクの開始時に in_progress に更新
- 完了時に completed に更新
- エラー発生時は原因を記録"""
)

async def complex_workflow():
    prompt = """以下のプロジェクトセットアップを実行してください：

1. プロジェクト構造の作成
   - src/ ディレクトリ作成
   - tests/ ディレクトリ作成
   - 設定ファイル作成

2. 基本ファイルの作成
   - main.py
   - __init__.py
   - conftest.py

3. 依存関係の設定
   - pyproject.toml 作成
   - requirements.txt 作成

4. 初期テストの作成
   - test_main.py

5. 動作確認
   - テスト実行

各ステップの進捗を追跡してください。"""

    async for message in query(prompt=prompt, options=options):
        print(message)
```

### 2. 並列タスクの管理

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    allowed_tools=["Task", "Read", "Glob", "Grep"],
    system_prompt="""並列実行可能なタスクは同時に進めてください：
- 独立したファイルの読み取り
- 異なるディレクトリの検索
- 関連のない分析タスク"""
)

async def parallel_tasks():
    prompt = """以下のコード分析タスクを実行してください（可能な限り並列で）：

1. src/ 内のファイル数カウント
2. tests/ 内のテスト数カウント
3. TODO/FIXME コメントの検索
4. 未使用インポートの検出
5. 型ヒントのカバレッジ確認"""

    async for message in query(prompt=prompt, options=options):
        print(message)
```

---

## 手順3: 進捗レポート

### 1. タスク進捗の可視化

**コード:**

```python
import asyncio
from claude_agent_sdk import (
    ClaudeAgentOptions,
    query,
    AssistantMessage,
    ToolUseBlock
)

async def track_progress(prompt: str):
    """タスク進捗を追跡"""

    options = ClaudeAgentOptions(
        allowed_tools=["Task", "Read", "Write", "Edit"],
        permission_mode="acceptEdits"
    )

    task_updates = []

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ToolUseBlock):
                    if block.name == "Task":
                        todos = block.input.get("todos", [])
                        task_updates.append(todos)

                        # 進捗表示
                        completed = sum(1 for t in todos if t.get("status") == "completed")
                        total = len(todos)
                        print(f"進捗: {completed}/{total} タスク完了")

    return task_updates

asyncio.run(track_progress("プロジェクトを初期化して"))
```

### 2. 詳細レポートの生成

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    allowed_tools=["Task", "Read", "Write"],
    permission_mode="acceptEdits",
    system_prompt="""タスク完了後、以下の形式でレポートを生成：

## 実行レポート

### 完了タスク
- [x] タスク1
- [x] タスク2

### 未完了タスク（あれば）
- [ ] タスク3（理由: ...）

### サマリー
- 総タスク数: N
- 完了: M
- 所要時間（推定）: X 分
"""
)

async def generate_report():
    prompt = "コードレビューを実行し、完了後にレポートを作成してください"

    async for message in query(prompt=prompt, options=options):
        print(message)
```

---

## 手順4: エラー回復とリトライ

### 1. タスク失敗時の処理

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    allowed_tools=["Task", "Read", "Write", "Edit", "Bash"],
    permission_mode="acceptEdits",
    system_prompt="""タスク失敗時の処理：
1. エラーの原因を分析
2. 可能なら自動修復を試みる
3. 修復不可能な場合は次のタスクに進む
4. 最後にスキップしたタスクをレポート"""
)

async def resilient_workflow():
    prompt = """以下のタスクを実行してください（エラーがあっても続行）：
1. 依存関係のインストール
2. リンターの実行
3. テストの実行
4. ビルドの実行

失敗したタスクは記録して、可能なら修復してください。"""

    async for message in query(prompt=prompt, options=options):
        print(message)
```

### 2. チェックポイントとリカバリ

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    allowed_tools=["Task", "Read", "Write"],
    permission_mode="acceptEdits",
    system_prompt="""長時間タスクのルール：
- 重要なステップごとにチェックポイントを作成
- 進捗を .checkpoint ファイルに保存
- 再開時はチェックポイントから続行"""
)

async def checkpointed_workflow():
    prompt = """大規模なコードリファクタリングを実行してください：
1. 各ファイルの処理前にチェックポイントを作成
2. エラー時はチェックポイントから再開可能に
3. 完了時にチェックポイントをクリーンアップ"""

    async for message in query(prompt=prompt, options=options):
        print(message)
```

---

## 手順5: タスクテンプレート

### 1. 再利用可能なワークフロー

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions

# コードレビューワークフロー
CODE_REVIEW_WORKFLOW = """
以下のコードレビュータスクを実行してください：

1. ファイル構造の確認
   - src/ ディレクトリの構造を把握
   - テストファイルの存在確認

2. コード品質チェック
   - 型ヒントの確認
   - docstring の存在確認
   - 命名規則の確認

3. セキュリティチェック
   - 機密情報のハードコード確認
   - 入力バリデーションの確認
   - SQL インジェクション対策確認

4. テストカバレッジ確認
   - 主要な関数のテスト有無
   - エッジケースのテスト

5. レポート作成
   - 発見した問題のリスト
   - 改善提案
"""

# プロジェクト初期化ワークフロー
PROJECT_INIT_WORKFLOW = """
以下のプロジェクト初期化タスクを実行してください：

1. ディレクトリ構造作成
2. 設定ファイル作成（pyproject.toml）
3. Git 初期化
4. .gitignore 作成
5. README.md 作成
6. 初期テスト作成
7. 動作確認
"""

def get_workflow_options(workflow: str) -> ClaudeAgentOptions:
    return ClaudeAgentOptions(
        allowed_tools=["Task", "Read", "Write", "Edit", "Glob", "Grep", "Bash"],
        permission_mode="acceptEdits",
        system_prompt=f"以下のワークフローを実行してください：\n\n{workflow}"
    )
```

<div style="background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #155724; line-height: 1;">&#x2714;</span>
    <span style="font-weight: bold; color: #155724; font-size: 15px;">ポイント</span>
  </div>
  <div style="color: #155724; line-height: 1.6;">
    よく使うワークフローはテンプレート化しておくと、一貫した品質で繰り返し実行できます。
  </div>
</div>

---

## 手順6: Task ツールとサブエージェントの連携

### 1. タスクごとに専門エージェントを使用

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, AgentDefinition, query

# 専門エージェントの定義
code_reviewer = AgentDefinition(
    description="コードレビューの専門家",
    prompt="コード品質とセキュリティを重視してレビューしてください",
    tools=["Read", "Glob", "Grep"]
)

test_writer = AgentDefinition(
    description="テスト作成の専門家",
    prompt="網羅的なテストケースを作成してください",
    tools=["Read", "Write", "Edit"]
)

options = ClaudeAgentOptions(
    allowed_tools=["Task"],
    agents={
        "reviewer": code_reviewer,
        "tester": test_writer
    },
    system_prompt="""タスクに応じて適切なエージェントを使用：
- コードレビュー → reviewer エージェント
- テスト作成 → tester エージェント"""
)
```

---

## 演習問題

### 演習1: カスタムワークフローエンジン

YAML 形式でワークフローを定義し、自動実行するエンジンを作成してください。

### 演習2: 進捗ダッシュボード

リアルタイムでタスク進捗を表示する TUI（テキストユーザーインターフェース）を作成してください。

### 演習3: タスク依存関係

タスク間の依存関係を定義し、依存関係に基づいて実行順序を最適化するシステムを作成してください。

---

## 次のステップ

ビルトインツールの学習が完了しました。次は [セッション](../advanced/01_sessions.md) で、会話のコンテキスト管理について学びましょう。
