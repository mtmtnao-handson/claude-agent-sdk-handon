# max_turns 設定

## 概要

このセクションでは、`max_turns` オプションを使って会話のターン数を制限する方法を学習します。

ターン数を適切に設定することで、コスト管理や無限ループの防止ができます。

**サンプルスクリプト:**

このドキュメントの例は、以下のスクリプトで実際に試すことができます：

```bash
src/02_options/04_max_turns/
├── 01_basic.py          # 手順1-2: 基本的な使い方、ユースケース別設定
├── 02_monitoring.py     # 手順3: ターン数のモニタリング
├── 03_budget_control.py # 手順4: コスト管理との組み合わせ
└── 04_adaptive.py       # 手順5-6: 動的なターン数調整、継続実行パターン
```

```bash
# 基本的な使い方 (手順1-2)
python src/02_options/04_max_turns/01_basic.py -l    # モード一覧
python src/02_options/04_max_turns/01_basic.py -h    # ヘルプ
python src/02_options/04_max_turns/01_basic.py -m qa -p "Pythonとは？"

# モニタリング (手順3)
python src/02_options/04_max_turns/02_monitoring.py -t 10 -p "プロジェクトを分析"
python src/02_options/04_max_turns/02_monitoring.py --verbose -t 15 -p "src/を調査"

# コスト管理 (手順4)
python src/02_options/04_max_turns/03_budget_control.py -c 0.10 -t 50
python src/02_options/04_max_turns/03_budget_control.py --interactive

# 動的ターン数調整 (手順5-6)
python src/02_options/04_max_turns/04_adaptive.py -m estimate -p "全ファイルを分析"
python src/02_options/04_max_turns/04_adaptive.py -m continue -p "大規模分析を実行"
python src/02_options/04_max_turns/04_adaptive.py -m progressive -p "プロジェクト調査"
```

---

## 手順1: max_turns の基本

### 1. ターンとは

1ターン = Claude が応答を生成し、必要に応じてツールを実行する1サイクル

```
ユーザー: "ファイルを読んで要約して"
  ├─ ターン1: Claude が Read ツールを呼び出す
  ├─ ターン2: Claude が内容を分析
  └─ ターン3: Claude が要約を返す
```

### 2. 基本的な設定

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

# 5ターンに制限
options = ClaudeAgentOptions(
    max_turns=5
)

async def limited_query():
    async for message in query(
        prompt="複雑な分析タスクを実行して",
        options=options
    ):
        print(message)
```

---

## 手順2: ターン数と用途の関係

### 1. 推奨設定

| ユースケース | 推奨 max_turns | 理由 |
|-------------|---------------|------|
| 単純な Q&A | 1-3 | 追加のツール使用が不要 |
| ファイル読み取り | 5-10 | 数ファイルの読み取りと分析 |
| コード生成 | 10-20 | 複数ファイルの作成・編集 |
| 複雑なリファクタリング | 20-50 | 多数のファイル操作 |
| 自動化タスク | 50-100 | 長時間の自動処理 |

### 2. ユースケース別の設定

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions

# Q&A 用
qa_options = ClaudeAgentOptions(
    max_turns=3,
    allowed_tools=[]  # ツールなし
)

# コードレビュー用
review_options = ClaudeAgentOptions(
    max_turns=10,
    allowed_tools=["Read", "Glob", "Grep"]
)

# 開発作業用
dev_options = ClaudeAgentOptions(
    max_turns=30,
    allowed_tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep"]
)

# 大規模リファクタリング用
refactor_options = ClaudeAgentOptions(
    max_turns=100,
    allowed_tools=["Read", "Write", "Edit", "Glob", "Grep"]
)
```

---

## 手順3: ターン数のモニタリング

### 1. 現在のターン数を追跡

**コード:**

```python
import asyncio
from claude_agent_sdk import (
    ClaudeAgentOptions,
    query,
    AssistantMessage,
    ResultMessage
)

async def monitored_query(prompt: str, max_turns: int = 10):
    options = ClaudeAgentOptions(max_turns=max_turns)

    turn_count = 0

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            turn_count += 1
            print(f"[ターン {turn_count}/{max_turns}]")

        if isinstance(message, ResultMessage):
            print(f"\n=== 完了 ===")
            print(f"実際のターン数: {message.num_turns}")
            print(f"最大ターン数: {max_turns}")
            print(f"コスト: ${message.total_cost_usd:.4f}")

asyncio.run(monitored_query("プロジェクトを分析して", max_turns=10))
```

<details>
<summary><strong>実行結果を見る</strong></summary>

```
[ターン 1/10]
[ターン 2/10]
[ターン 3/10]

=== 完了 ===
実際のターン数: 3
最大ターン数: 10
コスト: $0.0025
```

</details>

---

## 手順4: コスト管理との組み合わせ

### 1. ターン数とコストの予算管理

**コード:**

```python
import asyncio
from claude_agent_sdk import ClaudeAgentOptions, query, ResultMessage

class BudgetManager:
    def __init__(self, max_cost_usd: float, max_turns: int):
        self.max_cost_usd = max_cost_usd
        self.max_turns = max_turns
        self.total_cost = 0.0
        self.total_turns = 0

    def check_budget(self, cost: float, turns: int) -> bool:
        """予算内かどうかをチェック"""
        self.total_cost += cost
        self.total_turns += turns

        if self.total_cost > self.max_cost_usd:
            print(f"警告: コスト上限 (${self.max_cost_usd}) を超過")
            return False

        if self.total_turns > self.max_turns:
            print(f"警告: ターン上限 ({self.max_turns}) を超過")
            return False

        return True

    def get_remaining(self) -> dict:
        return {
            "remaining_cost": self.max_cost_usd - self.total_cost,
            "remaining_turns": self.max_turns - self.total_turns
        }

async def budget_aware_query(prompt: str, budget: BudgetManager):
    remaining = budget.get_remaining()

    options = ClaudeAgentOptions(
        max_turns=min(remaining["remaining_turns"], 10)
    )

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, ResultMessage):
            if not budget.check_budget(message.total_cost_usd, message.num_turns):
                print("予算超過のため停止")
                break
        else:
            print(message)

# 使用例
async def main():
    budget = BudgetManager(max_cost_usd=0.10, max_turns=50)

    prompts = [
        "README.md を読んで",
        "src/ の構造を分析して",
        "改善点を提案して"
    ]

    for prompt in prompts:
        print(f"\n--- {prompt} ---")
        remaining = budget.get_remaining()
        print(f"残り: ${remaining['remaining_cost']:.4f}, {remaining['remaining_turns']}ターン")

        await budget_aware_query(prompt, budget)

asyncio.run(main())
```

---

## 手順5: ターン制限時の動作

### 1. 制限に達した場合

**コード:**

```python
import asyncio
from claude_agent_sdk import (
    ClaudeAgentOptions,
    query,
    AssistantMessage,
    TextBlock,
    ResultMessage
)

async def test_turn_limit():
    # 意図的に少ないターン数を設定
    options = ClaudeAgentOptions(
        max_turns=2,
        allowed_tools=["Read", "Glob"]
    )

    # 多くのターンを必要とするタスク
    prompt = "プロジェクト内の全ファイルを読んで、詳細な分析レポートを作成してください"

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text[:200] + "...")

        if isinstance(message, ResultMessage):
            print(f"\n終了理由: ターン数制限")
            print(f"使用ターン: {message.num_turns}")

asyncio.run(test_turn_limit())
```

<div style="background-color: #f0f8ff; border: 1px solid #cce5ff; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #0d6efd; line-height: 1;">&#x24D8;</span>
    <span style="font-weight: bold; color: #0d6efd; font-size: 15px;">Note</span>
  </div>
  <div style="color: #454545; line-height: 1.6;">
    ターン制限に達すると、Claude は可能な限り現在の状態で応答を完了しようとします。タスクが中途半端に終わる可能性があるため、複雑なタスクには十分なターン数を設定してください。
  </div>
</div>

---

## 手順6: 動的なターン数調整

### 1. タスクの複雑さに応じた調整

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

def estimate_turns(prompt: str) -> int:
    """プロンプトからターン数を推定"""

    # キーワードベースの簡易推定
    keywords = {
        "分析": 5,
        "読んで": 3,
        "作成": 10,
        "リファクタリング": 20,
        "全ファイル": 15,
        "テスト": 10,
        "修正": 8,
    }

    base_turns = 5
    for keyword, turns in keywords.items():
        if keyword in prompt:
            base_turns = max(base_turns, turns)

    return base_turns

async def adaptive_query(prompt: str):
    estimated = estimate_turns(prompt)
    print(f"推定ターン数: {estimated}")

    options = ClaudeAgentOptions(
        max_turns=estimated,
        allowed_tools=["Read", "Write", "Edit", "Glob", "Grep"]
    )

    async for message in query(prompt=prompt, options=options):
        print(message)

# 使用例
# asyncio.run(adaptive_query("全ファイルを分析してリファクタリングして"))
```

### 2. 継続実行パターン

**コード:**

```python
import asyncio
from claude_agent_sdk import ClaudeAgentOptions, query, ResultMessage

async def continue_if_needed(
    prompt: str,
    initial_turns: int = 10,
    max_total_turns: int = 50
):
    """必要に応じてターンを継続"""

    total_turns = 0
    iteration = 0

    while total_turns < max_total_turns:
        iteration += 1
        remaining = max_total_turns - total_turns

        options = ClaudeAgentOptions(
            max_turns=min(initial_turns, remaining)
        )

        print(f"\n=== イテレーション {iteration} ===")

        current_prompt = prompt if iteration == 1 else "続きを実行してください"

        async for message in query(prompt=current_prompt, options=options):
            if isinstance(message, ResultMessage):
                total_turns += message.num_turns
                print(f"累計ターン: {total_turns}/{max_total_turns}")

                # タスクが完了したかどうかを確認
                # （実際にはより洗練された判定が必要）
                if message.num_turns < initial_turns:
                    print("タスク完了")
                    return
            else:
                print(message)

    print("最大ターン数に達しました")

# asyncio.run(continue_if_needed("大規模なコード分析を実行"))
```

<div style="background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #155724; line-height: 1;">&#x2714;</span>
    <span style="font-weight: bold; color: #155724; font-size: 15px;">ポイント</span>
  </div>
  <div style="color: #155724; line-height: 1.6;">
    長時間のタスクでは、セッション機能と組み合わせて継続実行することで、コンテキストを維持しながら大規模な処理が可能です。
  </div>
</div>

---

## 演習問題

### 演習1: 適応型ターン管理

プロンプトの内容を分析し、最適なターン数を自動設定するクラスを作成してください。

### 演習2: ターン消費レポート

各ツールがどれだけターンを消費したかを分析するレポート機能を実装してください。

### 演習3: 段階的ターン増加

まず少ないターンで試行し、不足していれば段階的に増やすスマートな実行戦略を実装してください。

---

## 次のステップ

ターン数の管理を理解しました。次は [system_prompt](05_system_prompt.md) で、システムプロンプトのカスタマイズについて学びましょう。
