# MCP 連携

## 概要

このセクションでは、Model Context Protocol (MCP) を使って外部サーバーと連携する方法を学習します。

MCP を使うと、データベース、ファイルシステム、外部 API など様々なサービスを Claude と統合できます。

---

## 手順1: MCP の基本概念

### 1. MCP とは

MCP (Model Context Protocol) は、AI モデルと外部ツール/データソースを接続するための標準プロトコルです。

```
┌─────────────┐     MCP      ┌─────────────┐
│   Claude    │◄────────────►│ MCP Server  │
│  Agent SDK  │              │(ツール提供)  │
└─────────────┘              └─────────────┘
                                   │
                                   ▼
                             ┌─────────────┐
                             │ 外部サービス │
                             │ (DB, API等) │
                             └─────────────┘
```

### 2. サーバーの種類

| タイプ | 説明 | 例 |
|-------|------|-----|
| インプロセス | SDK 内で直接実行 | カスタムツール |
| stdio | サブプロセスで実行 | 外部 MCP サーバー |
| SSE | HTTP 経由で接続 | リモートサーバー |

---

## 手順2: インプロセスサーバー

### 1. SDK 内でサーバーを作成

**コード:**

```python
from claude_agent_sdk import (
    tool,
    create_sdk_mcp_server,
    ClaudeAgentOptions,
    query
)

# カスタムツールを定義
@tool("echo", "入力をそのまま返します", {"message": str})
async def echo(args):
    return {"content": [{"type": "text", "text": args["message"]}]}

@tool("reverse", "文字列を逆順にします", {"text": str})
async def reverse(args):
    return {"content": [{"type": "text", "text": args["text"][::-1]}]}

# インプロセスサーバーを作成
internal_server = create_sdk_mcp_server(
    name="internal",
    version="1.0.0",
    tools=[echo, reverse]
)

# オプションに追加
options = ClaudeAgentOptions(
    mcp_servers={"internal": internal_server},
    allowed_tools=[
        "mcp__internal__echo",
        "mcp__internal__reverse"
    ]
)

async def main():
    async for message in query(
        prompt="'Hello World' を逆順にしてください",
        options=options
    ):
        print(message)
```

---

## 手順3: 外部 MCP サーバーの接続

### 1. stdio タイプのサーバー

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions

# 外部 MCP サーバーを設定
options = ClaudeAgentOptions(
    mcp_servers={
        # ファイルシステムサーバー
        "filesystem": {
            "type": "stdio",
            "command": "mcp-server-filesystem",
            "args": ["/allowed/directory"]
        },

        # SQLite サーバー
        "database": {
            "type": "stdio",
            "command": "mcp-server-sqlite",
            "args": ["--db-path", "/path/to/db.sqlite"]
        },

        # Git サーバー
        "git": {
            "type": "stdio",
            "command": "mcp-server-git",
            "args": ["/path/to/repo"]
        }
    },
    allowed_tools=[
        "mcp__filesystem__read_file",
        "mcp__filesystem__write_file",
        "mcp__database__query",
        "mcp__git__status"
    ]
)
```

### 2. 環境変数の設定

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions
import os

options = ClaudeAgentOptions(
    mcp_servers={
        "api_server": {
            "type": "stdio",
            "command": "mcp-server-api",
            "args": [],
            "env": {
                "API_KEY": os.getenv("MY_API_KEY"),
                "API_URL": "https://api.example.com"
            }
        }
    }
)
```

---

## 手順4: ハイブリッド構成

### 1. インプロセス + 外部サーバー

**コード:**

```python
from claude_agent_sdk import (
    tool,
    create_sdk_mcp_server,
    ClaudeAgentOptions
)

# カスタムツール（インプロセス）
@tool("log_action", "アクションをログに記録", {"action": str})
async def log_action(args):
    print(f"[LOG] {args['action']}")
    return {"content": [{"type": "text", "text": "ログ記録完了"}]}

internal_server = create_sdk_mcp_server(
    name="logger",
    version="1.0.0",
    tools=[log_action]
)

# ハイブリッド構成
options = ClaudeAgentOptions(
    mcp_servers={
        # インプロセス
        "logger": internal_server,

        # 外部（ファイルシステム）
        "fs": {
            "type": "stdio",
            "command": "mcp-server-filesystem",
            "args": ["/workspace"]
        },

        # 外部（データベース）
        "db": {
            "type": "stdio",
            "command": "mcp-server-sqlite",
            "args": ["--db-path", "data.db"]
        }
    },
    allowed_tools=[
        "mcp__logger__log_action",
        "mcp__fs__read_file",
        "mcp__fs__write_file",
        "mcp__db__query"
    ]
)
```

<div style="background-color: #f0f8ff; border: 1px solid #cce5ff; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #0d6efd; line-height: 1;">&#x24D8;</span>
    <span style="font-weight: bold; color: #0d6efd; font-size: 15px;">Note</span>
  </div>
  <div style="color: #454545; line-height: 1.6;">
    インプロセスサーバーは低レイテンシで動作しますが、外部サーバーは独立したプロセスで実行されるため、より分離された環境で動作します。
  </div>
</div>

---

## 手順5: 実践的な MCP 構成

### 1. 開発環境向け構成

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions

dev_options = ClaudeAgentOptions(
    mcp_servers={
        # ローカルファイルシステム
        "workspace": {
            "type": "stdio",
            "command": "mcp-server-filesystem",
            "args": ["/home/dev/projects"]
        },

        # ローカル PostgreSQL
        "postgres": {
            "type": "stdio",
            "command": "mcp-server-postgres",
            "args": [],
            "env": {
                "DATABASE_URL": "postgresql://localhost/devdb"
            }
        },

        # GitHub API
        "github": {
            "type": "stdio",
            "command": "mcp-server-github",
            "args": [],
            "env": {
                "GITHUB_TOKEN": "${GITHUB_TOKEN}"
            }
        }
    },
    allowed_tools=[
        "mcp__workspace__*",
        "mcp__postgres__query",
        "mcp__github__get_issues",
        "mcp__github__create_pr"
    ]
)
```

### 2. 本番環境向け構成

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions

prod_options = ClaudeAgentOptions(
    mcp_servers={
        # 読み取り専用ファイルシステム
        "docs": {
            "type": "stdio",
            "command": "mcp-server-filesystem",
            "args": ["/app/docs", "--read-only"]
        },

        # 監査付きデータベース
        "database": {
            "type": "stdio",
            "command": "mcp-server-postgres",
            "args": ["--audit-log", "/var/log/db-audit.log"],
            "env": {
                "DATABASE_URL": "${PROD_DATABASE_URL}"
            }
        }
    },
    # 本番環境では厳格なツール制限
    allowed_tools=[
        "mcp__docs__read_file",
        "mcp__database__query"  # SELECT のみ
    ]
)
```

---

## 手順6: MCP サーバーの管理

### 1. サーバーの健全性チェック

**コード:**

```python
import asyncio
from claude_agent_sdk import ClaudeAgentOptions, query

async def check_mcp_health(server_name: str, tool_name: str):
    """MCP サーバーの健全性をチェック"""

    options = ClaudeAgentOptions(
        mcp_servers={
            server_name: {
                "type": "stdio",
                "command": f"mcp-server-{server_name}",
                "args": []
            }
        },
        allowed_tools=[f"mcp__{server_name}__{tool_name}"],
        max_turns=1
    )

    try:
        async for message in query(
            prompt=f"{tool_name} ツールをテスト実行してください",
            options=options
        ):
            pass
        return {"server": server_name, "status": "healthy"}

    except Exception as e:
        return {"server": server_name, "status": "unhealthy", "error": str(e)}

# 複数サーバーをチェック
async def health_check_all():
    servers = [
        ("filesystem", "list_files"),
        ("database", "query"),
        ("github", "get_user")
    ]

    results = await asyncio.gather(*[
        check_mcp_health(server, tool)
        for server, tool in servers
    ])

    for result in results:
        status = "OK" if result["status"] == "healthy" else "NG"
        print(f"[{status}] {result['server']}")
```

### 2. エラーリカバリー

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions

class MCPServerManager:
    def __init__(self):
        self.servers = {}
        self.retry_counts = {}

    def configure_with_fallback(self, primary: dict, fallback: dict = None):
        """フォールバック付きでサーバーを設定"""
        self.servers["primary"] = primary
        if fallback:
            self.servers["fallback"] = fallback

    def get_options(self) -> ClaudeAgentOptions:
        """現在有効なサーバーでオプションを作成"""
        active_servers = {}

        for name, config in self.servers.items():
            if self.retry_counts.get(name, 0) < 3:
                active_servers[name] = config

        return ClaudeAgentOptions(mcp_servers=active_servers)

    def mark_failure(self, server_name: str):
        """サーバー失敗をマーク"""
        self.retry_counts[server_name] = self.retry_counts.get(server_name, 0) + 1

    def reset_failures(self):
        """失敗カウントをリセット"""
        self.retry_counts = {}
```

<div style="background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #155724; line-height: 1;">&#x2714;</span>
    <span style="font-weight: bold; color: #155724; font-size: 15px;">ポイント</span>
  </div>
  <div style="color: #155724; line-height: 1.6;">
    本番環境では、MCP サーバーの健全性監視とフォールバック戦略を実装することを推奨します。
  </div>
</div>

---

## 演習問題

### 演習1: カスタム MCP サーバー

独自のビジネスロジックを提供する MCP サーバーを作成し、Claude Agent SDK と統合してください。

### 演習2: マルチサーバーオーケストレーション

複数の MCP サーバーを連携させて、データの取得 → 加工 → 保存のパイプラインを構築してください。

### 演習3: MCP サーバーモニタリング

MCP サーバーの使用状況を監視し、パフォーマンスレポートを生成するシステムを作成してください。

---

## 次のステップ

応用機能の学習が完了しました。次は [コードレビューア](../05_projects/01_code_reviewer.md) で、実践的なプロジェクトを構築しましょう。
