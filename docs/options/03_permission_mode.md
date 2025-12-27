# permission_mode 設定

## 概要

このセクションでは、`permission_mode` オプションを使って Claude のツール実行権限を制御する方法を学習します。

権限モードを適切に設定することで、セキュリティと利便性のバランスを取ることができます。

**サンプルスクリプト:**

このドキュメントの例は、以下のスクリプトで実際に試すことができます：

```bash
src/02_options/03_permission_mode/
├── 01_basic.py          # 手順1-2: 基本概念とdefaultモード
├── 02_accept_edits.py   # 手順3: acceptEditsモード
├── 03_plan_mode.py      # 手順4: planモード（ドライラン）
├── 04_bypass.py         # 手順5: bypassPermissionsモード
└── 05_escalation.py     # 手順6: 段階的エスカレーション
```

```bash
# 基本的な使い方 (手順1-2)
python src/02_options/03_permission_mode/01_basic.py -l    # モード一覧
python src/02_options/03_permission_mode/01_basic.py -h    # ヘルプ
python src/02_options/03_permission_mode/01_basic.py -m default -p "ファイル一覧を表示"

# acceptEdits モード (手順3)
python src/02_options/03_permission_mode/02_accept_edits.py -l
python src/02_options/03_permission_mode/02_accept_edits.py -t refactor -f src/main.py
python src/02_options/03_permission_mode/02_accept_edits.py -w dev

# plan モード (手順4)
python src/02_options/03_permission_mode/03_plan_mode.py -p "テストを実行して"
python src/02_options/03_permission_mode/03_plan_mode.py --review -p "README.mdを更新"
python src/02_options/03_permission_mode/03_plan_mode.py --compare -p "src/を分析"

# bypassPermissions モード (手順5)
python src/02_options/03_permission_mode/04_bypass.py --safe -p "テンプレートを作成"
python src/02_options/03_permission_mode/04_bypass.py --ci -p "テストを実行"

# 段階的エスカレーション (手順6)
python src/02_options/03_permission_mode/05_escalation.py -l
python src/02_options/03_permission_mode/05_escalation.py -p "README.mdを更新"
python src/02_options/03_permission_mode/05_escalation.py --auto-escalate -p "変更を実行"
```

---

## 手順1: 権限モードの種類

### 1. 利用可能なモード

| モード | 説明 | ユースケース |
|-------|------|-------------|
| `default` | ツール実行時に確認を求める | 対話的な作業 |
| `acceptEdits` | ファイル編集を自動承認 | 開発作業 |
| `plan` | プランニングのみ、実行なし | ドライラン |
| `bypassPermissions` | 全操作を自動承認 | CI/CD 自動化 |

### 2. 安全性の比較

```
安全性: 高 ◄─────────────────────────► 低
        plan > default > acceptEdits > bypassPermissions
```

---

## 手順2: default モード

### 1. 基本的な動作

`default` モードでは、Claude がツールを使用する際に確認を求めます。

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    permission_mode="default",
    allowed_tools=["Read", "Write", "Bash"]
)

async def interactive_session():
    prompt = "hello.py を作成して実行してください"

    async for message in query(prompt=prompt, options=options):
        print(message)
```

### 2. canUseTool コールバック

`default` モードでは、`canUseTool` コールバックでカスタム承認ロジックを実装できます。

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient

async def custom_approval(tool_name: str, tool_input: dict) -> bool:
    """カスタム承認ロジック"""

    # Read は常に許可
    if tool_name == "Read":
        return True

    # Bash は特定のコマンドのみ許可
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        allowed_commands = ["ls", "cat", "grep", "python"]
        first_word = command.split()[0] if command.split() else ""
        return first_word in allowed_commands

    # その他は確認
    print(f"\n[確認] {tool_name} を実行しますか？")
    print(f"入力: {tool_input}")
    response = input("許可する (y/n): ")
    return response.lower() == "y"

options = ClaudeAgentOptions(
    permission_mode="default",
    allowed_tools=["Read", "Write", "Bash"]
)

# ClaudeSDKClient で canUseTool を設定
# （実際の実装は SDK バージョンにより異なる場合があります）
```

---

## 手順3: acceptEdits モード

### 1. 基本的な動作

`acceptEdits` モードでは、ファイルの作成・編集を自動承認します。

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    permission_mode="acceptEdits",
    allowed_tools=["Read", "Write", "Edit", "Glob"]
)

async def auto_edit_session():
    prompt = """
    以下のタスクを実行してください：
    1. src/main.py を読む
    2. docstring を追加
    3. ファイルを保存
    """

    async for message in query(prompt=prompt, options=options):
        print(message)
```

<div style="background-color: #f0f8ff; border: 1px solid #cce5ff; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #0d6efd; line-height: 1;">&#x24D8;</span>
    <span style="font-weight: bold; color: #0d6efd; font-size: 15px;">Note</span>
  </div>
  <div style="color: #454545; line-height: 1.6;">
    <code>acceptEdits</code> は Read, Write, Edit ツールを自動承認しますが、Bash などの他のツールは引き続き確認が必要です。
  </div>
</div>

### 2. 開発ワークフローでの使用

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

# 開発用の設定
dev_options = ClaudeAgentOptions(
    permission_mode="acceptEdits",
    allowed_tools=["Read", "Write", "Edit", "Glob", "Grep"],
    cwd="/path/to/project",
    system_prompt="あなたは経験豊富な Python 開発者です。"
)

async def refactor_code():
    prompt = """
    utils.py の calculate_total 関数をリファクタリングしてください：
    - 型ヒントを追加
    - docstring を追加
    - エッジケースの処理を追加
    """

    async for message in query(prompt=prompt, options=dev_options):
        print(message)
```

---

## 手順4: plan モード

### 1. 基本的な動作

`plan` モードでは、Claude は実行計画を立てますが、実際のツール実行は行いません。

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    permission_mode="plan",
    allowed_tools=["Read", "Write", "Edit", "Bash"]
)

async def dry_run():
    prompt = """
    以下のタスクの実行計画を立ててください：
    1. テストを実行
    2. 失敗したテストを修正
    3. ドキュメントを更新
    """

    async for message in query(prompt=prompt, options=options):
        print(message)
```

<details>
<summary><strong>実行結果を見る</strong></summary>

```
## 実行計画

### ステップ 1: テストの実行
- ツール: Bash
- コマンド: `pytest tests/ -v`
- 目的: 現在のテスト状況を確認

### ステップ 2: テスト結果の分析
- ツール: Read
- ファイル: テスト出力
- 目的: 失敗したテストを特定

### ステップ 3: コード修正
- ツール: Edit
- ファイル: 特定されたソースファイル
- 目的: バグを修正

### ステップ 4: ドキュメント更新
- ツール: Write/Edit
- ファイル: README.md, docs/
- 目的: 変更内容を文書化

---
注意: plan モードのため、上記は実行されません。
```

</details>

### 2. 実行前レビュー

**コード:**

```python
import asyncio
from claude_agent_sdk import ClaudeAgentOptions, query, AssistantMessage, TextBlock

async def review_before_execute(prompt: str):
    """まず計画を確認し、承認後に実行"""

    # Step 1: プランニング
    plan_options = ClaudeAgentOptions(
        permission_mode="plan",
        allowed_tools=["Read", "Write", "Edit", "Bash"]
    )

    print("=== 実行計画 ===")
    async for message in query(prompt=prompt, options=plan_options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)

    # Step 2: 確認
    print("\n" + "="*50)
    approval = input("この計画を実行しますか？ (y/n): ")

    if approval.lower() != "y":
        print("キャンセルしました")
        return

    # Step 3: 実行
    exec_options = ClaudeAgentOptions(
        permission_mode="acceptEdits",
        allowed_tools=["Read", "Write", "Edit", "Bash"]
    )

    print("\n=== 実行中 ===")
    async for message in query(prompt=prompt, options=exec_options):
        print(message)

asyncio.run(review_before_execute("README.md を更新してください"))
```

---

## 手順5: bypassPermissions モード

### 1. 基本的な動作

`bypassPermissions` モードでは、全ての操作が自動承認されます。

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

# 危険: 本番環境では使用しないでください
options = ClaudeAgentOptions(
    permission_mode="bypassPermissions",
    allowed_tools=["Read", "Write", "Edit", "Bash"]
)

async def automated_task():
    async for message in query(prompt="タスクを実行", options=options):
        print(message)
```

<div style="background-color: #fff3cd; border: 1px solid #ffc107; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #856404; line-height: 1;">&#x26A0;</span>
    <span style="font-weight: bold; color: #856404; font-size: 15px;">警告</span>
  </div>
  <div style="color: #454545; line-height: 1.6;">
    <code>bypassPermissions</code> は全ての確認をスキップします。以下の条件を満たす場合のみ使用してください：
    <ul style="margin-top: 8px; margin-bottom: 0;">
      <li>隔離された環境（コンテナ、サンドボックス）</li>
      <li>信頼できるプロンプトのみを使用</li>
      <li>allowed_tools を厳格に制限</li>
    </ul>
  </div>
</div>

### 2. 安全な自動化パターン

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query
import tempfile
import os

async def safe_automation(prompt: str):
    """一時ディレクトリで安全に自動実行"""

    with tempfile.TemporaryDirectory() as tmp_dir:
        # 一時ディレクトリに制限
        options = ClaudeAgentOptions(
            permission_mode="bypassPermissions",
            cwd=tmp_dir,
            # Bash を除外してファイル操作のみ許可
            allowed_tools=["Read", "Write", "Edit", "Glob"]
        )

        print(f"作業ディレクトリ: {tmp_dir}")

        async for message in query(prompt=prompt, options=options):
            print(message)

        # 結果を確認
        print("\n作成されたファイル:")
        for f in os.listdir(tmp_dir):
            print(f"  - {f}")
```

### 3. CI/CD での使用

**コード:**

```python
import os
from claude_agent_sdk import ClaudeAgentOptions, query

def get_ci_options() -> ClaudeAgentOptions:
    """CI 環境用のオプションを取得"""

    # CI 環境でのみ bypassPermissions を使用
    is_ci = os.getenv("CI", "false").lower() == "true"

    return ClaudeAgentOptions(
        permission_mode="bypassPermissions" if is_ci else "default",
        allowed_tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep"],
        max_turns=30
    )

async def ci_task():
    options = get_ci_options()
    print(f"権限モード: {options.permission_mode}")

    async for message in query(
        prompt="テストを実行し、失敗があれば修正してください",
        options=options
    ):
        print(message)
```

---

## 手順6: モードの組み合わせ戦略

### 1. 段階的エスカレーション

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query, ResultMessage

class PermissionEscalator:
    """必要に応じて権限をエスカレート"""

    MODES = ["plan", "default", "acceptEdits", "bypassPermissions"]

    def __init__(self, initial_mode: str = "plan"):
        self.current_index = self.MODES.index(initial_mode)

    @property
    def current_mode(self) -> str:
        return self.MODES[self.current_index]

    def escalate(self) -> bool:
        """次のモードにエスカレート"""
        if self.current_index < len(self.MODES) - 1:
            self.current_index += 1
            return True
        return False

    def get_options(self) -> ClaudeAgentOptions:
        return ClaudeAgentOptions(
            permission_mode=self.current_mode,
            allowed_tools=["Read", "Write", "Edit", "Glob"]
        )

async def escalating_execution(prompt: str):
    escalator = PermissionEscalator("plan")

    while True:
        print(f"\n=== モード: {escalator.current_mode} ===")
        options = escalator.get_options()

        async for message in query(prompt=prompt, options=options):
            print(message)

        if escalator.current_mode == "plan":
            proceed = input("実行を続けますか？ (y/n): ")
            if proceed.lower() == "y":
                escalator.escalate()
            else:
                break
        else:
            break
```

<div style="background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #155724; line-height: 1;">&#x2714;</span>
    <span style="font-weight: bold; color: #155724; font-size: 15px;">ポイント</span>
  </div>
  <div style="color: #155724; line-height: 1.6;">
    複雑なタスクでは、まず <code>plan</code> モードで計画を確認し、問題なければ <code>acceptEdits</code> で実行する段階的アプローチが安全です。
  </div>
</div>

---

## 演習問題

### 演習1: 承認ワークフロー

Slack や Email で承認を求め、承認後に実行するワークフローを作成してください。

### 演習2: 権限の時限設定

特定の時間帯のみ `acceptEdits` を許可し、それ以外は `default` を使用するロジックを実装してください。

### 演習3: 監査ログ付き自動化

`bypassPermissions` 使用時に全操作を詳細に記録する監査システムを作成してください。

---

## 次のステップ

権限モードを理解しました。次は [max_turns](04_max_turns.md) で、会話ターン数の制限について学びましょう。
