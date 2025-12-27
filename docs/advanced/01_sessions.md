# セッション管理

## 概要

このセクションでは、セッションを使って会話のコンテキストを維持する方法を学習します。

セッションを使用すると、複数のクエリにわたってコンテキストを保持し、継続的な対話が可能になります。

---

## 手順1: セッションの基本

### 1. ClaudeSDKClient によるセッション管理

**コード:**

```python
import asyncio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

async def session_example():
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Write", "Edit"],
        permission_mode="acceptEdits"
    )

    async with ClaudeSDKClient(options=options) as client:
        # 最初のクエリ
        await client.query("このプロジェクトの構造を分析してください")
        async for message in client.receive_response():
            print(message)

        # 続きのクエリ（コンテキストが維持される）
        await client.query("先ほどの分析に基づいて、改善点を提案してください")
        async for message in client.receive_response():
            print(message)

asyncio.run(session_example())
```

### 2. セッションの利点

| 機能 | 説明 |
|-----|------|
| コンテキスト保持 | 前の会話内容を記憶 |
| 継続的な作業 | 中断した作業を再開可能 |
| 効率的なトークン使用 | 重複説明が不要 |

---

## 手順2: セッション ID の管理

### 1. セッション ID の取得と再利用

**コード:**

```python
import asyncio
from claude_agent_sdk import query, ResultMessage

async def get_session_id():
    """セッション ID を取得"""

    session_id = None

    async for message in query(prompt="Hello!"):
        if isinstance(message, ResultMessage):
            session_id = message.session_id
            print(f"セッション ID: {session_id}")

    return session_id

# セッション ID を使って会話を再開
async def resume_session(session_id: str):
    # 注: 実際の再開方法は SDK バージョンにより異なる場合があります
    print(f"セッション {session_id} を再開")

asyncio.run(get_session_id())
```

### 2. セッションの永続化

**コード:**

```python
import json
from pathlib import Path
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

class SessionManager:
    def __init__(self, storage_dir: str = ".sessions"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)

    def save_session(self, session_id: str, metadata: dict):
        """セッション情報を保存"""
        session_file = self.storage_dir / f"{session_id}.json"
        with open(session_file, "w") as f:
            json.dump({
                "session_id": session_id,
                "metadata": metadata
            }, f)

    def load_session(self, session_id: str) -> dict:
        """セッション情報を読み込み"""
        session_file = self.storage_dir / f"{session_id}.json"
        if session_file.exists():
            with open(session_file) as f:
                return json.load(f)
        return None

    def list_sessions(self) -> list[str]:
        """保存されたセッション一覧"""
        return [f.stem for f in self.storage_dir.glob("*.json")]
```

---

## 手順3: マルチターン会話

### 1. 対話的なセッション

**コード:**

```python
import asyncio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, TextBlock

async def interactive_session():
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Glob", "Grep"]
    )

    async with ClaudeSDKClient(options=options) as client:
        print("対話セッションを開始します（'quit' で終了）")

        while True:
            user_input = input("\nあなた: ")

            if user_input.lower() == "quit":
                break

            await client.query(user_input)

            print("\nClaude: ", end="")
            async for message in client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            print(block.text)

asyncio.run(interactive_session())
```

### 2. ステートフルな作業

**コード:**

```python
import asyncio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

async def stateful_workflow():
    """ステートを維持しながら段階的に作業"""

    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Write", "Edit", "Glob"],
        permission_mode="acceptEdits"
    )

    async with ClaudeSDKClient(options=options) as client:
        # ステップ 1: 分析
        await client.query("src/ ディレクトリのコード構造を分析してください")
        async for message in client.receive_response():
            print(message)

        # ステップ 2: 計画（前の分析結果を参照）
        await client.query("分析結果に基づいて、リファクタリング計画を立ててください")
        async for message in client.receive_response():
            print(message)

        # ステップ 3: 実行（計画を参照）
        await client.query("計画の最初のステップを実行してください")
        async for message in client.receive_response():
            print(message)

asyncio.run(stateful_workflow())
```

<div style="background-color: #f0f8ff; border: 1px solid #cce5ff; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #0d6efd; line-height: 1;">&#x24D8;</span>
    <span style="font-weight: bold; color: #0d6efd; font-size: 15px;">Note</span>
  </div>
  <div style="color: #454545; line-height: 1.6;">
    セッション内では、Claude は前のやり取りを記憶しています。「先ほどの」「その結果を」などの参照が可能です。
  </div>
</div>

---

## 手順4: セッションのフォーク

### 1. セッションの分岐

**コード:**

```python
import asyncio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

async def fork_session():
    """セッションを分岐して異なるアプローチを試す"""

    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Glob"]
    )

    # 共通の開始点
    async with ClaudeSDKClient(options=options) as client:
        await client.query("プロジェクトを分析してください")
        async for message in client.receive_response():
            print("[共通] ", message)

        # ここでセッション ID を保存して分岐点を作成
        # session_id = client.session_id

    # 分岐 A: パフォーマンス最適化
    async with ClaudeSDKClient(options=options) as client_a:
        # 注: 実際のフォーク実装は SDK バージョンにより異なる
        await client_a.query("パフォーマンス改善に焦点を当てて提案してください")
        async for message in client_a.receive_response():
            print("[分岐A] ", message)

    # 分岐 B: コード品質改善
    async with ClaudeSDKClient(options=options) as client_b:
        await client_b.query("コード品質改善に焦点を当てて提案してください")
        async for message in client_b.receive_response():
            print("[分岐B] ", message)
```

---

## 手順5: セッションのベストプラクティス

### 1. コンテキスト管理

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions

# 長いセッション向けの設定
long_session_options = ClaudeAgentOptions(
    system_prompt="""長時間のセッションルール：
- 重要な決定事項は明示的に確認
- 定期的に進捗をサマリー
- 大きなコンテキストは分割して処理""",
    max_turns=50
)

# 短いタスク向けの設定
quick_task_options = ClaudeAgentOptions(
    max_turns=5
)
```

### 2. セッションのクリーンアップ

**コード:**

```python
import asyncio
from contextlib import asynccontextmanager
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, ResultMessage

@asynccontextmanager
async def managed_session(options: ClaudeAgentOptions):
    """クリーンアップを保証するセッション管理"""

    session_info = {
        "session_id": None,
        "total_cost": 0.0,
        "total_turns": 0
    }

    try:
        async with ClaudeSDKClient(options=options) as client:
            yield client, session_info

    finally:
        print(f"\n=== セッション終了 ===")
        print(f"セッション ID: {session_info['session_id']}")
        print(f"総コスト: ${session_info['total_cost']:.4f}")
        print(f"総ターン数: {session_info['total_turns']}")

# 使用例
async def example():
    options = ClaudeAgentOptions(allowed_tools=["Read"])

    async with managed_session(options) as (client, info):
        await client.query("Hello!")
        async for message in client.receive_response():
            if isinstance(message, ResultMessage):
                info["session_id"] = message.session_id
                info["total_cost"] += message.total_cost_usd
                info["total_turns"] += message.num_turns
```

<div style="background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #155724; line-height: 1;">&#x2714;</span>
    <span style="font-weight: bold; color: #155724; font-size: 15px;">ポイント</span>
  </div>
  <div style="color: #155724; line-height: 1.6;">
    セッションを使用する際は、コスト追跡とクリーンアップを忘れずに行いましょう。特に長時間のセッションではコストが積み上がる可能性があります。
  </div>
</div>

---

## 演習問題

### 演習1: セッション履歴

セッション内の全てのやり取りを記録し、後から参照できる履歴システムを作成してください。

### 演習2: セッションレジューム

中断したセッションを再開できる機能を実装してください。

### 演習3: マルチセッション管理

複数のセッションを並行して管理し、切り替えられるインターフェースを作成してください。

---

## 次のステップ

セッション管理を理解しました。次は [サブエージェント](02_subagents.md) で、専門化されたエージェントの作成について学びましょう。
