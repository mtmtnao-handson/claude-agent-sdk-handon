# エラーハンドリング

## 概要

このセクションでは、Claude Agent SDK で発生する可能性のあるエラーの処理方法を学習します。

適切なエラーハンドリングを行うことで、堅牢なアプリケーションを構築できます。

---

## 手順1: SDK の例外階層

### 1. 例外クラスの構造

```
ClaudeSDKError (基底クラス)
├── CLINotFoundError      # Claude Code CLI が見つからない
├── CLIConnectionError    # CLI との接続エラー
├── ProcessError          # プロセス実行エラー
└── CLIJSONDecodeError    # JSON パースエラー
```

### 2. インポート

**コード:**

```python
from claude_agent_sdk import (
    ClaudeSDKError,
    CLINotFoundError,
    CLIConnectionError,
    ProcessError,
    CLIJSONDecodeError
)
```

---

## 手順2: 基本的なエラーハンドリング

### 1. try-except による例外処理

**コード:**

```python
import asyncio
from claude_agent_sdk import (
    query,
    ClaudeSDKError,
    CLINotFoundError,
    CLIConnectionError,
    ProcessError,
    CLIJSONDecodeError
)

async def safe_query(prompt: str):
    try:
        async for message in query(prompt=prompt):
            print(message)

    except CLINotFoundError:
        print("エラー: Claude Code CLI がインストールされていません")
        print("解決方法: brew install --cask claude-code")

    except CLIConnectionError as e:
        print(f"エラー: CLI との接続に失敗しました")
        print(f"詳細: {e}")

    except ProcessError as e:
        print(f"エラー: プロセスが異常終了しました")
        print(f"終了コード: {e.exit_code}")
        print(f"stderr: {e.stderr}")

    except CLIJSONDecodeError as e:
        print(f"エラー: レスポンスのパースに失敗しました")
        print(f"詳細: {e}")

    except ClaudeSDKError as e:
        print(f"SDK エラー: {e}")

asyncio.run(safe_query("Hello!"))
```

<div style="background-color: #f0f8ff; border: 1px solid #cce5ff; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #0d6efd; line-height: 1;">&#x24D8;</span>
    <span style="font-weight: bold; color: #0d6efd; font-size: 15px;">Note</span>
  </div>
  <div style="color: #454545; line-height: 1.6;">
    より具体的な例外を先にキャッチし、基底クラス <code>ClaudeSDKError</code> を最後にキャッチするのがベストプラクティスです。
  </div>
</div>

---

## 手順3: リトライロジックの実装

### 1. 指数バックオフ付きリトライ

**コード:**

```python
import asyncio
from claude_agent_sdk import (
    query,
    ClaudeSDKError,
    CLIConnectionError,
    ResultMessage
)

async def query_with_retry(
    prompt: str,
    max_retries: int = 3,
    base_delay: float = 1.0
):
    """指数バックオフ付きでクエリをリトライ"""

    for attempt in range(max_retries):
        try:
            results = []
            async for message in query(prompt=prompt):
                results.append(message)
            # ループ完了後に成功を報告して結果を返す
            print(f"成功 (試行 {attempt + 1}/{max_retries})")
            return results

        except CLIConnectionError as e:
            delay = base_delay * (2 ** attempt)  # 指数バックオフ
            print(f"接続エラー (試行 {attempt + 1}/{max_retries})")
            print(f"{delay}秒後にリトライします...")

            if attempt < max_retries - 1:
                await asyncio.sleep(delay)
            else:
                raise

        except ClaudeSDKError:
            # その他のSDKエラーはリトライしない
            raise

    raise Exception("最大リトライ回数を超えました")

async def main():
    try:
        results = await query_with_retry("Hello, Claude!")
        print(f"取得メッセージ数: {len(results)}")
    except Exception as e:
        print(f"最終的に失敗: {e}")

asyncio.run(main())
```

---

## 手順4: タイムアウトの設定

### 1. asyncio.timeout を使用

**コード:**

```python
import asyncio
from claude_agent_sdk import query, ResultMessage

async def query_with_timeout(prompt: str, timeout_seconds: float = 30.0):
    """タイムアウト付きでクエリを実行"""

    try:
        async with asyncio.timeout(timeout_seconds):
            results = []
            async for message in query(prompt=prompt):
                results.append(message)
            return results

    except asyncio.TimeoutError:
        print(f"タイムアウト: {timeout_seconds}秒を超えました")
        return None

async def main():
    # 短いタイムアウトでテスト
    result = await query_with_timeout("大量のデータを分析して", timeout_seconds=5.0)

    if result is None:
        print("処理がタイムアウトしました。より長い時間を設定してください。")
    else:
        print(f"正常完了: {len(result)} メッセージ")

asyncio.run(main())
```

<div style="background-color: #fff3cd; border: 1px solid #ffc107; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #856404; line-height: 1;">&#x26A0;</span>
    <span style="font-weight: bold; color: #856404; font-size: 15px;">注意</span>
  </div>
  <div style="color: #454545; line-height: 1.6;">
    <code>asyncio.timeout()</code> は Python 3.11 以上で使用できます。3.10 では <code>asyncio.wait_for()</code> を使用してください。
  </div>
</div>

---

## 手順5: カスタム例外ハンドラー

### 1. エラーハンドラークラス

**コード:**

```python
import asyncio
from abc import ABC, abstractmethod
from claude_agent_sdk import (
    query,
    ClaudeSDKError,
    CLINotFoundError,
    CLIConnectionError,
    ProcessError
)

class ErrorHandler(ABC):
    @abstractmethod
    async def handle(self, error: Exception) -> bool:
        """エラーを処理し、リトライすべきかを返す"""
        pass

class LoggingErrorHandler(ErrorHandler):
    def __init__(self, log_file: str = "errors.log"):
        self.log_file = log_file

    async def handle(self, error: Exception) -> bool:
        with open(self.log_file, "a") as f:
            f.write(f"{type(error).__name__}: {error}\n")

        if isinstance(error, CLIConnectionError):
            return True  # リトライ可能
        return False  # リトライ不可

class NotificationErrorHandler(ErrorHandler):
    async def handle(self, error: Exception) -> bool:
        # 重大なエラーの場合は通知（例: Slack, Email）
        if isinstance(error, CLINotFoundError):
            print(f"[CRITICAL] CLI未インストール: {error}")
            # await send_slack_notification(str(error))
        return False

async def query_with_handlers(
    prompt: str,
    handlers: list[ErrorHandler]
):
    try:
        async for message in query(prompt=prompt):
            yield message

    except ClaudeSDKError as e:
        should_retry = False
        for handler in handlers:
            if await handler.handle(e):
                should_retry = True

        if not should_retry:
            raise

async def main():
    handlers = [
        LoggingErrorHandler(),
        NotificationErrorHandler()
    ]

    async for message in query_with_handlers("Hello!", handlers):
        print(message)

asyncio.run(main())
```

---

## 手順6: コンテキストマネージャーによるリソース管理

### 1. クリーンアップを保証する

**コード:**

```python
import asyncio
from contextlib import asynccontextmanager
from claude_agent_sdk import query, ClaudeSDKError, ResultMessage

@asynccontextmanager
async def managed_query(prompt: str):
    """クエリ実行をラップし、リソース管理とエラーハンドリングを提供"""

    results = []
    error = None

    try:
        async for message in query(prompt=prompt):
            results.append(message)
        yield results

    except ClaudeSDKError as e:
        error = e
        yield []  # 空の結果を返す

    finally:
        # クリーンアップ処理
        if error:
            print(f"エラーが発生しました: {error}")

        # コスト情報を出力
        for msg in results:
            if isinstance(msg, ResultMessage):
                print(f"セッション {msg.session_id} 完了 (${msg.total_cost_usd:.4f})")

async def main():
    async with managed_query("簡単なPython関数を書いて") as results:
        for msg in results:
            print(msg)

asyncio.run(main())
```

---

## 手順7: デバッグとトラブルシューティング

### 1. 詳細なエラー情報の取得

**コード:**

```python
import asyncio
import traceback
from claude_agent_sdk import query, ClaudeSDKError

async def debug_query(prompt: str):
    try:
        async for message in query(prompt=prompt):
            print(f"[DEBUG] {type(message).__name__}")

    except ClaudeSDKError as e:
        print("=== エラー詳細 ===")
        print(f"例外クラス: {type(e).__name__}")
        print(f"メッセージ: {e}")
        print(f"引数: {e.args}")
        print("\n=== スタックトレース ===")
        traceback.print_exc()

        # ProcessError の場合は追加情報
        if hasattr(e, 'exit_code'):
            print(f"\n終了コード: {e.exit_code}")
        if hasattr(e, 'stderr'):
            print(f"標準エラー: {e.stderr}")

asyncio.run(debug_query("テストプロンプト"))
```

### 2. ヘルスチェック関数

**コード:**

```python
import asyncio
from claude_agent_sdk import query, CLINotFoundError, ResultMessage

async def health_check() -> dict:
    """SDK の動作状態をチェック"""

    status = {
        "cli_available": False,
        "api_connection": False,
        "response_time_ms": None,
        "error": None
    }

    import time
    start = time.time()

    try:
        async for message in query(prompt="ping"):
            if isinstance(message, ResultMessage):
                status["cli_available"] = True
                status["api_connection"] = True
                status["response_time_ms"] = (time.time() - start) * 1000

    except CLINotFoundError:
        status["error"] = "Claude Code CLI not installed"
    except Exception as e:
        status["cli_available"] = True  # CLI はあるがAPI接続失敗
        status["error"] = str(e)

    return status

async def main():
    print("ヘルスチェック実行中...")
    result = await health_check()

    print(f"\nCLI 利用可能: {result['cli_available']}")
    print(f"API 接続: {result['api_connection']}")

    if result['response_time_ms']:
        print(f"応答時間: {result['response_time_ms']:.0f}ms")

    if result['error']:
        print(f"エラー: {result['error']}")

asyncio.run(main())
```

<div style="background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #155724; line-height: 1;">&#x2714;</span>
    <span style="font-weight: bold; color: #155724; font-size: 15px;">ポイント</span>
  </div>
  <div style="color: #155724; line-height: 1.6;">
    本番環境では、アプリケーション起動時にヘルスチェックを実行し、必要なコンポーネントが利用可能か確認しましょう。
  </div>
</div>

---

## 演習問題

### 演習1: 堅牢なクエリ関数

以下の機能を持つクエリ関数を作成してください：

- 最大3回のリトライ
- タイムアウト設定
- エラーログ記録
- 成功/失敗を示す Result 型の返却

### 演習2: サーキットブレーカーパターン

連続したエラーが発生した場合に、一定時間クエリを停止するサーキットブレーカーを実装してください。

### 演習3: エラー通知システム

重大なエラーが発生した場合に、外部サービス（Slack、Email など）に通知するシステムを作成してください。

---

## 次のステップ

エラーハンドリングを習得しました。次は [ClaudeSDKClient](04_claude_sdk_client.md) で、継続的な会話とセッション管理を学びましょう。
