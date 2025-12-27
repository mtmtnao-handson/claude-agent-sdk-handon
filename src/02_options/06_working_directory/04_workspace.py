"""
ワークスペース管理

Usage:
    python 04_workspace.py --list-workspaces
    python 04_workspace.py -w main -p "プロジェクトを分析して"
    python 04_workspace.py --copy main output "*.py"

Available commands:
    -w, --workspace : 指定したワークスペースで実行
    --list-workspaces : 登録されているワークスペースを一覧表示
    --copy            : ワークスペース間でファイルをコピー
"""
import argparse
import asyncio
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage, TextBlock, ToolUseBlock


# =============================================================================
# ワークスペース定義
# =============================================================================

@dataclass
class Workspace:
    """ワークスペース設定"""
    name: str
    path: Path
    tools: list[str] = field(default_factory=lambda: ["Read", "Glob", "Grep"])
    readonly: bool = False
    description: str = ""

    def __post_init__(self):
        if isinstance(self.path, str):
            self.path = Path(self.path).expanduser().resolve()


# =============================================================================
# ワークスペースマネージャー
# =============================================================================

class WorkspaceManager:
    """複数ワークスペースを管理するクラス"""

    def __init__(self):
        self.workspaces: dict[str, Workspace] = {}

    def add_workspace(
        self,
        name: str,
        path: str | Path,
        tools: list[str] = None,
        readonly: bool = False,
        description: str = ""
    ) -> Workspace:
        """ワークスペースを追加"""
        ws = Workspace(
            name=name,
            path=Path(path).expanduser().resolve(),
            tools=tools or ["Read", "Glob", "Grep"],
            readonly=readonly,
            description=description
        )
        self.workspaces[name] = ws
        return ws

    def get_workspace(self, name: str) -> Workspace | None:
        """ワークスペースを取得"""
        return self.workspaces.get(name)

    def list_workspaces(self) -> list[Workspace]:
        """全ワークスペースを一覧"""
        return list(self.workspaces.values())

    def get_options(self, workspace_name: str) -> ClaudeAgentOptions:
        """ワークスペース用のオプションを取得"""
        ws = self.get_workspace(workspace_name)
        if not ws:
            raise ValueError(f"ワークスペースが見つかりません: {workspace_name}")

        mode_text = "読み取り専用" if ws.readonly else "読み書き可能"

        return ClaudeAgentOptions(
            cwd=str(ws.path),
            system_prompt=f"""
ワークスペース: {ws.name}
パス: {ws.path}
モード: {mode_text}
説明: {ws.description or 'なし'}
""",
            allowed_tools=ws.tools
        )

    def copy_between_workspaces(
        self,
        source_ws: str,
        dest_ws: str,
        file_pattern: str = "*"
    ) -> list[Path]:
        """ワークスペース間でファイルをコピー"""
        source = self.get_workspace(source_ws)
        dest = self.get_workspace(dest_ws)

        if not source:
            raise ValueError(f"ソースワークスペースが見つかりません: {source_ws}")
        if not dest:
            raise ValueError(f"宛先ワークスペースが見つかりません: {dest_ws}")
        if dest.readonly:
            raise ValueError(f"宛先ワークスペースは読み取り専用です: {dest_ws}")

        copied_files = []
        for src_file in source.path.glob(file_pattern):
            if src_file.is_file():
                dest_file = dest.path / src_file.name
                shutil.copy2(src_file, dest_file)
                copied_files.append(dest_file)

        return copied_files


# =============================================================================
# デフォルトワークスペース設定
# =============================================================================

def create_default_manager() -> WorkspaceManager:
    """デフォルトのワークスペースマネージャーを作成"""
    manager = WorkspaceManager()

    # 現在のディレクトリをメインワークスペースとして追加
    cwd = Path.cwd()
    manager.add_workspace(
        name="main",
        path=cwd,
        tools=["Read", "Write", "Edit", "Glob", "Grep"],
        readonly=False,
        description="メインの作業ディレクトリ"
    )

    # 読み取り専用のアーカイブワークスペース
    archive_path = cwd / "archive"
    if archive_path.exists():
        manager.add_workspace(
            name="archive",
            path=archive_path,
            tools=["Read", "Glob", "Grep"],
            readonly=True,
            description="アーカイブ（読み取り専用）"
        )

    # 出力用ワークスペース
    output_path = cwd / "output"
    output_path.mkdir(exist_ok=True)
    manager.add_workspace(
        name="output",
        path=output_path,
        tools=["Read", "Write", "Glob", "Grep"],
        readonly=False,
        description="出力ファイル用"
    )

    # src ディレクトリがあれば追加
    src_path = cwd / "src"
    if src_path.exists():
        manager.add_workspace(
            name="src",
            path=src_path,
            tools=["Read", "Glob", "Grep"],
            readonly=True,
            description="ソースコード（読み取り専用）"
        )

    return manager


# =============================================================================
# CLI
# =============================================================================

def parse_args() -> argparse.Namespace:
    """コマンドライン引数をパース"""
    parser = argparse.ArgumentParser(
        description="ワークスペース管理",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-w", "--workspace",
        default="main",
        help="使用するワークスペース名"
    )
    parser.add_argument(
        "-p", "--prompt",
        default="このワークスペースの内容を確認してください",
        help="実行するプロンプト"
    )
    parser.add_argument(
        "--list-workspaces",
        action="store_true",
        help="登録されているワークスペースを一覧表示"
    )
    parser.add_argument(
        "--copy",
        nargs=3,
        metavar=("SOURCE", "DEST", "PATTERN"),
        help="ワークスペース間でファイルをコピー"
    )
    parser.add_argument(
        "--add-workspace",
        nargs=2,
        metavar=("NAME", "PATH"),
        help="新しいワークスペースを追加"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="詳細出力モード"
    )
    return parser.parse_args()


def print_workspaces(manager: WorkspaceManager):
    """ワークスペース一覧を表示"""
    print("=" * 60)
    print("登録されているワークスペース")
    print("=" * 60)

    for ws in manager.list_workspaces():
        mode = "RO" if ws.readonly else "RW"
        exists = "OK" if ws.path.exists() else "NOT FOUND"
        print(f"\n[{ws.name}] ({mode}) - {exists}")
        print(f"  パス: {ws.path}")
        print(f"  ツール: {ws.tools}")
        if ws.description:
            print(f"  説明: {ws.description}")


async def run_workspace(manager: WorkspaceManager, workspace_name: str, prompt: str, verbose: bool):
    """指定したワークスペースでクエリを実行"""
    try:
        ws = manager.get_workspace(workspace_name)
        if not ws:
            print(f"[エラー] ワークスペースが見つかりません: {workspace_name}")
            return

        options = manager.get_options(workspace_name)

        mode_text = "読み取り専用" if ws.readonly else "読み書き可能"
        print(f"[ワークスペース: {workspace_name}]")
        print(f"  パス: {ws.path}")
        print(f"  モード: {mode_text}")
        print(f"  ツール: {ws.tools}")
        print("-" * 60)
        print(f"プロンプト: {prompt}")
        print("-" * 60)

        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"[Text] {block.text}")
                    elif isinstance(block, ToolUseBlock):
                        if verbose:
                            print(f"[Tool] {block.name}: {block.input}")
                        else:
                            print(f"[Tool] {block.name}")
            elif isinstance(message, ResultMessage):
                if message.subtype == "success":
                    print(f"完了: {message.result}")

    except ValueError as e:
        print(f"[エラー] {e}")


def copy_files(manager: WorkspaceManager, source: str, dest: str, pattern: str):
    """ワークスペース間でファイルをコピー"""
    print(f"[コピー] {source} -> {dest} (パターン: {pattern})")
    print("-" * 60)

    try:
        copied = manager.copy_between_workspaces(source, dest, pattern)
        print(f"コピーされたファイル: {len(copied)} 件")
        for f in copied:
            print(f"  - {f.name}")
    except ValueError as e:
        print(f"[エラー] {e}")


async def main():
    """コマンドライン引数に基づいて実行"""
    args = parse_args()

    # デフォルトのマネージャーを作成
    manager = create_default_manager()

    # 新しいワークスペースを追加
    if args.add_workspace:
        name, path = args.add_workspace
        manager.add_workspace(name=name, path=path)
        print(f"ワークスペース '{name}' を追加しました: {path}")

    # ワークスペース一覧を表示
    if args.list_workspaces:
        print_workspaces(manager)
        return

    # ファイルコピー
    if args.copy:
        source, dest, pattern = args.copy
        copy_files(manager, source, dest, pattern)
        return

    # ワークスペースでクエリを実行
    print("=" * 60)
    await run_workspace(manager, args.workspace, args.prompt, args.verbose)


if __name__ == "__main__":
    asyncio.run(main())
