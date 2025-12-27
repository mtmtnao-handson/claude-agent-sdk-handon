"""
working_directory (cwd) の基本的な使い方

Usage:
    python 01_basic.py --mode basic --prompt "このプロジェクトの構造を確認して"
    python 01_basic.py -m project -n my-app -p "package.json を確認して"
    python 01_basic.py -m auto-detect -p "このリポジトリを分析して"

Available modes:
    basic       : 基本的な cwd 設定
    project     : プロジェクト別の設定
    auto-detect : Git ルートの自動検出
"""
import argparse
import asyncio
import subprocess
from pathlib import Path
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage, TextBlock, ToolUseBlock


# =============================================================================
# 基本設定
# =============================================================================

def create_basic_options(cwd: str) -> ClaudeAgentOptions:
    """基本的な cwd 設定"""
    return ClaudeAgentOptions(
        cwd=cwd,
        allowed_tools=["Read", "Glob", "Grep"]
    )


def create_path_options(cwd: Path) -> ClaudeAgentOptions:
    """Path オブジェクトを使用した cwd 設定"""
    return ClaudeAgentOptions(
        cwd=str(cwd),
        allowed_tools=["Read", "Glob", "Grep"]
    )


# =============================================================================
# プロジェクト管理
# =============================================================================

class ProjectManager:
    """複数プロジェクトを管理するクラス"""

    def __init__(self, base_path: str = "~/projects"):
        self.base_path = Path(base_path).expanduser()

    def get_project_path(self, project_name: str) -> Path:
        """プロジェクトパスを取得"""
        return self.base_path / project_name

    def get_options(self, project_name: str) -> ClaudeAgentOptions:
        """プロジェクト用のオプションを取得"""
        project_path = self.get_project_path(project_name)

        if not project_path.exists():
            raise ValueError(f"プロジェクトが見つかりません: {project_path}")

        return ClaudeAgentOptions(
            cwd=str(project_path),
            system_prompt=f"プロジェクト '{project_name}' で作業しています。",
            allowed_tools=["Read", "Write", "Edit", "Glob", "Grep"]
        )

    def list_projects(self) -> list[str]:
        """利用可能なプロジェクトを一覧"""
        if not self.base_path.exists():
            return []
        return [d.name for d in self.base_path.iterdir() if d.is_dir()]


# =============================================================================
# Git ルート自動検出
# =============================================================================

def detect_git_root(start_path: Path = None) -> Path | None:
    """Git リポジトリのルートを検出"""
    if start_path is None:
        start_path = Path.cwd()

    current = start_path.resolve()

    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent

    return None


def detect_project_root() -> Path:
    """プロジェクトルートを検出（Git、または特定のファイルから）"""
    # Git リポジトリを検索
    git_root = detect_git_root()
    if git_root:
        return git_root

    # package.json や pyproject.toml を検索
    current = Path.cwd()
    project_files = ["package.json", "pyproject.toml", "Cargo.toml", "go.mod"]

    while current != current.parent:
        for pf in project_files:
            if (current / pf).exists():
                return current
        current = current.parent

    # 見つからなければカレントディレクトリを返す
    return Path.cwd()


def get_auto_options() -> ClaudeAgentOptions:
    """プロジェクトルートを自動検出してオプションを返す"""
    project_root = detect_project_root()

    return ClaudeAgentOptions(
        cwd=str(project_root),
        system_prompt=f"プロジェクトルート: {project_root}",
        allowed_tools=["Read", "Glob", "Grep", "Bash"]
    )


# =============================================================================
# モード定義
# =============================================================================

MODE_DESCRIPTIONS = {
    "basic": "基本的な cwd 設定",
    "project": "プロジェクト別の設定",
    "auto-detect": "Git ルートの自動検出",
}


def parse_args() -> argparse.Namespace:
    """コマンドライン引数をパース"""
    parser = argparse.ArgumentParser(
        description="working_directory (cwd) の基本的な使い方",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-m", "--mode",
        choices=list(MODE_DESCRIPTIONS.keys()),
        default="basic",
        help="実行モード (default: basic)"
    )
    parser.add_argument(
        "-p", "--prompt",
        default="このディレクトリの構造を確認してください",
        help="実行するプロンプト"
    )
    parser.add_argument(
        "-n", "--project-name",
        default="",
        help="プロジェクト名 (project モード用)"
    )
    parser.add_argument(
        "-d", "--directory",
        default=".",
        help="作業ディレクトリ (basic モード用)"
    )
    parser.add_argument(
        "-l", "--list-modes",
        action="store_true",
        help="利用可能なモードの詳細を表示して終了"
    )
    return parser.parse_args()


def print_mode_details():
    """全モードの詳細を表示"""
    print("=" * 60)
    print("利用可能なモード一覧")
    print("=" * 60)

    for mode_name, desc in MODE_DESCRIPTIONS.items():
        print(f"\n[{mode_name}] {desc}")

    # 現在のプロジェクトルートを表示
    print("\n" + "-" * 60)
    print("現在の環境:")
    print(f"  カレントディレクトリ: {Path.cwd()}")
    git_root = detect_git_root()
    if git_root:
        print(f"  Git ルート: {git_root}")
    project_root = detect_project_root()
    print(f"  検出されたプロジェクトルート: {project_root}")


async def run_basic_mode(prompt: str, directory: str):
    """基本モードで実行"""
    cwd = Path(directory).resolve()
    print(f"[基本モード] cwd: {cwd}")
    print("-" * 60)

    options = create_basic_options(str(cwd))

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"[Text] {block.text}")
                elif isinstance(block, ToolUseBlock):
                    print(f"[Tool] {block.name}: {str(block.input)[:80]}...")
        elif isinstance(message, ResultMessage):
            if message.subtype == "success":
                print(f"完了: {message.result}")


async def run_project_mode(prompt: str, project_name: str):
    """プロジェクトモードで実行"""
    manager = ProjectManager()

    if not project_name:
        print("[プロジェクトモード] プロジェクト名が指定されていません")
        projects = manager.list_projects()
        if projects:
            print(f"利用可能なプロジェクト: {projects}")
        else:
            print(f"ベースパス {manager.base_path} にプロジェクトがありません")
        return

    try:
        options = manager.get_options(project_name)
        print(f"[プロジェクトモード] プロジェクト: {project_name}")
        print(f"  cwd: {options.cwd}")
        print("-" * 60)

        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"[Text] {block.text}")
                    elif isinstance(block, ToolUseBlock):
                        print(f"[Tool] {block.name}")
            elif isinstance(message, ResultMessage):
                if message.subtype == "success":
                    print(f"完了: {message.result}")

    except ValueError as e:
        print(f"エラー: {e}")


async def run_auto_detect_mode(prompt: str):
    """自動検出モードで実行"""
    options = get_auto_options()
    print(f"[自動検出モード] 検出された cwd: {options.cwd}")
    print("-" * 60)

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"[Text] {block.text}")
                elif isinstance(block, ToolUseBlock):
                    print(f"[Tool] {block.name}: {str(block.input)[:80]}...")
        elif isinstance(message, ResultMessage):
            if message.subtype == "success":
                print(f"完了: {message.result}")


async def main():
    """コマンドライン引数に基づいて実行"""
    args = parse_args()

    if args.list_modes:
        print_mode_details()
        return

    print("=" * 60)
    print(f"プロンプト: {args.prompt}")
    print("=" * 60)

    if args.mode == "basic":
        await run_basic_mode(args.prompt, args.directory)
    elif args.mode == "project":
        await run_project_mode(args.prompt, args.project_name)
    elif args.mode == "auto-detect":
        await run_auto_detect_mode(args.prompt)


if __name__ == "__main__":
    asyncio.run(main())
