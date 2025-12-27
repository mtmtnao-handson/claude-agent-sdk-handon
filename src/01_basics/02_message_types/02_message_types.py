"""
メッセージ型の処理
"""
import asyncio
from claude_agent_sdk import query, AssistantMessage, ResultMessage, TextBlock, ToolUseBlock


async def main():
    """メッセージ型による分岐処理"""
    async for message in query(prompt="現在のディレクトリのファイル一覧を表示してください"):
        if isinstance(message, AssistantMessage):
            print("=== AssistantMessage ===")
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"[Text] {block.text}")
                elif isinstance(block, ToolUseBlock):
                    print(f"[Tool] {block.name}: {block.input}")

        elif isinstance(message, ResultMessage):
            print("=== ResultMessage ===")
            # subtype をチェックしてからメンバ変数にアクセス
            if message.subtype == "success":
                print(f"セッションID: {message.result}")
            else:
                print(f"subtype: {message.subtype}")

if __name__ == "__main__":
    asyncio.run(main())
