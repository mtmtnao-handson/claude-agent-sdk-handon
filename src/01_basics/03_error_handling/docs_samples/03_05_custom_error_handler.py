"""
カスタム例外ハンドラー - エラーハンドラークラス
"""
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
