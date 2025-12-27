# フック (Hooks)

## 概要

このセクションでは、Hooks を使ってエージェントの動作をカスタマイズする方法を学習します。

Hooks を使うと、ツール実行の前後で独自の処理を挿入できます。

---

## 手順1: Hooks の基本

### 1. 利用可能なフックイベント

| イベント | タイミング | 用途 |
|---------|----------|------|
| `PreToolUse` | ツール実行前 | 権限チェック、ログ、ブロック |
| `PostToolUse` | ツール実行後 | 結果処理、ログ、追加コンテキスト |
| `UserPromptSubmit` | プロンプト送信時 | 入力検証、前処理 |
| `Stop` | 処理終了時 | クリーンアップ、レポート |

### 2. 基本的なフック定義

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, HookMatcher, query

async def my_pre_hook(input_data, tool_use_id, context):
    """ツール実行前に呼ばれるフック"""
    tool_name = input_data["tool_name"]
    tool_input = input_data["tool_input"]

    print(f"[PreToolUse] ツール: {tool_name}")
    print(f"[PreToolUse] 入力: {tool_input}")

    return {}  # 空の辞書を返すと通常通り実行

async def my_post_hook(input_data, tool_use_id, context):
    """ツール実行後に呼ばれるフック"""
    tool_name = input_data["tool_name"]
    result = input_data.get("tool_result", {})

    print(f"[PostToolUse] ツール: {tool_name}")
    print(f"[PostToolUse] 結果: {str(result)[:100]}...")

    return {}

options = ClaudeAgentOptions(
    allowed_tools=["Read", "Glob"],
    hooks={
        "PreToolUse": [
            HookMatcher(hooks=[my_pre_hook])
        ],
        "PostToolUse": [
            HookMatcher(hooks=[my_post_hook])
        ]
    }
)
```

---

## 手順2: HookMatcher によるフィルタリング

### 1. 特定ツールへのフック

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, HookMatcher

async def bash_guard(input_data, tool_use_id, context):
    """Bash コマンドを検証"""
    command = input_data["tool_input"].get("command", "")

    dangerous = ["rm -rf", "sudo", "> /dev/"]
    for pattern in dangerous:
        if pattern in command:
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": f"危険なパターン: {pattern}"
                }
            }
    return {}

async def file_logger(input_data, tool_use_id, context):
    """ファイル操作をログ"""
    file_path = input_data["tool_input"].get("file_path", "")
    print(f"[Log] ファイルアクセス: {file_path}")
    return {}

options = ClaudeAgentOptions(
    allowed_tools=["Read", "Write", "Edit", "Bash"],
    hooks={
        "PreToolUse": [
            # Bash のみにフック
            HookMatcher(matcher="Bash", hooks=[bash_guard]),
            # Read, Write, Edit にフック
            HookMatcher(matcher=["Read", "Write", "Edit"], hooks=[file_logger])
        ]
    }
)
```

### 2. ワイルドカードマッチング

**コード:**

```python
from claude_agent_sdk import HookMatcher

# 全てのツールにマッチ
all_tools = HookMatcher(matcher="*", hooks=[my_hook])

# 特定の複数ツール
file_tools = HookMatcher(matcher=["Read", "Write", "Edit"], hooks=[file_hook])

# MCP ツールにマッチ
mcp_tools = HookMatcher(matcher="mcp__*", hooks=[mcp_hook])
```

---

## 手順3: フックの戻り値

### 1. ツール実行の制御

**コード:**

```python
async def permission_hook(input_data, tool_use_id, context):
    """権限に基づいてツール実行を制御"""

    tool_name = input_data["tool_name"]

    # 許可
    if tool_name == "Read":
        return {}

    # 拒否
    if tool_name == "Bash":
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": "Bash は禁止されています"
            }
        }

    # 確認を求める（デフォルト動作に任せる）
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask"
        }
    }
```

### 2. 追加コンテキストの提供

**コード:**

```python
async def context_enrichment_hook(input_data, tool_use_id, context):
    """実行結果に追加情報を付与"""

    return {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": "注意: このファイルは本番環境のものです。慎重に扱ってください。"
        }
    }
```

---

## 手順4: 実践的なフック実装

### 1. 監査ログシステム

**コード:**

```python
import json
from datetime import datetime
from pathlib import Path
from claude_agent_sdk import ClaudeAgentOptions, HookMatcher

class AuditLogger:
    def __init__(self, log_file: str = "audit.jsonl"):
        self.log_file = Path(log_file)

    async def log_pre_tool(self, input_data, tool_use_id, context):
        """ツール実行前のログ"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event": "pre_tool_use",
            "tool_use_id": tool_use_id,
            "tool_name": input_data["tool_name"],
            "tool_input": input_data["tool_input"]
        }
        self._write_log(entry)
        return {}

    async def log_post_tool(self, input_data, tool_use_id, context):
        """ツール実行後のログ"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event": "post_tool_use",
            "tool_use_id": tool_use_id,
            "tool_name": input_data["tool_name"],
            "success": "error" not in str(input_data.get("tool_result", "")).lower()
        }
        self._write_log(entry)
        return {}

    def _write_log(self, entry: dict):
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# 使用例
logger = AuditLogger()

options = ClaudeAgentOptions(
    allowed_tools=["Read", "Write", "Edit", "Bash"],
    hooks={
        "PreToolUse": [HookMatcher(hooks=[logger.log_pre_tool])],
        "PostToolUse": [HookMatcher(hooks=[logger.log_post_tool])]
    }
)
```

### 2. レート制限

**コード:**

```python
import time
from collections import defaultdict
from claude_agent_sdk import ClaudeAgentOptions, HookMatcher

class RateLimiter:
    def __init__(self, max_calls: int = 10, window_seconds: int = 60):
        self.max_calls = max_calls
        self.window = window_seconds
        self.calls = defaultdict(list)

    async def check_rate(self, input_data, tool_use_id, context):
        """レート制限をチェック"""
        tool_name = input_data["tool_name"]
        now = time.time()

        # 古いエントリを削除
        self.calls[tool_name] = [
            t for t in self.calls[tool_name]
            if now - t < self.window
        ]

        if len(self.calls[tool_name]) >= self.max_calls:
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": f"{tool_name} のレート制限に達しました"
                }
            }

        self.calls[tool_name].append(now)
        return {}

# Bash は1分間に5回まで
bash_limiter = RateLimiter(max_calls=5, window_seconds=60)

options = ClaudeAgentOptions(
    allowed_tools=["Read", "Bash"],
    hooks={
        "PreToolUse": [
            HookMatcher(matcher="Bash", hooks=[bash_limiter.check_rate])
        ]
    }
)
```

### 3. コマンドホワイトリスト

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, HookMatcher

ALLOWED_COMMANDS = {
    "ls", "cat", "head", "tail", "grep", "find", "wc",
    "git", "python", "pip", "pytest", "npm", "node"
}

async def whitelist_hook(input_data, tool_use_id, context):
    """ホワイトリストにないコマンドをブロック"""

    command = input_data["tool_input"].get("command", "")
    first_word = command.split()[0] if command.split() else ""
    base_cmd = first_word.split("/")[-1]

    if base_cmd not in ALLOWED_COMMANDS:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": f"コマンド '{base_cmd}' は許可リストにありません"
            }
        }

    return {}
```

<div style="background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #155724; line-height: 1;">&#x2714;</span>
    <span style="font-weight: bold; color: #155724; font-size: 15px;">ポイント</span>
  </div>
  <div style="color: #155724; line-height: 1.6;">
    Hooks はセキュリティ、監査、カスタム制御に不可欠です。本番環境では必ず適切なフックを設定しましょう。
  </div>
</div>

---

## 手順5: フックの組み合わせ

### 1. 複数フックのチェーン

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, HookMatcher

async def log_hook(input_data, tool_use_id, context):
    print(f"[Log] {input_data['tool_name']}")
    return {}

async def validate_hook(input_data, tool_use_id, context):
    # バリデーション処理
    return {}

async def transform_hook(input_data, tool_use_id, context):
    # 入力の変換
    return {}

# フックは順番に実行される
options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [
            HookMatcher(hooks=[log_hook, validate_hook, transform_hook])
        ]
    }
)
```

---

## 演習問題

### 演習1: 機密データ検出

ファイル読み取り結果から機密情報（パスワード、APIキー）を検出し、マスクするフックを作成してください。

### 演習2: 実行時間トラッキング

各ツールの実行時間を計測し、統計をレポートするシステムを作成してください。

### 演習3: 承認ワークフロー

危険な操作に対して、外部サービス（Slack など）で承認を求めるフックを実装してください。

---

## 次のステップ

Hooks を理解しました。次は [カスタムツール](04_custom_tools.md) で、独自のツールを作成する方法を学びましょう。
