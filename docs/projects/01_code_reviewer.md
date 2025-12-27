# 実践プロジェクト: コードレビューア

## 概要

このプロジェクトでは、Claude Agent SDK を使って実用的なコードレビューツールを構築します。

セキュリティ、パフォーマンス、コード品質の観点から自動レビューを行い、レポートを生成します。

---

## プロジェクト構成

```
code_reviewer/
├── __init__.py
├── agents.py        # サブエージェント定義
├── hooks.py         # セキュリティフック
├── tools.py         # カスタムツール
├── config.py        # 設定
└── main.py          # メインアプリケーション
```

---

## 手順1: 設定ファイルの作成

### config.py

**コード:**

```python
"""コードレビューアの設定"""
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class ReviewConfig:
    """レビュー設定"""
    project_path: Path
    output_dir: Path = field(default_factory=lambda: Path("./review_reports"))
    max_file_size: int = 100_000  # 100KB
    excluded_dirs: list[str] = field(default_factory=lambda: [
        "node_modules", "__pycache__", ".git", "venv", ".venv"
    ])
    excluded_extensions: list[str] = field(default_factory=lambda: [
        ".min.js", ".map", ".lock"
    ])

@dataclass
class SecurityConfig:
    """セキュリティ設定"""
    dangerous_patterns: list[str] = field(default_factory=lambda: [
        "eval(", "exec(", "subprocess.call", "shell=True",
        "password", "secret", "api_key", "token"
    ])
    max_line_length: int = 120
    require_type_hints: bool = True

# デフォルト設定
DEFAULT_REVIEW_CONFIG = ReviewConfig(project_path=Path("."))
DEFAULT_SECURITY_CONFIG = SecurityConfig()
```

---

## 手順2: サブエージェントの定義

### agents.py

**コード:**

```python
"""コードレビュー用サブエージェント"""
from claude_agent_sdk import AgentDefinition

# セキュリティレビューエージェント
security_reviewer = AgentDefinition(
    description="セキュリティ脆弱性を検出するエージェント",
    prompt="""あなたはセキュリティエンジニアです。以下の観点からコードをレビューしてください：

## チェック項目
1. **インジェクション攻撃**
   - SQL インジェクション
   - コマンドインジェクション
   - XSS (クロスサイトスクリプティング)

2. **認証・認可**
   - ハードコードされた認証情報
   - 不適切なセッション管理
   - 権限チェックの欠如

3. **データ保護**
   - 機密データの平文保存
   - 不適切なログ出力
   - 暗号化の欠如

4. **入力検証**
   - 未検証のユーザー入力
   - 不適切な型チェック

## 出力形式
発見した問題は以下の形式で報告してください：
- ファイル: [ファイルパス]
- 行: [行番号]
- 重要度: [High/Medium/Low]
- 問題: [説明]
- 推奨: [修正方法]
""",
    tools=["Read", "Glob", "Grep"],
    model="sonnet"
)

# パフォーマンスレビューエージェント
performance_reviewer = AgentDefinition(
    description="パフォーマンス問題を検出するエージェント",
    prompt="""あなたはパフォーマンスエンジニアです。以下の観点からコードをレビューしてください：

## チェック項目
1. **計算効率**
   - 不必要なループ
   - 非効率なアルゴリズム
   - 重複計算

2. **メモリ使用**
   - メモリリークの可能性
   - 大きなオブジェクトの不要な保持
   - 不適切なキャッシュ

3. **I/O 効率**
   - N+1 クエリ問題
   - 不要なファイル操作
   - 同期処理のボトルネック

4. **並行処理**
   - ブロッキング操作
   - 競合状態の可能性
""",
    tools=["Read", "Glob", "Grep"],
    model="sonnet"
)

# コード品質レビューエージェント
quality_reviewer = AgentDefinition(
    description="コード品質を評価するエージェント",
    prompt="""あなたはシニアソフトウェアエンジニアです。以下の観点からコードをレビューしてください：

## チェック項目
1. **可読性**
   - 適切な命名
   - コメントの質
   - コードの構造

2. **保守性**
   - 単一責任の原則
   - DRY (Don't Repeat Yourself)
   - 適切な抽象化

3. **テスト容易性**
   - テストしやすい設計
   - 依存性注入
   - モック可能な設計

4. **ベストプラクティス**
   - 型ヒントの使用
   - エラーハンドリング
   - ドキュメンテーション
""",
    tools=["Read", "Glob", "Grep"],
    model="sonnet"
)

# レポート生成エージェント
report_generator = AgentDefinition(
    description="レビュー結果をレポートにまとめるエージェント",
    prompt="""あなたはテクニカルライターです。レビュー結果を以下の形式でレポートにまとめてください：

# コードレビューレポート

## 概要
[プロジェクトの概要と全体的な評価]

## サマリー
| カテゴリ | 問題数 | 重要度 High | 重要度 Medium | 重要度 Low |
|---------|--------|-------------|---------------|------------|

## セキュリティ
[セキュリティレビューの詳細]

## パフォーマンス
[パフォーマンスレビューの詳細]

## コード品質
[コード品質レビューの詳細]

## 推奨アクション
[優先度順の改善提案]

## 結論
[総評と次のステップ]
""",
    tools=["Read", "Write"],
    model="sonnet"
)

# エージェント辞書
REVIEW_AGENTS = {
    "security": security_reviewer,
    "performance": performance_reviewer,
    "quality": quality_reviewer,
    "report": report_generator
}
```

---

## 手順3: セキュリティフックの実装

### hooks.py

**コード:**

```python
"""セキュリティフック"""
import json
from datetime import datetime
from pathlib import Path
from claude_agent_sdk import HookMatcher

class ReviewAuditLogger:
    """レビュー操作の監査ログ"""

    def __init__(self, log_file: str = "review_audit.jsonl"):
        self.log_file = Path(log_file)

    async def log_tool_use(self, input_data, tool_use_id, context):
        """ツール使用をログ"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "tool": input_data["tool_name"],
            "input": str(input_data["tool_input"])[:500],
            "tool_use_id": tool_use_id
        }

        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        return {}

class ReviewSecurityGuard:
    """レビュー時のセキュリティガード"""

    def __init__(self, config):
        self.config = config

    async def check_file_access(self, input_data, tool_use_id, context):
        """ファイルアクセスを制限"""

        if input_data["tool_name"] not in ["Read", "Write", "Edit"]:
            return {}

        file_path = input_data["tool_input"].get("file_path", "")

        # 除外ディレクトリをチェック
        for excluded in self.config.excluded_dirs:
            if excluded in file_path:
                return {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": f"除外ディレクトリ: {excluded}"
                    }
                }

        # 除外拡張子をチェック
        for ext in self.config.excluded_extensions:
            if file_path.endswith(ext):
                return {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": f"除外ファイル形式: {ext}"
                    }
                }

        return {}

    async def block_write_operations(self, input_data, tool_use_id, context):
        """書き込み操作をブロック（読み取り専用モード）"""

        if input_data["tool_name"] in ["Write", "Edit"]:
            # レポート出力先のみ許可
            file_path = input_data["tool_input"].get("file_path", "")
            if "review_report" not in file_path:
                return {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": "レビュー中はソースコードの変更は禁止です"
                    }
                }

        return {}

def create_review_hooks(config, readonly: bool = True):
    """レビュー用フックを作成"""

    logger = ReviewAuditLogger()
    guard = ReviewSecurityGuard(config)

    hooks = {
        "PreToolUse": [
            # 全ツールにログ
            HookMatcher(hooks=[logger.log_tool_use]),
            # ファイルアクセス制限
            HookMatcher(
                matcher=["Read", "Write", "Edit"],
                hooks=[guard.check_file_access]
            ),
        ]
    }

    # 読み取り専用モードの場合
    if readonly:
        hooks["PreToolUse"].append(
            HookMatcher(
                matcher=["Write", "Edit"],
                hooks=[guard.block_write_operations]
            )
        )

    return hooks
```

---

## 手順4: カスタムツールの実装

### tools.py

**コード:**

```python
"""カスタムレビューツール"""
from pathlib import Path
from claude_agent_sdk import tool, create_sdk_mcp_server

@tool(
    "get_file_stats",
    "ファイルの統計情報を取得します",
    {"path": str}
)
async def get_file_stats(args: dict) -> dict:
    """ファイル統計を取得"""
    path = Path(args["path"])

    if not path.exists():
        return {"content": [{"type": "text", "text": f"パスが存在しません: {path}"}]}

    stats = {
        "total_files": 0,
        "total_lines": 0,
        "by_extension": {}
    }

    for file in path.rglob("*"):
        if file.is_file():
            ext = file.suffix or "no_ext"
            stats["total_files"] += 1

            if ext not in stats["by_extension"]:
                stats["by_extension"][ext] = {"files": 0, "lines": 0}

            stats["by_extension"][ext]["files"] += 1

            try:
                lines = len(file.read_text().splitlines())
                stats["total_lines"] += lines
                stats["by_extension"][ext]["lines"] += lines
            except:
                pass

    output = f"""## ファイル統計
- 総ファイル数: {stats['total_files']}
- 総行数: {stats['total_lines']}

### 拡張子別
"""
    for ext, data in sorted(stats["by_extension"].items()):
        output += f"- {ext}: {data['files']} ファイル, {data['lines']} 行\n"

    return {"content": [{"type": "text", "text": output}]}

@tool(
    "find_patterns",
    "危険なパターンを検索します",
    {"path": str, "patterns": list}
)
async def find_patterns(args: dict) -> dict:
    """危険なパターンを検索"""
    path = Path(args["path"])
    patterns = args["patterns"]

    findings = []

    for file in path.rglob("*.py"):
        try:
            content = file.read_text()
            for i, line in enumerate(content.splitlines(), 1):
                for pattern in patterns:
                    if pattern.lower() in line.lower():
                        findings.append({
                            "file": str(file),
                            "line": i,
                            "pattern": pattern,
                            "content": line.strip()[:100]
                        })
        except:
            pass

    if not findings:
        return {"content": [{"type": "text", "text": "危険なパターンは見つかりませんでした"}]}

    output = f"## 検出された危険なパターン ({len(findings)} 件)\n\n"
    for f in findings[:50]:  # 最大50件
        output += f"- **{f['file']}:{f['line']}** - `{f['pattern']}`\n"
        output += f"  ```\n  {f['content']}\n  ```\n\n"

    return {"content": [{"type": "text", "text": output}]}

# MCP サーバーを作成
review_tools_server = create_sdk_mcp_server(
    name="review-tools",
    version="1.0.0",
    tools=[get_file_stats, find_patterns]
)
```

---

## 手順5: メインアプリケーション

### main.py

**コード:**

```python
"""コードレビューアのメインアプリケーション"""
import asyncio
from pathlib import Path
from datetime import datetime
from claude_agent_sdk import ClaudeAgentOptions, query, ResultMessage

from .config import ReviewConfig, SecurityConfig, DEFAULT_REVIEW_CONFIG
from .agents import REVIEW_AGENTS
from .hooks import create_review_hooks
from .tools import review_tools_server

async def run_code_review(
    project_path: str,
    output_path: str = None,
    review_types: list[str] = None
):
    """コードレビューを実行"""

    config = ReviewConfig(project_path=Path(project_path))

    if output_path:
        config.output_dir = Path(output_path)

    config.output_dir.mkdir(parents=True, exist_ok=True)

    # レビュータイプ（デフォルトは全て）
    if review_types is None:
        review_types = ["security", "performance", "quality"]

    # オプションを設定
    options = ClaudeAgentOptions(
        cwd=config.project_path,
        agents=REVIEW_AGENTS,
        mcp_servers={"review": review_tools_server},
        allowed_tools=[
            "Read", "Glob", "Grep", "Task",
            "mcp__review__get_file_stats",
            "mcp__review__find_patterns"
        ],
        hooks=create_review_hooks(config, readonly=True),
        max_turns=50,
        system_prompt=f"""あなたはコードレビューアシスタントです。

## レビュー対象
プロジェクト: {config.project_path}

## 手順
1. get_file_stats ツールでプロジェクトの概要を把握
2. 各レビューエージェントを順番に実行
3. 結果をまとめてレポートを生成
"""
    )

    # レビュー実行
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = config.output_dir / f"review_report_{timestamp}.md"

    prompt = f"""以下のレビューを実行し、{report_file} にレポートを出力してください：

レビュータイプ: {', '.join(review_types)}

1. まず get_file_stats でプロジェクトの概要を確認
2. find_patterns で危険なパターンをスキャン
3. 各レビューエージェントを実行:
{chr(10).join(f'   - {t} エージェント' for t in review_types)}
4. report エージェントでレポートを生成
"""

    print(f"レビュー開始: {config.project_path}")
    print(f"レポート出力先: {report_file}")
    print("-" * 50)

    total_cost = 0.0

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, ResultMessage):
            total_cost = message.total_cost_usd
        else:
            # 進捗を表示
            print(".", end="", flush=True)

    print("\n" + "-" * 50)
    print(f"レビュー完了")
    print(f"レポート: {report_file}")
    print(f"コスト: ${total_cost:.4f}")

    return report_file

# CLI エントリーポイント
def main():
    import argparse

    parser = argparse.ArgumentParser(description="AI コードレビューア")
    parser.add_argument("project", help="レビュー対象のプロジェクトパス")
    parser.add_argument("-o", "--output", help="レポート出力先ディレクトリ")
    parser.add_argument(
        "-t", "--types",
        nargs="+",
        choices=["security", "performance", "quality"],
        help="レビュータイプ"
    )

    args = parser.parse_args()

    asyncio.run(run_code_review(
        project_path=args.project,
        output_path=args.output,
        review_types=args.types
    ))

if __name__ == "__main__":
    main()
```

---

## 使用例

### コマンドラインから実行

```bash
# 全レビューを実行
python -m code_reviewer /path/to/project

# セキュリティレビューのみ
python -m code_reviewer /path/to/project -t security

# 複数タイプを指定
python -m code_reviewer /path/to/project -t security performance -o ./reports
```

### Python から呼び出し

```python
import asyncio
from code_reviewer.main import run_code_review

async def main():
    report = await run_code_review(
        project_path="/path/to/project",
        review_types=["security", "quality"]
    )
    print(f"レポートを生成しました: {report}")

asyncio.run(main())
```

---

## 次のステップ

コードレビューアの構築が完了しました。次は [ドキュメント生成](02_documentation_generator.md) で、もう一つの実践プロジェクトを構築しましょう。
