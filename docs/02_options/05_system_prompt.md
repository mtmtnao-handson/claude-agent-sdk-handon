# system_prompt カスタマイズ

## 概要

このセクションでは、`system_prompt` オプションを使って Claude の振る舞いをカスタマイズする方法を学習します。

システムプロンプトを適切に設定することで、特定のタスクに最適化されたエージェントを作成できます。

**サンプルスクリプト:**

```bash
src/02_options/05_system_prompt/
├── 01_persona.py          # 手順1-2: ペルソナの設定
├── 02_output_format.py    # 手順3: 出力形式の指定
├── 03_constraints.py      # 手順4: 制約条件の設定
└── 04_template_builder.py # 手順5-6: 複合的なプロンプト構築
```

```bash
# ペルソナ一覧
python src/02_options/05_system_prompt/01_persona.py -l

# 出力形式一覧
python src/02_options/05_system_prompt/02_output_format.py -l

# 制約条件一覧
python src/02_options/05_system_prompt/03_constraints.py -l

# テンプレートプリセット一覧
python src/02_options/05_system_prompt/04_template_builder.py --list-presets
```

---

## 手順1: system_prompt の基本

### 1. 基本的な設定

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(
    system_prompt="あなたは親切な Python プログラミングの先生です。"
)

async def main():
    async for message in query(
        prompt="for ループの使い方を教えて",
        options=options
    ):
        print(message)
```

### 2. システムプロンプトの効果

| 設定 | 効果 |
|-----|------|
| ペルソナ | 応答のトーンと専門性を変更 |
| 出力形式 | JSON、Markdown などの形式を指定 |
| 制約条件 | 許可/禁止事項を定義 |
| ドメイン知識 | 特定分野の背景情報を提供 |

---

## 手順2: ペルソナの設定

### 1. 専門家ペルソナ

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions

# シニア開発者
senior_dev = ClaudeAgentOptions(
    system_prompt="""あなたは 20 年以上の経験を持つシニアソフトウェアエンジニアです。

特徴:
- コードの品質と保守性を重視
- ベストプラクティスと設計パターンに精通
- 初心者にも分かりやすく説明できる
- パフォーマンスとセキュリティを常に意識

コードレビュー時は以下の観点を確認:
1. 正確性とバグの可能性
2. パフォーマンスへの影響
3. セキュリティリスク
4. 可読性と保守性
5. テスト容易性
"""
)

# テクニカルライター
tech_writer = ClaudeAgentOptions(
    system_prompt="""あなたはテクニカルドキュメントの専門家です。

特徴:
- 明確で簡潔な文章を書く
- 技術的な概念を分かりやすく説明
- 一貫したスタイルを維持
- 読者の技術レベルに合わせた説明

ドキュメント作成時のルール:
- 能動態を使用
- 専門用語は初出時に説明
- コード例を必ず含める
- 段階的に複雑さを増す
"""
)
```

### 2. 役割に応じた振る舞い

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

def create_persona_options(role: str) -> ClaudeAgentOptions:
    """役割に応じたオプションを作成"""

    personas = {
        "mentor": """あなたは親切なメンターです。
- 質問には丁寧に答える
- 間違いは優しく指摘
- 学習を促進するヒントを与える
- 励ましの言葉を添える""",

        "reviewer": """あなたは厳格なコードレビューアです。
- バグは見逃さない
- ベストプラクティスを徹底
- 改善点を具体的に指摘
- 良い点も認める""",

        "architect": """あなたはソフトウェアアーキテクトです。
- システム全体を俯瞰
- スケーラビリティを重視
- 技術的負債を警告
- 将来の拡張性を考慮"""
    }

    return ClaudeAgentOptions(
        system_prompt=personas.get(role, ""),
        allowed_tools=["Read", "Glob", "Grep"]
    )
```

**実際に試す:**

```bash
# ペルソナ一覧を表示
python src/02_options/05_system_prompt/01_persona.py -l

# メンターとして実行
python src/02_options/05_system_prompt/01_persona.py -r mentor -p "Python の for ループについて教えて"

# レビューアとして実行
python src/02_options/05_system_prompt/01_persona.py -r reviewer -p "このコードをレビューして"
```

---

## 手順3: 出力形式の指定

### 1. JSON 出力

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions, query, AssistantMessage, TextBlock
import json

options = ClaudeAgentOptions(
    system_prompt="""分析結果は必ず以下の JSON 形式で出力してください:

{
    "summary": "分析の要約",
    "findings": [
        {
            "type": "bug" | "improvement" | "info",
            "severity": "high" | "medium" | "low",
            "description": "説明",
            "location": "ファイル:行番号"
        }
    ],
    "recommendations": ["推奨事項1", "推奨事項2"]
}

JSON 以外のテキストは出力しないでください。""",
    allowed_tools=["Read", "Glob", "Grep"]
)

async def analyze_code():
    async for message in query(
        prompt="src/main.py を分析してください",
        options=options
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    try:
                        result = json.loads(block.text)
                        print(json.dumps(result, indent=2, ensure_ascii=False))
                    except json.JSONDecodeError:
                        print(f"JSON パースエラー: {block.text}")
```

### 2. Markdown 形式

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions

markdown_options = ClaudeAgentOptions(
    system_prompt="""レポートは以下の Markdown 形式で出力してください:

# レポートタイトル

## 概要
[1-2 文の要約]

## 詳細分析

### セクション1
- ポイント1
- ポイント2

### セクション2
```python
# コード例があれば含める
```

## 結論
[推奨事項と次のステップ]

---
生成日時: [現在の日時]
"""
)
```

**実際に試す:**

```bash
# JSON 形式で出力
python src/02_options/05_system_prompt/02_output_format.py -f json -p "src/ を分析して"

# Markdown 形式で出力
python src/02_options/05_system_prompt/02_output_format.py -f markdown -p "レポートを作成して"

# JSON 検証付き
python src/02_options/05_system_prompt/02_output_format.py -f json --validate -p "分析して"
```

---

## 手順4: 制約条件の設定

### 1. 禁止事項の定義

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions

safe_options = ClaudeAgentOptions(
    system_prompt="""以下のルールを厳守してください:

## 禁止事項
- 本番環境のファイルを直接編集しない
- rm -rf などの破壊的コマンドを実行しない
- 機密情報（パスワード、APIキー）を出力しない
- 外部サービスに直接リクエストを送信しない

## 必須事項
- 変更前に必ずバックアップを確認
- 大きな変更は段階的に実行
- エラーが発生したら即座に報告
- 不明点があれば確認を求める

## 推奨事項
- コードにはコメントを追加
- テストも合わせて更新
- 変更内容を説明
""",
    allowed_tools=["Read", "Write", "Edit", "Glob", "Grep"]
)
```

### 2. セキュリティ制約

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions

security_options = ClaudeAgentOptions(
    system_prompt="""あなたはセキュリティを最優先するエンジニアです。

## セキュリティルール

### 入力検証
- すべてのユーザー入力をサニタイズ
- SQL インジェクション対策を確認
- XSS 対策を確認

### 認証・認可
- パスワードはハッシュ化を確認
- セッション管理の安全性を確認
- 最小権限の原則を適用

### データ保護
- 機密データの暗号化を確認
- ログに機密情報を出力しない
- HTTPS の使用を確認

コードを見る際は、常にこれらの観点でセキュリティリスクを評価してください。
""",
    allowed_tools=["Read", "Glob", "Grep"]
)
```

**実際に試す:**

```bash
# 安全モードで実行
python src/02_options/05_system_prompt/03_constraints.py -c safe -p "ファイルを編集して"

# セキュリティ重視モード
python src/02_options/05_system_prompt/03_constraints.py -c security -p "コードをレビューして"

# 読み取り専用モード
python src/02_options/05_system_prompt/03_constraints.py -c readonly -p "プロジェクトを確認して"
```

---

## 手順5: ドメイン固有の知識

### 1. プロジェクト固有の設定

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions

project_options = ClaudeAgentOptions(
    system_prompt="""このプロジェクトについての背景情報:

## プロジェクト概要
- 名前: MyApp
- 言語: Python 3.11
- フレームワーク: FastAPI
- データベース: PostgreSQL

## ディレクトリ構造
```
src/
├── api/          # API エンドポイント
├── models/       # SQLAlchemy モデル
├── services/     # ビジネスロジック
├── schemas/      # Pydantic スキーマ
└── utils/        # ユーティリティ
tests/            # テストコード
```

## コーディング規約
- Black でフォーマット
- isort でインポート整理
- mypy で型チェック
- pytest でテスト

## 命名規則
- クラス: PascalCase
- 関数/変数: snake_case
- 定数: UPPER_SNAKE_CASE
""",
    allowed_tools=["Read", "Write", "Edit", "Glob", "Grep", "Bash"],
    cwd="/path/to/myapp"
)
```

### 2. API 固有の知識

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions

api_options = ClaudeAgentOptions(
    system_prompt="""このプロジェクトの API 設計ルール:

## エンドポイント命名
- リソースは複数形: /users, /items
- ネストは2階層まで: /users/{id}/orders
- アクションは動詞を避ける: POST /orders (not /orders/create)

## レスポンス形式
成功時:
```json
{
    "data": {...},
    "meta": {"total": 100, "page": 1}
}
```

エラー時:
```json
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "説明",
        "details": [...]
    }
}
```

## HTTP ステータスコード
- 200: 成功
- 201: 作成成功
- 400: バリデーションエラー
- 401: 認証エラー
- 403: 権限エラー
- 404: リソース不在
- 500: サーバーエラー
"""
)
```

---

## 手順6: 複合的なシステムプロンプト

### 1. テンプレートベースの構築

**コード:**

```python
from claude_agent_sdk import ClaudeAgentOptions

def build_system_prompt(
    role: str,
    project_info: dict,
    constraints: list[str],
    output_format: str = None
) -> str:
    """システムプロンプトを組み立てる"""

    parts = []

    # 役割
    parts.append(f"# 役割\n{role}")

    # プロジェクト情報
    if project_info:
        parts.append("# プロジェクト情報")
        for key, value in project_info.items():
            parts.append(f"- {key}: {value}")

    # 制約条件
    if constraints:
        parts.append("# 制約条件")
        for c in constraints:
            parts.append(f"- {c}")

    # 出力形式
    if output_format:
        parts.append(f"# 出力形式\n{output_format}")

    return "\n\n".join(parts)

# 使用例
prompt = build_system_prompt(
    role="あなたはシニア Python 開発者です",
    project_info={
        "言語": "Python 3.11",
        "フレームワーク": "FastAPI",
        "データベース": "PostgreSQL"
    },
    constraints=[
        "本番環境のファイルを編集しない",
        "機密情報を出力しない",
        "テストを必ず書く"
    ],
    output_format="変更内容は Markdown 形式で説明してください"
)

options = ClaudeAgentOptions(system_prompt=prompt)
```

<div style="background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 6px; padding: 12px 16px; margin-bottom: 1em; font-size: 14px;">
  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
    <span style="font-size: 18px; color: #155724; line-height: 1;">&#x2714;</span>
    <span style="font-weight: bold; color: #155724; font-size: 15px;">ポイント</span>
  </div>
  <div style="color: #155724; line-height: 1.6;">
    システムプロンプトは再利用可能なテンプレートとして管理し、プロジェクトごとにカスタマイズすると効率的です。
  </div>
</div>

**実際に試す:**

```bash
# テンプレートを表示
python src/02_options/05_system_prompt/04_template_builder.py --show-template

# FastAPI プロジェクト用
python src/02_options/05_system_prompt/04_template_builder.py --role python-dev --framework fastapi --project-name MyAPI

# カスタム制約付き
python src/02_options/05_system_prompt/04_template_builder.py --role architect --add-constraint "パフォーマンスを最優先"
```

---

## 演習問題

### 演習1: ペルソナライブラリ

複数のペルソナ（レビューア、メンター、アーキテクトなど）を管理し、切り替え可能なクラスを作成してください。

### 演習2: 構造化出力

特定の JSON スキーマに従った出力を保証するシステムプロンプトを作成し、出力を検証する関数も実装してください。

### 演習3: プロンプトバージョン管理

システムプロンプトをバージョン管理し、効果を比較できる仕組みを作成してください。

---

## 次のステップ

システムプロンプトのカスタマイズを理解しました。次は [working_directory](06_working_directory.md) で、作業ディレクトリの設定について学びましょう。
