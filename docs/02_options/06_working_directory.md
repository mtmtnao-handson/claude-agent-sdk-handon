# working_directory (cwd) 設定

## 概要

このセクションでは、`cwd` オプションを使って Claude の作業ディレクトリを設定する方法を学習します。

作業ディレクトリを適切に設定することで、ファイル操作の安全性と利便性を向上できます。

**サンプルスクリプト:**

このドキュメントの例は、以下のスクリプトで実際に試すことができます：

```bash
src/02_options/07_working_directory/
├── 01_basic.py      # 手順1-2: 基本的な cwd 設定、プロジェクト管理
├── 02_sandbox.py    # 手順3: サンドボックス実行
├── 03_security.py   # 手順4: パス制限とセキュリティ
└── 04_workspace.py  # 手順5: ワークスペース管理
```

```bash
# 基本的な使い方 (手順1-2)
python src/02_options/07_working_directory/01_basic.py -l    # モード一覧
python src/02_options/07_working_directory/01_basic.py -m auto-detect -p "リポジトリを分析して"

# サンドボックス実行 (手順3)
python src/02_options/07_working_directory/02_sandbox.py -l
python src/02_options/07_working_directory/02_sandbox.py -m temp -p "hello.py を作成して実行して"

# パス制限とセキュリティ (手順4)
python src/02_options/07_working_directory/03_security.py -l
python src/02_options/07_working_directory/03_security.py -m readonly -p "コードを分析して"

# ワークスペース管理 (手順5)
python src/02_options/07_working_directory/04_workspace.py --list-workspaces
python src/02_options/07_working_directory/04_workspace.py -w main -p "プロジェクトを分析して"
```

---

## 手順1: cwd の基本

### 1. 基本的な設定

**コード:**

```python
from pathlib import Path
from claude_agent_sdk import ClaudeAgentOptions, query

# 文字列で指定
options_str = ClaudeAgentOptions(
    cwd="/path/to/project"
)

# Path オブジェクトで指定
options_path = ClaudeAgentOptions(
    cwd=Path("/path/to/project")
)

async def main():
    async for message in query(
        prompt="このプロジェクトの構造を分析して",
        options=options_str
    ):
        print(message)
```

### 2. cwd の効果

| 効果 | 説明 |
|-----|------|
| 相対パス解決 | ファイル操作の基準点 |
| セキュリティ | アクセス可能な範囲を制限 |
| コンテキスト | Claude がプロジェクト構造を理解 |

---

## 手順2: プロジェクト別の設定

### 1. 複数プロジェクトの管理

**コード:**

```python
from pathlib import Path
from claude_agent_sdk import ClaudeAgentOptions, query

class ProjectManager:
    def __init__(self, base_path: str = "~/projects"):
        self.base_path = Path(base_path).expanduser()

    def get_options(self, project_name: str) -> ClaudeAgentOptions:
        """プロジェクト用のオプションを取得"""
        project_path = self.base_path / project_name

        if not project_path.exists():
            raise ValueError(f"プロジェクトが存在しません: {project_path}")

        return ClaudeAgentOptions(
            cwd=project_path,
            system_prompt=f"プロジェクト '{project_name}' で作業しています",
            allowed_tools=["Read", "Write", "Edit", "Glob", "Grep"]
        )

# 使用例
async def work_on_project():
    manager = ProjectManager()

    # プロジェクト A で作業
    options_a = manager.get_options("project-a")
    async for message in query(
        prompt="README.md を読んで",
        options=options_a
    ):
        print(message)

    # プロジェクト B で作業
    options_b = manager.get_options("project-b")
    async for message in query(
        prompt="src/ の構造を分析して",
        options=options_b
    ):
        print(message)
```

### 2. 動的なディレクトリ選択

**コード:**

```python
import os
from pathlib import Path
from claude_agent_sdk import ClaudeAgentOptions

def detect_project_root() -> Path:
    """Git リポジトリのルートを検出"""
    current = Path.cwd()

    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent

    raise ValueError("Git リポジトリが見つかりません")

def get_auto_options() -> ClaudeAgentOptions:
    """現在のプロジェクトを自動検出してオプションを返す"""
    try:
        project_root = detect_project_root()
    except ValueError:
        project_root = Path.cwd()

    return ClaudeAgentOptions(
        cwd=project_root,
        allowed_tools=["Read", "Write", "Edit", "Glob", "Grep", "Bash"]
    )
```

---

## 手順3: サンドボックス実行

### 1. 一時ディレクトリでの安全な実行

**コード:**

```python
import asyncio
import tempfile
import shutil
from pathlib import Path
from claude_agent_sdk import ClaudeAgentOptions, query

async def sandboxed_execution(prompt: str, source_dir: str = None):
    """一時ディレクトリで安全に実行"""

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # 必要に応じてソースをコピー
        if source_dir:
            shutil.copytree(source_dir, tmp_path / "project")
            work_dir = tmp_path / "project"
        else:
            work_dir = tmp_path

        print(f"サンドボックス: {work_dir}")

        options = ClaudeAgentOptions(
            cwd=work_dir,
            permission_mode="acceptEdits",
            allowed_tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep"]
        )

        async for message in query(prompt=prompt, options=options):
            print(message)

        # 結果を確認
        print("\n生成されたファイル:")
        for f in work_dir.rglob("*"):
            if f.is_file():
                print(f"  {f.relative_to(work_dir)}")

# asyncio.run(sandboxed_execution("Python プロジェクトを初期化して"))
```

<div style="background-color: #f0f8ff; border: 1px solid #cce5ff; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #0d6efd; line-height: 1;">&#x24D8;</span>
    <span style="font-weight: bold; color: #0d6efd; font-size: 15px;">Note</span>
  </div>
  <div style="color: #454545; line-height: 1.6;">
    サンドボックス実行は、不明なコードの実行やテストに最適です。元のファイルは影響を受けません。
  </div>
</div>

### 2. Docker コンテナとの連携

**コード:**

```python
import subprocess
from claude_agent_sdk import ClaudeAgentOptions, query

async def docker_sandboxed_query(prompt: str, image: str = "python:3.11"):
    """Docker コンテナ内で実行"""

    # コンテナを起動
    container_id = subprocess.check_output([
        "docker", "run", "-d", "--rm",
        "-v", "/tmp/sandbox:/workspace",
        image, "tail", "-f", "/dev/null"
    ]).decode().strip()

    try:
        options = ClaudeAgentOptions(
            cwd="/tmp/sandbox",
            allowed_tools=["Read", "Write", "Edit", "Bash", "Glob"],
            permission_mode="acceptEdits"
        )

        async for message in query(prompt=prompt, options=options):
            print(message)

    finally:
        # コンテナを停止
        subprocess.run(["docker", "stop", container_id], capture_output=True)
```

---

## 手順4: パス制限とセキュリティ

### 1. ディレクトリ外へのアクセス防止

**コード:**

```python
from pathlib import Path
from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient, HookMatcher

def is_path_safe(path: str, allowed_root: Path) -> bool:
    """パスが許可されたディレクトリ内かチェック"""
    try:
        resolved = Path(path).resolve()
        return resolved.is_relative_to(allowed_root)
    except (ValueError, OSError):
        return False

async def path_guard_hook(input_data, tool_use_id, context):
    """ディレクトリ外へのアクセスをブロック"""

    tool_name = input_data["tool_name"]
    tool_input = input_data.get("tool_input", {})

    # パスを含むツールをチェック
    path_params = ["file_path", "path", "pattern"]
    allowed_root = Path(context.get("cwd", ".")).resolve()

    for param in path_params:
        if param in tool_input:
            path = tool_input[param]
            if not is_path_safe(path, allowed_root):
                return {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": f"パス '{path}' は許可されたディレクトリ外です"
                    }
                }

    return {}

# オプションに Hook を追加
options = ClaudeAgentOptions(
    cwd="/safe/project/path",
    allowed_tools=["Read", "Write", "Edit", "Glob"],
    hooks={
        "PreToolUse": [
            HookMatcher(hooks=[path_guard_hook])
        ]
    }
)
```

### 2. 読み取り専用ディレクトリの設定

**コード:**

```python
from pathlib import Path
from claude_agent_sdk import ClaudeAgentOptions

def create_readonly_options(project_path: str) -> ClaudeAgentOptions:
    """読み取り専用のオプションを作成"""
    return ClaudeAgentOptions(
        cwd=project_path,
        allowed_tools=["Read", "Glob", "Grep"],  # 書き込みツールを除外
        permission_mode="default"
    )

def create_write_enabled_options(
    project_path: str,
    writable_dirs: list[str] = None
) -> ClaudeAgentOptions:
    """特定ディレクトリのみ書き込み可能なオプションを作成"""

    # 書き込み可能なディレクトリを制限するロジックは
    # Hook で実装（上記の path_guard_hook を参照）

    return ClaudeAgentOptions(
        cwd=project_path,
        allowed_tools=["Read", "Write", "Edit", "Glob", "Grep"],
        system_prompt=f"""書き込みは以下のディレクトリのみ許可:
{chr(10).join(f'- {d}' for d in (writable_dirs or []))}

他のディレクトリへの書き込みは禁止です。"""
    )
```

---

## 手順5: ワークスペース管理

### 1. マルチワークスペース対応

**コード:**

```python
import asyncio
from pathlib import Path
from dataclasses import dataclass
from claude_agent_sdk import ClaudeAgentOptions, query

@dataclass
class Workspace:
    name: str
    path: Path
    tools: list[str]
    readonly: bool = False

class WorkspaceManager:
    def __init__(self):
        self.workspaces: dict[str, Workspace] = {}
        self.active_workspace: str = None

    def add_workspace(
        self,
        name: str,
        path: str,
        tools: list[str] = None,
        readonly: bool = False
    ):
        """ワークスペースを追加"""
        ws_path = Path(path).expanduser().resolve()

        if not ws_path.exists():
            raise ValueError(f"パスが存在しません: {ws_path}")

        self.workspaces[name] = Workspace(
            name=name,
            path=ws_path,
            tools=tools or ["Read", "Glob", "Grep"],
            readonly=readonly
        )

    def get_options(self, workspace_name: str) -> ClaudeAgentOptions:
        """ワークスペースのオプションを取得"""
        ws = self.workspaces.get(workspace_name)

        if not ws:
            raise ValueError(f"ワークスペースが見つかりません: {workspace_name}")

        tools = ws.tools if ws.readonly else ws.tools + ["Write", "Edit"]

        return ClaudeAgentOptions(
            cwd=ws.path,
            allowed_tools=tools,
            system_prompt=f"ワークスペース '{ws.name}' で作業中"
        )

# 使用例
manager = WorkspaceManager()
manager.add_workspace("frontend", "~/projects/frontend", readonly=True)
manager.add_workspace("backend", "~/projects/backend", tools=["Read", "Write", "Edit", "Bash"])
```

### 2. ワークスペース間のファイルコピー

**コード:**

```python
import shutil
from pathlib import Path

class WorkspaceManager:
    # ... 上記のコード ...

    def copy_between_workspaces(
        self,
        source_ws: str,
        dest_ws: str,
        file_pattern: str
    ):
        """ワークスペース間でファイルをコピー"""
        src = self.workspaces[source_ws].path
        dst = self.workspaces[dest_ws].path

        for file in src.glob(file_pattern):
            relative = file.relative_to(src)
            dest_file = dst / relative
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file, dest_file)
            print(f"コピー: {relative}")
```

<div style="background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #155724; line-height: 1;">&#x2714;</span>
    <span style="font-weight: bold; color: #155724; font-size: 15px;">ポイント</span>
  </div>
  <div style="color: #155724; line-height: 1.6;">
    複数のプロジェクトを扱う場合は、ワークスペースマネージャーを使って整理すると、誤って別のプロジェクトを編集するリスクを減らせます。
  </div>
</div>

---

## 演習問題

### 演習1: プロジェクト自動検出

`package.json`, `pyproject.toml`, `Cargo.toml` などの設定ファイルを検出し、プロジェクトタイプに応じた最適なオプションを返す関数を作成してください。

### 演習2: ディレクトリ監視

ワークスペース内のファイル変更を監視し、変更があったファイルをログに記録する機能を実装してください。

### 演習3: バーチャルワークスペース

複数のディレクトリを1つの仮想ワークスペースとして扱えるクラスを作成してください。

---

## 次のステップ

オプション設定の全てを学習しました。次は [ビルトインツール概要](../03_tools/01_builtin_tools_overview.md) で、Claude が使用できるツールについて詳しく学びましょう。
