"""
基本的な query() 関数の使い方
"""
import asyncio
from claude_agent_sdk import query


async def main():
    """最もシンプルな query() の例"""
    async for message in query(prompt="Hello, Claude!"):
        print(message)


if __name__ == "__main__":
    asyncio.run(main())
