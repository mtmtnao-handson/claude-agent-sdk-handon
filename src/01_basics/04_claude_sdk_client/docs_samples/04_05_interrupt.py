"""
割り込み機能 - 長い応答を中断する
"""
import asyncio
from claude_agent_sdk import ClaudeSDKClient
from claude_agent_sdk.types import AssistantMessage, ResultMessage, TextBlock


async def with_interrupt():
    async with ClaudeSDKClient() as client:
        await client.query("1から100までの数字をそれぞれ説明してください")

        async def timer_interrupt(delay: float):
            """指定秒数後に割り込みを実行"""
            await asyncio.sleep(delay)
            print(f"\n[タイマー割り込み実行: {delay}秒経過]")
            await client.interrupt()

        # 3秒後に割り込みするタイマーを開始
        timer_task = asyncio.create_task(timer_interrupt(15.0))

        try:
            async for message in client.receive_messages():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            print(block.text, end="", flush=True)

                # ResultMessage を受信したらループを終了
                if isinstance(message, ResultMessage):
                    print(f"\n[終了: {message.subtype}]")
                    break
        finally:
            # タイマーがまだ動いていたらキャンセル
            if not timer_task.done():
                timer_task.cancel()


asyncio.run(with_interrupt())
