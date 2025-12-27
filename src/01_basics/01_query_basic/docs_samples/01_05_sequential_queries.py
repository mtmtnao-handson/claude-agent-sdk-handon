import asyncio
from claude_agent_sdk import query, AssistantMessage, TextBlock, ResultMessage

async def sequential_queries():
    questions = [
        "1 + 1 は？",
        "その答えを2倍すると？",
        "さらにその答えの平方根は？"
    ]

    total_cost = 0.0

    for i, question in enumerate(questions, 1):
        print(f"\n--- 質問 {i}: {question} ---")

        async for message in query(prompt=question):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"回答: {block.text}")
            elif isinstance(message, ResultMessage):
                total_cost += message.total_cost_usd

    print(f"\n合計コスト: ${total_cost:.6f}")

asyncio.run(sequential_queries())
