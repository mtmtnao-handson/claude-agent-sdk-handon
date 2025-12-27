# サブエージェント

## 概要

このセクションでは、AgentDefinition を使ってサブエージェントを定義し、専門化されたタスクを実行する方法を学習します。

サブエージェントを使うと、複雑なワークフローを分割し、各部分を専門家に任せることができます。

---

## 手順1: AgentDefinition の基本

### 1. サブエージェントの定義

**コード:**

```python
from claude_agent_sdk import AgentDefinition, ClaudeAgentOptions, query

# コードレビューエージェント
code_reviewer = AgentDefinition(
    description="コードの品質とセキュリティをレビューする専門家",
    prompt="""あなたはシニアセキュリティエンジニアです。
以下の観点からコードをレビューしてください：
- バグの可能性
- セキュリティ脆弱性
- パフォーマンス問題
- ベストプラクティス違反""",
    tools=["Read", "Glob", "Grep"],
    model="sonnet"  # 高速なモデルを使用
)

# オプションにエージェントを追加
options = ClaudeAgentOptions(
    agents={"reviewer": code_reviewer},
    allowed_tools=["Task"]  # Task ツールでサブエージェントを呼び出す
)

async def use_subagent():
    prompt = "reviewer エージェントを使って src/ のコードをレビューしてください"

    async for message in query(prompt=prompt, options=options):
        print(message)
```

### 2. AgentDefinition のパラメータ

| パラメータ | 型 | 説明 |
|-----------|-----|------|
| `description` | string | エージェントの役割説明（選択時に参照される） |
| `prompt` | string | エージェントへのシステムプロンプト |
| `tools` | list[str] | エージェントが使用できるツール |
| `model` | string | 使用するモデル（sonnet, opus, haiku） |

---

## 手順2: 複数のサブエージェント

### 1. 役割分担

**コード:**

```python
from claude_agent_sdk import AgentDefinition, ClaudeAgentOptions

# セキュリティレビューア
security_reviewer = AgentDefinition(
    description="セキュリティ脆弱性を検出するエージェント",
    prompt="""セキュリティの観点からコードを分析：
- SQL インジェクション
- XSS 脆弱性
- 認証/認可の問題
- 機密情報の露出""",
    tools=["Read", "Grep"],
    model="sonnet"
)

# パフォーマンスアナライザー
performance_analyzer = AgentDefinition(
    description="パフォーマンス問題を分析するエージェント",
    prompt="""パフォーマンスの観点からコードを分析：
- 計算量の問題
- メモリリーク
- N+1 クエリ問題
- 不要な処理""",
    tools=["Read", "Grep"],
    model="sonnet"
)

# ドキュメントライター
doc_writer = AgentDefinition(
    description="技術ドキュメントを作成するエージェント",
    prompt="""明確で実用的なドキュメントを作成：
- API ドキュメント
- 使用例
- 注意事項""",
    tools=["Read", "Write", "Edit"],
    model="sonnet"
)

# 全エージェントを登録
options = ClaudeAgentOptions(
    agents={
        "security": security_reviewer,
        "performance": performance_analyzer,
        "docs": doc_writer
    },
    allowed_tools=["Task", "Read", "Glob"]
)
```

### 2. エージェントの選択と協調

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    agents={
        "security": security_reviewer,
        "performance": performance_analyzer,
        "docs": doc_writer
    },
    system_prompt="""タスクに応じて適切なエージェントを選択：
- セキュリティ懸念 → security エージェント
- パフォーマンス問題 → performance エージェント
- ドキュメント作成 → docs エージェント

複数の観点が必要な場合は、順番に複数のエージェントを使用してください。"""
)

async def coordinated_review():
    prompt = """src/auth.py を以下の順序でレビューしてください：
1. security エージェントでセキュリティレビュー
2. performance エージェントでパフォーマンス分析
3. 結果をまとめてレポート"""

    async for message in query(prompt=prompt, options=options):
        print(message)
```

---

## 手順3: サブエージェントのモデル選択

### 1. タスクに応じたモデル選択

**コード:**

```python
from claude_agent_sdk import AgentDefinition

# 高速・低コスト（簡単なタスク）
quick_agent = AgentDefinition(
    description="簡単なタスクを高速処理",
    prompt="シンプルに素早く処理してください",
    tools=["Read", "Grep"],
    model="haiku"  # 最速・最安
)

# バランス型（一般的なタスク）
balanced_agent = AgentDefinition(
    description="バランスの取れた処理",
    prompt="品質と速度のバランスを重視",
    tools=["Read", "Write", "Edit"],
    model="sonnet"  # バランス
)

# 高品質（複雑なタスク）
expert_agent = AgentDefinition(
    description="複雑な分析と判断",
    prompt="深い分析と高品質な出力を重視",
    tools=["Read", "Glob", "Grep", "WebSearch"],
    model="opus"  # 最高品質
)
```

### 2. コスト最適化パターン

**コード:**

```python
from claude_agent_sdk import AgentDefinition, ClaudeAgentOptions

# トリアージエージェント（低コスト）
triage_agent = AgentDefinition(
    description="タスクの振り分け",
    prompt="タスクの複雑さを評価し、適切なエージェントを選択",
    tools=["Read"],
    model="haiku"
)

# 実行エージェント（必要に応じて高コスト）
executor_agent = AgentDefinition(
    description="実際のタスク実行",
    prompt="高品質な結果を出力",
    tools=["Read", "Write", "Edit", "Bash"],
    model="sonnet"
)

# コスト最適化設定
cost_optimized_options = ClaudeAgentOptions(
    agents={
        "triage": triage_agent,
        "executor": executor_agent
    },
    system_prompt="""コスト最適化ルール：
1. まず triage エージェントでタスクを評価
2. 必要な場合のみ executor エージェントを使用
3. 簡単なタスクは自分で直接処理"""
)
```

<div style="background-color: #f0f8ff; border: 1px solid #cce5ff; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #0d6efd; line-height: 1;">&#x24D8;</span>
    <span style="font-weight: bold; color: #0d6efd; font-size: 15px;">Note</span>
  </div>
  <div style="color: #454545; line-height: 1.6;">
    モデル選択はコストと品質のトレードオフです。Haiku は最速・最安ですが、複雑なタスクには Sonnet や Opus が適しています。
  </div>
</div>

---

## 手順4: サブエージェントの実践パターン

### 1. コードレビューパイプライン

**コード:**

```python
from claude_agent_sdk import AgentDefinition, ClaudeAgentOptions, query

# ステージ 1: 静的解析
static_analyzer = AgentDefinition(
    description="静的コード解析",
    prompt="構文、型、スタイルの問題を検出",
    tools=["Read", "Glob", "Grep"],
    model="haiku"
)

# ステージ 2: ロジックレビュー
logic_reviewer = AgentDefinition(
    description="ビジネスロジックのレビュー",
    prompt="ロジックの正確性と効率性を検証",
    tools=["Read", "Grep"],
    model="sonnet"
)

# ステージ 3: レポート作成
report_generator = AgentDefinition(
    description="レビューレポートの作成",
    prompt="レビュー結果を構造化されたレポートにまとめる",
    tools=["Write"],
    model="sonnet"
)

pipeline_options = ClaudeAgentOptions(
    agents={
        "static": static_analyzer,
        "logic": logic_reviewer,
        "report": report_generator
    }
)

async def code_review_pipeline():
    prompt = """以下のパイプラインでコードレビューを実行：
1. static エージェントで静的解析
2. logic エージェントでロジックレビュー
3. report エージェントでレポート作成（review_report.md）"""

    async for message in query(prompt=prompt, options=pipeline_options):
        print(message)
```

### 2. リサーチアシスタント

**コード:**

```python
from claude_agent_sdk import AgentDefinition, ClaudeAgentOptions

# 検索エージェント
searcher = AgentDefinition(
    description="情報検索",
    prompt="関連情報を幅広く検索",
    tools=["WebSearch", "WebFetch"],
    model="haiku"
)

# 分析エージェント
analyst = AgentDefinition(
    description="情報分析",
    prompt="収集した情報を分析・評価",
    tools=["Read"],
    model="sonnet"
)

# サマリーエージェント
summarizer = AgentDefinition(
    description="要約作成",
    prompt="分析結果を簡潔にまとめる",
    tools=["Write"],
    model="sonnet"
)

research_options = ClaudeAgentOptions(
    agents={
        "search": searcher,
        "analyze": analyst,
        "summarize": summarizer
    }
)
```

---

## 手順5: エージェント間の情報共有

### 1. コンテキストの受け渡し

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    agents={
        "analyzer": AgentDefinition(
            description="コード分析",
            prompt="分析結果を構造化して出力",
            tools=["Read", "Glob"],
            model="sonnet"
        ),
        "improver": AgentDefinition(
            description="コード改善",
            prompt="分析結果に基づいて改善を実施",
            tools=["Read", "Edit"],
            model="sonnet"
        )
    },
    system_prompt="""エージェント間の情報共有ルール：
- analyzer の出力を improver に渡す
- 重要な発見事項は明示的に伝達
- 各ステップの結果をログに記録"""
)

async def chained_agents():
    prompt = """以下の手順でコードを改善：
1. analyzer で問題点を特定
2. analyzer の結果を基に improver で修正"""

    async for message in query(prompt=prompt, options=options):
        print(message)
```

<div style="background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #155724; line-height: 1;">&#x2714;</span>
    <span style="font-weight: bold; color: #155724; font-size: 15px;">ポイント</span>
  </div>
  <div style="color: #155724; line-height: 1.6;">
    サブエージェントは独立したコンテキストを持ちます。重要な情報は明示的に渡す必要があります。
  </div>
</div>

---

## 演習問題

### 演習1: エージェントオーケストレーター

複数のエージェントを動的に選択・実行するオーケストレーターを作成してください。

### 演習2: エージェント評価システム

各エージェントの出力品質を評価し、フィードバックを与えるシステムを実装してください。

### 演習3: 自己改善エージェント

自身のパフォーマンスを分析し、プロンプトを改善するエージェントを作成してください。

---

## 次のステップ

サブエージェントを理解しました。次は [フック](03_hooks.md) で、エージェントの動作をカスタマイズする方法を学びましょう。
