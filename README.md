# Claude Agent SDK Hands-on

Claude Agent SDK を学ぶためのハンズオン教材です。

## 概要

このリポジトリには、Claude Agent SDK の基本から応用までを段階的に学べるサンプルコードとドキュメントが含まれています。

## 構成

```
├── docs/           # ドキュメント (MkDocs)
│   ├── basics/     # 基礎編
│   ├── options/    # オプション設定
│   ├── tools/      # ツールの使い方
│   ├── advanced/   # 応用編
│   └── projects/   # プロジェクト例
├── src/            # サンプルコード
│   ├── basics/     # 基礎編のコード
│   ├── options/    # オプション設定のコード
│   ├── tools/      # ツール関連のコード
│   ├── advanced/   # 応用編のコード
│   └── projects/   # プロジェクト例のコード
└── mkdocs.yml      # MkDocs設定
```

## セットアップ

### 必要条件

- Python 3.10以上
- Claude Code CLI

### インストール

```bash
# 依存パッケージのインストール
pip install -r src/requirements.txt
```

## ドキュメントの閲覧

```bash
# MkDocsサーバーを起動
mkdocs serve
```

ブラウザで http://127.0.0.1:8000 にアクセスしてドキュメントを閲覧できます。

## 学習の進め方

1. **基礎編 (basics/)**: query関数、メッセージタイプ、エラーハンドリング、ClaudeSDKClient
2. **オプション (options/)**: ツール許可、パーミッションモード、システムプロンプト
3. **ツール (tools/)**: ファイル操作、Bash、検索ツール、Taskツール
4. **応用編 (advanced/)**: セッション管理、サブエージェント、Hooks、カスタムツール、MCP連携
5. **プロジェクト (projects/)**: 実践的なエージェント構築例

## ライセンス

MIT License
