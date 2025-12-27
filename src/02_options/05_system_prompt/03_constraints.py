"""
制約条件の設定 (手順4)

system_prompt で禁止事項や必須事項などの制約条件を設定します。
安全性を確保し、意図しない動作を防ぐために重要です。

Usage:
    python 03_constraints.py -l                  # 制約レベル一覧
    python 03_constraints.py -c safe -p "ファイルを編集して"
    python 03_constraints.py -c security -p "コードをレビューして"
    python 03_constraints.py -c strict -p "データベースを操作して"
"""
import argparse
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, TextBlock, ToolUseBlock

# =============================================================================
# 制約条件プロンプト定義
# =============================================================================

SAFE_CONSTRAINTS_PROMPT = """以下のルールを厳守してください:

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
"""

SECURITY_CONSTRAINTS_PROMPT = """あなたはセキュリティを最優先するエンジニアです。

## セキュリティルール

### 入力検証
- すべてのユーザー入力をサニタイズ
- SQL インジェクション対策を確認
- XSS 対策を確認
- パストラバーサル攻撃を防ぐ

### 認証・認可
- パスワードはハッシュ化を確認
- セッション管理の安全性を確認
- 最小権限の原則を適用
- 認証トークンの適切な管理

### データ保護
- 機密データの暗号化を確認
- ログに機密情報を出力しない
- HTTPS の使用を確認
- 個人情報の適切な取り扱い

### コード安全性
- 安全でない関数の使用を避ける（eval, exec など）
- 依存ライブラリの脆弱性をチェック
- エラーメッセージから情報が漏れないよう注意

コードを見る際は、常にこれらの観点でセキュリティリスクを評価してください。
"""

STRICT_CONSTRAINTS_PROMPT = """厳格なルールに従って作業してください:

## 絶対禁止
- データベースの DROP/TRUNCATE 操作
- 本番環境への直接デプロイ
- sudo を使ったコマンド実行
- システムファイルの変更
- 本番データの削除・変更
- credentials/secrets ファイルへのアクセス

## 事前承認が必要
- データベーススキーマの変更
- 外部 API の呼び出し
- 新しい依存関係の追加
- 設定ファイルの変更

## 必須の確認事項
- 操作対象が開発環境であることを確認
- 変更の影響範囲を明確化
- ロールバック手順の準備
- テスト実行の完了

## 実行前の質問
不明な点や懸念がある場合は、必ず実行前に質問してください。
"""

READONLY_CONSTRAINTS_PROMPT = """読み取り専用モードで動作します:

## 制限事項
- ファイルの作成・編集・削除は一切行わない
- システムコマンドを実行しない
- 外部への通信を行わない
- 設定の変更を行わない

## 許可されること
- ファイルの読み取り
- コードの分析
- 情報の検索
- レポートの生成（出力のみ）

## 動作原則
- 観察と分析に徹する
- 推奨事項を提案するが実行はしない
- 実行が必要な場合はユーザーに指示を求める
"""

TESTING_CONSTRAINTS_PROMPT = """テスト環境専用の制約:

## 許可される操作
- テストファイルの作成・編集
- テストデータベースへのアクセス
- モックサーバーの使用
- ログファイルの確認

## 禁止される操作
- 本番環境へのアクセス
- 本番データの使用
- 外部サービスへの実際のリクエスト

## テストルール
- テストは隔離された環境で実行
- テスト後のクリーンアップを実行
- テストデータは明確にラベル付け
- CI/CD パイプラインとの統合を考慮

## 品質基準
- テストカバレッジ 80% 以上を目指す
- エッジケースも必ずテスト
- 失敗時のエラーメッセージを明確に
"""

# =============================================================================
# 制約レベルマッピング
# =============================================================================

CONSTRAINTS = {
    "safe": {
        "name": "安全モード",
        "prompt": SAFE_CONSTRAINTS_PROMPT,
        "tools": ["Read", "Write", "Edit", "Glob", "Grep"],
    },
    "security": {
        "name": "セキュリティ重視",
        "prompt": SECURITY_CONSTRAINTS_PROMPT,
        "tools": ["Read", "Glob", "Grep"],
    },
    "strict": {
        "name": "厳格モード",
        "prompt": STRICT_CONSTRAINTS_PROMPT,
        "tools": ["Read", "Glob", "Grep"],
    },
    "readonly": {
        "name": "読み取り専用",
        "prompt": READONLY_CONSTRAINTS_PROMPT,
        "tools": ["Read", "Glob", "Grep"],
    },
    "testing": {
        "name": "テスト環境",
        "prompt": TESTING_CONSTRAINTS_PROMPT,
        "tools": ["Read", "Write", "Edit", "Bash", "Glob", "Grep"],
    },
}


def parse_args() -> argparse.Namespace:
    """コマンドライン引数をパース"""
    parser = argparse.ArgumentParser(
        description="system_prompt による制約条件設定",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-c", "--constraint",
        choices=list(CONSTRAINTS.keys()),
        default="safe",
        help="制約レベル (default: safe)"
    )
    parser.add_argument(
        "-p", "--prompt",
        default="このプロジェクトのファイルを確認してください",
        help="実行するプロンプト"
    )
    parser.add_argument(
        "-l", "--list-constraints",
        action="store_true",
        help="利用可能な制約レベルの一覧を表示して終了"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="詳細出力"
    )
    return parser.parse_args()


def print_constraints():
    """全制約レベルの詳細を表示"""
    print("=" * 60)
    print("利用可能な制約レベル一覧")
    print("=" * 60)

    for key, constraint in CONSTRAINTS.items():
        print(f"\n[{key}] {constraint['name']}")
        print(f"  allowed_tools: {constraint['tools']}")
        # 最初の5行を表示
        lines = constraint['prompt'].strip().split('\n')[:5]
        for line in lines:
            print(f"  {line}")
        print("  ...")


async def main():
    """メイン処理"""
    args = parse_args()

    if args.list_constraints:
        print_constraints()
        return

    constraint = CONSTRAINTS[args.constraint]
    options = ClaudeAgentOptions(
        system_prompt=constraint['prompt'],
        allowed_tools=constraint['tools']
    )

    print("=" * 60)
    print(f"制約レベル: {constraint['name']} ({args.constraint})")
    print(f"allowed_tools: {constraint['tools']}")
    if args.verbose:
        print("-" * 60)
        print("制約内容:")
        print(constraint['prompt'])
    print("-" * 60)
    print(f"プロンプト: {args.prompt}")
    print("=" * 60)
    print()

    async for message in query(
        prompt=args.prompt,
        options=options
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)
                elif isinstance(block, ToolUseBlock):
                    if args.verbose:
                        print(f"\n[Tool] {block.name}: {block.input}")


if __name__ == "__main__":
    asyncio.run(main())
