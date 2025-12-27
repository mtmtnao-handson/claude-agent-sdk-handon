import asyncio
from claude_agent_sdk import query, AssistantMessage, TextBlock

async def analyze_code():
    code = '''
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
'''

    prompt = f"""
以下のPythonコードを分析し、以下の観点から説明してください：
1. 何をする関数か
2. 時間計算量
3. 潜在的な問題点

コード:
{code}
"""

    async for message in query(prompt=prompt):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)

asyncio.run(analyze_code())
