# ClaudeSDKClient の基本

## 概要

このセクションでは、継続的な会話を管理するための `ClaudeSDKClient` クラスの使い方を学習します。

`query()` 関数が単発のクエリに適しているのに対し、`ClaudeSDKClient` はマルチターン会話、セッション管理、動的な設定変更が必要な場合に使用します。

---

## query() と ClaudeSDKClient の使い分け

| 特徴 | query() | ClaudeSDKClient |
|------|---------|-----------------|
| 用途 | 単発クエリ | 継続的な会話 |
| コンテキスト | 保持しない | 保持する |
| セッション管理 | 自動 | 手動制御可能 |
| 設定変更 | 不可 | 会話中に変更可能 |
| 割り込み | 不可 | 可能 |

---

## 手順1: 基本的な ClaudeSDKClient の使い方

### 1. コンテキストマネージャーを使った基本形

**コード:**

```python
import asyncio
from claude_agent_sdk import ClaudeSDKClient, AssistantMessage, TextBlock

async def main():
    async with ClaudeSDKClient() as client:
        await client.query("Pythonとは何ですか？")

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text)

asyncio.run(main())
```

<details>
<summary><strong>実行結果を見る</strong></summary>

```
Pythonは、読みやすく書きやすいことを重視した汎用プログラミング言語です。
1991年にグイド・ヴァン・ロッサムによって開発され、現在はWeb開発、
データサイエンス、機械学習など幅広い分野で使用されています。
```

</details>

### 2. コードの解説

| 要素 | 説明 |
|-----|------|
| `async with ClaudeSDKClient()` | コンテキストマネージャーで接続を管理 |
| `client.query()` | クエリを送信 |
| `client.receive_response()` | ResultMessage まで応答を受信 |

<div style="background-color: #f0f8ff; border: 1px solid #cce5ff; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #0d6efd; line-height: 1;">&#x24D8;</span>
    <span style="font-weight: bold; color: #0d6efd; font-size: 15px;">Note</span>
  </div>
  <div style="color: #454545; line-height: 1.6;">
    <code>async with</code> を使用すると、スコープを抜けるときに自動的に <code>disconnect()</code> が呼ばれます。
  </div>
</div>

---

## 手順2: マルチターン会話

### 1. コンテキストを維持した連続会話

`ClaudeSDKClient` の最大の利点は、前の会話のコンテキストを維持できることです。

**コード:**

```python
import asyncio
from claude_agent_sdk import ClaudeSDKClient, AssistantMessage, TextBlock, ResultMessage

async def multi_turn_conversation():
    async with ClaudeSDKClient() as client:
        # 最初の質問
        print("--- 質問1 ---")
        await client.query("私の名前は田中です。覚えておいてください。")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")

        # フォローアップ（コンテキストが維持される）
        print("\n--- 質問2 ---")
        await client.query("私の名前を覚えていますか？")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")

        # さらにフォローアップ
        print("\n--- 質問3 ---")
        await client.query("私の名前を使って挨拶してください。")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")

asyncio.run(multi_turn_conversation())
```

<details>
<summary><strong>実行結果を見る</strong></summary>

```
--- 質問1 ---
Claude: 承知しました。田中さんですね。お名前を覚えました。

--- 質問2 ---
Claude: はい、覚えています。あなたのお名前は田中さんです。

--- 質問3 ---
Claude: こんにちは、田中さん！お話できて嬉しいです。
```

</details>

<div style="background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #155724; line-height: 1;">&#x2714;</span>
    <span style="font-weight: bold; color: #155724; font-size: 15px;">ポイント</span>
  </div>
  <div style="color: #155724; line-height: 1.6;">
    <code>query()</code> 関数とは異なり、<code>ClaudeSDKClient</code> は同一インスタンス内で会話のコンテキストを自動的に維持します。
  </div>
</div>

---

## 手順3: オプション付きでクライアントを初期化

### 1. ClaudeAgentOptions との組み合わせ

**コード:**

```python
import asyncio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions
from claude_agent_sdk.types import AssistantMessage, TextBlock

async def with_options():
    options = ClaudeAgentOptions(
        system_prompt="あなたは親切な日本語アシスタントです。簡潔に回答してください。",
        max_turns=5,
        permission_mode="acceptEdits"
    )

    async with ClaudeSDKClient(options) as client:
        await client.query("再帰関数とは何ですか？")

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text)

asyncio.run(with_options())
```

<details>
<summary><strong>実行結果を見る</strong></summary>

```
再帰関数は、自分自身を呼び出す関数です。基底条件で終了し、
問題を小さな部分に分割して解決します。例：階乗計算、フィボナッチ数列。
```

</details>

---

## 手順4: 会話中の設定変更

### 1. パーミッションモードの動的変更

**コード:**

```python
import asyncio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions
from claude_agent_sdk.types import AssistantMessage, TextBlock

async def change_settings():
    options = ClaudeAgentOptions(
        permission_mode="default",
        allowed_tools=["Read", "Write", "Edit"]
    )

    async with ClaudeSDKClient(options) as client:
        # 最初は確認が必要なモード
        await client.query("現在のディレクトリのファイルを確認して")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text)

        # 編集を自動承認するモードに変更
        await client.set_permission_mode("acceptEdits")
        print("\n[パーミッションモードを acceptEdits に変更]\n")

        # ファイル編集が自動承認される
        await client.query("README.md に説明を追加して")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text)

asyncio.run(change_settings())
```

### 2. モデルの動的変更

```python
# 会話中にモデルを変更
await client.set_model("claude-sonnet-4-5")
```

---

## 手順5: 割り込み機能

### 1. 長い応答を中断する

**コード:**

```python
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

        # 15秒後に割り込みするタイマーを開始
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
```

<div style="background-color: #fff3cd; border: 1px solid #ffc107; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #856404; line-height: 1;">&#x26A0;</span>
    <span style="font-weight: bold; color: #856404; font-size: 15px;">注意</span>
  </div>
  <div style="color: #454545; line-height: 1.6;">
    <code>interrupt()</code> を呼び出すと、現在の応答生成が中断されます。中断後も同じクライアントで新しいクエリを送信できます。
  </div>
</div>

---

## 手順6: receive_messages() と receive_response() の違い

### 1. 二つのメソッドの比較

| メソッド | 説明 | 用途 |
|---------|------|------|
| `receive_messages()` | 全てのメッセージを受信し続ける | 長時間の処理、手動制御 |
| `receive_response()` | ResultMessage まで受信して停止 | 通常の会話フロー |

**receive_response() の例:**

```python
# ResultMessage を受信すると自動的に停止
async for message in client.receive_response():
    print(message)
# ここに到達 = 応答完了
```

**receive_messages() の例:**

```python
# 明示的に break しないと無限に待機
async for message in client.receive_messages():
    print(message)
    if isinstance(message, ResultMessage):
        break  # 手動で終了
```

---

## 手順7: 手動での接続管理

### 1. コンテキストマネージャーを使わない方法

**コード:**

```python
import asyncio
from claude_agent_sdk import ClaudeSDKClient
from claude_agent_sdk.types import AssistantMessage, TextBlock

async def manual_connection():
    client = ClaudeSDKClient()

    try:
        # 明示的に接続
        await client.connect()

        await client.query("こんにちは")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text)

    finally:
        # 明示的に切断
        await client.disconnect()

asyncio.run(manual_connection())
```

<div style="background-color: #f0f8ff; border: 1px solid #cce5ff; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #0d6efd; line-height: 1;">&#x24D8;</span>
    <span style="font-weight: bold; color: #0d6efd; font-size: 15px;">Note</span>
  </div>
  <div style="color: #454545; line-height: 1.6;">
    特別な理由がない限り、<code>async with</code> を使用することを推奨します。リソースの解放が確実に行われます。
  </div>
</div>

---

## 演習問題

### 演習1: 対話型計算機

`ClaudeSDKClient` を使って、以下の機能を持つ対話型計算機を作成してください：

1. ユーザーの計算リクエストを受け付ける
2. 前の計算結果を覚えている（「その答えを2倍して」などに対応）
3. 「終了」と入力されるまで会話を続ける

### 演習2: コンテキスト確認

同じ質問を `query()` と `ClaudeSDKClient` の両方で実行し、コンテキスト維持の違いを確認するコードを書いてください。

### 演習3: 設定変更の活用

会話の途中でパーミッションモードを変更し、その効果を確認できるデモを作成してください。

---

## まとめ

| 機能 | メソッド |
|------|----------|
| 接続 | `connect()` または `async with` |
| クエリ送信 | `query(prompt)` |
| 応答受信 | `receive_response()` / `receive_messages()` |
| 割り込み | `interrupt()` |
| 設定変更 | `set_permission_mode()` / `set_model()` |
| 切断 | `disconnect()` |

---

## 次のステップ

基本操作をマスターしました。次は [オプション設定](../options/01_options_overview.md) で、`ClaudeAgentOptions` の詳細な設定方法を学びましょう。
