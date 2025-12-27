import asyncio
import json
from datetime import datetime
from claude_agent_sdk import query, ClaudeAgentOptions

async def logged_query(prompt: str, log_file: str = "query_log.jsonl"):
    options = ClaudeAgentOptions(allowed_tools=["Read"])

    with open(log_file, "a") as f:
        async for message in query(prompt=prompt, options=options):
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "type": type(message).__name__,
                "data": str(message)[:500]  # 長すぎる場合は切り詰め
            }
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            print(f"[{log_entry['type']}] logged")

asyncio.run(logged_query("このプロジェクトの構造を説明して"))
