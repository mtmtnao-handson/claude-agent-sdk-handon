# オプション概要

## 概要

このセクションでは、`ClaudeAgentOptions` クラスを使って Claude Agent SDK の動作を細かく制御する方法を学習します。

オプションを適切に設定することで、セキュリティ、コスト、パフォーマンスを最適化できます。

---

## 手順1: ClaudeAgentOptions の基本

### 1. オプションクラスのインポートと基本構造

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

# 基本的なオプション設定
options = ClaudeAgentOptions(
    system_prompt="あなたはPythonの専門家です",
    max_turns=10,
    cwd="/path/to/project",
    allowed_tools=["Read", "Write", "Bash"],
    permission_mode="acceptEdits"
)

async def main():
    async for message in query(prompt="hello.py を作成して", options=options):
        print(message)
```

---

## 手順2: オプション一覧

### 1. 全オプションの概要

| オプション | 型 | 説明 | デフォルト |
|-----------|-----|------|-----------|
| `system_prompt` | `str` | カスタムシステムプロンプト | なし |
| `max_turns` | `int` | 最大会話ターン数 | 無制限 |
| `cwd` | `str` / `Path` | 作業ディレクトリ | カレントディレクトリ |
| `allowed_tools` | `list[str]` | 使用許可するツール | 全ツール |
| `permission_mode` | `str` | 権限モード | `"default"` |
| `model` | `str` | 使用するモデル | 設定による |
| `agents` | `dict` | サブエージェント定義 | なし |
| `hooks` | `dict` | フック設定 | なし |
| `mcp_servers` | `dict` | MCP サーバー設定 | なし |

### 2. オプションの優先順位

```
query() の options 引数 > ClaudeSDKClient の options > デフォルト値
```

---

## 手順3: 構成パターン

### 1. 読み取り専用モード

ファイルを変更せずに分析のみを行う場合。

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions

read_only = ClaudeAgentOptions(
    allowed_tools=["Read", "Glob", "Grep"],
    permission_mode="default"
)
```

### 2. 開発モード

開発中にファイル編集を自動承認する場合。

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions

development = ClaudeAgentOptions(
    allowed_tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep"],
    permission_mode="acceptEdits",
    max_turns=20
)
```

### 3. CI/CD モード

自動化パイプラインで完全自動実行する場合。

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions

ci_cd = ClaudeAgentOptions(
    allowed_tools=["Read", "Write", "Edit", "Bash"],
    permission_mode="bypassPermissions",
    max_turns=50
)
```

<div style="background-color: #fff3cd; border: 1px solid #ffc107; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #856404; line-height: 1;">&#x26A0;</span>
    <span style="font-weight: bold; color: #856404; font-size: 15px;">注意</span>
  </div>
  <div style="color: #454545; line-height: 1.6;">
    <code>bypassPermissions</code> は確認なしで全操作を実行します。信頼できる環境でのみ使用してください。
  </div>
</div>

### 4. コードレビューモード

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions

code_review = ClaudeAgentOptions(
    system_prompt="""
あなたはシニアコードレビューアです。
以下の観点からコードをレビューしてください：
- バグの可能性
- セキュリティ問題
- パフォーマンス
- 可読性
""",
    allowed_tools=["Read", "Glob", "Grep"],
    max_turns=10
)
```

---

## 手順4: オプションの再利用

### 1. ファクトリー関数パターン

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions

def create_analyzer_options(
    project_path: str,
    max_turns: int = 10
) -> ClaudeAgentOptions:
    """コード分析用のオプションを作成"""
    return ClaudeAgentOptions(
        system_prompt="あなたはコード分析の専門家です",
        cwd=project_path,
        allowed_tools=["Read", "Glob", "Grep"],
        max_turns=max_turns
    )

def create_developer_options(
    project_path: str,
    auto_approve: bool = False
) -> ClaudeAgentOptions:
    """開発作業用のオプションを作成"""
    return ClaudeAgentOptions(
        cwd=project_path,
        allowed_tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep"],
        permission_mode="acceptEdits" if auto_approve else "default",
        max_turns=30
    )

# 使用例
analyzer = create_analyzer_options("/path/to/project")
developer = create_developer_options("/path/to/project", auto_approve=True)
```

### 2. 環境別の構成

**コード:**

```python
import os
from claude_agent_sdk import ClaudeAgentOptions

def get_options_for_environment() -> ClaudeAgentOptions:
    """環境変数に基づいてオプションを設定"""

    env = os.getenv("ENVIRONMENT", "development")

    base_tools = ["Read", "Glob", "Grep"]

    if env == "production":
        return ClaudeAgentOptions(
            allowed_tools=base_tools,
            permission_mode="default",
            max_turns=5
        )

    elif env == "staging":
        return ClaudeAgentOptions(
            allowed_tools=base_tools + ["Write", "Edit"],
            permission_mode="default",
            max_turns=10
        )

    else:  # development
        return ClaudeAgentOptions(
            allowed_tools=base_tools + ["Write", "Edit", "Bash"],
            permission_mode="acceptEdits",
            max_turns=20
        )
```

---

## 手順5: オプションの検証

### 1. 設定の確認

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions

def validate_options(options: ClaudeAgentOptions) -> list[str]:
    """オプション設定を検証し、警告メッセージを返す"""

    warnings = []

    # 危険な組み合わせをチェック
    if options.permission_mode == "bypassPermissions":
        warnings.append("警告: bypassPermissions モードが有効です")

        if "Bash" in (options.allowed_tools or []):
            warnings.append("危険: Bash ツールが bypassPermissions で有効です")

    # ターン数のチェック
    if options.max_turns and options.max_turns > 50:
        warnings.append(f"注意: max_turns が {options.max_turns} に設定されています")

    # 作業ディレクトリのチェック
    if options.cwd:
        import os
        if not os.path.exists(options.cwd):
            warnings.append(f"エラー: 作業ディレクトリが存在しません: {options.cwd}")

    return warnings

# 使用例
options = ClaudeAgentOptions(
    permission_mode="bypassPermissions",
    allowed_tools=["Bash"],
    max_turns=100
)

for warning in validate_options(options):
    print(warning)
```

<details>
<summary><strong>実行結果を見る</strong></summary>

```
警告: bypassPermissions モードが有効です
危険: Bash ツールが bypassPermissions で有効です
注意: max_turns が 100 に設定されています
```

</details>

---

## 手順6: オプションの組み合わせ

### 1. 複数オプションのマージ

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions
from dataclasses import asdict

def merge_options(
    base: ClaudeAgentOptions,
    override: ClaudeAgentOptions
) -> ClaudeAgentOptions:
    """2つのオプションをマージ（override が優先）"""

    # 基本オプションを辞書に変換
    base_dict = {}
    override_dict = {}

    # 設定されているフィールドのみを取得
    for field in ['system_prompt', 'max_turns', 'cwd', 'allowed_tools', 'permission_mode']:
        base_val = getattr(base, field, None)
        override_val = getattr(override, field, None)

        if override_val is not None:
            base_dict[field] = override_val
        elif base_val is not None:
            base_dict[field] = base_val

    return ClaudeAgentOptions(**base_dict)

# 使用例
base_options = ClaudeAgentOptions(
    allowed_tools=["Read", "Glob"],
    max_turns=10
)

override_options = ClaudeAgentOptions(
    allowed_tools=["Read", "Write", "Edit"],  # 上書き
    system_prompt="カスタムプロンプト"  # 追加
)

merged = merge_options(base_options, override_options)
```

<div style="background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #155724; line-height: 1;">&#x2714;</span>
    <span style="font-weight: bold; color: #155724; font-size: 15px;">ポイント</span>
  </div>
  <div style="color: #155724; line-height: 1.6;">
    プロジェクト共通の基本オプションを定義し、タスクごとに必要な部分だけをオーバーライドするパターンが便利です。
  </div>
</div>

---

## 演習問題

### 演習1: プロファイル管理

複数のオプションプロファイル（analyzer, developer, reviewer など）を管理するクラスを作成してください。

### 演習2: 設定ファイル対応

YAML または JSON ファイルからオプションを読み込む関数を作成してください。

### 演習3: オプションビルダー

メソッドチェーンでオプションを構築できるビルダークラスを作成してください。

```python
options = (OptionsBuilder()
    .with_tools(["Read", "Write"])
    .with_permission_mode("acceptEdits")
    .with_max_turns(10)
    .build())
```

---

## 次のステップ

オプションの全体像を理解しました。次は [allowed_tools](02_allowed_tools.md) で、ツールの許可設定について詳しく学びましょう。
