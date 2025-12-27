# Bash ツール

## 概要

このセクションでは、Bash ツールを使ってシェルコマンドを実行する方法を学習します。

Bash ツールは最も強力なツールですが、セキュリティリスクも高いため、慎重に使用する必要があります。

---

## 手順1: Bash ツールの基本

### 1. 基本的な使い方

**コード:**

```python
import asyncio
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    allowed_tools=["Bash"],
    permission_mode="default"  # 確認を求める
)

async def run_command():
    prompt = "現在のディレクトリ構造を表示してください"

    async for message in query(prompt=prompt, options=options):
        print(message)

asyncio.run(run_command())
```

### 2. Bash ツールのパラメータ

| パラメータ | 型 | 説明 | デフォルト |
|-----------|-----|------|-----------|
| `command` | string | 実行するコマンド | 必須 |
| `timeout` | number | タイムアウト (ms) | 120000 |
| `description` | string | コマンドの説明 | なし |

### 3. 一般的なコマンド例

```python
# ディレクトリ操作
{"command": "ls -la"}
{"command": "pwd"}
{"command": "mkdir -p src/utils"}

# ファイル操作
{"command": "cat package.json"}
{"command": "head -n 20 README.md"}
{"command": "wc -l src/*.py"}

# Git 操作
{"command": "git status"}
{"command": "git log --oneline -10"}
{"command": "git diff HEAD~1"}

# パッケージ管理
{"command": "pip list"}
{"command": "npm ls --depth=0"}

# テスト実行
{"command": "pytest tests/ -v"}
{"command": "npm test"}
```

---

## 手順2: セキュリティ対策

### 1. 危険なコマンドのブロック

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, HookMatcher

# 危険なパターンのリスト
DANGEROUS_PATTERNS = [
    "rm -rf /",
    "rm -rf ~",
    "sudo",
    "chmod 777",
    "> /dev/sda",
    "mkfs",
    "dd if=",
    ":(){ :|:& };:",  # fork bomb
    "curl | bash",
    "wget | sh",
]

async def block_dangerous_commands(input_data, tool_use_id, context):
    """危険なコマンドをブロック"""

    if input_data["tool_name"] != "Bash":
        return {}

    command = input_data["tool_input"].get("command", "")

    for pattern in DANGEROUS_PATTERNS:
        if pattern in command:
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": f"危険なパターンを検出: {pattern}"
                }
            }

    return {}

options = ClaudeAgentOptions(
    allowed_tools=["Bash"],
    hooks={
        "PreToolUse": [
            HookMatcher(matcher="Bash", hooks=[block_dangerous_commands])
        ]
    }
)
```

<div style="background-color: #fff3cd; border: 1px solid #ffc107; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #856404; line-height: 1;">&#x26A0;</span>
    <span style="font-weight: bold; color: #856404; font-size: 15px;">警告</span>
  </div>
  <div style="color: #454545; line-height: 1.6;">
    Bash ツールは任意のシェルコマンドを実行できます。本番環境では必ず以下の対策を実施してください：
    <ul style="margin-top: 8px; margin-bottom: 0;">
      <li>ホワイトリストによるコマンド制限</li>
      <li>サンドボックス/コンテナでの実行</li>
      <li>最小権限ユーザーでの実行</li>
    </ul>
  </div>
</div>

### 2. コマンドホワイトリスト

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, HookMatcher

# 許可するコマンドのホワイトリスト
ALLOWED_COMMANDS = {
    "ls", "cat", "head", "tail", "grep", "find",
    "pwd", "echo", "wc",
    "git", "npm", "pip", "python", "pytest",
    "make", "cargo", "go"
}

async def whitelist_commands(input_data, tool_use_id, context):
    """ホワイトリストにないコマンドをブロック"""

    if input_data["tool_name"] != "Bash":
        return {}

    command = input_data["tool_input"].get("command", "")
    first_word = command.split()[0] if command.split() else ""

    # パイプやリダイレクトを考慮
    base_command = first_word.split("/")[-1]

    if base_command not in ALLOWED_COMMANDS:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": f"コマンド '{base_command}' は許可されていません"
            }
        }

    return {}

secure_options = ClaudeAgentOptions(
    allowed_tools=["Bash"],
    hooks={
        "PreToolUse": [
            HookMatcher(matcher="Bash", hooks=[whitelist_commands])
        ]
    }
)
```

---

## 手順3: 実用的なユースケース

### 1. ビルドとテスト

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    allowed_tools=["Read", "Bash", "Glob"],
    permission_mode="acceptEdits",
    system_prompt="テスト失敗時は原因を分析し、修正を提案してください"
)

async def build_and_test():
    prompt = """以下の手順を実行してください：
1. 依存関係をインストール (pip install -r requirements.txt)
2. テストを実行 (pytest)
3. 失敗したテストがあれば原因を分析"""

    async for message in query(prompt=prompt, options=options):
        print(message)
```

### 2. Git 操作

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

git_options = ClaudeAgentOptions(
    allowed_tools=["Bash", "Read", "Edit"],
    permission_mode="default",
    system_prompt="""Git 操作の原則：
- force push は禁止
- main/master への直接 commit は避ける
- commit メッセージは具体的に"""
)

async def git_workflow():
    prompt = """以下の Git 操作を実行してください：
1. 現在のブランチとステータスを確認
2. 変更をステージング
3. 適切なコミットメッセージでコミット"""

    async for message in query(prompt=prompt, options=options):
        print(message)
```

### 3. 環境情報の取得

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    allowed_tools=["Bash"],
    max_turns=5
)

async def get_environment_info():
    prompt = """開発環境の情報を収集してください：
- Python バージョン
- インストール済みパッケージ
- Node.js バージョン（あれば）
- Git 設定"""

    async for message in query(prompt=prompt, options=options):
        print(message)
```

---

## 手順4: タイムアウトとエラー処理

### 1. 長時間コマンドの処理

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    allowed_tools=["Bash"],
    system_prompt="""長時間かかるコマンドの場合：
- timeout パラメータを適切に設定
- 進捗が確認できるオプションを使用（例: -v）
- バックグラウンド実行が必要な場合は報告"""
)

async def long_running_command():
    prompt = "大きなプロジェクトのテストを実行してください（タイムアウトを5分に設定）"

    async for message in query(prompt=prompt, options=options):
        print(message)
```

### 2. コマンド失敗時の処理

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    allowed_tools=["Bash", "Read", "Edit"],
    system_prompt="""コマンドが失敗した場合：
1. エラーメッセージを分析
2. 原因を特定
3. 解決策を提案または実行
4. 依存関係の問題なら自動で解決を試みる"""
)

async def handle_errors():
    prompt = "pytest を実行して、失敗があれば修正してください"

    async for message in query(prompt=prompt, options=options):
        print(message)
```

---

## 手順5: 出力の処理

### 1. コマンド出力の解析

**コード:**

```python
import asyncio
from claude_agent_sdk import (
    ClaudeAgentOptions,
    query,
    AssistantMessage,
    ToolUseBlock
)

async def analyze_command_output():
    options = ClaudeAgentOptions(
        allowed_tools=["Bash"],
        system_prompt="コマンドの出力を解析し、重要な情報を抽出してください"
    )

    command_results = []

    async for message in query(
        prompt="git log --oneline -20 を実行し、最近のコミット傾向を分析して",
        options=options
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ToolUseBlock):
                    if block.name == "Bash":
                        command_results.append(block.input.get("command"))

    print(f"実行されたコマンド: {command_results}")

asyncio.run(analyze_command_output())
```

### 2. 出力のフィルタリング

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, HookMatcher

async def filter_sensitive_output(input_data, tool_use_id, context):
    """機密情報を含む出力をフィルタリング"""

    if input_data.get("hookEventName") != "PostToolUse":
        return {}

    if input_data.get("tool_name") != "Bash":
        return {}

    result = input_data.get("tool_result", {})
    stdout = result.get("stdout", "")

    # 機密パターンを検出
    sensitive_patterns = ["password", "secret", "api_key", "token"]

    for pattern in sensitive_patterns:
        if pattern.lower() in stdout.lower():
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": "警告: 出力に機密情報が含まれている可能性があります"
                }
            }

    return {}
```

---

## 手順6: ベストプラクティス

### 1. 安全な Bash 使用ガイドライン

<div style="background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #155724; line-height: 1;">&#x2714;</span>
    <span style="font-weight: bold; color: #155724; font-size: 15px;">推奨プラクティス</span>
  </div>
  <div style="color: #155724; line-height: 1.6;">
    <ul style="margin: 0; padding-left: 20px;">
      <li>permission_mode="default" で確認を求める</li>
      <li>ホワイトリストでコマンドを制限</li>
      <li>適切なタイムアウトを設定</li>
      <li>サンドボックス環境での実行を検討</li>
      <li>出力のログを記録</li>
    </ul>
  </div>
</div>

### 2. CI/CD での使用

**コード:**

```python
import os
from claude_agent_sdk import ClaudeAgentOptions

def get_ci_bash_options() -> ClaudeAgentOptions:
    """CI 環境用の Bash オプション"""

    is_ci = os.getenv("CI", "false").lower() == "true"

    if is_ci:
        return ClaudeAgentOptions(
            allowed_tools=["Bash", "Read", "Write", "Edit"],
            permission_mode="bypassPermissions",
            system_prompt="""CI 環境での実行ルール：
- 対話的なコマンドは使用しない
- エラー時は詳細なログを出力
- テスト失敗時は終了コード 1 を返す"""
        )
    else:
        return ClaudeAgentOptions(
            allowed_tools=["Bash", "Read"],
            permission_mode="default"
        )
```

---

## 演習問題

### 演習1: コマンドログ

実行された全ての Bash コマンドとその結果をログファイルに記録するシステムを作成してください。

### 演習2: インタラクティブ確認

危険度に応じて確認レベルを変える（低危険: 自動承認、中危険: 簡易確認、高危険: 詳細確認）システムを実装してください。

### 演習3: コマンド提案

プロンプトから最適なコマンドを提案し、ユーザーが承認するまで実行しないインターフェースを作成してください。

---

## 次のステップ

Bash ツールを理解しました。次は [検索ツール](04_search_tools.md) で、Glob と Grep について学びましょう。
