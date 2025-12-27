# query() 関数の基本

## 概要

このセクションでは、Claude Agent SDK の最も基本的なエントリーポイントである `query()` 関数の使い方を学習します。

`query()` 関数は、プロンプトを Claude に送信し、ストリーミング形式でレスポンスを受け取る非同期関数です。

---

## 手順1: 基本的な query() の使い方

### 1. 最小限のコード

**コード:**

```python
import asyncio
from claude_agent_sdk import query

async def main():
    async for message in query(prompt="Pythonとは何ですか？"):
        print(message)

asyncio.run(main())
```

<details>
<summary><strong>実行結果を見る</strong></summary>

```
SystemMessage(subtype='init', data={'type': 'system', 'subtype': 'init', 'cwd': '/Users/hirotaka/claude_agent_sdk_hands_on', 'session_id': 'f72b6fb0-ef22-462b-a635-c268e648263e', 'tools': ['Task', 'TaskOutput', 'Bash', 'Glob', 'Grep', 'ExitPlanMode', 'Read', 'Edit', 'Write', 'NotebookEdit', 'WebFetch', 'TodoWrite', 'WebSearch', 'KillShell', 'AskUserQuestion', 'Skill', 'SlashCommand', 'EnterPlanMode'], 'mcp_servers': [], 'model': 'claude-opus-4-5-20251101', 'permissionMode': 'default', 'slash_commands': ['compact', 'context', 'cost', 'init', 'pr-comments', 'release-notes', 'review', 'security-review'], 'apiKeySource': 'none', 'claude_code_version': '2.0.72', 'output_style': 'default', 'agents': ['general-purpose', 'statusline-setup', 'Explore', 'Plan'], 'skills': [], 'plugins': [], 'uuid': 'ed561546-55cb-4806-8332-c09f4cf0337c'})
AssistantMessage(content=[TextBlock(text='Pythonは、1991年にグイド・ヴァンロッサム（Guido van Rossum）によって開発された、汎用の高水準プログラミング言語です。\n\n## 主な特徴\n\n### 1. **読みやすく書きやすい構文**\n- インデント（字下げ）でコードブロックを表現\n- シンプルで直感的な文法\n- 初心者にも学びやすい\n\n### 2. **インタプリタ型言語**\n- コンパイル不要で即座に実行可能\n- 対話的に試しながらプログラミングできる\n\n### 3. **マルチパラダイム**\n- オブジェクト指向プログラミング\n- 手続き型プログラミング\n- 関数型プログラミング\n\n### 4. **豊富なライブラリとフレームワーク**\n- **Web開発**: Django, Flask, FastAPI\n- **データサイエンス**: NumPy, Pandas, Matplotlib\n- **機械学習/AI**: TensorFlow, PyTorch, scikit-learn\n- **自動化**: Selenium, BeautifulSoup\n\n## 主な用途\n\n| 分野 | 説明 |\n|------|------|\n| Web開発 | サーバーサイドアプリケーション |\n| データ分析 | データの処理・可視化 |\n| 機械学習・AI | モデルの構築・学習 |\n| 自動化・スクリプト | 業務効率化ツール |\n| 科学技術計算 | 研究・シミュレーション |\n\n## 簡単なコード例\n\n```python\n# Hello Worldの出力\nprint("Hello, World!")\n\n# リストの操作\nnumbers = [1, 2, 3, 4, 5]\nsquared = [n ** 2 for n in numbers]\nprint(squared)  # [1, 4, 9, 16, 25]\n```\n\nPythonは現在、世界で最も人気のあるプログラミング言語の一つであり、特にデータサイエンスやAI分野で広く使われています。')], model='claude-opus-4-5-20251101', parent_tool_use_id=None, error=None)
ResultMessage(subtype='success', duration_ms=11672, duration_api_ms=17363, is_error=False, num_turns=1, session_id='f72b6fb0-ef22-462b-a635-c268e648263e', total_cost_usd=0.027421999999999995, usage={'input_tokens': 3, 'cache_creation_input_tokens': 330, 'cache_read_input_tokens': 14779, 'output_tokens': 597, 'server_tool_use': {'web_search_requests': 0, 'web_fetch_requests': 0}, 'service_tier': 'standard', 'cache_creation': {'ephemeral_1h_input_tokens': 0, 'ephemeral_5m_input_tokens': 330}}, result='Pythonは、1991年にグイド・ヴァンロッサム（Guido van Rossum）によって開発された、汎用の高水準プログラミング言語です。\n\n## 主な特徴\n\n### 1. **読みやすく書きやすい構文**\n- インデント（字下げ）でコードブロックを表現\n- シンプルで直感的な文法\n- 初心者にも学びやすい\n\n### 2. **インタプリタ型言語**\n- コンパイル不要で即座に実行可能\n- 対話的に試しながらプログラミングできる\n\n### 3. **マルチパラダイム**\n- オブジェクト指向プログラミング\n- 手続き型プログラミング\n- 関数型プログラミング\n\n### 4. **豊富なライブラリとフレームワーク**\n- **Web開発**: Django, Flask, FastAPI\n- **データサイエンス**: NumPy, Pandas, Matplotlib\n- **機械学習/AI**: TensorFlow, PyTorch, scikit-learn\n- **自動化**: Selenium, BeautifulSoup\n\n## 主な用途\n\n| 分野 | 説明 |\n|------|------|\n| Web開発 | サーバーサイドアプリケーション |\n| データ分析 | データの処理・可視化 |\n| 機械学習・AI | モデルの構築・学習 |\n| 自動化・スクリプト | 業務効率化ツール |\n| 科学技術計算 | 研究・シミュレーション |\n\n## 簡単なコード例\n\n```python\n# Hello Worldの出力\nprint("Hello, World!")\n\n# リストの操作\nnumbers = [1, 2, 3, 4, 5]\nsquared = [n ** 2 for n in numbers]\nprint(squared)  # [1, 4, 9, 16, 25]\n```\n\nPythonは現在、世界で最も人気のあるプログラミング言語の一つであり、特にデータサイエンスやAI分野で広く使われています。', structured_output=None)
```

</details>

### 2. コードの解説

| 要素 | 説明 |
|-----|------|
| `async for` | 非同期イテレーションでストリーミングレスポンスを受信 |
| `query()` | メインのエントリーポイント関数 |
| `prompt` | Claude に送信するプロンプト |
| `message` | 受信した各メッセージ（AssistantMessage, ResultMessage など） |

<div style="background-color: #f0f8ff; border: 1px solid #cce5ff; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #0d6efd; line-height: 1;">&#x24D8;</span>
    <span style="font-weight: bold; color: #0d6efd; font-size: 15px;">Note</span>
  </div>
  <div style="color: #454545; line-height: 1.6;">
    <code>query()</code> は AsyncIterator を返すため、必ず <code>async for</code> で処理します。通常の <code>for</code> ループは使用できません。
  </div>
</div>

---

## 手順2: テキストレスポンスの抽出

### 1. テキストのみを抽出する

実際のアプリケーションでは、テキスト部分だけを取り出したいことが多いです。

**コード:**

```python
import asyncio
from claude_agent_sdk import query, AssistantMessage, TextBlock

async def get_text_response(prompt: str) -> str:
    """プロンプトを送信し、テキストレスポンスを返す"""
    text_parts = []

    async for message in query(prompt=prompt):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    text_parts.append(block.text)

    return "".join(text_parts)

async def main():
    response = await get_text_response("Pythonの主な特徴を3つ教えてください")
    print(response)

asyncio.run(main())
```

<details>
<summary><strong>実行結果を見る</strong></summary>


Pythonの主な特徴を3つご紹介します：

## 1. **シンプルで読みやすい構文**
Pythonはインデント（字下げ）でコードブロックを表現し、英語に近い直感的な構文を持っています。これにより、初心者でも学びやすく、コードの可読性が高いのが特徴です。

```python
# 例：シンプルなfor文
for i in range(5):
    print(f"Hello {i}")
```

## 2. **豊富なライブラリとエコシステム**
標準ライブラリが充実しているだけでなく、以下のような分野で強力なサードパーティライブラリが存在します：
- **データサイエンス**: NumPy, Pandas, Matplotlib
- **機械学習**: TensorFlow, PyTorch, scikit-learn
- **Web開発**: Django, Flask, FastAPI

## 3. **汎用性の高さ（マルチパラダイム）**
Pythonは様々な用途に使える汎用プログラミング言語です：
- Webアプリケーション開発
- データ分析・機械学習
- 自動化スクリプト
- ゲーム開発
- IoT・組み込みシステム

また、オブジェクト指向、手続き型、関数型など複数のプログラミングスタイルに対応しています。

---

これらの特徴から、Pythonは初心者からプロフェッショナルまで幅広く使われている人気の言語となっています。


</details>

---

## 手順3: コンテキスト付きのクエリ

### 1. コードを含むプロンプト

**コード:**

```python
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
```

<details>
<summary><strong>実行結果を見る</strong></summary>


## コード分析

### 1. 何をする関数か

この関数は**階乗（factorial）**を計算する再帰関数です。

- `n!`（nの階乗）を計算します
- 例：`factorial(5)` → `5! = 5 × 4 × 3 × 2 × 1 = 120`

**動作の流れ：**
```
factorial(5)
→ 5 * factorial(4)
→ 5 * 4 * factorial(3)
→ 5 * 4 * 3 * factorial(2)
→ 5 * 4 * 3 * 2 * factorial(1)
→ 5 * 4 * 3 * 2 * 1
→ 120
```

---

### 2. 時間計算量

| 計算量 | 説明 |
|--------|------|
| **時間計算量** | **O(n)** - n回の再帰呼び出しを行う |
| **空間計算量** | **O(n)** - コールスタックにn個のフレームが積まれる |

---

### 3. 潜在的な問題点

#### ❌ **スタックオーバーフロー**
```python
factorial(10000)  # RecursionError: maximum recursion depth exceeded
```
Pythonのデフォルト再帰上限（約1000）を超えると例外が発生します。

#### ❌ **負の数の処理が不適切**
```python
factorial(-5)  # 無限再帰 → スタックオーバーフロー
```
`n <= 1`の条件により、負の数でも1を返しますが、数学的に負の整数の階乗は未定義です。

#### ❌ **型チェックがない**
```python
factorial(3.5)   # 予期しない動作
factorial("5")   # TypeError
```

---

### 改善版コード

```python
def factorial(n):
    # 入力検証
    if not isinstance(n, int):
        raise TypeError("整数を入力してください")
    if n < 0:
        raise ValueError("負の数の階乗は定義されていません")
    
    # 反復版（スタックオーバーフローを防ぐ）
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
```

または、標準ライブラリを使用：
```python
from math import factorial  # 最も効率的
```

</details>

---

## 手順4: ResultMessage からコスト情報を取得

### 1. API コストの確認

**コード:**

```python
import asyncio
from claude_agent_sdk import query, ResultMessage

async def check_cost():
    async for message in query(prompt="Hello, Claude!"):
        if isinstance(message, ResultMessage):
            print(f"セッションID: {message.session_id}")
            print(f"API コスト: ${message.total_cost_usd:.6f}")
            print(f"合計ターン数: {message.num_turns}")
            print(f"実行時間: {message.duration_ms}ms")
            if message.usage:
                print(f"使用量: {message.usage}")

asyncio.run(check_cost())
```

<details>
<summary><strong>実行結果を見る</strong></summary>

```
セッションID: b8ba7509-b4df-46f4-8aed-add1dc65f0a1
API コスト: $0.011431
合計ターン数: 1
実行時間: 2406ms
使用量: {'input_tokens': 3, 'cache_creation_input_tokens': 324, 'cache_read_input_tokens': 14779, 'output_tokens': 47, 'server_tool_use': {'web_search_requests': 0, 'web_fetch_requests': 0}, 'service_tier': 'standard', 'cache_creation': {'ephemeral_1h_input_tokens': 0, 'ephemeral_5m_input_tokens': 324}}
```

</details>

<div style="background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #155724; line-height: 1;">&#x2714;</span>
    <span style="font-weight: bold; color: #155724; font-size: 15px;">ポイント</span>
  </div>
  <div style="color: #155724; line-height: 1.6;">
    <code>ResultMessage</code> は必ずレスポンスの最後に送信されます。コスト管理やログ記録に活用しましょう。
  </div>
</div>

---

## 手順5: 複数のクエリを順次実行

### 1. 連続した質問

**コード:**

```python
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
```

<div style="background-color: #fff3cd; border: 1px solid #ffc107; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #856404; line-height: 1;">&#x26A0;</span>
    <span style="font-weight: bold; color: #856404; font-size: 15px;">注意</span>
  </div>
  <div style="color: #454545; line-height: 1.6;">
    この例では各 <code>query()</code> は独立しており、前の会話のコンテキストは引き継がれません。コンテキストを維持するには「セッション」を使用します（後のセクションで解説）。
  </div>
</div>

---

## 演習問題

### 演習1: 基本的なクエリ

以下の要件を満たす関数を作成してください：

1. プロンプトを受け取る
2. Claude に送信
3. テキストレスポンスとコストを辞書で返す

```python
async def query_with_cost(prompt: str) -> dict:
    # ここに実装
    pass
```

### 演習2: 複数の質問を並列実行

`asyncio.gather()` を使って、複数の質問を並列に実行する関数を作成してください。

### 演習3: レスポンスのストリーミング表示

テキストを1文字ずつ表示するような、タイプライター風の表示を実装してください。

---

## 次のステップ

`query()` 関数の基本がわかりました。次は [メッセージ型](02_message_types.md) で、返却されるさまざまなメッセージタイプについて詳しく学びましょう。
