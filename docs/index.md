# Claude Agent SDK (Python) ハンズオン

## 概要

このハンズオンでは、**Claude Agent SDK (Python)** を使用して、エージェント型AIアプリケーションを構築する方法を学習します。

Claude Agent SDK は、Claude Code の内部で使用されているエージェントループ、ツール、コンテキスト管理機能をプログラマブルに提供するSDKです。通常の Anthropic Client SDK とは異なり、ツールの実行を Claude が自律的に行うため、開発者はツールループを自分で実装する必要がありません。

---

## Claude Agent SDK とは

```python
# Client SDK: ツールループを自分で実装
response = client.messages.create(...)
while response.stop_reason == "tool_use":
    result = your_tool_executor(response.tool_use)
    response = client.messages.create(tool_result=result, ...)

# Agent SDK: Claude が自律的にツールを実行
async for message in query(prompt="auth.py のバグを修正して"):
    print(message)
```

**主な特徴:**

- **自律的なツール実行**: ファイル読み書き、コマンド実行、Web検索などを Claude が自動で実行
- **ストリーミングレスポンス**: リアルタイムで進捗を確認可能
- **豊富なビルトインツール**: Read, Write, Edit, Bash, Glob, Grep, WebSearch, WebFetch, Task
- **高度なカスタマイズ**: Hooks, サブエージェント, カスタムツール, MCP連携

---

## 前提条件

| 項目 | 説明 |
|-----|------|
| Python | 3.10 以上 |
| Claude Code | ローカルにインストール済み（ランタイムとして必要） |
| エディタ | VS Code 推奨 |
| 認証 | Anthropic API Key / Amazon Bedrock / Google Vertex AI のいずれか |

<div style="background-color: #f0f8ff; border: 1px solid #cce5ff; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #0d6efd; line-height: 1;">&#x24D8;</span>
    <span style="font-weight: bold; color: #0d6efd; font-size: 15px;">Note</span>
  </div>
  <div style="color: #454545; line-height: 1.6;">
    Claude Agent SDK は Claude Code CLI をランタイムとして使用します。SDK単体では動作しないため、事前に Claude Code のインストールが必要です。
  </div>
</div>

---

## 学習目標

このハンズオンを完了すると、以下ができるようになります：

- `query()` 関数を使った基本的なエージェント実行
- `ClaudeAgentOptions` による詳細な動作制御
- ビルトインツールの活用
- セッション管理による会話の継続
- サブエージェントを使った複雑なワークフロー構築
- Hooks によるカスタム処理の追加
- カスタムツールと MCP サーバーの作成

---

## ハンズオンの流れ

| セクション | 内容 | ファイル数 |
|-----------|------|-----------|
| 0 | [環境セットアップ](00_setup/01_environment_setup.md) | 1 |
| 1 | [基本操作](01_basics/01_query_function.md) | 4 |
| 2 | [オプション設定](02_options/01_options_overview.md) | 6 |
| 3 | [ビルトインツール](03_tools/01_builtin_tools_overview.md) | 6 |
| 4 | [応用機能](04_advanced/01_sessions.md) | 5 |
| 5 | [実践プロジェクト](05_projects/01_code_reviewer.md) | 2 |

---

## 次のステップ

[環境セットアップ](00_setup/01_environment_setup.md) に進みましょう。
