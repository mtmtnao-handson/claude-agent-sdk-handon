"""
サンドボックス実行 (一時ディレクトリ / Docker)

Usage:
    python 02_sandbox.py --mode temp --prompt "hello.py を作成して実行して"
    python 02_sandbox.py -m temp-copy -s ./src -p "コードを分析して改善して"
    python 02_sandbox.py -m docker -p "Python スクリプトを作成して実行して"

Available modes:
    temp      : 一時ディレクトリでサンドボックス実行
    temp-copy : ソースをコピーしてサンドボックス実行
    docker    : Docker コンテナでサンドボックス実行
"""
import argparse
import asyncio
import shutil
import tempfile
import os
from pathlib import Path
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage, TextBlock, ToolUseBlock


# =============================================================================
# 一時ディレクトリ サンドボックス
# =============================================================================

async def sandboxed_execution(prompt: str, source_dir: str = None):
    """一時ディレクトリでサンドボックス実行"""

    with tempfile.TemporaryDirectory() as tmp_dir:
        print(f"[サンドボックス] 一時ディレクトリ: {tmp_dir}")

        # ソースディレクトリがある場合はコピー
        if source_dir and Path(source_dir).exists():
            src_path = Path(source_dir)
            for item in src_path.iterdir():
                dest = Path(tmp_dir) / item.name
                if item.is_dir():
                    shutil.copytree(item, dest)
                else:
                    shutil.copy2(item, dest)
            print(f"  ソースをコピー: {source_dir} -> {tmp_dir}")

        options = ClaudeAgentOptions(
            cwd=tmp_dir,
            system_prompt=f"""
あなたは一時的なサンドボックス環境で作業しています。
作業ディレクトリ: {tmp_dir}
このディレクトリ外のファイルにはアクセスしないでください。
作成したファイルは実行終了後に削除されます。
""",
            allowed_tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep"],
            permission_mode="acceptEdits"
        )

        print("-" * 60)

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

        # 作成されたファイルを表示
        print("\n" + "=" * 60)
        print("作成されたファイル:")
        print("=" * 60)
        for root, dirs, files in os.walk(tmp_dir):
            for f in files:
                rel_path = Path(root) / f
                print(f"  {rel_path.relative_to(tmp_dir)}")


# =============================================================================
# Docker サンドボックス
# =============================================================================

async def docker_sandboxed_query(
    prompt: str,
    image: str = "python:3.11-slim",
    source_dir: str = None
):
    """Docker コンテナでサンドボックス実行"""

    # Docker が利用可能か確認
    docker_check = os.system("docker --version > /dev/null 2>&1")
    if docker_check != 0:
        print("[エラー] Docker がインストールされていないか、実行できません")
        return

    with tempfile.TemporaryDirectory() as tmp_dir:
        sandbox_path = Path(tmp_dir) / "sandbox"
        sandbox_path.mkdir()

        # ソースディレクトリがある場合はコピー
        if source_dir and Path(source_dir).exists():
            src_path = Path(source_dir)
            for item in src_path.iterdir():
                dest = sandbox_path / item.name
                if item.is_dir():
                    shutil.copytree(item, dest)
                else:
                    shutil.copy2(item, dest)
            print(f"  ソースをコピー: {source_dir}")

        print(f"[Docker サンドボックス]")
        print(f"  イメージ: {image}")
        print(f"  マウント: {sandbox_path}")

        # Docker コンテナを起動
        container_name = f"claude-sandbox-{os.getpid()}"
        start_cmd = f"docker run -d --name {container_name} -v {sandbox_path}:/workspace -w /workspace {image} sleep 3600"

        os.system(start_cmd)
        print(f"  コンテナ: {container_name}")

        try:
            options = ClaudeAgentOptions(
                cwd=str(sandbox_path),
                system_prompt=f"""
あなたは Docker コンテナ内のサンドボックス環境で作業しています。
作業ディレクトリ: /workspace (ホスト: {sandbox_path})
コンテナ名: {container_name}
イメージ: {image}

Bash コマンドを実行する場合は、`docker exec {container_name} <command>` を使用してください。
例: docker exec {container_name} python script.py
""",
                allowed_tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep"],
                permission_mode="acceptEdits"
            )

            print("-" * 60)

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

            # 作成されたファイルを表示
            print("\n" + "=" * 60)
            print("作成されたファイル:")
            print("=" * 60)
            for f in sandbox_path.iterdir():
                print(f"  {f.name}")

        finally:
            # コンテナを停止・削除
            os.system(f"docker stop {container_name} > /dev/null 2>&1")
            os.system(f"docker rm {container_name} > /dev/null 2>&1")
            print(f"\n[クリーンアップ] コンテナ {container_name} を削除しました")


# =============================================================================
# CLI
# =============================================================================

MODE_DESCRIPTIONS = {
    "temp": "一時ディレクトリでサンドボックス実行",
    "temp-copy": "ソースをコピーしてサンドボックス実行",
    "docker": "Docker コンテナでサンドボックス実行",
}


def parse_args() -> argparse.Namespace:
    """コマンドライン引数をパース"""
    parser = argparse.ArgumentParser(
        description="サンドボックス実行",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-m", "--mode",
        choices=list(MODE_DESCRIPTIONS.keys()),
        default="temp",
        help="実行モード (default: temp)"
    )
    parser.add_argument(
        "-p", "--prompt",
        default="hello.py を作成して実行してください",
        help="実行するプロンプト"
    )
    parser.add_argument(
        "-s", "--source",
        default="",
        help="コピーするソースディレクトリ"
    )
    parser.add_argument(
        "-i", "--image",
        default="python:3.11-slim",
        help="Docker イメージ (docker モード用)"
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
    print("サンドボックスモード一覧")
    print("=" * 60)

    for mode_name, desc in MODE_DESCRIPTIONS.items():
        print(f"\n[{mode_name}] {desc}")

    print("\n" + "-" * 60)
    print("使用例:")
    print("  python 02_sandbox.py -m temp -p 'hello.py を作成して実行して'")
    print("  python 02_sandbox.py -m temp-copy -s ./src -p 'コードを分析して'")
    print("  python 02_sandbox.py -m docker -i python:3.11 -p 'スクリプトを実行'")


async def main():
    """コマンドライン引数に基づいて実行"""
    args = parse_args()

    if args.list_modes:
        print_mode_details()
        return

    print("=" * 60)
    print(f"モード: {args.mode} ({MODE_DESCRIPTIONS[args.mode]})")
    print(f"プロンプト: {args.prompt}")
    print("=" * 60)

    if args.mode == "temp":
        await sandboxed_execution(args.prompt)
    elif args.mode == "temp-copy":
        await sandboxed_execution(args.prompt, args.source)
    elif args.mode == "docker":
        await docker_sandboxed_query(args.prompt, args.image, args.source)


if __name__ == "__main__":
    asyncio.run(main())
