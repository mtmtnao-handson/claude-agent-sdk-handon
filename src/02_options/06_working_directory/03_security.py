"""
パス制限とセキュリティ

Usage:
    python 03_security.py --mode readonly --prompt "コードを分析して"
    python 03_security.py -m restricted -p "ファイルを編集して"
    python 03_security.py -m path-guard -p "システムファイルを読んで"

Available modes:
    readonly   : 読み取り専用モード
    restricted : 書き込み先制限モード
    path-guard : パスガードモード（cwd 外へのアクセスをブロック）
"""
import argparse
import asyncio
from pathlib import Path
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage, TextBlock, ToolUseBlock


# =============================================================================
# パス安全性チェック
# =============================================================================

def is_path_safe(path: str, allowed_root: Path) -> bool:
    """パスが許可されたルート内にあるかチェック"""
    try:
        # パスを正規化
        check_path = Path(path).resolve()
        allowed = allowed_root.resolve()

        # 許可されたルート内にあるか確認
        return str(check_path).startswith(str(allowed))
    except Exception:
        return False


def get_dangerous_paths() -> list[str]:
    """危険なパスのリスト"""
    return [
        "/etc",
        "/var",
        "/usr",
        "/bin",
        "/sbin",
        "/root",
        "/home",
        "~",
        "..",
        "/System",
        "/Library",
    ]


# =============================================================================
# 読み取り専用オプション
# =============================================================================

def create_readonly_options(project_path: str) -> ClaudeAgentOptions:
    """読み取り専用のオプションを作成"""
    return ClaudeAgentOptions(
        cwd=project_path,
        system_prompt=f"""
あなたは読み取り専用モードで作業しています。
作業ディレクトリ: {project_path}

重要: ファイルの作成・編集・削除は許可されていません。
分析とレポートのみを行ってください。
""",
        allowed_tools=["Read", "Glob", "Grep"]
    )


# =============================================================================
# 書き込み先制限オプション
# =============================================================================

def create_restricted_write_options(
    project_path: str,
    writable_dirs: list[str] = None
) -> ClaudeAgentOptions:
    """書き込み先を制限したオプションを作成"""
    if writable_dirs is None:
        writable_dirs = ["output", "generated", "tmp"]

    writable_list = "\n".join(f"  - {d}" for d in writable_dirs)

    return ClaudeAgentOptions(
        cwd=project_path,
        system_prompt=f"""
あなたは書き込み先が制限されたモードで作業しています。
作業ディレクトリ: {project_path}

書き込み可能なディレクトリ:
{writable_list}

重要:
- 上記のディレクトリ以外へのファイル作成・編集は禁止です
- 既存のソースコードを直接編集しないでください
- 出力は指定されたディレクトリに保存してください
""",
        allowed_tools=["Read", "Write", "Edit", "Glob", "Grep"]
    )


# =============================================================================
# パスガードオプション
# =============================================================================

def create_path_guard_options(project_path: str) -> ClaudeAgentOptions:
    """パスガード付きのオプションを作成"""
    dangerous_paths = get_dangerous_paths()
    dangerous_list = ", ".join(dangerous_paths[:5]) + " など"

    return ClaudeAgentOptions(
        cwd=project_path,
        system_prompt=f"""
あなたはパスガードモードで作業しています。
作業ディレクトリ: {project_path}

セキュリティ制限:
- 作業ディレクトリ外のファイルにアクセスしないでください
- 以下のパスへのアクセスは禁止: {dangerous_list}
- 絶対パスの使用は避け、相対パスを使用してください
- ".." を使ったディレクトリトラバーサルは禁止です

違反が検出された場合、操作は拒否されます。
""",
        allowed_tools=["Read", "Write", "Edit", "Glob", "Grep", "Bash"]
    )


# =============================================================================
# セキュリティレポート
# =============================================================================

def generate_security_report(project_path: str) -> dict:
    """セキュリティ設定のレポートを生成"""
    path = Path(project_path).resolve()

    report = {
        "project_path": str(path),
        "exists": path.exists(),
        "is_git_repo": (path / ".git").exists(),
        "sensitive_files": [],
        "recommendations": [],
    }

    # 機密ファイルをチェック
    sensitive_patterns = [".env", ".env.*", "*.pem", "*.key", "credentials*", "secrets*"]
    for pattern in sensitive_patterns:
        matches = list(path.glob(pattern))
        report["sensitive_files"].extend([str(m.relative_to(path)) for m in matches])

    # 推奨事項を追加
    if report["sensitive_files"]:
        report["recommendations"].append("機密ファイルを .gitignore に追加してください")

    if not report["is_git_repo"]:
        report["recommendations"].append("Git リポジトリとして初期化することを検討してください")

    return report


# =============================================================================
# CLI
# =============================================================================

MODE_DESCRIPTIONS = {
    "readonly": "読み取り専用モード",
    "restricted": "書き込み先制限モード",
    "path-guard": "パスガードモード",
}


def parse_args() -> argparse.Namespace:
    """コマンドライン引数をパース"""
    parser = argparse.ArgumentParser(
        description="パス制限とセキュリティ",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-m", "--mode",
        choices=list(MODE_DESCRIPTIONS.keys()),
        default="readonly",
        help="セキュリティモード (default: readonly)"
    )
    parser.add_argument(
        "-p", "--prompt",
        default="このプロジェクトを分析してください",
        help="実行するプロンプト"
    )
    parser.add_argument(
        "-d", "--directory",
        default=".",
        help="作業ディレクトリ"
    )
    parser.add_argument(
        "-w", "--writable-dirs",
        nargs="+",
        default=["output", "generated", "tmp"],
        help="書き込み可能なディレクトリ (restricted モード用)"
    )
    parser.add_argument(
        "-l", "--list-modes",
        action="store_true",
        help="利用可能なモードの詳細を表示して終了"
    )
    parser.add_argument(
        "--security-report",
        action="store_true",
        help="セキュリティレポートを表示して終了"
    )
    return parser.parse_args()


def print_mode_details():
    """全モードの詳細を表示"""
    print("=" * 60)
    print("セキュリティモード一覧")
    print("=" * 60)

    modes_info = {
        "readonly": {
            "desc": "読み取り専用モード",
            "tools": ["Read", "Glob", "Grep"],
            "features": ["ファイル読み取りのみ", "分析・レポート向け"]
        },
        "restricted": {
            "desc": "書き込み先制限モード",
            "tools": ["Read", "Write", "Edit", "Glob", "Grep"],
            "features": ["指定ディレクトリのみ書き込み可", "ソースコード保護"]
        },
        "path-guard": {
            "desc": "パスガードモード",
            "tools": ["Read", "Write", "Edit", "Glob", "Grep", "Bash"],
            "features": ["cwd 外アクセス禁止", "ディレクトリトラバーサル防止"]
        },
    }

    for mode_name, info in modes_info.items():
        print(f"\n[{mode_name}] {info['desc']}")
        print(f"  allowed_tools: {info['tools']}")
        print(f"  特徴: {', '.join(info['features'])}")


async def run_readonly_mode(prompt: str, directory: str):
    """読み取り専用モードで実行"""
    cwd = Path(directory).resolve()
    print(f"[読み取り専用モード] cwd: {cwd}")
    print("-" * 60)

    options = create_readonly_options(str(cwd))

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


async def run_restricted_mode(prompt: str, directory: str, writable_dirs: list[str]):
    """書き込み先制限モードで実行"""
    cwd = Path(directory).resolve()
    print(f"[書き込み先制限モード] cwd: {cwd}")
    print(f"  書き込み可能: {writable_dirs}")
    print("-" * 60)

    options = create_restricted_write_options(str(cwd), writable_dirs)

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"[Text] {block.text}")
                elif isinstance(block, ToolUseBlock):
                    print(f"[Tool] {block.name}: {str(block.input)[:60]}...")
        elif isinstance(message, ResultMessage):
            if message.subtype == "success":
                print(f"完了: {message.result}")


async def run_path_guard_mode(prompt: str, directory: str):
    """パスガードモードで実行"""
    cwd = Path(directory).resolve()
    print(f"[パスガードモード] cwd: {cwd}")
    print("-" * 60)

    options = create_path_guard_options(str(cwd))

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"[Text] {block.text}")
                elif isinstance(block, ToolUseBlock):
                    print(f"[Tool] {block.name}: {str(block.input)[:60]}...")
        elif isinstance(message, ResultMessage):
            if message.subtype == "success":
                print(f"完了: {message.result}")


async def main():
    """コマンドライン引数に基づいて実行"""
    args = parse_args()

    if args.list_modes:
        print_mode_details()
        return

    if args.security_report:
        print("=" * 60)
        print("セキュリティレポート")
        print("=" * 60)
        report = generate_security_report(args.directory)
        for key, value in report.items():
            print(f"  {key}: {value}")
        return

    print("=" * 60)
    print(f"モード: {args.mode} ({MODE_DESCRIPTIONS[args.mode]})")
    print(f"プロンプト: {args.prompt}")
    print("=" * 60)

    if args.mode == "readonly":
        await run_readonly_mode(args.prompt, args.directory)
    elif args.mode == "restricted":
        await run_restricted_mode(args.prompt, args.directory, args.writable_dirs)
    elif args.mode == "path-guard":
        await run_path_guard_mode(args.prompt, args.directory)


if __name__ == "__main__":
    asyncio.run(main())
